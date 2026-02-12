from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile

class UsernameMobileAuthenticationForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    mobile_number = forms.CharField(max_length=15, label='Mobile Number', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        mobile_number = cleaned_data.get('mobile_number')
        password = cleaned_data.get('password')
        if not username or not mobile_number or not password:
            raise forms.ValidationError('All fields are required.')
        try:
            user = User.objects.get(username=username)
            if not hasattr(user, 'profile') or user.profile.mobile_number != mobile_number:
                raise forms.ValidationError('Username and mobile number do not match.')
            if not user.check_password(password):
                raise forms.ValidationError('Invalid password.')
            if not user.is_active:
                raise forms.ValidationError('This account is inactive.')
            cleaned_data['user'] = user
        except User.DoesNotExist:
            raise forms.ValidationError('Invalid username or mobile number.')
        return cleaned_data


# Form for unlock request
from .models import UnlockRequest, FlipBook

class UnlockRequestForm(forms.ModelForm):
    class Meta:
        model = UnlockRequest
        fields = ['flipbook', 'candidate_full_name', 'date_of_birth', 'parents_mobile_number', 'marital_status', 'terms_accepted']
        widgets = {
            'flipbook': forms.HiddenInput(),
            'candidate_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parents_mobile_number': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'marital_status': forms.Select(attrs={'class': 'form-control'}),
            'terms_accepted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_terms_accepted(self):
        terms = self.cleaned_data.get('terms_accepted')
        if not terms:
            raise forms.ValidationError('You must accept the terms and conditions.')
        return terms
