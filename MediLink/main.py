import flet as ft
from datetime import datetime
from views.Cliente import cliente_view
from views.Medicamento import medicamento_view
from views.RecetaCompleta import receta_completa_view
from views.Altatrabajadores import alta_trabajadores_view
from views.venta import caja_view
from views.GestionPersonal import gestion_personal_view
from theme.estilos import tema_medico, COLOR_FONDO


def main(page: ft.Page):
    page.title = "MediLink - Sistema Médico"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = tema_medico
    page.bgcolor = COLOR_FONDO

    page.window.width = 1280
    page.window.height = 800
    page.window.min_width = 1000
    page.window.min_height = 680
    page.window.resizable = True

    page.rol_actual = "Ninguno"

    # ==========================================
    # 1. PANTALLA DE LOGIN
    # ==========================================
    def cargar_login(e=None):
        page.views.clear()

        txt_usuario = ft.TextField(
            label="Usuario",
            width=300,
            prefix_icon=ft.Icons.PERSON_OUTLINE
        )
        txt_password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            prefix_icon=ft.Icons.LOCK_OUTLINE
        )
        lbl_mensaje = ft.Text(color="red", weight="bold")

        def intentar_login(e):
            # Diccionario de usuarios de prueba (Simulando la BD)
            usuarios_prueba = {
                "admin": {"pass": "123", "rol": "Administrador"},
                "medico": {"pass": "123", "rol": "Médico General"},
                "recepcion": {"pass": "123", "rol": "Recepcionista"}
            }

            user = txt_usuario.value.lower().strip()
            pwd = txt_password.value.strip()

            if user in usuarios_prueba and usuarios_prueba[user]["pass"] == pwd:
                # Login Exitoso: Guardamos el rol y entramos al sistema
                page.rol_actual = usuarios_prueba[user]["rol"]
                cargar_inicio()
            else:
                lbl_mensaje.value = "Credenciales incorrectas. Intente de nuevo."
                page.update()

        # Diseño de la vista de Login
        page.views.append(
            ft.View(
                route="/login",
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.LOCAL_HOSPITAL_ROUNDED,
                                        size=80, color=ft.Colors.BLUE_700),
                                ft.Text("MediLink", size=35, weight="bold",
                                        color=ft.Colors.BLUE_800),
                                ft.Text("Gestión Médica Integral",
                                        size=16, color=ft.Colors.GREY_600),
                                ft.Divider(height=30, color="transparent"),
                                txt_usuario,
                                txt_password,
                                lbl_mensaje,
                                ft.Button(
                                    "Iniciar Sesión",
                                    on_click=intentar_login,
                                    width=300,
                                    height=50,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(
                                            radius=10),
                                        bgcolor=ft.Colors.BLUE_700,
                                        color=ft.Colors.WHITE
                                    )
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
                    )
                ]
            )
        )
        page.update()

    # ==========================================
    # 2. PANTALLA PRINCIPAL (DASHBOARD)
    # ==========================================
    def cargar_inicio(e=None):
        page.views.clear()

        now = datetime.now()
        hora = now.strftime("%H:%M")
        fecha = now.strftime("%d/%m/%Y")

        iconos_rol = {
            "Administrador":  ft.Icons.ADMIN_PANEL_SETTINGS,
            "Médico General": ft.Icons.MEDICAL_SERVICES,
            "Recepcionista":  ft.Icons.PEOPLE_ALT,
        }

        # ── Tarjeta de módulo ────────────────────────────────────
        def tarjeta_modulo(icono, titulo, descripcion, color_icono,
                           color_borde, on_click):
            return ft.Container(
                width=230, height=155,
                border_radius=14,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(
                    1, ft.Colors.with_opacity(0.15, "#000000")),
                shadow=ft.BoxShadow(
                    blur_radius=10, spread_radius=0,
                    color=ft.Colors.with_opacity(0.10, "#000000"),
                    offset=ft.Offset(0, 3)
                ),
                ink=True,
                on_click=on_click,
                content=ft.Row([
                    # Barra de color izquierda
                    ft.Container(
                        width=6,
                        border_radius=ft.border_radius.only(
                            top_left=14, bottom_left=14),
                        bgcolor=color_borde
                    ),
                    # Contenido
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(16, 18, 16, 18),
                        content=ft.Column([
                            ft.Container(
                                width=46,
                                height=46,
                                border_radius=12,
                                bgcolor=ft.Colors.with_opacity(
                                    0.12, color_icono),
                                content=ft.Icon(
                                    icono, color=color_icono, size=26),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Container(height=10),
                            ft.Text(titulo, weight=ft.FontWeight.BOLD,
                                    size=14, color="#1A1A2E"),
                            ft.Text(descripcion, size=11,
                                    color=ft.Colors.GREY_600,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                        ], spacing=2)
                    ),
                ])
            )

        # ── Módulos por rol ──────────────────────────────────────
        modulos_por_rol = {
            "Administrador": [
                tarjeta_modulo(
                    ft.Icons.PERSON_SEARCH, "Pacientes",
                    "Registro y consulta de pacientes",
                    "#1565C0", "#1565C0", ir_cliente),
                tarjeta_modulo(
                    ft.Icons.MEDICATION, "Medicamentos",
                    "Inventario y control de stock",
                    "#2E7D32", "#2E7D32", ir_medicamento),
                tarjeta_modulo(
                    ft.Icons.RECEIPT_LONG, "Receta Médica",
                    "Generación y consulta de recetas",
                    "#E65100", "#E65100", ir_receta_completa),
                tarjeta_modulo(
                    ft.Icons.MANAGE_ACCOUNTS, "Personal Médico",
                    "Alta, edición y baja de personal",
                    "#6A1B9A", "#6A1B9A", ir_gestion_personal),
                tarjeta_modulo(
                    ft.Icons.POINT_OF_SALE, "Caja / Ventas",
                    "Cobro de consultas y medicamentos",
                    "#00695C", "#00695C", ir_venta),
            ],
            "Médico General": [
                tarjeta_modulo(
                    ft.Icons.PERSON_SEARCH, "Pacientes",
                    "Registro y consulta de pacientes",
                    "#1565C0", "#1565C0", ir_cliente),
                tarjeta_modulo(
                    ft.Icons.MEDICATION, "Medicamentos",
                    "Consultar inventario de medicamentos",
                    "#2E7D32", "#2E7D32", ir_medicamento),
                tarjeta_modulo(
                    ft.Icons.RECEIPT_LONG, "Receta Médica",
                    "Generación y consulta de recetas",
                    "#E65100", "#E65100", ir_receta_completa),
            ],
            "Recepcionista": [
                tarjeta_modulo(
                    ft.Icons.PERSON_SEARCH, "Pacientes",
                    "Registro y consulta de pacientes",
                    "#1565C0", "#1565C0", ir_cliente),
                tarjeta_modulo(
                    ft.Icons.POINT_OF_SALE, "Caja / Ventas",
                    "Cobro de consultas y medicamentos",
                    "#00695C", "#00695C", ir_venta),
            ],
        }

        tarjetas = modulos_por_rol.get(page.rol_actual, [])

        # ── Barra superior ────────────────────────────────────────
        barra_superior = ft.Container(
            padding=ft.Padding(30, 22, 30, 22),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=["#004AAD", "#1976D2"],
            ),
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LOCAL_HOSPITAL,
                                color=ft.Colors.WHITE, size=28),
                        ft.Text("MediLink", size=26,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE),
                    ], spacing=8),
                    ft.Text("Sistema de Gestión Médica Integral",
                            size=12, color=ft.Colors.WHITE70),
                ], spacing=4),
                ft.Column([
                    ft.Row([
                        ft.Icon(iconos_rol.get(page.rol_actual,
                                               ft.Icons.PERSON),
                                color=ft.Colors.WHITE70, size=18),
                        ft.Text(page.rol_actual, size=13,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.W_500),
                    ], spacing=6),
                    ft.Row([
                        ft.Icon(ft.Icons.ACCESS_TIME,
                                color=ft.Colors.WHITE70, size=14),
                        ft.Text(f"{hora}  ·  {fecha}",
                                size=12, color=ft.Colors.WHITE70),
                    ], spacing=4),
                    ft.Container(height=4),
                    ft.ElevatedButton(
                        "Cerrar sesión",
                        icon=ft.Icons.LOGOUT,
                        on_click=cargar_login,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_700,
                            bgcolor=ft.Colors.WHITE,
                            padding=ft.Padding(12, 6, 12, 6),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        height=36,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=2),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

        # ── Cuerpo ────────────────────────────────────────────────
        saludo_hora = (
            "Buenos días" if now.hour < 12
            else "Buenas tardes" if now.hour < 19
            else "Buenas noches"
        )

        cuerpo = ft.Container(
            expand=True,
            padding=ft.Padding(40, 30, 40, 30),
            content=ft.Column([
                ft.Text(f"{saludo_hora} — Panel de {page.rol_actual}",
                        size=20, weight=ft.FontWeight.W_600,
                        color="#1A1A2E"),
                ft.Text("Selecciona el módulo con el que deseas trabajar",
                        size=13, color=ft.Colors.GREY_600),
                ft.Container(height=20),
                ft.Row(
                    tarjetas,
                    wrap=True,
                    spacing=22,
                    run_spacing=22,
                ),
            ], spacing=6)
        )

        page.views.append(
            ft.View(
                route="/dashboard",
                bgcolor="#F4F7F6",
                controls=[
                    ft.Column([barra_superior, cuerpo],
                              spacing=0, expand=True)
                ]
            )
        )
        page.update()

    # ==========================================
    # 3. FUNCIONES DE NAVEGACIÓN
    # ==========================================

    def ir_cliente(e):
        page.views.clear()
        page.views.append(cliente_view(page, cargar_inicio))
        page.update()

    def ir_medicamento(e):
        page.views.clear()
        page.views.append(medicamento_view(page, cargar_inicio))
        page.update()

    def ir_receta_completa(e):
        page.views.clear()
        page.views.append(receta_completa_view(page, cargar_inicio))
        page.update()

    def ir_venta(e):
        page.views.clear()
        page.views.append(caja_view(page, cargar_inicio))
        page.update()

    def ir_gestion_personal(e):
        page.views.clear()
        page.views.append(
            gestion_personal_view(
                page,
                ir_a_alta=ir_altaTra,
                ir_a_editar=ir_editar_trabajador,
                volver=cargar_inicio
            )
        )
        page.update()

    def ir_altaTra(e):
        page.views.clear()
        page.views.append(alta_trabajadores_view(page, ir_gestion_personal))
        page.update()

    def ir_editar_trabajador(datos_empleado):
        page.views.clear()
        # Pasamos los datos del empleado a la vista de Alta para que los cargue
        page.views.append(alta_trabajadores_view(
            page, ir_gestion_personal, datos_empleado))
        page.update()

    # ==========================================
    # 4. COMPONENTES DE LA INTERFAZ (UI)
    # ==========================================

    # Header con botón de Cerrar Sesión
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("MediLink", size=24, weight="bold",
                        color=ft.Colors.BLUE_400),
                ft.TextButton(
                    "Cerrar Sesión",
                    icon=ft.Icons.LOGOUT,
                    on_click=cargar_login,
                    icon_color="red"
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.Padding(20, 10, 20, 10),
        bgcolor=ft.Colors.CYAN_200,
        border_radius=10
    )

    # Definición de Botones del Menú
    btn1 = ft.Container(
        content=ft.Column([ft.Icon(ft.Icons.PERSON, size=40), ft.Text(
            "Paciente")], horizontal_alignment="center"),
        padding=20, border_radius=10, ink=True, on_click=ir_cliente, width=150, height=120, bgcolor=ft.Colors.BLUE_100
    )
    btn2 = ft.Container(
        content=ft.Column([ft.Icon(ft.Icons.MEDICATION, size=40), ft.Text(
            "Medicamentos")], horizontal_alignment="center"),
        padding=20, border_radius=10, ink=True, on_click=ir_medicamento, width=150, height=120, bgcolor=ft.Colors.GREEN_100
    )

    btn3 = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.RECEIPT_LONG, size=40),
                ft.Text("Receta")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        border_radius=10,
        ink=True,
        on_click=ir_receta_completa,
        width=150,
        height=120,
        bgcolor=ft.Colors.ORANGE_100
    )
    btn_4 = ft.Container(
        content=ft.Column([ft.Icon(ft.Icons.MANAGE_ACCOUNTS, size=40), ft.Text(
            "Personal")], horizontal_alignment="center"),
        padding=20, border_radius=10, ink=True, on_click=ir_gestion_personal, width=150, height=120, bgcolor=ft.Colors.PURPLE_100
    )
    btn_5 = ft.Container(
        content=ft.Column([ft.Icon(ft.Icons.MONEY, size=40), ft.Text(
            "Venta")], horizontal_alignment="center"),
        padding=20, border_radius=10, ink=True, on_click=ir_venta, width=150, height=120, bgcolor=ft.Colors.TEAL_100
    )

    # Ejecución inicial: Cargamos la pantalla de Login
    cargar_login()


# Punto de entrada de la aplicación
ft.run(main)
