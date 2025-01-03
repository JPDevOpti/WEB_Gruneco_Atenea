from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
    )

    # Sobrecargamos el método 'confirm_login_allowed' para autenticar por email en lugar de username
    def confirm_login_allowed(self, user):
        if not user.email:
            raise forms.ValidationError("Este correo no está registrado.")
        return super().confirm_login_allowed(user)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("username")
        password = cleaned_data.get("password")
        
        # Verificamos si el usuario existe con el email
        user = authenticate(username=email, password=password)
        if user is None:
            raise forms.ValidationError("Correo o contraseña incorrectos.")
        
        return cleaned_data

