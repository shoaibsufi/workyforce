"""
planning/urls.py — URL patterns for the planning app.

HOW URL ROUTING WORKS (recap):
  1. Django checks each pattern in order until one matches
  2. path('projects/', ...) matches exactly '/projects/'
  3. path('projects/<int:pk>/', ...) matches '/projects/42/' and passes pk=42 to the view
  4. The name= argument lets you refer to URLs by name in templates:
       {% url 'project_list' %}  instead of hardcoding '/projects/'
     This means if you change the URL path, templates update automatically.

URL PARAMETER TYPES:
  <int:pk>    → matches an integer, passes it as an int named 'pk'
  <str:name>  → matches any string, passes it as 'name'
  <slug:slug> → matches URL-safe strings (letters, numbers, hyphens)
"""

from django.urls import path
from . import views   # Import views from the same package (planning/)

# app_name allows namespacing — you'd refer to URLs as 'planning:project_list'
# This prevents clashes if multiple apps have a view called 'list'.
app_name = 'planning'

urlpatterns = [
    # -------------------------------------------------------------------------
    # HOME / DASHBOARD
    # -------------------------------------------------------------------------
    # '' matches the root URL '/'
    path('', views.dashboard, name='dashboard'),

    # -------------------------------------------------------------------------
    # PROJECTS
    # -------------------------------------------------------------------------
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),

    # -------------------------------------------------------------------------
    # STAFF
    # -------------------------------------------------------------------------
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),

    # -------------------------------------------------------------------------
    # ALLOCATIONS
    # -------------------------------------------------------------------------
    path('allocations/', views.allocation_list, name='allocation_list'),

    # -------------------------------------------------------------------------
    # BUDGET SWAPS
    # -------------------------------------------------------------------------
    path('swaps/', views.swap_list, name='swap_list'),

    # -------------------------------------------------------------------------
    # DATA IMPORT
    # -------------------------------------------------------------------------
    # This page triggers the spreadsheet import
    path('import/', views.import_data, name='import_data'),
]
