$('document').ready(function(){
    $('[data-toggle="tooltip"]').tooltip()
    $('#boton-agrega-tema-tooltip').tooltip();

    var nombre_reunion = $('.lista-reuniones.active > a').text();
    $('#nombre-reunion-active').text(nombre_reunion);

    //Antes de hacer el post al servidor se llena la descripcion sacandola del summernote
    $('#agregar_tema').on('click',function(data) {
        descripcion_tema_html = $('#descripcion-tema').code()
        descripcion_tema = $('#descripcion-tema').code().replace(/<\/p>/gi, "\n").replace(/<br\/?>/gi, "\n").replace(/<\/?[^>]+(>|$)/g, "");
        var descripcion_tema_input = htmlEscape(descripcion_tema);
        var descripcion_tema_input_html = htmlEscape(descripcion_tema_html);
        $('#descripcion-tema-input').val(descripcion_tema_input);
        $('#descripcion-tema-input-html').val(descripcion_tema_input_html);
    })

    //Modal de editar un tema
    $('.modal-editar-tema').on('click', function(evt){
        evt.preventDefault();
        var id_tema = $(this).attr('name');
        $('.editando-tema').load("/editar_tema/"+id_tema, function ( status) {
            if ( status === 'success' )
            {
                $($this).modal({ show: true });
            }
        });
    });

    //Modal de editar un tema
    $('.modal-ver-lista-asistentes').on('click', function(evt){
        evt.preventDefault();
        var id_acta = $(this).attr('name');
        $('.ver_lista_asistentes').load("/ver_lista_asistentes/"+id_acta, function ( status) {
            if ( status === 'success' )
            {
                $($this).modal({ show: true });
            }
        });
    });

    //Modal de editar una reunion
    $('.modal-editar-reunion').on('click', function(evt){
        evt.preventDefault();
        var ids = $('.detalle-reunion').attr('id').split('_')
        var id_proyecto = ids[1]
        var id_acta = ids[2]
        $('.editar_reunion').load("/modal_editar_acta/"+id_proyecto+"/"+id_acta, function ( status) {
            if ( status === 'success' )
            {
                $($this).modal({ show: true });
            }
        });
    });

    //Modal de agregar un elemento
    $('.modal-agregar-elemento').on('click', function(evt){
        evt.preventDefault();
        var id_tema = $(this).attr('name');
        $('.agregando-elemento').load("/agregar_elemento/"+id_tema, function ( status) {
            if ( status === 'success' )
            {
                $($this).modal({ show: true });
            }
        });
    });

    //Modal de editar un elemento
    $('.modal-editar-elemento').on('click', function(evt){
        evt.preventDefault();
        var id_elemento = $(this).attr('name');
        $('.editando-elemento').load("/editar_elemento/"+id_elemento, function ( status) {
            if ( status === 'success' )
            {
                $($this).modal({ show: true });
            }
        });
    });

    $('body').on('click', '.modal-ver-trazabilidad', function(evt){
        evt.preventDefault();
        var id_elemento = $(this).attr('data-name');
        $('.ver-trazabilidad').load("/detalle_elemento_trazabilidad/"+id_elemento, function ( status) {
            if ( status === 'success' )
            {
                $($this).modal({ show: true });
            }
        });
    })

    $('#modal-editar-reunion').on('shown.bs.modal', function (e) {
        $('.selectpicker').selectpicker('refresh');
    });

    $('#modal-agregar-elemento').on('shown.bs.modal', function (e) {
        $('#tipo_elemento').on('change',function(data) {
            var estados_compromisos = '<option name="estado_tipo_elemento" value="PA">Pendiente por asignar</option>\
                                        <option name="estado_tipo_elemento" value="Asignado" data-subtext="No ha empezado a realizarlo">Asignado</option>\
                                        <option name="estado_tipo_elemento" value="En curso" data-subtext="Asignado y se está realizando">En curso</option>\
                                        <option name="estado_tipo_elemento" value="Completado">Completado</option>\
                                        <option name="estado_tipo_elemento" value="Eliminado">Eliminado</option>';
            var estados_acuerdos = '<option name="estado_tipo_elemento" value="Vigente">Vigente<\/option>\
                                    <option name="estado_tipo_elemento value="Eliminado">Eliminado<\/option>';
            var estados_dudas = '<option name="estado_tipo_elemento" value="Pendiente">Pendiente</option>\
                                <option name="estado_tipo_elemento" value="Resuelta">Resuelta</option>\
                                <option name="estado_tipo_elemento" value="Eliminada">Eliminada</option>';
            $('#estado_elemento').find('option').remove();
            if($(this).val() == 'Compromiso'){
                $('#estado_elemento').append(estados_compromisos);
                //$('#usuario_responsable_compromiso').css('display','block');
            }
            if($(this).val() == 'Acuerdo' || $(this).val() == 'Desacuerdo') {
                $('#estado_elemento').append(estados_acuerdos);
                $('#usuario_responsable_compromiso').css('display','none');
            }
            if($(this).val() == 'Duda'){
                $('#estado_elemento').append(estados_dudas);
                $('#usuario_responsable_compromiso').css('display','none');
            }
            $('#estado_elemento').selectpicker('refresh');

        });

    })

    /*$('body').on('click','#agregar_elemento',function(e){
        e.preventDefault();
        if ($(this).closest('form').find('#fecha_termino').val() == ""){
            console.log("1");
            return false;
        }
        if ($(this).closest('form').find('#responsable_elemento').val() == ""){
            console.log("2");
            return false;
        }
        if ($(this).closest('form').find('#nombre_elemento').val() == ""){
            console.log("3");
            return false;
        }
        if ($(this).closest('form').find('#descripcion_elemento').val() == ""){
            console.log("4");
            return false;
        }
        $('.form-agregar-elemento').submit();
    })*/

    $('body').on('click', '.selector-tipo-elemento', function(e){
        var imagen = $(this);
        $('#tipo_elemento').val($(imagen).attr('name'));
        $('.selector-tipo-elemento').each(function(){
            $(this).find('img').css('background-color', 'transparent');
        })
        $(imagen).find('img').css('background-color', 'grey');
    });

    $('body').on('click','.eliminar-tema',function(){
        var ids = $('.detalle-reunion').attr('id').split('_')
        var id_proyecto = ids[1]
        var id_acta = ids[2]
        var id_tema = $(this).attr('id').split('_')[1];
        eliminar_tema(id_proyecto, id_acta, id_tema);
    })

    $('body').on('click','.eliminar-reunion',function(){
        var ids = $('.detalle-reunion').attr('id').split('_')
        var id_proyecto = ids[1]
        var id_acta = ids[2]
        eliminar_reunion(id_proyecto, id_acta);
    })



});

function cargarMapaMental(){
    var id_proyecto = $('.menu-principal-proyecto').attr('name');
        $.ajax({
                async: true,
                type: 'get',
                url: '/ver_mapa_mental/'+id_proyecto+'/',
                beforeSend: function () {
                    //$('#loading').fadeIn(100);
                },
                success: function (response) {
                    var data_arbol = response;
                    console.log(response)

                    + function(d3) {

                        var swatches = function(el) {
                            var w = $('#d3-chart22').width(),
                            h = screen.height;

                            var circleWidth = 7;

                            var palette = {
                              "lightgray": "#819090",
                              "gray": "#708284",
                              "mediumgray": "#536870",
                              "darkgray": "#475B62",
                              "darkblue": "#0A2933",
                              "darkerblue": "#042029",
                              "paleryellow": "#FCF4DC",
                              "paleyellow": "#EAE3CB",
                              "yellow": "#A57706",
                              "orange": "#BD3613",
                              "red": "#D11C24",
                              "pink": "#C61C6F",
                              "purple": "#595AB7",
                              "blue": "#2176C7",
                              "green": "#259286",
                              "white": "#fefefe",
                              "yellowgreen": "#738A05"
                            }
                            var nodes = [];
                            for (var key in data_arbol) {
                                if (data_arbol[key]['indice_padre'] == -1){
                                    var tmp = {name : data_arbol[key]['nombre']}
                                    nodes.push(tmp)    
                                }
                                
                            }
                            for (var key in data_arbol) {
                                if (data_arbol[key]['indice_padre'] > -1){
                                    var tmp = {
                                        name : data_arbol[key]['nombre'],
                                        target : [data_arbol[key]['indice_padre']],
                                        id : data_arbol[key]['id']
                                    }
                                    nodes.push(tmp)    
                                }
                                
                            }

                            /*var nodes = [{
                              name: "D3"
                            }, {
                              name: "Core",
                              target: [0]
                            }, {
                              name: "Scales",
                              target: [0]
                            }, {
                              name: "SVG"
                            }, {
                              name: "Time",
                              target: [0]
                            }, {
                              name: "Time",
                              target: [0]
                            }, {
                              name: "Geometry",
                              target: [3]
                            }, {
                              name: "Geography",
                              target: [0]
                            }];*/
                            

                            var links = [];

                            for (var i = 0; i < nodes.length; i++) {
                              if (nodes[i].target !== undefined) {
                                for (var x = 0; x < nodes[i].target.length; x++) {
                                  links.push({
                                    source: nodes[i],
                                    target: nodes[nodes[i].target[x]]
                                  })
                                }
                              }
                            }

                            var myChart = d3.select(el)
                              .append('svg')
                              .attr('width', w)
                              .attr('height', h)

                            var force = d3.layout.force()
                              .nodes(nodes)
                              .links([])
                              .gravity(0.1)
                              .charge(-1000)
                              .size([w, h])

                            var link = myChart.selectAll('line')
                              .data(links).enter().append('line')
                              .attr('stroke', palette.white)

                            var node = myChart.selectAll('circle')
                              .data(nodes).enter()
                              .append('g')
                              .call(force.drag);

                            node.append('circle')
                              .attr('cx', function(d) {
                                return d.x;
                              })
                              .attr('cy', function(d) {
                                return d.y;
                              })
                              .attr('r', circleWidth)
                              .attr('stroke', function(d, i) {
                                if (i > 0) {
                                  return palette.pink
                                } else {
                                  return "transparent"
                                }
                              })
                              .attr('stroke-width', 2)
                              .attr('fill', function(d, i) {
                                if (i > 0) {
                                  return palette.white
                                } else {
                                  return "transparent"
                                }
                              })

                            node.append('text')
                              .text(function(d) {
                                return d.name
                              })
                              .attr('data-toggle','modal')
                              .attr('data-target','#modal-ver-trazabilidad')
                              .attr('data-name',function(d) {
                                return d.id
                              })
                              .attr('class', 'modal-ver-trazabilidad')
                              .attr('title','Acuerdo de coordinación')
                              .attr('font-family', 'Roboto Slab')
                              .attr('fill', function(d, i) {
                                if (i > 0) {
                                  return palette.mediumgray
                                } else {
                                  return palette.white
                                }
                              })
                              .attr('x', function(d, i) {
                                if (i > 0) {
                                  return circleWidth + 20
                                } else {
                                  return circleWidth - 15
                                }
                              })
                              .attr('y', function(d, i) {
                                if (i > 0) {
                                  return circleWidth
                                } else {
                                  return 8
                                }
                              })
                              .attr('text-anchor', function(d, i) {
                                if (i > 0) {
                                  return 'beginning'
                                } else {
                                  return 'end'
                                }
                              })
                              .attr('font-size', function(d, i) {
                                if (i > 0) {
                                  return '1.5em'
                                } else {
                                  return '2.2em'
                                }
                              })

                            force.on('tick', function(e) {
                              node.attr('transform', function(d, i) {
                                return 'translate(' + d.x + ', ' + d.y + ')';
                              })

                              link
                                .attr('x1', function(d) {
                                  return d.source.x
                                })
                                .attr('y1', function(d) {
                                  return d.source.y
                                })
                                .attr('x2', function(d) {
                                  return d.target.x
                                })
                                .attr('y2', function(d) {
                                  return d.target.y
                                })
                            })

                            force.start();

                        }('#d3-chart22');

                    }(window.d3);
                    $('body').on('click','.caminando', function(){
                        alert("sdfds")
                    })
                }
            });


        
    }

function eliminar_tema(id_proyecto, id_acta, id_tema){
    swal({
        title: "¿Estás seguro?",
        text: "El tema y sus elementos serán eliminados permanentemente.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
        closeOnConfirm: false
    }, function(){
        var url = '/eliminar_tema/'
        $.post(
            url,
            {
                'id_proyecto':id_proyecto,
                'id_acta':id_acta,
                'id_tema':id_tema
            }).success(function(){
                swal("¡Tema eliminado!", "El tema ha sido eliminado exitósamente.", "success");
                setTimeout(refresh, 1000);
            })
    });
};

function eliminar_reunion(id_proyecto, id_acta){
    swal({
        title: "¿Estás seguro?",
        text: "La reunion y todos sus temas y elementos asociados serán eliminados permanentemente.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
        closeOnConfirm: false
    }, function(){
        var url = '/eliminar_reunion/'
        $.post(
            url,
            {
                'id_proyecto':id_proyecto,
                'id_acta':id_acta
            }).success(function(){
                swal("¡Reunion eliminada!", "La reunión ha sido eliminada exitósamente.", "success");
                setTimeout(refresh, 1000);
            })
    });
};

function refresh(){
    window.location.reload(false);
}

function htmlEscape(str) {
    return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
}
