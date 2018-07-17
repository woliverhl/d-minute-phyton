# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from models import *
from forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import datetime
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

from reuniones import ir_detalle_proyecto

import linecache
import sys, os
reload(sys)
sys.setdefaultencoding('utf8')

@login_required(login_url='/index/')
def agregar_proyecto(request):
    proyectos = Proyecto.objects.all()
    usuarios = Usuario.objects.all()
    posibles_miembros = lista_usuarios(request.user.username)
    if request.method == 'POST':
        nombre = request.POST['agregar_proyecto_nombre'].capitalize()
        descripcion = request.POST['agregar_proyecto_descripcion'].capitalize()
        miembros = request.POST.getlist('agregar_proyecto_miembros')
        fecha_inicio = datetime.datetime.strptime(request.POST['agregar_proyecto_fecha_inicio'], '%d/%m/%Y').strftime('%Y-%m-%d')
        fecha_termino = datetime.datetime.strptime(request.POST['agregar_proyecto_fecha_fin'], '%d/%m/%Y').strftime('%Y-%m-%d')

        proyecto = Proyecto(nombre_proyecto=nombre, descripcion_proyecto=descripcion, fecha_inicio_proyecto=fecha_inicio, fecha_fin_proyecto=fecha_termino).save()
        proyecto = Proyecto.objects.get(id=Proyecto.objects.latest('id').id)

        #Agregamos al usuario que agregó el proyecto (usuario logueado) como miembro
        user_jefe = Usuario.objects.get(user=User.objects.get(username=request.user.username))
        usuario_proyecto = Usuario_Proyecto(usuario=user_jefe, proyecto=proyecto, rol_proyecto="Jefe")
        usuario_proyecto.save()

        #Agregamos a los demas miembros escogidos y les enviamos correo de notificación
        for x in miembros:
            user = Usuario.objects.get(id=int(x))
            usuario_proyecto = Usuario_Proyecto(usuario=user, proyecto=proyecto, rol_proyecto="Miembro Regular")
            usuario_proyecto.save()
            correo = user.user.username

            #Solo envia correo si es direccion valida
            #if valida_correo(correo):
            #    mensaje = 'Estimado %s, Ud ha sido añadido como miembro del proyecto titulado %s. El jefe de proyecto es %s %s. Ingresa a meetingviewer.herokuapp.com para revisarlo!' %(user.user.first_name, proyecto.nombre_proyecto, user_jefe.user.first_name, user_jefe.user.last_name)
            #    send_mail('Has sido añadido a un nuevo proyecto!',mensaje, 'meeting.viewer@gmail.com',[user.user.username], fail_silently=False)
        proyectos_activos = lista_proyectos_activos(request.user.username)
        ctx = {'successAgregar': True, 'lista_usuarios':posibles_miembros, 'lista_proyectos_activos':proyectos_activos, 'proyecto_agregado':proyecto}
    else:
        ctx = {}
    return render(request, 'walo-template/index.html', ctx)



@login_required(login_url='/index/')
def editar_proyecto(request):
    ctx = {}
    if request.method == 'POST':
        id_proyecto = request.POST.get('proyecto_id')
        nombre = request.POST.get('editar_proyecto_nombre')
        print "fecha termino es: ", request.POST.get('editar_proyecto_fecha_termino')
        if request.POST.get('editar_proyecto_fecha_inicio'):
            fecha_inicio = datetime.datetime.strptime(request.POST.get('editar_proyecto_fecha_inicio'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_inicio = None
        if request.POST.get('editar_proyecto_fecha_termino'):
            fecha_termino = datetime.datetime.strptime(request.POST.get('editar_proyecto_fecha_termino'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_termino = None
        descripcion = request.POST.get('editar_proyecto_descripcion')
        miembros = request.POST.getlist('editar_proyecto_miembros')
        proyecto_editar = Proyecto.objects.get(id=id_proyecto)
        proyecto_editar.descripcion_proyecto = descripcion
        proyecto_editar.nombre_proyecto = nombre
        proyecto_editar.fecha_inicio_proyecto = fecha_inicio
        proyecto_editar.fecha_fin_proyecto = fecha_termino

        for x in miembros:
            user = Usuario.objects.get(id=int(x))
            if user not in proyecto_editar.usuario_proyecto_set.all():
                print "Usuario nuevo del proyecto:", user
                usuario_proyecto = Usuario_Proyecto(usuario=user, proyecto=proyecto_editar, rol_proyecto="Miembro Regular")
                usuario_proyecto.save()
        proyecto_editar.save()
        proyecto = Proyecto.objects.get(id=id_proyecto)
        posibles_miembros = lista_usuarios(request.user.username)
        proyectos_activos = lista_proyectos_activos(request.user.username)
        ctx['proyecto'] = proyecto
        ctx['lista_usuarios'] = posibles_miembros
        ctx['lista_proyectos_activos'] = proyectos_activos
        ctx['successEditar'] = True
    else:
        posibles_miembros = lista_usuarios(request.user.username)
        proyectos_activos = lista_proyectos_activos(request.user.username)
        ctx['lista_usuarios'] = posibles_miembros
        ctx['lista_proyectos_activos'] = proyectos_activos
    return render(request, 'walo-template/index.html',ctx)

@login_required(login_url='/index/')
def ver_proyecto(request, id_proyecto):
    ctx = {}
    proyecto = Proyecto.objects.get(id=id_proyecto)
    posibles_miembros = lista_usuarios(request.user.username)
    proyectos_activos = lista_proyectos_activos(request.user.username)
    ctx['proyecto'] = proyecto
    ctx['lista_usuarios'] = posibles_miembros
    ctx['lista_proyectos_activos'] = proyectos_activos
    return render(request, 'walo-template/index.html',ctx)

@login_required(login_url='/index/')
def agregar_acta(request, id_proyecto):
    proyecto_acta = Proyecto.objects.get(id=id_proyecto)
    if request.method == 'POST':
        #Agregamos el acta
        if request.POST.get('agregar_acta_fecha'):
            fecha_acta = datetime.datetime.strptime(request.POST.get('agregar_acta_fecha'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_acta = None
        resumen_acta = request.POST.get('agregar_acta_resumen')
        nueva_acta = Acta(proyecto_acta=proyecto_acta, fecha_acta=fecha_acta, resumen_acta=resumen_acta).save()
        acta = Acta.objects.get(id=Acta.objects.latest('id').id)

        #Por cada miembro, añadimos usuario_acta
        miembros_presentes = request.POST.getlist('agregar_acta_miembros_presentes')
        miembros_proyecto = Usuario_Proyecto.objects.filter(proyecto=proyecto_acta)
        for miembro in miembros_proyecto:
            presente = False
            secretario = False
            usuario = Usuario.objects.get(user=miembro.usuario.user)
            if str(usuario.id) in miembros_presentes:
                #Solo si estuvo presente, puede ser secretario
                presente = True
            if request.user == usuario.user: #El usuario logueado se deja como secretario del acta
                secretario = True
            usuario_acta=Usuario_Acta(usuario=usuario, acta=acta, presente=presente, secretario=secretario)
            usuario_acta.save()

        #Añadimos cada tema al acta
        cantidad_temas = request.POST.get('cantidad_total_temas')
        nombres_temas = request.POST.getlist('nombre_tema')
        descripcion_temas = request.POST.getlist('descripcion_tema')
        cantidad_elementos_tema = request.POST.getlist('cant_elementos')

        #Valores de los elementos
        nombres_elementos = request.POST.getlist('nombre_elemento_hidden')
        descripcion_elementos = request.POST.getlist('descripcion_elemento_hidden')
        responsables_elementos = request.POST.getlist('responsable_elemento_hidden')
        tipos_elementos = request.POST.getlist('tipo_elemento_hidden')
        estados_elementos = request.POST.getlist('estado_elemento_hidden')
        fechas_inicio = request.POST.getlist('fecha_inicio_hidden')
        fechas_termino = request.POST.getlist('fecha_termino_hidden')
        elementos_padre = request.POST.getlist('elemento_padre_hidden')
        elementos_padre_update = elementos_padre
        elementos_padres_creados_en_acta = []
        padres_temp = list(set(elementos_padre))
        padres_obj = []
        """
        Se agregan elementos padres que no existan, para que no den problemas después!
        """
        for j in range(len(padres_temp)):
            #Si no es digito, significa que no es id, por ende fue elemento que se agregó en la misma acta y no en una anterior
            tempStr = str(padres_temp[j])
            if tempStr.isdigit() or tempStr == '':
                pass
            else:
                temp = nombres_elementos.index(padres_temp[j])
                if tipos_elementos[temp] == 'Compromiso' and estados_elementos[temp] != "Pendiente por asignar":
                    if responsables_elementos[temp]: #Si el usuario no está vacio
                        usuario_responsable = Usuario.objects.get(user=responsables_elementos[temp])
                    else:
                        usuario_responsable = None
                else:
                    usuario_responsable = None
                #Validamos fechas
                if fechas_inicio[temp]:
                    fecha_inicio = datetime.datetime.strptime(fechas_inicio[temp], '%d/%m/%Y').strftime('%Y-%m-%d')
                else:
                    fecha_inicio = None
                if fechas_termino[temp]:
                    fecha_termino = datetime.datetime.strptime(fechas_termino[temp], '%d/%m/%Y').strftime('%Y-%m-%d')
                else:
                    fecha_termino = None
                nuevo_elemento = Elemento(tipo_elemento=tipos_elementos[temp], elemento_padre=None,
                                          usuario_responsable=usuario_responsable, tema=None, fecha_inicio=fecha_inicio,
                                          fecha_termino=fecha_termino, estado_elemento=estados_elementos[j],
                                          titulo_elemento=nombres_elementos[temp], descripcion_elemento=descripcion_elementos[temp])
                nuevo_elemento.save()
                """
                Reemplazamos el nombre del elemento padre por el id
                """
                for i in range(len(elementos_padre)):
                    if nuevo_elemento.titulo_elemento == elementos_padre[i]:
                        elementos_padre_update[i] = nuevo_elemento.id
                elementos_padres_creados_en_acta.append(nuevo_elemento.titulo_elemento)
                padres_obj.append(nuevo_elemento)
        #Ya se guardaron todos los elementos que no existían previamente y que son padre de algún otro!!
        for i in range(int(cantidad_temas)):
            titulo_tema = nombres_temas[i]
            descripcion_tema = descripcion_temas[i]
            nuevo_tema = Tema(acta_tema=acta, titulo_tema=titulo_tema, descripcion_tema=descripcion_tema)
            nuevo_tema.save()

            #Añadimos cada elemento del tema
            tema = Tema.objects.get(id=Tema.objects.latest('id').id)
            cant_elementos_tema_temp = cantidad_elementos_tema[i]
            for j in range(int(cant_elementos_tema_temp)):
                id_elemento_padre = str(elementos_padre_update[j])
                if id_elemento_padre.isdigit():
                    elemento_padre = Elemento.objects.get(id=int(id_elemento_padre))
                else:
                    elemento_padre = None
                """
                Sí elemento está en esta lista, significa que es elemento padre que se creó recién!, por lo cual solo hay que actualizarlo con el tema y el padre, no crearlo de cero
                """
                if nombres_elementos[j] in elementos_padres_creados_en_acta:
                    for k in range(len(padres_obj)):
                        if nombres_elementos[j] == padres_obj[k].titulo_elemento:
                            padres_obj[k].elemento_padre = elemento_padre
                            padres_obj[k].tema = tema
                            padres_obj[k].save()
                else:
                    tipo_elemento = tipos_elementos[j]
                    titulo_elemento = nombres_elementos[j]
                    estado_elemento = estados_elementos[j]
                    if tipo_elemento == 'Compromiso' and estado_elemento != "Pendiente por asignar":
                        if responsables_elementos[j]: #Si el usuario no está vacio
                            usuario_responsable = Usuario.objects.get(user=responsables_elementos[j])
                        else:
                            usuario_responsable = None
                    else:
                        usuario_responsable = None
                    #Validamos fechas
                    if fechas_inicio[j]:
                        fecha_inicio = datetime.datetime.strptime(fechas_inicio[j], '%d/%m/%Y').strftime('%Y-%m-%d')
                    else:
                        fecha_inicio = None
                    if fechas_termino[j]:
                        fecha_termino = datetime.datetime.strptime(fechas_termino[j], '%d/%m/%Y').strftime('%Y-%m-%d')
                    else:
                        fecha_termino = None
                    nuevo_elemento = Elemento(tipo_elemento=tipo_elemento, elemento_padre=elemento_padre,
                                              usuario_responsable=usuario_responsable, tema=tema, fecha_inicio=fecha_inicio,
                                              fecha_termino=fecha_termino, estado_elemento=estado_elemento,
                                              titulo_elemento=titulo_elemento, descripcion_elemento=descripcion_elementos[j])
                    nuevo_elemento.save()
            #Tenemos que sacar de la lista los elementos que ya fueron ingresados, por la forma en la que se leen es la unica forma en que se agreguen correctamente
            for x in range(int(cant_elementos_tema_temp)):
                nombres_elementos.pop(0)
                descripcion_elementos.pop(0)
                responsables_elementos.pop(0)
                tipos_elementos.pop(0)
                estados_elementos.pop(0)
                elementos_padre_update.pop(0)
                fechas_inicio.pop(0)
                fechas_termino.pop(0)
        return ir_panel_proyecto(request, id_proyecto, "agregar", True)
    else:
        return ir_panel_proyecto(request, id_proyecto, None, None)

def agregar_usuario(request):
    ctx = {}
    if request.method == 'POST':
        #Se modificó para que se ingrese el mail como username
        username = request.POST['agregar_usuario_username']
        nombres = request.POST['agregar_usuario_nombres'].title()
        apellidos = request.POST['agregar_usuario_apellidos'].title()
        password = request.POST['agregar_usuario_password']
        usuario_nuevo = User(username=username, first_name=nombres, last_name=apellidos,
                             email=username, password=password)
        #Para encriptar la clave
        usuario_nuevo.set_password(password)
        usuario_nuevo.save()
        Usuario(user=usuario_nuevo).save()

        #Logueamos al usuario y lo redigirigmos al index
        ctx['successAgregarUsuario'] = True
        ctx['username'] = username
        ctx['password'] = password
    return render(request, 'walo-template/agregar_usuario.html', ctx)


def index_view(request):
    ctx={}
    #Validamos que usuario no esté logueado
    if request.user.is_authenticated():
        posibles_miembros = lista_usuarios(request.user.username)
        proyectos_activos = lista_proyectos_activos(request.user.username)
        ctx = {'lista_usuarios':posibles_miembros, 'lista_proyectos_activos':proyectos_activos}
        return render(request, 'walo-template/index.html', ctx)
    else:
        if request.method == 'POST':
            accion = request.POST['accion']
            if accion == 'agregar_usuario':
                username = request.POST['agregar_usuario_username']
                nombres = request.POST['agregar_usuario_nombres'].title()
                apellidos = request.POST['agregar_usuario_apellidos'].title()
                email = request.POST['agregar_usuario_email']
                password = request.POST['agregar_usuario_password']
                usuario_nuevo = User(username=username, first_name=nombres, last_name=apellidos,
                                     email=email, password=password)
                #Para encriptar la clave
                usuario_nuevo.set_password(password)
                usuario_nuevo.save()
                Usuario(user=usuario_nuevo).save()

                #Logueamos al usuario y lo redigirigmos al index
                user = authenticate(username=username, password=password)
                login(request, user)
                posibles_miembros = lista_usuarios(request.user.username)
                proyectos_activos = lista_proyectos_activos(request.user.username)
                ctx = {'lista_usuarios':posibles_miembros, 'lista_proyectos_activos':proyectos_activos}
                return render(request, 'walo-template/index.html', ctx)
            elif accion == 'login_usuario':
                username = request.POST['login_username']
                password = request.POST['login_password']

                #Validamos si usuario existe
                if User.objects.filter(username=username):
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        login(request, user)
                        posibles_miembros = lista_usuarios(request.user.username)
                        proyectos_activos = lista_proyectos_activos(request.user.username)
                        ctx['lista_usuarios'] = posibles_miembros
                        ctx['lista_proyectos_activos'] = proyectos_activos
                        return render(request, 'walo-template/index.html', ctx)
                    else:
                        ctx['errorPassword'] = True
                else:
                    #Usuario no existe o ingreso datos incorrectos
                    ctx['errorUsuarioNoExiste'] = True
                    return render(request, 'walo-template/login.html', ctx)
            else:
                pass
        #cualquier otra accion lleva al login
        return render(request, 'walo-template/login.html', ctx)

@login_required(login_url='/index/')
def ver_calendario_actas(request, id_proyecto):
    ctx = {}
    proyecto = Proyecto.objects.get(id=id_proyecto)
    actas_proyecto = Acta.objects.filter(proyecto_acta=proyecto)
    usuarios_proyecto = Usuario_Proyecto.objects.filter(proyecto=proyecto)
    #Validamos si el usuario es jefe. Si lo es, se le permite editar cualquier acta.
    es_jefe = usuario_logueado_es_jefe(request.user, usuarios_proyecto)
    return render(request, 'walo-template/proyectos/calendario_actas.html', ctx)

@login_required(login_url='/index/')
def editar_acta(request, id_proyecto):
    es_jefe = False
    #Hacer lo de los permisos para que en el back end validar que pueda editar
    if request.method == 'POST':

        #validamos que pueda realmente pueda editar el acta


        proyecto = Proyecto.objects.get(id=id_proyecto)
        id_acta = request.POST.get('id_reunion_editar')
        permitir_editar = True
        acta = Acta.objects.get(id=id_acta)
        #Editamos el acta
        fecha_acta = datetime.datetime.strptime(request.POST.get('editar_acta_fecha'), '%d/%m/%Y').strftime('%Y-%m-%d')
        resumen_acta = request.POST.get('editar_acta_resumen')
        acta.resumen_acta = resumen_acta
        acta.fecha_acta = fecha_acta
        acta.save()



        #Por cada miembro, añadimos usuario_acta
        miembros_presentes = request.POST.getlist('editar_acta_miembros_presentes')
        miembros_proyecto = Usuario_Proyecto.objects.filter(proyecto=proyecto)
        secretario_proyecto = request.POST.get('editar_acta_secretario')
        for miembro in miembros_proyecto:
            presente = False
            usuario = Usuario.objects.get(user=miembro.usuario.user)
            if str(usuario.id) in miembros_presentes:
                #Solo si estuvo presente, puede ser secretario
                presente = True
            usuario_acta=Usuario_Acta.objects.get(usuario=usuario, acta=acta)
            usuario_acta.presente = presente
            usuario_acta.save()



        #Añadimos cada tema al acta
        cantidad_temas = request.POST.get('editar_reunion_cantidad_total_temas')
        nombres_temas = request.POST.getlist('nombre_tema')
        descripcion_temas = request.POST.getlist('descripcion_tema')
        cantidad_elementos_tema = request.POST.getlist('cant_elementos')
        temas_id = request.POST.getlist('id_tema')
        temas_eliminados_id = request.POST.getlist('id_tema_eliminado')

        #Valores de los elementos
        nombres_elementos = request.POST.getlist('nombre_elemento_hidden')
        descripcion_elementos = request.POST.getlist('descripcion_elemento_hidden')
        responsables_elementos = request.POST.getlist('responsable_elemento_hidden')
        tipos_elementos = request.POST.getlist('tipo_elemento_hidden')
        estados_elementos = request.POST.getlist('estado_elemento_hidden')
        fechas_inicio = request.POST.getlist('fecha_inicio_hidden')
        fechas_termino = request.POST.getlist('fecha_termino_hidden')
        elementos_padre = request.POST.getlist('elemento_padre_hidden')
        elementos_id = request.POST.getlist('elemento_id_hidden')
        elementos_eliminados_id = request.POST.getlist('id_elemento_eliminado')
        elementos_padre_update = elementos_padre
        elementos_padres_creados_en_acta = []
        padres_temp = list(set(elementos_padre))
        padres_obj = []

        #Se agregan elementos padres que no existan, para que no den problemas después!
        for j in range(len(padres_temp)):
            #Si no es digito, significa que no es id, por ende fue elemento que se agregó en la misma acta y no en una anterior
            tempStr = str(padres_temp[j])
            if tempStr.isdigit() or tempStr == '':
                pass
            else:
                temp = nombres_elementos.index(padres_temp[j])
                if tipos_elementos[temp] == 'Compromiso' and estados_elementos[temp] != "Pendiente por asignar":
                    if responsables_elementos[temp]: #Si el usuario no está vacio
                        usuario_responsable = Usuario.objects.get(user=responsables_elementos[temp])
                    else:
                        usuario_responsable = None
                else:
                    usuario_responsable = None
                #Validamos fechas
                if fechas_inicio[temp]:
                    fecha_inicio = datetime.datetime.strptime(fechas_inicio[temp], '%d/%m/%Y').strftime('%Y-%m-%d')
                else:
                    fecha_inicio = None
                if fechas_termino[temp]:
                    fecha_termino = datetime.datetime.strptime(fechas_termino[temp], '%d/%m/%Y').strftime('%Y-%m-%d')
                else:
                    fecha_termino = None
                nuevo_elemento = Elemento(tipo_elemento=tipos_elementos[temp], elemento_padre=None,
                                          usuario_responsable=usuario_responsable, tema=None, fecha_inicio=fecha_inicio,
                                          fecha_termino=fecha_termino, estado_elemento=estados_elementos[j],
                                          titulo_elemento=nombres_elementos[temp], descripcion_elemento=descripcion_elementos[temp])
                nuevo_elemento.save()
                """
                Reemplazamos el nombre del elemento padre por el id
                """
                for i in range(len(elementos_padre)):
                    if nuevo_elemento.titulo_elemento == elementos_padre[i]:
                        elementos_padre_update[i] = nuevo_elemento.id
                elementos_padres_creados_en_acta.append(nuevo_elemento.titulo_elemento)
                padres_obj.append(nuevo_elemento)
        #Ya se guardaron todos los elementos que no existían previamente y que son padre de algún otro!!

        #Eliminamos todas las relaciones de padre de los elementos a eliminar
        for act in proyecto.acta_set.all():
            for tema in act.tema_set.all():
                for element in tema.elemento_set.all():
                    if element.elemento_padre:
                        if str(element.elemento_padre.id) in str(elementos_eliminados_id): #Si el elemento padre está en elementos_eliminados_id, significa que el elemento a eliminar es padre
                            element.elemento_padre = None
                            element.save()

        #Eliminamos los elementos
        for i in range(len(elementos_eliminados_id)):
            elemento_eliminar = Elemento.objects.get(id=elementos_eliminados_id[i])
            elemento_eliminar.delete()

        #Eliminamos todos los temas que fueron eliminados
        for i in range(len(temas_eliminados_id)):
            print "eliminando tema id: ", temas_eliminados_id[i]
            if temas_eliminados_id[i]: #Si id no está vacío, se elimina
                tema_eliminar = Tema.objects.get(id=int(temas_eliminados_id[i]))
                tema_eliminar.delete()

        #Editamos el resto de los temas/elementos, y agregamos los temas/elementos nuevos
        for i in range(int(cantidad_temas)):
            if temas_id[i]: #Si el tema id existe, es porque el tema ya existía
                tema = Tema.objects.get(id=temas_id[i])
                tema.titulo_tema = nombres_temas[i]
                tema.descripcion_tema = descripcion_temas[i]
                tema.save()
            else: #Si tema_id está vacío, significa que el tema es nuevo, por lo que se agrega
                titulo_tema = nombres_temas[i]
                descripcion_tema = descripcion_temas[i]
                nuevo_tema = Tema(acta_tema=acta, titulo_tema=titulo_tema, descripcion_tema=descripcion_tema)
                nuevo_tema.save()
                tema = Tema.objects.get(id=Tema.objects.latest('id').id)
            cant_elementos_tema_temp = cantidad_elementos_tema[i]
            for j in range(int(cant_elementos_tema_temp)):
                id_elemento_padre = str(elementos_padre_update[j])
                if id_elemento_padre.isdigit():
                    try:
                        elemento_padre = Elemento.objects.get(id=int(id_elemento_padre))
                    except:
                        elemento_padre = None
                else:
                    elemento_padre = None
                """
                Si elemento está en esta lista, significa que es elemento padre que se creó recién!, por lo cual solo hay que actualizarlo con el tema y el padre, no crearlo de cero
                """
                if nombres_elementos[j] in elementos_padres_creados_en_acta:
                    for k in range(len(padres_obj)):
                        if nombres_elementos[j] == padres_obj[k].titulo_elemento:
                            padres_obj[k].elemento_padre = elemento_padre
                            padres_obj[k].tema = tema
                            padres_obj[k].save()
                else:
                    tipo_elemento = tipos_elementos[j]
                    titulo_elemento = nombres_elementos[j]
                    estado_elemento = estados_elementos[j]
                    descripcion_elemento = descripcion_elementos[j]
                    if tipo_elemento == 'Compromiso' and estado_elemento != "Pendiente por asignar":
                        if responsables_elementos[j]: #Si el usuario no está vacio
                            usuario_responsable = Usuario.objects.get(user=responsables_elementos[j])
                        else:
                            usuario_responsable = None
                    else:
                        usuario_responsable = None
                    #Validamos fechas
                    if fechas_inicio[j]:
                        fecha_inicio = datetime.datetime.strptime(fechas_inicio[j], '%d/%m/%Y').strftime('%Y-%m-%d')
                    else:
                        fecha_inicio = None
                    if fechas_termino[j]:
                        fecha_termino = datetime.datetime.strptime(fechas_termino[j], '%d/%m/%Y').strftime('%Y-%m-%d')
                    else:
                        fecha_termino = None

                    if elementos_id[j]: #Si elemento_id existe, es porque el elemento ya existía
                        editar_elemento = Elemento.objects.get(id=elementos_id[j])
                        editar_elemento.tipo_elemento = tipo_elemento
                        editar_elemento.elemento_padre=elemento_padre
                        editar_elemento.usuario_responsable = usuario_responsable
                        editar_elemento.fecha_inicio = fecha_inicio
                        editar_elemento.fecha_termino = fecha_termino
                        editar_elemento.estado_elemento = estado_elemento
                        editar_elemento.titulo_elemento = titulo_elemento
                        editar_elemento.descripcion_elemento = descripcion_elemento
                        #No se agrega el tema puesto que no puede cambiarse
                    else:
                        editar_elemento = Elemento(tipo_elemento=tipo_elemento, elemento_padre=elemento_padre,
                                              usuario_responsable=usuario_responsable, tema=tema, fecha_inicio=fecha_inicio,
                                              fecha_termino=fecha_termino, estado_elemento=estado_elemento,
                                              titulo_elemento=titulo_elemento, descripcion_elemento=descripcion_elemento)
                    editar_elemento.save()
            #Tenemos que sacar de la lista los elementos que ya fueron ingresados, por la forma en la que se leen es la unica forma en que se agreguen correctamente
            for x in range(int(cant_elementos_tema_temp)):
                nombres_elementos.pop(0)
                descripcion_elementos.pop(0)
                responsables_elementos.pop(0)
                tipos_elementos.pop(0)
                estados_elementos.pop(0)
                elementos_padre_update.pop(0)
                fechas_inicio.pop(0)
                fechas_termino.pop(0)
                elementos_id.pop(0)
        return ir_panel_proyecto(request, id_proyecto, "editar", True)
    else:
        return ir_panel_proyecto(request, id_proyecto, "editar", False)

@login_required(login_url='/index/')
def eliminar_acta(request, id_proyecto):
    if request.method == 'POST':
        try:
            id_acta = request.POST.get('paginacion_activa')
            acta = Acta.objects.get(id=id_acta)
            acta.delete()
            return ir_panel_proyecto(request, id_proyecto, "eliminar", True)
        except Exception,e:
            print e
    return ir_panel_proyecto(request, id_proyecto, "eliminar", False)

@login_required(login_url='/index/')
def eliminar_proyecto(request):
    ctx = {}
    if request.method == 'POST':
        try:
            id_proyecto = request.POST.get('id_proyecto_eliminar')
            proyecto = Proyecto.objects.get(id=id_proyecto)
            proyecto.delete()
            ctx['lista_proyectos_activos'] = lista_proyectos_activos(request.user.username)
            ctx['lista_usuarios'] = lista_usuarios(request.user.username)
            ctx['successEliminarProyecto'] = True
            return render(request, 'walo-template/index.html', ctx)
        except Exception,e:
            print e
    ctx['lista_proyectos_activos'] = lista_proyectos_activos(request.user.username)
    ctx['lista_usuarios'] = lista_usuarios(request.user.username)
    return render(request, 'walo-template/index.html', ctx)

@login_required(login_url='/index/')
@csrf_exempt
def agregar_tarjeta(request, id_proyecto):
    ctx = {}
    try:
        nombre_tarea = request.POST.get('nombre_tarea')
        if request.POST.get('fecha_inicio'):
            fecha_inicio_tarea = datetime.datetime.strptime(request.POST.get('fecha_inicio'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_inicio_tarea = None
        if request.POST.get('fecha_termino'):
            fecha_vencimiento_tarea = datetime.datetime.strptime(request.POST.get('fecha_termino'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_vencimiento_tarea = None
        descripcion_tarea = request.POST.get('descripcion_tarea')
        if request.POST.get('elemento_padre'):
            elemento_padre = Elemento.objects.get(id=request.POST.get('elemento_padre'))
        else:
            elemento_padre = None
        estado_tarea = request.POST.get('estado_tarea')
        tema_tarea = Tema.objects.get(id=request.POST.get('tema_tarea'))
        if request.POST.get('usuario_responsable'):
            usuario_responsable = Usuario.objects.get(user=request.POST.get('usuario_responsable'))
        else:
            usuario_responsable = None
        nueva_tarea = Elemento(tipo_elemento='Compromiso', elemento_padre=elemento_padre,
                                  usuario_responsable=usuario_responsable, tema=tema_tarea, fecha_inicio=fecha_inicio_tarea,
                                  fecha_termino=fecha_vencimiento_tarea, estado_elemento=estado_tarea,
                                  titulo_elemento=nombre_tarea, descripcion_elemento=descripcion_tarea)
        nueva_tarea.save()

        tarea = Elemento.objects.get(id=Elemento.objects.latest('id').id)
        ctx['success'] = True
        ctx['id_tarea'] = tarea.id
        ctx['nombre_tarea'] = tarea.titulo_elemento if nombre_tarea else ""
        ctx['descripcion_tarea'] = tarea.descripcion_elemento if descripcion_tarea else ""
        ctx['fecha_inicio'] = datetime.datetime.strptime(str(tarea.fecha_inicio), '%Y-%m-%d').strftime('%d/%m/%Y') if fecha_inicio_tarea else ""
        ctx['fecha_termino'] = datetime.datetime.strptime(str(tarea.fecha_termino), '%Y-%m-%d').strftime('%d/%m/%y') if fecha_vencimiento_tarea else ""
        ctx['usuario_responsable_id'] = tarea.usuario_responsable.id if tarea.usuario_responsable else ""
        ctx['usuario_responsable_nombre'] = tarea.usuario_responsable.user.first_name+" "+tarea.usuario_responsable.user.last_name if tarea.usuario_responsable else ""
        ctx['elemento_padre_id'] = tarea.elemento_padre.id if tarea.elemento_padre else ""
        ctx['elemento_padre_titulo'] = tarea.elemento_padre.titulo_elemento if tarea.elemento_padre else ""
        ctx['tema_id'] = tarea.tema_id
        ctx['acta_id'] = tarea.tema.acta_tema_id
        return JsonResponse(ctx)
    except Exception as e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    return ir_panel_proyecto(request, id_proyecto, "agregar_tarjeta", False)

@login_required(login_url='/index/')
@csrf_exempt
def cambiar_estado_tarjeta(request, id_proyecto):
    ctx = {}
    try:
        id_tarea = request.POST.get('id_tarea')
        estado_tarea = request.POST.get('estado_tarea')
        tarea = Elemento.objects.get(id=id_tarea)
        tarea.estado_elemento = estado_tarea
        if estado_tarea == "Pendiente por asignar":
            tarea.usuario_responsable = None
        tarea.save()
        ctx['success'] = True
        return JsonResponse(ctx)
    except Exception,e:
        print e
    return ir_panel_proyecto(request, id_proyecto, "error", False)

@login_required(login_url='/index/')
@csrf_exempt
def escoger_responsable_tarjeta(request, id_proyecto):
    ctx = {}
    try:
        id_tarea = request.POST.get('id_tarea')
        estado_tarea = request.POST.get('estado_tarea')
        if request.POST.get('fecha_inicio_tarea'):
            fecha_inicio_tarea = datetime.datetime.strptime(request.POST.get('fecha_inicio_tarea'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_inicio_tarea = None
        if request.POST.get('fecha_termino_tarea'):
            fecha_termino_tarea = datetime.datetime.strptime(request.POST.get('fecha_termino_tarea'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_termino_tarea = None
        usuario_responsable = Usuario.objects.get(id=request.POST.get('usuario_responsable'))
        tarea = Elemento.objects.get(id=id_tarea)
        tarea.estado_elemento = estado_tarea
        tarea.usuario_responsable = usuario_responsable
        tarea.fecha_inicio = fecha_inicio_tarea
        tarea.fecha_termino = fecha_termino_tarea
        tarea.save()
        ctx['success'] = True
        return JsonResponse(ctx)
    except Exception,e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

@login_required(login_url='/index/')
@csrf_exempt
def eliminar_tarea(request, id_proyecto):
    ctx = {}
    try:
        id_tarea = request.POST.get('id_tarea')
        tarea = Elemento.objects.get(id=id_tarea)
        tareas = Elemento.objects.filter(elemento_padre=tarea)

        #Seteamos null todos los elementos  que tienen como padre el elemento eliminar
        #Esto puede setearse con on_delete=models.SET_NULL, pero modificaciones del modelo cuestan mucho en heroku
        for tarea_temp in tareas:
            tarea_temp.elemento_padre = None
            tarea_temp.save()
        tarea.delete()
        ctx['success'] = True
        return JsonResponse(ctx)
    except Exception,e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

@login_required(login_url='/index/')
def ver_kanban(request, id_proyecto):
    ctx = {}
    actas_con_tema = []
    proyecto = Proyecto.objects.get(id=id_proyecto)
    actas = Acta.objects.filter(proyecto_acta=proyecto)

    for acta in actas:
        if len(acta.tema_set.all())>0: #Si el acta tiene temas, se agrega a la lista
            actas_con_tema.append(acta)
    #Compromisos que no tienen temas (es decir, fueron agregados directamente al tablero kanban)
    tareas = Elemento.objects.filter(tipo_elemento='Compromiso')
    ctx['proyecto'] = proyecto
    ctx['tareas'] = tareas
    ctx['actas_con_tema'] = actas_con_tema
    return render(request, 'walo-template/proyectos/kanban.html', ctx)

@login_required(login_url='/index/')
def ver_sintesis_dialogica(request, id_proyecto):
    ctx = {}
    proyecto = Proyecto.objects.get(id=id_proyecto)
    usuarios_proyecto = Usuario_Proyecto.objects.filter(proyecto=proyecto)
    actas = Acta.objects.filter(proyecto_acta=proyecto)
    ctx['proyecto'] = proyecto
    ctx['usuarios_proyecto'] = usuarios_proyecto
    return render(request, 'walo-template/proyectos/sintesis_dialogica.html', ctx)

@login_required(login_url='/index/')
@csrf_exempt
def filtrar_elementos(request, id_proyecto):
    ctx = {}
    try:
        nombre_elemento = request.POST.get('nombre_elemento')
        if request.POST.get('fecha_inicio'):
            fecha_inicio = datetime.datetime.strptime(request.POST.get('fecha_inicio'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_inicio = None
        if request.POST.get('fecha_termino'):
            fecha_termino = datetime.datetime.strptime(request.POST.get('fecha_termino'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_termino = None

        usuario_responsable = request.POST.getlist('usuarios_responsables[]')
        if request.POST.get('texto_en_discusion'):
            lista_palabras_discusion = request.POST.get('texto_en_discusion').split()
        else:
            lista_palabras_discusion = []
        elementos_encontrados = []
        #Recorremos todos los elementos de las actas
        proyecto = Proyecto.objects.get(id=id_proyecto)
        actas = Acta.objects.filter(proyecto_acta=proyecto)

        #Se obtienen todos los elementos de la lista y se almacenan en elementos_encontrados. Si alguno de los filtros no calzan, se elimina de la lista

        for acta in actas:
            for tema in acta.tema_set.all():
                for elemento in tema.elemento_set.all():

                    #Si todos los filtros en filtros_aplicados se cumplen, se mantiene el elemento en la lista, pues cumple con los filtros
                    #Si hay al menos un False, significa que no cumple, por lo que se saca de la lista
                    filtros_aplicados = [False] * 5 #Arreglo con 5 falses

                    if nombre_elemento == "" or nombre_elemento.lower() in elemento.titulo_elemento.lower():
                        filtros_aplicados[0] = True
                    #Se puede cambiar any por all para que calcen todas las palabras y no solo una
                    #if not any(palabra in elemento.descripcion_elemento for palabra in lista_palabras_discusion) and not any(palabra in tema.descripcion_tema for palabra in lista_palabras_discusion):
                    if lista_palabras_discusion == [] or any(palabra.lower() in tema.descripcion_tema.lower() for palabra in lista_palabras_discusion):
                        filtros_aplicados[1] = True
                    if fecha_inicio == None or str(fecha_inicio) == str(elemento.fecha_inicio):
                        filtros_aplicados[2] = True
                    if fecha_termino == None or str(fecha_termino) == str(elemento.fecha_termino):
                        filtros_aplicados[3] = True
                    if not usuario_responsable or (elemento.tipo_elemento == "Compromiso" and str(elemento.usuario_responsable.id) in usuario_responsable): #Si se filtra por usuario repsonsable, se borran todos los elementos que no sean comrpomisos pues no tienen usuarios responsables
                        filtros_aplicados[4] = True
                    if not False in filtros_aplicados:
                        elementos_encontrados.append(elemento.id)
        ctx['elementos_filtrados'] = elementos_encontrados
        print ctx
        return JsonResponse(ctx)
    except Exception as e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

@login_required(login_url='/index/')
def ver_panel_proyecto(request, id_proyecto, id_acta = None):
    return ir_detalle_proyecto(request, id_proyecto, id_acta)
    #return ir_panel_proyecto(request, id_proyecto, "ninguna", None)

@login_required(login_url='/index/')
@csrf_exempt
def editar_tarjeta(request, id_proyecto):
    ctx = {}
    try:
        nombre_tarea = request.POST.get('nombre_tarea')
        if request.POST.get('fecha_inicio'):
            fecha_inicio_tarea = datetime.datetime.strptime(request.POST.get('fecha_inicio'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_inicio_tarea = None
        if request.POST.get('fecha_termino'):
            fecha_vencimiento_tarea = datetime.datetime.strptime(request.POST.get('fecha_termino'), '%d/%m/%Y').strftime('%Y-%m-%d')
        else:
            fecha_vencimiento_tarea = None
        descripcion_tarea = request.POST.get('descripcion_tarea')
        if request.POST.get('elemento_padre'):
            elemento_padre = Elemento.objects.get(id=request.POST.get('elemento_padre'))
        else:
            elemento_padre = None
        estado_tarea = request.POST.get('estado_tarea')
        tema_tarea = Tema.objects.get(id=request.POST.get('tema_tarea'))
        if request.POST.get('usuario_responsable'):
            usuario_responsable = Usuario.objects.get(user=request.POST.get('usuario_responsable'))
        else:
            usuario_responsable = None

        id_tarea = request.POST.get('id_tarea_editada')

        tarea_editada = Elemento.objects.get(id=id_tarea)
        tarea_editada.usuario_responsable = usuario_responsable
        tarea_editada.tema = tema_tarea
        tarea_editada.fecha_inicio = fecha_inicio_tarea
        tarea_editada.fecha_termino = fecha_vencimiento_tarea
        tarea_editada.titulo_elemento = nombre_tarea
        tarea_editada.descripcion_elemento = descripcion_tarea
        tarea_editada.save()

        tarea = tarea_editada
        ctx['success'] = True
        ctx['id_tarea'] = tarea.id
        ctx['nombre_tarea'] = tarea.titulo_elemento if nombre_tarea else ""
        ctx['descripcion_tarea'] = tarea.descripcion_elemento if descripcion_tarea else ""
        ctx['fecha_inicio'] = datetime.datetime.strptime(str(tarea.fecha_inicio), '%Y-%m-%d').strftime('%d/%m/%Y') if fecha_inicio_tarea else ""
        ctx['fecha_termino'] = datetime.datetime.strptime(str(tarea.fecha_termino), '%Y-%m-%d').strftime('%d/%m/%Y') if fecha_vencimiento_tarea else ""
        ctx['usuario_responsable_id'] = tarea.usuario_responsable.id if tarea.usuario_responsable else ""
        ctx['usuario_responsable_nombre'] = tarea.usuario_responsable.user.first_name+" "+tarea.usuario_responsable.user.last_name if tarea.usuario_responsable else ""
        ctx['elemento_padre_id'] = tarea.elemento_padre.id if tarea.elemento_padre else ""
        ctx['elemento_padre_titulo'] = tarea.elemento_padre.titulo_elemento if tarea.elemento_padre else ""
        ctx['tema_id'] = tarea.tema_id
        ctx['acta_id'] = tarea.tema.acta_tema_id
        return JsonResponse(ctx)
    except Exception as e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        ctx['success'] = False
        return JsonResponse(ctx)
"""
Funciones varias
"""

@csrf_exempt
def cerrar_sesion(request):
    logout(request)
    return render(request, 'walo-template/login.html')

def lista_usuarios(usuario_logueado):
    return Usuario.objects.all().exclude(user=User.objects.get(username=usuario_logueado))

def lista_proyectos_activos(usuario_logueado):
    user = User.objects.get(username=usuario_logueado)
    usuario = Usuario.objects.get(user=user)
    #FALTA VALIDAR QUE EL PROYECTO ESTE ACTIVO
    usuario_proyectos = Usuario_Proyecto.objects.filter(usuario=usuario)
    return usuario_proyectos

def usuario_logueado_es_jefe(usuario_logueado, usuarios_proyecto):
    for usuario_proyecto in usuarios_proyecto:
        if usuario_proyecto.usuario.user == usuario_logueado: #se tiene que verificar solo para el usuario logueado
            if usuario_proyecto.rol_proyecto == "Jefe":
                return True
    return False


def ir_panel_proyecto(request, id_proyecto, accion, estado_accion):
    ctx = {}
    #Variables para el panel
    proyecto = Proyecto.objects.get(id=id_proyecto)
    actas = Acta.objects.filter(proyecto_acta=Proyecto.objects.get(id=id_proyecto)).order_by('fecha_acta')
    usuarios_proyecto = Usuario_Proyecto.objects.filter(proyecto=proyecto)
    ctx['cantidad_actas_proyecto'] = len(actas)+1 #Esto es para la numeración de los elementos. Para ello, se le suma 1 adicional, pues la siguiente acta deberá ser la cant_actas+1.
    ctx['proyecto'] = proyecto
    ctx['usuarios_proyecto'] = usuarios_proyecto
    ctx['actas'] = actas

    #Capturamos todos los compromisos activos (no eliminados)
    elementos_activos = []
    numeraciones = []
    num_acta = 0
    num_elemento = 0
    for acta in actas:
        fecha_acta = acta.fecha_acta
        num_acta = num_acta+1
        for tema in acta.tema_set.all():
            for elemento in tema.elemento_set.all():
                num_elemento = num_elemento + 1
                if elemento.tipo_elemento == "Compromiso":
                        if elemento.estado_elemento != "Eliminado" and elemento.estado_elemento != "Completado":
                            #Si elemento no tiene fecha inicio, no se considera como activo
                            numeracion = str(num_acta)+"."+str(num_elemento)
                            numeraciones.append(numeracion)
                            elementos_activos.append(elemento)
    #Ahora que tenemos los CO activos, para cada acta seleccionamso aquellos que no sean de una reunión futura
    """
    for acta in actas:
        for elemento in elementos_activos:
            if elemento.fecha_inicio is not None:
                if elemento.fecha_inicio < acta.fecha_acta:
    """

    #Esto es para poder iterar sobre las dos listas en un for
    ctx['total_compromisos_activos'] = zip(elementos_activos, numeraciones)

    #Variables para el tablero kanban
    actas_con_tema = []
    for acta in actas:
        if len(acta.tema_set.all())>0: #Si el acta tiene temas, se agrega a la lista
            actas_con_tema.append(acta)
    #Compromisos que no tienen temas (es decir, fueron agregados directamente al tablero kanban)
    tareas = Elemento.objects.filter(tipo_elemento='Compromiso')
    ctx['tareas'] = tareas
    ctx['actas_con_tema'] = actas_con_tema

    #Revisamos si usuario logueado es jefe. Si es jefe, se añaden todas las actas como editables
    es_jefe = False
    usuario_logueado = Usuario.objects.get(user=User.objects.get(username=request.user.username))
    user_proyecto_logueado = Usuario_Proyecto.objects.get(proyecto=proyecto, usuario=usuario_logueado)
    if user_proyecto_logueado.rol_proyecto == "Jefe":
        es_jefe = True
    ctx['es_jefe'] = es_jefe
    if accion == "agregar" or accion == "editar" or accion == "eliminar" or accion == "editar_tarjeta":
        if accion == "eliminar":
            print "accion es eliminar"
            success_accion = "successEliminar"
        elif accion == "agregar":
            success_accion = "successAgregarActa"
        elif accion == "editar":
            success_accion = "successEditarActa"
        else:
            success_accion = "successEditarTarea"
        ctx[success_accion] = estado_accion
    return render(request, 'walo-template/proyectos/panel_proyecto.html', ctx)

@login_required(login_url='/index/')
@csrf_exempt
def datos_grafico(request, id_proyecto):
    ctx = []
    try:
        actas = Acta.objects.filter(proyecto_acta=Proyecto.objects.get(id=id_proyecto)).order_by('fecha_acta')
        num_reunion = 0
        num_elemento = 0
        num_tema = 0
        for acta in actas:
            num_reunion += 1
            for tema in acta.tema_set.all():
                num_tema += 1
                for elemento in tema.elemento_set.all():
                    num_elemento += 1
                    datos_elemento = {}
                    nombre_elemento = str(num_tema)+"."+str(num_elemento)
                    #nombre_elemento = numeracion
                    datos_elemento['name'] = nombre_elemento
                    tipo = ""
                    if elemento.tipo_elemento == "Compromiso":
                        tipo = "CO"
                    elif elemento.tipo_elemento == "Acuerdo":
                        tipo = "AC"
                    elif elemento.tipo_elemento == "Desacuerdo":
                        tipo = "DE"
                    elif elemento.tipo_elemento == "Duda":
                        tipo = "DU"
                    datos_elemento['nombre_mostrado'] = str(num_reunion)+"."+str(num_elemento)+" "+tipo
                    datos_elemento['imports'] = [] #padre elemento

                    #para numerar al padre
                    #Se debe recorrer de nuevo toodo porque si no, no se sabe el numero del tema para el nombre del 'import'
                    if elemento.elemento_padre is not None:
                        num_reunion_temp = 0
                        num_elem_temp = 0
                        num_tema_temp = 0
                        for act in actas:
                            num_reunion_temp += 1
                            for tem in act.tema_set.all():
                                num_tema_temp += 1
                                for elem in tem.elemento_set.all():
                                    num_elem_temp += 1
                                    if elemento.elemento_padre.id == elem.id:
                                        tipo_padre = ""
                                        if elem.tipo_elemento == "Compromiso":
                                            tipo_padre = "CO"
                                        elif elem.tipo_elemento == "Acuerdo":
                                            tipo_padre = "AC"
                                        elif elem.tipo_elemento == "Desacuerdo":
                                            tipo_padre = "DE"
                                        elif elem.tipo_elemento == "Duda":
                                            tipo_padre = "DU"
                                        nombre_elemento_padre_2 = str(num_tema_temp)+"."+str(num_elem_temp)
                        datos_elemento['imports'].append(nombre_elemento_padre_2)
                    datos_elemento['type'] = elemento.tipo_elemento #TIPO ELEMENTO
                    datos_elemento['friendly'] = {} #datos elemento
                    datos_elemento['friendly']['element'] = elemento.titulo_elemento
                    datos_elemento['friendly']['subject'] = tema.titulo_tema
                    datos_elemento['id_elemento'] = elemento.id
                    ctx.append(datos_elemento)
        return JsonResponse(ctx, safe=False)
    except Exception as e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return JsonResponse({})

@login_required(login_url='/index/')
@csrf_exempt
def obtener_compromisos_activos_por_acta(request, id_proyecto):
    ctx = {}
    try:
        if request.method == 'POST':
            id_acta = request.POST.get('id_acta')
            acta = Acta.objects.get(id=id_acta)
            actas = Acta.objects.filter(proyecto_acta=Proyecto.objects.get(id=id_proyecto)).order_by('fecha_acta')

            #Se usan listas y luego se unen para los datos de los elementos porque no se pueden pasar por JSON objetos del modelo de datos
            elementos_activos = []
            titulos_elementos = []
            fecha_inicio_elementos = []
            fecha_terminos_elementos = []
            responsable_elementos = []
            padre_elementos = []
            estado_elementos = []
            descripcion_elementos = []
            numeraciones = []

            num_acta = 0
            num_elemento = 0
            for act in actas:
                num_acta += 1
                for tema in act.tema_set.all():
                    for elemento in tema.elemento_set.all():
                        num_elemento += 1
                        if act.fecha_acta and acta.fecha_acta: #si las fechas están definidas
                            #Se agregan los elementos de actas anteriores, como los de la misma acta
                            if ((act.fecha_acta < acta.fecha_acta) or act == acta) and elemento.estado_elemento != "Completado" and elemento.tipo_elemento == "Compromiso": #si la acta fue hecha antes
                                numeracion = str(num_acta)+"."+str(num_elemento)
                                elementos_activos.append(elemento.id)
                                titulos_elementos.append(elemento.titulo_elemento)
                                fecha_inicio = elemento.fecha_inicio if elemento.fecha_inicio else "No definida"
                                fecha_termino = elemento.fecha_termino if elemento.fecha_termino else "No definida"
                                fecha_inicio_elementos.append(fecha_inicio)
                                fecha_terminos_elementos.append(fecha_termino)
                                if elemento.usuario_responsable:
                                    responsable_elementos.append(elemento.usuario_responsable.user.first_name+" "+elemento.usuario_responsable.user.last_name)
                                else:
                                    responsable_elementos.append("No asignado")
                                if elemento.elemento_padre:
                                    padre_elementos.append(elemento.elemento_padre.titulo_elemento)
                                else:
                                    padre_elementos.append("No tiene")
                                estado_elementos.append(elemento.estado_elemento)
                                descripcion_elementos.append(elemento.descripcion_elemento)
                                numeraciones.append(numeracion)
            ctx['total_compromisos_activos'] = zip(titulos_elementos,responsable_elementos,fecha_inicio_elementos,fecha_terminos_elementos,descripcion_elementos,estado_elementos,padre_elementos,numeraciones)
        return JsonResponse(ctx, safe=False)
    except Exception as e:
        print e
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return JsonResponse({})


def valida_correo(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
