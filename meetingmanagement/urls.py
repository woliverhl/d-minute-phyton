from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'easymeetings.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^index/$', 'meetingmanagement.views.index_view', name='index_view'),
    url(r'^cerrar_sesion/$', 'meetingmanagement.views.cerrar_sesion', name='cerrar_sesion'),
    url(r'^agregar_proyecto/$', 'meetingmanagement.views.agregar_proyecto', name='agregar_proyecto'),
    url(r'^editar_proyecto/$', 'meetingmanagement.views.editar_proyecto', name='editar_proyecto'),
    url(r'^ver_lista_asistentes/(?P<id_acta>\d+)/$', 'meetingmanagement.reuniones.ver_lista_asistentes', name='ver_lista_asistentes'),
    url(r'^ver_mapa_mental/(?P<id_proyecto>\d+)/$', 'meetingmanagement.reuniones.ver_mapa_mental', name='ver_mapa_mental'),
    url(r'^modal_editar_acta/(?P<id_proyecto>\d+)/(?P<id_acta>\d+)/$', 'meetingmanagement.reuniones.modal_editar_acta', name='modal_editar_acta'),
    url(r'^editar_acta/(?P<id_acta>\d+)/$', 'meetingmanagement.reuniones.editar_acta', name='editar_acta'),
    #url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/$', 'ver_proyecto', name='ver_proyecto'),
    url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/$', 'meetingmanagement.views.ver_panel_proyecto', name='ver_panel_proyecto'),
    url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/(?P<id_acta>\d+)/$', 'meetingmanagement.views.ver_panel_proyecto', name='ver_panel_proyecto'),
    url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/calendario_actas/$', 'meetingmanagement.views.ver_calendario_actas', name='ver_calendario_actas'),
    url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/kanban/$', 'meetingmanagement.views.ver_kanban', name='ver_kanban'),
    url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/sintesis_dialogica/$', 'meetingmanagement.views.ver_sintesis_dialogica', name='sintesis_dialogica'),
    url(r'^/agregar_acta/(?P<id_proyecto>\d+)/$', 'meetingmanagement.reuniones.agregar_acta', name='agregar_acta'),
    url(r'^/agregar_tema/(?P<id_proyecto>\d+)/(?P<id_acta>\d+)/$', 'meetingmanagement.reuniones.agregar_tema', name='agregar_tema'),
    url(r'^editar_tema/(?P<id_tema>\d+)/$', 'meetingmanagement.reuniones.editar_tema', name='editar_tema'),
    url(r'^agregar_elemento/(?P<id_tema>\d+)/$', 'meetingmanagement.reuniones.agregar_elemento', name='agregar_elemento'),
    url(r'^editar_elemento/(?P<id_elemento>\d+)/$', 'meetingmanagement.reuniones.editar_elemento', name='editar_elemento'),
    url(r'^detalle_elemento_trazabilidad/(?P<id_elemento>\d+)/$', 'meetingmanagement.reuniones.detalle_elemento_trazabilidad', name='detalle_elemento_trazabilidad'),
    url(r'^eliminar_tema/$', 'meetingmanagement.reuniones.eliminar_tema', name='eliminar_tema'),
    url(r'^eliminar_reunion/$', 'meetingmanagement.reuniones.eliminar_reunion', name='eliminar_reunion'),
    url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/editar_acta/$', 'meetingmanagement.views.editar_acta', name='editar_acta'),
    url(r'^proyectos/ver_proyecto/(?P<id_proyecto>\d+)/eliminar_acta/$', 'meetingmanagement.views.eliminar_acta', name='eliminar_acta'),
    url(r'^(?P<id_proyecto>\d+)/filtrar_elementos/$', 'meetingmanagement.views.filtrar_elementos', name='filtrar_elementos'),
    url(r'^(?P<id_proyecto>\d+)/agregar_tarjeta/$', 'meetingmanagement.views.agregar_tarjeta', name='agregar_tarjeta'),
    url(r'^(?P<id_proyecto>\d+)/cambiar_estado_tarjeta/$', 'meetingmanagement.views.cambiar_estado_tarjeta', name='cambiar_estado_tarjeta'),
    url(r'^(?P<id_proyecto>\d+)/escoger_responsable_tarjeta/$', 'meetingmanagement.views.escoger_responsable_tarjeta', name='escoger_responsable_tarjeta'),
    url(r'^(?P<id_proyecto>\d+)/datos_grafico/$', 'meetingmanagement.views.datos_grafico', name='datos_grafico'),
    url(r'^(?P<id_proyecto>\d+)/obtener_compromisos_activos_por_acta/$', 'meetingmanagement.views.obtener_compromisos_activos_por_acta', name='obtener_compromisos_activos_por_acta'),
    url(r'^eliminar_proyecto/$', 'meetingmanagement.views.eliminar_proyecto', name='eliminar_proyecto'),
    url(r'^agregar_usuario/$', 'meetingmanagement.views.agregar_usuario', name='agregar_usuario'),
    url(r'^(?P<id_proyecto>\d+)/eliminar_tarea/$', 'meetingmanagement.views.eliminar_tarea', name='eliminar_tarea'),
    url(r'^(?P<id_proyecto>\d+)/editar_tarjeta/$', 'meetingmanagement.views.editar_tarjeta', name='editar_tarjeta'),
    url(r'^$', 'meetingmanagement.views.index_view', name='index_view'),
)