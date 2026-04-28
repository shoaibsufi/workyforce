"""
settings.py — Django's main configuration file.

Think of this as the "control panel" for the entire project. Django reads this
file at startup and uses it to configure everything: the database, installed
apps, templates, static files, etc.

HOW TO USE:
  - You must set SECRET_KEY to something secret in production (not this placeholder).
  - DEBUG=True is fine locally; set it to False before deploying publicly.
  - ALLOWED_HOSTS must list your server's domain/IP in production.
"""

from pathlib import Path

# BASE_DIR is the absolute path to the root of your project.
# Path(__file__) is the path to this settings file; .resolve().parent.parent
# goes two levels up — first to workforce_planner/, then to the project root.
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------------
# SECURITY
# -------------------------------------------------------------------------

# SECRET_KEY is used to sign cookies, sessions, tokens etc.
# NEVER commit a real key to version control.
SECRET_KEY = 'django-insecure-change-me-before-deploying-to-production'

# DEBUG=True means Django shows detailed error pages and reloads code on change.
# Always False in production — it would expose your internals to the world.
DEBUG = True

# Which hostnames Django is allowed to serve.
# '*' means "any" — fine for local dev, but tighten this for production.
ALLOWED_HOSTS = ['*']

# -------------------------------------------------------------------------
# INSTALLED APPS
# -------------------------------------------------------------------------
# Django is built around "apps" — self-contained modules of functionality.
# You must register every app here so Django knows to include it.
INSTALLED_APPS = [
    # Django's own built-in apps:
    'django.contrib.admin',        # The automatic admin interface (/admin/)
    'django.contrib.auth',         # User authentication (login, logout, etc.)
    'django.contrib.contenttypes', # Framework for generic relations
    'django.contrib.sessions',     # Session management (remembering users)
    'django.contrib.messages',     # One-time flash messages (e.g. "Saved!")
    'django.contrib.staticfiles',  # Serving CSS/JS/images

    # Our custom app — this is where all our workforce planning logic lives.
    'planning',
]

# -------------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------------
# Middleware are hooks that process every HTTP request and response.
# They run in order on the way IN and in reverse order on the way OUT.
# Think of them as a stack of wrappers around your view functions.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',       # Security headers
    'django.contrib.sessions.middleware.SessionMiddleware', # Session handling
    'django.middleware.common.CommonMiddleware',            # URL normalisation
    'django.middleware.csrf.CsrfViewMiddleware',           # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Attaches user to request
    'django.contrib.messages.middleware.MessageMiddleware', # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Clickjacking protection
]

# -------------------------------------------------------------------------
# URL CONFIGURATION
# -------------------------------------------------------------------------
# This tells Django where to find the "root" URL patterns file.
# Django reads urls.py to know which URL maps to which view.
ROOT_URLCONF = 'workforce_planner.urls'

# -------------------------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------------------------
# Templates are HTML files with special Django template tags ({% ... %}, {{ ... }})
# that get filled in with real data before being sent to the browser.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS: extra directories to search for templates.
        # We use BASE_DIR / 'templates' for project-wide base templates.
        'DIRS': [BASE_DIR / 'templates'],
        # APP_DIRS=True also looks inside each app's own templates/ folder.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # These inject variables into every template automatically.
                # e.g. 'request' gives templates access to the current HTTP request.
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -------------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------------
# Django supports multiple databases (PostgreSQL, MySQL, etc.)
# SQLite is the default — it's a single file, zero configuration, great for dev.
# When you're ready for production, swap this out for PostgreSQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # The database will be created as a file called db.sqlite3 in BASE_DIR.
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------------------------------------------------------------
# STATIC FILES (CSS, JavaScript, Images)
# -------------------------------------------------------------------------
# When DEBUG=True, Django serves static files automatically.
# In production you'd use a proper web server (nginx) or a CDN for this.
STATIC_URL = 'static/'

# -------------------------------------------------------------------------
# DEFAULT PRIMARY KEY TYPE
# -------------------------------------------------------------------------
# Every Django model gets an auto-generated primary key "id" field.
# BigAutoField uses a 64-bit integer — essentially unlimited records.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
