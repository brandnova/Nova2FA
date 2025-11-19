from django import forms
from .registry import get_method_choices


class TwoFactorSetupForm(forms.Form):
    """
    Form for setting up two-factor authentication.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate choices from registry
        self.fields['method'].choices = get_method_choices()
    
    method = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        widget=forms.RadioSelect,
        label="Authentication Method"
    )


class TOTPVerificationForm(forms.Form):
    """
    Form for verifying TOTP codes.
    """
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '000000',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'class': 'nova2fa-input'
        }),
        label="Authentication Code"
    )


class EmailOTPVerificationForm(forms.Form):
    """
    Form for verifying email OTP codes.
    """
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '000000',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'class': 'nova2fa-input'
        }),
        label="Email Code"
    )


class BackupCodeVerificationForm(forms.Form):
    """
    Form for verifying backup codes.
    """
    code = forms.CharField(
        max_length=8,
        min_length=8,
        widget=forms.TextInput(attrs={
            'placeholder': 'XXXXXXXX',
            'autocomplete': 'one-time-code',
            'style': 'text-transform: uppercase;',
            'class': 'nova2fa-input'
        }),
        label="Backup Code"
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '').upper().strip()
        return code


class DisableTwoFactorForm(forms.Form):
    """
    Form for disabling two-factor authentication.
    """
    confirm = forms.BooleanField(
        required=True,
        label="I understand that disabling two-factor authentication will make my account less secure."
    )