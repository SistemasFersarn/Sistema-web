from django.contrib import messages
from django.shortcuts import render
import json
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings

@login_required
def editar_contenido(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'contenido.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar.html", {"contenido": {}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción: agregar, eliminar o editar
        try:
            if action == "add":
                try:
                    # Determinar el índice de la nueva tarjeta
                    nuevo_idx = len(data["tarjetas"])

                    # Obtener los datos del formulario
                    nuevo_titulo = request.POST.get("nuevo_titulo", "Nuevo título")
                    nueva_descripcion = request.POST.get("nueva_descripcion", "Nueva descripción")
                    nueva_imagen = request.FILES.get("nueva_imagen")  # Obtener la imagen subida

                    # Ruta absoluta para guardar la nueva imagen
                    if nueva_imagen:
                        ruta_imagen_absoluta = os.path.join(
                            settings.BASE_DIR, "static", "images", "INFORMACION_FERSAN", f"tarjeta_{nuevo_idx + 1}.png"
                        )
                        os.makedirs(os.path.dirname(ruta_imagen_absoluta), exist_ok=True)  # Crear el directorio si no existe
                        with open(ruta_imagen_absoluta, "wb") as img_file:
                            for chunk in nueva_imagen.chunks():
                                img_file.write(chunk)

                        # Ruta relativa para almacenar en JSON
                        ruta_imagen = os.path.relpath(ruta_imagen_absoluta, os.path.join(settings.BASE_DIR, "static"))
                    else:
                        ruta_imagen = "images/INFORMACION_FERSAN/default.png"  # Imagen por defecto

                    # Crear la nueva tarjeta
                    nueva_tarjeta = {
                        "titulo": nuevo_titulo,
                        "descripcion": nueva_descripcion,
                        "imagen": ruta_imagen  # Guardar la ruta relativa en el JSON
                    }

                    # Agregar la tarjeta a los datos existentes
                    data["tarjetas"].append(nueva_tarjeta)

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Tarjeta agregada exitosamente.")
                except Exception as e:
                    messages.error(request, f"Ocurrió un error al agregar la tarjeta: {str(e)}")

            elif action.startswith("delete_"):
                # Extraer el índice de la tarjeta a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["tarjetas"]):
                    tarjeta_eliminada = data["tarjetas"].pop(idx)

                    # Eliminar imagen asociada
                    imagen_path = tarjeta_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Renombrar las imágenes de las tarjetas restantes
                    for new_idx, tarjeta in enumerate(data["tarjetas"]):
                        nueva_imagen_path_relativa = f"images/INFORMACION_FERSAN/tarjeta_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", nueva_imagen_path_relativa)

                        # Obtener la ruta absoluta de la imagen anterior
                        old_imagen_path_relativa = tarjeta["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        # Renombrar físicamente si existe el archivo
                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)

                        # Actualizar la ruta en la estructura JSON
                        tarjeta["imagen"] = nueva_imagen_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Tarjeta eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de tarjeta no válido.")


            elif action == "edit":
                try:
                    # Obtener el número total de tarjetas existentes
                    tarjetas_existentes = len(data["tarjetas"])

                    for idx in range(tarjetas_existentes):
                        # Obtener los nuevos valores de título y descripción desde el formulario
                        titulo = request.POST.get(f"titulo_{idx}", "").strip()
                        descripcion = request.POST.get(f"descripcion_{idx}", "").strip()

                        # Si no se envían valores, conservar los originales
                        data["tarjetas"][idx]["titulo"] = titulo if titulo else data["tarjetas"][idx]["titulo"]
                        data["tarjetas"][idx]["descripcion"] = descripcion if descripcion else data["tarjetas"][idx]["descripcion"]

                        # Verificar si hay una nueva imagen cargada para esta tarjeta
                        imagen_key = f"imagen_{idx}"
                        if imagen_key in request.FILES:
                            imagen = request.FILES[imagen_key]

                            # Construir la ruta absoluta para la nueva imagen
                            ruta_imagen_absoluta = os.path.join(
                                settings.BASE_DIR, "static", "images", "INFORMACION_FERSAN", f"tarjeta_{idx + 1}.png"
                            )

                            # Eliminar la imagen anterior si existe
                            imagen_anterior_relativa = data["tarjetas"][idx]["imagen"]
                            imagen_anterior_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_anterior_relativa)
                            if os.path.exists(imagen_anterior_absoluta):
                                os.remove(imagen_anterior_absoluta)

                            # Crear directorio si no existe
                            os.makedirs(os.path.dirname(ruta_imagen_absoluta), exist_ok=True)

                            # Guardar la nueva imagen
                            with open(ruta_imagen_absoluta, "wb") as img_file:
                                for chunk in imagen.chunks():
                                    img_file.write(chunk)

                            # Actualizar la ruta de la imagen en el JSON (guardar solo la ruta relativa)
                            ruta_imagen_relativa = os.path.relpath(ruta_imagen_absoluta, os.path.join(settings.BASE_DIR, "static"))
                            data["tarjetas"][idx]["imagen"] = ruta_imagen_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Tarjetas actualizadas exitosamente.")
                except Exception as e:
                    messages.error(request, f"Ocurrió un error al editar las tarjetas: {str(e)}")


            # Guardar cambios en el archivo JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")

        return render(request, "editar.html", {"contenido": data})

    return render(request, "editar.html", {"contenido": data})



@login_required
def editar_notas(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'notes.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_n.html", {"notes": {}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción: agregar, eliminar o editar
        try:
            if action == "add":
                try:
                    # Crear una nueva nota
                    nuevo_idx = len(data["notas"])
                    titulo = request.POST.get("nuevo_titulo", "Nuevo título")
                    descripcion = request.POST.get("nueva_descripcion", "Nueva descripción")
                    enlace = request.POST.get("nuevo_enlace", "#")
                    nueva_imagen = request.FILES.get("nueva_imagen")  # Obtener la imagen subida

                    # Ruta para guardar la nueva imagen
                    if nueva_imagen:
                        ruta_imagen_absoluta = os.path.join(
                                settings.BASE_DIR, "static", "images", "Notas", f"nota_{nuevo_idx + 1}.png"
                            )
                        os.makedirs(os.path.dirname(ruta_imagen_absoluta), exist_ok=True)  # Crear el directorio si no existe
                        with open(ruta_imagen_absoluta, "wb") as img_file:
                            for chunk in nueva_imagen.chunks():
                                img_file.write(chunk)

                        # Ruta relativa para almacenar en JSON
                        ruta_imagen = os.path.relpath(ruta_imagen_absoluta, os.path.join(settings.BASE_DIR, "static"))

                    else:
                        ruta_imagen = "images/Notas/default.png"  # Imagen por defecto

                    # Crear la nueva nota
                    nueva_nota = {
                        "titulo": titulo,
                        "descripcion": descripcion,
                        "enlace": enlace,
                        "imagen": ruta_imagen  # Guardar la ruta relativa
                    }

                    # Agregar la nueva nota a los datos
                    data["notas"].append(nueva_nota)

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Nota agregada exitosamente.")
                except Exception as e:
                    messages.error(request, f"Ocurrió un error al agregar la Nota: {str(e)}")


            elif action.startswith("delete_"):
                # Extraer el índice de la nota a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["notas"]):
                    nota_eliminada = data["notas"].pop(idx)

                    # Eliminar imagen asociada
                    imagen_path = nota_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Renombrar imágenes restantes
                    for new_idx, nota in enumerate(data["notas"]):
                        nueva_imagen_path_relativa = f"images/Notas/nota_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", nueva_imagen_path_relativa)

                        # Obtener la ruta absoluta de la imagen anterior
                        old_imagen_path_relativa = nota["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)


                        # Renombrar físicamente si existe el archivo
                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)


                        nota["imagen"] = nueva_imagen_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Nota eliminada correctamente.")
                else:
                    messages.error(request, "Índice de nota no válido.")

            elif action == "edit":
                try:
                    # Editar notas existentes
                    notas_existentes = len(data["notas"])

                    for idx in range(notas_existentes):
                        titulo = request.POST.get(f"titulo_{idx}", data["notas"][idx].get("titulo", ""))
                        descripcion = request.POST.get(f"descripcion_{idx}", data["notas"][idx].get("descripcion", ""))
                        enlace = request.POST.get(f"enlace_{idx}", data["notas"][idx].get("enlace", ""))

                        # Actualizar los datos
                        data["notas"][idx]["titulo"] = titulo
                        data["notas"][idx]["descripcion"] = descripcion
                        data["notas"][idx]["enlace"] = enlace

                        # Procesar la nueva imagen, si se proporciona
                        imagen_key = f"imagen_{idx}"
                        if imagen_key in request.FILES:
                            imagen = request.FILES[imagen_key]

                            ruta_imagen_absoluta = os.path.join(
                                    settings.BASE_DIR, "static", "images", "Notas", f"nota_{idx + 1}.png"
                                )
                            # Eliminar imagen anterior si existe
                            imagen_anterior_relativa = os.path.join("static", data["notas"][idx]["imagen"])
                            imagen_anterior_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_anterior_relativa)
                            if os.path.exists(imagen_anterior_absoluta):
                                os.remove(imagen_anterior_absoluta)

                            # Crear directorio si no existe
                            os.makedirs(os.path.dirname(ruta_imagen_absoluta), exist_ok=True)

                            # Guardar la nueva imagen
                            with open(ruta_imagen_absoluta, "wb") as img_file:
                                for chunk in imagen.chunks():
                                    img_file.write(chunk)

                            # Actualizar la ruta en el JSON
                            ruta_imagen_relativa = os.path.relpath(ruta_imagen_absoluta, os.path.join(settings.BASE_DIR, "static"))
                            data["notas"][idx]["imagen"] = ruta_imagen_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Notas editadas correctamente.")
                except Exception as e:
                    messages.error(request, f"Ocurrió un error al editar las tarjetas: {str(e)}")

            # Guardar cambios en el archivo JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")

        return render(request, "editar_n.html", {"notes": data})

    return render(request, "editar_n.html", {"notes": data})


@login_required
def editar_carrusel(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'carrusel.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_carrusel.html", {"nota": {"carrusel_info": []}})

    # Convertir las claves del JSON en una lista para poder iterar sobre ellas
    carrusel_info = [
        {"categoria": agencia["categoria"], "image": agencia["image"], "text": agencia["text"]}
        for agencia in data.values()
    ]

    if request.method == "POST":
        try:
            # Actualizar datos existentes
            for idx, (key, agencia) in enumerate(data.items()):
                agencia["text"] = request.POST.get(f"tex_{idx}", agencia["text"])

                # Procesar logo si se actualiza
                image_key = f"image_{idx}"
                if image_key in request.FILES:
                    image = request.FILES[image_key]
                    ruta_imagen_absoluta = os.path.join(settings.BASE_DIR, 'static', 'images', f'carrusel_agencia_{idx + 1}.png')
                    # Crear directorio si no existe
                    os.makedirs(os.path.dirname(ruta_imagen_absoluta), exist_ok=True)


                    with open(ruta_imagen_absoluta, "wb") as image_file:
                        for chunk in image.chunks():
                            image_file.write(chunk)

                    agencia["image"] = f"/static/images/carrusel_agencia_{idx + 1}.png"

            # Guardar los cambios en el archivo JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            messages.success(request, "Los cambios se realizaron con éxito.")

        except Exception as e:
            messages.error(request, f"Ocurrió un error al guardar los cambios: {str(e)}")
            return render(request, "editar_carrusel.html", {"nota": {"carrusel_info": carrusel_info}})

    # Renderizar la página con los datos existentes
    return render(request, "editar_carrusel.html", {"nota": {"carrusel_info": carrusel_info}})



""" Agencias------------------------------------------------------------------------------------------------------------ """

@login_required
def editar_vw(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'vw.json')

    # Intentar leer el archivo JSON
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_vw.html", {"vw": {"vw_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["vw_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_vw_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"vw_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["vw_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["vw_info"]):
                    agencia_eliminada = data["vw_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, vw_info in enumerate(data["vw_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/vw_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = vw_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            vw_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_vw_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = vw_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            vw_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["vw_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_vw_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"vw_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    return render(request, "editar_vw.html", {"vw": {"vw_info": data["vw_info"]}})



@login_required
def editar_suzuki(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'suzuki.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_suzuki.html", {"suzuki": {"suzuki_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["suzuki_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_suzuki_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"suzuki_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["suzuki_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["suzuki_info"]):
                    agencia_eliminada = data["suzuki_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, suzuki_info in enumerate(data["suzuki_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/suzuki_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = suzuki_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            suzuki_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_suzuki_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = suzuki_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            suzuki_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["suzuki_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_suzuki_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"suzuki_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    return render(request, "editar_suzuki.html", {"suzuki": {"suzuki_info": data["suzuki_info"]}})


@login_required
def editar_harley(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'harley.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_harley.html", {"harley": {"harley_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["harley_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_harley_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"harley_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["harley_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["harley_info"]):
                    agencia_eliminada = data["harley_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, harley_info in enumerate(data["harley_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/harley_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = harley_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            harley_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_harley_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = harley_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            harley_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["harley_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_harley_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"harley_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    # Renderizar la página con los datos existentes
    return render(request, "editar_harley.html", {"harley": {"harley_info": data["harley_info"]}})


@login_required
def editar_omoda(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'omoda.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_omoda.html", {"omoda": {"omoda_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["omoda_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_omoda_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"omoda_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["omoda_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["omoda_info"]):
                    agencia_eliminada = data["omoda_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, omoda_info in enumerate(data["omoda_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/omoda_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = omoda_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            omoda_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_omoda_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = omoda_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            omoda_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["omoda_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_omoda_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"omoda_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    # Renderizar la página con los datos existentes
    return render(request, "editar_omoda.html", {"omoda": {"omoda_info": data["omoda_info"]}})


@login_required
def editar_seat(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'seat.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_seat.html", {"seat": {"seat_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["seat_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_seat_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"seat_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["seat_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["seat_info"]):
                    agencia_eliminada = data["seat_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, seat_info in enumerate(data["seat_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/seat_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = seat_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            seat_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_seat_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = seat_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            seat_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["seat_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_seat_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"seat_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    # Renderizar la página con los datos existentes
    return render(request, "editar_seat.html", {"seat": {"seat_info": data["seat_info"]}})


@login_required
def editar_sev(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'sev.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_sev.html", {"sev": {"sev_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["sev_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_sev_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"sev_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["sev_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["sev_info"]):
                    agencia_eliminada = data["sev_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, sev_info in enumerate(data["sev_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/sev_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = sev_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            sev_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_sev_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = sev_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            sev_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["sev_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_sev_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"sev_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    # Renderizar la página con los datos existentes
    return render(request, "editar_sev.html", {"sev": {"sev_info": data["sev_info"]}})


@login_required
def editar_zeekr(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'zeekr.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_zeekr.html", {"zeekr": {"zeekr_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["zeekr_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_zeekr_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"zeekr_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["zeekr_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["zeekr_info"]):
                    agencia_eliminada = data["zeekr_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, zeekr_info in enumerate(data["zeekr_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/zeekr_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = zeekr_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            zeekr_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_zeekr_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = zeekr_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            zeekr_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["zeekr_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_zeekr_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"zeekr_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    # Renderizar la página con los datos existentes
    return render(request, "editar_zeekr.html", {"zeekr": {"zeekr_info": data["zeekr_info"]}})


@login_required
def editar_chirey(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'chirey.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_chirey.html", {"chirey": {"chirey_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["chirey_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_chirey_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"chirey_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["chirey_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["chirey_info"]):
                    agencia_eliminada = data["chirey_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, chirey_info in enumerate(data["chirey_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/chirey_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = chirey_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            chirey_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_chirey_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = chirey_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            chirey_info["logo"] = nueva_logo_path_relativa



                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["chirey_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_chirey_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"chirey_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    # Renderizar la página con los datos existentes
    return render(request, "editar_chirey.html", {"chirey": {"chirey_info": data["chirey_info"]}})


@login_required
def editar_motor(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'motor.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        # Si ocurre un error al leer el archivo JSON
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_motor.html", {"motor": {"motor_info": []}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción que indica qué operación realizar
        try:
            if action == "add":
                # Agregar una nueva agencia
                nuevo_idx = len(data["motor_info"])
                nueva_agencia = {
                    "lugar": request.POST.get("nuevo_lugar", "").strip(),
                    "logo": "images/LOGO_SUCURSAL/default.png",  # Imagen por defecto
                    "imagen": "images/default.png",
                    "concecionario": request.POST.get("nuevo_concecionario", "").strip(),
                    "direccion": request.POST.get("nueva_direccion", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "facebook": request.POST.get("nuevo_facebook", "").strip(),
                    "instagram": request.POST.get("nuevo_instagram", "").strip(),
                    "whatsapp": request.POST.get("nuevo_whatsapp", "").strip(),
                    "linkedin": request.POST.get("nuevo_linkedin", "").strip(),
                }

                # Guardar logo si se proporciona
                nuevo_logo = request.FILES.get("nuevo_logo")
                if nuevo_logo:
                    extension = os.path.splitext(nuevo_logo.name)[1]
                    nombre_logo = f"logo_motor_{nuevo_idx + 1}{extension}"
                    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)
                    os.makedirs(os.path.dirname(ruta_logo), exist_ok=True)

                    with open(ruta_logo, "wb") as file:
                        for chunk in nuevo_logo.chunks():
                            file.write(chunk)

                    nueva_agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                # Guardar imagen si se proporciona
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"motor_{nuevo_idx + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/{nombre_imagen}"

                data["motor_info"].append(nueva_agencia)
                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                # Extraer el índice de la agencia a eliminar
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["motor_info"]):
                    agencia_eliminada = data["motor_info"].pop(idx)

                    # Eliminar imágenes asociadas si no son "default.png"
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Eliminar logo asociado si no es el predeterminado
                    logo_path = agencia_eliminada.get("logo")
                    logo_absoluta = os.path.join(settings.BASE_DIR, "static", logo_path)
                    if logo_path and os.path.exists(logo_absoluta):
                        os.remove(logo_absoluta)

                    # Renombrar imágenes y logos restantes
                    for new_idx, motor_info in enumerate(data["motor_info"]):
                        # Renombrar imagen
                        nueva_imagen_path_relativa = f"images/motor_{new_idx + 1}.png"
                        nueva_imagen_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_imagen_path_relativa)
                        old_imagen_path_relativa = motor_info["imagen"]
                        old_imagen_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_imagen_path_relativa)

                        if os.path.exists(old_imagen_path_absoluta):
                            os.rename(old_imagen_path_absoluta, nueva_imagen_path_absoluta)
                            motor_info["imagen"] = nueva_imagen_path_relativa

                        # Renombrar logo
                        nueva_logo_path_relativa = f"images/LOGO_SUCURSAL/logo_motor_{new_idx + 1}.png"
                        nueva_logo_path_absoluta = os.path.join(settings.BASE_DIR, 'static', nueva_logo_path_relativa)
                        old_logo_path_relativa = motor_info["logo"]
                        old_logo_path_absoluta = os.path.join(settings.BASE_DIR, "static", old_logo_path_relativa)

                        if os.path.exists(old_logo_path_absoluta):
                            os.rename(old_logo_path_absoluta, nueva_logo_path_absoluta)
                            motor_info["logo"] = nueva_logo_path_relativa

                    # Guardar los cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Agencia eliminada y archivos actualizados correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                # Editar agencias existentes
                for idx, agencia in enumerate(data["motor_info"]):
                    agencia["lugar"] = request.POST.get(f"lugar_{idx}", agencia["lugar"]).strip()
                    agencia["concecionario"] = request.POST.get(f"concecionario_{idx}", agencia["concecionario"]).strip()
                    agencia["direccion"] = request.POST.get(f"direccion_{idx}", agencia["direccion"]).strip()
                    agencia["enlace"] = request.POST.get(f"enlace_{idx}", agencia["enlace"]).strip()
                    agencia["telefono"] = request.POST.get(f"telefono_{idx}", agencia["telefono"]).strip()
                    agencia["facebook"] = request.POST.get(f"facebook_{idx}", agencia["facebook"]).strip()
                    agencia["instagram"] = request.POST.get(f"instagram_{idx}", agencia["instagram"]).strip()
                    agencia["whatsapp"] = request.POST.get(f"whatsapp_{idx}", agencia["whatsapp"]).strip()
                    agencia["linkedin"] = request.POST.get(f"linkedin_{idx}", agencia["linkedin"]).strip()

                    # Procesar nuevo logo
                    logo_key = f"logo_{idx}"
                    if logo_key in request.FILES:
                        nuevo_logo = request.FILES[logo_key]
                        extension = os.path.splitext(nuevo_logo.name)[1]
                        nombre_logo = f"logo_motor_{idx + 1}{extension}"
                        ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'images', 'LOGO_SUCURSAL', nombre_logo)

                        with open(ruta_logo, "wb") as file:
                            for chunk in nuevo_logo.chunks():
                                file.write(chunk)

                        agencia["logo"] = f"images/LOGO_SUCURSAL/{nombre_logo}"

                    # Procesar nueva imagen
                    imagen_key = f"imagen_{idx}"
                    if imagen_key in request.FILES:
                        nueva_imagen = request.FILES[imagen_key]
                        extension = os.path.splitext(nueva_imagen.name)[1]
                        nombre_imagen = f"motor_{idx + 1}{extension}"
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', nombre_imagen)

                        with open(ruta_imagen, "wb") as file:
                            for chunk in nueva_imagen.chunks():
                                file.write(chunk)

                        agencia["imagen"] = f"images/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    # Renderizar la página con los datos existentes
    return render(request, "editar_motor.html", {"motor": {"motor_info": data["motor_info"]}})


@login_required
def editar_horarios(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'horarios.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_horarios.html", {"hora": {}})

    if request.method == "POST":
        action = request.POST.get("action")  # Acción: add, edit, delete
        try:
            if action == "add":
                # Crear una nueva tarjeta de horario
                agencia = request.POST.get("agencia", "")
                departamento = request.POST.get("nuevo_departamento", "Nuevo Departamento")
                horarios = request.POST.get("nuevo_horario", "Nuevo Horario")

                if agencia not in data["horarios"]:
                    data["horarios"][agencia] = []

                nueva_tarjeta = {
                    "departamento": departamento,
                    "horarios": horarios,
                }

                # Agregar la nueva tarjeta a la agencia
                data["horarios"][agencia].append(nueva_tarjeta)

                # Guardar cambios en el archivo JSON
                with open(json_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

                messages.success(request, "Nuevo horario agregado con éxito.")

            elif action.startswith("delete_"):
                # Dividir la acción para obtener la agencia y el índice
                parts = action.split("_")  # Divide usando "_"

                if len(parts) == 3:  # Verifica que tenga la estructura esperada
                    agencia, idx = parts[1], int(parts[2])

                    if agencia in data["horarios"] and 0 <= idx < len(data["horarios"][agencia]):
                        data["horarios"][agencia].pop(idx)

                        # Guardar cambios en el archivo JSON
                        with open(json_path, "w", encoding="utf-8") as file:
                            json.dump(data, file, indent=4, ensure_ascii=False)

                        messages.success(request, "Horario eliminado con éxito.")
                    else:
                        messages.error(request, "Índice no válido para eliminar el horario.")
                else:
                    messages.error(request, "Formato de acción no válido.")


            elif action == "edit":
                for agencia, departamentos in data["horarios"].items():
                    for idx, depto in enumerate(departamentos):
                        # Usamos el índice y agencia para obtener los datos correctos
                        departamento_key = f"departamento_{agencia}_{idx}"
                        horarios_key = f"horarios_{agencia}_{idx}"

                        # Obtener los datos desde el formulario (con un valor predeterminado si no se envía)
                        departamento = request.POST.get(departamento_key, depto["departamento"])
                        horarios = request.POST.get(horarios_key, depto["horarios"])

                        # Actualizamos los datos del departamento
                        depto["departamento"] = departamento
                        depto["horarios"] = horarios

                # Guardamos los cambios en el archivo JSON
                with open(json_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

                messages.success(request, "Horarios actualizados con éxito.")


        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar la solicitud: {str(e)}")

        return render(request, "editar_horarios.html", {"hora": data})

    return render(request, "editar_horarios.html", {"hora": data})



@login_required
def editar_ubicacion(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'ubicacion.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_ubicacion.html", {"ubicacion": {}})

    if request.method == "POST":
        action = request.POST.get("action")  # Determinar la acción: add, edit, delete
        try:
            if action == "add":
                # Agregar una nueva tarjeta
                encabezado = request.POST.get("nuevo_encabezado", "").strip()
                direccion = request.POST.get("nueva_direccion", "").strip()
                telefono = request.POST.get("nuevo_telefono", "").strip()

                if encabezado and direccion and telefono:
                    nueva_tarjeta = {
                        "encabezado": encabezado,
                        "direccion": direccion,
                        "telefono": telefono,
                    }
                    data["pie_ubicacion"].append(nueva_tarjeta)

                    # Guardar cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, "Nueva tarjeta de ubicación agregada con éxito.")
                else:
                    messages.error(request, "Todos los campos son obligatorios para agregar una nueva tarjeta.")

            elif action.startswith("delete_"):
                # Eliminar una tarjeta específica por índice
                idx = int(action.split("_")[1])
                if 0 <= idx < len(data["pie_ubicacion"]):
                    data["pie_ubicacion"].pop(idx)

                    # Guardar cambios en el archivo JSON
                    with open(json_path, "w", encoding="utf-8") as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    messages.success(request, f"Tarjeta de ubicación {idx + 1} eliminada con éxito.")
                else:
                    messages.error(request, "Índice no válido para eliminar la tarjeta.")

            elif action == "edit":
                # Editar tarjetas existentes
                for idx in range(len(data["pie_ubicacion"])):
                    encabezado = request.POST.get(f"encabezado_{idx}", data["pie_ubicacion"][idx]["encabezado"]).strip()
                    direccion = request.POST.get(f"direccion_{idx}", data["pie_ubicacion"][idx]["direccion"]).strip()
                    telefono = request.POST.get(f"telefono_{idx}", data["pie_ubicacion"][idx]["telefono"]).strip()

                    if encabezado and direccion and telefono:
                        data["pie_ubicacion"][idx]["encabezado"] = encabezado
                        data["pie_ubicacion"][idx]["direccion"] = direccion
                        data["pie_ubicacion"][idx]["telefono"] = telefono
                    else:
                        messages.error(request, f"Los campos no pueden estar vacíos en la tarjeta {idx + 1}.")

                # Guardar cambios en el archivo JSON
                with open(json_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)

                messages.success(request, "Tarjetas de ubicación actualizadas con éxito.")

        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar la solicitud: {str(e)}")

        return render(request, "editar_ubicacion.html", {"ubicacion": data})

    return render(request, "editar_ubicacion.html", {"ubicacion": data})


@login_required
def editar_loc_ag(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'loc_agencia.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_loc_ag.html", {"agencias": {}})

    if request.method == "POST":
        action = request.POST.get("action")

        try:
            if action == "add":
                categoria = request.POST.get("nueva_categoria", "").strip().lower()
                nueva_agencia = {
                    "nombre": request.POST.get("nueva_agencia", "").strip(),
                    "imagen": "images/default.png",
                    "contacto": request.POST.get("nuevo_contacto", "").strip(),
                    "enlace": request.POST.get("nuevo_enlace", "").strip(),
                }

                # Manejo de imagen
                nueva_imagen = request.FILES.get("nueva_imagen")
                if nueva_imagen:
                    extension = os.path.splitext(nueva_imagen.name)[1]
                    nombre_imagen = f"{categoria}_loc_agen_{len(data['agencias'].get(categoria, [])) + 1}{extension}"
                    ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', 'localizador_agencias', nombre_imagen)
                    os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)

                    with open(ruta_imagen, "wb") as file:
                        for chunk in nueva_imagen.chunks():
                            file.write(chunk)

                    nueva_agencia["imagen"] = f"images/localizador_agencias/{nombre_imagen}"

                # Agregar la nueva agencia a la categoría correspondiente
                if categoria in data["agencias"]:
                    data["agencias"][categoria].append(nueva_agencia)
                else:
                    data["agencias"][categoria] = [nueva_agencia]

                messages.success(request, "Nueva agencia agregada con éxito.")

            elif action.startswith("delete_"):
                categoria, idx = action.split("_")[1], int(action.split("_")[2])
                if categoria in data["agencias"] and 0 <= idx < len(data["agencias"][categoria]):
                    agencia_eliminada = data["agencias"][categoria].pop(idx)

                    # Eliminar la imagen si existe
                    imagen_path = agencia_eliminada.get("imagen")
                    imagen_absoluta = os.path.join(settings.BASE_DIR, "static", imagen_path)
                    if imagen_path and os.path.exists(imagen_absoluta):
                        os.remove(imagen_absoluta)

                    # Renombrar las imágenes restantes para mantener la numeración
                    for i, agencia in enumerate(data["agencias"][categoria]):
                        imagen_actual = agencia["imagen"]
                        extension = os.path.splitext(imagen_actual)[1]
                        nuevo_nombre = f"{categoria}_loc_agen_{i + 1}.png"
                        nueva_ruta = os.path.join(settings.BASE_DIR, 'static', 'images', 'localizador_agencias', nuevo_nombre)

                        imagen_absoluta_actual = os.path.join(settings.BASE_DIR, "static", imagen_actual)
                        if os.path.exists(imagen_absoluta_actual):
                            os.rename(imagen_absoluta_actual, nueva_ruta)

                        agencia["imagen"] = f"images/localizador_agencias/{nuevo_nombre}"

                    messages.success(request, "Agencia eliminada correctamente.")
                else:
                    messages.error(request, "Índice de agencia no válido.")

            elif action == "edit":
                for categoria, agencias_list in data["agencias"].items():
                    for idx, agencia in enumerate(agencias_list):
                        agencia["nombre"] = request.POST.get(f"nombre_{categoria}_{idx}", agencia["nombre"]).strip()
                        agencia["contacto"] = request.POST.get(f"contacto_{categoria}_{idx}", agencia["contacto"]).strip()
                        agencia["enlace"] = request.POST.get(f"enlace_{categoria}_{idx}", agencia["enlace"]).strip()

                        imagen_key = f"imagen_{categoria}_{idx}"
                        if imagen_key in request.FILES:
                            nueva_imagen = request.FILES[imagen_key]
                            extension = os.path.splitext(nueva_imagen.name)[1]
                            nombre_imagen = f"{categoria}_loc_agen_{idx + 1}{extension}"
                            ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', 'localizador_agencias', nombre_imagen)

                            with open(ruta_imagen, "wb") as file:
                                for chunk in nueva_imagen.chunks():
                                    file.write(chunk)

                            agencia["imagen"] = f"images/localizador_agencias/{nombre_imagen}"

                messages.success(request, "Agencias editadas con éxito.")

            # Guardar cambios en el JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    return render(request, "editar_loc_ag.html", {"agencias": data["agencias"]})


@login_required
def editar_atencion(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'atencion.json')

    # Cargar JSON
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_atencion.html", {"agencias": []})

    if request.method == "POST":
        action = request.POST.get("action")

        try:
            if action == "edit_icons":
                # Guardar iconos generales
                iconos = {
                    "icon_fon_global": "icon_tel_global.png",
                    "icon_email_global": "icon_email_global.png"
                }

                for key, filename in iconos.items():
                    if key in request.FILES:
                        imagen = request.FILES[key]
                        ruta_imagen = os.path.join(settings.BASE_DIR, 'static', 'images', filename)

                        os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)
                        with open(ruta_imagen, "wb") as imagen_file:
                            for chunk in imagen.chunks():
                                imagen_file.write(chunk)

                        # Actualizar JSON
                        data[key.replace("_global", "")] = f"images/{filename}"

                messages.success(request, "Íconos editados con éxito.")

            elif action == "add":
                nueva_categoria = request.POST.get("nueva_categoria", "").strip()
                nueva_agencia = {
                    "agencia": request.POST.get("nueva_agencia", "").strip(),
                    "telefono": request.POST.get("nuevo_telefono", "").strip(),
                    "correo": request.POST.get("nuevo_correo", "").strip(),
                }

                # Si la categoría no existe, inicializarla como una lista vacía
                if nueva_categoria not in data["notas"]:
                    data["notas"][nueva_categoria] = []

                # Agregar la nueva agencia a la categoría correcta
                data["notas"][nueva_categoria].append(nueva_agencia)

                messages.success(request, "Nueva agencia agregada con éxito.")


            elif action.startswith("delete_"):
                partes = action.split("_", 2)  # 🔹 Separa en 3 partes máximo: ["delete", "categoria", "idx"]

                if len(partes) < 3:
                    messages.error(request, "Formato de acción no válido.")
                    return redirect("alguna_vista")  # 🔹 Evita errores si falta algún dato

                categoria = partes[1]  # 🔹 Extraemos el nombre de la agencia
                try:
                    idx = int(partes[2])  # 🔹 Convertimos el índice a número
                except ValueError:
                    messages.error(request, "Índice no válido.")
                    return redirect("alguna_vista")

                if categoria in data["notas"] and 0 <= idx < len(data["notas"][categoria]):
                    data["notas"][categoria].pop(idx)  # 🔹 Eliminamos la agencia por índice
                    messages.success(request, f"Agencia en '{categoria}' eliminada con éxito.")
                else:
                    messages.error(request, "Agencia no encontrada.")



            elif action == "edit":
                for agencia, notas in data["notas"].items():
                    for idx, nota in enumerate(notas):
                        nota["agencia"] = request.POST.get(f"notas[{agencia}][{idx}][agencia]", nota["agencia"]).strip()
                        nota["telefono"] = request.POST.get(f"notas[{agencia}][{idx}][telefono]", nota["telefono"]).strip()
                        nota["correo"] = request.POST.get(f"notas[{agencia}][{idx}][correo]", nota["correo"]).strip()

                        # Procesar iconos específicos de la agencia
                        for tipo in ["fon", "email"]:
                            imagen_key = f"logo_{tipo}_{agencia}_{idx}"
                            if imagen_key in request.FILES:
                                imagen = request.FILES[imagen_key]
                                ruta_imagen = os.path.join(settings.BASE_DIR, f'static/images/icon_{tipo}_{agencia}_{idx}.png')

                                with open(ruta_imagen, "wb") as imagen_file:
                                    for chunk in imagen.chunks():
                                        imagen_file.write(chunk)

                                nota[f"icon_{tipo}"] = f"images/icon_{tipo}_{agencia}_{idx}.png"

                messages.success(request, "Agencias editadas con éxito.")


            # Guardar cambios en JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud: {str(e)}")

    return render(request, "editar_atencion.html", {"notas": data["notas"]})



@login_required
def editar_acerca(request):
    json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'acerca.json')

    try:
        # Leer el archivo JSON
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        messages.error(request, f"Error al leer el archivo JSON: {str(e)}")
        return render(request, "editar_acerca.html", {"data": {}})

    if request.method == "POST":
        action = request.POST.get("action")  # Determinar la acción
        try:
            if action == "change_logo":
                # Manejar cambio de logo
                if "nuevo_logo" in request.FILES:
                    nuevo_logo = request.FILES["nuevo_logo"]

                    # Validar que el archivo subido es una imagen
                    if nuevo_logo.content_type.startswith("image/"):
                        # Definir la ruta absoluta para almacenar el logo con un nombre fijo
                        logo_folder = os.path.join(settings.BASE_DIR, "static", "images")
                        os.makedirs(logo_folder, exist_ok=True)  # Crear la carpeta si no existe

                        # Forzar el nombre del archivo
                        logo_filename = "logo_acerca.png"
                        logo_path_abs = os.path.join(logo_folder, logo_filename)

                        # Guardar el archivo físicamente
                        with open(logo_path_abs, "wb+") as destination:
                            for chunk in nuevo_logo.chunks():
                                destination.write(chunk)

                        # Guardar la ruta relativa en el JSON
                        relative_logo_path = "images/logo_acerca.png"
                        data["logo"] = relative_logo_path

                        # Guardar cambios en el archivo JSON
                        with open(json_path, "w", encoding="utf-8") as file:
                            json.dump(data, file, indent=4, ensure_ascii=False)

                        messages.success(request, "Logo actualizado con éxito.")
                    else:
                        messages.error(request, "El archivo subido no es una imagen válida.")
                else:
                    messages.error(request, "No se seleccionó ningún archivo para el logo.")



            elif action == "edit_content":
                # Editar las secciones de "contenido"
                for idx in range(len(data["contenido"])):
                    subtitulo = request.POST.get(f"subtitulo_{idx}", data["contenido"][idx]["subtitulo"]).strip()
                    descripcion = request.POST.get(f"descripcion_{idx}", data["contenido"][idx]["descripcion"]).strip()

                    if subtitulo and descripcion:
                        data["contenido"][idx]["subtitulo"] = subtitulo
                        data["contenido"][idx]["descripcion"] = descripcion
                    else:
                        messages.error(request, f"Los campos no pueden estar vacíos en la sección {idx + 1}.")

            elif action == "add_content":
                # Agregar una nueva sección a "contenido"
                subtitulo = request.POST.get("nuevo_subtitulo", "").strip()
                descripcion = request.POST.get("nueva_descripcion", "").strip()

                if subtitulo and descripcion:
                    nueva_seccion = {"subtitulo": subtitulo, "descripcion": descripcion}
                    data["contenido"].append(nueva_seccion)

                    messages.success(request, "Nueva sección agregada con éxito.")
                else:
                    messages.error(request, "Todos los campos son obligatorios para agregar una nueva sección.")

            elif action.startswith("delete_content_"):
                # Eliminar una sección de "contenido" por índice
                idx = int(action.split("_")[2])
                if 0 <= idx < len(data["contenido"]):
                    data["contenido"].pop(idx)
                    messages.success(request, f"Sección {idx + 1} eliminada con éxito.")
                else:
                    messages.error(request, "Índice no válido para eliminar la sección.")

            elif action == "edit_service":
                # Editar los servicios existentes
                for idx in range(len(data["servicios"])):
                    nombre = request.POST.get(f"nombre_servicio_{idx}", data["servicios"][idx]["nombre"]).strip()
                    descripcion = request.POST.get(f"descripcion_servicio_{idx}", data["servicios"][idx]["descripcion"]).strip()

                    if nombre and descripcion:
                        data["servicios"][idx]["nombre"] = nombre
                        data["servicios"][idx]["descripcion"] = descripcion
                    else:
                        messages.error(request, f"Los campos no pueden estar vacíos en el servicio {idx + 1}.")

            elif action == "add_service":
                # Agregar un nuevo servicio
                nombre = request.POST.get("nuevo_nombre_servicio", "").strip()
                descripcion = request.POST.get("nueva_descripcion_servicio", "").strip()

                if nombre and descripcion:
                    nuevo_servicio = {"nombre": nombre, "descripcion": descripcion}
                    data["servicios"].append(nuevo_servicio)

                    messages.success(request, "Nuevo servicio agregado con éxito.")
                else:
                    messages.error(request, "Todos los campos son obligatorios para agregar un nuevo servicio.")

            elif action.startswith("delete_service_"):
                # Eliminar un servicio por índice
                idx = int(action.split("_")[2])
                if 0 <= idx < len(data["servicios"]):
                    data["servicios"].pop(idx)
                    messages.success(request, f"Servicio {idx + 1} eliminado con éxito.")
                else:
                    messages.error(request, "Índice no válido para eliminar el servicio.")

            # Guardar cambios en el archivo JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar la solicitud: {str(e)}")

        return render(request, "editar_acerca.html", {"data": data})

    return render(request, "editar_acerca.html", {"data": data})

