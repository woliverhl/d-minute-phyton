# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Usuario(models.Model):
    user = models.OneToOneField(User)
    #imagen_usuario = models.ImageField("imagen",upload_to = 'productos/',)

class Proyecto(models.Model):
    nombre_proyecto = models.CharField("Nombre Proyecto", max_length=100)
    descripcion_proyecto = models.TextField("Descripción")
    fecha_inicio_proyecto = models.DateField("Fecha Inicio", null=True, blank=True)
    fecha_fin_proyecto = models.DateField("Fecha Finalización", null=True, blank=True)    
    #falta parametro ACTIVO
    def __str__(self):
        return self.nombre_proyecto

class Acta(models.Model):
    proyecto_acta = models.ForeignKey(Proyecto, verbose_name="proyecto del acta")
    fecha_acta = models.DateTimeField("Fecha")
    resumen_acta = models.TextField("Resumen del Acta")
    correlativo = int(0) 
    def __str__(self):
        return self.id

class Usuario_Acta(models.Model):
    usuario = models.ForeignKey(Usuario, verbose_name="usuarios participantes")
    acta = models.ForeignKey(Acta, verbose_name="acta")
    presente = models.BooleanField("¿Asistió?", default=False)
    secretario = models.BooleanField(default=False)


class Usuario_Proyecto(models.Model):
    ROLES = (
        ('Miembro Regular', 'Miembro Regular'),
        ('Secretario', 'Secretario'),
        ('Jefe', 'Jefe')
    )
    usuario = models.ForeignKey(Usuario, verbose_name="usuario del proyecto")
    proyecto = models.ForeignKey(Proyecto, verbose_name="usuario del proyecto")
    rol_proyecto = models.CharField("Rol en el Proyecto", choices=ROLES, max_length=30)

    def __str__(self):
        return 'Usuario: '+self.usuario.user.username+'. Proyecto: '+self.proyecto.nombre_proyecto

class Tema(models.Model):
    acta_tema = models.ForeignKey(Acta, verbose_name="acta del tema")
    titulo_tema = models.CharField(max_length=100)
    descripcion_tema = models.TextField("Descripción del Tema")
    descripcion_tema_html = models.TextField("Descripción del Tema en codigo HTML", blank=True, null=True)

    def __str__(self):
        return self.titulo_tema

class Elemento(models.Model):
    TIPOS = (
        ('AC', 'Acuerdo de Coordinación'),
        ('CI', 'Compromiso Individual'),
        ('DU', 'Duda o Busqueda'),
        ('DE', 'Desacuerdo o Brecha'),
        ('NC', 'Normas Comunes')
    )
    tipo_elemento = models.CharField("Tipo Elemento", choices=TIPOS, max_length=10)
    elemento_padre = models.ForeignKey('self',null=True, blank=True, verbose_name="elemento padre")
    usuario_responsable = models.ForeignKey(Usuario, null=True, blank=True, verbose_name="usuario responsable")
    tema = models.ForeignKey(Tema, null=True, blank=True, verbose_name="tema al que pertenece")
    fecha_inicio = models.DateField("Fecha inicio", null=True, blank=True)
    fecha_termino = models.DateField("Fecha termino", null=True, blank=True)
    estado_elemento = models.CharField("Estado", max_length=50)
    titulo_elemento = models.CharField("Titulo", max_length=100)
    descripcion_elemento = models.CharField("Descripcion", max_length=1200)
    fecha_asignado = models.DateField("Fecha asignado", default=timezone.now)

"""
class Checklist_Kanban(models.Model):
    item = models.CharField(max_length="50")

    def __str__(self):
        return self.item


class Tarea_Kanban(models.Model):
    elemento_dialogico = models.ForeignKey(Elemento, null=True)
    nombre_tarea = models.CharField(max_length=50)
    fecha_inicio_tarea = models.DateField(null=True, blank=True)
    fecha_vencimiento_tarea = models.DateField(null=True, blank=True)
    descripcion_tarea = models.CharField(max_length=600, null=True, blank=True)
    #checklist_tarea = models.ForeignKey(Checklist_Kanban, null=True, blank=True)


class Usuario_Tarea(models.Model):
    usuario = models.ForeignKey(Usuario)
    tarea = models.ForeignKey(Tarea_Kanban)
"""
