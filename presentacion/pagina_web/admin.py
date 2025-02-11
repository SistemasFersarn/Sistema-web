from django.contrib import admin

from pagina_web.models import *
admin.site.register (Marca)
admin.site.register (Agencia)
admin.site.register (Sucursal)
admin.site.register (Departamento)
admin.site.register (Directorio)
admin.site.register (AutosNuevos)

""" APARTADO PARA PODER CAMBIAR LA INFORMACION DE LA PAGINA """
from .models import InfoCard, Brand, InterestCard
admin.site.register(InfoCard)
admin.site.register(Brand)
admin.site.register(InterestCard)