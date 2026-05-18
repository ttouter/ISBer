import flet as ft
import asyncio
from logic.gestor_trabajadores import registrar_trabajador, actualizar_trabajador
from logic.validators import (
    filtrar_letras, filtrar_numeros, filtrar_curp, filtrar_rfc,
    filtrar_direccion, validar_direccion_completa
)
from theme.estilos import COLOR_ALERTA, COLOR_EXITO, estilo_boton_principal
from data.ubicaciones import PAISES, obtener_estados, obtener_ciudades
from theme.estilos import COLOR_ALERTA, COLOR_EXITO, estilo_boton_principal
from theme.estilos import COLOR_ALERTA, COLOR_EXITO, estilo_boton_principal, crear_appbar


def alta_trabajadores_view(page: ft.Page, volver, datos_edicion=None):

    # ============================================================
    # FACTORY DE TEXTFIELDS CON FILTROS
    # ============================================================
    def tf_letras(label, expand=True):
        tf = ft.TextField(label=label, expand=expand)

        def _f(e):
            limpio = filtrar_letras(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    def tf_numeros(label, expand=True, max_len=None,
                   keyboard=ft.KeyboardType.NUMBER):
        tf = ft.TextField(label=label, expand=expand, keyboard_type=keyboard)

        def _f(e):
            limpio = filtrar_numeros(tf.value)
            if max_len:
                limpio = limpio[:max_len]
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    def tf_curp(label, expand=True):
        tf = ft.TextField(label=label, expand=expand,
                          hint_text="18 caracteres",
                          capitalization=ft.TextCapitalization.CHARACTERS)

        def _f(e):
            limpio = filtrar_curp(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    def tf_rfc(label, expand=True):
        tf = ft.TextField(label=label, expand=expand,
                          hint_text="12 o 13 caracteres",
                          capitalization=ft.TextCapitalization.CHARACTERS)

        def _f(e):
            limpio = filtrar_rfc(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    def tf_direccion(label, expand=True):
        tf = ft.TextField(label=label, expand=expand, multiline=True,
                          min_lines=1, max_lines=3)

        def _f(e):
            limpio = filtrar_direccion(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    # ============================================================
    # CAMPOS DEL FORMULARIO (UNA SOLA VEZ)
    # ============================================================
    nombre = tf_letras("Nombre(s)")
    ap_paterno = tf_letras("Apellido Paterno")
    ap_materno = tf_letras("Apellido Materno")

    fecha_nac = ft.TextField(label="Fecha de Nacimiento",
                             hint_text="AAAA-MM-DD", read_only=True, expand=True)
    fecha_ingreso = ft.TextField(label="Fecha de Ingreso",
                                 hint_text="AAAA-MM-DD", read_only=True, expand=True)

    def cambiar_fecha_nac(e):
        if date_picker_nac.value:
            fecha_nac.value = date_picker_nac.value.strftime("%Y-%m-%d")
        page.update()

    def cambiar_fecha_ingre(e):
        if date_picker_ingreso.value:
            fecha_ingreso.value = date_picker_ingreso.value.strftime(
                "%Y-%m-%d")
        page.update()

    date_picker_nac = ft.DatePicker(on_change=cambiar_fecha_nac)
    date_picker_ingreso = ft.DatePicker(on_change=cambiar_fecha_ingre)
    page.overlay.extend([date_picker_nac, date_picker_ingreso])

    btn_fecha_nac = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: (
            setattr(date_picker_nac, "open", True), page.update())
    )
    btn_fecha_ingre = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: (setattr(date_picker_ingreso,
                            "open", True), page.update())
    )

    genero = ft.Dropdown(
        label="Género", expand=True,
        options=[
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Femenino"),
        ]
    )

    curp = tf_curp("CURP")
    rfc = tf_rfc("RFC")

    # ============================================================
    # UBICACIÓN (dropdowns dependientes: país → estado → ciudad)
    # ============================================================
    pais   = None
    estado = None
    ciudad = None

    def cambiar_pais(e):
        estado.options = [ft.dropdownm2.Option(s) for s in obtener_estados(pais.value)]
        estado.value   = None
        ciudad.options = []
        ciudad.value   = None
        estado.update()
        ciudad.update()

    def cambiar_estado(e):
        if estado.value:
            ciudad.options = [ft.dropdownm2.Option(c) for c in obtener_ciudades(estado.value)]
        else:
            ciudad.options = []
        ciudad.value = None
        ciudad.update()

    pais = ft.DropdownM2(
        label="País", expand=True,
        options=[ft.dropdownm2.Option(p) for p in PAISES],
        value="México",
        on_change=cambiar_pais,
    )

    estado = ft.DropdownM2(
        label="Estado", expand=True,
        options=[ft.dropdownm2.Option(s) for s in obtener_estados("México")],
        on_change=cambiar_estado,
    )

    ciudad = ft.DropdownM2(
        label="Ciudad", expand=True,
        options=[],
    )

    direccion = tf_direccion("Calle, número y colonia *")

    telefono = tf_numeros("Teléfono", max_len=10,
                          keyboard=ft.KeyboardType.PHONE)
    correo = ft.TextField(label="Correo electrónico", expand=True,
                          keyboard_type=ft.KeyboardType.EMAIL)

    cedula = tf_numeros("Cédula Profesional", max_len=8)
    cedula.helper_text = "Solo para Médico General"
    cedula.disabled = True  # Inicia deshabilitada hasta seleccionar puesto

    # ============================================================
    # CAMBIO DE PUESTO -> activa/desactiva cédula
    # ============================================================
    def cambiar_puesto(e):
        if puesto.value == "Médico General":
            cedula.disabled = False
            cedula.label = "Cédula Profesional *"
            cedula.helper_text = "Cédula obligatoria para Médico General"
            cedula.border_color = ft.Colors.BLUE_400
        else:
            cedula.disabled = True
            cedula.value = ""
            cedula.label = "Cédula Profesional"
            cedula.helper_text = "Solo para Médico General"
            cedula.border_color = None
        page.update()

    puesto = ft.Dropdown(
        label="Puesto", expand=True,
        options=[
            ft.dropdown.Option("Médico General"),
            ft.dropdown.Option("Farmacéutico"),
            ft.dropdown.Option("Recepcionista"),
            ft.dropdown.Option("Administrador"),
            ft.dropdown.Option("Mantenimiento"),
        ],
        on_select=cambiar_puesto  # ¡on_change, no on_select!
    )

    turno = ft.Dropdown(
        label="Turno", expand=True,
        options=[
            ft.dropdown.Option("Matutino"),
            ft.dropdown.Option("Vespertino"),
            ft.dropdown.Option("Nocturno"),
            ft.dropdown.Option("Mixto"),
        ],
    )

    mensaje = ft.Text()

    # ============================================================
    # MODO EDICIÓN: precargar datos
    # ============================================================
    if datos_edicion:
        nombre.value = datos_edicion.get('nombre', '') or ''
        ap_paterno.value = datos_edicion.get('ap_paterno', '') or ''
        ap_materno.value = datos_edicion.get('ap_materno', '') or ''
        fecha_nac.value = str(datos_edicion.get('fecha_nacimiento', '') or '')
        genero.value = datos_edicion.get('genero')
        curp.value = datos_edicion.get('curp', '') or ''
        rfc.value = datos_edicion.get('rfc', '') or ''

        # Parsear dirección guardada (formato: "calle | Ciudad | Estado | País")
        dir_guardada = datos_edicion.get('direccion', '') or ''
        partes = [p.strip() for p in dir_guardada.split('|')]
        direccion.value = partes[0] if len(partes) > 0 else ''
        if len(partes) >= 4:
            pais.value   = partes[3]
            estado.options = [ft.dropdownm2.Option(s) for s in obtener_estados(partes[3])]
            estado.value = partes[2]
            ciudad.options = [ft.dropdownm2.Option(c) for c in obtener_ciudades(partes[2])]
            ciudad.value = partes[1]

        telefono.value = datos_edicion.get('telefono', '') or ''
        correo.value = datos_edicion.get('correo', '') or ''
        puesto.value = datos_edicion.get('puesto')
        cedula.value = datos_edicion.get('cedula_profesional', '') or ''
        turno.value = datos_edicion.get('turno')
        fecha_ingreso.value = str(datos_edicion.get('fecha_ingreso', '') or '')

        # Sincronizar estado de cédula según el puesto cargado
        if puesto.value == "Médico General":
            cedula.disabled = False
            cedula.label = "Cédula Profesional *"
            cedula.helper_text = "Cédula obligatoria para Médico General"
            cedula.border_color = ft.Colors.BLUE_400

    # ============================================================
    # GUARDAR
    # ============================================================
    async def limpiar_mensaje():
        await asyncio.sleep(4)
        mensaje.value = ""
        page.update()

    def guardar(e):

        ok_dir, msg_dir = validar_direccion_completa(direccion.value)
        if not ok_dir:
            mensaje.value = msg_dir
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar_mensaje)
            return
        
        # Armar dirección completa (formato: "calle | Ciudad | Estado | País")
        partes_dir = [
            (direccion.value or "").strip(),
            (ciudad.value or "").strip(),
            (estado.value or "").strip(),
            (pais.value or "").strip(),
        ]
        direccion_completa = " | ".join(partes_dir)

        if datos_edicion:
            exito, msj_res = actualizar_trabajador(
                datos_edicion['id_trabajador'],
                nombre.value, ap_paterno.value, ap_materno.value,
                fecha_nac.value, genero.value, curp.value, rfc.value,
                direccion_completa, telefono.value, correo.value,
                puesto.value, cedula.value, turno.value, fecha_ingreso.value
            )
        else:
            exito, msj_res = registrar_trabajador(
                nombre.value, ap_paterno.value, ap_materno.value,
                fecha_nac.value, genero.value, curp.value, rfc.value,
                direccion_completa, telefono.value, correo.value,
                puesto.value, cedula.value, turno.value, fecha_ingreso.value
            )

        mensaje.value = msj_res
        mensaje.color = "green" if exito else "red"

        if exito and not datos_edicion:
            for campo in [nombre, ap_paterno, ap_materno, fecha_nac,
                          curp, rfc, direccion, telefono, correo,
                          cedula, fecha_ingreso]:
                campo.value = ""
            puesto.value = None
            genero.value = None
            turno.value = None
            pais.value = "México"
            estado.value = None
            ciudad.value = None
            ciudad.options = []
            cedula.disabled = True
            cedula.label = "Cédula Profesional"
            cedula.helper_text = "Solo para Médico General"
            cedula.border_color = None

        page.update()
        page.run_task(limpiar_mensaje)

    titulo_vista = "Editar Personal Médico" if datos_edicion else "Registro de Personal Médico"
    texto_boton = "Guardar Cambios" if datos_edicion else "Guardar"
    btn_guardar = ft.ElevatedButton(texto_boton, icon=ft.Icons.SAVE,
                                    on_click=guardar, style=estilo_boton_principal)

    # ============================================================
    # LAYOUT
    # ============================================================
    return ft.View(
        route="/alta_trabajadores",
        appbar=crear_appbar(titulo_vista, volver),
        controls=[
            ft.Container(
                expand=True, padding=20,
                content=ft.Column([
                    ft.Card(
                        elevation=5, expand=True,
                        content=ft.Container(
                            expand=True, padding=30,
                            content=ft.Column([
                                ft.Divider(),
                                ft.Text("Datos Personales", weight="bold"),
                                ft.Row(
                                    [nombre, ap_paterno, ap_materno], spacing=15),
                                ft.Row(
                                    [fecha_nac, btn_fecha_nac, genero], spacing=15),
                                ft.Row([curp, rfc], spacing=15),
                                ft.Row([pais, estado, ciudad], spacing=15),
                                ft.Row([direccion], spacing=15),
                                ft.Row([telefono, correo], spacing=15),
                                ft.Divider(),
                                ft.Text("Datos Profesionales", weight="bold"),
                                ft.Row([puesto, cedula], spacing=15),
                                ft.Row([turno, fecha_ingreso,
                                       btn_fecha_ingre], spacing=15),
                                ft.Divider(),
                                ft.Row(
                                    [btn_guardar],
                                    alignment=ft.MainAxisAlignment.END
                                ),
                                mensaje
                            ], spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)
                        )
                    )
                ], expand=True)
            )
        ]
    )
