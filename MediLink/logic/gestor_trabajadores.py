# logic/gestor_trabajadores.py
from database.consultas import (
    insertar_trabajador,
    actualizar_trabajador_bd,
    buscar_trabajador_por_curp_rfc,
    buscar_trabajador_por_correo,
    buscar_cedula_medico, 
)
from logic.validators import (
    validar_nombre, validar_curp, validar_rfc,
    validar_telefono, validar_email, validar_fecha,
    validar_cedula_profesional, validar_fecha_pasada,
    validar_mayor_edad_trabajador, validar_fecha_ingreso,
)


def _validar_campos_trabajador(nombre, ap_paterno, ap_materno, fecha_nac, genero,
                              curp, rfc, telefono, correo, puesto, cedula,
                              turno, fecha_ingreso):
    """Validaciones comunes. Devuelve (ok, msg)."""

    ok, msg = validar_nombre(nombre, "Nombre", min_len=2)
    if not ok: return False, msg

    ok, msg = validar_nombre(ap_paterno, "Apellido paterno", min_len=2)
    if not ok: return False, msg

    if ap_materno:
        ok, msg = validar_nombre(ap_materno, "Apellido materno")
        if not ok: return False, msg

    if not genero:
        return False, "Género es obligatorio."

    # Fecha de nacimiento: válida, en el pasado y al menos 18 años
    ok, msg = validar_fecha_pasada(fecha_nac, "Fecha de nacimiento")
    if not ok: return False, msg

    ok, msg = validar_mayor_edad_trabajador(fecha_nac, edad_minima=18)
    if not ok: return False, msg

    # CURP: validar formato Y que coincida con el género
    ok, msg = validar_curp(curp, genero=genero)
    if not ok: return False, msg

    ok, msg = validar_rfc(rfc)
    if not ok: return False, msg

    ok, msg = validar_telefono(telefono, opcional=True, longitud=10)
    if not ok: return False, msg

    ok, msg = validar_email(correo, opcional=True)
    if not ok: return False, msg

    if not puesto:
        return False, "Puesto es obligatorio."

    if not turno:
        return False, "Turno es obligatorio."

    # Fecha de ingreso: válida, en el pasado, y al menos 18 años después de fecha_nac
    ok, msg = validar_fecha_ingreso(fecha_ingreso, fecha_nac)
    if not ok: return False, msg

    # Cédula obligatoria solo para Médico General
    es_medico = (puesto == "Médico General")
    ok, msg = validar_cedula_profesional(cedula, requerida=es_medico)
    if not ok: return False, msg

    return True, ""


def registrar_trabajador(nombre, ap_paterno, ap_materno, fecha_nac, genero,
                        curp, rfc, direccion, telefono, correo, puesto,
                        cedula, turno, fecha_ingreso):
    """Inserta un trabajador nuevo. Verifica unicidad de CURP, RFC y correo."""

    ok, msg = _validar_campos_trabajador(
        nombre, ap_paterno, ap_materno, fecha_nac, genero, curp, rfc,
        telefono, correo, puesto, cedula, turno, fecha_ingreso
    )
    if not ok:
        return False, msg

    curp_limpio = curp.strip().upper()
    rfc_limpio  = rfc.strip().upper()
    correo_limpio = (correo or "").strip().lower()

    # Verificar unicidad CURP/RFC
    duplicado = buscar_trabajador_por_curp_rfc(curp_limpio, rfc_limpio)
    if duplicado:
        if duplicado.get('curp') == curp_limpio:
            return False, (f"Ya existe un trabajador con esa CURP "
                          f"({duplicado['nombre']} {duplicado['ap_paterno']}).")
        if duplicado.get('rfc') == rfc_limpio:
            return False, (f"Ya existe un trabajador con ese RFC "
                          f"({duplicado['nombre']} {duplicado['ap_paterno']}).")

    # Verificar unicidad de correo (si se proporcionó)
    if correo_limpio:
        dup_correo = buscar_trabajador_por_correo(correo_limpio)
        if dup_correo:
            return False, (f"Ya existe un trabajador con ese correo "
                          f"({dup_correo['nombre']} {dup_correo['ap_paterno']}).")
            
    # Unicidad de cédula profesional (solo si es Médico General)
    if puesto == "Médico General":
        cedula_limpia = cedula.strip()
        dup_cedula = buscar_cedula_medico(cedula_limpia)
        if dup_cedula:
            return False, (f"Ya existe un médico con esa cédula "
                           f"({dup_cedula['nombre']} {dup_cedula['ap_paterno']}).")

    cedula_final = cedula.strip() if puesto == "Médico General" else ""

    exito = insertar_trabajador(
        nombre.strip(), ap_paterno.strip(),
        ap_materno.strip() if ap_materno else "",
        fecha_nac, genero, curp_limpio, rfc_limpio,
        direccion.strip() if direccion else "",
        telefono.strip() if telefono else "",
        correo_limpio,
        puesto, cedula_final, turno, fecha_ingreso
    )

    if exito:
        return True, "Trabajador registrado exitosamente."
    return False, "Error al guardar el trabajador."


def actualizar_trabajador(id_trabajador, nombre, ap_paterno, ap_materno, fecha_nac,
                         genero, curp, rfc, direccion, telefono, correo,
                         puesto, cedula, turno, fecha_ingreso):
    """Actualiza un trabajador existente. Verifica que CURP/RFC/correo no coincidan con OTRO."""

    ok, msg = _validar_campos_trabajador(
        nombre, ap_paterno, ap_materno, fecha_nac, genero, curp, rfc,
        telefono, correo, puesto, cedula, turno, fecha_ingreso
    )
    if not ok:
        return False, msg

    curp_limpio = curp.strip().upper()
    rfc_limpio  = rfc.strip().upper()
    correo_limpio = (correo or "").strip().lower()

    # Unicidad: si CURP/RFC pertenecen a OTRO trabajador, no permitir
    duplicado = buscar_trabajador_por_curp_rfc(curp_limpio, rfc_limpio)
    if duplicado and duplicado.get('id_trabajador') != id_trabajador:
        if duplicado.get('curp') == curp_limpio:
            return False, (f"Esa CURP ya pertenece a otro trabajador "
                          f"({duplicado['nombre']} {duplicado['ap_paterno']}).")
        if duplicado.get('rfc') == rfc_limpio:
            return False, (f"Ese RFC ya pertenece a otro trabajador "
                          f"({duplicado['nombre']} {duplicado['ap_paterno']}).")

    # Unicidad correo
    if correo_limpio:
        dup_correo = buscar_trabajador_por_correo(correo_limpio)
        if dup_correo and dup_correo.get('id_trabajador') != id_trabajador:
            return False, (f"Ese correo ya pertenece a otro trabajador "
                          f"({dup_correo['nombre']} {dup_correo['ap_paterno']}).")
            
    # Unicidad de cédula al EDITAR: solo si pertenece a OTRO médico
    if puesto == "Médico General":
        cedula_limpia = cedula.strip()
        dup_cedula = buscar_cedula_medico(cedula_limpia)
        if dup_cedula and dup_cedula.get('id_trabajador') != id_trabajador:
            return False, (f"Esa cédula ya pertenece a otro médico "
                           f"({dup_cedula['nombre']} {dup_cedula['ap_paterno']}).")

    cedula_final = cedula.strip() if puesto == "Médico General" else ""

    exito = actualizar_trabajador_bd(
        id_trabajador,
        nombre.strip(), ap_paterno.strip(),
        ap_materno.strip() if ap_materno else "",
        fecha_nac, genero, curp_limpio, rfc_limpio,
        direccion.strip() if direccion else "",
        telefono.strip() if telefono else "",
        correo_limpio,
        puesto, cedula_final, turno, fecha_ingreso
    )

    if exito:
        return True, "Trabajador actualizado exitosamente."
    return False, "Error al actualizar."