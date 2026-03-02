from rest_framework import routers

from .views import ChangeLogViewSet

router = routers.DefaultRouter()
router.register(r"change-logs", ChangeLogViewSet, basename="changelog")

urlpatterns = router.urls
