from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import ClienteController, ProductoController, VentaController, DevolucionController
from models import Devolucion

clientes = ClienteController()
productos = ProductoController()
ventas = VentaController(clientes, productos)
devoluciones = DevolucionController(ventas, productos, clientes)


def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENÚ CLIENTES
# =====================================================================

def crear_cliente():
    imprimir_titulo("CREAR CLIENTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "telefono": input("Teléfono: "),
        "ciudad": input("Ciudad: "),
    }
    mostrar_resultado(*clientes.crear(datos))
    pausa()


def listar_clientes():
    imprimir_titulo("CLIENTES")
    mostrar_lista(clientes.leer(), "Todavía no hay clientes.")
    pausa()


def buscar_cliente():
    imprimir_titulo("BUSCAR CLIENTE")
    termino = input("Nombre, email, teléfono o ciudad: ")
    encontrados = clientes.buscar(termino)
    mostrar_lista(encontrados, f"Ningún cliente coincide con '{termino}'.")
    pausa()


def ver_cliente():
    imprimir_titulo("VER CLIENTE POR ID")
    cliente = clientes.obtener(pedir_entero("Id: "))
    if cliente is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(cliente)
    pausa()


def actualizar_cliente():
    imprimir_titulo("ACTUALIZAR CLIENTE")
    id_cliente = pedir_entero("Id: ")
    cliente = clientes.obtener(id_cliente)
    if cliente is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {cliente.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "telefono", "ciudad"):
        actual = getattr(cliente, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*clientes.actualizar(id_cliente, cambios))
    pausa()


def eliminar_cliente():
    imprimir_titulo("ELIMINAR CLIENTE")
    id_cliente = pedir_entero("Id: ")
    cliente = clientes.obtener(id_cliente)
    if cliente is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {cliente.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*clientes.eliminar(id_cliente))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ PRODUCTOS
# =====================================================================

def crear_producto():
    imprimir_titulo("CREAR PRODUCTO")
    datos = {
        "nombre": input("Nombre: "),
        "precio": input("Precio: "),
        "stock": input("Stock: "),
    }
    mostrar_resultado(*productos.crear(datos))
    pausa()


def listar_productos():
    imprimir_titulo("PRODUCTOS")
    mostrar_lista(productos.leer(), "Todavía no hay productos.")
    pausa()


def buscar_producto():
    imprimir_titulo("BUSCAR PRODUCTO")
    termino = input("Nombre: ")
    mostrar_lista(productos.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_producto():
    imprimir_titulo("VER PRODUCTO POR ID")
    producto = productos.obtener(pedir_entero("Id: "))
    if producto is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(producto)
        imprimir_info(f"Precio con IVA: ${producto.con_iva(producto.precio):.2f}")
    pausa()


def actualizar_producto():
    imprimir_titulo("ACTUALIZAR PRODUCTO")
    id_producto = pedir_entero("Id: ")
    producto = productos.obtener(id_producto)
    if producto is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {producto.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "precio", "stock"):
        actual = getattr(producto, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*productos.actualizar(id_producto, cambios))
    pausa()


def eliminar_producto():
    imprimir_titulo("ELIMINAR PRODUCTO")
    id_producto = pedir_entero("Id: ")
    producto = productos.obtener(id_producto)
    if producto is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {producto.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*productos.eliminar(id_producto))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ VENTAS
# =====================================================================

def registrar_venta():
    imprimir_titulo("REGISTRAR VENTA")
    imprimir_info("Clientes:")
    mostrar_lista(clientes.leer())
    imprimir_info("Productos:")
    mostrar_lista(productos.leer())

    datos = {
        "cliente_id": pedir_entero("\nId del cliente: "),
        "producto_id": pedir_entero("Id del producto: "),
        "cantidad": pedir_entero("Cantidad: "),
    }
    if None in datos.values():
        imprimir_error("Todos los datos deben ser números enteros")
        return pausa()

    mostrar_resultado(*ventas.crear(datos))
    pausa()


def listar_ventas():
    imprimir_titulo("VENTAS")
    mostrar_lista(ventas.leer(), "Todavía no hay ventas.")
    pausa()


def ver_comprobante():
    imprimir_titulo("COMPROBANTE")
    texto = ventas.comprobante(pedir_entero("Id de la venta: "))
    if texto is None:
        imprimir_error("No existe esa venta")
    else:
        print(texto)
    pausa()


def anular_venta():
    imprimir_titulo("ANULAR VENTA")
    id_venta = pedir_entero("Id de la venta: ")
    if id_venta and confirmar("Se devolverá el stock. ¿Confirma?"):
        mostrar_resultado(*ventas.eliminar(id_venta))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DEVOLUCIONES
# =====================================================================

def crear_devolucion():
    imprimir_titulo("REGISTRAR DEVOLUCIÓN")
    id_venta = pedir_entero("Id de la venta / factura: ")
    if id_venta is None:
        imprimir_error("El ID debe ser un número entero")
        return pausa()

    venta = ventas.obtener(id_venta)
    if venta is None:
        imprimir_error(f"No existe ninguna venta con ID #{id_venta}")
        return pausa()

    cliente = clientes.obtener(venta.cliente_id)
    producto = productos.obtener(venta.producto_id)
    devueltas = devoluciones.cantidad_devuelta(id_venta)
    disponibles = devoluciones.cantidad_disponible(venta)

    imprimir_info(f"--- DETALLES DE LA VENTA #{venta.id} ---")
    print(f"  Fecha Venta     : {venta.fecha}")
    print(f"  Cliente         : {cliente.nombre_completo() if cliente else 'Desconocido'}")
    print(f"  Producto        : {producto.nombre if producto else 'Desconocido'} (Stock actual en tienda: {producto.stock if producto else 0})")
    print(f"  Precio Unitario : ${venta.precio_unitario:.2f}")
    print(f"  Comprados       : {venta.cantidad} | Ya devueltos: {devueltas} | Disponibles: {disponibles}\n")

    if disponibles <= 0:
        imprimir_error("Esta venta no tiene unidades disponibles para devolver.")
        return pausa()

    cantidad = pedir_entero(f"Cantidad a devolver (máx {disponibles}): ")
    if cantidad is None or cantidad <= 0:
        imprimir_error("Cantidad no válida")
        return pausa()

    print("\nSeleccione el motivo:")
    for i, m in enumerate(Devolucion.MOTIVOS, 1):
        info_regreso = "No reingresa a tienda" if m == "defectuoso" else "Reingresa al stock"
        print(f"  {i}. {m.capitalize()} ({info_regreso})")

    opcion_motivo = input("Opción de motivo: ").strip()
    if opcion_motivo.isdigit() and 1 <= int(opcion_motivo) <= len(Devolucion.MOTIVOS):
        motivo = Devolucion.MOTIVOS[int(opcion_motivo) - 1]
    else:
        motivo = opcion_motivo

    mostrar_resultado(*devoluciones.crear({
        "venta_id": id_venta,
        "cantidad": cantidad,
        "motivo": motivo
    }))
    pausa()


def consultar_devolucion():
    imprimir_titulo("CONSULTAR DEVOLUCIONES DE UNA VENTA")
    id_venta = pedir_entero("Id de la venta / factura: ")
    if id_venta is None:
        imprimir_error("El ID debe ser un número entero")
        return pausa()

    venta = ventas.obtener(id_venta)
    if venta is None:
        imprimir_error(f"No existe ninguna venta con ID #{id_venta}")
        return pausa()

    cliente = clientes.obtener(venta.cliente_id)
    producto = productos.obtener(venta.producto_id)
    lista_devs = devoluciones.devoluciones_de_venta(id_venta)

    imprimir_info(f"--- FACTURA #{venta.id} ---")
    print(f"  Cliente      : {cliente.nombre_completo() if cliente else 'Desconocido'}")
    print(f"  Producto     : {producto.nombre if producto else 'Desconocido'} (Stock actual: {producto.stock if producto else 0})")
    print(f"  Compradas    : {venta.cantidad}")
    print(f"  Devueltas    : {devoluciones.cantidad_devuelta(id_venta)}")
    print(f"  Disponibles  : {devoluciones.cantidad_disponible(venta)}\n")

    mostrar_lista(lista_devs, "Esta venta no tiene devoluciones registradas.")

    reembolsado_venta = round(sum(d.monto for d in lista_devs), 2)
    imprimir_info(f"Total reembolsado en esta venta: ${reembolsado_venta:.2f}")
    pausa()


def listar_todas_devoluciones():
    imprimir_titulo("TODAS LAS DEVOLUCIONES")
    mostrar_lista(devoluciones.leer(), "No hay devoluciones registradas.")
    pausa()


def ver_nota_credito():
    imprimir_titulo("NOTA DE CRÉDITO")
    id_dev = pedir_entero("Id de la devolución: ")
    if id_dev is None:
        imprimir_error("El ID debe ser un número entero")
        return pausa()

    texto = devoluciones.nota_credito(id_dev)
    if texto is None:
        imprimir_error(f"No existe la devolución #{id_dev}")
    else:
        print(texto)
    pausa()


def resumen():
    imprimir_titulo("RESUMEN DEL SISTEMA")
    print(f"  Clientes          : {len(clientes.leer())}")
    print(f"  Ciudades          : {', '.join(clientes.ciudades()) or '-'}")
    print(f"  Productos         : {len(productos.leer())}")
    bajos = productos.con_stock_bajo()
    print(f"  Stock bajo        : {', '.join(p.nombre for p in bajos) or 'ninguno'}")
    print(f"  Ventas            : {len(ventas.leer())}")
    total_v = ventas.total_vendido()
    total_r = devoluciones.total_reembolsado()
    print(f"  Devoluciones      : {len(devoluciones.leer())}")
    print(f"  Total vendido     : ${total_v:.2f}")
    print(f"  Total reembolsado : ${total_r:.2f}")
    print(f"  Ventas netas      : ${total_v - total_r:.2f}")
    pausa()


# =====================================================================
# DICCIONARIOS DE MENÚS
# =====================================================================

MENU_CLIENTES = {
    "1": ("Crear cliente", crear_cliente),
    "2": ("Ver todos", listar_clientes),
    "3": ("Buscar", buscar_cliente),
    "4": ("Ver por id", ver_cliente),
    "5": ("Actualizar", actualizar_cliente),
    "6": ("Eliminar", eliminar_cliente),
    "0": ("Volver", None),
}

MENU_PRODUCTOS = {
    "1": ("Crear producto", crear_producto),
    "2": ("Ver todos", listar_productos),
    "3": ("Buscar", buscar_producto),
    "4": ("Ver por id", ver_producto),
    "5": ("Actualizar", actualizar_producto),
    "6": ("Eliminar", eliminar_producto),
    "0": ("Volver", None),
}

MENU_VENTAS = {
    "1": ("Registrar venta", registrar_venta),
    "2": ("Ver todas", listar_ventas),
    "3": ("Ver comprobante", ver_comprobante),
    "4": ("Anular venta", anular_venta),
    "0": ("Volver", None),
}

MENU_DEVOLUCIONES = {
    "1": ("Registrar devolución", crear_devolucion),
    "2": ("Consultar devoluciones por venta", consultar_devolucion),
    "3": ("Ver todas las devoluciones", listar_todas_devoluciones),
    "4": ("Ver nota de crédito", ver_nota_credito),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue

        _, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA DE VENTAS")
        print("  1. Clientes")
        print("  2. Productos")
        print("  3. Ventas")
        print("  4. Devoluciones")
        print("  5. Resumen")
        print("  0. Salir\n")

        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("CLIENTES", MENU_CLIENTES)
        elif tecla == "2":
            ejecutar_menu("PRODUCTOS", MENU_PRODUCTOS)
        elif tecla == "3":
            ejecutar_menu("VENTAS", MENU_VENTAS)
        elif tecla == "4":
            ejecutar_menu("DEVOLUCIONES", MENU_DEVOLUCIONES)
        elif tecla == "5":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")