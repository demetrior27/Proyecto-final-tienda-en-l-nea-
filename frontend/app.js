const API = "http://127.0.0.1:8000";
let token = localStorage.getItem("token") || "";
let usuarioActual = JSON.parse(localStorage.getItem("usuario") || "null");

function limpiar(el) {
    while (el.firstChild) el.removeChild(el.firstChild);
}

function notificar(texto) {
    const n = document.getElementById("notificacion");
    n.textContent = texto;
    n.classList.remove("oculto");
    setTimeout(() => n.classList.add("oculto"), 3200);
}

function mostrarVista(idVista) {
    document.querySelectorAll(".vista").forEach(v => v.classList.add("oculto"));
    document.getElementById(idVista).classList.remove("oculto");
}

function actualizarUIUsuario() {
    const badge = document.getElementById("user-badge");
    const btnAdmin = document.getElementById("nav-admin");
    const btnLogout = document.getElementById("btn-logout");
    const btnAuth = document.getElementById("nav-auth");

    if (usuarioActual && token) {
        badge.textContent = `${usuarioActual.nombre} (${usuarioActual.rol})`;
        btnLogout.classList.remove("oculto");
        btnAuth.classList.add("oculto");
        if (usuarioActual.rol === "admin") btnAdmin.classList.remove("oculto");
        else btnAdmin.classList.add("oculto");
    } else {
        badge.textContent = "Invitado";
        btnAdmin.classList.add("oculto");
        btnLogout.classList.add("oculto");
        btnAuth.classList.remove("oculto");
    }
}

// Crear tarjeta de producto sin usar innerHTML
function crearCardProducto(p) {
    const card = document.createElement("article");
    card.className = "card-prod";

    const img = document.createElement("img");
    img.src = p.imagen.startsWith("http") ? p.imagen : `${API}${p.imagen}`;
    img.alt = p.nombre;

    const body = document.createElement("div");
    body.className = "card-body";

    const cat = document.createElement("span");
    cat.className = "stock-badge";
    cat.textContent = p.categoria_nombre;

    const title = document.createElement("h3");
    title.textContent = p.nombre;

    const desc = document.createElement("p");
    desc.textContent = p.descripcion;

    const precio = document.createElement("p");
    precio.className = "precio";
    precio.textContent = `$${Number(p.precio).toFixed(2)}`;

    const stock = document.createElement("p");
    stock.className = "stock-badge";
    stock.textContent = p.stock > 0 ? `Disponibles: ${p.stock}` : "Agotado";

    const btnDetalle = document.createElement("button");
    btnDetalle.className = "btn-pri";
    btnDetalle.textContent = "Ver Detalle";
    btnDetalle.addEventListener("click", () => abrirDetalleProducto(p.id));

    body.append(cat, title, desc, precio, stock, btnDetalle);

    if (usuarioActual && usuarioActual.rol === "admin") {
        const btnDel = document.createElement("button");
        btnDel.className = "btn-danger";
        btnDel.textContent = "Eliminar (Admin)";
        btnDel.addEventListener("click", async () => {
            await fetch(`${API}/productos/${p.id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            notificar("Producto eliminado");
            cargarCatalogo();
        });
        body.appendChild(btnDel);
    }

    card.append(img, body);
    return card;
}

// --- A. LANDING PAGE ---
async function cargarHome() {
    mostrarVista("vista-home");
    const [resAleatorios, resCats] = await Promise.all([
        fetch(`${API}/productos/aleatorios`),
        fetch(`${API}/categorias/`)
    ]);
    const aleatorios = await resAleatorios.json();
    const categorias = await resCats.json();

    const contAleatorios = document.getElementById("home-aleatorios");
    limpiar(contAleatorios);
    aleatorios.forEach(p => contAleatorios.appendChild(crearCardProducto(p)));

    const contCats = document.getElementById("home-categorias");
    limpiar(contCats);
    categorias.forEach(c => {
        const tag = document.createElement("span");
        tag.className = "tag-cat";
        tag.textContent = c.nombre;
        tag.addEventListener("click", () => {
            cargarCatalogo("", c.id);
        });
        contCats.appendChild(tag);
    });
}

// --- B. CATÁLOGO ---
async function cargarSelectCategorias() {
    const res = await fetch(`${API}/categorias/`);
    const cats = await res.json();

    const selectFiltro = document.getElementById("cat-filter-select");
    const selectAdmin = document.getElementById("prod-cat-select");
    limpiar(selectFiltro);
    limpiar(selectAdmin);

    const optTodos = document.createElement("option");
    optTodos.value = "";
    optTodos.textContent = "Todas las categorías";
    selectFiltro.appendChild(optTodos);

    cats.forEach(c => {
        const o1 = document.createElement("option");
        o1.value = c.id;
        o1.textContent = c.nombre;
        selectFiltro.appendChild(o1);

        const o2 = document.createElement("option");
        o2.value = c.id;
        o2.textContent = `${c.id} - ${c.nombre}`;
        selectAdmin.appendChild(o2);
    });
}

async function cargarCatalogo(buscar = "", categoria_id = "") {
    mostrarVista("vista-catalogo");
    await cargarSelectCategorias();

    const params = new URLSearchParams();
    if (buscar) params.append("buscar", buscar);
    if (categoria_id) params.append("categoria_id", categoria_id);

    const res = await fetch(`${API}/productos/?${params.toString()}`);
    const prods = await res.json();

    const grid = document.getElementById("catalogo-grid");
    limpiar(grid);
    if (prods.length === 0) {
        const vacio = document.createElement("p");
        vacio.textContent = "No se encontraron productos.";
        grid.appendChild(vacio);
        return;
    }
    prods.forEach(p => grid.appendChild(crearCardProducto(p)));
}

// --- C. DETALLE DEL PRODUCTO ---
async function abrirDetalleProducto(id) {
    mostrarVista("vista-detalle");
    const res = await fetch(`${API}/productos/${id}`);
    const p = await res.json();

    const cont = document.getElementById("detalle-contenedor");
    limpiar(cont);

    const img = document.createElement("img");
    img.src = p.imagen.startsWith("http") ? p.imagen : `${API}${p.imagen}`;

    const info = document.createElement("div");
    info.className = "card-body";

    const cat = document.createElement("p");
    cat.className = "stock-badge";
    cat.textContent = `Categoría: ${p.categoria_nombre} (ID Producto: ${p.id})`;

    const title = document.createElement("h2");
    title.textContent = p.nombre;

    const desc = document.createElement("p");
    desc.textContent = p.descripcion;

    const precio = document.createElement("p");
    precio.className = "precio";
    precio.textContent = `$${Number(p.precio).toFixed(2)}`;

    const stock = document.createElement("p");
    stock.textContent = `Stock disponible: ${p.stock}`;

    const inputCant = document.createElement("input");
    inputCant.type = "number";
    inputCant.min = "1";
    inputCant.max = p.stock;
    inputCant.value = "1";

    const btnAdd = document.createElement("button");
    btnAdd.className = "btn-sec";
    btnAdd.textContent = p.stock > 0 ? "Agregar al Carrito" : "Sin Stock";
    btnAdd.disabled = p.stock <= 0;
    btnAdd.addEventListener("click", async () => {
        if (!token) {
            notificar("Inicia sesión para agregar productos al carrito");
            mostrarVista("vista-auth");
            return;
        }
        const cant = parseInt(inputCant.value, 10);
        const r = await fetch(`${API}/carrito/items`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ producto_id: p.id, cantidad: cant })
        });
        if (r.ok) {
            notificar("Producto agregado al carrito");
            cargarCarrito();
        } else {
            const err = await r.json();
            notificar(err.detail || "Error al agregar");
        }
    });

    info.append(cat, title, desc, precio, stock, inputCant, btnAdd);
    cont.append(img, info);
}

// --- E. CARRITO ---
async function cargarCarrito() {
    if (!token) {
        notificar("Debes iniciar sesión para ver tu carrito");
        mostrarVista("vista-auth");
        return;
    }
    mostrarVista("vista-carrito");
    const res = await fetch(`${API}/carrito/`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await res.json();
    const lista = document.getElementById("carrito-lista");
    limpiar(lista);

    data.items.forEach(item => {
        const row = document.createElement("div");
        row.className = "item-row";

        const nombre = document.createElement("strong");
        nombre.textContent = `${item.nombre} ($${item.precio} c/u)`;

        const inputCant = document.createElement("input");
        inputCant.type = "number";
        inputCant.min = "1";
        inputCant.max = item.stock_disponible;
        inputCant.value = item.cantidad;
        inputCant.style.width = "80px";
        inputCant.addEventListener("change", async () => {
            await fetch(`${API}/carrito/items/${item.item_id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify({ cantidad: parseInt(inputCant.value, 10) })
            });
            cargarCarrito();
        });

        const sub = document.createElement("span");
        sub.textContent = `Subtotal: $${Number(item.subtotal).toFixed(2)}`;

        const btnDel = document.createElement("button");
        btnDel.className = "btn-danger";
        btnDel.textContent = "Quitar";
        btnDel.addEventListener("click", async () => {
            await fetch(`${API}/carrito/items/${item.item_id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });
            cargarCarrito();
        });

        row.append(nombre, inputCant, sub, btnDel);
        lista.appendChild(row);
    });

    document.getElementById("carrito-total").textContent = `Total: $${Number(data.total).toFixed(2)}`;
}

// --- F. MIS PEDIDOS ---
async function cargarMisPedidos() {
    if (!token) {
        notificar("Inicia sesión para consultar tus pedidos");
        mostrarVista("vista-auth");
        return;
    }
    mostrarVista("vista-pedidos");
    const res = await fetch(`${API}/pedidos/mis-pedidos`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    const pedidos = await res.json();
    const lista = document.getElementById("pedidos-lista");
    limpiar(lista);

    pedidos.forEach(ped => {
        const box = document.createElement("div");
        box.className = "card-form";

        const head = document.createElement("h3");
        head.textContent = `Pedido #${ped.id} | Fecha: ${ped.fecha} | Estado: ${ped.estado.toUpperCase()} | Total: $${Number(ped.total).toFixed(2)}`;
        box.appendChild(head);

        ped.items.forEach(i => {
            const p = document.createElement("p");
            p.textContent = `• ${i.nombre} x ${i.cantidad} ($${i.precio_unitario}) = $${i.subtotal}`;
            box.appendChild(p);
        });
        lista.appendChild(box);
    });
}

// --- G. ADMIN ---
async function cargarPanelAdmin() {
    mostrarVista("vista-admin");
    await cargarSelectCategorias();
    const res = await fetch(`${API}/pedidos/admin`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) return;
    const pedidos = await res.json();
    const lista = document.getElementById("admin-pedidos-lista");
    limpiar(lista);

    pedidos.forEach(ped => {
        const row = document.createElement("div");
        row.className = "item-row";

        const info = document.createElement("span");
        info.textContent = `Pedido #${ped.id} (${ped.usuario_email}) - Total: $${ped.total} - Estado actual: ${ped.estado}`;

        const selectEstado = document.createElement("select");
        selectEstado.style.width = "160px";
        ["pendiente", "procesando", "enviado", "entregado"].forEach(est => {
            const opt = document.createElement("option");
            opt.value = est;
            opt.textContent = est;
            if (ped.estado === est) opt.selected = true;
            selectEstado.appendChild(opt);
        });

        selectEstado.addEventListener("change", async () => {
            await fetch(`${API}/pedidos/${ped.id}/estado`, {
                method: "PUT",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify({ estado: selectEstado.value })
            });
            notificar(`Estado del pedido #${ped.id} actualizado`);
            cargarPanelAdmin();
        });

        row.append(info, selectEstado);
        lista.appendChild(row);
    });
}

// --- EVENTOS ---
document.getElementById("nav-home").addEventListener("click", cargarHome);
document.getElementById("nav-catalogo").addEventListener("click", () => cargarCatalogo());
document.getElementById("nav-carrito").addEventListener("click", cargarCarrito);
document.getElementById("nav-pedidos").addEventListener("click", cargarMisPedidos);
document.getElementById("nav-admin").addEventListener("click", cargarPanelAdmin);
document.getElementById("nav-auth").addEventListener("click", () => mostrarVista("vista-auth"));
document.getElementById("btn-volver-catalogo").addEventListener("click", () => cargarCatalogo());

document.getElementById("btn-logout").addEventListener("click", () => {
    token = "";
    usuarioActual = null;
    localStorage.clear();
    actualizarUIUsuario();
    notificar("Sesión cerrada");
    cargarHome();
});

document.getElementById("home-search-btn").addEventListener("click", () => {
    const q = document.getElementById("home-search-input").value.trim();
    cargarCatalogo(q, "");
});

document.getElementById("cat-filter-btn").addEventListener("click", () => {
    const q = document.getElementById("cat-search-input").value.trim();
    const cat = document.getElementById("cat-filter-select").value;
    cargarCatalogo(q, cat);
});

document.getElementById("cat-clear-btn").addEventListener("click", () => {
    document.getElementById("cat-search-input").value = "";
    document.getElementById("cat-filter-select").value = "";
    cargarCatalogo();
});

document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-pass").value;
    const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });
    if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        usuarioActual = data.usuario;
        localStorage.setItem("token", token);
        localStorage.setItem("usuario", JSON.stringify(usuarioActual));
        actualizarUIUsuario();
        notificar(`Bienvenido ${usuarioActual.nombre}`);
        cargarHome();
    } else {
        notificar("Credenciales incorrectas");
    }
});

document.getElementById("form-registro").addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
        nombre: document.getElementById("reg-nombre").value,
        email: document.getElementById("reg-email").value,
        password: document.getElementById("reg-pass").value,
        rol: document.getElementById("reg-rol").value
    };
    const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    if (res.ok) {
        notificar("Usuario registrado con éxito. Ahora inicia sesión.");
        e.target.reset();
    } else {
        notificar("Error: El correo ya está registrado.");
    }
});

document.getElementById("btn-confirmar-compra").addEventListener("click", async () => {
    const res = await fetch(`${API}/pedidos/`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
    });
    if (res.ok) {
        notificar("¡Pedido generado y stock descontado con éxito!");
        cargarMisPedidos();
    } else {
        const err = await res.json();
        notificar(err.detail || "No se pudo procesar el pedido");
    }
});

document.getElementById("form-categoria").addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
        nombre: document.getElementById("cat-nombre").value,
        descripcion: document.getElementById("cat-desc").value
    };
    const res = await fetch(`${API}/categorias/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify(body)
    });
    if (res.ok) {
        notificar("Categoría creada");
        e.target.reset();
        cargarSelectCategorias();
    }
});

document.getElementById("form-producto").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("prod-id").value;
    const body = {
        nombre: document.getElementById("prod-nombre").value,
        descripcion: document.getElementById("prod-desc").value,
        precio: parseFloat(document.getElementById("prod-precio").value),
        stock: parseInt(document.getElementById("prod-stock").value, 10),
        imagen: document.getElementById("prod-img").value,
        categoria_id: parseInt(document.getElementById("prod-cat-select").value, 10)
    };
    const url = id ? `${API}/productos/${id}` : `${API}/productos/`;
    const metodo = id ? "PUT" : "POST";
    const res = await fetch(url, {
        method: metodo,
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify(body)
    });
    if (res.ok) {
        notificar("Producto guardado correctamente");
        e.target.reset();
        cargarCatalogo();
    }
});

document.addEventListener("DOMContentLoaded", () => {
    actualizarUIUsuario();
    cargarHome();
});