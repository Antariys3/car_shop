from .settings import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
DEBUG = True

# Use local static files instead of Amazon S3 storage for tests
AWS_STORAGE_BUCKET_NAME = "your-test-bucket-name"
AWS_S3_ACCESS_KEY_ID = "your-test-access-key-id"
AWS_S3_SECRET_ACCESS_KEY = "your-test-secret-access-key"
AWS_S3_REGION_NAME = "eu-north-1"

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "LOCATION": BASE_DIR / "staticfiles",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "LOCATION": BASE_DIR / "media",
    },
}
