from abc import ABC, abstractmethod

from models import Cliente, Producto, Venta, Devolucion
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


class CrudBase(ABC):
    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class ClienteController(CrudBase):
    def __init__(self, archivo="data/clientes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Cliente.desde_diccionario(datos))

    def guardar(self):
        datos = [c.a_diccionario() for c in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            usados = {c.email for c in self.lista if c.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        telefono = str(datos.get("telefono", "")).strip()
        if telefono != "" and not telefono.isdigit():
            return "El teléfono solo puede tener números"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_cliente):
        for cliente in self.lista:
            if cliente.id == id_cliente:
                return cliente
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for cliente in self.lista:
            if (texto in cliente.nombre.lower()
                    or texto in cliente.apellido.lower()
                    or texto in cliente.email
                    or texto in cliente.telefono
                    or texto in cliente.ciudad.lower()):
                encontrados.append(cliente)
        return encontrados

    def siguiente(self):
        mayor = 0
        for cliente in self.lista:
            if cliente.id > mayor:
                mayor = cliente.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cliente = Cliente(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["apellido"]).strip().title(),
                          str(datos["email"]).strip().lower(),
                          str(datos.get("telefono", "")).strip(),
                          str(datos.get("ciudad", "")).strip().title())
        self.lista.append(cliente)
        self.guardar()
        return True, f"Cliente creado: {cliente.etiqueta()}"

    def actualizar(self, id_cliente, datos):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "apellido", "email", "telefono", "ciudad"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_cliente)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "ciudad"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            setattr(cliente, campo, valor)

        self.guardar()
        return True, f"Cliente {id_cliente} actualizado"

    def eliminar(self, id_cliente):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"

        self.lista.remove(cliente)
        self.guardar()
        return True, f"Cliente {id_cliente} eliminado"

    def ciudades(self):
        return sorted({c.ciudad for c in self.lista if c.ciudad != ""})


class ProductoController(CrudBase):
    def __init__(self, archivo="data/productos.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Producto.desde_diccionario(datos))

    def guardar(self):
        datos = [p.a_diccionario() for p in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "precio"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "precio" in datos and not Producto.es_precio_valido(datos["precio"]):
            return f"Precio inválido: '{datos['precio']}' (debe ser un número mayor a 0)"

        stock = str(datos.get("stock", "")).strip()
        if stock != "" and not stock.isdigit():
            return "El stock debe ser un número entero positivo"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otro in self.lista:
                if otro.nombre == nombre and otro.id != id_actual:
                    return f"Ya existe un producto llamado {nombre}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_producto):
        for producto in self.lista:
            if producto.id == id_producto:
                return producto
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for producto in self.lista:
            if texto in producto.nombre.lower():
                encontrados.append(producto)
        return encontrados

    def siguiente(self):
        mayor = 0
        for producto in self.lista:
            if producto.id > mayor:
                mayor = producto.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        stock = str(datos.get("stock", "")).strip()
        producto = Producto(self.siguiente(),
                            str(datos["nombre"]).strip().title(),
                            float(datos["precio"]),
                            int(stock) if stock != "" else 0)
        self.lista.append(producto)
        self.guardar()
        return True, f"Producto creado: {producto.etiqueta()}"

    def actualizar(self, id_producto, datos):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "precio", "stock"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_producto)
        if error:
            return False, error

        if "nombre" in datos:
            producto.nombre = str(datos["nombre"]).strip().title()
        if "precio" in datos:
            producto.precio = float(datos["precio"])
        if "stock" in datos:
            producto.stock = int(datos["stock"])

        self.guardar()
        return True, f"Producto {id_producto} actualizado"

    def eliminar(self, id_producto):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"

        self.lista.remove(producto)
        self.guardar()
        return True, f"Producto {id_producto} eliminado"

    def con_stock_bajo(self):
        return [p for p in self.lista if p.stock_bajo()]


class VentaController(CrudBase):
    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        self.clientes = clientes
        self.productos = productos
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Venta.desde_diccionario(datos))

    def guardar(self):
        datos = [v.a_diccionario() for v in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
            producto_id = int(datos.get("producto_id", 0))
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return "cliente_id, producto_id y cantidad deben ser números enteros"

        if cantidad <= 0:
            return "La cantidad debe ser mayor a 0"
        if self.clientes.obtener(cliente_id) is None:
            return f"No existe un cliente con id {cliente_id}"

        producto = self.productos.obtener(producto_id)
        if producto is None:
            return f"No existe un producto con id {producto_id}"
        if not producto.hay_stock(cantidad):
            return (f"Stock insuficiente de {producto.nombre}: "
                    f"hay {producto.stock}, piden {cantidad}")
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_venta):
        for venta in self.lista:
            if venta.id == id_venta:
                return venta
        return None

    def buscar(self, texto):
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas

        for venta in self.lista:
            if texto in venta.fecha:
                encontradas.append(venta)
        return encontradas

    def siguiente(self):
        mayor = 0
        for venta in self.lista:
            if venta.id > mayor:
                mayor = venta.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        producto = self.productos.obtener(int(datos["producto_id"]))
        venta = Venta(self.siguiente(),
                      int(datos["cliente_id"]),
                      producto.id,
                      int(datos["cantidad"]),
                      producto.precio)

        producto.descontar_stock(venta.cantidad)
        self.productos.guardar()
        self.lista.append(venta)
        self.guardar()
        return True, f"Venta {venta.id} registrada por ${venta.calcular_total():.2f}"

    def actualizar(self, id_venta, datos):
        return False, "Las ventas no se pueden modificar: anúlela y registre otra"

    def eliminar(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return False, f"No existe la venta {id_venta}"

        producto = self.productos.obtener(venta.producto_id)
        if producto is not None:
            producto.devolver_stock(venta.cantidad)
            self.productos.guardar()

        self.lista.remove(venta)
        self.guardar()
        return True, f"Venta {id_venta} anulada y stock devuelto"

    def comprobante(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return None

        cliente = self.clientes.obtener(venta.cliente_id)
        producto = self.productos.obtener(venta.producto_id)
        total = venta.calcular_total()

        texto = f"COMPROBANTE #{venta.id}   fecha: {venta.fecha}\n"
        texto += f"Cliente : {cliente.nombre_completo() if cliente else 'eliminado'}\n"
        texto += f"Producto: {producto.nombre if producto else 'eliminado'}\n"
        texto += f"Cantidad: {venta.cantidad} x ${venta.precio_unitario:.2f}\n"
        texto += "-" * 42 + "\n"
        texto += f"SUBTOTAL: ${total:.2f}\n"
        texto += f"TOTAL con IVA: ${Producto.con_iva(total):.2f}"
        return texto

    def total_vendido(self):
        return round(sum(v.calcular_total() for v in self.lista), 2)


class DevolucionController(CrudBase):
    def __init__(self, ventas, productos, clientes, archivo="data/devoluciones.json"):
        self.ventas = ventas
        self.productos = productos
        self.clientes = clientes
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Devolucion.desde_diccionario(datos))

    def guardar(self):
        datos = [dev.a_diccionario() for dev in self.lista]
        self.gestor.guardar(datos)

    def devoluciones_de_venta(self, venta_id):
        return [d for d in self.lista if d.venta_id == venta_id]

    def cantidad_devuelta(self, venta_id):
        return sum(d.cantidad for d in self.devoluciones_de_venta(venta_id))

    def cantidad_disponible(self, venta):
        return venta.cantidad - self.cantidad_devuelta(venta.id)

    def calcular_reembolso(self, venta, cantidad):
        return Producto.con_iva(cantidad * venta.precio_unitario)

    def validar(self, datos):
        try:
            venta_id = int(datos.get("venta_id", 0))
            cantidad = int(datos.get("cantidad", 0))
            motivo = str(datos.get("motivo", "")).strip().lower()
        except (TypeError, ValueError):
            return "venta_id y cantidad deben ser números enteros"

        venta = self.ventas.obtener(venta_id)
        if venta is None:
            return f"No existe la venta #{venta_id}"

        if not Devolucion.dentro_del_plazo(venta.fecha):
            return f"Superó el límite de {Devolucion.DIAS_LIMITE} días para devoluciones"

        disponible = self.cantidad_disponible(venta)
        if cantidad <= 0:
            return "La cantidad a devolver debe ser mayor a 0"
        if cantidad > disponible:
            return f"Solo se pueden devolver {disponible} unidad(es) de esta venta"

        if not Devolucion.es_motivo_valido(motivo):
            return f"Motivo no válido. Opciones: {', '.join(Devolucion.MOTIVOS)}"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_registro):
        for dev in self.lista:
            if dev.id == id_registro:
                return dev
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for dev in self.lista:
            if texto in dev.motivo or texto in dev.fecha or texto == str(dev.venta_id):
                encontradas.append(dev)
        return encontradas

    def siguiente(self):
        mayor = 0
        for dev in self.lista:
            if dev.id > mayor:
                mayor = dev.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        venta = self.ventas.obtener(int(datos["venta_id"]))
        cantidad = int(datos["cantidad"])
        motivo = str(datos["motivo"]).strip().lower()
        monto_reembolso = self.calcular_reembolso(venta, cantidad)

        devolucion = Devolucion(
            self.siguiente(),
            venta.id,
            cantidad,
            motivo,
            monto_reembolso
        )

        producto = self.productos.obtener(venta.producto_id)
        if producto and devolucion.regresa_al_stock():
            producto.devolver_stock(cantidad)
            self.productos.guardar()
            msg_stock = f"Stock restablecido (+{cantidad} en inventario -> Nuevo stock: {producto.stock})"
        else:
            msg_stock = "Producto defectuoso: no se restablece en el inventario"

        self.lista.append(devolucion)
        self.guardar()
        return True, f"Devolución #{devolucion.id} registrada · Reembolso: ${devolucion.monto:.2f} · {msg_stock}"

    def actualizar(self, id_registro, datos):
        return False, "Las devoluciones no se pueden modificar por políticas de auditoría"

    def eliminar(self, id_registro):
        return False, "Las devoluciones registradas no se pueden eliminar"

    def nota_credito(self, id_devolucion):
        dev = self.obtener(id_devolucion)
        if dev is None:
            return None

        venta = self.ventas.obtener(dev.venta_id)
        cliente = self.clientes.obtener(venta.cliente_id) if (self.clientes and venta) else None
        producto = self.productos.obtener(venta.producto_id) if venta else None

        texto = f"NOTA DE CRÉDITO #{dev.id}   fecha: {dev.fecha}\n"
        texto += f"Factura  : #{dev.venta_id}   ({cliente.nombre_completo() if cliente else 'Desconocido'})\n"
        texto += f"Producto : {producto.nombre if producto else 'Desconocido'}\n"
        texto += f"Cantidad : {dev.cantidad} x ${venta.precio_unitario:.2f}\n"
        texto += f"Motivo   : {dev.motivo.capitalize()}\n"
        texto += "-" * 46 + "\n"
        texto += f"TOTAL REEMBOLSADO (con IVA): ${dev.monto:.2f}\n"
        stock_txt = f"Reingresado al stock (Stock actual: {producto.stock})" if (producto and dev.regresa_al_stock()) else "No regresa a stock (defectuoso)"
        texto += f"Estado Stock : {stock_txt}"
        return texto

    def total_reembolsado(self):
        return round(sum(d.monto for d in self.lista), 2)