"""
planning/admin.py — Registers models with Django's admin interface.

THE DJANGO ADMIN:
  Django provides a free, fully-functional CRUD admin panel at /admin/.
  By registering your models here, you get:
    - A list view of all records
    - Search and filter controls
    - A form to add/edit/delete records

  To use it:
    1. Run: python manage.py createsuperuser
    2. Visit: http://localhost:8000/admin/
    3. Log in with your superuser credentials

CUSTOMISING THE ADMIN:
  You can pass a ModelAdmin class to admin.site.register() to customise
  how a model appears in the admin. Common options:
    list_display   — which columns to show in the list view
    list_filter    — which fields to add filter checkboxes for
    search_fields  — which fields to search through
    ordering       — default sort order
"""

from django.contrib import admin
from .models import (
    StaffMember, StaffCost, Project, ProjectBudget,
    WorkPackage, StaffAllocation, BudgetSwap
)


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    """Admin configuration for StaffMember model."""
    # list_display: columns shown in the changelist (the main table view)
    list_display = ['initials', 'name', 'staff_type', 'department', 'pcm_until']
    # list_filter: adds filter sidebar with checkboxes
    list_filter = ['staff_type', 'department']
    # search_fields: enables search box; __ traverses related fields
    search_fields = ['name', 'initials', 'department']
    ordering = ['name']


@admin.register(StaffCost)
class StaffCostAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'valid_from', 'valid_until', 'monthly_cost', 'confidence']
    list_filter = ['confidence']
    search_fields = ['staff_member__name', 'staff_member__initials']
    # raw_id_fields: for ForeignKeys, shows a text input + popup instead of a huge dropdown
    raw_id_fields = ['staff_member']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'rcode', 'is_active', 'start_date', 'end_date',
        'pm_original', 'is_ts_required', 'is_audited'
    ]
    list_filter = ['is_active', 'is_ts_required', 'is_audited']
    search_fields = ['name', 'rcode', 'notes']
    ordering = ['end_date', 'name']
    # date_hierarchy: adds a drill-down date navigation bar
    date_hierarchy = 'end_date'


@admin.register(ProjectBudget)
class ProjectBudgetAdmin(admin.ModelAdmin):
    list_display = ['project', 'budget_di_original', 'budget_da_original', 'budget_additional']
    search_fields = ['project__name']
    raw_id_fields = ['project']


@admin.register(WorkPackage)
class WorkPackageAdmin(admin.ModelAdmin):
    list_display = ['project', 'wp_number', 'title', 'person_months', 'start_date', 'end_date']
    list_filter = ['project']
    search_fields = ['project__name', 'wp_number', 'title']
    raw_id_fields = ['project']


@admin.register(StaffAllocation)
class StaffAllocationAdmin(admin.ModelAdmin):
    list_display = [
        'staff_member', 'project', 'start_date', 'end_date',
        'fte', 'person_months', 'cost', 'work_packages'
    ]
    list_filter = ['staff_member', 'project']
    search_fields = ['staff_member__name', 'staff_member__initials', 'project__name', 'notes']
    raw_id_fields = ['staff_member', 'project']
    date_hierarchy = 'start_date'


@admin.register(BudgetSwap)
class BudgetSwapAdmin(admin.ModelAdmin):
    list_display = [
        'from_project_name', 'to_project_name', 'date',
        'amount_gbp', 'notes'
    ]
    search_fields = ['from_project_name', 'to_project_name', 'notes']
    date_hierarchy = 'date'
