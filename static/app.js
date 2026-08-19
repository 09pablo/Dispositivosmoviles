const API = "";

const elListaProductos = document.getElementById("lista-productos");
const elListaCarrito = document.getElementById("lista-carrito");
const elTotalCarrito = document.getElementById("total-carrito");
const elMensajeCarrito = document.getElementById("mensaje-carrito");
const elMensajeRegistrar = document.getElementById("mensaje-registrar");
const formRegistrar = document.getElementById("form-registrar");
const btnToggleForm = document.getElementById("btn-toggle-form");
const btnFinalizar = document.getElementById("btn-finalizar");

btnToggleForm.addEventListener("click", () => {
  formRegistrar.classList.toggle("hidden");
});

async function cargarProductos() {
  const res = await fetch(`${API}/productos`);
  const productos = await res.json();

  elListaProductos.innerHTML = "";
  if (productos.length === 0) {
    elListaProductos.innerHTML = '<p class="vacio">No hay productos registrados todavia.</p>';
    return;
  }

  for (const producto of productos) {
    const div = document.createElement("div");
    div.className = "producto";
    div.innerHTML = `
      <h3>${producto.nombre}</h3>
      <div class="precio">$${producto.precio.toFixed(2)}</div>
      <div class="stock">Stock: ${producto.stock}</div>
      <div class="fila-agregar">
        <input type="number" min="1" max="${producto.stock}" value="1" ${producto.stock === 0 ? "disabled" : ""} />
        <button type="button" ${producto.stock === 0 ? "disabled" : ""}>Agregar</button>
      </div>
    `;

    const input = div.querySelector("input");
    const boton = div.querySelector("button");
    boton.addEventListener("click", () => agregarAlCarrito(producto.id, Number(input.value)));

    elListaProductos.appendChild(div);
  }
}

async function agregarAlCarrito(productoId, cantidad) {
  elMensajeCarrito.textContent = "";
  const res = await fetch(`${API}/carrito`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ producto_id: productoId, cantidad }),
  });
  const datos = await res.json();

  if (!res.ok) {
    elMensajeCarrito.textContent = datos.error || "No se pudo agregar el producto.";
    elMensajeCarrito.className = "mensaje error";
    return;
  }

  await Promise.all([cargarProductos(), cargarCarrito()]);
}

async function cargarCarrito() {
  const res = await fetch(`${API}/carrito`);
  const datos = await res.json();

  elListaCarrito.innerHTML = "";
  if (datos.items.length === 0) {
    elListaCarrito.innerHTML = '<p class="vacio">El carrito esta vacio.</p>';
  } else {
    for (const item of datos.items) {
      const div = document.createElement("div");
      div.className = "item-carrito";
      div.innerHTML = `<span>${item.nombre} x${item.cantidad}</span><span>$${item.subtotal.toFixed(2)}</span>`;
      elListaCarrito.appendChild(div);
    }
  }

  elTotalCarrito.textContent = datos.total.toFixed(2);
}

btnFinalizar.addEventListener("click", async () => {
  const total = elTotalCarrito.textContent;
  const confirmado = window.confirm(`¿Seguro que quieres pagar el carrito? Total: $${total}`);
  if (!confirmado) return;

  elMensajeCarrito.textContent = "";
  const res = await fetch(`${API}/carrito/finalizar`, { method: "POST" });
  const datos = await res.json();

  if (!res.ok) {
    elMensajeCarrito.textContent = datos.error || "No se pudo finalizar la compra.";
    elMensajeCarrito.className = "mensaje error";
    return;
  }

  elMensajeCarrito.textContent = `${datos.mensaje}. Total pagado: $${datos.total.toFixed(2)}`;
  elMensajeCarrito.className = "mensaje exito";
  await cargarCarrito();
});

formRegistrar.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  elMensajeRegistrar.textContent = "";

  const nombre = document.getElementById("nombre").value.trim();
  const precio = document.getElementById("precio").value;
  const stock = document.getElementById("stock").value || 0;

  const res = await fetch(`${API}/productos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, precio, stock }),
  });
  const datos = await res.json();

  if (!res.ok) {
    elMensajeRegistrar.textContent = datos.error || "No se pudo registrar el producto.";
    elMensajeRegistrar.className = "mensaje error";
    return;
  }

  elMensajeRegistrar.textContent = `Producto "${datos.nombre}" registrado correctamente.`;
  elMensajeRegistrar.className = "mensaje exito";
  formRegistrar.reset();
  document.getElementById("stock").value = 0;
  await cargarProductos();
});

cargarProductos();
cargarCarrito();
