from core.choices import DataSourceStatusChoices
from netbox.api.fields import ChoiceField
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from netbox_branching.api.serializers import BranchSerializer
from rest_framework import serializers

from .nested_serializers import NestedIPFabricSnapshotSerializer
from .nested_serializers import NestedIPFabricSourceSerializer
from .nested_serializers import NestedIPFabricSyncSerializer
from .nested_serializers import NestedIPFabricTransformMapSerializer
from ipfabric_netbox.models import IPFabricIngestion
from ipfabric_netbox.models import IPFabricIngestionIssue
from ipfabric_netbox.models import IPFabricRelationshipField
from ipfabric_netbox.models import IPFabricSnapshot
from ipfabric_netbox.models import IPFabricSource
from ipfabric_netbox.models import IPFabricSync
from ipfabric_netbox.models import IPFabricTransformField
from ipfabric_netbox.models import IPFabricTransformMap
from ipfabric_netbox.models import IPFabricTransformMapGroup

__all__ = (
    "IPFabricSyncSerializer",
    "IPFabricSnapshotSerializer",
    "IPFabricRelationshipFieldSerializer",
    "IPFabricTransformFieldSerializer",
    "IPFabricTransformMapSerializer",
    "IPFabricTransformMapGroupSerializer",
    "IPFabricIngestionSerializer",
    "IPFabricIngestionIssueSerializer",
    "IPFabricSourceSerializer",
)


class IPFabricSyncSerializer(NetBoxModelSerializer):
    snapshot_data = NestedIPFabricSnapshotSerializer(read_only=True)

    class Meta:
        model = IPFabricSync
        fields = [
            "id",
            "name",
            "display",
            "snapshot_data",
            "type",
            "status",
            "parameters",
            "last_synced",
            "created",
            "last_updated",
        ]


class IPFabricSnapshotSerializer(NetBoxModelSerializer):
    source = NestedIPFabricSourceSerializer()
    data = serializers.JSONField()
    date = serializers.DateTimeField()
    last_updated = serializers.DateTimeField()

    class Meta:
        model = IPFabricSnapshot
        fields = [
            "id",
            "name",
            "source",
            "snapshot_id",
            "status",
            "date",
            "display",
            "sites",
            "data",
            "created",
            "last_updated",
        ]

        extra_kwargs = {
            "raw_data": {"write_only": True},
        }


class IPFabricRelationshipFieldSerializer(NetBoxModelSerializer):
    transform_map = NestedIPFabricTransformMapSerializer(read_only=True)
    source_model = ContentTypeField(read_only=True)

    class Meta:
        model = IPFabricRelationshipField
        fields = [
            "id",
            "transform_map",
            "source_model",
            "target_field",
            "coalesce",
            "template",
        ]


class IPFabricTransformMapGroupSerializer(NetBoxModelSerializer):
    class Meta:
        model = IPFabricTransformMapGroup
        fields = [
            "name",
            "description",
            "transform_maps",
            "created",
            "last_updated",
        ]


class IPFabricTransformMapSerializer(NetBoxModelSerializer):
    target_model = ContentTypeField(read_only=True)

    class Meta:
        model = IPFabricTransformMap
        fields = [
            "id",
            "source_model",
            "target_model",
            "created",
            "last_updated",
        ]


class IPFabricTransformFieldSerializer(NetBoxModelSerializer):
    transform_map = NestedIPFabricTransformMapSerializer(read_only=True)

    class Meta:
        model = IPFabricTransformField
        fields = [
            "id",
            "transform_map",
            "source_field",
            "target_field",
            "coalesce",
            "template",
        ]


class IPFabricIngestionSerializer(NetBoxModelSerializer):
    branch = BranchSerializer(read_only=True)
    sync = NestedIPFabricSyncSerializer(read_only=True)

    class Meta:
        model = IPFabricIngestion
        fields = [
            "id",
            "name",
            "branch",
            "sync",
        ]


class IPFabricIngestionIssueSerializer(NetBoxModelSerializer):
    ingestion = IPFabricIngestionSerializer(read_only=True)

    class Meta:
        model = IPFabricIngestionIssue
        fields = [
            "id",
            "ingestion",
            "timestamp",
            "model",
            "message",
            "raw_data",
            "coalesce_fields",
            "defaults",
            "exception",
        ]


class IPFabricSourceSerializer(NetBoxModelSerializer):
    status = ChoiceField(choices=DataSourceStatusChoices)
    url = serializers.URLField()

    class Meta:
        model = IPFabricSource
        fields = [
            "id",
            "url",
            "display",
            "name",
            "type",
            "status",
            "last_synced",
            "description",
            "comments",
            "parameters",
            "created",
            "last_updated",
        ]
