"""
planning/views.py — View functions for the eScience Lab Workforce Planner.
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Q
from .models import Project, StaffMember, StaffAllocation, BudgetSwap, WorkPackage, StaffCost
import datetime


def dashboard(request):
    today = datetime.date.today()

    active_projects = Project.objects.filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True),
        is_active=True
    )

    three_months_from_now = today + datetime.timedelta(days=90)
    ending_soon = Project.objects.filter(
        end_date__gte=today,
        end_date__lte=three_months_from_now,
        is_active=True
    ).order_by('end_date')

    total_staff = StaffMember.objects.count()

    current_allocations = StaffAllocation.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).select_related('staff_member', 'project')

    recent_swaps = BudgetSwap.objects.order_by('-date')[:5]

    context = {
        'active_projects_count': active_projects.count(),
        'total_staff': total_staff,
        'ending_soon': ending_soon,
        'current_allocations': current_allocations,
        'recent_swaps': recent_swaps,
        'today': today,
    }
    return render(request, 'planning/dashboard.html', context)


def project_list(request):
    """
    Shows all projects.

    STAFF TOOLTIP APPROACH:
      Django templates cannot do dict[variable_key] lookups — you can't write
      {{ my_dict[project.pk] }} in a template. The solution is to attach the
      data directly onto each project object as a plain Python attribute before
      passing it to the template. The template then accesses it as
      {{ project.staff_tooltip }} just like any other field.

      We build the tooltip text in Python from a single extra DB query
      (one query for all allocations, not one per project) and attach it
      as project.staff_tooltip — a newline-separated string of names that
      the browser renders as a multi-line native tooltip via the HTML
      'title' attribute.
    """
    today = datetime.date.today()
    projects = Project.objects.all()

    status_filter = request.GET.get('status', 'all')
    if status_filter == 'active':
        projects = projects.filter(is_active=True, end_date__gte=today)
    elif status_filter == 'ended':
        projects = projects.filter(Q(is_active=False) | Q(end_date__lt=today))
    elif status_filter == 'future':
        projects = projects.filter(start_date__gt=today)

    projects = projects.annotate(
        staff_count=Count('allocations__staff_member', distinct=True)
    ).order_by('end_date', 'name')

    # Single query: fetch all (project_id, name, initials) rows for these projects,
    # deduplicated so each person appears once per project regardless of how many
    # allocation periods they have.
    allocation_rows = (
        StaffAllocation.objects
        .filter(project__in=projects)
        .values('project_id', 'staff_member__name', 'staff_member__initials')
        .distinct()
        .order_by('staff_member__name')
    )

    # Group into a dict: project_id -> newline-separated "Name (XX)" string
    staff_by_project = {}
    for row in allocation_rows:
        pid = row['project_id']
        label = f"{row['staff_member__name']} ({row['staff_member__initials']})"
        if pid not in staff_by_project:
            staff_by_project[pid] = []
        if label not in staff_by_project[pid]:
            staff_by_project[pid].append(label)

    # Attach tooltip text directly onto each project object.
    # Django templates can read any Python attribute, not just DB fields,
    # so {{ project.staff_tooltip }} works perfectly.
    for project in projects:
        names = staff_by_project.get(project.pk, [])
        project.staff_tooltip = '\n'.join(names)

    context = {
        'projects': projects,
        'status_filter': status_filter,
        'today': today,
    }
    return render(request, 'planning/project_list.html', context)


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    allocations = project.allocations.all().select_related('staff_member').order_by('start_date')
    work_packages = project.work_packages.all().order_by('wp_number')

    try:
        budget = project.budget
    except Exception:
        budget = None

    swaps_out = project.swaps_out.all()
    swaps_in = project.swaps_in.all()
    total_pm = allocations.aggregate(total=Sum('person_months'))['total'] or 0

    context = {
        'project': project,
        'allocations': allocations,
        'work_packages': work_packages,
        'budget': budget,
        'swaps_out': swaps_out,
        'swaps_in': swaps_in,
        'total_pm': total_pm,
    }
    return render(request, 'planning/project_detail.html', context)


def staff_list(request):
    today = datetime.date.today()

    staff = StaffMember.objects.prefetch_related(
        'allocations__project'
    ).order_by('name')

    current_work = {}
    current_allocations = StaffAllocation.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).select_related('staff_member', 'project')

    for alloc in current_allocations:
        sid = alloc.staff_member_id
        if sid not in current_work:
            current_work[sid] = []
        current_work[sid].append(alloc)

    for person in staff:
        person.current_allocations = current_work.get(person.id, [])

    context = {'staff': staff, 'today': today}
    return render(request, 'planning/staff_list.html', context)


def staff_detail(request, pk):
    person = get_object_or_404(StaffMember, pk=pk)
    today = datetime.date.today()

    allocations = person.allocations.all().select_related('project').order_by('start_date')
    past    = [a for a in allocations if a.end_date < today]
    current = [a for a in allocations if a.start_date <= today <= a.end_date]
    future  = [a for a in allocations if a.start_date > today]

    costs = person.costs.all().order_by('valid_from')
    total_cost = allocations.aggregate(total=Sum('cost'))['total'] or 0

    context = {
        'person': person,
        'allocations_past': past,
        'allocations_current': current,
        'allocations_future': future,
        'costs': costs,
        'total_cost': total_cost,
        'today': today,
    }
    return render(request, 'planning/staff_detail.html', context)


def allocation_list(request):
    today = datetime.date.today()
    allocations = StaffAllocation.objects.select_related(
        'staff_member', 'project'
    ).order_by('start_date')

    if request.GET.get('current'):
        allocations = allocations.filter(start_date__lte=today, end_date__gte=today)

    staff_filter = request.GET.get('staff', '')
    if staff_filter:
        allocations = allocations.filter(staff_member__initials=staff_filter)

    project_filter = request.GET.get('project', '')
    if project_filter:
        allocations = allocations.filter(project__name__icontains=project_filter)

    all_staff = StaffMember.objects.order_by('initials')

    context = {
        'allocations': allocations,
        'all_staff': all_staff,
        'staff_filter': staff_filter,
        'project_filter': project_filter,
        'current_only': bool(request.GET.get('current')),
        'today': today,
    }
    return render(request, 'planning/allocation_list.html', context)


def swap_list(request):
    swaps = BudgetSwap.objects.select_related(
        'from_project', 'to_project'
    ).order_by('-date')

    total_swapped = swaps.aggregate(total=Sum('amount_gbp'))['total'] or 0

    context = {'swaps': swaps, 'total_swapped': total_swapped}
    return render(request, 'planning/swap_list.html', context)


def import_data(request):
    if request.method == 'POST':
        try:
            from .management.commands.import_spreadsheet import Command
            cmd = Command()
            import os
            spreadsheet_path = os.environ.get('SPREADSHEET_PATH', 'esl-workforce-plan.xlsx')
            result = cmd.import_data(spreadsheet_path)
            message = f"Import complete. {result}"
            success = True
        except Exception as e:
            message = f"Import failed: {e}"
            success = False

        context = {'message': message, 'success': success}
        return render(request, 'planning/import_result.html', context)

    return render(request, 'planning/import_data.html', {})
