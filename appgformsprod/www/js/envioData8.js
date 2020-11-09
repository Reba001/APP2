var envio ={
    sendTotal: function(){
        if (verificacion()){
            envio.fetchAux();
            envio.enfetchEnd();
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
                        console.log("fechasig: "+result.rows.item(i).fechasig);
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
                    console.log(len);
                    localStorage.setItem("longitud",len);
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
        debugger;
        var iduser = window.localStorage.getItem("id");
        var dire = window.localStorage.getItem("gformsGes");
        let Data = 'mutation{ ' +
                        'addFacturadores( ' +
                            'fac_idfor: "' + formid +'" '+
                            ',fac_datos: "' +datos+ '" '+
                            ',fac_external_id: "' + external +'" '+
                            ',fac_usuario_grabacion: "' + usuario+'" '+
                            ',fac_iduser: '+ iduser +
                            ',fac_codcia: "1" '+
                            ',id_estado: ' + status +
                            ',fecha_asignacion: "'+ fecha+'"){ '+
                                'id ' +
                                'fac_idfor ' +
                                'fac_external_id ' +
                        '}' +
                    '}';
        console.log(Data);
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
                debugger;
                envio.update(external);
            },
            error: function (data) {
                console.log(data);
            }
        });
    },
    sendDataAux: function(formid,datos,external,usuario,fecha,id,padre,status){
        var iduser = window.localStorage.getItem("id");
        var dire = window.localStorage.getItem("GformsInd");
        let Data = 'mutation{ ' +
                        'addAuxiliares( ' +
                              'raux_external_id: "' + external+'" '+
                              ',raux_rec_external_id: "' +padre+ '" '+
                            ',raux_idfor: "' + formid +'" '+
                            ',raux_datos: "' + datos+'" '+
                            ',raux_usuario_grabacion: "'+ usuario +'"'+
                            ',raux_iduser:'+iduser +
                            ',raux_codcia: "1"' +
                            ',id_estado: ' + status +
                            ',fecha_asignacion: "'+ fecha+'"){ '+
                                'id ' +
                                'raux_idfor ' +
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
                var addAuxiliares = JSON.parse(JSON.stringify(data));
                envio.updateAux(external);
            },
            error: function (data) {
                console.log(data);
                $("#everything-wrapper").fadeOut(600);
                debugger;
                location.reload();
            }
        });
    },
    update: function(id){
        debugger;
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
        debugger;
        $("#everything-wrapper").fadeOut(600);
        location.reload();
        console.log("Actualización de Datos Exitoso");
    },
    successUT: function(){
        var len = localStorage.getItem("enviados");
        var actual = parseInt(len)+1;
        localStorage.setItem("enviados",actual);
        var lon = localStorage.getItem("longitud");
        debugger;
        if(actual==lon){
            $("#everything-wrapper").fadeOut(600);
            location.reload();
        }
        console.log("Actualización de Datos Exitoso");
    },
}