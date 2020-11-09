function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function getFecha(){
    var f = new Date();
    document.write(f.getDate() + "/" + (f.getMonth() +1) + "/" + f.getFullYear());
    return f.getDate() + "/" + (f.getMonth() +1) + "/" + f.getFullYear();    
}

function goback(){   
    window.history.back();
    // window.history.go(-1);
}   

function verificacion(){
    if(navigator.onLine) {
        return true
    } else {
        Swal.fire({
            type: 'error',
            title: 'Sin Conexión',
            text: 'Comprueba tu conexión a internet y vuelve a intentarlo mas tarde!.',
          })
    }
}

function ruta(pagina){
    window.location=pagina;
}


