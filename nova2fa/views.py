import datetime
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.conf import settings
import logging

from .models import UserTwoFactorSettings, EmailOTP
from .forms import (
    TwoFactorSetupForm, TOTPVerificationForm, EmailOTPVerificationForm,
    BackupCodeVerificationForm, DisableTwoFactorForm
)
from .registry import get_method, get_enabled_methods

logger = logging.getLogger(__name__)


def rate_limit(key, limit=5, timeout=300):
    """
    Simple rate limiting decorator.
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            cache_key = f"nova2fa_rate_limit_{key}_{request.user.pk if request.user.is_authenticated else request.META.get('REMOTE_ADDR')}"
            count = cache.get(cache_key, 0)
            
            if count >= limit:
                messages.error(request, "Too many attempts. Please try again later.")
                return redirect('nova2fa:settings')
            
            cache.set(cache_key, count + 1, timeout)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def nova2fa_settings(request):
    """
    View for managing 2FA settings.
    """
    two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(
        user=request.user
    )
    
    # Get enabled methods
    enabled_methods = get_enabled_methods()
    
    context = {
        'two_factor_settings': two_factor_settings,
        'enabled_methods': enabled_methods,
    }
    
    return render(request, 'nova2fa/settings.html', context)


@login_required
def setup_2fa(request):
    """
    View for setting up 2FA - method selection.
    """
    two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(
        user=request.user
    )
    
    if two_factor_settings.is_enabled:
        messages.info(request, "Two-factor authentication is already enabled.")
        return redirect('nova2fa:settings')
    
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            method_code = form.cleaned_data['method']
            method = get_method(method_code)
            
            if not method:
                messages.error(request, "Invalid authentication method selected.")
                return redirect('nova2fa:setup_2fa')
            
            # Store method in session
            request.session['nova2fa_setup_method'] = method_code
            
            # Handle method-specific setup
            if method_code == 'totp':
                setup_data = method.setup(request.user)
                request.session['nova2fa_setup_secret'] = setup_data['secret']  # Encrypted
                request.session['nova2fa_setup_secret_display'] = setup_data['secret_display']  # Plain
                request.session['nova2fa_qr_code_path'] = setup_data['qr_code_path']
                return redirect('nova2fa:setup_totp')
            
            elif method_code == 'email':
                if method.send(request.user):
                    messages.success(
                        request,
                        f"A verification code has been sent to {request.user.email}."
                    )
                    return redirect('nova2fa:verify_email_otp')
                else:
                    messages.error(
                        request,
                        "Failed to send verification code. Please try again."
                    )
    else:
        form = TwoFactorSetupForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'nova2fa/setup.html', context)


@login_required
def setup_totp(request):
    """
    View for TOTP setup with QR code.
    """
    if 'nova2fa_setup_secret' not in request.session or 'nova2fa_qr_code_path' not in request.session:
        messages.error(request, "Setup session expired. Please start again.")
        return redirect('nova2fa:setup_2fa')
    
    secret = request.session['nova2fa_setup_secret']  # Encrypted secret
    secret_display = request.session.get('nova2fa_setup_secret_display', '')  # Plain text for display
    qr_code_path = request.session['nova2fa_qr_code_path']
    
    if not os.path.exists(qr_code_path):
        messages.error(request, "QR code not found. Please try again.")
        return redirect('nova2fa:setup_2fa')
    
    if request.method == 'POST':
        form = TOTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Get TOTP method and verify
            method = get_method('totp')
            
            # Temporarily store encrypted secret for verification
            two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(
                user=request.user
            )
            two_factor_settings.totp_secret = secret  # Store encrypted
            two_factor_settings.save()
            
            if method.verify(request.user, code):
                # Setup backup codes
                backup_method = get_method('backup')
                backup_data = backup_method.setup(request.user)
                
                # Enable 2FA
                two_factor_settings.is_enabled = True
                two_factor_settings.method = 'totp'
                two_factor_settings.backup_codes = backup_data['hashed_codes']  # Store hashed
                two_factor_settings.last_verified = timezone.now()
                two_factor_settings.save()
                
                # Clean up session
                if 'nova2fa_setup_secret' in request.session:
                    del request.session['nova2fa_setup_secret']
                if 'nova2fa_setup_secret_display' in request.session:
                    del request.session['nova2fa_setup_secret_display']
                
                try:
                    os.remove(qr_code_path)
                except OSError:
                    pass
                
                if 'nova2fa_qr_code_path' in request.session:
                    del request.session['nova2fa_qr_code_path']
                
                # Store plain text codes in session for one-time display
                request.session['nova2fa_new_backup_codes'] = backup_data['codes']
                
                messages.success(
                    request,
                    "Two-factor authentication has been enabled successfully. Please save your backup codes!"
                )
                return redirect('nova2fa:view_backup_codes')
            else:
                # Remove temporarily stored secret
                two_factor_settings.totp_secret = None
                two_factor_settings.save()
                messages.error(request, "Invalid verification code. Please try again.")
    else:
        form = TOTPVerificationForm()
    
    context = {
        'form': form,
        'secret': secret_display,  # Show plain text for manual entry
        'qr_code_url': reverse('nova2fa:qr_code'),
    }
    
    return render(request, 'nova2fa/setup_totp.html', context)


@login_required
def qr_code(request):
    """
    Serve the QR code image.
    """
    if 'nova2fa_qr_code_path' not in request.session:
        raise Http404("QR code not found")
    
    qr_code_path = request.session['nova2fa_qr_code_path']
    
    if not os.path.exists(qr_code_path):
        raise Http404("QR code not found")
    
    with open(qr_code_path, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/png')


@login_required
def verify_email_otp(request):
    """
    Verify email OTP during setup.
    """
    if request.method == 'POST':
        form = EmailOTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Get email method and verify
            method = get_method('email')
            
            if method.verify(request.user, code):
                # Setup backup codes
                backup_method = get_method('backup')
                backup_data = backup_method.setup(request.user)
                
                # Enable 2FA
                two_factor_settings, created = UserTwoFactorSettings.objects.get_or_create(
                    user=request.user
                )
                two_factor_settings.is_enabled = True
                two_factor_settings.method = 'email'
                two_factor_settings.backup_codes = backup_data['hashed_codes']  # Store hashed
                two_factor_settings.last_verified = timezone.now()
                two_factor_settings.save()
                
                # Store plain text codes in session for one-time display
                request.session['nova2fa_new_backup_codes'] = backup_data['codes']
                
                messages.success(
                    request,
                    "Two-factor authentication has been enabled successfully. Please save your backup codes!"
                )
                return redirect('nova2fa:view_backup_codes')
            else:
                messages.error(
                    request,
                    "Invalid or expired verification code. Please try again."
                )
                return redirect('nova2fa:request_email_otp')
    else:
        form = EmailOTPVerificationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'nova2fa/verify_email_otp.html', context)


@login_required
def request_email_otp(request):
    """
    Request a new email OTP during setup.
    """
    method = get_method('email')
    
    if method.send(request.user):
        messages.success(
            request,
            f"A new verification code has been sent to {request.user.email}."
        )
    else:
        messages.error(
            request,
            "Failed to send verification code. Please try again."
        )
    
    return redirect('nova2fa:verify_email_otp')


@login_required
@never_cache
@rate_limit('verify_2fa', limit=10, timeout=900)
def verify_2fa(request):
    """
    Main 2FA verification view during login flow.
    """
    # Check if already verified
    def is_2fa_verified():
        verified_at = request.session.get('nova2fa_verified_at')
        if not verified_at:
            return False
        
        try:
            if isinstance(verified_at, str):
                verified_at = timezone.datetime.fromisoformat(verified_at)
            
            if timezone.is_naive(verified_at):
                verified_at = timezone.make_aware(verified_at)
            
            verification_window_hours = getattr(
                settings,
                'NOVA2FA_VERIFICATION_WINDOW_DAYS',
                14
            ) * 24
            now = timezone.now()
            return (now - verified_at) < datetime.timedelta(hours=verification_window_hours)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing 2FA verification timestamp: {str(e)}")
            return False

    if is_2fa_verified():
        next_url = request.session.get('nova2fa_next_url', 'home')
        if 'nova2fa_next_url' in request.session:
            del request.session['nova2fa_next_url']
        if 'nova2fa_verification_in_progress' in request.session:
            del request.session['nova2fa_verification_in_progress']
        return redirect(next_url)
    
    # Get 2FA settings
    try:
        two_factor_settings = UserTwoFactorSettings.objects.get(user=request.user)
    except UserTwoFactorSettings.DoesNotExist:
        if 'nova2fa_next_url' in request.session:
            next_url = request.session.pop('nova2fa_next_url')
            return redirect(next_url)
        return redirect('home')
    
    if not two_factor_settings.is_enabled:
        next_url = request.session.get('nova2fa_next_url', 'home')
        if 'nova2fa_next_url' in request.session:
            del request.session['nova2fa_next_url']
        return redirect(next_url)
    
    if not two_factor_settings.needs_verification():
        next_url = request.session.get('nova2fa_next_url', 'home')
        if 'nova2fa_next_url' in request.session:
            del request.session['nova2fa_next_url']
        if 'nova2fa_verification_in_progress' in request.session:
            del request.session['nova2fa_verification_in_progress']
        return redirect(next_url)
    
    # Check if using backup code
    use_backup_code = request.GET.get('backup') == 'true' or request.POST.get('use_backup_code')
    
    if use_backup_code:
        return handle_backup_code_verification(request, two_factor_settings)
    
    # Handle method-specific verification
    if two_factor_settings.method == 'totp':
        return handle_totp_verification(request, two_factor_settings)
    elif two_factor_settings.method == 'email':
        return handle_email_verification(request, two_factor_settings)
    
    messages.error(request, "Unsupported two-factor authentication method.")
    return redirect('home')


def handle_backup_code_verification(request, two_factor_settings):
    """Handle backup code verification."""
    # Check if account is locked
    if two_factor_settings.is_locked():
        lockout_time = (two_factor_settings.locked_until - timezone.now()).seconds // 60
        messages.error(
            request,
            f"Account temporarily locked due to too many failed attempts. Please try again in {lockout_time} minutes."
        )
        return render(request, 'nova2fa/verify.html', {'method': 'backup', 'locked': True})
    
    if request.method == 'POST':
        form = BackupCodeVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            method = get_method('backup')
            if method.verify(request.user, code):
                two_factor_settings.update_last_verified()
                request.session['nova2fa_verified_at'] = timezone.now().isoformat()
                
                if 'nova2fa_verification_in_progress' in request.session:
                    del request.session['nova2fa_verification_in_progress']
                
                request.session.save()
                
                next_url = request.session.get('nova2fa_next_url', 'home')
                if 'nova2fa_next_url' in request.session:
                    del request.session['nova2fa_next_url']
                
                remaining_codes = two_factor_settings.get_available_backup_codes_count()
                if remaining_codes == 0:
                    messages.warning(
                        request,
                        "You have used all your backup codes. Please generate new ones."
                    )
                elif remaining_codes <= 2:
                    messages.warning(
                        request,
                        f"You have {remaining_codes} backup codes remaining."
                    )
                
                messages.success(
                    request,
                    "Two-factor authentication verified successfully using backup code."
                )
                return redirect(next_url)
            else:
                if two_factor_settings.is_locked():
                    messages.error(
                        request,
                        "Too many failed attempts. Your account has been temporarily locked."
                    )
                else:
                    messages.error(
                        request,
                        "Invalid or already used backup code. Please try again."
                    )
    else:
        form = BackupCodeVerificationForm()
    
    context = {
        'method': 'backup',
        'form': form,
        'available_codes_count': two_factor_settings.get_available_backup_codes_count(),
        'failed_attempts': two_factor_settings.failed_attempts,
    }
    
    return render(request, 'nova2fa/verify.html', context)


def handle_totp_verification(request, two_factor_settings):
    """Handle TOTP verification."""
    if request.method == 'POST':
        form = TOTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            method = get_method('totp')
            if method.verify(request.user, code):
                two_factor_settings.update_last_verified()
                request.session['nova2fa_verified_at'] = timezone.now().isoformat()
                
                if 'nova2fa_verification_in_progress' in request.session:
                    del request.session['nova2fa_verification_in_progress']
                
                request.session.save()
                
                next_url = request.session.get('nova2fa_next_url', 'home')
                if 'nova2fa_next_url' in request.session:
                    del request.session['nova2fa_next_url']
                
                messages.success(
                    request,
                    "Two-factor authentication verified successfully."
                )
                return redirect(next_url)
            else:
                messages.error(request, "Invalid verification code. Please try again.")
    else:
        form = TOTPVerificationForm()
    
    context = {
        'method': 'totp',
        'form': form,
        'has_backup_codes': two_factor_settings.has_available_backup_codes(),
    }
    
    return render(request, 'nova2fa/verify.html', context)


def handle_email_verification(request, two_factor_settings):
    """Handle email OTP verification."""
    otp_sent = request.session.get('nova2fa_email_otp_sent', False)
    
    if request.method == 'POST':
        if request.POST.get('action') == 'send_otp':
            method = get_method('email')
            try:
                if method.send(request.user):
                    request.session['nova2fa_email_otp_sent'] = True
                    request.session.save()
                    otp_sent = True
                    messages.success(
                        request,
                        f"A verification code has been sent to {request.user.email}."
                    )
                else:
                    messages.error(
                        request,
                        "Failed to send verification code. Please try again."
                    )
            except Exception as e:
                logger.error(f"Error sending OTP: {str(e)}")
                messages.error(
                    request,
                    "There was an error sending the verification code. Please try again."
                )
        
        elif otp_sent:
            form = EmailOTPVerificationForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                
                method = get_method('email')
                if method.verify(request.user, code):
                    two_factor_settings.update_last_verified()
                    request.session['nova2fa_verified_at'] = timezone.now().isoformat()
                    
                    if 'nova2fa_verification_in_progress' in request.session:
                        del request.session['nova2fa_verification_in_progress']
                    
                    if 'nova2fa_email_otp_sent' in request.session:
                        del request.session['nova2fa_email_otp_sent']
                    
                    request.session.save()
                    
                    next_url = request.session.get('nova2fa_next_url', 'home')
                    if 'nova2fa_next_url' in request.session:
                        del request.session['nova2fa_next_url']
                    
                    messages.success(
                        request,
                        "Two-factor authentication verified successfully."
                    )
                    return redirect(next_url)
                else:
                    messages.error(
                        request,
                        "Invalid or expired verification code. Please try again."
                    )
    
    if otp_sent:
        form = EmailOTPVerificationForm()
    else:
        form = None
    
    context = {
        'method': 'email',
        'otp_sent': otp_sent,
        'form': form,
        'has_backup_codes': two_factor_settings.has_available_backup_codes(),
    }
    
    return render(request, 'nova2fa/verify.html', context)


@login_required
def request_verification_otp(request):
    """Request new OTP during verification flow."""
    try:
        two_factor_settings = UserTwoFactorSettings.objects.get(
            user=request.user,
            is_enabled=True,
            method='email'
        )
        
        method = get_method('email')
        if method.send(request.user):
            request.session['nova2fa_email_otp_sent'] = True
            request.session.save()
            messages.success(
                request,
                f"A new verification code has been sent to {request.user.email}."
            )
        else:
            messages.error(
                request,
                "Failed to send verification code. Please try again."
            )
    except UserTwoFactorSettings.DoesNotExist:
        messages.error(
            request,
            "Email two-factor authentication is not enabled for your account."
        )
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        messages.error(
            request,
            "There was an error sending the verification code. Please try again."
        )
    
    return redirect('nova2fa:verify')


@login_required
def disable_2fa(request):
    """Disable 2FA for the user."""
    two_factor_settings = get_object_or_404(
        UserTwoFactorSettings,
        user=request.user,
        is_enabled=True
    )
    
    if request.method == 'POST':
        form = DisableTwoFactorForm(request.POST)
        if form.is_valid():
            two_factor_settings.is_enabled = False
            two_factor_settings.totp_secret = None
            two_factor_settings.backup_codes = []
            two_factor_settings.used_backup_codes = []
            two_factor_settings.save()
            
            messages.success(request, "Two-factor authentication has been disabled.")
            return redirect('nova2fa:settings')
    else:
        form = DisableTwoFactorForm()
    
    context = {
        'form': form,
        'two_factor_settings': two_factor_settings,
    }
    
    return render(request, 'nova2fa/disable.html', context)


@login_required
def view_backup_codes(request):
    """View backup codes with status."""
    two_factor_settings = get_object_or_404(
        UserTwoFactorSettings,
        user=request.user,
        is_enabled=True
    )
    
    # Check if there are new codes to display (from setup)
    new_codes = request.session.pop('nova2fa_new_backup_codes', None)
    
    if new_codes:
        # Display new codes (plain text, one-time only)
        backup_codes_status = [{
            'code': code,
            'is_used': False
        } for code in new_codes]
        show_codes = True
    else:
        # Codes are hashed, can't display them
        backup_codes_status = []
        show_codes = False
    
    context = {
        'backup_codes_status': backup_codes_status,
        'available_count': two_factor_settings.get_available_backup_codes_count(),
        'total_count': len(two_factor_settings.backup_codes),
        'show_codes': show_codes,
        'new_codes': new_codes is not None,
    }
    
    return render(request, 'nova2fa/backup_codes.html', context)


@login_required
@require_POST
def regenerate_backup_codes(request):
    """Regenerate backup codes."""
    two_factor_settings = get_object_or_404(
        UserTwoFactorSettings,
        user=request.user,
        is_enabled=True
    )
    
    backup_method = get_method('backup')
    backup_data = backup_method.setup(request.user)
    
    two_factor_settings.backup_codes = backup_data['hashed_codes']  # Store hashed
    two_factor_settings.used_backup_codes = []
    two_factor_settings.save()
    
    # Store plain text codes in session for one-time display
    request.session['nova2fa_new_backup_codes'] = backup_data['codes']
    
    messages.success(
        request,
        "New backup codes have been generated. All previous codes are now invalid. Please save these codes!"
    )
    return redirect('nova2fa:view_backup_codes')


@login_required
def change_2fa_method(request):
    """Change 2FA method."""
    two_factor_settings = get_object_or_404(
        UserTwoFactorSettings,
        user=request.user,
        is_enabled=True
    )
    
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            method_code = form.cleaned_data['method']
            
            if method_code == two_factor_settings.method:
                messages.info(
                    request,
                    f"You are already using {method_code} for two-factor authentication."
                )
                return redirect('nova2fa:settings')
            
            request.session['nova2fa_setup_method'] = method_code
            
            method = get_method(method_code)
            
            if method_code == 'totp':
                setup_data = method.setup(request.user)
                request.session['nova2fa_setup_secret'] = setup_data['secret']
                request.session['nova2fa_qr_code_path'] = setup_data['qr_code_path']
                return redirect('nova2fa:setup_totp')
            
            elif method_code == 'email':
                if method.send(request.user):
                    messages.success(
                        request,
                        f"A verification code has been sent to {request.user.email}."
                    )
                    return redirect('nova2fa:verify_email_otp')
                else:
                    messages.error(
                        request,
                        "Failed to send verification code. Please try again."
                    )
    else:
        form = TwoFactorSetupForm(initial={'method': two_factor_settings.method})
    
    context = {
        'form': form,
        'two_factor_settings': two_factor_settings,
    }
    
    return render(request, 'nova2fa/change_method.html', context)