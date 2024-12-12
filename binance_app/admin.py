from django.contrib import admin

# Register your models here.
from .models import Position, Portfolio

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('symbol',)

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('wallet_balance', 'realized_pnl')