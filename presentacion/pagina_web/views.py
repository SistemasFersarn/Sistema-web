from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import json
from itertools import groupby
import os
from django.conf import settings

def menu_hamburguesa(request):
    return render(request, 'components\menu_hamburguesa.html')

def pie_de_pagina(request):
    return render(request, 'components\pie_de_pagina.html')

def interfaz_modificar(request):
    return render(request, 'components\interfaz_modificar.html')

def marcas(request):
    return render(request, 'pagina\marcas.html')

def home(request):
    contenido_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'contenido.json')
    notas_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'notes.json')

    try:
        # Leer contenido.json
        with open(contenido_path, "r", encoding="utf-8") as contenido_file:
            contenido_data = json.load(contenido_file)

        # Leer notes.json
        with open(notas_path, "r", encoding="utf-8") as notas_file:
            notas_data = json.load(notas_file)

        # Enviar ambos conjuntos de datos a la plantilla
        print(f"Datos enviados a la plantilla: contenido={contenido_data}, notas={notas_data}")  # Depuración
        return render(request, "pagina/home.html", {"contenido": contenido_data, "notas": notas_data})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/home.html", {"contenido": {"tarjetas": []}, "notas": {"notas": []}})

@login_required
def inicio_usuario(request):
    return render(request, 'pagina/inicio_usuario.html')

@login_required
def registro(request):
    return render(request, 'pagina/inicio_usuario.html')  # Muestra el formulario de login

def salir(request):
    logout(request)
    return redirect('/')


def marcas(request):
    return render(request, 'pagina/marcas.html')


def acerca_empresa(request):
    acerca_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'acerca.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(acerca_path, "r", encoding="utf-8") as acerca_file:
            acerca_data = json.load(acerca_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: data_data={acerca_data}")  # Depuración
        return render(request, "pagina/acerca_empresa.html", {"data": acerca_data})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos o un mensaje de error en caso de error
        return render(request, "pagina/acerca_empresa.html", {"data": {"error": "No se pudo cargar la información."}})


def atencion_al_cliente(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'atencion.json')

    # Leer el archivo JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Asegurar que 'notas' es un diccionario en lugar de una lista
    notas = data.get('notas', {})

    # Agregar los iconos al contexto
    icons = {
        'icon_fon': data.get('icon_fon', ''),
        'icon_email': data.get('icon_email', '')
    }

    return render(request, 'pagina/atencion_al_cliente.html', {'notas': notas, 'icon_fon': icons['icon_fon'], 'icon_email': icons['icon_email']})



def localizador_agencias(request):
    # Cargar el archivo JSON con codificación UTF-8
    file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'loc_agencia.json')

    # Leer el archivo JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Transformar el JSON en una lista de agencias con su categoría (marca)
    agencias = []
    for categoria, agencias_list in data['agencias'].items():
        for agencia in agencias_list:
            agencia['categoria'] = categoria  # Agregar la categoría (marca) a cada agencia
            agencias.append(agencia)

    # Agrupar agencias por categoría
    grouped_agencias = {
        categoria: list(agencias_iter)
        for categoria, agencias_iter in groupby(sorted(agencias, key=lambda x: x['categoria']), key=lambda x: x['categoria'])
    }

    # Renderizar la plantilla con los datos
    return render(request, 'pagina/localizador_agencias.html', {'grouped_agencias': grouped_agencias})

def volkswagen(request):
    vw_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'vw.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(vw_path, "r", encoding="utf-8") as vw_file:
            vw_data = json.load(vw_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: vw_volkswagen={vw_data}")  # Depuración
        return render(request, "pagina/volkswagen.html", {"vw": vw_data})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/volkswagen.html", {"vw": {"vw_info": []}})

def suzuki(request):
    suzuki_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'suzuki.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(suzuki_path, "r", encoding="utf-8") as suzuki_file:
            suzuki_info = json.load(suzuki_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: suzuki={suzuki_info}")  # Depuración
        return render(request, "pagina/suzuki.html", {"suzuki": suzuki_info})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/suzuki.html", {"suzuki": {"suzuki_info": []}})

def harley(request):
    harley_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'harley.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(harley_path, "r", encoding="utf-8") as harley_file:
            harley_data = json.load(harley_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: vw_volkswagen={harley_data}")  # Depuración
        return render(request, "pagina/harley.html", {"harley": harley_data})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/harley.html", {"harley": {"harley_info": []}})

def seat(request):
    seat_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'seat.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(seat_path, "r", encoding="utf-8") as seat_file:
            seat_info = json.load(seat_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: seat={seat_info}")  # Depuración
        return render(request, "pagina/seat.html", {"seat": seat_info})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/seat.html", {"seat": {"seat_info": []}})

def omoda(request):
    omoda_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'omoda.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(omoda_path, "r", encoding="utf-8") as omoda_file:
            omoda_info = json.load(omoda_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: omoda={omoda_info}")  # Depuración
        return render(request, "pagina/omoda.html", {"omoda": omoda_info})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/omoda.html", {"omoda": {"omoda_info": []}})

def sev(request):
    sev_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'sev.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(sev_path, "r", encoding="utf-8") as sev_file:
            sev_info = json.load(sev_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: sev={sev_info}")  # Depuración
        return render(request, "pagina/sev.html", {"sev": sev_info})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/sev.html", {"sev": {"sev_info": []}})

def zeekr(request):
    zeekr_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'zeekr.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(zeekr_path, "r", encoding="utf-8") as zeekr_file:
            zeekr_info = json.load(zeekr_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: zeekr={zeekr_info}")  # Depuración
        return render(request, "pagina/zeekr.html", {"zeekr": zeekr_info})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/zeekr.html", {"zeekr": {"zeekr_info": []}})

def chirey(request):
    chirey_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'chirey.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(chirey_path, "r", encoding="utf-8") as chirey_file:
            chirey_info = json.load(chirey_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: chirey={chirey_info}")  # Depuración
        return render(request, "pagina/chirey.html", {"chirey": chirey_info})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/chirey.html", {"chirey": {"chirey_info": []}})

def motornation(request):
    motor_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'motor.json')

    try:
        # Leer el archivo JSON con codificación UTF-8 para asegurar la correcta lectura de caracteres especiales
        with open(motor_path, "r", encoding="utf-8") as motor_file:
            motor_info = json.load(motor_file)

        # Enviar los datos a la plantilla
        print(f"Datos enviados a la plantilla: motor={motor_info}")  # Depuración
        return render(request, "pagina/motornation.html", {"motor": motor_info})

    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        # Enviar datos vacíos en caso de error
        return render(request, "pagina/motornation.html", {"motor": {"motor_info": []}})

