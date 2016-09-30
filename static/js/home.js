function obtenerReporte(id){
  $(".header-copy").remove();

  $.ajax({
    type: "GET",
    url: "http://localhost:8000/reportes/reporte/"+id+"/"+10+"/1",
    success: function(data){
      // Genera las filas de la tabla
      var rows = $.map(data['data'], function(actual,indice,array){
            var tr = "<tr>";
            var indice, valor;
            for(indice in actual){
              tr += "<td>"+actual[indice]+"</td>";
            }
            tr += "</tr>";
            return tr;
      });

      // Genera las cabeceras de la tala
      var th = "";
      for(var indice in data.headers){
        th += "<th>"+data.headers[indice]+"</th>";
      }

      $("table thead tr").html(th);
      $("table tbody").html(rows);

      // Flota la cabecera de la tabla
      $('.table-fixed-header').fixedHeader();

      /* sincroniza cabeceras*/
      $(".header tr th").each(function(i,o){
        $($(".header-copy tr th")[i]).width($(o).width());
      });

      // Mueve la cabecera junto con la tabla al hacer scroll lateral 
      $(document).scroll(function(){
        $(".header-copy").css({
          "transform": "translate(-"+($(this).scrollLeft())+"px, 0)"
        });
      });
    }
  });
}
