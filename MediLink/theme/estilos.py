import flet as ft

# ==========================================
# 1. DEFINICIÓN DE LA PALETA DE COLORES
# ==========================================

# Paleta 1 (Tonos Azules)
COLOR_PRIMARIO = "#004AAD"       # Para barras de navegación y botones principales (Guardar, Registrar) [cite: 1]
COLOR_SECUNDARIO = "#2D9CDB"     # Para títulos de secciones o botones de acción secundaria [cite: 1]
COLOR_FONDO = "#F4F7F6"          # Color general del lienzo para que la vista descanse [cite: 1]
COLOR_TEXTO = "#333333"          # Para lectura de datos del paciente y diagnósticos [cite: 1]
COLOR_EXITO = "#27AE60"          # Para confirmación de transacciones y altas exitosas [cite: 1]
COLOR_ALERTA = "#EB5757"         # Para alertas de stock de medicamentos o campos obligatorios vacíos [cite: 1]

# Paleta 2 (Tonos Turquesa y Neutros)
COLOR_PRIMARIO_ALT = "#14B8A6"   # Para identidad visual de la app y elementos destacados [cite: 2]
COLOR_ACENTO = "#0F172A"         # Para menús laterales y texto de alta jerarquía (Nombres de doctores) [cite: 2]
COLOR_SUPERFICIE = "#FFFFFF"     # Para tarjetas de información (Cards) para pacientes o medicamentos [cite: 2]
COLOR_RESALTADO = "#E2E8F0"      # Para bordes de tablas y separadores en la gestión de personal [cite: 2]
COLOR_ATENCION = "#F59E0B"       # Para recordatorios de diagnósticos pendientes o bajo inventario [cite: 2]


# ==========================================
# 2. CONFIGURACIÓN DEL TEMA GENERAL
# ==========================================

# Combinamos los colores en el tema principal de la página
tema_medico = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=COLOR_PRIMARIO, 
        secondary=COLOR_SECUNDARIO,
        surface=COLOR_SUPERFICIE,
        error=COLOR_ALERTA,
    ),
    text_theme=ft.TextTheme(
        # Nombres de doctores o títulos principales
        title_large=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=COLOR_ACENTO),
        # Lectura de datos del paciente
        body_medium=ft.TextStyle(size=14, color=COLOR_TEXTO)
    )
)

# ==========================================
# 3. ESTILOS ESPECÍFICOS PARA COMPONENTES
# ==========================================

# Estilo para botones como "Guardar" o "Registrar"
estilo_boton_principal = ft.ButtonStyle(
    color=ft.Colors.WHITE,
    bgcolor=COLOR_PRIMARIO,
    padding=15,
    shape=ft.RoundedRectangleBorder(radius=8)
)

# Estilo para botones secundarios
estilo_boton_secundario = ft.ButtonStyle(
    color=ft.Colors.WHITE,
    bgcolor=COLOR_SECUNDARIO,
    padding=15,
    shape=ft.RoundedRectangleBorder(radius=8)
)

# Estilo para las tarjetas (Cards) de pacientes o medicamentos
estilo_tarjeta = {
    "padding": 20,
    "border_radius": 10,
    "bgcolor": COLOR_SUPERFICIE,
    # Se usa el color de resaltado para el borde de la tarjeta
    "border": ft.border.all(1, COLOR_RESALTADO),
    "shadow": ft.BoxShadow(spread_radius=1, blur_radius=5, color=COLOR_RESALTADO)
}