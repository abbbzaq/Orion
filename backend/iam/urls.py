from rest_framework import routers

from .views import (
    SysGroupMenuViewSet,
    SysGroupViewSet,
    SysMenuViewSet,
    SysUserGroupViewSet,
    SysUserViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", SysUserViewSet, basename="sysuser")
router.register(r"groups", SysGroupViewSet, basename="sysgroup")
router.register(r"menus", SysMenuViewSet, basename="sysmenu")
router.register(r"user-groups", SysUserGroupViewSet, basename="sysusergroup")
router.register(r"group-menus", SysGroupMenuViewSet, basename="sysgroupmenu")

urlpatterns = router.urls
