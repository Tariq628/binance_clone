from decimal import Decimal
from django.shortcuts import render

from binance_app.models import Portfolio

def round_to_two_decimal_places(value):
    """Round a value to two decimal places using Decimal."""
    return Decimal(value).quantize(Decimal('0.00'))

# Create your views here.
def index(request):
    portfolio = Portfolio.objects.first()  # Fetch the first portfolio (or adjust for your needs)
    
    # Calculate the unrealized PnL and margin balance
    unrealized_pnl = portfolio.calculate_unrealized_pnl()  
    margin_balance = portfolio.calculate_margin_balance()  
    
    # Get the wallet balance
    wallet_balance = portfolio.wallet_balance  
    
    # Round the values to 2 decimal places using the separate function
    unrealized_pnl = round_to_two_decimal_places(unrealized_pnl)
    margin_balance = round_to_two_decimal_places(margin_balance)
    wallet_balance = round_to_two_decimal_places(wallet_balance)
    
    # Pass portfolio, unrealized_pnl, margin_balance, and wallet_balance to the template
    return render(request, 'index.html', {
        'unrealized_pnl': unrealized_pnl,
        'margin_balance': margin_balance,
        'wallet_balance': wallet_balance,
    })
