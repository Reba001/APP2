var db = window.openDatabase("gforms", "1.0", "DB de Gforms", 1000000); 
var app = {
    // Application Constructor
    initialize: function() {
        this.bindEvents();
    },
    // Bind Event Listeners
    // Enlazar los eventos que se requieren en el inicio. Los eventos comunes son:
    // 'load', 'deviceready', 'offline' y 'online'.
    bindEvents: function() {
        app.onDeviceReady();
    },
    // Deviceready Event Handler
    //
    // El alcance de 'este' es el evento. Para llamar al 'recibidoEvento'
    // función, debemos llamar explícitamente 'app.receivedEvent (...);'
    onDeviceReady: function() {
        app.receivedEvent('deviceready');
    },
    // Actualizar DOM en un evento recibido
    receivedEvent: function(id) {
       app.CreateTables();
    },
    CreateTables: function(){
        // Create Table
        db.transaction(this.formularios, this.errorCB, this.successTB("formularios"));//creación de la tabla formularios
        db.transaction(this.actividadEconomica, this.errorCB, this.successTB("actividad economica"));//creación de la tabla actividad economica
        db.transaction(this.destinoCredito, this.errorCB, this.successTB("destino credito"));//creación de la tabla destino de credito   
        app.insertData();
    },
    /***********Función de errores************/
    errorCB: function(err) {
        alert("Error procesando SQL: "+err.message);
    },
    successCB: function() {
        alert("Creación db Completa!");
    },
    successTB: function(tb) {
     alert("Creación de Tabla "+tb+" Completa!");
    },
    successIs: function(){
     alert("Sincronización completa!");
    },
    /**************Fin de errores**************/
    /*************Creación de tablas ****************/
    formularios: function(tx){
        tx.executeSql('CREATE TABLE IF NOT EXISTS formularios (id INTEGER PRIMARY KEY AUTOINCREMENT,datos TEXT,esquema TEXT,opciones TEXT,vista TEXT,nombre TEXT,version TEXT,descripcion TEXT,img TEXT)');
    },
    actividadEconomica: function(tx){
        tx.executeSql("CREATE TABLE IF NOT EXISTS actividad_economica(id INTEGER PRIMARY KEY AUTOINCREMENT,acte_codsece INTEGER,acte_codigo TEXT,acte_descripcion TEXT,acte_estado TEXT)")
    },
    destinoCredito: function(tx){
       tx.executeSql("CREATE TABLE IF NOT EXISTS destino_credito(id INTEGER PRIMARY KEY AUTOINCREMENT, des_codigo TEXT,des_descripcion TEXT,des_estado TEXT)")
    },
    /****************Fin de cración de tablas**************/
    /***********Inserción de datos en las tablas**********/
    insertData: function(){
        this.apiForm();
        
    },
    apiForm: function(){
        alert("Consultando api");
        $.getJSON("https://pagina.craftygt.ga/api/formularios",function(result){
            alert(result);
            for (x=0; x < result.length; x++) { 
                alert(result['nombre']);
            }
        }
        /*
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": "https://pagina.craftygt.ga/api/formularios",
            "method": "GET",
            "headers": {
                "cache-control": "no-cache",
                "Postman-Token": "78220e21-ebca-427d-8cae-2912960da2f1"
                }
        }
 
        $.ajax(settings).done(function (response) {
            alert("empezando a consultar api");
            var obj = response.data;
            var html ="";
            alert(response.data);
            for (var valor of obj) {
                alert(valor.datos,valor.esquema,valor.opciones,valor.vista,valor.nombre,valor.version,valor.descripcion,valor.img);
                db.transaction(this.insertForm(tx,valor.datos,valor.esquema,valor.opciones,valor.vista,valor.nombre,valor.version,valor.descripcion,valor.img), this.errorCB, this.successIs);
            }
            alert("Finalizo insersión");
        }
        );*/  
    },
    insertForm: function(tx,datos,esquema,opciones,vista,nombre,version,descripcion,img){

        alert(datos,esquema,opciones,vista,nombre,version,descripcion,img);
        tx.executeSql("INSERT INTO formularios(datos,esquema,opciones,vista,nombre,version,descripcion,img) VALUES (?,?,?,?,?,?,?,?)",[datos],[esquema],[opciones],[vista],[nombre],[version],[descripcion],[img]);
        alert("Finalizo insersión");
    },
   /**************Fin de insersion de datos******************/
 
   /***********Funciones para obtención de datos********************/
    getFormularios: function(){
        alert("Empezo a obtener los datos");
        db.transaction(function(tx){
   
        tx.executeSql("select * from formularios",[],function(tx1,result){
        var len = result.rows.length;
   
        for (var i=0; i<len; i++){
            html += "<li onclick='ver("+result.rows.item(i).id+")'>Nombre: "+result.rows.item(i).nombre+"<br/> Tipo: <br/><div class='right top'>Version: "+result.rows.item(i).version+"</div></li>";
            alert(html);
        }
  
        document.getElementById("formularios").innerHTML =html;
  
        },errorCB);
        }, errorCB, successCB);
    }
    /******************Fin de funciones*******************/
 
};
