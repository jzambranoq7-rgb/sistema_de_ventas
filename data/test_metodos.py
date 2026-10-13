import os
from models import Cliente, Producto, Venta
from views import ClienteController, ProductoController, VentaController


def limpiar_archivos_prueba():
    for ruta in ("data/clientes.json", "data/productos.json", "data/ventas.json"):
        if os.path.exists(ruta):
            os.remove(ruta)


def ejecutar_pruebas():
    limpiar_archivos_prueba()

    # 1. Modelos, herencia y polimorfismo
    cli_m = Cliente(1, "Ana", "Perez", "ana@x.com", "0991234567", "Guayaquil")
    pro_m = Producto(1, "Teclado", 25.5, 6)
    ven_m = Venta(1, 1, 1, 2, 25.5)

    assert hasattr(cli_m, "id") and cli_m.nombre_completo() == "Ana Perez"
    assert "Guayaquil" in cli_m.etiqueta()
    assert "Teclado" in pro_m.etiqueta()
    assert ven_m.calcular_total() == 51.0

    # 2. Métodos estáticos y de clase
    assert Producto.es_precio_valido(10) is True
    assert Producto.es_precio_valido(-5) is False
    assert Producto.con_iva(100) == 115.0

    d = {"id": 2, "nombre": "Mouse", "precio": 12.0, "stock": 4}
    p_obj = Producto.desde_diccionario(d)
    assert isinstance(p_obj, Producto) and p_obj.stock_bajo() is True

    # 3. ClienteController
    ctrl_c = ClienteController("data/clientes.json")
    ok, _ = ctrl_c.crear({
        "nombre": "Ana", "apellido": "Perez",
        "email": "ana@x.com", "telefono": "0991234567", "ciudad": "Guayaquil"
    })
    assert ok is True
    ok_dup, _ = ctrl_c.crear({
        "nombre": "Luis", "apellido": "Mora",
        "email": "ana@x.com", "telefono": "0987654321", "ciudad": "Quito"
    })
    assert ok_dup is False

    # 4. ProductoController
    ctrl_p = ProductoController("data/productos.json")
    ok_p, _ = ctrl_p.crear({"nombre": "Teclado", "precio": 25.5, "stock": 6})
    assert ok_p is True
    ok_p_dup, _ = ctrl_p.crear({"nombre": "Teclado", "precio": 30.0, "stock": 2})
    assert ok_p_dup is False

    # 5. VentaController
    ctrl_v = VentaController(ctrl_c, ctrl_p, "data/ventas.json")
    ok_v, _ = ctrl_v.crear({"cliente_id": 1, "producto_id": 1, "cantidad": 2})
    assert ok_v is True
    assert ctrl_p.obtener(1).stock == 4

    ok_v_sin_stock, _ = ctrl_v.crear({"cliente_id": 1, "producto_id": 1, "cantidad": 99})
    assert ok_v_sin_stock is False

    cert = ctrl_v.comprobante(1)
    assert "Ana Perez" in cert and "Teclado" in cert and "58.65" in cert

    ok_anul, _ = ctrl_v.eliminar(1)
    assert ok_anul is True
    assert ctrl_p.obtener(1).stock == 6

    print("TODAS LAS PRUEBAS DEL SISTEMA DE VENTAS PASARON EXITOSAMENTE")


if __name__ == "__main__":
    ejecutar_pruebas()