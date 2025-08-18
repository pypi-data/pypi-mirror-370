from rest_framework import serializers
from .models.account_types import AccountType
from .models.trading_platform import TradingPlatformServer

class BaseAccountTypeSerializer(serializers.ModelSerializer):
    """Base serializer for account types"""
    server_name = serializers.CharField(source='server.name', read_only=True)
    available_leverages = serializers.ListField(read_only=True)

    class Meta:
        model = AccountType
        fields = [
            'id', 'name', 'server', 'server_name', 'min_first_deposit', 
            'leverages', 'default_leverage', 'default_group', 'is_active', 
            'show_cp', 'show_crm', 'show_agreement', 'sequence', 
            'account_type', 'platform', 'max_unapproved_accounts', 
            'available_leverages'
        ]
        read_only_fields = ['id']

    def validate_server(self, value):
        try:
            return TradingPlatformServer.objects.get(id=value.id)
        except TradingPlatformServer.DoesNotExist:
            raise serializers.ValidationError("Invalid server ID") 