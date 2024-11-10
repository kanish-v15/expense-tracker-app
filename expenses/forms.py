"""Forms.py"""

from datetime import datetime
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Category, Expense

def validate_password_strength(password):
    """validates password with 8 characters"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")

# pylint: disable=R0901
class CustomUserCreationForm(UserCreationForm):
    """makes email field required"""
    email = forms.EmailField(required=True)

    # pylint: disable=R0903
    class Meta:
        """meta class"""
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """checks duplicate emails"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean_password1(self):
        """Validates password"""
        password1 = self.cleaned_data.get('password1')
        validate_password_strength(password1)
        return password1

class CustomAuthenticationForm(AuthenticationForm):
    """authenticates using username"""
    username = forms.CharField(label='Email / Username')

class ExpenseForm(forms.ModelForm):
    """expense form"""
    category = forms.ChoiceField(choices=[])
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.now()
    )
    description = forms.CharField(
        label='Expense Name',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # pylint: disable=R0903
    class Meta:
        """meta class"""
        model = Expense
        fields = ['amount', 'category', 'description', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # pylint: disable=E1101
            self.fields['category'].choices = [('', 'Select a category')] + [
                (category.name, category.name) for category in Category.objects.filter(user=user)
            ]

class CategoryForm(forms.ModelForm):
    """category form"""
    # pylint: disable=R0903
    class Meta:
        """meta class"""
        model = Category
        fields = ['name']

class ExpenseFilterForm(forms.Form):
    """Expense filter form"""
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    # pylint: disable=E1101
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False)
    search_term = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # pylint: disable=E1101
            self.fields['category'].queryset = Category.objects.filter(user=user)
