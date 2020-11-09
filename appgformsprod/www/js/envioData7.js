var envio ={
    sendTotal:async function(){
        if (verificacion()){
            var stack = $.Callbacks('unique');
            stack.add(envio.fetchAux);
            stack.fire();
        }
    },
    enfetchEnd: function(){
        var usr = window.localStorage.getItem("login");
        gforms.transaction(function(tx){
            var formid = getParameterByName('formid');
            tx.executeSql('SELECT form_id,data,external_id,fechasig,id,status from datos WHERE form_id=? and estado=?', [formid,"Finalizado"], function(tx1,result){
                var len = result.rows.length;
                if(len != 0){
                    for(var i=0; i<len; i++){
                        var obj =result.rows.item(i).data;
                        var miCadena = obj.replace(/[']/g, "`");
                        var objson = miCadena.replace(/"/g, "'");
                        envio.sendData(result.rows.item(i).form_id,objson,result.rows.item(i).external_id,usr,result.rows.item(i).fechasig,parseInt(result.rows.item(i).id),result.rows.item(i).status);
                    }
                }
                else{
                    $("#everything-wrapper").fadeOut(600);
                    location.reload();
                }
            },envio.errorCT);
        },envio.errorCT,envio.successCT);
    },
    fetchAux: function(){
        $("#everything-wrapper").show();
            var usr = window.localStorage.getItem("login");
            gforms.transaction(function(tx){
                tx.executeSql('SELECT form_id,data,external_id,fechasig,id,external,status from daux WHERE estado=?', ["Finalizado"], function(tx1,result){
                    var len = result.rows.length;
                    localStorage.setItem("longitud",len);
                    localStorage.setItem("enviados",0);
                    if(len != 0){
                        for(var i=0; i<len; i++){
                            
                            var obj =result.rows.item(i).data;
                            var miCadena = obj.replace(/[']/g, "`");
                            var objson = miCadena.replace(/"/g, "'");
                            envio.sendDataAux(result.rows.item(i).form_id,objson,result.rows.item(i).external_id,usr,result.rows.item(i).fechasig,parseInt(result.rows.item(i).id),result.rows.item(i).external,result.rows.item(i).status);
                        }
                    }
                },envio.errorCT);
            },envio.errorCT,envio.successCT);
    },
    sendData: function(formid,datos,external,usuario,fecha,id,status){
        var iduser = window.localStorage.getItem("id");
        var dire = window.localStorage.getItem("GformsGru");
        let Data = 'mutation{ ' +
                        'addGrupos( ' +
                            'rgru_idfor: "' + formid +'" '+
                            ',rgru_datos: "' +datos+ '" '+
                            ',rgru_external_id: "' + external +'" '+
                            ',rgru_usuario_grabacion: "' + usuario+'" '+
                            ',rgru_iduser: '+ iduser +
                            ',rgru_codcia: "1" '+
                            ',id_estado: ' + status +
                            ',fecha_asignacion: "'+ fecha+'"){ '+
                                'id ' +
                                'rgru_idfor ' +
                                'rgru_external_id ' +
                        '}' +
                    '}';
        console.log(Data);
        debugger;
        $.ajax({
            url: dire,
            async: false,   // this will solve the problem
            headers: {
                "Content-Type": "application/graphql"
            },
            type: "POST",
            contentType: "application/graphql",
            data: Data,
            success: function (data) {
                var rec_recibidos = JSON.parse(JSON.stringify(data));
                envio.update(external);
            },
            error: function (data) {
                console.log(data);
                location.reload();
            }
        });
    },
    sendDataAux: function(formid,datos,external,usuario,fecha,id,padre,status){
        var iduser = window.localStorage.getItem("id");
        var dire = window.localStorage.getItem("GformsGru");
        let Data = 'mutation{ ' +
                        'addIntegrantes( ' +
                              'rint_external_id: "' + external+'" '+
                              ',rint_rgru_external_id: "' +padre+ '" '+
                            ',rint_idfor: "' + formid +'" '+
                            ',rint_datos: "' + datos+'" '+
                            ',rint_usuario_grabacion: "'+ usuario +'"'+
                            ',rint_iduser:'+iduser +
                            ',rint_codcia: "1"' +
                            ',id_estado: ' + status +
                            ',fecha_asignacion: "'+ fecha+'"){ '+
                                'id ' +
                                'rint_idfor ' +
                        '}' +
                    '}';
        $.ajax({
            url: dire,
            async: false,   // this will solve the problem
            headers: {
                "Content-Type": "application/graphql"
            },
            type: "POST",
            contentType: "application/graphql",
            data: Data,
            success: function (data) {
                var addAuxiliares = JSON.parse(JSON.stringify(data));
                envio.updateAux(external);
            },
            error: function (data) {
                console.log(data);
            }
        });
    },
    update: function(id){
        var date = new Date();
        var d  = date.getDate();
        var day = (d < 10) ? '0' + d : d;
        var m = date.getMonth() + 1;
        var month = (m < 10) ? '0' + m : m;
        var yy = date.getYear();
        var year = (yy < 1000) ? yy + 1900 : yy;
        var h = date.getHours();
        var m = date.getMinutes();
        var s = date.getSeconds();
        var fecha = year + "-" + month + "-" +day+" "+h+":"+m+":"+s;
        gforms.transaction(function (tx) {
            tx.executeSql("UPDATE datos SET estado='Enviado',fechasig=? where external_id= ? ", [fecha,id], envio.successUT, envio.errorUT);
        }, envio.errorUT, envio.successUTF);
    },
    updateAux: function(id){
        gforms.transaction(function (tx) {
            tx.executeSql("UPDATE daux SET estado='Enviado' where external_id= ? ", [id], envio.successUT, envio.errorUT);
        }, envio.errorUT, envio.successUT);
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
    //finaliza el envio del padre
    successUTF: function(){
        $("#everything-wrapper").fadeOut(600);
        location.reload();
        console.log("Actualización de Datos Exitoso");
    },
    successUT: function(){
        var len = localStorage.getItem("enviados");
        var actual = parseInt(len)+1;
        console.log("enviados: "+actual);
        localStorage.setItem("enviados",actual);
        var lon = localStorage.getItem("longitud");
        if(actual==lon){
            $("#everything-wrapper").fadeOut(600);
            location.reload();
        }
        console.log("Actualización de Datos Exitoso");
    },
}