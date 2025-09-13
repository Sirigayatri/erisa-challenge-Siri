import csv
import os
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from database.models import Claim, ClaimDetail


class Command(BaseCommand):
    help = 'Load claims and claim details from pipe-delimited CSV files with options to overwrite or append data'

    def add_arguments(self, parser):
        parser.add_argument('claim_list_file', type=str, help='Path to claim list CSV file')
        parser.add_argument('claim_detail_file', type=str, help='Path to claim detail CSV file')
        parser.add_argument(
            '--mode',
            choices=['overwrite', 'append', 'smart'],
            default='smart',
            help='Data import mode: overwrite (replace all), append (add new only), smart (update existing, add new)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompts'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )

    def handle(self, *args, **options):
        claim_list_file = options['claim_list_file']
        claim_detail_file = options['claim_detail_file']
        mode = options['mode']
        force = options['force']
        dry_run = options['dry_run']

        # Validate file paths
        if not os.path.exists(claim_list_file):
            raise CommandError(f'Claim list file not found: {claim_list_file}')
        
        if not os.path.exists(claim_detail_file):
            raise CommandError(f'Claim detail file not found: {claim_detail_file}')

        # Show import summary
        self.show_import_summary(claim_list_file, claim_detail_file, mode, dry_run)
        
        # Confirm import if not forced
        if not force and not dry_run:
            if not self.confirm_import(mode):
                self.stdout.write(self.style.WARNING('Import cancelled by user'))
                return

        self.stdout.write('Starting to load claims data...')

        try:
            with transaction.atomic():
                # Load claims
                claims_stats = self.load_claims(claim_list_file, mode, dry_run)
                
                # Load claim details
                details_stats = self.load_claim_details(claim_detail_file, mode, dry_run)

                if not dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully processed claims data:\n'
                            f'  Claims: {claims_stats["total"]} total, '
                            f'{claims_stats["created"]} created, '
                            f'{claims_stats["updated"]} updated, '
                            f'{claims_stats["skipped"]} skipped\n'
                            f'  Details: {details_stats["total"]} total, '
                            f'{details_stats["created"]} created, '
                            f'{details_stats["updated"]} updated, '
                            f'{details_stats["skipped"]} skipped'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'DRY RUN - No data was actually imported:\n'
                            f'  Claims: {claims_stats["total"]} would be processed\n'
                            f'  Details: {details_stats["total"]} would be processed'
                        )
                    )

        except Exception as e:
            raise CommandError(f'Error during import: {e}')

    def show_import_summary(self, claim_list_file, claim_detail_file, mode, dry_run):
        """Show summary of what will be imported"""
        self.stdout.write(f'\n📊 Import Summary:')
        self.stdout.write(f'  Mode: {mode.upper()}')
        self.stdout.write(f'  Claim List: {claim_list_file}')
        self.stdout.write(f'  Claim Details: {claim_detail_file}')
        self.stdout.write(f'  Dry Run: {"Yes" if dry_run else "No"}')
        
        if mode == 'overwrite':
            self.stdout.write(self.style.WARNING('  ⚠️  OVERWRITE MODE: All existing data will be replaced'))
        elif mode == 'append':
            self.stdout.write(self.style.SUCCESS('  ➕ APPEND MODE: Only new data will be added'))
        else:  # smart
            self.stdout.write(self.style.SUCCESS('  🧠 SMART MODE: Existing data will be updated, new data added'))
        
        self.stdout.write('')

    def confirm_import(self, mode):
        """Get user confirmation for import"""
        if mode == 'overwrite':
            response = input('⚠️  This will OVERWRITE all existing data. Are you sure? (yes/no): ')
        else:
            response = input(f'Proceed with {mode.upper()} import? (yes/no): ')
        
        return response.lower() in ['yes', 'y']

    def load_claims(self, file_path, mode, dry_run):
        """Load claims from CSV file with specified mode"""
        stats = {'total': 0, 'created': 0, 'updated': 0, 'skipped': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='|')
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Parse and validate data
                        claim_id = int(row['id'])
                        billed_amount = Decimal(row['billed_amount'])
                        paid_amount = Decimal(row['paid_amount'])
                        discharge_date = datetime.strptime(row['discharge_date'], '%Y-%m-%d').date()
                        
                        stats['total'] += 1
                        
                        # Check if claim exists
                        existing_claim = Claim.objects.filter(id=claim_id).first()
                        
                        if existing_claim:
                            if mode == 'append':
                                self.stdout.write(f'Skipping existing claim {claim_id} (append mode)')
                                stats['skipped'] += 1
                                continue
                            elif mode == 'overwrite':
                                if not dry_run:
                                    existing_claim.delete()
                                    existing_claim = None
                                self.stdout.write(f'Will replace existing claim {claim_id}')
                        
                        if not dry_run:
                            # Create or update claim
                            if existing_claim:
                                # Update existing claim
                                existing_claim.patient_name = row['patient_name']
                                existing_claim.billed_amount = billed_amount
                                existing_claim.paid_amount = paid_amount
                                existing_claim.status = row['status']
                                existing_claim.insurer_name = row['insurer_name']
                                existing_claim.discharge_date = discharge_date
                                existing_claim.save()
                                stats['updated'] += 1
                                self.stdout.write(f'Updated claim {claim_id}')
                            else:
                                # Create new claim
                                Claim.objects.create(
                            id=claim_id,
                                    patient_name=row['patient_name'],
                                    billed_amount=billed_amount,
                                    paid_amount=paid_amount,
                                    status=row['status'],
                                    insurer_name=row['insurer_name'],
                                    discharge_date=discharge_date,
                                )
                                stats['created'] += 1
                            self.stdout.write(f'Created claim {claim_id}')
                        else:
                            if existing_claim:
                                stats['updated'] += 1
                            else:
                                stats['created'] += 1
                        
                    except (ValueError, KeyError) as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Error processing claim at row {row_num}: {e}'
                            )
                        )
                        stats['skipped'] += 1
                        continue
                        
        except Exception as e:
            raise CommandError(f'Error reading claim list file: {e}')
        
        return stats

    def load_claim_details(self, file_path, mode, dry_run):
        """Load claim details from CSV file with specified mode"""
        stats = {'total': 0, 'created': 0, 'updated': 0, 'skipped': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter='|')
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        if len(row) != 4:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Invalid row format at row {row_num}: expected 4 columns, got {len(row)}'
                                )
                            )
                            stats['skipped'] += 1
                            continue
                        
                        # Parse row data
                        detail_id = int(row[0])
                        claim_id = int(row[1])
                        denial_reason = row[2]
                        cpt_codes = row[3]
                        
                        # Handle "N/A" denial reason
                        if denial_reason == "N/A":
                            denial_reason = ""
                        
                        stats['total'] += 1
                        
                        # Check if claim exists
                        try:
                            claim = Claim.objects.get(id=claim_id)
                        except Claim.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Claim {claim_id} not found for detail {detail_id} at row {row_num}'
                                )
                            )
                            stats['skipped'] += 1
                            continue
                        
                        # Check if detail exists
                        existing_detail = ClaimDetail.objects.filter(claim=claim).first()
                        
                        if existing_detail:
                            if mode == 'append':
                                self.stdout.write(f'Skipping existing detail for claim {claim_id} (append mode)')
                                stats['skipped'] += 1
                                continue
                            elif mode == 'overwrite':
                                if not dry_run:
                                    existing_detail.delete()
                                    existing_detail = None
                                self.stdout.write(f'Will replace existing detail for claim {claim_id}')
                        
                        if not dry_run:
                            # Create or update claim detail
                            if existing_detail:
                                # Update existing detail
                                existing_detail.denial_reason = denial_reason
                                existing_detail.cpt_codes = cpt_codes
                                existing_detail.save()
                                stats['updated'] += 1
                                self.stdout.write(f'Updated detail for claim {claim_id}')
                            else:
                                # Create new detail
                                ClaimDetail.objects.create(
                            claim=claim,
                                    denial_reason=denial_reason,
                                    cpt_codes=cpt_codes,
                                )
                                stats['created'] += 1
                            self.stdout.write(f'Created detail for claim {claim_id}')
                        else:
                            if existing_detail:
                                stats['updated'] += 1
                            else:
                                stats['created'] += 1
                        
                    except (ValueError, IndexError) as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Error processing claim detail at row {row_num}: {e}'
                            )
                        )
                        stats['skipped'] += 1
                        continue
                        
        except Exception as e:
            raise CommandError(f'Error reading claim detail file: {e}')
        
        return stats
