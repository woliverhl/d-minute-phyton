# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from models import *
from forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
import linecache
import sys, os
import time
reload(sys)
sys.setdefaultencoding('utf8')

#Funcion V2.0
def ir_detalle_proyecto(request, id_proyecto, id_acta = None):
    #Variables para el panel
    proyecto = Proyecto.objects.get(id=id_proyecto)
    listas_actas = Acta.objects.filter(proyecto_acta=Proyecto.objects.get(id=id_proyecto)).order_by('fecha_acta')
    usuarios_proyecto = Usuario_Proyecto.objects.filter(proyecto=proyecto)    

    if not id_acta:
        try:
            acta = listas_actas[0]
            acta_seleccionada = acta.id
        except KeyError:
            acta = None
            acta_seleccionada = None
        except IndexError:
            acta = None
            acta_seleccionada = None
    else:
        try:
            acta = Acta.objects.get(id=int(id_acta))
            acta_seleccionada = acta.id
        except:
            try:
                acta = listas_actas[0]
                acta_seleccionada = acta.id
            except KeyError:
                acta = None
                acta_seleccionada = None
            except IndexError:
                acta = None
                acta_seleccionada = None
    #Capturamos todos los compromisos activos (no eliminados)
    elementos_activos = []
    numeraciones = []
    num_acta = 0
    num_elemento = 0
    for ac in listas_actas:
        fecha_acta = ac.fecha_acta
        num_acta = num_acta + 1
        ac.correlativo = int(num_acta)
        for tema in ac.tema_set.all():
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
    for ac in listas_actas:
        for elemento in elementos_activos:
            if elemento.fecha_inicio is not None:
                if elemento.fecha_inicio < ac.fecha_acta:
    """

    #Variables para el tablero kanban
    actas_con_tema = []
    for ac in listas_actas:
        if len(ac.tema_set.all())>0: #Si el acta tiene temas, se agrega a la lista
            actas_con_tema.append(ac)
    #Compromisos que no tienen temas (es decir, fueron agregados directamente al tablero kanban)
    tareas = Elemento.objects.filter(tipo_elemento='Compromiso')

    #Revisamos si usuario logueado es jefe. Si es jefe, se añaden todas las actas como editables
    es_jefe = False
    usuario_logueado = Usuario.objects.get(user=User.objects.get(username=request.user.username))
    user_proyecto_logueado = Usuario_Proyecto.objects.get(proyecto=proyecto, usuario=usuario_logueado)
    if user_proyecto_logueado.rol_proyecto == "Jefe":
        es_jefe = True
    temas_acta = Tema.objects.filter(acta_tema=acta)
    elementos_tema = {}
    for ta in temas_acta:
        elementos = Elemento.objects.filter(tema=ta)
        if elementos:
            elementos_tema[ta.id] = Elemento.objects.filter(tema=ta)
    data = {
        'acta_seleccionada':acta_seleccionada,
        'es_jefe':es_jefe,
        'tareas':tareas,
        'actas_con_tema':actas_con_tema,
        'temas_acta':temas_acta,
        'elementos_tema':elementos_tema,
        'total_compromisos_activos': zip(elementos_activos, numeraciones),  #Esto es para poder iterar sobre las dos listas en un for
        'cantidad_actas_proyecto' : len(listas_actas)+1, #Esto es para la numeración de los elementos. Para ello, se le suma 1 adicional, pues la siguiente acta deberá ser la cant_actas+1.
        'proyecto' : proyecto,
        'usuarios_proyecto' : usuarios_proyecto,
        'listas_actas' : listas_actas,
        'acta' : acta
    }
    return render(request, 'walo-template/proyectos/reuniones/panel_proyecto.html', data)

@login_required(login_url='/index/')
def agregar_acta(request, id_proyecto):
    proyecto_acta = Proyecto.objects.get(id=id_proyecto)
    acta_id = None
    if request.method == 'POST':
        #if request.POST.get('tipo_post'):

        #Agregamos el acta

        if request.POST.get('agregar_acta_hora'):
            hora_acta = request.POST.get('agregar_acta_hora')
        else:
            hora_acta = "00:00"


        if request.POST.get('agregar_acta_fecha'):
            fecha_acta = datetime.strptime(request.POST.get('agregar_acta_fecha') + " " + hora_acta, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
        else:
            fecha_acta = None


        resumen_acta = request.POST.get('agregar_acta_resumen')
        nueva_acta = Acta(proyecto_acta=proyecto_acta, fecha_acta=fecha_acta, resumen_acta=resumen_acta).save()
        acta = Acta.objects.get(id=Acta.objects.latest('id').id)
        acta_id = acta.id

        #Por cada miembro, añadimos usuario_acta
        miembros_presentes = request.POST.getlist('agregar_acta_miembros_presentes')
        agrega_asistentes_reunion(request, miembros_presentes, acta)

    return redirect('ver_panel_proyecto', id_proyecto=id_proyecto, id_acta=acta_id)

@login_required(login_url='/index/')
def editar_acta(request, id_acta):
    acta = Acta.objects.get(id=id_acta)

    if request.POST.get('agregar_acta_hora'):
        hora_acta = request.POST.get('agregar_acta_hora')
    else:
        hora_acta = "00:00"

    if request.POST.get('agregar_acta_fecha'):
        fecha_acta = datetime.strptime(request.POST.get('agregar_acta_fecha') + " " + hora_acta, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
    else:
        fecha_acta = None
    resumen_acta = request.POST.get('agregar_acta_resumen')

    acta.fecha_acta = fecha_acta
    acta.resumen_acta = resumen_acta
    acta.save()

    usuario_acta = Usuario_Acta.objects.filter(acta=acta)
    usuario_acta.delete()
    #Por cada miembro, añadimos usuario_acta
    miembros_presentes = request.POST.getlist('agregar_acta_miembros_presentes')
    agrega_asistentes_reunion(request, miembros_presentes, acta)

    return redirect('ver_panel_proyecto', id_proyecto=acta.proyecto_acta.id, id_acta=acta.id)

def agrega_asistentes_reunion(request, lista_asistentes, acta):

    miembros_proyecto = Usuario_Proyecto.objects.filter(proyecto=acta.proyecto_acta)
    for la in lista_asistentes:
        presente = False
        secretario = False
        asistente = Usuario_Proyecto.objects.get(usuario__id=int(la), proyecto=acta.proyecto_acta)
        if asistente in miembros_proyecto:
            presente = True
        if asistente.usuario.user == request.user:
            secretario = True
        usuario_acta=Usuario_Acta(usuario=asistente.usuario, acta=acta, presente=presente, secretario=secretario)
        usuario_acta.save()


@login_required(login_url='/index/')
def agregar_tema(request, id_proyecto, id_acta):
    proyecto_acta = Proyecto.objects.get(id=id_proyecto)
    acta = Acta.objects.get(id=id_acta)
    if request.method == 'POST':
        #Se agrega el tema
        titulo_tema = request.POST.get('titulo-tema')
        descripcion_tema = request.POST.get('descripcion-tema-input')
        tema = Tema.objects.create(
            acta_tema = acta,
            titulo_tema = titulo_tema,
            descripcion_tema = descripcion_tema
        )
    return redirect('ver_panel_proyecto', id_proyecto=id_proyecto, id_acta=id_acta)

@login_required(login_url='/index/')
def ver_lista_asistentes(request, id_acta):
    asistentes = Usuario_Acta.objects.filter(acta__id=int(id_acta))
    data = {
        'asistentes':asistentes
    }

    return render(request, 'walo-template/proyectos/reuniones/modals/lista_asistentes.html', data)

@login_required(login_url='/index/')
def modal_editar_acta(request, id_proyecto, id_acta):
    proyecto = Proyecto.objects.get(id=int(id_proyecto))
    usuarios_proyecto = Usuario_Proyecto.objects.filter(proyecto=proyecto)
    acta = Acta.objects.get(id=int(id_acta))
    usuarios_acta = Usuario_Acta.objects.filter(acta=acta)
    print usuarios_acta
    usuarios = Usuario.objects.filter(id__in = usuarios_acta.values('usuario_id'))
    print usuarios
    data = {
        'usuarios_proyecto':usuarios_proyecto,
        'usuarios_acta':usuarios,
        'acta':acta,
        'proyecto':proyecto
    }

    return render(request, 'walo-template/proyectos/reuniones/modals/editar_reunion.html', data)

@login_required(login_url='/index/')
def editar_tema(request, id_tema):
    tema = Tema.objects.get(id=int(id_tema))
    if request.method == 'POST':
        #Se agrega el tema
        titulo_tema = request.POST.get('titulo-tema')
        descripcion_tema = request.POST.get('descripcion-tema-input')
        tema.titulo_tema = titulo_tema
        tema.descripcion_tema = descripcion_tema
        tema.save()
        return redirect('ver_panel_proyecto', id_proyecto=tema.acta_tema.proyecto_acta.id, id_acta=tema.acta_tema.id)

    data = {
        'tema':tema
    }

    return render(request, 'walo-template/proyectos/reuniones/modals/editar_tema.html', data)

@login_required(login_url='/index/')
def agregar_elemento(request, id_tema):
    tema = Tema.objects.get(id=int(id_tema))
    if request.method == 'POST':
        #Se agrega el tema
        usuario_logueado = Usuario.objects.get(user__username=request.user.username)
        persona_asignada = request.POST.get('persona_asignada')
        nombre_elemento = request.POST.get('nombre_elemento')
        descripcion_elemento = request.POST.get('descripcion_elemento')
        tipo_elemento = request.POST.get('tipo_elemento')
        estado_elemento = request.POST.get('estado_elemento')
        elemento_padre = request.POST.get('elemento_padre')
        fecha_inicio = time.strftime("%d/%m/%Y")
        fecha_termino = request.POST.get('fecha_termino')

        padre = None
        if elemento_padre:
            padre = Elemento.objects.get(id=int(elemento_padre))

        persona = Usuario.objects.get(id=int(persona_asignada))
        elemento = Elemento.objects.create(
            tipo_elemento = tipo_elemento,
            elemento_padre = padre,
            usuario_responsable = usuario_logueado,
            tema = tema,
            fecha_inicio = datetime.strptime(time.strftime("%d/%m/%Y"),'%d/%m/%Y'),
            fecha_termino = datetime.strptime(fecha_termino,'%d/%m/%Y'),
            estado_elemento = estado_elemento,
            titulo_elemento = nombre_elemento,
            descripcion_elemento = descripcion_elemento,
        )
        return redirect('ver_panel_proyecto', id_proyecto=tema.acta_tema.proyecto_acta.id, id_acta=tema.acta_tema.id)
    usuarios_acta = Usuario_Acta.objects.filter(acta=tema.acta_tema)
    acta = tema.acta_tema
    proyecto = acta.proyecto_acta
    actas = Acta.objects.filter(proyecto_acta=proyecto)
    temas = Tema.objects.filter(acta_tema__in=actas)
    elementos = Elemento.objects.filter(tema__in=temas)
    data = {
        'tema':tema,
        'usuarios_acta':usuarios_acta,
        'elementos':elementos
    }
    return render(request, 'walo-template/proyectos/reuniones/modals/agregar_elemento.html', data)

@login_required(login_url='/index/')
def editar_elemento(request, id_elemento):
    elemento = Elemento.objects.get(id=int(id_elemento))
    if request.method == 'POST':
        #Se agrega el tema
        usuario_logueado = Usuario.objects.get(user__username=request.user.username)
        #persona_asignada = request.POST.get('persona_asignada')
        nombre_elemento = request.POST.get('nombre_elemento')
        descripcion_elemento = request.POST.get('descripcion_elemento')
        tipo_elemento = request.POST.get('tipo_elemento')
        estado_elemento = request.POST.get('estado_elemento')
        elemento_padre = request.POST.get('elemento_padre')
        fecha_termino = request.POST.get('fecha_termino')

        padre = None
        if elemento_padre:
            print elemento_padre
            padre = Elemento.objects.get(id=int(elemento_padre))

        #persona = Usuario.objects.get(id=int(persona_asignada))
        elemento.tipo_elemento = tipo_elemento
        elemento.elemento_padre = padre
        elemento.usuario_responsable = usuario_logueado
        elemento.fecha_termino = datetime.strptime(fecha_termino,'%d/%m/%Y')
        elemento.estado_elemento = estado_elemento
        elemento.titulo_elemento = nombre_elemento
        elemento.descripcion_elemento = descripcion_elemento
        elemento.save()

        return redirect('ver_panel_proyecto', id_proyecto=elemento.tema.acta_tema.proyecto_acta.id, id_acta=elemento.tema.acta_tema.id)
    tema = elemento.tema
    acta = tema.acta_tema
    proyecto = acta.proyecto_acta
    actas = Acta.objects.filter(proyecto_acta=proyecto)
    temas = Tema.objects.filter(acta_tema__in=actas)
    elementos = Elemento.objects.filter(tema__in=temas)
    data = {
        'elemento':elemento,
        'lista_elementos':elementos
    }
    return render(request, 'walo-template/proyectos/reuniones/modals/editar_elemento.html', data)

@csrf_exempt
@login_required(login_url='/index/')
def eliminar_tema(request):
    id_proyecto = int(request.POST.get('id_proyecto'))
    id_acta = int(request.POST.get('id_acta'))
    id_tema = request.POST.get('id_tema')
    tema = Tema.objects.get(id=int(id_tema))
    tema.delete()
    return redirect('ver_panel_proyecto', id_proyecto=id_proyecto, id_acta=id_acta)

@csrf_exempt
@login_required(login_url='/index/')
def eliminar_reunion(request):
    id_proyecto = int(request.POST.get('id_proyecto'))
    id_acta = int(request.POST.get('id_acta'))
    acta = Acta.objects.get(id=id_acta)
    acta.delete()
    return redirect('ver_panel_proyecto', id_proyecto=id_proyecto)

@csrf_exempt
@login_required(login_url='/index/')
def ver_mapa_mental(request, id_proyecto):
    proyecto = Proyecto.objects.get(id=int(id_proyecto))
    actas = Acta.objects.filter(proyecto_acta=proyecto)
    dict_resultado = {}
    dict_tmp = {}
    indice = 0
    dict_tmp[0] = {
        'indice_padre' : -1,
        'indice_propio' : -1,
        'nombre' : proyecto.nombre_proyecto
    }
    for a in actas:    
        temas = Tema.objects.filter(acta_tema=a)
        for t in temas:
            elemento = Elemento.objects.filter(tema=t, elemento_padre__isnull=True).order_by('pk')
            for e in elemento:
                dict_tmp[e.pk] = {
                    'indice_padre' : 0,
                    'indice_propio' : indice,
                    'nombre' : e.titulo_elemento,
                    'tema': t.titulo_tema,
                    'acta': a.fecha_acta,
                    'id': e.pk
                }
                indice = indice + 1
            for e in elemento:
                dict_resultado = obtieneMapaHijos(dict_tmp, a, t, e)


    return JsonResponse(dict_resultado)

def obtieneMapaHijos(dict_elementos, acta, tema, elemento):
    dict_tmp = dict_elementos
    elementos = Elemento.objects.filter(tema=tema, elemento_padre=elemento).order_by('pk')
    if not elementos:
        return dict_tmp
    else:
        for e in elementos:
            dict_tmp[e.pk] = {
                'indice_padre' : dict_elementos[elemento.pk]['indice_propio'],
                'indice_propio' : 0,
                'nombre' : e.titulo_elemento,
                'tema': tema.titulo_tema,
                'acta': acta.fecha_acta,
                'id': e.pk
            }
        for e in elementos:
            dict_tmp = obtieneMapaHijos(dict_tmp, acta, tema, e)
        return dict_tmp


@login_required(login_url='/index/')
def detalle_elemento_trazabilidad(request, id_elemento):
    elemento = Elemento.objects.get(id=int(id_elemento))
    tema = elemento.tema
    acta = tema.acta_tema
    proyecto = acta.proyecto_acta
    data = {
        'tema':tema,
        'elemento':elemento,
        'acta':acta,
        'proyecto':proyecto
    }
    return render(request, 'walo-template/proyectos/reuniones/modals/detalle_elemento_trazabilidad.html', data)