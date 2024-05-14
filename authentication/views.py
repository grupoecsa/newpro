from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Cambia 'index' por el nombre de la URL de tu página principal
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos.'})
    else:
        return render(request, 'login.html')

from django.shortcuts import render

def index(request):
    # Aquí puedes realizar cualquier lógica necesaria para mostrar datos en la página principal
    return render(request, 'index.html') 

def user_logout(request):
    logout(request)
    return redirect('login')  # Cambia 'login' por el nombre de la URL de tu página de inicio de sesión
