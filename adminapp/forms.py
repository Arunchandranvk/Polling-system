from django import forms
from .models import Poll, Option
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        return cleaned_data


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ["question", "expiry_date"]  # created_by handled in view
        widgets = {
            "expiry_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ["text"]
