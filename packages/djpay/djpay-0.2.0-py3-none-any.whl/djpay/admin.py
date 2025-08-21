# dj
from django.contrib import admin

# internal
from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Bill Admin"""

    model = Bill

    list_display = ["__str__", "amount", "created_at", "verified"]
    list_filter = ["backend", "verified", "created_at"]
