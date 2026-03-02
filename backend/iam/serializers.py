from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SysGroup, SysGroupMenu, SysMenu, SysUser, SysUserGroup

User = get_user_model()


class SysUserSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user")
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = SysUser
        fields = [
            "id",
            "user_id",
            "username",
            "display_name",
            "phone",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "username"]


class SysGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysGroup
        fields = [
            "id",
            "group_name",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SysMenuSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=SysMenu.objects.all(), source="parent", allow_null=True, required=False
    )

    class Meta:
        model = SysMenu
        fields = [
            "id",
            "parent_id",
            "menu_name",
            "menu_type",
            "path",
            "component",
            "permission_code",
            "sort",
            "visible",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SysUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUserGroup
        fields = ["id", "user", "group"]
        read_only_fields = ["id"]


class SysGroupMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysGroupMenu
        fields = ["id", "group", "menu"]
        read_only_fields = ["id"]
