# Generated by Django 5.1.3 on 2024-12-11 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('binance_app', '0002_remove_portfolio_margin_balance_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolio',
            name='customized_wallet_balance',
        ),
    ]
