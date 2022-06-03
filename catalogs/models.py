from django.db import models

from users.models import User

class Catalog(models.Model):
    name = models.CharField(
        max_length=100, help_text="Name of Catalog", unique=True
    )
    file_name = models.CharField(
        max_length=100, help_text="Location of static catolog data file", unique=True
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True, null=True)