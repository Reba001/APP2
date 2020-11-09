var app={
    initialize:function(){
        localStorage.setItem('icon','');
        $('#nform').text(localStorage.getItem('nform'));
        var formid = getParameterByName('formid');
        this.datos("cPen","finalizados","enviados");
        var proceso = localStorage.getItem("proceso");
        this.icon(formid);
    },
    icon: function(id){
        gforms.transaction(function(tx){
            tx.executeSql("SELECT icon,nombre from formularios WHERE form_id=?", [id], function(tx1,result){
                var len = result.rows.length;
                    for(var i=0; i<len; i++){
                        localStorage.setItem('icon',result.rows.item(i).icon);
                    }
            },this.errorCT);
        },this.errorCT,this.successCT);
    },
    datos: function(p,f,e){
        gforms.transaction(function(tx){
            var pen="";
            var fin="";
            var env="";
            var formid = getParameterByName('formid');
            var pendientes = document.getElementById(p);
            var finalizados = document.getElementById(f);
            var enviados = document.getElementById(e);
            var proceso = localStorage.getItem("proceso");
            var usuario = window.localStorage.getItem("login");

            tx.executeSql("SELECT id,external_id,fechasig,estado from daux WHERE form_id=? and usuario=? ORDER BY estado ASC", [formid,usuario], function(tx1,result){
                var len = result.rows.length;
                    for(var i=0; i<len; i++){
                        var externalid = "";
                        var iden = "";
                        var fecha ="";
                        if(result.rows.item(i).estado=="Finalizado"){
                            fin += '<li ><a href="#" ><i class="fa fa-angle-right "></i><i class="font-17 fa fa-check color-green-dark"></i><span>' +result.rows.item(i).external_id + '</span><em>' + result.rows.item(i).fechasig + '</em></a></li>'
                        }
                        else{
                            if(result.rows.item(i).estado=="Enviado"){
                                env += '<li ><a href="#"><i class="fa fa-angle-right "></i><i class="font-17 fa fa-check color-green-dark"></i><span>' +result.rows.item(i).external_id + '</span><em>' + result.rows.item(i).fechasig + '</em></a></li>'
                            }
                            else{
                                externalid = result.rows.item(i).external_id;
                                iden = result.rows.item(i).id;
                                fecha = result.rows.item(i).fechasig;
                                app.hijos(externalid,fecha,iden);
                            }
                        }
                    }   
                    finalizados.innerHTML = fin;
                    enviados.innerHTML = env;
            },this.errorCT);
        },this.errorCT,this.successCT);
    },
    hijos: function(ex,fe,id){
        
        gforms.transaction(function(tx){
            tx.executeSql("SELECT id,external_id,external,fechasig,estado,form_id from daux WHERE external=? ORDER BY estado ASC", [ex], function(tx2,aux){
                var len1 = aux.rows.length;
                if(len1>0){
                    var icon  = localStorage.getItem('icon');            
                    var a = document.createElement("a");
                    var ai1 = document.createElement("i");
                    var ai = document.createElement("i");
                    var di = document.createElement("i");
                    var  aC = document.createTextNode(ex+" ("+fe+")");
                    a.setAttribute("href","#");
                    ai1.setAttribute("onclick","app.openData("+id+")")
                    di.setAttribute("onclick","app.delete("+id+")")
                    a.setAttribute("class","color-black font-10");
                    a.setAttribute("data-accordion","accordion-"+id);
                    ai.setAttribute("class","fa fa-angle-down");
                    di.setAttribute("class","font-18 fa fa-trash color-red-dark");
                    di.setAttribute("style","margin-right:11px !important; float:right; margin:13px");
                    // ai1.setAttribute("class","font-18 fa fa-users color-green-dark");
                    ai1.setAttribute("class","font-18 "+icon+" color-orange-dark");
                    // ai1.setAttribute("style","margin:6px");
                    
                    document.getElementById("cPen").appendChild(a);
                    a.appendChild(ai1);
                    a.appendChild(aC);
                    a.appendChild(di);
                    a.appendChild(ai);

                    var div = document.createElement("div");
                    div.setAttribute("class","accordion-content");
                    div.setAttribute("id","accordion-"+id);
                    document.getElementById("cPen").appendChild(div);

                    for(var ii=0; ii<len1; ii++){
                        var p = document.createElement("p");
                        var pi = document.createElement("i");
                        var hi = document.createElement("i");
                        pi.setAttribute("onclick","app.openAux("+aux.rows.item(ii).id+","+aux.rows.item(ii).form_id+")")
                        if(aux.rows.item(ii).estado=='Finalizado'){
                            pi.setAttribute("class","font-15 fa fa-user color-green-dark");
                        }
                        else{
                            
                            pi.setAttribute("class","font-15 fa fa-user color-red-dark");
                        }                                
                        pi.setAttribute("style","margin:8px; margin-left:15px;");
                        hi.setAttribute("class","font-18 fa fa-trash color-red-dark");
                        hi.setAttribute("style","margin-right:11px !important; float:right; margin:13px");
                        hi.setAttribute("onclick","app.deleteAux("+aux.rows.item(ii).id+")")
                        p.setAttribute("class","color-black font-8");
                        var  pC = document.createTextNode("  "+aux.rows.item(ii).external_id+" ("+aux.rows.item(ii).fechasig+")");
                        p.appendChild(pi);
                        p.appendChild(pC);
                        div.appendChild(p);
                        p.appendChild(hi);
                    }
                    $(a).on( "click", function(){
                            var accordion_number = $(this).data('accordion');
                            $('.accordion-content').slideUp(200);
                            $('.accordion i').removeClass('rotate-180');
                            if($('#'+accordion_number).is(":visible")){
                                $('#'+accordion_number).slideUp(200);
                                $(this).find('i:last-child').removeClass('rotate-180');
                            }else{
                                $('#'+accordion_number).slideDown(200);
                                $(this).find('i:last-child').addClass('rotate-180');
                            }
                        });
               
                }
                else{
                    var icon  = localStorage.getItem('icon');
                    var a = document.createElement("a");
                    var ai1 = document.createElement("i");
                    var ai = document.createElement("i");
                    var di = document.createElement("i");
                    var  aC = document.createTextNode(ex+" ("+fe+")");
                    a.setAttribute("href","#");
                    ai1.setAttribute("onclick","app.openAux("+id+")");
                    di.setAttribute("onclick","app.delete("+id+")")
                    a.setAttribute("class","color-black font-10");
                    a.setAttribute("data-accordion","accordion-"+id);
                    ai.setAttribute("class","fa fa-angle-right");
                    di.setAttribute("class","font-18  fa fa-trash color-red-dark");
                    di.setAttribute("style","margin-right:11px !important; float:right; margin:13px");
                    ai1.setAttribute("class","font-18 "+icon+" color-orange-dark");
                    // ai1.setAttribute("style","margin:8px");
                    document.getElementById("cPen").appendChild(a);
                    a.appendChild(ai1);
                    a.appendChild(aC);
                    a.appendChild(di);
                    a.appendChild(ai);
                }
            },this.errorCT);
        },this.errorCT,this.successCT);
    },
    openData: function(id){
        var form_id = getParameterByName('formid');
        localStorage.setItem("dataId",id);
        document.location = "formDatas.html?id=" + id+"&formid="+form_id;
    },
    openAux: function(id){
        var form_id = getParameterByName('formid');
        var form = getParameterByName('formid');
        localStorage.setItem("dataId",id);
        document.location = "smodalD.html?id=" + id+"&formid="+form+"&idv="+form_id;
    },
    delete: function(id){
        Swal.fire({
            title: 'Estás seguro?',
            text: "¡No podrás revertir esto!",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '¡Sí, Eliminar!'
            }).then((result) => {
            if (result.value) {
                gforms.transaction(function(tx){
                    var executeQuery = "DELETE FROM daux where Id=?";
                    tx.executeSql(executeQuery, [id],function (tx, result) {
                        Swal.fire(
                            'Eliminado',
                            'el formulario ha sido eliminado.',
                            'success'
                        );
                        window.location.reload(true);
                    },function (error) { alert('Data no Eliminada'); });
                },this.errorCT,this.successCT);
            }
        });
    },
    deleteAux: function(id){
        Swal.fire({
            title: 'Estás seguro?',
            text: "¡No podrás revertir esto!",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '¡Sí, Eliminar!'
            }).then((result) => {
            if (result.value) {
                gforms.transaction(function(tx){
                    var executeQuery = "DELETE FROM daux where Id=?";
                    tx.executeSql(executeQuery, [id],function (tx, result) {
                        Swal.fire(
                            'Eliminado',
                            'el formulario ha sido eliminado.',
                            'success'
                        );
                        window.location.reload(true);
                    },function (error) { alert('Data no Eliminada'); });
                },this.errorCT,this.successCT);
            }
        });
    },
    errorCT: function(err){
        console.log("Error al seleccionar Formularios:"+err.message);
    },
    successCT: function(){

        console.log("Consulta de formularios Exitoso");
    },
    errorUT: function(){
        console.log("Error al actualizar datos de formularios");
    },
    abrir:function(){
        var id = getParameterByName('formid');
        document.location.href = "formulario.html?formid=" + id;
    }
}