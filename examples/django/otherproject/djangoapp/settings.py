from otherproject.config import config


SECRET_KEY = "django-insecure-042da!xqzr+^+e&aw+ioy$mvv)17j*6)_3#j#@zseicr#+oli-"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "otherproject.djangoapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": "localhost",
        "PORT": config["postgres_port"],
        "NAME": config["postgres_dbname"],
        "USER": config["postgres_username"],
        "PASSWORD": config["postgres_password"],
        "AUTOCOMMIT": True,
    }
}

STATIC_URL = config["django_static_url"]
STATIC_ROOT = config["django_static_root"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
