from django.urls import path
from . import views

app_name = 'claims'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # New dashboard as default
    path('list/', views.claim_list, name='claim_list'),  # Legacy list view
    path('csv_upload/', views.csv_upload_view, name='csv_upload'),  # Direct CSV upload
    path('<int:claim_id>/detail/', views.claim_detail_partial, name='claim_detail'),
    path('<int:claim_id>/detail/partial/', views.claim_detail_partial, name='claim_detail_partial'),
    
    # API endpoints for dashboard functionality
    path('<int:pk>/flag/', views.flag_claim_api, name='flag_claim_api'),
    path('<int:pk>/note/', views.add_note_api, name='add_note_api'),
    path('load-more/', views.load_more_claims, name='load_more_claims'),
    
    # Report page
    path('report/', views.report_view, name='report'),
]
