const API = "";

const elListaProductos = document.getElementById("lista-productos");
const elMensajeRegistrar = document.getElementById("mensaje-registrar");
const formRegistrar = document.getElementById("form-registrar");
const btnToggleForm = document.getElementById("btn-toggle-form");

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
    `;
    elListaProductos.appendChild(div);
  }
}

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
