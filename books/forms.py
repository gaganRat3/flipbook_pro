from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email


class UsernameEmailAuthenticationForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    email = forms.EmailField(label='Email', required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if not username or not email or not password:
            raise forms.ValidationError('All fields are required.')
        try:
            user = User.objects.get(username=username, email=email)
            if not user.check_password(password):
                raise forms.ValidationError('Invalid password.')
            if not user.is_active:
                raise forms.ValidationError('This account is inactive.')
            cleaned_data['user'] = user
        except User.DoesNotExist:
            raise forms.ValidationError('Invalid username or email.')
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
