from decimal import Decimal
from django.db import models

import random
import requests
from django.db import models

class Position(models.Model):
    symbol = models.CharField(max_length=20)  # Symbol like BTCUSDT
    initial_quantity = models.DecimalField(max_digits=20, decimal_places=6)  # The number of units initially purchased (e.g., 10 apples)
    entry_price = models.DecimalField(max_digits=20, decimal_places=6)
    leverage = models.IntegerField(default=75)
    position_type = models.CharField(max_length=10, choices=[('long', 'Long'), ('short', 'Short')])

    fluctuation_min = models.DecimalField(max_digits=20, decimal_places=6, default=40.32)
    fluctuation_max = models.DecimalField(max_digits=20, decimal_places=6, default=41.76)
    fluctuation_frequency = models.DecimalField(max_digits=20, decimal_places=6, default=0.5)  # In seconds

    @property
    def position_value(self):
        """Calculate the position value (Position Size × Entry Price)."""
        return self.initial_quantity * self.entry_price

    @property
    def margin(self):
        """Calculate the margin based on Position Size, Entry Price, and Leverage."""
        return (self.size * self.entry_price) / self.leverage

    @property
    def unrealized_pnl(self):
        """Calculate unrealized PnL based on market price and entry price."""
        mark_price = self.mark_price
        if self.position_type == 'long':
            print("(mark_price - self.entry_price) * self.initial_quantity")
            print((mark_price))
            print((self.entry_price))
            print((self.initial_quantity))
            print((mark_price - self.entry_price) * self.initial_quantity)
            return (mark_price - self.entry_price) * self.initial_quantity
        else:
            print("(mark_price - self.entry_price) * self.initial_quantity")
            print((mark_price - self.entry_price) * self.initial_quantity)
            return (self.entry_price - mark_price) * self.initial_quantity

    @property
    def roi(self):
        """Calculate ROI based on unrealized PnL and margin."""
        return (self.unrealized_pnl / self.margin) * 100

    @property
    def margin_ratio(self):
        """Calculate margin ratio using Maintenance Margin + Unrealized Loss."""
        maint_margin = self.maintenance_margin  # Maintenance margin rate (0.6% default)
        unrealized_loss = self.unrealized_pnl if self.unrealized_pnl < 0 else 0
        margin_balance = self.margin  # Margin balance, in this case, it's the margin
        return ((maint_margin + unrealized_loss) / margin_balance) * 100

    @property
    def maintenance_margin(self):
        """Calculate the maintenance margin (0.6% default)."""
        return self.size * 0.006

    @property
    def mark_price(self):
        """Fetch the real-time Mark Price from Binance API."""
        url = f'https://fapi.binance.com/fapi/v1/premiumIndex?symbol={self.symbol.upper()}'
        response = requests.get(url)
        data = response.json()
        return Decimal(data['markPrice'])


    @property
    def liq_price(self):
        """Generate a random fluctuation in the given range."""
        fluctuation_range = self.fluctuation_max - self.fluctuation_min
        random_fluctuation = random.uniform(self.fluctuation_min, self.fluctuation_max)
        return random_fluctuation

    def __str__(self):
        return f"Position {self.symbol} - {self.position_type.capitalize()}"


class Portfolio(models.Model):
    wallet_balance = models.DecimalField(max_digits=20, decimal_places=2)
    realized_pnl = models.CharField(max_length=100)  # Store both value and percentage as a string

    def calculate_unrealized_pnl(self):
        positions = Position.objects.all()  # Get all positions to calculate the unrealized PNL
        total_unrealized_pnl = sum([position.unrealized_pnl for position in positions])
        print("total_unrealized_pnl")
        print(total_unrealized_pnl)
        return total_unrealized_pnl

    def calculate_margin_balance(self):
        """Calculate and return the Margin Balance (MB)."""
        unrealized_pnl = self.calculate_unrealized_pnl()
        margin_balance = self.wallet_balance + unrealized_pnl  # Example calculation
        return margin_balance

    def __str__(self):
        return f"Portfolio"


