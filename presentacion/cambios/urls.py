from django.urls import path
from . import views

urlpatterns = [
    path('editar/', views.editar_contenido, name='editar_contenido'),
    path('editar_n/', views.editar_notas, name='editar_notas'),
    
    path('editar_vw/', views.editar_vw, name='editar_vw'),
    path('editar_suzuki/', views.editar_suzuki, name='editar_suzuki'),
    path('editar_harley', views.editar_harley, name='editar_harley'),
    path('editar_seat', views.editar_seat, name='editar_seat'),
    path('editar_omoda', views.editar_omoda, name='editar_omoda'),
    path('editar_sev', views.editar_sev, name='editar_sev'),
    path('editar_zeekr', views.editar_zeekr, name='editar_zeekr'),
    path('editar_chirey', views.editar_chirey, name='editar_chirey'),
    path('editar_motor', views.editar_motor, name='editar_motor'),

    
    path('editar_horarios', views.editar_horarios, name='editar_horarios'),
    path('editar_ubicacion', views.editar_ubicacion, name='editar_ubicacion'),
    path('editar_loc_ag', views.editar_loc_ag, name='editar_loc_ag'),
    path('editar_atencion', views.editar_atencion, name='editar_atencion'),
    path('editar_acerca', views.editar_acerca, name='editar_acerca'),
    path('editar_carrusel', views.editar_carrusel, name='editar_carrusel'),
    
]