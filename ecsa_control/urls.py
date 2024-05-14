# En ecsa_control/urls.py

from django.contrib import admin
from django.urls import path, include
from authentication.views import user_login, user_logout, index
from generador_qr.views import generar_interfaz  # Importa la nueva vista generar_interfaz
from django.conf import settings
from django.conf.urls.static import static
from power_report.views import generate_report

urlpatterns = [
    path('admin/', admin.site.urls),  # URL para el panel de administración de Django
    path('login/', user_login, name='login'),  # URL para el inicio de sesión
    path('logout/', user_logout, name='logout'),  # URL para cerrar sesión
    path('index/', index, name='index'),  # URL para la página principal
    path('generar/', generar_interfaz, name='generar_qr'),  # Asocia /generar/ con la vista generar_interfaz
    path('power-report/', generate_report, name='power_report'),  # Ajusta la URL según tu preferencia
    path('generate-report/', generate_report, name='generate_report'),


    # Otras URLs de tu proyecto aquí
]

# Configuración para servir archivos estáticos en modo de desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
