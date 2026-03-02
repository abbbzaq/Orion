from django.contrib import admin

from .models import CloudAccount, CloudDisk, CloudInstance, CloudNetwork, CloudTag


@admin.register(CloudAccount)
class CloudAccountAdmin(admin.ModelAdmin):
	list_display = ("id", "provider", "account_id", "project_name", "status", "updated_at")
	search_fields = ("provider", "account_id", "project_name")
	list_filter = ("provider", "status")
	readonly_fields = ("created_at", "updated_at")
	ordering = ("-updated_at",)
	list_per_page = 20


@admin.register(CloudInstance)
class CloudInstanceAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"instance_id",
		"name",
		"account",
		"region",
		"status",
		"owner",
		"env",
		"updated_at",
	)
	search_fields = ("instance_id", "name", "private_ip", "public_ip", "owner")
	list_filter = ("status", "charge_type", "env", "region")
	readonly_fields = ("created_at", "updated_at")
	ordering = ("-updated_at",)
	list_per_page = 20
	list_select_related = ("account",)


@admin.register(CloudDisk)
class CloudDiskAdmin(admin.ModelAdmin):
	list_display = ("id", "disk_id", "disk_type", "size_gb", "encrypted", "instance", "status")
	search_fields = ("disk_id", "instance__instance_id")
	list_filter = ("disk_type", "encrypted", "status")
	readonly_fields = ("created_at", "updated_at")
	ordering = ("-updated_at",)
	list_per_page = 20
	list_select_related = ("instance",)


@admin.register(CloudNetwork)
class CloudNetworkAdmin(admin.ModelAdmin):
	list_display = ("id", "instance", "vpc_id", "subnet_id", "security_group_id", "cidr", "updated_at")
	search_fields = ("instance__instance_id", "vpc_id", "subnet_id", "security_group_id")
	readonly_fields = ("updated_at",)
	ordering = ("-updated_at",)
	list_per_page = 20
	list_select_related = ("instance",)


@admin.register(CloudTag)
class CloudTagAdmin(admin.ModelAdmin):
	list_display = ("id", "instance", "tag_key", "tag_value")
	search_fields = ("instance__instance_id", "tag_key", "tag_value")
	list_filter = ("tag_key",)
	ordering = ("-id",)
	list_per_page = 20
	list_select_related = ("instance",)
