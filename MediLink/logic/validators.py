import re
from datetime import datetime, date

# ============================================================
# EXPRESIONES REGULARES
# ============================================================
RE_SOLO_LETRAS       = re.compile(r"[^A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]")
RE_SOLO_NUMEROS      = re.compile(r"[^0-9]")
RE_NUMEROS_DECIMAL   = re.compile(r"[^0-9.]")
RE_LETRAS_NUMEROS    = re.compile(r"[^A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s]")
RE_PRESION           = re.compile(r"[^0-9/]")
RE_LOTE              = re.compile(r"[^A-Za-z0-9-]")
RE_DOSIS             = re.compile(r"[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s/().,-]")
RE_DIRECCION         = re.compile(r"[^A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s,.#°-]")

RE_EMAIL             = re.compile(r"^[\w\.\-+]+@[\w\-]+\.[\w\.\-]+$")
RE_CURP              = re.compile(r"^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[A-Z0-9]{2}$")
RE_RFC_FISICA        = re.compile(r"^[A-ZÑ&]{4}[0-9]{6}[A-Z0-9]{3}$")
RE_RFC_MORAL         = re.compile(r"^[A-ZÑ&]{3}[0-9]{6}[A-Z0-9]{3}$")


# ============================================================
# FILTROS EN TIEMPO REAL
# ============================================================
def filtrar_letras(texto: str) -> str:
    """Permite solo letras (con acentos y ñ) y espacios."""
    return RE_SOLO_LETRAS.sub("", texto or "")

def filtrar_numeros(texto: str) -> str:
    """Permite solo dígitos."""
    return RE_SOLO_NUMEROS.sub("", texto or "")

def filtrar_numeros_decimal(texto: str) -> str:
    """Permite dígitos y un solo punto decimal."""
    if not texto:
        return ""
    limpio = RE_NUMEROS_DECIMAL.sub("", texto)
    if limpio.count(".") > 1:
        partes = limpio.split(".")
        limpio = partes[0] + "." + "".join(partes[1:])
    return limpio

def filtrar_letras_numeros(texto: str) -> str:
    """Permite letras, números y espacios."""
    return RE_LETRAS_NUMEROS.sub("", texto or "")

def filtrar_presion(texto: str) -> str:
    """Permite dígitos y la barra '/'. Ejemplo: 120/80"""
    return RE_PRESION.sub("", texto or "")

def filtrar_lote(texto: str) -> str:
    """Permite letras, números y guion. Ejemplo: L-001"""
    return RE_LOTE.sub("", (texto or "").upper())

def filtrar_dosis(texto: str) -> str:
    """Permite letras, números, espacios y signos comunes en dosis."""
    return RE_DOSIS.sub("", texto or "")

def filtrar_direccion(texto: str) -> str:
    """Permite letras, números, espacios y signos comunes en direcciones."""
    return RE_DIRECCION.sub("", texto or "")

def filtrar_curp(texto: str) -> str:
    """CURP: siempre mayúsculas, sin espacios, máx 18 caracteres."""
    return re.sub(r"[^A-Z0-9]", "", (texto or "").upper())[:18]

def filtrar_rfc(texto: str) -> str:
    """RFC: siempre mayúsculas, sin espacios, máx 13 caracteres."""
    return re.sub(r"[^A-ZÑ&0-9]", "", (texto or "").upper())[:13]


# ============================================================
# UTILIDADES DE FECHA
# ============================================================
def _parse_fecha(s):
    """Convierte 'AAAA-MM-DD' a date. None si falla."""
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de fecha de nacimiento (str o date)."""
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = _parse_fecha(fecha_nacimiento)
    if not fecha_nacimiento:
        return None
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


# ============================================================
# VALIDACIONES FINALES
# ============================================================
def validar_nombre(valor, nombre_campo="Nombre", min_len=2):
    valor = (valor or "").strip()
    if not valor:
        return False, f"{nombre_campo} es obligatorio."
    if len(valor) < min_len:
        return False, f"{nombre_campo} debe tener al menos {min_len} caracteres."
    if RE_SOLO_LETRAS.search(valor):
        return False, f"{nombre_campo} solo puede contener letras."
    return True, ""

def validar_entero(valor, nombre_campo="Campo", min_val=None, max_val=None):
    if valor is None or str(valor).strip() == "":
        return False, f"{nombre_campo} es obligatorio."
    try:
        n = int(str(valor).strip())
    except ValueError:
        return False, f"{nombre_campo} debe ser un número entero."
    if min_val is not None and n < min_val:
        return False, f"{nombre_campo} debe ser mayor o igual a {min_val}."
    if max_val is not None and n > max_val:
        return False, f"{nombre_campo} debe ser menor o igual a {max_val}."
    return True, ""

def validar_decimal(valor, nombre_campo="Campo", min_val=None, max_val=None, opcional=False):
    s = str(valor or "").strip()
    if not s:
        if opcional:
            return True, ""
        return False, f"{nombre_campo} es obligatorio."
    try:
        n = float(s)
    except ValueError:
        return False, f"{nombre_campo} debe ser un número."
    if min_val is not None and n < min_val:
        return False, f"{nombre_campo} debe ser mayor o igual a {min_val}."
    if max_val is not None and n > max_val:
        return False, f"{nombre_campo} debe ser menor o igual a {max_val}."
    return True, ""

def validar_email(valor, opcional=True):
    s = (valor or "").strip()
    if not s:
        return (True, "") if opcional else (False, "Correo es obligatorio.")
    if not RE_EMAIL.match(s):
        return False, "Formato de correo inválido (ej: nombre@dominio.com)."
    if len(s) > 150:
        return False, "Correo demasiado largo (máx 150 caracteres)."
    return True, ""

def validar_telefono(valor, opcional=True, longitud=10):
    s = (valor or "").strip()
    if not s:
        return (True, "") if opcional else (False, "Teléfono es obligatorio.")
    if not s.isdigit():
        return False, "Teléfono solo debe contener números."
    if len(s) != longitud:
        return False, f"Teléfono debe tener exactamente {longitud} dígitos."
    return True, ""

def validar_curp(valor, genero=None):
    """Valida formato CURP. Si pasas género, valida que el carácter 11 (H/M) coincida."""
    s = (valor or "").strip().upper()
    if len(s) != 18:
        return False, "CURP debe tener exactamente 18 caracteres."
    if not RE_CURP.match(s):
        return False, "CURP no tiene formato válido."

    # Validar coherencia con el género (carácter en posición 10, índice 10)
    if genero:
        sexo_curp = s[10]
        if genero == "Masculino" and sexo_curp != "H":
            return False, "La CURP indica sexo Femenino pero seleccionaste Masculino."
        if genero == "Femenino" and sexo_curp != "M":
            return False, "La CURP indica sexo Masculino pero seleccionaste Femenino."

    return True, ""

def validar_rfc(valor):
    s = (valor or "").strip().upper()
    if len(s) not in (12, 13):
        return False, "RFC debe tener 12 o 13 caracteres."
    if len(s) == 13 and not RE_RFC_FISICA.match(s):
        return False, "RFC de persona física no tiene formato válido."
    if len(s) == 12 and not RE_RFC_MORAL.match(s):
        return False, "RFC de persona moral no tiene formato válido."
    return True, ""

def validar_presion(valor, opcional=True):
    s = (valor or "").strip()
    if not s:
        return (True, "") if opcional else (False, "Presión es obligatoria.")
    if not re.match(r"^\d{2,3}/\d{2,3}$", s):
        return False, "Presión debe tener formato 120/80."
    # Rangos razonables
    try:
        sistolica, diastolica = s.split("/")
        sistolica = int(sistolica)
        diastolica = int(diastolica)
        if not (50 <= sistolica <= 250):
            return False, "Presión sistólica fuera de rango (50-250)."
        if not (30 <= diastolica <= 150):
            return False, "Presión diastólica fuera de rango (30-150)."
        if diastolica >= sistolica:
            return False, "La presión sistólica debe ser mayor que la diastólica."
    except ValueError:
        return False, "Presión inválida."
    return True, ""

def validar_cedula_profesional(valor, requerida=False):
    s = (valor or "").strip()
    if not s:
        return (True, "") if not requerida else (False, "Cédula profesional es obligatoria.")
    if not s.isdigit():
        return False, "Cédula solo debe contener números."
    if not (7 <= len(s) <= 8):
        return False, "Cédula debe tener entre 7 y 8 dígitos."
    return True, ""

def validar_fecha(valor, nombre_campo="Fecha"):
    s = (valor or "").strip()
    if not s:
        return False, f"{nombre_campo} es obligatoria."
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return False, f"{nombre_campo} debe tener formato AAAA-MM-DD."
    f = _parse_fecha(s)
    if not f:
        return False, f"{nombre_campo} no es una fecha válida."
    return True, ""


def validar_fecha_pasada(valor, nombre_campo="Fecha"):
    """Valida que la fecha sea válida Y anterior o igual a hoy."""
    ok, msg = validar_fecha(valor, nombre_campo)
    if not ok:
        return False, msg
    f = _parse_fecha(valor)
    if f > date.today():
        return False, f"{nombre_campo} no puede ser una fecha futura."
    return True, ""


def validar_fecha_futura(valor, nombre_campo="Fecha", incluir_hoy=True):
    """Valida que la fecha sea posterior (o igual) a hoy. Útil para caducidad."""
    ok, msg = validar_fecha(valor, nombre_campo)
    if not ok:
        return False, msg
    f = _parse_fecha(valor)
    hoy = date.today()
    if incluir_hoy:
        if f < hoy:
            return False, f"{nombre_campo} no puede ser anterior a hoy."
    else:
        if f <= hoy:
            return False, f"{nombre_campo} debe ser posterior a hoy."
    return True, ""


def validar_edad_coherente(edad, fecha_nacimiento, tolerancia=1):
    """Verifica que la edad escrita coincida (±tolerancia años) con la fecha de nacimiento."""
    try:
        edad_int = int(str(edad).strip())
    except (ValueError, TypeError):
        return False, "Edad inválida."

    edad_real = calcular_edad(fecha_nacimiento)
    if edad_real is None:
        return False, "Fecha de nacimiento inválida."

    if abs(edad_int - edad_real) > tolerancia:
        return False, (
            f"La edad ({edad_int}) no coincide con la fecha de nacimiento "
            f"({edad_real} años calculados)."
        )
    return True, ""


def validar_mayor_edad_trabajador(fecha_nacimiento, edad_minima=18):
    """Verifica que un trabajador tenga al menos la edad mínima."""
    edad = calcular_edad(fecha_nacimiento)
    if edad is None:
        return False, "Fecha de nacimiento inválida."
    if edad < edad_minima:
        return False, f"El trabajador debe tener al menos {edad_minima} años."
    if edad > 100:
        return False, "Edad fuera de rango (¿fecha de nacimiento correcta?)."
    return True, ""


def validar_fecha_ingreso(fecha_ingreso, fecha_nacimiento):
    """Verifica que fecha_ingreso sea posterior a fecha_nacimiento + 18 años y no futura."""
    ok, msg = validar_fecha_pasada(fecha_ingreso, "Fecha de ingreso")
    if not ok:
        return False, msg

    f_ing = _parse_fecha(fecha_ingreso)
    f_nac = _parse_fecha(fecha_nacimiento)
    if not f_nac:
        return True, ""  # Si la fecha_nac falla, ya se valida en otro lado

    diferencia_anios = (f_ing - f_nac).days / 365.25
    if diferencia_anios < 18:
        return False, "La fecha de ingreso debe ser al menos 18 años después de la fecha de nacimiento."

    return True, ""

# ============================================================
# EFECTOS PARA FLET
# ============================================================
def aplicar_error(textfield, mensaje):
    """Marca un TextField como inválido (borde rojo + helper text rojo)."""
    textfield.error_text = mensaje
    textfield.border_color = "red"

def limpiar_error(textfield):
    """Quita el estado de error del TextField."""
    textfield.error_text = None
    textfield.border_color = None

def validar_direccion_completa(valor):
    """Verifica que la dirección contenga al menos 3 palabras (calle, número, colonia) y un número."""
    s = (valor or "").strip()
    if not s:
        return False, "La calle, número y colonia son obligatorios."
    
    # Verificar que tenga al menos un número (para el número de casa)
    if not re.search(r'\d', s):
        return False, "La dirección debe contener un número (ej. #123)."
        
    # Verificar que tenga al menos 3 partes (ej. 'Calle', '12', 'Centro')
    if len(s.split()) < 3:
        return False, "Debes incluir calle, número y colonia separados por espacios."
        
    return True, ""

def validar_nombre_medicamento(valor, min_len=2):
    valor = (valor or "").strip()
    if not valor:
        return False, "El nombre del medicamento es obligatorio."
    if len(valor) < min_len:
        return False, f"El nombre debe tener al menos {min_len} caracteres."
    
    # Permitir letras, números, espacios y guiones (Rechaza símbolos extraños como @, #, $, etc.)
    if re.search(r"[^A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s\-]", valor):
        return False, "El nombre del medicamento contiene caracteres no válidos."
    return True, ""

def validar_formato_lote(valor):
    """Valida que el lote tenga el formato exacto de L seguido de 3 números (Ej: L001, L999)"""
    valor = (valor or "").strip().upper() # Lo convertimos a mayúscula por si escribieron 'l' minúscula
    
    if not valor:
        return False, "El lote es obligatorio."
    
    # ^L significa "Empieza con L"
    # \d{3} significa "Exactamente 3 dígitos (0-9)"
    # $ significa "Termina ahí"
    if not re.match(r"^L\d{3}$", valor):
        return False, "Formato de lote inválido. Debe ser 'L' seguido de 3 números (Ej: L001)."
    
    return True, ""
