import flet as ft
import asyncio
from logic.gestor_clientes import registrar_cliente, actualizar_cliente
from logic.validators import (
    filtrar_letras, filtrar_numeros, filtrar_numeros_decimal, filtrar_presion, validar_direccion_completa
)
from database.consultas import (
    obtener_todos_clientes,
    buscar_clientes_por_apellido,
    obtener_historial_bd,
    deshabilitar_cliente,
    activar_cliente,
    eliminar_historial_bd,
)
from data.ubicaciones import PAISES, obtener_estados, obtener_ciudades
from theme.estilos import crear_appbar


def cliente_view(page: ft.Page, volver):

    # ============================================================
    # ESTADO
    # ============================================================
    cliente_en_edicion = {"id": None}
    state_filtro = {"filtro": "TODOS"}

    # ============================================================
    # CAMPOS CON FILTROS EN TIEMPO REAL
    # ============================================================
    def crear_textfield_letras(label, expand=True, **kwargs):
        tf = ft.TextField(label=label, expand=expand, **kwargs)
        def _filtrar(e):
            limpio = filtrar_letras(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _filtrar
        return tf

    def crear_textfield_numero_entero(label, expand=True, max_len=None, **kwargs):
        tf = ft.TextField(label=label, expand=expand,
                         keyboard_type=ft.KeyboardType.NUMBER, **kwargs)
        def _filtrar(e):
            limpio = filtrar_numeros(tf.value)
            if max_len:
                limpio = limpio[:max_len]
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _filtrar
        return tf

    def crear_textfield_numero_decimal(label, expand=True, **kwargs):
        tf = ft.TextField(label=label, expand=expand,
                         keyboard_type=ft.KeyboardType.NUMBER, **kwargs)
        def _filtrar(e):
            limpio = filtrar_numeros_decimal(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _filtrar
        return tf

    def crear_textfield_presion(label, expand=True, **kwargs):
        tf = ft.TextField(label=label, expand=expand, hint_text="120/80", **kwargs)
        def _filtrar(e):
            limpio = filtrar_presion(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _filtrar
        return tf

    # TODOS los campos llevan asterisco (*) para indicar que son obligatorios
    nombre        = crear_textfield_letras("Nombre(s) *")
    ap_paterno    = crear_textfield_letras("Apellido Paterno *")
    ap_materno    = crear_textfield_letras("Apellido Materno *")
    edad          = crear_textfield_numero_entero("Edad *", max_len=3)

    sexo = ft.DropdownM2(
        label="Sexo *", expand=True,
        options=[
            ft.dropdownm2.Option("Masculino"),
            ft.dropdownm2.Option("Femenino"),
            ft.dropdownm2.Option("Otro"),
        ]
    )

    fecha_nacimiento = ft.TextField(
        label="Fecha de nacimiento *", hint_text="AAAA-MM-DD",
        read_only=True, expand=True
    )

    peso        = crear_textfield_numero_decimal("Peso (kg) *")
    talla       = crear_textfield_numero_decimal("Talla (cm) *")
    oxigenacion = crear_textfield_numero_decimal("Oxigenación (%) *")
    presion     = crear_textfield_presion("Presión (mmHg) *")
    temperatura = crear_textfield_numero_decimal("Temperatura (°C) *")
    correo      = ft.TextField(label="Correo electrónico *", expand=True,
                               keyboard_type=ft.KeyboardType.EMAIL)

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
        label="País *", expand=True,
        options=[ft.dropdownm2.Option(p) for p in PAISES],
        value="México",
        on_change=cambiar_pais,
    )

    estado = ft.DropdownM2(
        label="Estado *", expand=True,
        options=[ft.dropdownm2.Option(s) for s in obtener_estados("México")],
        on_change=cambiar_estado,
    )

    ciudad = ft.DropdownM2(
        label="Ciudad *", expand=True,
        options=[],
    )

    direccion = ft.TextField(
        label="Calle, número y colonia *",
        multiline=True, min_lines=1, max_lines=3, expand=True
    )

    # ---- DatePicker ----
    def seleccionar_fecha(e):
        date_picker.open = True
        page.update()

    def cambiar_fecha(e):
        if date_picker.value:
            fecha_nacimiento.value = date_picker.value.strftime("%Y-%m-%d")
        page.update()

    date_picker = ft.DatePicker(on_change=cambiar_fecha)
    page.overlay.append(date_picker)

    btn_fecha = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=seleccionar_fecha)

    titulo_form = ft.Text("Registro de Cliente", size=20, weight="bold")
    aviso_obligatorios = ft.Text(
        "Todos los campos marcados con * son obligatorios.",
        size=12, italic=True, color=ft.Colors.GREY_700
    )
    texto_btn_guar = ft.Ref[ft.ElevatedButton]()
    mensaje = ft.Text()

    async def limpiar_msg():
        await asyncio.sleep(3)
        mensaje.value = ""
        page.update()

    # ============================================================
    # LIMPIAR FORMULARIO
    # ============================================================
    def limpiar_formulario():
        cliente_en_edicion["id"] = None
        titulo_form.value = "Registro de Cliente"
        for campo in [nombre, ap_paterno, ap_materno, edad, fecha_nacimiento,
                      peso, talla, oxigenacion, presion, temperatura, correo,
                      direccion]:
            campo.value = ""
        sexo.value = None
        pais.value = "México"
        estado.options = [ft.dropdownm2.Option(s) for s in obtener_estados("México")]
        estado.value = None
        ciudad.options = []
        ciudad.value = None
        if texto_btn_guar.current:
            texto_btn_guar.current.text = "Guardar"
        btn_cancelar.visible = False
        page.update()

    # ============================================================
    # CARGAR FORMULARIO EN MODO EDICIÓN
    # ============================================================
    def cargar_en_formulario(pac):
        cliente_en_edicion["id"] = pac["id_cliente"]
        titulo_form.value = "Editar Cliente"
        nombre.value           = pac.get("nombre", "")
        ap_paterno.value       = pac.get("ap_paterno", "")
        ap_materno.value       = pac.get("ap_materno", "") or ""
        edad.value             = str(pac.get("edad", ""))
        sexo.value             = pac.get("sexo")
        fecha_nacimiento.value = str(pac.get("fecha_nacimiento", ""))
        peso.value             = str(pac.get("peso", "")) if pac.get("peso") else ""
        talla.value            = str(pac.get("talla", "")) if pac.get("talla") else ""
        oxigenacion.value      = str(pac.get("oxigenacion", "")) if pac.get("oxigenacion") else ""
        presion.value          = pac.get("presion", "") or ""
        temperatura.value      = str(pac.get("temperatura", "")) if pac.get("temperatura") else ""
        correo.value           = pac.get("correo", "") or ""

        # Parsear dirección guardada (formato: "calle | Ciudad | Estado | País")
        dir_guardada = pac.get("direccion", "") or ""
        partes = [p.strip() for p in dir_guardada.split('|')]
        direccion.value = partes[0] if len(partes) > 0 else ''
        if len(partes) >= 4:
            pais.value   = partes[3]
            estado.options = [ft.dropdownm2.Option(s) for s in obtener_estados(partes[3])]
            estado.value = partes[2]
            ciudad.options = [ft.dropdownm2.Option(c) for c in obtener_ciudades(partes[2])]
            ciudad.value = partes[1]

        if texto_btn_guar.current:
            texto_btn_guar.current.text = "Guardar Cambios"
        btn_cancelar.visible = True
        page.update()

    # ============================================================
    # DIÁLOGO: paciente duplicado
    # ============================================================
    info_duplicado = ft.Text("")

    def cerrar_dlg_dup(e):
        dialogo_duplicado.open = False
        page.update()

    def confirmar_guardar_aunque_dup(e):
        dialogo_duplicado.open = False
        page.update()
        _guardar_real(forzar=True)

    dialogo_duplicado = ft.AlertDialog(
        title=ft.Text("Paciente posiblemente duplicado", weight="bold"),
        content=ft.Column([info_duplicado], height=120, width=400),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dlg_dup),
            ft.ElevatedButton("Crear de todas formas", on_click=confirmar_guardar_aunque_dup),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.overlay.append(dialogo_duplicado)

    # ============================================================
    # GUARDAR (insertar o actualizar)
    # ============================================================
    def _guardar_real(forzar=False):
        
        ok_dir, msg_dir = validar_direccion_completa(direccion.value)
        if not ok_dir:
            mensaje.value = msg_dir
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar_msg)
            return

        # Armar dirección completa (formato: "calle | Ciudad | Estado | País")
        partes_dir = [
            (direccion.value or "").strip(),
            (ciudad.value or "").strip(),
            (estado.value or "").strip(),
            (pais.value or "").strip(),
        ]
        direccion_completa = " | ".join(partes_dir)

        if cliente_en_edicion["id"] is not None:
            exito, msj_res = actualizar_cliente(
                cliente_en_edicion["id"],
                nombre.value, ap_paterno.value, ap_materno.value,
                edad.value, sexo.value, fecha_nacimiento.value,
                peso.value, talla.value, oxigenacion.value,
                presion.value, temperatura.value, correo.value,
                direccion_completa
            )
            duplicado_dict = None
        else:
            exito, msj_res, duplicado_dict = registrar_cliente(
                nombre.value, ap_paterno.value, ap_materno.value,
                edad.value, sexo.value, fecha_nacimiento.value,
                peso.value, talla.value, oxigenacion.value,
                presion.value, temperatura.value, correo.value,
                direccion_completa,
                forzar_aunque_duplicado=forzar
            )

        if not exito and msj_res == "DUPLICADO" and duplicado_dict:
            info_duplicado.value = (
                f"Ya existe un paciente con esos mismos datos:\n\n"
                f"ID: {duplicado_dict['id_cliente']}\n"
                f"Nombre: {duplicado_dict['nombre']} {duplicado_dict['ap_paterno']} "
                f"{duplicado_dict.get('ap_materno') or ''}\n"
                f"Edad: {duplicado_dict.get('edad', '—')}\n\n"
                f"¿Deseas crearlo de todas formas?"
            )
            dialogo_duplicado.open = True
            page.update()
            return

        mensaje.value = msj_res
        mensaje.color = "green" if exito else "red"

        if exito:
            limpiar_formulario()
            recargar_tabla()

        page.update()
        page.run_task(limpiar_msg)

    def guardar(e):
        _guardar_real(forzar=False)

    btn_guardar = ft.ElevatedButton(
        "Guardar", ref=texto_btn_guar,
        icon=ft.Icons.SAVE, on_click=guardar
    )

    btn_cancelar = ft.ElevatedButton(
        "Cancelar edición", icon=ft.Icons.CANCEL,
        on_click=lambda _: limpiar_formulario(), visible=False
    )

    # ============================================================
    # DIÁLOGO HISTORIAL MÉDICO
    # ============================================================
    contenido_historial = ft.Column(
        scroll=ft.ScrollMode.AUTO, height=400, width=600, spacing=15
    )

    def cerrar_historial(e):
        dialogo_historial.open = False
        page.update()

    dialogo_historial = ft.AlertDialog(
        title=ft.Text("Historial Médico del Paciente", weight="bold"),
        content=contenido_historial,
        actions=[ft.TextButton("Cerrar", on_click=cerrar_historial)],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.overlay.append(dialogo_historial)

    def abrir_historial(paciente):
        pac_actual = paciente  # guardar referencia para recargar

        def recargar_historial():
            """Reconstruye el contenido del diálogo sin cerrarlo."""
            contenido_historial.controls.clear()
            registros = obtener_historial_bd(pac_actual["id_cliente"])

            if not registros:
                contenido_historial.controls.append(
                    ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=40,
                                    color=ft.Colors.GREY_500),
                            ft.Text(
                                "Este paciente no tiene historial médico registrado.",
                                italic=True,
                                text_align=ft.TextAlign.CENTER
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                )
            else:
                for reg in registros:
                    medico_txt = reg.get('nombre_medico') or "Médico no registrado"
                    cedula_txt = reg.get('cedula_profesional') or "—"
                    id_hist    = reg.get('id_historial')

                    def confirmar_borrar(reg_a_borrar):
                        """Muestra diálogo de confirmación antes de borrar."""
                        fecha_txt = str(reg_a_borrar.get('fecha') or '—')
                        diag_txt  = (reg_a_borrar.get('diagnostico') or '—')[:60]

                        def cerrar_conf(e=None):
                            dlg_conf.open = False
                            page.update()

                        def hacer_borrar(e):
                            ok = eliminar_historial_bd(reg_a_borrar['id_historial'])
                            cerrar_conf()
                            if ok:
                                recargar_historial()
                                page.update()
                            else:
                                contenido_historial.controls.insert(0,
                                    ft.Text("Error al eliminar el registro.",
                                            color=ft.Colors.RED)
                                )
                                page.update()

                        dlg_conf = ft.AlertDialog(
                            modal=True,
                            title=ft.Text("¿Eliminar esta receta?",
                                          weight="bold",
                                          color=ft.Colors.RED_700),
                            content=ft.Column([
                                ft.Text("Se eliminará permanentemente el siguiente registro:",
                                        size=13),
                                ft.Container(
                                    bgcolor=ft.Colors.RED_50,
                                    border=ft.border.all(1, ft.Colors.RED_200),
                                    border_radius=8,
                                    padding=10,
                                    content=ft.Column([
                                        ft.Text(f"📅 Fecha: {fecha_txt}",
                                                weight="bold"),
                                        ft.Text(f"🩺 Dx: {diag_txt}",
                                                size=12),
                                    ], spacing=4)
                                ),
                                ft.Text("Esta acción no se puede deshacer.",
                                        color=ft.Colors.RED_700,
                                        size=12, italic=True),
                            ], spacing=8, tight=True),
                            actions=[
                                ft.TextButton("Cancelar", on_click=cerrar_conf),
                                ft.ElevatedButton(
                                    "Sí, eliminar",
                                    icon=ft.Icons.DELETE_FOREVER,
                                    on_click=hacer_borrar,
                                    bgcolor=ft.Colors.RED_600,
                                    color=ft.Colors.WHITE
                                ),
                            ],
                            actions_alignment=ft.MainAxisAlignment.END
                        )

                        if dlg_conf not in page.overlay:
                            page.overlay.append(dlg_conf)
                        dlg_conf.open = True
                        page.update()

                    contenido_historial.controls.append(
                        ft.Card(
                            elevation=2,
                            content=ft.Container(
                                padding=15,
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.CALENDAR_MONTH,
                                                color=ft.Colors.BLUE_700, size=18),
                                        ft.Text(f"Fecha: {reg['fecha']}",
                                                weight="bold",
                                                color=ft.Colors.BLUE_700,
                                                expand=True),
                                        # Botón eliminar en la esquina
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_color=ft.Colors.RED_400,
                                            tooltip="Eliminar esta receta",
                                            on_click=lambda _, r=reg: confirmar_borrar(r)
                                        ),
                                    ]),
                                    ft.Text(
                                        f"Médico: {medico_txt}  |  Cédula: {cedula_txt}",
                                        size=12, color=ft.Colors.GREY_700
                                    ),
                                    ft.Divider(height=5),
                                    ft.Text("Diagnóstico:", weight="bold"),
                                    ft.Text(reg['diagnostico'] or "Sin diagnóstico"),
                                    ft.Text("Tratamiento Prescrito:", weight="bold"),
                                    ft.Text(reg['tratamiento'] or "Sin tratamiento"),
                                ], spacing=5)
                            )
                        )
                    )

            page.update()

        # Abrir el diálogo y cargar por primera vez
        dialogo_historial.title = ft.Text(
            f"Historial Médico: {paciente['nombre']} {paciente['ap_paterno']}",
            weight="bold"
        )
        recargar_historial()
        dialogo_historial.open = True
        page.update()

    # ============================================================
    # TABLA DE CLIENTES
    # ============================================================
    buscador_tabla = ft.TextField(
        label="Buscar por apellido...",
        prefix_icon=ft.Icons.SEARCH, expand=True,
        on_change=lambda e: buscar_en_tabla(e)
    )
    
    filtro_estado_pac = ft.DropdownM2(
        label="Estado", width=160,
        options=[
            ft.dropdownm2.Option("TODOS"),
            ft.dropdownm2.Option("ACTIVO"),
            ft.dropdownm2.Option("INACTIVO"),
        ],
        value="TODOS",
    )

    def on_cambio_filtro(e):
        state_filtro["filtro"] = filtro_estado_pac.value
        aplicar_filtros()

    filtro_estado_pac.on_change = on_cambio_filtro

    tabla_clientes = ft.DataTable(
        column_spacing=12, horizontal_margin=8,
        columns=[
            ft.DataColumn(ft.Text("ID",        size=12, weight="bold")),
            ft.DataColumn(ft.Text("Nombre",    size=12, weight="bold")),
            ft.DataColumn(ft.Text("Apellidos", size=12, weight="bold")),
            ft.DataColumn(ft.Text("Edad",      size=12, weight="bold")),
            ft.DataColumn(ft.Text("Sexo",      size=12, weight="bold")),
            ft.DataColumn(ft.Text("F. Nac.",   size=12, weight="bold")),
            ft.DataColumn(ft.Text("Correo",    size=12, weight="bold")),
            ft.DataColumn(ft.Text("Estado",    size=12, weight="bold")),
            ft.DataColumn(ft.Text("Editar",    size=12, weight="bold")),
            ft.DataColumn(ft.Text("Historial", size=12, weight="bold")),
            ft.DataColumn(ft.Text("Acción",    size=12, weight="bold")),
        ],
        rows=[]
    )

    contenedor_tabla = ft.Column(controls=[tabla_clientes],
                                 scroll=ft.ScrollMode.AUTO, expand=True)

    # ============================================================
    # ============================================================
    # DESHABILITAR CLIENTE
    # ============================================================
    def confirmar_baja_cliente(pac):
        motivo = ft.TextField(
            label="Motivo de baja",
            multiline=True, min_lines=2, max_lines=4,
            autofocus=True
        )

        def cerrar(e=None):
            dlg.open = False
            page.update()

        def hacer_baja(e):
            if not motivo.value or not motivo.value.strip():
                motivo.error_text = "El motivo es obligatorio."
                page.update()
                return
            ok = deshabilitar_cliente(pac['id_cliente'], motivo.value.strip())
            cerrar()
            if ok:
                aplicar_filtros()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Dar de baja a {pac['nombre']} {pac['ap_paterno']}"),
            content=ft.Container(
                width=400,
                content=ft.Column([
                    ft.Text("Captura el motivo de la baja:",
                            color=ft.Colors.GREY_700),
                    motivo
                ], tight=True)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton(
                    "Confirmar baja",
                    on_click=hacer_baja,
                    bgcolor=ft.Colors.RED_400,
                    color=ft.Colors.WHITE
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        if dlg not in page.overlay:
            page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # ============================================================
    # REACTIVAR CLIENTE
    # ============================================================
    def confirmar_activar_cliente(pac):
        def cerrar(e=None):
            dlg.open = False
            page.update()

        def hacer_activar(e):
            ok = activar_cliente(pac['id_cliente'])
            cerrar()
            if ok:
                aplicar_filtros()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Reactivar paciente"),
            content=ft.Text(
                f"¿Reactivar a {pac['nombre']} {pac['ap_paterno']}?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton(
                    "Sí, reactivar",
                    on_click=hacer_activar,
                    bgcolor=ft.Colors.GREEN_500,
                    color=ft.Colors.WHITE
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        if dlg not in page.overlay:
            page.overlay.append(dlg)
        dlg.open = True
        page.update()
    # ============================================================
    
    def hacer_fila(pac):
        est = pac.get('estado') or 'ACTIVO'
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(pac.get("id_cliente", "")), size=11)),
            ft.DataCell(ft.Text(pac.get("nombre", ""), size=11)),
            ft.DataCell(ft.Text(
                f"{pac.get('ap_paterno', '')} {pac.get('ap_materno', '') or ''}".strip(),
                size=11
            )),
            ft.DataCell(ft.Text(str(pac.get("edad", "")), size=11)),
            ft.DataCell(ft.Text(pac.get("sexo", "") or "", size=11)),
            ft.DataCell(ft.Text(str(pac.get("fecha_nacimiento", "") or ""), size=11)),
            ft.DataCell(ft.Text(pac.get("correo", "") or "", size=11)),
            # Columna ESTADO (badge de color)
            ft.DataCell(
                ft.Container(
                    content=ft.Text(
                        est, color=ft.Colors.WHITE,
                        size=11, weight="bold"
                    ),
                    bgcolor=ft.Colors.GREEN if est == "ACTIVO" else ft.Colors.RED,
                    padding=ft.Padding(8, 4, 8, 4),
                    border_radius=12
                )
            ),
            # Botón EDITAR
            ft.DataCell(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=ft.Colors.BLUE_400,
                    tooltip="Editar cliente",
                    on_click=lambda _, p=pac: cargar_en_formulario(p)
                )
            ),
            # Botón HISTORIAL
            ft.DataCell(
                ft.IconButton(
                    icon=ft.Icons.HISTORY,
                    icon_color=ft.Colors.GREEN_600,
                    tooltip="Ver historial médico",
                    on_click=lambda _, p=pac: abrir_historial(p)
                )
            ),
            # Botón DESHABILITAR / REACTIVAR
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.CANCEL,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Dar de baja",
                        visible=(est == "ACTIVO"),
                        on_click=lambda _, p=pac: confirmar_baja_cliente(p)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHECK_CIRCLE,
                        icon_color=ft.Colors.GREEN_500,
                        tooltip="Reactivar",
                        visible=(est == "INACTIVO"),
                        on_click=lambda _, p=pac: confirmar_activar_cliente(p)
                    ),
                ])
            ),
        ])

    def aplicar_filtros(lista_base=None):
        if lista_base is None:
            termino = buscador_tabla.value.strip()
            if len(termino) >= 2:
                lista_base = buscar_clientes_por_apellido(termino)
            else:
                lista_base = obtener_todos_clientes()

        filtro = state_filtro["filtro"]
        if filtro != "TODOS":
            lista_base = [
                p for p in lista_base
                if (p.get('estado') or 'ACTIVO') == filtro
            ]
        poblar_tabla(lista_base)

    def poblar_tabla(lista):
        tabla_clientes.rows.clear()
        for pac in lista:
            tabla_clientes.rows.append(hacer_fila(pac))
        page.update()

    def recargar_tabla():
        aplicar_filtros()

    def buscar_en_tabla(e):
        termino = buscador_tabla.value.strip()
        if len(termino) >= 2:
            aplicar_filtros(buscar_clientes_por_apellido(termino))
        else:
            aplicar_filtros()

    recargar_tabla()

    # ============================================================
    # LAYOUT
    # ============================================================
    formulario = ft.Card(
        elevation=5,
        content=ft.Container(
            padding=25,
            content=ft.Column([
                titulo_form,
                aviso_obligatorios,
                ft.Divider(),
                ft.Text("Datos Personales", weight="bold"),
                ft.Row([nombre]),
                ft.Row([ap_paterno, ap_materno], spacing=15),
                ft.Row([edad, sexo], spacing=15),
                ft.Row([fecha_nacimiento, btn_fecha], spacing=10),
                ft.Row([pais, estado, ciudad], spacing=15),
                ft.Row([direccion], spacing=15),
                ft.Row([correo]),
                ft.Text("Signos Vitales", weight="bold"),
                ft.Row([peso, talla], spacing=15),
                ft.Row([oxigenacion, presion, temperatura], spacing=15),
                ft.Row(
                    [btn_guardar, btn_cancelar],
                    alignment=ft.MainAxisAlignment.END
                ),
                mensaje
            ], spacing=12)
        )
    )

    seccion_tabla = ft.Card(
        elevation=3, expand=True,
        content=ft.Container(
            padding=20, expand=True,
            content=ft.Column(expand=True, controls=[
                ft.Text("Clientes Registrados", size=18, weight="bold"),
                ft.Divider(),
                ft.Row([buscador_tabla, filtro_estado_pac,
                        ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Recargar",
                                      on_click=lambda _: recargar_tabla())]),
                ft.Row([contenedor_tabla], scroll=ft.ScrollMode.AUTO, expand=True),
            ])
        )
    )

    return ft.View(
        route="/cliente",
        appbar=crear_appbar("Gestión de Pacientes", volver),
        controls=[
            ft.Container(
                expand=True, padding=20,
                content=ft.Column(
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    controls=[formulario, ft.Container(height=10), seccion_tabla]
                )
            )
        ]
    )