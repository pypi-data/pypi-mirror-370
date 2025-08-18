from django.db import models
from django.contrib.postgres.fields import ArrayField
from dataclasses import dataclass
from typing import List

@dataclass
class MT5ServerConfig:
    """Configuration for an MT5 server"""
    id: int
    name: str
    type: str  # 'demo' or 'live'
    ips: List[str]  # List of IP addresses for failover
    username: int
    manager_password: str
    api_password: str

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.type not in ['demo', 'live']:
            raise ValueError(f"Invalid server type: {self.type}. Must be 'demo' or 'live'")
        
        if not self.username:
            raise ValueError("Username must be provided")

        if not isinstance(self.username, int):
            raise ValueError("Username must be an integer")

        if not self.manager_password:
            raise ValueError("Manager password must be provided")

        if not self.ips:
            raise ValueError("At least one IP address must be provided")
        
        if not isinstance(self.id, int):
            raise ValueError("Server ID must be an integer")

class TradingPlatformServer(models.Model):
    PLATFORM_TYPES = (
        ('mt5', 'MetaTrader 5'),
        ('mt4', 'MetaTrader 4'),
        ('vertex', 'Vertex'),
    )

    SERVER_TYPES = (
        ('demo', 'Demo'),
        ('live', 'Live'),
    )

    name = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_TYPES)
    ips = ArrayField(
        models.CharField(max_length=15),
        help_text="List of IP addresses for the server"
    )
    type = models.CharField(max_length=4, choices=SERVER_TYPES)
    username = models.IntegerField(help_text="Platform Manager account login number")
    is_active = models.BooleanField(default=True)
    is_connected = models.BooleanField(default=False)
    connection_timeout = models.IntegerField(default=30)
    max_retries = models.IntegerField(default=3)
    retry_min_wait = models.IntegerField(default=1)
    retry_max_wait = models.IntegerField(default=30)
    health_check_interval = models.IntegerField(default=30)
    error_log = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_trading_platform_server'
        app_label = 'system_settings'
        verbose_name = "Trading Platform Server"
        verbose_name_plural = "Trading Platform Servers"
        permissions = [
            ('view_trading_platform_server', 'Can view trading platform server'),
            ('add_trading_platform_server', 'Can add trading platform server'),
            ('change_trading_platform_server', 'Can change trading platform server'),
            ('delete_trading_platform_server', 'Can delete trading platform server'),
            ('enable_trading_platform_server', 'Can enable trading platform server'),
            ('disable_trading_platform_server', 'Can disable trading platform server'),
            ('view_trading_platform_config', 'Can view trading platform config'),
        ]

    def __str__(self):
        return f"{self.name} ({self.platform} - {self.type})"

    def save(self, *args, **kwargs):
        # Ensure type is lowercase before saving
        if self.type:
            self.type = self.type.lower()
        super().save(*args, **kwargs)
    
    def to_server_config(self):
      """Convert to MT5ServerConfig object"""
      # Create and return MT5ServerConfig object directly
      return MT5ServerConfig(
          id=int(self.id),
          name=str(self.name),
          ips=[str(ip) for ip in self.ips],
          type=str(self.type.lower()),
          username=int(self.username),
          manager_password=str(self.manager_password),
          api_password=str(self.api_password)
      )

class TradingPlatformServerLog(models.Model):
    """Stores historical logs for trading platform server events."""

    EVENT_TYPES = (
        ('CONNECT_SUCCESS', 'Connection Successful'),
        ('CONNECT_FAIL', 'Connection Failed'),
        ('DISCONNECT', 'Disconnected'),
        ('HEALTH_CHECK_FAIL', 'Health Check Failed'),
        ('RECONNECT_ATTEMPT', 'Reconnection Attempt'),
        ('RECONNECT_SUCCESS', 'Reconnection Successful'),
        ('RECONNECT_FAIL', 'Reconnection Failed'),
    )

    server = models.ForeignKey(
        TradingPlatformServer,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    details = models.TextField(blank=True, null=True, help_text="Details about the event, e.g., error message.")

    class Meta:
        db_table = 'system_trading_platform_server_log'
        app_label = 'system_settings' # Ensure this matches the app label of TradingPlatformServer
        verbose_name = "Trading Platform Server Log"
        verbose_name_plural = "Trading Platform Server Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.server.name} - {self.event_type}"
