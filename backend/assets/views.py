from django.db.models import Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from auditlog.models import ChangeLog
from cmdb_backend.permissions import IsAdminOrOpsWriteElseRead
from .models import CloudAccount, CloudInstance
from .serializers import (
	CloudAccountSerializer,
	CloudInstanceRelationSerializer,
	CloudInstanceSerializer,
)


class CloudAccountViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = CloudAccount.objects.all().order_by("-created_at")
	serializer_class = CloudAccountSerializer
	permission_classes = [IsAdminOrOpsWriteElseRead]

	def perform_create(self, serializer):
		obj = serializer.save()
		ChangeLog.objects.create(
			resource_type="cloud_account",
			resource_id=str(obj.id),
			field="create",
			old_value="",
			new_value=f"{obj.provider}:{obj.account_id}:{obj.project_name}",
			operator=self._operator(),
			source="manual",
		)

	def perform_update(self, serializer):
		instance = self.get_object()
		old_values = {
			"provider": instance.provider,
			"account_id": instance.account_id,
			"project_name": instance.project_name,
			"auth_ref": instance.auth_ref,
			"status": instance.status,
		}
		obj = serializer.save()
		for field_name, old_value in old_values.items():
			new_value = getattr(obj, field_name)
			if old_value != new_value:
				ChangeLog.objects.create(
					resource_type="cloud_account",
					resource_id=str(obj.id),
					field=field_name,
					old_value=str(old_value),
					new_value=str(new_value),
					operator=self._operator(),
					source="manual",
				)

	def perform_destroy(self, instance):
		resource_id = str(instance.id)
		ChangeLog.objects.create(
			resource_type="cloud_account",
			resource_id=resource_id,
			field="delete",
			old_value=f"{instance.provider}:{instance.account_id}:{instance.project_name}",
			new_value="",
			operator=self._operator(),
			source="manual",
		)
		instance.delete()

	def _operator(self):
		if self.request.user and self.request.user.is_authenticated:
			return self.request.user.username
		return "system"


class CloudInstanceViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = CloudInstance.objects.select_related("account").all().order_by("-created_at")
	serializer_class = CloudInstanceSerializer
	permission_classes = [IsAdminOrOpsWriteElseRead]

	def get_queryset(self):
		queryset = self.queryset
		provider = self.request.query_params.get("provider")
		account_id = self.request.query_params.get("account_id")
		region = self.request.query_params.get("region")
		status_value = self.request.query_params.get("status")
		owner = self.request.query_params.get("owner")
		env = self.request.query_params.get("env")
		tag_key = self.request.query_params.get("tag_key")
		tag_value = self.request.query_params.get("tag_value")

		if provider:
			queryset = queryset.filter(account__provider=provider)
		if account_id:
			queryset = queryset.filter(account_id=account_id)
		if region:
			queryset = queryset.filter(region=region)
		if status_value:
			queryset = queryset.filter(status=status_value)
		if owner:
			queryset = queryset.filter(owner=owner)
		if env:
			queryset = queryset.filter(env=env)
		if tag_key:
			queryset = queryset.filter(tags__tag_key=tag_key)
		if tag_value:
			queryset = queryset.filter(tags__tag_value=tag_value)

		return queryset.distinct()

	def perform_create(self, serializer):
		obj = serializer.save()
		ChangeLog.objects.create(
			resource_type="cloud_instance",
			resource_id=obj.instance_id,
			field="create",
			old_value="",
			new_value=obj.name,
			operator=self._operator(),
			source="manual",
		)

	def perform_update(self, serializer):
		instance = self.get_object()
		old_values = {
			"name": instance.name,
			"region": instance.region,
			"zone": instance.zone,
			"instance_type": instance.instance_type,
			"private_ip": instance.private_ip,
			"public_ip": instance.public_ip,
			"status": instance.status,
			"owner": instance.owner,
			"env": instance.env,
		}
		obj = serializer.save()
		for field_name, old_value in old_values.items():
			new_value = getattr(obj, field_name)
			if old_value != new_value:
				ChangeLog.objects.create(
					resource_type="cloud_instance",
					resource_id=obj.instance_id,
					field=field_name,
					old_value=str(old_value),
					new_value=str(new_value),
					operator=self._operator(),
					source="manual",
				)

	def perform_destroy(self, instance):
		ChangeLog.objects.create(
			resource_type="cloud_instance",
			resource_id=instance.instance_id,
			field="delete",
			old_value=instance.name,
			new_value="",
			operator=self._operator(),
			source="manual",
		)
		instance.delete()

	@action(detail=True, methods=["get"], url_path="relations")
	def relations(self, request, pk=None):
		instance = self.get_object()
		serializer = CloudInstanceRelationSerializer(instance)
		return Response(serializer.data)

	@action(detail=False, methods=["get"], url_path="alerts")
	def alerts(self, request):
		required_tags = ["env", "business_unit", "owner", "cost_center", "service_name"]
		missing_owner = self.get_queryset().filter(Q(owner="") | Q(owner__isnull=True))
		missing_tags = self.get_queryset().annotate(
			required_tag_count=Count(
				"tags__tag_key",
				filter=Q(tags__tag_key__in=required_tags),
				distinct=True,
			)
		).filter(required_tag_count__lt=len(required_tags))
		high_risk = self.get_queryset().filter(
			networks__inbound_rules__icontains="0.0.0.0/0"
		).filter(
			Q(networks__inbound_rules__icontains="22") | Q(networks__inbound_rules__icontains="3389")
		)

		payload = {
			"required_tags": required_tags,
			"missing_owner_count": missing_owner.distinct().count(),
			"missing_tags_count": missing_tags.distinct().count(),
			"high_risk_port_count": high_risk.distinct().count(),
			"missing_owner_samples": list(missing_owner.values("id", "instance_id", "name")[:10]),
			"missing_tags_samples": list(missing_tags.values("id", "instance_id", "name")[:10]),
			"high_risk_port_samples": list(high_risk.values("id", "instance_id", "name")[:10]),
		}
		return Response(payload, status=status.HTTP_200_OK)

	def _operator(self):
		if self.request.user and self.request.user.is_authenticated:
			return self.request.user.username
		return "system"
