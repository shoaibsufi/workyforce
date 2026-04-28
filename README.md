# eScience Lab Workforce Planner — Django App

A web application that replaces the Excel workforce planning spreadsheet with
a proper database-backed web interface. Built with Django.

---

## What This Does

- Stores all staff, projects, work packages, allocations, and budget swaps in a database
- Provides a web interface to browse, filter, and explore the data
- Imports data from your existing Excel spreadsheet
- Includes Django's admin panel for editing records

---

## Project Structure

```
workforce_planner/          ← Project root
│
├── manage.py               ← Django CLI tool (run everything from here)
├── requirements.txt        ← Python packages to install
│
├── workforce_planner/      ← Project configuration package
│   ├── settings.py         ← All Django configuration (DB, apps, etc.)
│   ├── urls.py             ← Root URL routing
│   └── wsgi.py             ← Production server entry point
│
└── planning/               ← The main Django "app"
    ├── models.py           ← Database tables (Staff, Project, Allocation, etc.)
    ├── views.py            ← Request handlers (dashboard, project list, etc.)
    ├── urls.py             ← URL patterns for this app
    ├── admin.py            ← Django admin configuration
    ├── templates/
    │   └── planning/
    │       ├── base.html           ← Shared layout (nav bar, styles)
    │       ├── dashboard.html      ← Home page
    │       ├── project_list.html   ← All projects
    │       ├── project_detail.html ← Single project page
    │       ├── staff_list.html     ← All staff
    │       ├── staff_detail.html   ← Single staff member page
    │       ├── allocation_list.html
    │       ├── swap_list.html
    │       ├── import_data.html
    │       └── import_result.html
    └── management/
        └── commands/
            └── import_spreadsheet.py  ← CLI command to import Excel data
```

---

## Setup Instructions

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Create the database

Django uses "migrations" to create database tables from your model definitions.
This is a two-step process:

```bash
# Step 1: Generate migration files (detects changes to models.py)
python manage.py makemigrations planning

# Step 2: Apply migrations (creates the actual database tables)
python manage.py migrate
```

After this you'll have a `db.sqlite3` file — your entire database in one file.

### 3. Create an admin user

This lets you log in to the Django admin panel at /admin/

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username and password.

### 4. Import the spreadsheet

Place the Excel file in the project root, then run:

```bash
python manage.py import_spreadsheet
```

Or specify a custom path:

```bash
python manage.py import_spreadsheet --file=/path/to/your/spreadsheet.xlsx
```

You can also trigger the import from the web interface at /import/

### 5. Start the development server

```bash
python manage.py runserver
```

Then open your browser at: http://localhost:8000/

---

## Key URLs

| URL | What it shows |
|-----|---------------|
| / | Dashboard — summary stats and active allocations |
| /projects/ | All projects with filtering |
| /projects/42/ | Detail page for project with id=42 |
| /staff/ | All staff members |
| /staff/7/ | Detail page for staff member with id=7 |
| /allocations/ | All allocations with filters |
| /swaps/ | Budget swaps |
| /import/ | Trigger spreadsheet import |
| /admin/ | Django admin panel (login required) |

---

## Django Concepts Quick Reference

### The URL → View → Template flow

1. Browser requests `/projects/`
2. Django reads `urls.py` → finds `path('projects/', views.project_list, ...)`
3. Django calls `project_list(request)` in `views.py`
4. The view queries the database: `Project.objects.all()`
5. The view calls `render(request, 'planning/project_list.html', {'projects': ...})`
6. Django fills in the template with the data and returns HTML

### ORM Quick Reference

```python
# Get all records
Project.objects.all()

# Filter records
Project.objects.filter(is_active=True)
Project.objects.filter(end_date__gte=datetime.date.today())  # >= today

# Get a single record (raises DoesNotExist if not found)
Project.objects.get(pk=1)

# Get or 404 (use in views with URL parameters)
from django.shortcuts import get_object_or_404
project = get_object_or_404(Project, pk=pk)

# Create a record
p = Project(name='My Project')
p.save()

# Get or create
obj, created = Project.objects.get_or_create(name='My Project', defaults={...})

# Follow relationships
project.allocations.all()  # all allocations for a project (uses related_name)
alloc.staff_member.name    # the name of the staff member on an allocation
```

### Template Quick Reference

```html
{{ variable }}              Output a variable
{{ variable|filter }}       Apply a filter (e.g. |date:"M Y", |truncatechars:50)
{% if condition %}...{% endif %}
{% for item in list %}...{% empty %}...{% endfor %}
{% url 'planning:project_list' %}    Generate a URL by name
{% url 'planning:project_detail' project.pk %}  URL with parameter
{% extends 'planning/base.html' %}  Inherit from base template
{% block name %}...{% endblock %}   Define/override a block
{% include 'partial.html' %}        Include a sub-template
{% csrf_token %}                    Required in POST forms
```

---

## Updating the App

If you change `models.py`:
```bash
python manage.py makemigrations planning
python manage.py migrate
```

If you update the spreadsheet and want to re-import:
```bash
python manage.py import_spreadsheet
```
(Safe to run multiple times — won't create duplicates)
