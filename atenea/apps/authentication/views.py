from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DoctorLoginForm
from .models import Doctor


def login_view(request):
    form = DoctorLoginForm()

    if request.method == "POST":
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get("correo")
            contraseña = form.cleaned_data.get("contraseña")

            try:
                doctor = Doctor.objects.get(Correo=correo)
                if doctor.Contraseña == contraseña:
                    request.session['doctor_id'] = doctor.idDoctor
                    request.session['doctor_nombre'] = doctor.Nombre
                    messages.success(request, f'Bienvenido, {doctor.Nombre}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Credenciales incorrectas. Por favor, verifica tu correo y contraseña.')
            except Doctor.DoesNotExist:
                messages.error(request, 'Credenciales incorrectas. Por favor, verifica tu correo y contraseña.')

    return render(request, "accounts/login.html", {"form": form})