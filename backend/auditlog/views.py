from rest_framework import mixins, viewsets

from cmdb_backend.permissions import IsCMDBMember
from .models import ChangeLog
from .serializers import ChangeLogSerializer


class ChangeLogViewSet(
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	viewsets.GenericViewSet,
):
	queryset = ChangeLog.objects.all().order_by("-changed_at")
	serializer_class = ChangeLogSerializer
	permission_classes = [IsCMDBMember]

	def get_queryset(self):
		queryset = self.queryset
		resource_type = self.request.query_params.get("resource_type")
		resource_id = self.request.query_params.get("resource_id")
		operator = self.request.query_params.get("operator")
		field = self.request.query_params.get("field")
		start_time = self.request.query_params.get("start_time")
		end_time = self.request.query_params.get("end_time")

		if resource_type:
			queryset = queryset.filter(resource_type=resource_type)
		if resource_id:
			queryset = queryset.filter(resource_id=resource_id)
		if operator:
			queryset = queryset.filter(operator=operator)
		if field:
			queryset = queryset.filter(field=field)
		if start_time:
			queryset = queryset.filter(changed_at__gte=start_time)
		if end_time:
			queryset = queryset.filter(changed_at__lte=end_time)

		return queryset
