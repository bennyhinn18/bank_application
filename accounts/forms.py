from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class TransactionForm(forms.Form):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    )
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
