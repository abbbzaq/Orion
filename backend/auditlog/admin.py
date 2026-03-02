from django.contrib import admin

from .models import ChangeLog


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"resource_type",
		"resource_id",
		"field",
		"operator",
		"source",
		"changed_at",
	)
	search_fields = ("resource_type", "resource_id", "field", "operator")
	list_filter = ("resource_type", "source", "changed_at")
	readonly_fields = ("changed_at",)
	ordering = ("-changed_at",)
	list_per_page = 20
