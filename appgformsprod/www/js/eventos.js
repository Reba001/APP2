var platform;

window.onload= function(){
    platform = cordova.platformId;    
    document.addEventListener("deviceready", onDeviceReady, false);
    // cordova.plugins.backgroundMode.excludeFromTaskList();

}
function onDeviceReady() {
    app.initialize();
    document.addEventListener("backbutton", BackKeyDown, false);
    //document.addEventListener("pause", onPause, false);
    if(document.location.pathname.includes('datosAdmin.html')||document.location.pathname.includes('Data6.html')||document.location.pathname.includes('smodalD.html')||document.location.pathname.includes('formDataFin.html')||document.location.pathname.includes('/Data2.html')||document.location.pathname.includes('/Data3.html')||document.location.pathname.includes('/Data5.html')||document.location.pathname.includes('/datosO.html')||document.location.pathname.includes('/formDatas.html')||document.location.pathname.includes('/formData.html')||document.location.pathname.includes('/formulario.html')||document.location.pathname.includes('/smodal.html')||document.location.pathname.includes('/modal.html')||document.location.pathname.includes('/datos.html')||document.location.pathname.includes('/Data8.html')){
        console.log("datosO.html")
    }else{
        menu();
    }
    var color = localStorage.getItem("fondo");
    var democs = 'gradient-body-1 gradient-body-2 gradient-body-3 gradient-body-4 gradient-body-5 gradient-body-6 gradient-body-7 gradient-body-8 gradient-body-9 gradient-body-10';
    $('.page-bg, .menu-bg').removeClass(democs).addClass(color);
        notificaciones();
    requestLocationAccuracy();
    comprobar();
    
    var notificationOpenedCallback = function(jsonData) {
        console.log('notificationOpenedCallback: ' + JSON.stringify(jsonData));
    };
    window.plugins.OneSignal.setRequiresUserPrivacyConsent(true);
    
      window.plugins.OneSignal
        .startInit("cd9675aa-d893-453d-84d5-bacfd7ac1232")
        .handleNotificationOpened(notificationOpenedCallback)
        .endInit();
    
    window.plugins.OneSignal.userProvidedPrivacyConsent((providedConsent) => {
        if(providedConsent==true){
            window.plugins.OneSignal.getPermissionSubscriptionState(function(status) {
                console.log(status.subscriptionStatus.userId); // String: OneSignal Player ID
                var userId =status.subscriptionStatus.userId
                var iduser = window.localStorage.getItem("login");
                var onsignal = window.localStorage.getItem("onsignal");

                if(onsignal==0){
                    var form = new FormData();
                    form.append("user", iduser);
                    form.append("idonesignal", userId.toString());
                    console.log(form);
                    var RegPush = localStorage.getItem('RegPush');
                    console.log(RegPush);
                    $.ajax({
                        url: RegPush,
                        type: 'POST',
                        processData: false,
                        contentType: false,
                        mimeType: "multipart/form-data",
                        data: form,
                        success: function(data){
                            console.log(data);
                                if(data){
                                    localStorage.setItem("onsignal",data);
                                }
                        },
                        error: function (data) {
                            console.log(data);
                        }
                        });
                }
            });
        }
        else{
            Swal.fire({
                title: "Notificaciones",
                text: "Para recibir notificaciones debes",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: 'green',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Si, Activar'
              }).then((result) => {
                if (result.value) {
                    window.plugins.OneSignal.provideUserConsent(true);
                    localStorage.setItem("onsignal","0");
                }
            })
        }
    });
    
}

function notificaciones(){
    console.log("notificaciones");
    var socket = io.connect("http://52.167.178.236:5001");

    var idUsuario = window.localStorage.getItem("id");
    socket.on("chat-noty-"+idUsuario, function(data){
        console.log(data);
        
        cordova.plugins.notification.local.schedule({
            id: 20,
            title: 'Mensaje de?',
            icon: 'http://climberindonesia.com/assets/icon/ionicons-2.0.1/png/512/android-chat.png',
            text: [
                { person: data.user , message: data.text }
            ]
        });
    });

}

function pago(){
    console.log("notificaciones de pago");
    var net = require('net');
    var client = new net.Socket();
    client.connect(5002, 'http://52.167.178.236', function() {
        console.log('Connected');
        client.write('Hello, server! Love, Client.');
    });

    client.on("chat-noty-"+idUsuario, function(data) {
        console.log('Received: ' + data);
        cordova.plugins.notification.local.schedule({
            id: 20,
            title: 'Mensaje de?',
            icon: 'http://iforms.genesisempresarial.org/im/pay.png',
            text: [
                { person: data.user , message: data.text }
            ]
        });
        client.destroy(); // kill client after server's response
    });

    client.on('close', function() {
        console.log('Connection closed');
    });
}
function BackKeyDown()
{
    console.log("backbutton");
    console.log(document.location.pathname);
    if(document.location.pathname.includes('/formularios.html')){
        console.log("si funciona hahah");
    }
    if(document.location.pathname.includes('/chat2.html')){
        console.log("si funciona hahah");
    }
    if(document.location.pathname.includes('/Data2.html')){
        document.location.href="formularios.html";
    }
    if(document.location.pathname.includes('/Data3.html')){
        document.location.href="formularios.html";
    }
    if(document.location.pathname.includes('/Data5.html')){
        document.location.href="formularios.html";
    }
    if(document.location.pathname.includes('/Data6.html')){
        document.location.href="formularios.html";
    }
    if(document.location.pathname.includes('/Data8.html')){
        document.location.href="formularios.html";
    }
    if(document.location.pathname.includes('/formDataFin.html')){
        document.location.href="formularios.html";
    }
    if(document.location.pathname.includes('/datos.html')){
        document.location.href="formularios.html";
    }
    if(document.location.pathname.includes('/adminDatos.html')){
        document.location.href="admin.html";
    }
    if(document.location.pathname.includes('/datosAdmin.html')){
        document.location.href="admin.html";
    }
    if(document.location.pathname.includes('/modal.html')){
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Desea salir?",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Si',
            cancelButtonText: 'No'
        }).then((result) => {
            if (result.value) {                
                var un = localStorage.getItem("dataId");
                document.location = "formDatas.html?id=" + un+"&formid="+idform;
            }
        })
    }
    if(document.location.pathname.includes('/smodal.html')){
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Desea salir?",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Si',
            cancelButtonText: 'No'
        }).then((result) => {
            if (result.value) {                
                var proceso = localStorage.getItem("proceso");
                if(proceso==2){
                    window.location="Data2.html?formid="+idform;
                }
                if(proceso==3){
                    window.location="Data3.html?formid="+idform;
                }
                if(proceso==5){
                    window.location="Data5.html?formid="+idform;
                }
            }
        })
    }
    if(document.location.pathname.includes('/formulario.html')){
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Desea salir?",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Si',
            cancelButtonText: 'No'
        }).then((result) => {
            if (result.value) {
                var proceso = localStorage.getItem("proceso");
                if(proceso==2){
                    window.location="Data2.html?formid="+idform;
                }
                if(proceso==3){
                    window.location="Data3.html?formid="+idform;
                }
                if(proceso==5){
                    window.location="Data5.html?formid="+idform;
                }
                if(proceso==8){
                    window.location="Data8.html?formid="+idform;
                }
            }
        })
    }

    if(document.location.pathname.includes('/formDatas.html')){
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Desea salir?",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Si',
            cancelButtonText: 'No'
        }).then((result) => {
            if (result.value) {
                var proceso = localStorage.getItem("proceso");
                if(proceso==2){
                    window.location="Data2.html?formid="+idform;
                }
                if(proceso==3){
                    window.location="Data3.html?formid="+idform;
                }
                if(proceso==5){
                    window.location="Data5.html?formid="+idform;
                }
                if(proceso==8){
                    window.location="Data8.html?formid="+idform;
                }
            }
        })
    }
    if(document.location.pathname.includes('/formData.html')){
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Desea salir?",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Si',
            cancelButtonText: 'No'
        }).then((result) => {
            if (result.value) {
                var proceso = localStorage.getItem("proceso");
                
                    window.location="datos.html?formid="+idform;
                
            }
        })
    }
    if(document.location.pathname.includes('/smodalD.html')){
        Swal.fire({
            title: '¿Estás seguro?',
            text: "Desea salir?",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Si',
            cancelButtonText: 'No'
        }).then((result) => {
            if (result.value) {
                var id = getParameterByName('formid');
                
                    window.location="Data6.html?formid="+id;
                
            }
        })
    }
}

function onPause() {    
}


var ruta = {
    interna: function(){
        var dire ="http://192.168.9.12:3000/gforms";
        // window.localStorage.removeItem("url");
        // window.localStorage.setItem("url",dire);
        window.location.reload();
    },
    externa: function(){
        var dire ="http://52.167.178.236:3000/gforms";
        // window.localStorage.removeItem("url");
        // window.localStorage.setItem("url",dire);
        window.location.reload();
    },
    pagina: function(pagina){
        window.location=pagina;
    }
}



var Latitude = undefined;
var Longitude = undefined;

// Get geo coordinates

function getMapLocation() {
    
    navigator.geolocation.getCurrentPosition
    (onMapSuccess, onMapError, { maximumAge: 3000, enableHighAccuracy: true });
}
function getCordenadas() {
    
    navigator.geolocation.getCurrentPosition
    (onMap, onMapError, { maximumAge: 3000, enableHighAccuracy: true });
    var cord = window.localStorage.getItem("cordenadas");
    return cord;
}

// Success callback for get geo coordinates

var onMap = function (position) {
    var json = {
        data: []
    };
    Latitude = position.coords.latitude;
    Longitude = position.coords.longitude;
    json.data.push({
        "Latitude" : Latitude,
        "Longitude" : Longitude
    });
    window.localStorage.setItem("cordenadas",JSON.stringify(json.data));
    
}

function onMapError(error) {
    console.log('code: ' + error.code + '\n' +
        'message: ' + error.message + '\n');
        
}
function comprobar(position){
    if(document.location.pathname.includes('/formulario.html')){
        requestLocationAccuracy();
        getMapLocation();
        setInterval('getMapLocation()',300000);
    }
    if(document.location.pathname.includes('/formData.html')){
        requestLocationAccuracy();
        getMapLocation();
        setInterval('getMapLocation()',300000);
    }
    if(document.location.pathname.includes('/modal.html')){
        requestLocationAccuracy();
        getMapLocation();
        setInterval('getMapLocation()',300000);
    }
    if(document.location.pathname.includes('/smodal.html')){
        requestLocationAccuracy();
        getMapLocation();
        setInterval('getMapLocation()',300000);
    }
    if(document.location.pathname.includes('/formDatas.html')){
        requestLocationAccuracy();
        getMapLocation();
        setInterval('getMapLocation()',300000);
    }
}
var onMapSuccess = function (position){
    Latitude = position.coords.latitude;
    Longitude = position.coords.longitude;

    var ex = window.localStorage.getItem("ExternalID");
    var idusuario = window.localStorage.getItem("id");
    var externalid = ex;
    
    var RegPoint = localStorage.getItem('RegPoint');
    console.log(RegPoint);
    var route = RegPoint+idusuario+"/"+externalid+"/"+Latitude+"/"+Longitude+"/4"
    console.log(route);
    $.ajax({
        url: route,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            console.log(data);
        },
        error: function (data) {
            console.log(data);
        }
    });
}
function onError(error) {
    console.error("The following error occurred: " + error);
}
function handleLocationAuthorizationStatus(status) {
    switch (status) {
        case cordova.plugins.diagnostic.permissionStatus.GRANTED:
            if(platform === "ios"){
                onError("Los servicios de ubicación ya están activados");
            }else{
                _makeRequest();
            }
            break;
        case cordova.plugins.diagnostic.permissionStatus.NOT_REQUESTED:
            requestLocationAuthorization();
            break;
        case cordova.plugins.diagnostic.permissionStatus.DENIED:
            if(platform === "android"){
                onError("Usuario denegado permiso para usar la ubicación");
            }else{
                _makeRequest();
            }
            break;
        case cordova.plugins.diagnostic.permissionStatus.DENIED_ALWAYS:
            // Android only
            onError("Usuario denegado permiso para usar la ubicación");
            break;
        case cordova.plugins.diagnostic.permissionStatus.GRANTED_WHEN_IN_USE:
            // iOS only
            onError("Los servicios de ubicación ya están activados");
            break;
    }
}

function requestLocationAuthorization() {
    cordova.plugins.diagnostic.requestLocationAuthorization(handleLocationAuthorizationStatus, onError);
}

function requestLocationAccuracy() {
    cordova.plugins.diagnostic.getLocationAuthorizationStatus(handleLocationAuthorizationStatus, onError);
}

function _makeRequest(){
    cordova.plugins.locationAccuracy.canRequest(function(canRequest){
        if (canRequest) {
            cordova.plugins.locationAccuracy.request(function () {
                    console.info("Solicitud de precisión de ubicación exitosa");
                }, function (error) {
                    onError("Error al solicitar la precisión de la ubicación:" + JSON.stringify(error));
                    if (error) {
                        // Android only
                        onError("error code=" + error.code + "; error message=" + error.message);
                    }
                }, cordova.plugins.locationAccuracy.REQUEST_PRIORITY_HIGH_ACCURACY // iOS will ignore this
            );
        } else {
            // On iOS, this will occur if Location Services is currently on OR a request is currently in progress.
            // On Android, this will occur if the app doesn't have authorization to use location.
            onError("No se puede solicitar la precisión de la ubicación");
        }
    });
}

