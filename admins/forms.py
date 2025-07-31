from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AdminLoginForm(forms.Form):
    """
    Custom admin login form with data validation and cleaning
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'placeholder': _('Username'),
            'required': True
        }),
        label=_('Username')
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': _('Password'),
            'required': True
        }),
        label=_('Password')
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        Initialize form with request object for authentication
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_username(self):
        """
        Clean and validate username field
        """
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip().lower()
            if len(username) < 3:
                raise ValidationError(
                    _('Username must be at least 3 characters long.'))
        return username

    def clean_password(self):
        """
        Clean and validate password field
        """
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 4:
                raise ValidationError(
                    _('Password must be at least 4 characters long.'))
        return password

    def clean(self):
        """
        Validate the entire form and authenticate user
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Authenticate user
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )

            if self.user_cache is None:
                raise ValidationError(_('Invalid username or password.'))

            if not self.user_cache.is_active:
                raise ValidationError(_('This account is inactive.'))

            if not self.user_cache.is_superuser:
                raise ValidationError(
                    _('You do not have permission to access the admin area.'))

        return cleaned_data

    def get_user(self):
        """
        Return authenticated user
        """
        return self.user_cache
