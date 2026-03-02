from rest_framework import serializers

from .models import CloudAccount, CloudDisk, CloudInstance, CloudNetwork, CloudTag


class CloudAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudAccount
        fields = [
            "id",
            "provider",
            "account_id",
            "project_name",
            "auth_ref",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CloudInstanceSerializer(serializers.ModelSerializer):
    account = CloudAccountSerializer(read_only=True)
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=CloudAccount.objects.all(), source="account", write_only=True
    )

    class Meta:
        model = CloudInstance
        fields = [
            "id",
            "instance_id",
            "name",
            "account",
            "account_id",
            "region",
            "zone",
            "instance_type",
            "image_id",
            "os_type",
            "private_ip",
            "public_ip",
            "status",
            "charge_type",
            "owner",
            "env",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "account"]


class CloudDiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudDisk
        fields = [
            "id",
            "disk_id",
            "disk_type",
            "size_gb",
            "encrypted",
            "status",
            "created_at",
            "updated_at",
        ]


class CloudNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudNetwork
        fields = [
            "id",
            "vpc_id",
            "subnet_id",
            "security_group_id",
            "cidr",
            "inbound_rules",
            "outbound_rules",
            "updated_at",
        ]


class CloudTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudTag
        fields = ["id", "tag_key", "tag_value"]


class CloudInstanceRelationSerializer(serializers.ModelSerializer):
    account = CloudAccountSerializer(read_only=True)
    disks = CloudDiskSerializer(many=True, read_only=True)
    networks = CloudNetworkSerializer(many=True, read_only=True)
    tags = CloudTagSerializer(many=True, read_only=True)

    class Meta:
        model = CloudInstance
        fields = [
            "id",
            "instance_id",
            "name",
            "account",
            "region",
            "zone",
            "instance_type",
            "status",
            "owner",
            "env",
            "private_ip",
            "public_ip",
            "disks",
            "networks",
            "tags",
            "updated_at",
        ]
