from rest_framework import serializers

from .models import ChangeLog


class ChangeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeLog
        fields = [
            "id",
            "resource_type",
            "resource_id",
            "field",
            "old_value",
            "new_value",
            "operator",
            "source",
            "changed_at",
        ]
        read_only_fields = ["id", "changed_at"]
