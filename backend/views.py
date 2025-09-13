from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum, Avg, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import tempfile
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.urls import reverse
import json
from database.models import Claim, Note, Flag

def dashboard(request):
    """Main dashboard view with statistics and claims list."""
    # Get filter parameters
    status_q = request.GET.get('status') or ''
    insurer_q = request.GET.get('insurer') or ''
    page = request.GET.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    # Base queryset - order by claim ID for consistent ordering
    qs = Claim.objects.all().order_by('id')
    
    # Apply filters
    if status_q:
        qs = qs.filter(status__icontains=status_q)
    if insurer_q:
        qs = qs.filter(insurer_name__icontains=insurer_q)
    
    # Get total count for pagination
    total_filtered_claims = qs.count()
    
    # Pagination: 30 claims per page, max 100 claims total
    claims_per_page = 30
    max_claims = 100
    
    # Calculate pagination
    if page <= 0:
        page = 1
    
    start_index = (page - 1) * claims_per_page
    end_index = min(start_index + claims_per_page, max_claims)
    
    # Get claims for current page
    claims = qs.select_related('detail').prefetch_related('flags', 'notes')[start_index:end_index]
    
    # Check if there are more claims to load
    has_more = end_index < min(total_filtered_claims, max_claims)
    has_previous = page > 1
    
    # Get statistics
    total_claims = Claim.objects.count()
    flagged_claims = Flag.objects.count()
    total_notes = Note.objects.count()
    
    # Get status-based counts for sidebar
    pending_count = Claim.objects.filter(status__icontains='pending').count()
    under_review_count = Claim.objects.filter(status__icontains='under review').count()
    paid_count = Claim.objects.filter(status__icontains='paid').count()
    denied_count = Claim.objects.filter(status__icontains='denied').count()
    underpaid_count = Claim.objects.filter(status__icontains='underpaid').count()
    
    # Calculate average underpayment
    claims_with_underpayment = [claim.underpayment() for claim in Claim.objects.all()]
    avg_underpayment = sum(claims_with_underpayment) / len(claims_with_underpayment) if claims_with_underpayment else 0
    
    context = {
        "claims": claims,
        "q_status": status_q,
        "q_insurer": insurer_q,
        "total_claims": total_claims,
        "flagged_claims": flagged_claims,
        "total_notes": total_notes,
        "avg_underpayment": avg_underpayment,
        "pending_count": pending_count,
        "under_review_count": under_review_count,
        "paid_count": paid_count,
        "denied_count": denied_count,
        "underpaid_count": underpaid_count,
        "current_page": page,
        "has_more": has_more,
        "has_previous": has_previous,
        "total_filtered_claims": total_filtered_claims,
        "showing_start": start_index + 1,
        "showing_end": end_index,
    }
    
    return render(request, "claims/dashboard.html", context)

def claim_list(request):
    """Legacy claim list view - redirects to dashboard."""
    return dashboard(request)

def claim_detail_partial(request, pk):
    """HTMX endpoint for claim details."""
    claim = get_object_or_404(Claim.objects.select_related('detail'), pk=pk)
    print(f"DEBUG: Rendering claim {pk} with template claims/_claim_detail.html")
    print(f"DEBUG: Claim has {claim.notes.count()} notes and {claim.flags.count()} flags")
    try:
        return render(request, "claims/_claim_detail.html", {"claim": claim})
    except Exception as e:
        print(f"ERROR rendering template: {e}")
        return render(request, "claims/_claim_detail.html", {"claim": claim})

@csrf_exempt
@require_http_methods(["POST"])
def flag_claim_api(request, pk):
    """API endpoint to flag a claim."""
    try:
        claim = get_object_or_404(Claim, pk=pk)
        Flag.objects.create(claim=claim, created_by=request.user if request.user.is_authenticated else None)
        return JsonResponse({'success': True, 'message': 'Claim flagged successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def add_note_api(request, pk):
    """API endpoint to add a note to a claim."""
    try:
        claim = get_object_or_404(Claim, pk=pk)
        data = json.loads(request.body)
        note_text = data.get('text', '').strip()
        
        if not note_text:
            return JsonResponse({'success': False, 'error': 'Note text is required'}, status=400)
        
        Note.objects.create(
            claim=claim, 
            text=note_text,
            created_by=request.user if request.user.is_authenticated else None
        )
        return JsonResponse({'success': True, 'message': 'Note added successfully'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def csv_upload_view(request):
    """CSV upload view with smart merge functionality"""
    if request.method == 'POST':
        try:
            # Get uploaded CSV files
            claim_list_file = request.FILES.get('claim_list_file')
            claim_detail_file = request.FILES.get('claim_detail_file')
            
            # Check if we have a single CSV file (new format) or both files (existing format)
            if not claim_list_file and not claim_detail_file:
                return JsonResponse({'success': False, 'message': 'No CSV files provided'})
            
            # If only one file is provided, assume it's the claim list and create empty detail file
            if claim_list_file and not claim_detail_file:
                # For now, use the existing claim_detail_data.csv as the detail file
                claim_detail_file_path = 'claim_detail_data.csv'
                if not os.path.exists(claim_detail_file_path):
                    return JsonResponse({'success': False, 'message': 'Claim detail file not found. Please upload both files.'})
            elif claim_detail_file and not claim_list_file:
                return JsonResponse({'success': False, 'message': 'Please upload the claim list file as well.'})
            elif claim_list_file and claim_detail_file:
                # Both files provided - use them
                claim_detail_file_path = None
            else:
                return JsonResponse({'success': False, 'message': 'Please upload at least the claim list file.'})
            
            # Save files temporarily
            temp_dir = tempfile.mkdtemp()
            claim_list_path = os.path.join(temp_dir, 'claim_list.csv')
            
            with open(claim_list_path, 'wb') as f:
                for chunk in claim_list_file.chunks():
                    f.write(chunk)
            
            # Handle claim detail file
            if claim_detail_file_path:
                # Use existing file
                claim_detail_path = claim_detail_file_path
            else:
                # Use uploaded file
                claim_detail_path = os.path.join(temp_dir, 'claim_detail.csv')
                with open(claim_detail_path, 'wb') as f:
                    for chunk in claim_detail_file.chunks():
                        f.write(chunk)
            
            # Count existing claims and user data before import
            existing_claims_count = Claim.objects.count()
            existing_flags_count = Flag.objects.count()
            existing_notes_count = Note.objects.count()
            
            # Call the management command with smart merge
            try:
                call_command('load_claims', claim_list_path, claim_detail_path, '--mode', 'smart', '--force')
                
                # Count after import
                new_claims_count = Claim.objects.count()
                new_flags_count = Flag.objects.count()
                new_notes_count = Note.objects.count()
                
                # Calculate what was updated
                claims_updated = new_claims_count - existing_claims_count
                flags_preserved = new_flags_count - existing_flags_count
                notes_preserved = new_notes_count - existing_notes_count
                
                message = f"Updated {claims_updated} claims. Preserved {flags_preserved} flags and {notes_preserved} notes."
                
                return JsonResponse({
                    'success': True, 
                    'message': message,
                    'claims_updated': claims_updated,
                    'flags_preserved': flags_preserved,
                    'notes_preserved': notes_preserved
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error during import: {str(e)}'})
            finally:
                # Clean up temp files
                import shutil
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error processing upload: {str(e)}'})
    
    # Get current statistics for context
    total_claims = Claim.objects.count()
    flagged_claims = Flag.objects.count()
    total_notes = Note.objects.count()
    
    # Financial summary
    financial_stats = Claim.objects.aggregate(
        total_billed=Sum('billed_amount'),
        total_paid=Sum('paid_amount'),
    )
    
    total_underpayment = sum(claim.underpayment() for claim in Claim.objects.all())
    avg_underpayment = total_underpayment / total_claims if total_claims > 0 else 0
    
    context = {
        'total_claims': total_claims,
        'flagged_claims': flagged_claims,
        'total_notes': total_notes,
        'financial_stats': financial_stats,
        'total_underpayment': total_underpayment,
        'avg_underpayment': avg_underpayment,
    }
    
    return render(request, 'claims/csv_upload.html', context)

def add_flag(request, pk):
    """Add a flag to a claim."""
    claim = get_object_or_404(Claim, pk=pk)
    Flag.objects.create(claim=claim)
    return claim_detail_partial(request, pk)

def add_note(request, pk):
    """Add a note to a claim."""
    claim = get_object_or_404(Claim, pk=pk)
    Note.objects.create(claim=claim, text=request.POST.get("text",""))
    return claim_detail_partial(request, pk)

def load_more_claims(request):
    """API endpoint to load more claims for pagination."""
    try:
        page = int(request.GET.get('page', 1))
        status_q = request.GET.get('status', '')
        insurer_q = request.GET.get('insurer', '')
        
        # Base queryset - order by claim ID for consistent ordering
        qs = Claim.objects.all().order_by('id')
        
        # Apply filters
        if status_q:
            qs = qs.filter(status__icontains=status_q)
        if insurer_q:
            qs = qs.filter(insurer_name__icontains=insurer_q)
        
        # Pagination: 30 claims per page, max 100 claims total
        claims_per_page = 30
        max_claims = 100
        
        start_index = (page - 1) * claims_per_page
        end_index = min(start_index + claims_per_page, max_claims)
        
        # Get claims for current page
        claims = qs.select_related('detail').prefetch_related('flags', 'notes')[start_index:end_index]
        
        # Check if there are more claims to load
        total_filtered_claims = qs.count()
        has_more = end_index < min(total_filtered_claims, max_claims)
        has_previous = page > 1
        
        # Render claims as HTML
        from django.template.loader import render_to_string
        claims_html = render_to_string('claims/claims_table_rows.html', {
            'claims': claims,
            'request': request
        })
        
        return JsonResponse({
            'success': True,
            'html': claims_html,
            'has_more': has_more,
            'has_previous': has_previous,
            'current_page': page,
            'showing_end': end_index,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def report_view(request):
    """Generate comprehensive reports with charts and analytics."""
    try:
        print("Starting report_view...")
        
        # Get limited claims data for performance
        claims = Claim.objects.all()
        print(f"Total claims available: {claims.count()}")
        
        # Status distribution for pie chart (limit to 1000 claims)
        status_distribution = claims.values('status').annotate(count=Count('id')).order_by('-count')[:1000]
        print(f"Status distribution: {list(status_distribution)}")
        status_data = {
            'labels': [item['status'] for item in status_distribution],
            'data': [item['count'] for item in status_distribution],
            'colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
        }
        print(f"Status data: {status_data}")
        print("Status data processed...")
        
        # Billed vs Paid amounts by insurer for bar chart (limit to 5 insurers)
        billed_paid_data = []
        insurers = list(claims.values('insurer_name').distinct()[:5])
        print(f"Found insurers: {insurers}")
        for insurer in insurers:
            insurer_claims = claims.filter(insurer_name=insurer['insurer_name'])[:1000]  # Limit per insurer
            total_billed = float(insurer_claims.aggregate(Sum('billed_amount'))['billed_amount__sum'] or 0)
            total_paid = float(insurer_claims.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0)
            billed_paid_data.append({
                'insurer': insurer['insurer_name'],
                'billed': total_billed,
                'paid': total_paid
            })
        print(f"Billed paid data: {billed_paid_data}")
        print("Billed paid data processed...")
        
        # Underpayment by insurer for horizontal bar chart (limit to 5 insurers)
        underpayment_data = []
        for insurer in insurers:
            insurer_claims = claims.filter(insurer_name=insurer['insurer_name'])[:1000]  # Limit per insurer
            total_underpayment = sum(float(claim.underpayment()) for claim in insurer_claims)
            avg_underpayment = total_underpayment / insurer_claims.count() if insurer_claims.count() > 0 else 0
            underpayment_data.append({
                'insurer': insurer['insurer_name'],
                'avg_underpayment': avg_underpayment,
                'total_underpayment': total_underpayment,
                'claim_count': insurer_claims.count()
            })
        
        # Sort by average underpayment
        underpayment_data.sort(key=lambda x: x['avg_underpayment'], reverse=True)
        print(f"Underpayment data: {underpayment_data}")
        print("Underpayment data processed...")
        
        # Financial summary (limit to 1000 claims for performance)
        limited_claims = claims[:1000]
        financial_summary = limited_claims.aggregate(
            total_billed=Sum('billed_amount'),
            total_paid=Sum('paid_amount'),
            avg_billed=Avg('billed_amount'),
            avg_paid=Avg('paid_amount')
        )
        
        # Calculate total underpayment (simplified)
        total_underpayment = float(sum(claim.underpayment() for claim in limited_claims))
        avg_underpayment = total_underpayment / limited_claims.count() if limited_claims.count() > 0 else 0
        print("Financial summary processed...")
        
        # Simplified monthly data (last 6 months only)
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        monthly_data = []
        for i in range(6):  # Reduced from 12 to 6 months
            month_start = timezone.now() - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            month_claims = claims.filter(created_at__range=[month_start, month_end])[:1000]  # Limit per month
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'count': month_claims.count(),
                'billed': float(sum(claim.billed_amount for claim in month_claims)),
                'paid': float(sum(claim.paid_amount for claim in month_claims)),
                'underpayment': float(sum(claim.underpayment() for claim in month_claims))
            })
        
        monthly_data.reverse()  # Show oldest to newest
        print("Monthly data processed...")
        
        # Top underpayments (limit to 5)
        top_underpayments = []
        for claim in limited_claims[:100]:  # Only check first 100 claims
            underpayment = claim.underpayment()
            if underpayment > 0:
                top_underpayments.append({
                    'claim_id': claim.id,
                    'patient_name': claim.patient_name,
                    'insurer': claim.insurer_name,
                    'underpayment': float(underpayment),
                    'billed': float(claim.billed_amount),
                    'paid': float(claim.paid_amount)
                })
        
        top_underpayments.sort(key=lambda x: x['underpayment'], reverse=True)
        top_underpayments = top_underpayments[:5]  # Limit to 5
        print("Top underpayments processed...")
        
        # Flagged claims analysis
        flagged_claims = claims.filter(flags__isnull=False).distinct()[:1000]
        flagged_status_dist = flagged_claims.values('status').annotate(count=Count('id'))
        
        # Notes analysis
        claims_with_notes = claims.filter(notes__isnull=False).distinct()[:1000]
        
        context = {
            'status_data': status_data,
            'billed_paid_data': billed_paid_data,
            'underpayment_data': underpayment_data,
            'financial_summary': financial_summary,
            'total_underpayment': total_underpayment,
            'avg_underpayment': avg_underpayment,
            'monthly_data': monthly_data,
            'top_underpayments': top_underpayments,
            'flagged_claims_count': flagged_claims.count(),
            'flagged_status_dist': flagged_status_dist,
            'claims_with_notes_count': claims_with_notes.count(),
            'total_claims': limited_claims.count(),
        }
        
        print("Rendering template...")
        return render(request, 'claims/report.html', context)
    
    except Exception as e:
        print(f"Error in report_view: {e}")
        import traceback
        traceback.print_exc()
        return render(request, 'claims/report.html', {
            'error': str(e),
            'status_data': {'labels': [], 'data': [], 'colors': []},
            'billed_paid_data': [],
            'underpayment_data': [],
            'financial_summary': {},
            'total_underpayment': 0,
            'avg_underpayment': 0,
            'monthly_data': [],
            'top_underpayments': [],
            'flagged_claims_count': 0,
            'flagged_status_dist': [],
            'claims_with_notes_count': 0,
            'total_claims': 0,
        })
