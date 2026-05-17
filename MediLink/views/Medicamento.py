import flet as ft
import asyncio
from datetime import datetime
from logic.gestor_medicamento import (
    registrar_medicamento, reabastecer, actualizar as actualizar_med,
)
from logic.validators import (
    filtrar_letras_numeros, filtrar_numeros, filtrar_numeros_decimal, filtrar_lote,
)
from database.consultas import (
    buscar_farmaceuticas,
    autocompletar_medicamentos,
    obtener_todos_medicamentos,
    filtrar_medicamentos_por_clasificacion,
)


def medicamento_view(page: ft.Page, volver):

    # ============================================================
    # ESTADO: si estamos editando uno existente
    # ============================================================
    state = {
        "id_editando": None,        # ID si estamos modificando uno existente
        "duplicado_detectado": None # info del duplicado al guardar
    }

    # ============================================================
    # FACTORY DE TEXTFIELDS CON FILTROS
    # ============================================================
    def tf_letras_numeros(label, expand=True):
        tf = ft.TextField(label=label, expand=expand)
        def _f(e):
            limpio = filtrar_letras_numeros(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    def tf_decimal(label, expand=True):
        tf = ft.TextField(label=label, expand=expand,
                         keyboard_type=ft.KeyboardType.NUMBER)
        def _f(e):
            limpio = filtrar_numeros_decimal(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    def tf_entero(label, expand=True, max_len=None):
        tf = ft.TextField(label=label, expand=expand,
                         keyboard_type=ft.KeyboardType.NUMBER)
        def _f(e):
            limpio = filtrar_numeros(tf.value)
            if max_len:
                limpio = limpio[:max_len]
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    def tf_lote(label, expand=True):
        tf = ft.TextField(label=label, expand=expand,
                         capitalization=ft.TextCapitalization.CHARACTERS)
        def _f(e):
            limpio = filtrar_lote(tf.value)
            if limpio != tf.value:
                tf.value = limpio
                tf.update()
        tf.on_change = _f
        return tf

    # ============================================================
    # CAMPOS DEL FORMULARIO
    # ============================================================
    nombre = ft.TextField(
        label="Nombre del Medicamento *", 
        expand=True,
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"[a-zAÁÉÍÓÚáéíóúÑñÜü0-9\s\-]",
            replacement_string=""
        ), 
        hint_text="Empieza a escribir para ver sugerencias...")

    sugerencias_med = ft.Column(spacing=0)

    clasificacion = ft.Dropdown(
        label="Clasificación", expand=True,
        options=[
            ft.dropdown.Option("Analgésico"),
            ft.dropdown.Option("Antibiótico"),
            ft.dropdown.Option("Antiinflamatorio"),
            ft.dropdown.Option("Antialérgico"),
        ]
    )

    presentacion = ft.Dropdown(
        label="Presentación", expand=True,
        options=[
            ft.dropdown.Option("Tabletas"),
            ft.dropdown.Option("Jarabe"),
            ft.dropdown.Option("Cápsulas"),
            ft.dropdown.Option("Inyección"),
        ]
    )

    precio       = tf_decimal("Precio Unitario")
    stock        = tf_entero("Stock", max_len=7)
    lote         = tf_lote("Número de lote")
    precio_lote  = tf_decimal("Precio por lote")
    mg           = tf_entero("Cantidad mg", max_len=6)

    caducidad = ft.TextField(label="Fecha de caducidad", read_only=True, expand=True)
    fecha_alta = ft.TextField(
        label="Fecha de alta", value=datetime.now().strftime("%Y-%m-%d"),
        read_only=True, expand=True
    )

    farmaceutica = tf_letras_numeros("Farmacéutica")
    sugerencias_farm = ft.Column(spacing=0)

    descripcion = ft.TextField(
        label="Descripción *", multiline=True,
        min_lines=2, max_lines=4, expand=True
    )

    mensaje = ft.Text()

    # ============================================================
    # AUTOCOMPLETADO DE MEDICAMENTO
    # ============================================================
    def buscar_med(e):
        # Filtro de caracteres permitidos
        limpio = filtrar_letras_numeros(nombre.value)
        if limpio != nombre.value:
            nombre.value = limpio
            nombre.update()

        # Limpiar sugerencias
        sugerencias_med.controls.clear()

        # Si estamos editando uno y el usuario cambia el nombre, salir de modo edición
        if state["id_editando"]:
            state["id_editando"] = None
            actualizar_modo_botones()

        termino = (nombre.value or "").strip()
        if len(termino) >= 2:
            resultados = autocompletar_medicamentos(termino)
            for med in resultados:
                texto_principal = (
                    f"{med['nombre_producto']} ({med['presentacion']}, "
                    f"{med['cantidad_mg']} mg)"
                )
                texto_secundario = (
                    f"Stock: {med['stock']}  |  Lote: {med.get('numero_lote') or '—'}  "
                    f"|  ${float(med['precio_unitario']):.2f}"
                )
                sugerencias_med.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.MEDICATION,
                                        color=ft.Colors.BLUE_400),
                        title=ft.Text(texto_principal, size=13, weight="bold"),
                        subtitle=ft.Text(texto_secundario, size=11,
                                         color=ft.Colors.GREY_700),
                        dense=True,
                        on_click=lambda e, m=med: cargar_medicamento(m)
                    )
                )
        page.update()

    nombre.on_change = buscar_med

    def cargar_medicamento(med):
        """Precarga datos de un medicamento existente para registrar un NUEVO LOTE.
        NO entra en modo edición: al guardar se creará un registro nuevo."""

        # IMPORTANTE: NO ponemos state["id_editando"] porque queremos que
        # se cree un registro NUEVO, no que se actualice el existente.

        # Guardar valores ORIGINALES para validar que el nuevo lote sea distinto
        state["lote_original"]      = med.get('numero_lote') or ''
        state["caducidad_original"] = str(med['fecha_caducidad']) if med.get('fecha_caducidad') else ''

        # Llenar identidad y datos de referencia (lo que típicamente se mantiene)
        nombre.value         = med['nombre_producto']
        clasificacion.value  = med['clasificacion']
        presentacion.value   = med['presentacion']
        precio.value         = str(med['precio_unitario'])
        mg.value             = str(med['cantidad_mg'])
        farmaceutica.value   = med.get('farmaceutica') or ''
        descripcion.value    = med.get('descripcion') or ''

        # 👇 Campos del NUEVO lote: vacíos, los captura el usuario
        stock.value     = ""
        lote.value      = ""
        caducidad.value = ""
        precio_lote.value = ""
        fecha_alta.value  = datetime.now().strftime("%Y-%m-%d")

        # Bloquear identidad (porque debe ser el mismo medicamento conceptualmente)
        nombre.read_only = True
        presentacion.disabled = True
        mg.read_only = True

        sugerencias_med.controls.clear()
        actualizar_modo_botones()

        mensaje.value = (
            "📦 Registrando NUEVO LOTE del medicamento. "
            "Captura número de lote, stock y fecha de caducidad del lote que llegó."
        )
        mensaje.color = "blue"

        page.update()

    # ============================================================
    # AUTOCOMPLETADO DE FARMACÉUTICA
    # ============================================================
    filtro_farm_original = farmaceutica.on_change

    def buscar_farm(e):
        if filtro_farm_original:
            filtro_farm_original(e)
        termino = (farmaceutica.value or "").strip()
        sugerencias_farm.controls.clear()
        if len(termino) >= 1:
            for nombre_farm in buscar_farmaceuticas(termino):
                sugerencias_farm.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LOCAL_PHARMACY,
                                        color=ft.Colors.GREEN),
                        title=ft.Text(nombre_farm), dense=True,
                        on_click=lambda e, nf=nombre_farm: seleccionar_farm(nf)
                    )
                )
        page.update()

    def seleccionar_farm(nombre_farm):
        farmaceutica.value = nombre_farm
        sugerencias_farm.controls.clear()
        page.update()

    farmaceutica.on_change = buscar_farm

    # ============================================================
    # FECHA DE CADUCIDAD
    # ============================================================
    def cambiar_fecha(e):
        if date_picker.value:
            caducidad.value = date_picker.value.strftime("%Y-%m-%d")
            page.update()

    date_picker = ft.DatePicker(on_change=cambiar_fecha)
    page.overlay.append(date_picker)

    btn_fecha = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH, tooltip="Seleccionar fecha",
        on_click=lambda _: (setattr(date_picker, "open", True), page.update())
    )

    # ============================================================
    # MENSAJES Y LIMPIEZA
    # ============================================================
    async def limpiar_mensaje():
        await asyncio.sleep(4)
        mensaje.value = ""
        page.update()

    def limpiar_campos():
        for campo in [nombre, precio, stock, lote, precio_lote, mg,
                      caducidad, farmaceutica, descripcion]:
            campo.value = ""
        clasificacion.value = None
        presentacion.value = None
        fecha_alta.value = datetime.now().strftime("%Y-%m-%d")
        sugerencias_med.controls.clear()
        sugerencias_farm.controls.clear()

        # Reactivar campos de identidad
        nombre.read_only = False
        presentacion.disabled = False
        mg.read_only = False

        state["id_editando"] = None
        
        state["lote_original"] = ""
        state["caducidad_original"] = ""
        state["fecha_alta_original"] = ""
        
        actualizar_modo_botones()
        page.update()

    # ============================================================
    # BOTONES PRINCIPALES (cambian según el modo)
    # ============================================================
    btn_principal = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE)
    btn_cancelar_edicion = ft.ElevatedButton(
        "Cancelar edición", icon=ft.Icons.CANCEL,
        visible=False,
        on_click=lambda _: limpiar_campos()
    )
    info_modo = ft.Text("", size=12, italic=True)

    def actualizar_modo_botones():
        if state["id_editando"]:
            btn_principal.text = "Actualizar / Reabastecer"
            btn_principal.icon = ft.Icons.UPDATE
            btn_cancelar_edicion.visible = True
            info_modo.value = (
                f"📝 Editando medicamento existente (ID: {state['id_editando']}). "
                "El nombre, presentación y mg están bloqueados."
            )
            info_modo.color = ft.Colors.BLUE_400
        else:
            btn_principal.text = "Guardar"
            btn_principal.icon = ft.Icons.SAVE
            btn_cancelar_edicion.visible = False
            info_modo.value = (
                "💡 Empieza a escribir el nombre para ver sugerencias. "
                "Si seleccionas uno existente, podrás actualizarlo."
            )
            info_modo.color = ft.Colors.GREY_700

    # ============================================================
    # DIÁLOGO DE REABASTECIMIENTO (cuando hay duplicado al GUARDAR)
    # ============================================================
    info_existente = ft.Text("")

    def cerrar_dlg(e):
        dialogo_reabastecer.open = False
        page.update()

    def confirmar_reabastecer(e):
        dialogo_reabastecer.open = False
        page.update()
        med_existente = state["duplicado_detectado"]
        if not med_existente:
            return
        try:
            stock_extra = int(stock.value)
            precio_unit = float(precio.value)
        except (ValueError, TypeError):
            mensaje.value = "Datos numéricos inválidos."
            mensaje.color = "red"
            page.update()
            return

        ok, msj = reabastecer(
            id_medicamento=med_existente['id_medicamento'],
            stock_extra=stock_extra,
            nuevo_lote=lote.value,
            precio_lote=precio_lote.value,
            caducidad=caducidad.value,
            precio_unitario=precio_unit
        )
        mensaje.value = msj
        mensaje.color = "green" if ok else "red"
        if ok:
            limpiar_campos()
            recargar_tabla()
            state["duplicado_detectado"] = None
        page.update()
        page.run_task(limpiar_mensaje)

    dialogo_reabastecer = ft.AlertDialog(
        title=ft.Text("Medicamento ya registrado", weight="bold"),
        content=ft.Column([info_existente], height=180, width=450),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dlg),
            ft.ElevatedButton("Reabastecer (sumar stock)",
                              icon=ft.Icons.ADD_CIRCLE,
                              on_click=confirmar_reabastecer,
                              bgcolor=ft.Colors.GREEN_100,
                              color=ft.Colors.GREEN_900),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.overlay.append(dialogo_reabastecer)

    # ============================================================
    # GUARDAR / ACTUALIZAR (función principal del botón)
    # ============================================================
    def construir_data():
        return {
            "nombre": (nombre.value or "").strip(),
            "clasificacion": clasificacion.value,
            "presentacion": presentacion.value,
            "precio": precio.value,
            "stock": stock.value,
            "lote": (lote.value or "").strip(),
            "precio_lote": precio_lote.value,
            "mg": mg.value,
            "caducidad": caducidad.value,
            "fecha_alta": fecha_alta.value,
            "farmaceutica": (farmaceutica.value or "").strip(),
            "descripcion": (descripcion.value or "").strip(),
        }

    def accion_principal(e):
        data = construir_data()
        if not data["descripcion"]:
            mensaje.value = "La descripción del medicamento es obligatoria."
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar_mensaje)
            return
        
        # ===== MODO EDICIÓN REAL (botón lápiz de la tabla) =====
        if state["id_editando"]:
            ok, msj = actualizar_med(state["id_editando"], data)
            mensaje.value = msj
            mensaje.color = "green" if ok else "red"
            if ok:
                limpiar_campos()
                recargar_tabla()
            page.update()
            page.run_task(limpiar_mensaje)
            return

        # ===== MODO ALTA (nuevo medicamento O nuevo lote de uno existente) =====

        # Si viene de hacer clic en una sugerencia, validar que lote y caducidad
        # sean DIFERENTES a los del lote original
        viene_de_sugerencia = bool(state.get("lote_original")) or bool(state.get("caducidad_original"))
        if viene_de_sugerencia:
            lote_actual = (lote.value or "").strip()
            cad_actual  = (caducidad.value or "").strip()

            if lote_actual == state.get("lote_original", ""):
                mensaje.value = ("El número de lote es el mismo que el registrado. "
                                 "Un lote nuevo debe tener un número distinto.")
                mensaje.color = "red"
                page.update()
                page.run_task(limpiar_mensaje)
                return

            if cad_actual == state.get("caducidad_original", ""):
                mensaje.value = ("La fecha de caducidad es la misma que la del lote anterior. "
                                 "Un lote nuevo debe tener fecha de caducidad distinta.")
                mensaje.color = "red"
                page.update()
                page.run_task(limpiar_mensaje)
                return

        # Pasamos forzar_nuevo=True para que NO trate de detectar duplicado:
        # queremos un registro nuevo siempre.
        resultado = registrar_medicamento(data, forzar_nuevo=True)
        ok  = resultado[0]
        msj = resultado[1]

        # Mensaje personalizado si era un lote nuevo de uno existente
        if ok and viene_de_sugerencia:
            msj = "✓ Nuevo lote registrado correctamente."

        mensaje.value = msj
        mensaje.color = "green" if ok else "red"

        if ok:
            limpiar_campos()
            recargar_tabla()

        page.update()
        page.run_task(limpiar_mensaje)

    btn_principal.on_click = accion_principal

    # ============================================================
    # TABLA DE MEDICAMENTOS CON FILTROS
    # ============================================================
    filtro_clasificacion = ft.Dropdown(
        label="Filtrar por clasificación",
        width=250,
        options=[
            ft.dropdown.Option("Todas"),
            ft.dropdown.Option("Analgésico"),
            ft.dropdown.Option("Antibiótico"),
            ft.dropdown.Option("Antiinflamatorio"),
            ft.dropdown.Option("Antialérgico"),
        ],
        value="Todas",
    )

    buscador_tabla = ft.TextField(
        label="Buscar por nombre...",
        prefix_icon=ft.Icons.SEARCH, expand=True,
    )

    tabla = ft.DataTable(
        column_spacing=10, horizontal_margin=8,
        columns=[
            ft.DataColumn(ft.Text("ID",         size=11, weight="bold")),
            ft.DataColumn(ft.Text("Nombre",     size=11, weight="bold")),
            ft.DataColumn(ft.Text("Clasif.",    size=11, weight="bold")),
            ft.DataColumn(ft.Text("Pres.",      size=11, weight="bold")),
            ft.DataColumn(ft.Text("mg",         size=11, weight="bold")),
            ft.DataColumn(ft.Text("Stock",      size=11, weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("Precio",     size=11, weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("Lote",       size=11, weight="bold")),
            ft.DataColumn(ft.Text("Caducidad",  size=11, weight="bold")),
            ft.DataColumn(ft.Text("Farm.",      size=11, weight="bold")),
            ft.DataColumn(ft.Text("Editar",     size=11, weight="bold")),
        ],
        rows=[]
    )

    contenedor_tabla = ft.Column(controls=[tabla], scroll=ft.ScrollMode.AUTO,
                                 expand=True)

    def hacer_fila(med):
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(med['id_medicamento']), size=11)),
            ft.DataCell(ft.Text(med['nombre_producto'], size=11)),
            ft.DataCell(ft.Text(med['clasificacion'], size=11)),
            ft.DataCell(ft.Text(med['presentacion'], size=11)),
            ft.DataCell(ft.Text(str(med['cantidad_mg']), size=11)),
            ft.DataCell(ft.Text(str(med['stock']), size=11)),
            ft.DataCell(ft.Text(f"${float(med['precio_unitario']):.2f}", size=11)),
            ft.DataCell(ft.Text(med.get('numero_lote') or "—", size=11)),
            ft.DataCell(ft.Text(str(med.get('fecha_caducidad') or "—"), size=11)),
            ft.DataCell(ft.Text(med.get('farmaceutica') or "—", size=11)),
            ft.DataCell(
                ft.IconButton(
                    icon=ft.Icons.EDIT, icon_color=ft.Colors.BLUE_400,
                    tooltip="Editar este medicamento",
                    on_click=lambda _, m=med: cargar_medicamento(m)
                )
            ),
        ])

    # Lista en memoria para filtros locales
    cache_medicamentos = {"lista": []}

    def poblar_tabla(lista):
        tabla.rows.clear()
        for med in lista:
            tabla.rows.append(hacer_fila(med))
        page.update()

    def aplicar_filtros():
        lista_base = cache_medicamentos["lista"]

        # Filtro por clasificación (lo recargamos del servidor para precisión)
        if filtro_clasificacion.value and filtro_clasificacion.value != "Todas":
            lista_base = filtrar_medicamentos_por_clasificacion(filtro_clasificacion.value)
            cache_medicamentos["lista"] = lista_base

        # Filtro por nombre (en memoria)
        termino = (buscador_tabla.value or "").strip().lower()
        if termino:
            lista_filtrada = [
                m for m in lista_base
                if termino in m['nombre_producto'].lower()
            ]
        else:
            lista_filtrada = lista_base

        poblar_tabla(lista_filtrada)

    def recargar_tabla():
        if filtro_clasificacion.value and filtro_clasificacion.value != "Todas":
            cache_medicamentos["lista"] = filtrar_medicamentos_por_clasificacion(
                filtro_clasificacion.value
            )
        else:
            cache_medicamentos["lista"] = obtener_todos_medicamentos()
        aplicar_filtros()

    filtro_clasificacion.on_change = lambda e: recargar_tabla()
    buscador_tabla.on_change = lambda e: aplicar_filtros()

    # Carga inicial
    recargar_tabla()
    actualizar_modo_botones()

    # ============================================================
    # LAYOUT
    # ============================================================
    formulario = ft.Card(
        content=ft.Container(
            padding=20, width=850,
            content=ft.Column(controls=[
                ft.Text("Alta / Edición de medicamento", size=22,
                        weight=ft.FontWeight.BOLD),
                info_modo,
                ft.Divider(),
                ft.Row([nombre]),
                sugerencias_med,
                ft.Row([clasificacion, presentacion]),
                ft.Row([precio, stock]),
                ft.Row([lote, precio_lote, mg]),
                ft.Row([caducidad, btn_fecha]),
                ft.Row([fecha_alta]),
                ft.Row([farmaceutica]),
                sugerencias_farm,
                descripcion,
                ft.Row(
                    [btn_principal, btn_cancelar_edicion,
                     ft.ElevatedButton("Volver", on_click=volver)],
                    alignment=ft.MainAxisAlignment.END
                ),
                mensaje
            ], spacing=10)
        )
    )

    seccion_tabla = ft.Card(
        content=ft.Container(
            padding=20, width=850,
            content=ft.Column(controls=[
                ft.Text("Medicamentos Registrados", size=18, weight="bold"),
                ft.Divider(),
                ft.Row([buscador_tabla, filtro_clasificacion,
                        ft.IconButton(icon=ft.Icons.REFRESH,
                                      tooltip="Recargar",
                                      on_click=lambda _: recargar_tabla())]),
                ft.Row([contenedor_tabla], scroll=ft.ScrollMode.AUTO,
                       expand=True),
            ])
        )
    )

    return ft.View(
        route="/medicamento",
        controls=[
            ft.Container(
                expand=True, padding=15,
                content=ft.Column(
                    controls=[formulario, ft.Container(height=10), seccion_tabla],
                    expand=True, scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ]
    )