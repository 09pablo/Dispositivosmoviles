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


class Tienda:
    def __init__(self):
        self.productos = []

    def registrar_producto(self, nombre, precio, stock):
        producto = Producto(nombre, precio, stock)
        self.productos.append(producto)
        return producto

    def buscar_producto(self, producto_id):
        for producto in self.productos:
            if producto.id == producto_id:
                return producto
        return None


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


if __name__ == "__main__":
    from waitress import serve

    print("Servidor de produccion (waitress) corriendo en http://127.0.0.1:5000")
    serve(app, host="127.0.0.1", port=5000)
