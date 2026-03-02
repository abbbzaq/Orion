from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cmdb_backend.permissions import IsAdminOnly
from .models import SysGroup, SysGroupMenu, SysMenu, SysUser, SysUserGroup
from .serializers import (
	SysGroupMenuSerializer,
	SysGroupSerializer,
	SysMenuSerializer,
	SysUserGroupSerializer,
	SysUserSerializer,
)

User = get_user_model()

ROLE_GROUP_NAMES = {
	"admin": "管理员",
	"ops": "运维",
	"readonly": "只读",
}

ROLE_ALIASES = {
	"admin": {"admin", "administrator", "管理员"},
	"ops": {"ops", "operation", "运维"},
	"readonly": {"readonly", "read_only", "viewer", "只读"},
}


def normalize_role(value: str) -> str:
	text = (value or "").strip().lower()
	for role, aliases in ROLE_ALIASES.items():
		if text in aliases:
			return role
	return ""


class SysUserViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = SysUser.objects.select_related("user").all().order_by("-created_at")
	serializer_class = SysUserSerializer
	permission_classes = [IsAdminOnly]

	@action(detail=False, methods=["post"], url_path="assign-role")
	def assign_role(self, request):
		username = request.data.get("username")
		raw_role = request.data.get("role")
		role = normalize_role(raw_role)

		if not username or not role:
			return Response(
				{
					"detail": "参数错误：username 与 role 必填，role 仅支持 admin/ops/readonly。",
				},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			return Response({"detail": "用户不存在。"}, status=status.HTTP_404_NOT_FOUND)

		target_group_name = ROLE_GROUP_NAMES[role]
		target_group, _ = SysGroup.objects.get_or_create(
			group_name=target_group_name,
			defaults={"description": f"{target_group_name}角色", "status": "active"},
		)

		role_group_names = list(ROLE_GROUP_NAMES.values())
		old_role_group_ids = SysGroup.objects.filter(group_name__in=role_group_names).values_list("id", flat=True)
		SysUserGroup.objects.filter(user=user, group_id__in=old_role_group_ids).delete()
		SysUserGroup.objects.get_or_create(user=user, group=target_group)

		user.is_staff = True
		user.is_superuser = role == "admin"
		user.save(update_fields=["is_staff", "is_superuser"])

		return Response(
			{
				"username": user.username,
				"role": role,
				"group_name": target_group_name,
			},
			status=status.HTTP_200_OK,
		)


class SysGroupViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = SysGroup.objects.all().order_by("-created_at")
	serializer_class = SysGroupSerializer
	permission_classes = [IsAdminOnly]


class SysMenuViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = SysMenu.objects.select_related("parent").all().order_by("sort", "id")
	serializer_class = SysMenuSerializer
	permission_classes = [IsAdminOnly]


class SysUserGroupViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = SysUserGroup.objects.select_related("user", "group").all().order_by("-id")
	serializer_class = SysUserGroupSerializer
	permission_classes = [IsAdminOnly]


class SysGroupMenuViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = SysGroupMenu.objects.select_related("group", "menu").all().order_by("-id")
	serializer_class = SysGroupMenuSerializer
	permission_classes = [IsAdminOnly]
