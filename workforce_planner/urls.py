"""
workforce_planner/urls.py — The ROOT URL configuration.

HOW DJANGO ROUTING WORKS:
  1. A browser requests a URL, e.g. /projects/
  2. Django looks here first (ROOT_URLCONF = 'workforce_planner.urls')
  3. It goes through the urlpatterns list from top to bottom
  4. When a pattern matches the URL, it calls the associated view (or includes
     another urls.py file for further matching)
  5. The view returns an HTTP response (usually rendered HTML)

The 'include()' function is a way of splitting URLs across multiple files.
Here we say "any URL starting with '' (i.e. everything) should be looked up
in planning/urls.py". This keeps each app's URLs self-contained.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # The built-in Django admin panel — free CRUD interface at /admin/
    # Very useful for inspecting and editing data during development.
    path('admin/', admin.site.urls),

    # Delegate ALL other URLs to our planning app's urls.py file.
    # include() simply reads planning/urls.py and checks it for further matches.
    path('', include('planning.urls')),
]
