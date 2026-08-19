"""API REST de la mini tienda: registrar productos y consultar productos disponibles."""

from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="static", static_url_path="")


class Producto:
    _contador = 0

    def __init__(self, nombre, precio, stock=0):
        Producto._contador += 1
        self.id = Producto._contador
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }


class ItemCarrito:
    def __init__(self, producto, cantidad):
        self.producto = producto
        self.cantidad = cantidad

    @property
    def subtotal(self):
        return round(self.producto.precio * self.cantidad, 2)

    def to_dict(self):
        return {
            "producto_id": self.producto.id,
            "nombre": self.producto.nombre,
            "precio": self.producto.precio,
            "cantidad": self.cantidad,
            "subtotal": self.subtotal,
        }


class Tienda:
    def __init__(self):
        self.productos = []
        self.carrito = []

    def registrar_producto(self, nombre, precio, stock):
        producto = Producto(nombre, precio, stock)
        self.productos.append(producto)
        return producto

    def buscar_producto(self, producto_id):
        for producto in self.productos:
            if producto.id == producto_id:
                return producto
        return None

    def agregar_al_carrito(self, producto, cantidad):
        if cantidad > producto.stock:
            raise ValueError("No hay suficiente stock disponible")
        for item in self.carrito:
            if item.producto is producto:
                item.cantidad += cantidad
                producto.stock -= cantidad
                return item
        item = ItemCarrito(producto, cantidad)
        self.carrito.append(item)
        producto.stock -= cantidad
        return item

    def total_carrito(self):
        return round(sum(item.subtotal for item in self.carrito), 2)

    def finalizar_compra(self):
        total = self.total_carrito()
        items = [item.to_dict() for item in self.carrito]
        self.carrito = []
        return total, items


tienda = Tienda()
tienda.registrar_producto("Camiseta", 15.99, 10)
tienda.registrar_producto("Pantalon", 29.99, 5)
tienda.registrar_producto("Zapatos", 45.50, 3)


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Recurso no encontrado"}), 404


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api")
def api_info():
    return jsonify({
        "mensaje": "API mini tienda",
        "endpoints": {
            "GET /productos": "ver productos disponibles",
            "GET /productos/<id>": "ver un producto",
            "POST /productos": "registrar producto (nombre, precio obligatorios)",
            "POST /carrito": "agregar producto al carrito (producto_id, cantidad)",
            "GET /carrito": "ver carrito y total",
            "POST /carrito/finalizar": "finalizar compra",
        },
    })


# Ver productos disponibles
@app.get("/productos")
def ver_productos():
    return jsonify([p.to_dict() for p in tienda.productos])


@app.get("/productos/<int:producto_id>")
def ver_producto(producto_id):
    producto = tienda.buscar_producto(producto_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(producto.to_dict())


# Registrar producto (nombre y precio obligatorios)
@app.post("/productos")
def registrar_producto():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    precio = datos.get("precio")
    stock = datos.get("stock", 0)

    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    try:
        precio = float(precio)
    except (TypeError, ValueError):
        return jsonify({"error": "El precio es obligatorio y debe ser numerico"}), 400
    if precio <= 0:
        return jsonify({"error": "El precio debe ser mayor a 0"}), 400
    try:
        stock = int(stock)
    except (TypeError, ValueError):
        return jsonify({"error": "El stock debe ser un numero entero"}), 400
    if stock < 0:
        return jsonify({"error": "El stock no puede ser negativo"}), 400

    producto = tienda.registrar_producto(nombre, precio, stock)
    return jsonify(producto.to_dict()), 201


# Agregar producto al carrito
@app.post("/carrito")
def agregar_al_carrito():
    datos = request.get_json(silent=True) or {}
    producto_id = datos.get("producto_id")
    cantidad = datos.get("cantidad")

    try:
        producto_id = int(producto_id)
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        return jsonify({"error": "producto_id y cantidad son obligatorios y deben ser numeros"}), 400
    if cantidad <= 0:
        return jsonify({"error": "La cantidad debe ser mayor a 0"}), 400

    producto = tienda.buscar_producto(producto_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    try:
        item = tienda.agregar_al_carrito(producto, cantidad)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(item.to_dict()), 201


# Mostrar productos del carrito y calcular el total
@app.get("/carrito")
def ver_carrito():
    return jsonify({
        "items": [item.to_dict() for item in tienda.carrito],
        "total": tienda.total_carrito(),
    })


# Finalizar la compra
@app.post("/carrito/finalizar")
def finalizar_compra():
    if not tienda.carrito:
        return jsonify({"error": "El carrito esta vacio"}), 400
    total, items = tienda.finalizar_compra()
    return jsonify({"mensaje": "Compra realizada con exito", "items": items, "total": total})


if __name__ == "__main__":
    from waitress import serve

    print("Servidor de produccion (waitress) corriendo en http://127.0.0.1:5000")
    serve(app, host="127.0.0.1", port=5000)
