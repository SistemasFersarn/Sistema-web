# Generated by Django 5.1.2 on 2024-11-24 22:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('logo', models.ImageField(upload_to='brand_logos/')),
            ],
        ),
        migrations.CreateModel(
            name='CitaServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.CharField(choices=[('Volkswagen', 'Volkswagen'), ('Suzuki', 'Suzuki'), ('SEAT', 'SEAT')], max_length=20)),
                ('agencia', models.CharField(max_length=100)),
                ('año', models.PositiveIntegerField()),
                ('version', models.CharField(max_length=100)),
                ('kilometraje', models.PositiveIntegerField()),
                ('numero_serie', models.CharField(max_length=17)),
                ('placas', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id_departamento', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_departamento', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Directorio',
            fields=[
                ('id_directorio', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('ap_pa', models.CharField(max_length=100)),
                ('ap_ma', models.CharField(max_length=100)),
                ('contraseña', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=15)),
                ('puesto', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('id_departamento_id', models.IntegerField()),
                ('id_sucursal_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='InfoCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='info_cards/')),
            ],
        ),
        migrations.CreateModel(
            name='InterestCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='interest_cards/')),
                ('link', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id_marca', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_marca', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Agencia',
            fields=[
                ('id_agencia', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_agencia', models.CharField(max_length=40)),
                ('id_marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pagina_web.marca')),
            ],
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id_sucursal', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_sucursal', models.CharField(max_length=40)),
                ('ubicacion', models.CharField(max_length=60)),
                ('id_agencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pagina_web.agencia')),
            ],
        ),
        migrations.CreateModel(
            name='AutosNuevos',
            fields=[
                ('id_autonuevo', models.AutoField(primary_key=True, serialize=False)),
                ('modelo', models.CharField(max_length=40)),
                ('color', models.CharField(max_length=40)),
                ('num_puertas', models.IntegerField()),
                ('año', models.IntegerField()),
                ('transmision', models.CharField(choices=[('manual', 'Manual'), ('automatico', 'Automático'), ('semiautomatico', 'Semiautomático')], max_length=20)),
                ('tipo_auto', models.CharField(choices=[('Sedán', 'Sedán'), ('Coupé', 'Coupé'), ('Convertible', 'Convertible'), ('Hatchback', 'Hatchback'), ('SUV', 'SUV'), ('Pick-up', 'Pick-up'), ('Híbrido', 'Híbrido')], max_length=20)),
                ('precio_auto_MX', models.DecimalField(decimal_places=2, max_digits=12)),
                ('id_marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pagina_web.marca')),
                ('id_sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pagina_web.sucursal')),
            ],
        ),
    ]
