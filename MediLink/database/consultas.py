# database/consultas.py
from database.conexion import conectar

# ============================================================
# HELPERS INTERNOS
# ============================================================
def _ejecutar_sp_lectura(nombre_sp, params=()):
    """Ejecuta un SP de lectura y devuelve lista de dicts."""
    conexion = conectar()
    if conexion is None:
        return []
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.callproc(nombre_sp, params)
        resultados = []
        for result in cursor.stored_results():
            resultados.extend(result.fetchall())
        return resultados
    except Exception as e:
        print(f"Error en SP {nombre_sp}: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


def _ejecutar_sp_escritura(nombre_sp, params=()):
    """Ejecuta un SP de escritura y hace commit."""
    conexion = conectar()
    if conexion is None:
        return False
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.callproc(nombre_sp, params)
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error en SP {nombre_sp}: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


# ============================================================
# CLIENTES
# ============================================================
def insertar_cliente(nombre, ap_paterno, ap_materno, edad, sexo, fecha_nacimiento,
                     peso, talla, oxigenacion, presion, temperatura, correo, direccion):
    return _ejecutar_sp_escritura(
        'sp_insertar_cliente',
        (nombre, ap_paterno, ap_materno, edad, sexo, fecha_nacimiento,
         peso, talla, oxigenacion, presion, temperatura, correo, direccion)
    )


def obtener_todos_clientes():
    return _ejecutar_sp_lectura('sp_obtener_todos_clientes')


def buscar_clientes_por_apellido(termino):
    return _ejecutar_sp_lectura('sp_buscar_clientes_por_apellido', (termino,))


def actualizar_cliente_bd(id_cliente, nombre, ap_paterno, ap_materno, edad, sexo,
                          fecha_nacimiento, peso, talla, oxigenacion,
                          presion, temperatura, correo, direccion):
    return _ejecutar_sp_escritura(
        'sp_actualizar_cliente',
        (id_cliente, nombre, ap_paterno, ap_materno, edad, sexo, fecha_nacimiento,
         peso, talla, oxigenacion, presion, temperatura, correo, direccion)
    )


def buscar_paciente_duplicado(nombre, ap_paterno, ap_materno, fecha_nacimiento):
    res = _ejecutar_sp_lectura(
        'sp_buscar_paciente_duplicado',
        (nombre, ap_paterno, ap_materno or '', fecha_nacimiento)
    )
    return res[0] if res else None


def buscar_cliente_por_correo(correo):
    """Devuelve el cliente si existe alguien con ese correo, None si no."""
    res = _ejecutar_sp_lectura('sp_buscar_cliente_por_correo', (correo,))
    return res[0] if res else None


# ============================================================
# MEDICAMENTOS
# ============================================================
def insertar_medicamento(data):
    """Devuelve (exito, mensaje)."""
    conexion = conectar()
    if conexion is None:
        return False, "Error de conexión a la base de datos"
    cursor = None
    try:
        cursor = conexion.cursor()
        valores = (
            data["nombre"], data["clasificacion"], data["presentacion"],
            data["precio"], data["stock"], data["lote"], data["precio_lote"],
            data["mg"], data["caducidad"], data["fecha_alta"],
            data["farmaceutica"], data["descripcion"]
        )
        cursor.callproc('sp_insertar_medicamento', valores)
        conexion.commit()
        return True, "Medicamento registrado exitosamente."
    except Exception as e:
        return False, str(e)
    finally:
        if cursor:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


def buscar_medicamentos_bd(termino):
    """Para venta/caja: devuelve tuplas (id, nombre, precio, stock)."""
    conexion = conectar()
    if conexion is None:
        return []
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.callproc('sp_buscar_medicamentos', (termino,))
        resultados = []
        for result in cursor.stored_results():
            resultados.extend(result.fetchall())
        return resultados
    except Exception as e:
        print(f"Error al buscar medicamentos: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


def obtener_stock_medicamento(id_medicamento):
    """Devuelve el stock actual de un medicamento. Útil para validar antes de cobrar."""
    conexion = conectar()
    if conexion is None:
        return None
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT stock FROM medicamentos WHERE id_medicamento = %s",
            (id_medicamento,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error al consultar stock: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


def buscar_farmaceuticas(termino):
    filas = _ejecutar_sp_lectura('sp_buscar_farmaceuticas', (termino,))
    return [fila['farmaceutica'] for fila in filas if fila.get('farmaceutica')]


def buscar_medicamento_existente(nombre, presentacion, cantidad_mg):
    res = _ejecutar_sp_lectura(
        'sp_buscar_medicamento_existente',
        (nombre, presentacion, cantidad_mg)
    )
    return res[0] if res else None


def reabastecer_medicamento(id_medicamento, stock_extra, nuevo_lote,
                            precio_lote, caducidad, precio_unitario):
    return _ejecutar_sp_escritura(
        'sp_reabastecer_medicamento',
        (id_medicamento, stock_extra, nuevo_lote, precio_lote,
         caducidad, precio_unitario)
    )


def autocompletar_medicamentos(termino):
    """SP: sp_autocompletar_medicamentos - sugerencias mientras escribes."""
    return _ejecutar_sp_lectura('sp_autocompletar_medicamentos', (termino,))


def obtener_todos_medicamentos():
    """SP: sp_obtener_todos_medicamentos - para la tabla completa."""
    return _ejecutar_sp_lectura('sp_obtener_todos_medicamentos')


def filtrar_medicamentos_por_clasificacion(clasificacion):
    """SP: sp_filtrar_medicamentos_clasificacion"""
    return _ejecutar_sp_lectura(
        'sp_filtrar_medicamentos_clasificacion',
        (clasificacion,)
    )


def actualizar_medicamento(id_med, clasificacion, precio_unit, stock,
                           numero_lote, precio_lote, caducidad,
                           farmaceutica, descripcion):
    """SP: sp_actualizar_medicamento - edita campos no identitarios."""
    return _ejecutar_sp_escritura(
        'sp_actualizar_medicamento',
        (id_med, clasificacion, precio_unit, stock, numero_lote,
         precio_lote, caducidad, farmaceutica, descripcion)
    )


# ============================================================
# VENTAS
# ============================================================
def procesar_venta_completa(total, tipo_consulta, carrito):
    """
    Procesa una venta con validación previa de stock.
    Devuelve (exito, mensaje).
    """
    conexion = conectar()
    if conexion is None:
        return False, "Error de conexión"

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)

        # 1) Validar stock disponible ANTES de tocar nada
        for item in carrito:
            cursor.execute(
                "SELECT nombre_producto, stock FROM medicamentos "
                "WHERE id_medicamento = %s FOR UPDATE",
                (item["id_medicamento"],)
            )
            row = cursor.fetchone()
            if not row:
                conexion.rollback()
                return False, f"El medicamento ID {item['id_medicamento']} ya no existe."
            if row["stock"] < item["cantidad"]:
                conexion.rollback()
                return False, (f"Stock insuficiente de '{row['nombre_producto']}'. "
                               f"Disponibles: {row['stock']}, "
                               f"solicitados: {item['cantidad']}.")

        # 2) Crear venta y registrar detalles
        cursor.close()
        cursor = conexion.cursor()
        resultado_venta = cursor.callproc(
            'sp_crear_venta', (total, tipo_consulta, 0))
        id_nueva_venta = resultado_venta[2]

        for item in carrito:
            valores_detalle = (
                id_nueva_venta, item["id_medicamento"], item["cantidad"],
                item["precio"], item["subtotal"]
            )
            cursor.callproc('sp_insertar_detalle', valores_detalle)

        conexion.commit()
        return True, "Venta registrada y stock actualizado correctamente."

    except Exception as e:
        conexion.rollback()
        return False, f"Error al procesar la venta: {e}"
    finally:
        if cursor:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


# ============================================================
# TRABAJADORES
# ============================================================
def insertar_trabajador(nombre, ap_paterno, ap_materno, fecha_nac, genero,
                        curp, rfc, direccion, telefono, correo,
                        puesto, cedula, turno, fecha_ingreso):
    return _ejecutar_sp_escritura(
        'sp_insertar_trabajador',
        (nombre, ap_paterno, ap_materno, fecha_nac, genero,
         curp, rfc, direccion, telefono, correo,
         puesto, cedula, turno, fecha_ingreso)
    )


def obtener_trabajadores():
    """Devuelve TODOS los trabajadores (incluyendo INACTIVOS)."""
    return _ejecutar_sp_lectura('sp_obtener_todos_trabajadores')


def actualizar_trabajador_bd(id_trabajador, nombre, ap_paterno, ap_materno,
                             fecha_nac, genero, curp, rfc, direccion,
                             telefono, correo, puesto, cedula, turno,
                             fecha_ingreso):
    return _ejecutar_sp_escritura(
        'sp_actualizar_trabajador',
        (id_trabajador, nombre, ap_paterno, ap_materno, fecha_nac, genero,
         curp, rfc, direccion, telefono, correo,
         puesto, cedula, turno, fecha_ingreso)
    )


def obtener_medico_por_id(id_medico):
    resultados = _ejecutar_sp_lectura(
        'sp_obtener_trabajador_por_id', (id_medico,))
    return resultados[0] if resultados else None


def buscar_trabajador_por_curp_rfc(curp, rfc):
    res = _ejecutar_sp_lectura(
        'sp_buscar_trabajador_por_curp_rfc', (curp, rfc))
    return res[0] if res else None


def buscar_trabajador_por_correo(correo):
    """Devuelve el trabajador si existe alguien con ese correo, None si no."""
    res = _ejecutar_sp_lectura('sp_buscar_trabajador_por_correo', (correo,))
    return res[0] if res else None


def deshabilitar_trabajador(id_trabajador, observacion):
    """Usa SP en vez de SQL crudo."""
    return _ejecutar_sp_escritura(
        'sp_deshabilitar_trabajador',
        (id_trabajador, observacion)
    )


def activar_trabajador(id_trabajador):
    """Usa SP en vez de SQL crudo."""
    return _ejecutar_sp_escritura(
        'sp_activar_trabajador',
        (id_trabajador,)
    )


# ============================================================
# HISTORIAL MÉDICO
# ============================================================
def guardar_historial_bd(id_cliente, id_medico, fecha, diagnostico, tratamiento):
    return _ejecutar_sp_escritura(
        'sp_insertar_historial',
        (id_cliente, id_medico, fecha, diagnostico, tratamiento)
    )


def obtener_historial_bd(id_cliente):
    return _ejecutar_sp_lectura('sp_obtener_historial_cliente', (id_cliente,))

# ============================================================
# MODIFICAR PERSONAL MEDICO GENERAL
# ============================================================


def buscar_cedula_medico(cedula):
    """Devuelve el médico con esa cédula si existe, None si no."""
    res = _ejecutar_sp_lectura(
        'sp_buscar_cedula_medico',
        (cedula,)
    )
    return res[0] if res else None

# ============================================================
# TRABAJADOR GENÉRICO (para farmacéutico en caja)
# ============================================================
def obtener_trabajador_por_id(id_trabajador):
    """Devuelve cualquier trabajador por ID (no filtra por puesto)."""
    res = _ejecutar_sp_lectura(
        'sp_obtener_trabajador_por_id',
        (id_trabajador,)
    )
    return res[0] if res else None

# ============================================================
# DESHABILITAR / ACTIVAR CLIENTE
# ============================================================
def deshabilitar_cliente(id_cliente, observacion):
    return _ejecutar_sp_escritura(
        'sp_deshabilitar_cliente',
        (id_cliente, observacion)
    )

def activar_cliente(id_cliente):
    return _ejecutar_sp_escritura(
        'sp_activar_cliente',
        (id_cliente,)
    )

def eliminar_historial_bd(id_historial):
    return _ejecutar_sp_escritura(
        'sp_eliminar_historial',
        (id_historial,)
    )