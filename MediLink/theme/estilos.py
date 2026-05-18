import flet as ft

# ==========================================
# 1. DEFINICIÓN DE LA PALETA DE COLORES
# ==========================================
COLOR_PRIMARIO      = "#004AAD"
COLOR_SECUNDARIO    = "#2D9CDB"
COLOR_FONDO         = "#F4F7F6"
COLOR_TEXTO         = "#333333"
COLOR_EXITO         = "#27AE60"
COLOR_ALERTA        = "#EB5757"

COLOR_PRIMARIO_ALT  = "#14B8A6"
COLOR_ACENTO        = "#0F172A"
COLOR_SUPERFICIE    = "#FFFFFF"
COLOR_RESALTADO     = "#E2E8F0"
COLOR_ATENCION      = "#F59E0B"


# ==========================================
# 2. CONFIGURACIÓN DEL TEMA GENERAL
# ==========================================
tema_medico = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=COLOR_PRIMARIO,
        secondary=COLOR_SECUNDARIO,
        surface=COLOR_SUPERFICIE,
        error=COLOR_ALERTA,
    ),
    text_theme=ft.TextTheme(
        title_large=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color=COLOR_ACENTO),
        body_medium=ft.TextStyle(size=14, color=COLOR_TEXTO)
    )
)


# ==========================================
# 3. ESTILOS ESPECÍFICOS PARA COMPONENTES
# ==========================================
estilo_boton_principal = ft.ButtonStyle(
    color=ft.Colors.WHITE,
    bgcolor=COLOR_PRIMARIO,
    padding=15,
    shape=ft.RoundedRectangleBorder(radius=8)
)

estilo_boton_secundario = ft.ButtonStyle(
    color=ft.Colors.WHITE,
    bgcolor=COLOR_SECUNDARIO,
    padding=15,
    shape=ft.RoundedRectangleBorder(radius=8)
)

estilo_tarjeta = {
    "padding": 20,
    "border_radius": 10,
    "bgcolor": COLOR_SUPERFICIE,
    "border": ft.border.all(1, COLOR_RESALTADO),
    "shadow": ft.BoxShadow(spread_radius=1, blur_radius=5, color=COLOR_RESALTADO)
}


# ==========================================
# 4. APPBAR UNIFORME PARA TODAS LAS VISTAS
# ==========================================
def crear_appbar(titulo: str, volver_fn) -> ft.AppBar:
    """Barra superior idéntica en todas las pantallas."""
    return ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=ft.Colors.WHITE,
            tooltip="Volver",
            on_click=volver_fn,
        ),
        leading_width=50,
        title=ft.Text(
            titulo,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            size=18,
        ),
        center_title=False,
        bgcolor=COLOR_PRIMARIO,
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LOCAL_HOSPITAL, color=ft.Colors.WHITE70, size=16),
                    ft.Text("MediLink", color=ft.Colors.WHITE70, size=13),
                ], spacing=4),
                padding=ft.Padding(0, 0, 20, 0),
            )
        ],
    )