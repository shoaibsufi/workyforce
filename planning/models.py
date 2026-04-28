"""
planning/models.py — The data models for the eScience Lab Workforce Planner.

WHAT IS A MODEL?
  A Django model is a Python class that maps directly to a database table.
  Each attribute of the class becomes a column in the table.
  Django uses these definitions to:
    1. Create the actual database tables (via `python manage.py migrate`)
    2. Provide a Python API for querying and saving data
    3. Auto-generate admin forms

CHANGELOG:
  v2 — Updated to match the March 2026 spreadsheet revision:
    - StaffMember: added `employee_number` field (new column in staff sheet)
    - StaffMember: added `pcm_projected_until` field (new column in staff sheet)
    - Two new staff members (AF = Ali Feizollah, PS = Paul Slavin) are handled
      automatically — no model change needed, just new rows in the DB.
    - HI1 and SRSE1 sheets removed from spreadsheet — existing DB rows are
      harmless and will simply stop being updated on re-import.
"""

from django.db import models


# =============================================================================
# STAFF MEMBER
# Mirrors the 'staff' sheet and the per-person sheets (CAG, SSR, MA, etc.)
# =============================================================================

class StaffMember(models.Model):
    """
    Represents a person who works in the eScience Lab.

    Corresponds to rows in the 'staff' sheet.
    The initials (e.g. 'SS', 'MA') are used as the unique identifier
    because that's how the spreadsheet cross-references everything.
    """

    # Staff type choices — mirrors the 'Type' column in the staff sheet
    ACADEMIC = 'Academic'
    RESEARCH = 'Research'
    PS = 'PS'            # Professional Services
    STAFF_TYPE_CHOICES = [
        (ACADEMIC, 'Academic'),
        (RESEARCH, 'Research Staff'),
        (PS, 'Professional Services'),
    ]

    # CharField stores text. max_length is required — set it generously.
    initials = models.CharField(
        max_length=10,
        unique=True,  # No two staff members can share initials
        help_text="Short identifier used across the spreadsheet (e.g. 'SS', 'MA')"
    )

    name = models.CharField(max_length=200, help_text="Full name of the staff member")

    # NEW in v2: Employee number added to the staff sheet
    # blank=True means the form field is optional; it defaults to '' (empty string)
    # We use CharField rather than IntegerField because employee numbers aren't
    # used for arithmetic and may occasionally have leading zeros or prefixes.
    employee_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="University employee/staff ID number (e.g. 5030408)"
    )

    # choices= restricts the value to one of the listed options.
    staff_type = models.CharField(
        max_length=20,
        choices=STAFF_TYPE_CHOICES,
        blank=True,
        help_text="Academic, Research, or Professional Services"
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department/Group (e.g. CS/eSL, IT/RIT)"
    )

    # DateField stores a date (no time component).
    # null=True / blank=True = optional field (the DB can store NULL).
    pcm_until = models.DateField(
        null=True, blank=True,
        help_text="Confirmed date until which the staff member's PCM runs"
    )

    # NEW in v2: The spreadsheet now has a separate 'PCM projected till' column,
    # distinguishing a confirmed end date from a projected/estimated one.
    pcm_projected_until = models.DateField(
        null=True, blank=True,
        help_text="Projected (estimated) date until which PCM may run — may extend beyond confirmed date"
    )

    timesheets_approved_until = models.DateField(
        null=True, blank=True,
        help_text="Month up to which timesheets have been approved/submitted"
    )

    notes = models.TextField(
        blank=True,
        help_text="Free-text notes about this staff member's arrangements"
    )

    # __str__ controls how a model instance appears as a string.
    # This is what shows in the admin panel and in template {{ obj }} expressions.
    def __str__(self):
        return f"{self.name} ({self.initials})"

    class Meta:
        # Meta class controls database-level behaviour.
        # ordering means queries will be sorted by name by default.
        ordering = ['name']
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"


# =============================================================================
# STAFF COST
# Mirrors the 'costs' sheet — monthly salary/cost figures
# =============================================================================

class StaffCost(models.Model):
    """
    Records the monthly cost for a staff member over a date range.
    A person may have multiple cost entries if their salary changed over time.

    Mirrors the 'costs' sheet.
    """

    # ForeignKey creates a many-to-one relationship.
    # Many cost records can belong to one staff member.
    # on_delete=CASCADE means: if the staff member is deleted, delete their cost records too.
    # related_name='costs' lets you do:  staff_member.costs.all()
    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='costs',
        help_text="Which staff member this cost applies to"
    )

    valid_from = models.DateField(help_text="Start of the period this cost applies")
    valid_until = models.DateField(help_text="End of the period this cost applies")

    # DecimalField stores exact decimal numbers — important for money!
    # max_digits=10 means up to 10 significant digits; decimal_places=2 = pence.
    monthly_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly cost in £ (salary + on-costs)"
    )

    confidence = models.CharField(
        max_length=50,
        blank=True,
        help_text="How accurate is this figure? (e.g. 'Approx', 'Close', 'Exact')"
    )

    notes = models.TextField(blank=True, help_text="Source or explanation of this cost figure")

    def __str__(self):
        return f"{self.staff_member.initials} — £{self.monthly_cost}/mo ({self.valid_from} to {self.valid_until})"

    class Meta:
        ordering = ['staff_member', 'valid_from']


# =============================================================================
# PROJECT
# Mirrors the 'projects' sheet
# =============================================================================

class Project(models.Model):
    """
    Represents a funded research or software project.

    Mirrors the 'projects' sheet. The 'name' field is used as the primary
    identifier because that's how the spreadsheet links to allocations.
    """

    name = models.CharField(
        max_length=300,
        unique=True,
        help_text="Full project name (e.g. 'BiodiversityGenomicsEurope')"
    )

    rcode = models.CharField(
        max_length=50,
        blank=True,
        help_text="University R-code (finance reference), e.g. R127778"
    )

    # BooleanField stores True/False. null=True allows a "not set" state.
    is_active = models.BooleanField(
        null=True,
        blank=True,
        help_text="Is this project currently active?"
    )

    is_ts_required = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Timesheet (TS) required?",
        help_text="Does this project require timesheets?"
    )

    is_audited = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Audit required?",
        help_text="Is this project subject to external audit?"
    )

    # Person-months (PMs) — unit of work effort
    pm_original = models.FloatField(
        null=True, blank=True,
        help_text="Originally allocated person-months"
    )

    pm_additional = models.FloatField(
        null=True, blank=True,
        help_text="Additional person-months added later"
    )

    pm_used = models.FloatField(
        null=True, blank=True,
        help_text="Person-months already used/recorded"
    )

    start_date = models.DateField(null=True, blank=True, help_text="Project start date")
    end_date = models.DateField(null=True, blank=True, help_text="Project end date")

    work_type = models.CharField(
        max_length=200,
        blank=True,
        help_text="Type of work (e.g. 'EU Horizon', 'UKRI')"
    )

    possible_staff = models.TextField(
        blank=True,
        help_text="Free-text notes on who could work on this project"
    )

    notes = models.TextField(blank=True, help_text="General notes about this project")

    # Property: computed fields that behave like attributes but are not stored in the DB.
    @property
    def pm_available(self):
        """Calculated field: original + additional - used."""
        orig = self.pm_original or 0
        add = self.pm_additional or 0
        used = self.pm_used or 0
        return orig + add - used

    @property
    def duration_months(self):
        """Calculate project duration in months."""
        if self.start_date and self.end_date:
            delta = (self.end_date.year - self.start_date.year) * 12
            delta += self.end_date.month - self.start_date.month + 1
            return delta
        return None

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['end_date', 'name']


# =============================================================================
# PROJECT BUDGET
# Mirrors the 'project_costs' sheet — staff budget figures
# =============================================================================

class ProjectBudget(models.Model):
    """
    Financial budget for a project (as opposed to person-month allocations).
    Mirrors the 'project_costs' sheet.
    """

    # OneToOneField: each project has exactly one budget record.
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='budget',
        help_text="The project this budget belongs to"
    )

    budget_di_original = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name="Original DI (A01) budget £",
        help_text="Originally awarded budget for directly-incurred staff costs"
    )

    budget_da_original = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name="Original DA (A12) budget £",
        help_text="Originally awarded budget for directly-allocated staff costs"
    )

    budget_additional = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Any additional budget awarded"
    )

    def __str__(self):
        return f"Budget for {self.project.name}"

    @property
    def total_budget(self):
        """Sum of all budget lines."""
        return (self.budget_di_original or 0) + \
               (self.budget_da_original or 0) + \
               (self.budget_additional or 0)


# =============================================================================
# WORK PACKAGE
# Mirrors the 'project_WPs' sheet
# =============================================================================

class WorkPackage(models.Model):
    """
    A sub-division of a project — projects are broken into Work Packages (WPs),
    each with their own person-month budget and title.

    Mirrors the 'project_WPs' sheet.
    """

    # ForeignKey: many WPs can belong to one Project.
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='work_packages',
        help_text="The project this Work Package belongs to"
    )

    wp_number = models.CharField(
        max_length=20,
        help_text="Work Package identifier (e.g. 'WP1', 'WP3')"
    )

    title = models.CharField(
        max_length=500,
        blank=True,
        help_text="Full title of this Work Package"
    )

    person_months = models.FloatField(
        null=True, blank=True,
        help_text="Total person-months allocated to this Work Package"
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.project.name} — {self.wp_number}"

    class Meta:
        ordering = ['project', 'wp_number']
        # unique_together: the combination of project + wp_number must be unique.
        unique_together = [['project', 'wp_number']]


# =============================================================================
# STAFF ALLOCATION
# Mirrors the individual per-person sheets (CAG, SSR, MA, etc.)
# This is the heart of the workforce planner — who works on what and when.
# =============================================================================

class StaffAllocation(models.Model):
    """
    Records a period during which a staff member works on a specific project.

    Each row in a person's sheet (e.g. sheet 'SS') becomes one StaffAllocation.
    For example:
        Shoaib Sufi worked on EVERSE from 2024-06-01 to 2024-09-30 at 60% FTE.

    This is the central join table between Staff and Projects.
    """

    staff_member = models.ForeignKey(
        StaffMember,
        on_delete=models.CASCADE,
        related_name='allocations',
        help_text="Which person is allocated"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='allocations',
        help_text="Which project they are allocated to"
    )

    start_date = models.DateField(help_text="Start of this allocation period")
    end_date = models.DateField(help_text="End of this allocation period")

    # FTE = Full-Time Equivalent. 1.0 = 100%, 0.5 = 50%, etc.
    fte = models.FloatField(
        help_text="Fraction of full-time worked on this project (e.g. 0.5 = 50%)"
    )

    # Person-months = fte * number_of_months
    person_months = models.FloatField(
        null=True, blank=True,
        help_text="Total person-months for this allocation (FTE × months)"
    )

    # Hours per month = FTE × 143.4 (the standard productive hours/month used in the spreadsheet)
    hours_per_month = models.FloatField(
        null=True, blank=True,
        help_text="Hours per month worked on this project"
    )

    # Calculated cost for this allocation period
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True, blank=True,
        help_text="Total cost (£) of this allocation period"
    )

    work_packages = models.CharField(
        max_length=200,
        blank=True,
        help_text="Which Work Packages this person is working on (e.g. 'WP2, WP3')"
    )

    notes = models.TextField(
        blank=True,
        help_text="Any notes about this particular allocation"
    )

    @property
    def duration_months(self):
        """How many months does this allocation span?"""
        if self.start_date and self.end_date:
            delta = (self.end_date.year - self.start_date.year) * 12
            delta += self.end_date.month - self.start_date.month + 1
            return delta
        return None

    def __str__(self):
        return (
            f"{self.staff_member.initials} → {self.project.name} "
            f"({self.start_date} to {self.end_date}, {self.fte*100:.0f}% FTE)"
        )

    class Meta:
        ordering = ['staff_member', 'start_date']


# =============================================================================
# BUDGET SWAP
# Mirrors the 'swapsies' sheet — inter-project budget transfers
# =============================================================================

class BudgetSwap(models.Model):
    """
    Records transfers of budget between projects.
    When a staff member's time is paid by one project but they actually
    work on another, a swap is recorded here.

    Mirrors the 'swapsies' sheet.
    """

    # null=True on ForeignKey allows the project to not exist in our DB yet
    from_project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='swaps_out',
        help_text="Project that is paying / giving up budget"
    )

    to_project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='swaps_in',
        help_text="Project that receives the budget"
    )

    # Store the original names as text too, in case the project record is missing
    from_project_name = models.CharField(max_length=300, blank=True)
    to_project_name = models.CharField(max_length=300, blank=True)

    date = models.DateField(null=True, blank=True, help_text="When the swap occurred")
    amount_gbp = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Amount transferred in £"
    )

    notes = models.TextField(blank=True, help_text="Reason for the swap")
    action_to_balance = models.TextField(blank=True, help_text="What needs to happen to settle this")

    def __str__(self):
        from_name = self.from_project_name or str(self.from_project)
        to_name = self.to_project_name or str(self.to_project)
        return f"£{self.amount_gbp} from {from_name} → {to_name}"

    class Meta:
        ordering = ['-date']
