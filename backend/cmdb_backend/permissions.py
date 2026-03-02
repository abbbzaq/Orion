from rest_framework.permissions import SAFE_METHODS, BasePermission

from iam.models import SysUserGroup


ROLE_ALIASES = {
    "admin": {"admin", "administrator", "管理员"},
    "ops": {"ops", "operation", "运维"},
    "readonly": {"readonly", "read_only", "viewer", "只读"},
}


def _normalize_role(group_name: str) -> str:
    value = (group_name or "").strip().lower()
    for role, aliases in ROLE_ALIASES.items():
        if value in aliases:
            return role
    return ""


def get_user_roles(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()
    if user.is_superuser:
        return {"admin", "ops", "readonly"}

    group_names = SysUserGroup.objects.filter(user=user).values_list("group__group_name", flat=True)
    roles = {_normalize_role(name) for name in group_names}
    return {role for role in roles if role}


class IsCMDBMember(BasePermission):
    message = "无权限访问，请联系管理员分配CMDB角色。"

    def has_permission(self, request, view):
        return bool(get_user_roles(request.user))


class IsAdminOrOpsWriteElseRead(BasePermission):
    message = "当前角色无此操作权限。"

    def has_permission(self, request, view):
        roles = get_user_roles(request.user)
        if not roles:
            return False
        if request.method in SAFE_METHODS:
            return bool(roles & {"admin", "ops", "readonly"})
        return bool(roles & {"admin", "ops"})


class IsAdminOnly(BasePermission):
    message = "仅管理员可操作该接口。"

    def has_permission(self, request, view):
        roles = get_user_roles(request.user)
        return "admin" in roles
