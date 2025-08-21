# dj
from django.db import models

# internal
from .utils import clean_json_data


class Bill(models.Model):
    """Bill"""

    backend = models.CharField(max_length=150)
    amount = models.PositiveBigIntegerField()
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    extra = models.JSONField(default=dict)
    next_step = models.URLField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def has_next_step(self):
        return True if self.next_step else False

    def clean_extra(self):
        self.extra = clean_json_data(self.extra)

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.clean_extra()
        return super().save(*args, force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.backend}-{self.id}"

    def __repr__(self):
        return f"Bill(id={self.id}, backend={self.backend})"
