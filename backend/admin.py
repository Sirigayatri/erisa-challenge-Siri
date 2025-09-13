from django.contrib import admin
from database.models import Claim, ClaimDetail, Flag, Note

# Register models but hide them from admin interface
@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        # Hide from admin interface
        return {}

@admin.register(ClaimDetail)
class ClaimDetailAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        # Hide from admin interface
        return {}

@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        # Hide from admin interface
        return {}

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        # Hide from admin interface
        return {}

# Customize admin site
admin.site.site_header = "ERISA Recovery Claims Management"
admin.site.site_title = "ERISA Recovery Admin"
admin.site.index_title = "Claims Management System"
