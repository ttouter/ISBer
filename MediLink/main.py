import flet as ft
from views.Cliente import cliente_view
from views.Medicamento import medicamento_view
from views.RecetaCompleta import receta_completa_view
from views.Altatrabajadores import alta_trabajadores_view
from views.venta import caja_view
from views.GestionPersonal import gestion_personal_view
from theme.estilos import tema_medico, COLOR_FONDO

def main(page: ft.Page):
    page.title = "MediLink - Sistema Médico"
    page.window.width = 950
    page.window.height = 650
    page.theme_mode = ft.ThemeMode.LIGHT
    # Inicializamos la variable del rol directamente en el objeto 'page'
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
                                ft.Icon(ft.Icons.LOCAL_HOSPITAL_ROUNDED, size=80, color=ft.Colors.BLUE_700),
                                ft.Text("MediLink", size=35, weight="bold", color=ft.Colors.BLUE_800),
                                ft.Text("Gestión Médica Integral", size=16, color=ft.Colors.GREY_600),
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
                                        shape=ft.RoundedRectangleBorder(radius=10),
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
        
        # Filtramos los botones según el rol almacenado
        botones_permitidos = []

        if page.rol_actual == "Administrador":
            botones_permitidos = [btn1, btn2, btn3, btn_4, btn_5]
        elif page.rol_actual == "Médico General":
            botones_permitidos = [btn1, btn2, btn3]
        elif page.rol_actual == "Recepcionista":
            botones_permitidos = [btn1, btn_5]

        # Contenido dinámico del Dashboard
        content = ft.Column(
            [
                ft.Text(f"Bienvenido - Panel de {page.rol_actual}", size=22, weight="bold"),
                ft.Divider(),
                ft.Row(
                    botones_permitidos, 
                    alignment=ft.MainAxisAlignment.CENTER, 
                    spacing=30,
                    wrap=True
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        page.views.append(
            ft.View(
                route="/dashboard",
                controls=[
                    header,
                    content
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
        page.views.append(alta_trabajadores_view(page, ir_gestion_personal, datos_empleado))
        page.update()

    # ==========================================
    # 4. COMPONENTES DE LA INTERFAZ (UI)
    # ==========================================
    
    # Header con botón de Cerrar Sesión
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text("MediLink", size=24, weight="bold", color=ft.Colors.BLUE_400),
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
        content=ft.Column([ft.Icon(ft.Icons.PERSON, size=40), ft.Text("Paciente")], horizontal_alignment="center"),
        padding=20, border_radius=10, ink=True, on_click=ir_cliente, width=150, height=120, bgcolor=ft.Colors.BLUE_100
    )
    btn2 = ft.Container(
        content=ft.Column([ft.Icon(ft.Icons.MEDICATION, size=40), ft.Text("Medicamentos")], horizontal_alignment="center"),
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
        content=ft.Column([ft.Icon(ft.Icons.MANAGE_ACCOUNTS, size=40), ft.Text("Personal")], horizontal_alignment="center"),
        padding=20, border_radius=10, ink=True, on_click=ir_gestion_personal, width=150, height=120, bgcolor=ft.Colors.PURPLE_100
    )
    btn_5 = ft.Container(
        content=ft.Column([ft.Icon(ft.Icons.MONEY, size=40), ft.Text("Venta")], horizontal_alignment="center"),
        padding=20, border_radius=10, ink=True, on_click=ir_venta, width=150, height=120, bgcolor=ft.Colors.TEAL_100
    )

    # Ejecución inicial: Cargamos la pantalla de Login
    cargar_login()

# Punto de entrada de la aplicación
ft.run(main)