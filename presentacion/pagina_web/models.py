from django.db import models

# Create your models here.

class CitaServicio(models.Model):
    MARCAS = [
        ('Volkswagen', 'Volkswagen'),
        ('Suzuki', 'Suzuki'),
        ('SEAT', 'SEAT'),
    ]

    marca = models.CharField(max_length=20, choices=MARCAS)
    agencia = models.CharField(max_length=100)
    año = models.PositiveIntegerField()
    version = models.CharField(max_length=100)
    kilometraje = models.PositiveIntegerField()
    numero_serie = models.CharField(max_length=17)
    placas = models.CharField(max_length=10)

    def str(self):
        return f'{self.marca} - {self.numero_serie}'
    
    
    # Modelo para Marca
class Marca(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=40)

    def str(self):
        return self.nombre_marca


# Modelo para Agencia
class Agencia(models.Model):
    id_agencia = models.AutoField(primary_key=True)
    nombre_agencia = models.CharField(max_length=40)
    id_marca = models.ForeignKey(Marca, on_delete=models.CASCADE)

    def str(self):
        return self.id_agencia


# Modelo para Sucursal
class Sucursal(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre_sucursal = models.CharField(max_length=40)
    ubicacion = models.CharField(max_length=60)
    id_agencia = models.ForeignKey(Agencia, on_delete=models.CASCADE)

    def str(self):
        return self.nombre_sucursal


# Modelo para Departamento
class Departamento(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    nombre_departamento = models.CharField(max_length=40)

    def str(self):
        return self.nombre_departamento


# Modelo para Directorio

class Directorio(models.Model):
    id_directorio = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=100)
    ap_pa = models.CharField(max_length=100)
    ap_ma = models.CharField(max_length=100)
    contraseña = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    puesto = models.CharField(max_length=100)
    correo = models.EmailField()
    id_departamento_id = models.IntegerField()
    id_sucursal_id = models.IntegerField()

    def _str_(self):
        return self.nombre



# Modelo para Autos Nuevos
class AutosNuevos(models.Model):
    id_autonuevo = models.AutoField(primary_key=True)
    id_marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.CharField(max_length=40)
    color = models.CharField(max_length=40)
    num_puertas = models.IntegerField()
    año = models.IntegerField()
    TRANSMISION_CHOICES = [
        ('manual', 'Manual'),
        ('automatico', 'Automático'),
        ('semiautomatico', 'Semiautomático'),
    ]
    transmision = models.CharField(max_length=20, choices=TRANSMISION_CHOICES)
    TIPO_AUTO_CHOICES = [
        ('Sedán', 'Sedán'),
        ('Coupé', 'Coupé'),
        ('Convertible', 'Convertible'),
        ('Hatchback', 'Hatchback'),
        ('SUV', 'SUV'),
        ('Pick-up', 'Pick-up'),
        ('Híbrido', 'Híbrido'),
    ]
    tipo_auto = models.CharField(max_length=20, choices=TIPO_AUTO_CHOICES)
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    precio_auto_MX = models.DecimalField(max_digits=12, decimal_places=2)

    def str(self):
        return f"{self.modelo} - {self.color}"

""" APARTADO PARA PODER CAMBIAR LA INFORMACION DE LA PAGINA """

class InfoCard(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='info_cards/')

    def __str__(self):
        return self.title

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brand_logos/')

    def __str__(self):
        return self.name

class InterestCard(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='interest_cards/')
    link = models.URLField()

    def __str__(self):
        return self.title