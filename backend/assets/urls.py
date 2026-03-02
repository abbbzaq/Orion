from rest_framework import routers

from .views import CloudAccountViewSet, CloudInstanceViewSet

router = routers.DefaultRouter()
router.register(r"accounts", CloudAccountViewSet, basename="cloudaccount")
router.register(r"instances", CloudInstanceViewSet, basename="cloudinstance")

urlpatterns = router.urls
