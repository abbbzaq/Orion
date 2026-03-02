from django.contrib import admin

from .models import SysGroup, SysGroupMenu, SysMenu, SysUser, SysUserGroup


@admin.register(SysUser)
class SysUserAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "display_name", "phone", "status", "updated_at")
	search_fields = ("user__username", "display_name", "phone")
	list_filter = ("status",)
	readonly_fields = ("created_at", "updated_at")
	ordering = ("-updated_at",)
	list_per_page = 20
	list_select_related = ("user",)


@admin.register(SysGroup)
class SysGroupAdmin(admin.ModelAdmin):
	list_display = ("id", "group_name", "status", "updated_at")
	search_fields = ("group_name", "description")
	list_filter = ("status",)
	readonly_fields = ("created_at", "updated_at")
	ordering = ("-updated_at",)
	list_per_page = 20


@admin.register(SysUserGroup)
class SysUserGroupAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "group")
	search_fields = ("user__username", "group__group_name")
	list_filter = ("group",)
	ordering = ("-id",)
	list_per_page = 20
	list_select_related = ("user", "group")


@admin.register(SysMenu)
class SysMenuAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"menu_name",
		"menu_type",
		"parent",
		"path",
		"permission_code",
		"sort",
		"visible",
		"status",
	)
	search_fields = ("menu_name", "path", "permission_code")
	list_filter = ("menu_type", "visible", "status")
	readonly_fields = ("created_at", "updated_at")
	ordering = ("sort", "id")
	list_per_page = 20
	list_select_related = ("parent",)


@admin.register(SysGroupMenu)
class SysGroupMenuAdmin(admin.ModelAdmin):
	list_display = ("id", "group", "menu")
	search_fields = ("group__group_name", "menu__menu_name")
	list_filter = ("group",)
	ordering = ("-id",)
	list_per_page = 20
	list_select_related = ("group", "menu")
