var table = null;
var url = "http://localhost:8000/";

function obtenerReporte(id, nombre_tabla){
    // verificamos que la tabla no exista y la destruimos en caso contrario
    // para evitar errores al instanciar de nuevo el mosmo objeto
    if ( table != null ){
      try{
        table.destroy();
      }catch(err){}
    }

    var url_reporte = url+"reportes/reporte/"+id+"/"+nombre_tabla;
    var url_cabceras = url+"reportes/cabeceras_reporte/"+id+"/"+nombre_tabla;

    $.ajax({
      type: "GET",
      url: url_cabceras,
      success: function(data){
        // Genera las cabeceras de la tala
        var th = "<tr>";
        for(var indice in data.headers){
          th += "<th>"+data.headers[indice]+"</th>";
        }
        th += "</tr>";
        $("table thead").html(th);


        // Instanciamos el objeto de tabla
        table = $("table").DataTable({
          serverSide: true,
          bSortClasses: false,
          bProcessing: true,
          ajax: {
            url: url_reporte,
            type: "GET",
          },
          deferRender: true,
          scrollY: 500,
          scrollX: true,
          scroller: {
            loadingIndicator: false
          }
        });

      }
    });

}
