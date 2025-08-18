from django.db import models
from shared_models.accounts.models import Account
from shared_models.common.base import BaseModel

class Deal(BaseModel):
    deal_ticket = models.BigIntegerField(unique=True, db_index=True)
    external_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    login = models.BigIntegerField(db_index=True)
    dealer = models.BigIntegerField(db_index=True)
    order_ticket = models.BigIntegerField(db_index=True)
    action = models.IntegerField()
    entry = models.IntegerField(db_index=True)
    digits = models.IntegerField()
    digits_currency = models.IntegerField()
    contract_size = models.DecimalField(max_digits=20, decimal_places=10)
    time = models.DateTimeField(db_index=True)
    time_msc = models.BigIntegerField(db_index=True)
    symbol = models.CharField(max_length=50, db_index=True)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    price_sl = models.DecimalField(max_digits=20, decimal_places=10)
    price_tp = models.DecimalField(max_digits=20, decimal_places=10)
    volume = models.DecimalField(max_digits=20, decimal_places=10)
    volume_ext = models.DecimalField(max_digits=30, decimal_places=15)
    volume_closed = models.DecimalField(max_digits=20, decimal_places=10)
    volume_closed_ext = models.DecimalField(max_digits=30, decimal_places=15)
    profit = models.DecimalField(max_digits=20, decimal_places=10)
    profit_raw = models.DecimalField(max_digits=20, decimal_places=10)
    storage = models.DecimalField(max_digits=20, decimal_places=10)
    commission = models.DecimalField(max_digits=20, decimal_places=10)
    fee = models.DecimalField(max_digits=20, decimal_places=10)
    value = models.DecimalField(max_digits=20, decimal_places=10)
    rate_profit = models.DecimalField(max_digits=20, decimal_places=10)
    rate_margin = models.DecimalField(max_digits=20, decimal_places=10)
    expert_id = models.BigIntegerField(null=True, blank=True)
    position_id = models.BigIntegerField(db_index=True)
    comment = models.CharField(max_length=255, null=True, blank=True)
    price_position = models.DecimalField(max_digits=20, decimal_places=10)
    tick_value = models.DecimalField(max_digits=20, decimal_places=10)
    tick_size = models.DecimalField(max_digits=20, decimal_places=10)
    flags = models.BigIntegerField()
    reason = models.IntegerField(null=True, blank=True, db_index=True)
    gateway = models.CharField(max_length=100, null=True, blank=True)
    price_gateway = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    market_bid = models.DecimalField(max_digits=20, decimal_places=10)
    market_ask = models.DecimalField(max_digits=20, decimal_places=10)
    market_last = models.DecimalField(max_digits=20, decimal_places=10)
    modification_flags = models.IntegerField()
    raw_data = models.JSONField(default=dict, blank=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["deal_ticket"]),
            models.Index(fields=["login"]),
            models.Index(fields=["account"]),
            models.Index(fields=["time"]),
            models.Index(fields=["time_msc"]),
            models.Index(fields=["position_id"]),
            models.Index(fields=["symbol"]),
            models.Index(fields=["entry"]),
            models.Index(fields=["reason"]),
            models.Index(fields=['position_id', 'login', 'entry'], name='idx_deal_position_lookup'),
            models.Index(fields=['login', 'time'], name='idx_deal_login_time'),
        ]
        db_table = "deal"
        verbose_name = "Deal"
        verbose_name_plural = "Deals" 