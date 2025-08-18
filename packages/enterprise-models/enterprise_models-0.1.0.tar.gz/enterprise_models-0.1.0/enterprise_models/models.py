from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

optional = {"null": True, "blank": True}


class GenericModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **optional,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **optional,
        related_name="+",
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **optional,
        related_name="+",
    )

    class Meta:
        abstract = True


class Contractor(GenericModel):
    contractor_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.contractor_name

class Department(GenericModel):
    department_number = models.CharField(max_length=50, unique=True)
    department_name = models.CharField(max_length=100)

    l1_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **optional,
        related_name='l1_departments'
    )

    l2_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **optional,
        related_name='l2_departments'
    )

    effective_start_date = models.DateField(**optional)
    effective_end_date = models.DateField(**optional)

    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive')]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active',
        db_index=True
    )

    def save(self, *args, **kwargs):
        self.group_type = 'Department'  # Automatically set group_type
        super().save(*args, **kwargs)
