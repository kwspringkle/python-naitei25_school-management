from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from utils.constant import (
    ADMIN_INVALID_CREDENTIALS_ERROR, ADMIN_INACTIVE_ACCOUNT_ERROR,
    TEACHER_USERNAME_MAX_LENGTH, TEACHER_INVALID_CREDENTIALS_ERROR, TEACHER_IS_TEACHER_ATTRIBUTE,
    FORM_CONTROL_CLASS, REQUIRED_ATTRIBUTE, USERNAME_PLACEHOLDER, PASSWORD_PLACEHOLDER
)


class TeacherLoginForm(forms.Form):
    """
    Form for teacher authentication
    """
    username = forms.CharField(
        max_length=TEACHER_USERNAME_MAX_LENGTH,
        widget=forms.TextInput(attrs={
            'class': FORM_CONTROL_CLASS,
            'placeholder': _(USERNAME_PLACEHOLDER),
            'required': REQUIRED_ATTRIBUTE
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': FORM_CONTROL_CLASS, 
            'placeholder': _(PASSWORD_PLACEHOLDER),
            'required': REQUIRED_ATTRIBUTE
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        Initialize form with request object
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validate user credentials and check if user is a teacher
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
                raise ValidationError(_(ADMIN_INVALID_CREDENTIALS_ERROR))

            if not self.user_cache.is_active:
                raise ValidationError(_(ADMIN_INACTIVE_ACCOUNT_ERROR))

            # Check if user is a teacher
            if not getattr(self.user_cache, TEACHER_IS_TEACHER_ATTRIBUTE, False):
                raise ValidationError(_(TEACHER_INVALID_CREDENTIALS_ERROR))

        return cleaned_data

    def get_user(self):
        """
        Return authenticated user
        """
        return self.user_cache