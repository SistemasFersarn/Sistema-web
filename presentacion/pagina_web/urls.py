from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('menu_hamburguesa/', views.menu_hamburguesa, name='menu_hamburguesa'),
    path('pie_de_pagina/', views.pie_de_pagina, name='pie_de_pagina'),
    path('interfaz_modificar/', views.interfaz_modificar, name='interfaz_modificar'),

    #PAGINA INICIAL
    path('home/', views.home, name='home'),

    #MENU LATERAL
    path('registro/', views.registro, name='registro'),
    path('inicio_usuario/', views.inicio_usuario, name='inicio_usuario'),
    path('marcas/', views.marcas, name='marcas'),  

    #path('cita_servicio/', views.agendar_cita, name='agendar_cita'),
    #path('cita_confirmada/', views.cita_confirmada, name='cita_confirmada'),  
    
    path('acerca_empresa/', views.acerca_empresa, name='acerca_empresa'),
    path('atencion_al_cliente/', views.atencion_al_cliente, name='atencion_al_cliente'),
    path('localizador_agencias/', views.localizador_agencias, name='localizador_agencias'),

    #INFO DE LAS MARCAS
    path('volkswagen/', views.volkswagen, name='volkswagen'),
    path('suzuki/', views.suzuki, name='suzuki'),
    path('harley/', views.harley, name='harley'),
    path('seat/', views.seat, name='seat'),
    path('omoda/', views.omoda, name='omoda'),
    path('sev/', views.sev, name='sev'),
    path('zeekr/', views.zeekr, name='zeekr'),
    path('chirey/', views.chirey, name='chirey'),
    path('motornation/', views.motornation, name='motornation'),

    #Sesion
    path('salir/', views.salir, name="salir"),

]


    
