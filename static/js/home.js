var table = null;
var url = "http://localhost:8000/";
var visible = false;


$("#nuevo_reporte").submit(function(){
    $("#guardar").addClass("disabled");
});

function obtenerReporte(id, nombre_tabla){
    $("#columns").show();
    showHideColumns(0);

    // verificamos que la tabla no exista y la destruimos en caso contrario
    // para evitar errores al instanciar de nuevo el mosmo objeto
    if ( table != null ){
      try{
        table.destroy();
      }catch(err){}
    }

    $("table thead, table tbody").empty();

    var url_reporte = url+"reportes/reporte/"+id+"/"+nombre_tabla;
    var url_cabceras = url+"reportes/cabeceras_reporte/"+id+"/"+nombre_tabla;

    $.ajax({
      type: "GET",
      url: url_cabceras,
      success: function(data){
        // Genera las cabeceras de la tala
        $(".chips").empty();
        var th = "<tr>";
        for(var indice in data.headers){
          $(".chips").append('<div class="chip">'+data.headers[indice]+'<i class="fa fa-times" onclick="eliminarColumna(\''+indice+'\', \''+nombre_tabla+'\', $(this))"></i></div>')
          th += "<th>"+data.headers[indice]+"</th>";
        }
        th += "</tr>";
        $("table thead").html(th);


        // Instanciamos el objeto de tabla
        table = $("table").DataTable({
          serverSide: true,
          bSortClasses: false,
          bProcessing: true,
          searching: false,
          ajax: {
            url: url_reporte,
            type: "GET",
            data: {
              lebgth: 10
            }
          },
          deferRender: true,
          scrollY: 400,
          scrollX: true,
          scroller: {
            loadingIndicator: false
          }
        });

      }
    });

}

function showHideColumns(visible_){
  if ( visible_ == 0 ) {
      $(".chips").hide();
      return;
  }

  if ( visible ){
    $("#columns i").attr("class", "fa fa-angle-right");
  }else {
    $("#columns i").attr("class", "fa fa-angle-down");
  }

  $( ".chips" ).toggle("slow", function(){
    visible = (visible==false)?true:false;
  });

}


function eliminarColumna(columna, reporte, objeto){
  var url_drop = url+"reportes/reporte/dropcolumn/"+columna+"/"+reporte;

  if ( confirm("Seguro que desea eliminar la columna "+ columna) ){
    objeto.remove();
    $.ajax({
      url: encodeURI(url_drop),
      type: "GET",
      success: function(data){
        if ( data.success == "true" ){
          $("#"+reporte).click();
        }
      }
    })
  }
}

function eliminar_reporte(id, nombre, nombre_tabla){
  var url_drop = url+"reportes/reporte/eliminar/"+id+"/"+nombre_tabla
  if ( confirm("Seguro que desea eliminar el reporte "+nombre) )
  $.ajax({
    url: url_drop,
    type: "GET",
    success: function(data){
      window.location = url+'home/';
    }
  })
}
