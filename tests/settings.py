USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "example.sqlite",
    }
}

ROOT_URLCONF = "djmoney_rates.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "djmoney_rates",
]

SECRET_KEY = "1234567890evonove"

TEMPLATES = [
    {
        'OPTIONS': {
            'debug': True,
        }
    }
]

SITE_ID = 1
