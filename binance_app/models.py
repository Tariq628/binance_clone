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
        margin = (self.size * self.entry_price) / self.leverage
        return margin.quantize(Decimal('0.00'))  # Round to 2 decimal places

    @property
    def unrealized_pnl(self):
        """Calculate unrealized PnL based on market price and entry price."""
        mark_price = self.mark_price
        if self.position_type == 'long':
            unrealized = (mark_price - self.entry_price) * self.initial_quantity
        else:
            unrealized = (self.entry_price - mark_price) * self.initial_quantity
        return unrealized.quantize(Decimal('0.00'))  # Round to 2 decimal places

    @property
    def size(self):
        """Calculate the size (total value of holdings)."""
        size_value = self.initial_quantity * self.mark_price
        return size_value.quantize(Decimal('0.0001'))  # Round to 4 decimal places

    @property
    def roi(self):
        """Calculate ROI based on unrealized PnL and margin."""
        roi_value = (self.unrealized_pnl / self.margin) * 100
        return roi_value.quantize(Decimal('0.00'))  # Round to 2 decimal places

    @property
    def margin_ratio(self):
        """Calculate margin ratio using Maintenance Margin + Unrealized Loss."""
        maint_margin = self.maintenance_margin  # Maintenance margin rate (0.6% default)
        unrealized_loss = self.unrealized_pnl if self.unrealized_pnl < 0 else 0
        margin_balance = self.margin  # Margin balance, in this case, it's the margin
        margin_ratio_value = ((maint_margin + unrealized_loss) / margin_balance) * 100
        return margin_ratio_value.quantize(Decimal('0.00'))  # Round to 2 decimal places

    @property
    def maintenance_margin(self):
        """Calculate the maintenance margin (0.6% default)."""
        return self.size * Decimal('0.006')

    @property
    def mark_price(self):
        """Fetch the real-time Mark Price from Binance API."""
        url = f'https://fapi.binance.com/fapi/v1/premiumIndex?symbol={self.symbol.upper()}'
        response = requests.get(url)
        data = response.json()
        mark_price_value = Decimal(data['markPrice'])
        return mark_price_value.quantize(Decimal('0.0001'))  # Round to 4 decimal places

    @property
    def liq_price(self):
        """Generate a random fluctuation in the given range."""
        # Convert Decimal values to float for use with random.uniform()
        fluctuation_min_float = float(self.fluctuation_min)
        fluctuation_max_float = float(self.fluctuation_max)
        
        # Generate a random fluctuation within the range
        random_fluctuation = random.uniform(fluctuation_min_float, fluctuation_max_float)
        
        # Convert back to Decimal and round to 4 decimal places
        return Decimal(random_fluctuation).quantize(Decimal('0.0001'))  # Round to 4 decimal places

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


