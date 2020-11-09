var gforms = window.openDatabase("gforms","1.0","DB de Gforms",10000000000);
var catalogos = window.openDatabase("catalogos", "1.0", "catalogos de Gforms", 10000000000);

var db = {
    initialize: function(){
        this.createTables();
    },
    createTables: function(){
        var forms= 'CREATE TABLE IF NOT EXISTS formularios (id INTEGER PRIMARY KEY AUTOINCREMENT,form_id INTEGER, for_codcia TEXT, esquema TEXT,nombre TEXT,version TEXT,descripcion TEXT,usuario TEXT,proceso TEXT,icon TEXT,idflujo INTEGER)';
        var datos = 'CREATE TABLE IF NOT EXISTS datos (id INTEGER PRIMARY KEY AUTOINCREMENT, form_id INTEGER,external_id TEXT, data TEXT,fechasig TEXT, estado TEXT, usuario TEXT,status TEXT)';
        var asig = 'CREATE TABLE IF NOT EXISTS asig (id INTEGER PRIMARY KEY AUTOINCREMENT, form_id INTEGER,external_id TEXT, data TEXT,fechasig TEXT, estado TEXT, usuario TEXT,status TEXT)';
        var asFin = 'CREATE TABLE IF NOT EXISTS asigFin (id INTEGER PRIMARY KEY AUTOINCREMENT, form_id INTEGER,external_id TEXT, data TEXT,fechasig TEXT, estado TEXT, usuario TEXT,status TEXT)';
        var depa = 'CREATE TABLE IF NOT EXISTS departamentos (id INTEGER PRIMARY KEY AUTOINCREMENT, dep_codigo INTEGER, dep_descripcion TEXT)';
        var muni = 'CREATE TABLE IF NOT EXISTS municipios (id INTEGER PRIMARY KEY AUTOINCREMENT, mun_depcod INTEGER, mun_codigo INTEGER, mun_descripcion TEXT)';
        var alde = 'CREATE TABLE IF NOT EXISTS aldeas (id INTEGER PRIMARY KEY AUTOINCREMENT, ald_depcod INTEGER, ald_muncod INTEGER, ald_codigo INTEGER, ald_descripcion TEXT)';
        var prod = 'CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY AUTOINCREMENT, Pro_Codigo INTEGER, Pro_Nombre TEXT, pro_codcia INTEGER, Pro_Estado TEXT)';
        var subpro = 'CREATE TABLE IF NOT EXISTS subproductos (id INTEGER PRIMARY KEY AUTOINCREMENT, Sub_CodPro INTEGER, Sub_Codigo INTEGER, Sub_Nombre TEXT, Sub_Estado TEXT)';
        var act = 'CREATE TABLE IF NOT EXISTS actividad_economica(id INTEGER PRIMARY KEY AUTOINCREMENT,acte_codsece INTEGER,acte_codigo TEXT,acte_descripcion TEXT,acte_estado TEXT)';
        var sec = 'CREATE TABLE IF NOT EXISTS sector_economico(id INTEGER PRIMARY KEY AUTOINCREMENT, sece_Codigo TEXT,sece_descripcion TEXT,sece_codcia TEXT,sece_estado TEXT,sece_adicionales TEXT,des_estado TEXT)';
        var geo = 'CREATE TABLE IF NOT EXISTS geo(id INTEGER PRIMARY KEY,usuario TEXT, latitude TEXT,longitude TEXT,externalid text)';
        var daux = 'CREATE TABLE IF NOT EXISTS daux (id INTEGER PRIMARY KEY AUTOINCREMENT, form_id INTEGER, external_id TEXT, external TEXT, data TEXT,fechasig TEXT, estado TEXT, usuario TEXT,status TEXT)';
        var flu = 'CREATE TABLE IF NOT EXISTS flujos (id INTEGER, flu_descripcion TEXT, flu_estado INTEGER)';
        var seg = 'CREATE TABLE IF NOT EXISTS seguimiento (id INTEGER PRIMARY KEY AUTOINCREMENT, form_id INTEGER,external_id TEXT, data TEXT,fechasig TEXT, estado TEXT, usuario TEXT,status TEXT)';

        this.transactionGforms(forms);
        this.transactionGforms(datos);
        this.transactionGforms(asig);
        this.transactionGforms(asFin);
        this.transactionGforms(geo);
        this.transactionGforms(daux);
        this.transactionGforms(flu);
        this.transactionGforms(seg);

        this.transactionCatalogos(depa);
        this.transactionCatalogos(muni);
        this.transactionCatalogos(alde);
        this.transactionCatalogos(prod);
        this.transactionCatalogos(subpro);
        this.transactionCatalogos(act);
        this.transactionCatalogos(sec);
    },
    transactionGforms: function(query){
        gforms.transaction(function (tx) {
            tx.executeSql(query);
        }, function (error) {
            console.log('transaction dbGforms error: ' + error.message);
        }, function () {
            console.log('Tablas Creadas en dbGforms!!');
        });
    },
    transactionCatalogos: function(query){
        catalogos.transaction(function (tx) {
            tx.executeSql(query);
        }, function (error) {
            console.log('transaction dbCatalogos error: ' + error.message);
        }, function () {
            console.log('Tablas Creadas en dbCatalogos!!');
        });
    },
    truncateFull: function(){
        var forms = 'DELETE FROM formularios';
        this.transactionDelete(gforms,forms);
    },
    trucateCatalogos: function(){
        var depa = "DELETE FROM departamentos";
        var muni = "DELETE FROM municipios";
        var prod = "DELETE FROM productos";
        var subpro = "DELETE FROM subproductos";
        var act = "DELETE FROM actividad_economica";
        var sec = "DELETE FROM sector_economico";
        var flu = "DELETE FROM flujos";

        this.transactionDelete(catalogos,depa);
        this.transactionDelete(catalogos,muni);
        this.transactionDelete(catalogos,prod);
        this.transactionDelete(catalogos,subpro);
        this.transactionDelete(catalogos,act);
        this.transactionDelete(catalogos,sec);
        this.transactionDelete(gforms,flu);
    },
    ultimos: function(){
        var query2 = "DELTE from daux where external NOT IN(select external_id from datos ORDER BY  id DESC LIMIT 3)";
        var query = "DELTE from datos where external_id NOT IN(select external_id from datos ORDER BY  id DESC LIMIT 3)";
        this.transactionDelete(gforms,query2);
        this.transactionDelete(gforms,query);
    },
    trucateAldeas:function(){
        var alde = "DELETE FROM aldeas";
        this.transactionDelete(catalogos,alde);
    },
    transactionDelete: function(db,query){
        db.transaction(function(tx) {
            tx.executeSql(query, [], function(tx, result) {
                console.info(result.rowsAffected+' Registros Eliminados! '+query);
            }, function(tx, error) {
                console.log(error);
            });
        }, this.transError, this.transSuccess);
    },
    transError: function(t,e){
        console.error("Error Ocurrido ! Codigo:" + e.code + " Mensaje : " + e.message);
    },
    transSuccess: function(t,r){
        console.info("Transaccion Completa!");
    }
};

