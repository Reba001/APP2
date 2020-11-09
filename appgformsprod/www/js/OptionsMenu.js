function menu(){
    // crea un nuevo div 
    // y añade contenido 
    var jsonMenu ={
        "menu": [
          {
            "texto": "Inicio",
            "class":"menu-item active-menu",
            "icono": "fa gradient-green-light fa-home",
            "data-menu":"",
            "data-menu-type":"",
            "funcion": "ruta.pagina('formularios.html');"
          },
          {
            "texto": "Chat",
            "class":"menu-item",
            "icono": "fa gradient-mint-dark fa-comment",
            "data-menu-type":"",
            "funcion": "ruta.pagina('chat2.html');"
          },
          {
            "texto": "Ajustes",
            "class":"menu-item",
            "icono": "fa gradient-sky-light fa-cog",
            "data-menu-type":"",
            "funcion": "ruta.pagina('sistema.html');"
          },
          {
            "texto": "Cerrar sesión",
            "class":"menu-item",
            "icono": "fa gradient-sky-dark fa-envelope",
            "data-menu":"",
            "data-menu-type":"",
            "funcion": "logout();"
          }
        ]
      };

    var usuario = localStorage.getItem("login");
    
    var div1 = document.createElement("div");
    var mscroll = document.createElement("div");
    var mheader = document.createElement("div");
    var alogo = document.createElement("a");
    var h1 = document.createElement("h1");
    var p1 = document.createElement("p");
    var div2 = document.createElement("div");
    var vm = document.createElement("em");
    var em = document.createElement("em");
    
    var i = document.createElement("i");

    var  h1C = document.createTextNode("Bienvenido");
    var  p1C = document.createTextNode(usuario);
    var  vc = document.createTextNode("Version: "+AppVersion.version);
    // var  vc = document.createTextNode("Version: ");
    var  emC = document.createTextNode("Navegación");
    

    div1.setAttribute("class","menu-bg gradient-body-8");
    mscroll.setAttribute("class","menu-scroll");
    mheader.setAttribute("class","menu-header");
    alogo.setAttribute("class","menu-logo");
    div2.setAttribute("class","menu-list icon-background-active");
    vm.setAttribute("class","menu-divider top-10");
    em.setAttribute("class","menu-divider top-10");
    
    i.setAttribute("class","fa gradient-green-light fa-home");

    alogo.setAttribute("href","index.html");

    document.getElementById("menu-1").appendChild(div1);
    document.getElementById("menu-1").appendChild(mscroll);
    document.getElementById("menu-1").appendChild(mheader);
    document.getElementById("menu-1").appendChild(div2);
    
    
    h1.appendChild(h1C);
    p1.appendChild(p1C);
    vm.appendChild(vc);
    em.appendChild(emC);
    

    mheader.appendChild(alogo);
    mheader.appendChild(h1);
    mheader.appendChild(p1);
    
    div2.appendChild(em);
    
    
    // añade el elemento creado y su contenido al DOM 
    for(var i in jsonMenu.menu){
        var a = document.createElement("a");
        var icono = document.createElement("i");

        var ac = document.createTextNode(jsonMenu.menu[i].texto);

        a.setAttribute("class",jsonMenu.menu[i].class);
        icono.setAttribute("class",jsonMenu.menu[i].icono);
        
        if(jsonMenu.menu[i].funcion !=""){
            a.setAttribute("onclick",jsonMenu.menu[i].funcion);
        }
        if(jsonMenu.menu[i]["data-menu"]!=""){
            a.setAttribute("data-menu",jsonMenu.menu[i]["data-menu"]);
        }
        if(jsonMenu.menu[i]["data-menu-type"] != ""){
            a.setAttribute("data-menu-type",jsonMenu.menu[i]["data-menu-type"]);
        }

        a.appendChild(icono);
        a.appendChild(ac);
        div2.appendChild(a);
    }
    div2.appendChild(vm);
}

function ruta(pagina){
  window.location=pagina;
}
