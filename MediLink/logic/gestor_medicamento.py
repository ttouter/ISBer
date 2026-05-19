# logic/gestor_medicamento.py
from database.consultas import (
    insertar_medicamento,
    buscar_medicamento_existente,
    reabastecer_medicamento,
    actualizar_medicamento,
    verificar_lote_existente,
)
from logic.validators import (
    validar_decimal, validar_entero, validar_fecha,
    validar_fecha_futura,
)


def _validar_campos_medicamento(data, requerir_identidad=True):
    """
    Valida los campos del formulario de medicamento.
    Si requerir_identidad=False, no valida nombre/presentación/mg
    (útil para actualizar uno existente).
    """
    if requerir_identidad:
        if not data.get("nombre") or len(str(data["nombre"]).strip()) < 2:
            return False, "Nombre del producto debe tener al menos 2 caracteres."
        if not data.get("presentacion"):
            return False, "Presentación es obligatoria."
        ok, msg = validar_entero(data.get("mg"), "Cantidad mg",
                                 min_val=1, max_val=100000)
        if not ok: return False, msg

    if not data.get("clasificacion"):
        return False, "Clasificación es obligatoria."

    ok, msg = validar_decimal(data.get("precio"), "Precio unitario",
                              min_val=0.01, max_val=100000)
    if not ok: return False, msg

    ok, msg = validar_entero(data.get("stock"), "Stock",
                             min_val=0, max_val=1000000)
    if not ok: return False, msg

    if not data.get("lote") or len(str(data["lote"]).strip()) < 1:
        return False, "Número de lote es obligatorio."

    lote_str = str(data["lote"]).strip()
    if not lote_str.isdigit():
        return False, "El número de lote solo puede contener dígitos (ej: 1001)."
    if int(lote_str) < 1:
        return False, "El número de lote debe ser mayor a 0."

    ok, msg = validar_decimal(data.get("precio_lote"), "Precio por lote",
                              min_val=0.01, max_val=10000000, opcional=True)
    if not ok: return False, msg

    # Fecha de caducidad: debe ser HOY o posterior, no en el pasado
    ok, msg = validar_fecha_futura(data.get("caducidad"),
                                   "Fecha de caducidad", incluir_hoy=True)
    if not ok: return False, msg

    if not data.get("farmaceutica") or len(str(data["farmaceutica"]).strip()) < 2:
        return False, "Farmacéutica es obligatoria."

    return True, ""


# ============================================================
# WRAPPER COMPATIBLE (desempaque de 2 o 3 valores)
# ============================================================
class _ResultadoMedicamento(tuple):
    def __new__(cls, exito, mensaje, extra=None):
        return super().__new__(cls, (exito, mensaje, extra))

    def __iter__(self):
        return iter((self[0], self[1]))

    @property
    def exito(self):    return self[0]
    @property
    def mensaje(self):  return self[1]
    @property
    def extra(self):    return self[2]


def registrar_medicamento(data, forzar_nuevo=False):
    """
    Registra un medicamento.
    - OK:           (True, msg, None)
    - Ya existe:    (False, "DUPLICADO", dict_existente)
    - Error:        (False, msg_error, None)
    """
    ok, msg = _validar_campos_medicamento(data, requerir_identidad=True)
    if not ok:
        return _ResultadoMedicamento(False, msg, None)

    # Verificar que el número de lote no esté ya en uso
    if verificar_lote_existente(data["lote"]):
        return _ResultadoMedicamento(
            False,
            f"El número de lote {data['lote']} ya existe. Usa un número diferente.",
            None
        )

    if not forzar_nuevo:
        try:
            existente = buscar_medicamento_existente(
                str(data["nombre"]).strip(),
                data["presentacion"],
                int(data["mg"])
            )
        except (ValueError, TypeError):
            existente = None
        if existente:
            return _ResultadoMedicamento(False, "DUPLICADO", existente)

    exito, msg_ins = insertar_medicamento(data)
    return _ResultadoMedicamento(exito, msg_ins, None)


def actualizar(id_medicamento, data):
    """
    Actualiza un medicamento existente (sin tocar identidad).
    Devuelve (exito, mensaje).
    """
    ok, msg = _validar_campos_medicamento(data, requerir_identidad=False)
    if not ok:
        return False, msg

    # Verificar que el lote no lo tenga otro medicamento distinto
    if verificar_lote_existente(data["lote"], excluir_id=id_medicamento):
        return False, f"El número de lote {data['lote']} ya está en uso por otro medicamento."

    try:
        precio_unit  = float(data["precio"])
        stock_int    = int(data["stock"])
        precio_l     = float(data["precio_lote"]) if data.get("precio_lote") else 0.0
    except (ValueError, TypeError):
        return False, "Datos numéricos inválidos."

    exito = actualizar_medicamento(
        id_med=id_medicamento,
        clasificacion=data["clasificacion"],
        precio_unit=precio_unit,
        stock=stock_int,
        numero_lote=str(data["lote"]).strip(),
        precio_lote=precio_l,
        caducidad=data["caducidad"],
        farmaceutica=str(data["farmaceutica"]).strip(),
        descripcion=str(data.get("descripcion") or "").strip()
    )

    if exito:
        return True, "Medicamento actualizado correctamente."
    return False, "Error al actualizar en la base de datos."


def reabastecer(id_medicamento, stock_extra, nuevo_lote, precio_lote,
                caducidad, precio_unitario):
    """Suma stock al medicamento existente."""
    ok, msg = validar_entero(stock_extra, "Stock a agregar",
                             min_val=1, max_val=1000000)
    if not ok: return False, msg

    ok, msg = validar_decimal(precio_unitario, "Precio unitario",
                              min_val=0.01, max_val=100000)
    if not ok: return False, msg

    # La caducidad del NUEVO lote debe ser hoy o posterior
    ok, msg = validar_fecha_futura(caducidad, "Fecha de caducidad",
                                   incluir_hoy=True)
    if not ok: return False, msg

    if not nuevo_lote or len(str(nuevo_lote).strip()) < 1:
        return False, "Número de lote es obligatorio."

    lote_str = str(nuevo_lote).strip()
    if not lote_str.isdigit():
        return False, "El número de lote solo puede contener dígitos (ej: 1001)."
    if int(lote_str) < 1:
        return False, "El número de lote debe ser mayor a 0."

    # El nuevo lote no debe estar ya registrado en ningún medicamento
    if verificar_lote_existente(lote_str):
        return False, f"El número de lote {lote_str} ya existe. Usa un número diferente."

    exito = reabastecer_medicamento(
        id_medicamento=id_medicamento,
        stock_extra=int(stock_extra),
        nuevo_lote=str(nuevo_lote).strip(),
        precio_lote=float(precio_lote) if precio_lote else 0.0,
        caducidad=caducidad,
        precio_unitario=float(precio_unitario)
    )

    if exito:
        return True, f"Stock actualizado: +{stock_extra} unidades agregadas."
    return False, "Error al reabastecer en la base de datos."