# logic/gestor_clientes.py
from database.consultas import (
    insertar_cliente,
    actualizar_cliente_bd,
    buscar_paciente_duplicado,
    buscar_cliente_por_correo,
)
from logic.validators import (
    validar_nombre, validar_entero, validar_decimal,
    validar_email, validar_presion, validar_fecha_pasada,
    validar_edad_coherente,
)


class _ResultadoCliente(tuple):
    """Desempaca los 3 valores (exito, mensaje, extra)."""
    def __new__(cls, exito, mensaje, extra=None):
        return super().__new__(cls, (exito, mensaje, extra))

    @property
    def exito(self):    return self[0]
    @property
    def mensaje(self):  return self[1]
    @property
    def extra(self):    return self[2]


def _validar_campos_paciente(nombre, ap_paterno, ap_materno, edad, sexo,
                             fecha_nacimiento, peso, talla, oxigenacion,
                             presion, temperatura, correo):
    """
    Valida los campos del paciente. TODOS son obligatorios.
    """

    # ---- DATOS PERSONALES (todos obligatorios) ----
    ok, msg = validar_nombre(nombre, "Nombre")
    if not ok: return False, msg

    ok, msg = validar_nombre(ap_paterno, "Apellido paterno")
    if not ok: return False, msg

    # AHORA ap_materno es obligatorio
    ok, msg = validar_nombre(ap_materno, "Apellido materno")
    if not ok: return False, msg

    if not sexo:
        return False, "Sexo es obligatorio."

    ok, msg = validar_fecha_pasada(fecha_nacimiento, "Fecha de nacimiento")
    if not ok: return False, msg

    ok, msg = validar_entero(edad, "Edad", min_val=0, max_val=120)
    if not ok: return False, msg

    ok, msg = validar_edad_coherente(edad, fecha_nacimiento, tolerancia=1)
    if not ok: return False, msg

    # ---- SIGNOS VITALES (ahora todos obligatorios) ----
    ok, msg = validar_decimal(peso, "Peso", min_val=0.5, max_val=300,
                              opcional=False)
    if not ok: return False, msg

    ok, msg = validar_decimal(talla, "Talla", min_val=30, max_val=250,
                              opcional=False)
    if not ok: return False, msg

    ok, msg = validar_decimal(oxigenacion, "Oxigenación",
                              min_val=0, max_val=100, opcional=False)
    if not ok: return False, msg

    ok, msg = validar_presion(presion, opcional=False)
    if not ok: return False, msg

    ok, msg = validar_decimal(temperatura, "Temperatura",
                              min_val=30, max_val=45, opcional=False)
    if not ok: return False, msg

    # ---- CORREO (ahora obligatorio) ----
    ok, msg = validar_email(correo, opcional=False)
    if not ok: return False, msg

    return True, ""


def _normalizar(nombre, ap_paterno, ap_materno, edad, peso, talla,
                oxigenacion, presion, temperatura, correo):
    return {
        "nombre":      nombre.strip(),
        "ap_paterno":  ap_paterno.strip(),
        "ap_materno":  ap_materno.strip(),
        "edad":        int(edad),
        "peso":        float(peso),
        "talla":       float(talla),
        "oxigenacion": float(oxigenacion),
        "presion":     presion.strip(),
        "temperatura": float(temperatura),
        "correo":      correo.strip().lower(),
    }


def registrar_cliente(nombre, ap_paterno, ap_materno, edad, sexo,
                      fecha_nacimiento, peso, talla, oxigenacion,
                      presion, temperatura, correo, direccion,
                      forzar_aunque_duplicado=False):
    """Registra un cliente nuevo. Detecta duplicados por nombre+fecha y por correo."""

    ok, msg = _validar_campos_paciente(
        nombre, ap_paterno, ap_materno, edad, sexo, fecha_nacimiento,
        peso, talla, oxigenacion, presion, temperatura, correo
    )
    if not ok:
        return _ResultadoCliente(False, msg, None)

    n = _normalizar(nombre, ap_paterno, ap_materno, edad, peso, talla,
                    oxigenacion, presion, temperatura, correo)

    dup_correo = buscar_cliente_por_correo(n["correo"])
    if dup_correo:
        return _ResultadoCliente(
            False,
            f"Ya existe un paciente con ese correo: "
            f"{dup_correo['nombre']} {dup_correo['ap_paterno']} "
            f"(ID {dup_correo['id_cliente']}).",
            None
        )

    if not forzar_aunque_duplicado:
        duplicado = buscar_paciente_duplicado(
            n["nombre"], n["ap_paterno"], n["ap_materno"], fecha_nacimiento
        )
        if duplicado:
            return _ResultadoCliente(False, "DUPLICADO", duplicado)

    exito = insertar_cliente(
        n["nombre"], n["ap_paterno"], n["ap_materno"],
        n["edad"], sexo, fecha_nacimiento,
        n["peso"], n["talla"], n["oxigenacion"],
        n["presion"], n["temperatura"], n["correo"],
        direccion
    )

    if exito:
        return _ResultadoCliente(True, "Cliente registrado correctamente.", None)
    return _ResultadoCliente(False, "Error al guardar en la base de datos.", None)


def actualizar_cliente(id_cliente, nombre, ap_paterno, ap_materno, edad, sexo,
                      fecha_nacimiento, peso, talla, oxigenacion,
                      presion, temperatura, correo, direccion):
    """Actualiza un cliente existente."""
    ok, msg = _validar_campos_paciente(
        nombre, ap_paterno, ap_materno, edad, sexo, fecha_nacimiento,
        peso, talla, oxigenacion, presion, temperatura, correo
    )
    if not ok:
        return False, msg

    n = _normalizar(nombre, ap_paterno, ap_materno, edad, peso, talla,
                    oxigenacion, presion, temperatura, correo)

    dup_correo = buscar_cliente_por_correo(n["correo"])
    if dup_correo and dup_correo.get('id_cliente') != id_cliente:
        return False, (
            f"Ese correo ya pertenece a otro paciente "
            f"({dup_correo['nombre']} {dup_correo['ap_paterno']})."
        )

    exito = actualizar_cliente_bd(
        id_cliente,
        n["nombre"], n["ap_paterno"], n["ap_materno"],
        n["edad"], sexo, fecha_nacimiento,
        n["peso"], n["talla"], n["oxigenacion"],
        n["presion"], n["temperatura"], n["correo"],
        direccion
    )

    if exito:
        return True, "Cliente actualizado correctamente."
    return False, "Error al actualizar en la base de datos."