import flet as ft
from database.consultas import (
    obtener_trabajadores,
    deshabilitar_trabajador,
    activar_trabajador
)
from theme.estilos import crear_appbar


def gestion_personal_view(page: ft.Page, ir_a_alta, ir_a_editar, volver):

    # ============================================================
    # ESTADO
    # ============================================================
    state = {
        "filtro_estado": "TODOS",  # TODOS, ACTIVO, INACTIVO
        "termino_busqueda": ""
    }

    # ============================================================
    # CONTROLES
    # ============================================================
    filtro_estado = ft.Dropdown(
        label="Estado",
        width=180,
        value="TODOS",
        options=[
            ft.dropdown.Option("TODOS"),
            ft.dropdown.Option("ACTIVO"),
            ft.dropdown.Option("INACTIVO"),
        ]
    )

    buscador = ft.TextField(
        label="Buscar por nombre o apellido...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True
    )

    tabla = ft.DataTable(
        column_spacing=12,
        horizontal_margin=8,
        columns=[
            ft.DataColumn(ft.Text("ID", weight="bold")),
            ft.DataColumn(ft.Text("Nombre", weight="bold")),
            ft.DataColumn(ft.Text("Puesto", weight="bold")),
            ft.DataColumn(ft.Text("Turno", weight="bold")),
            ft.DataColumn(ft.Text("Estado", weight="bold")),
            ft.DataColumn(ft.Text("Acciones", weight="bold")),
        ],
        rows=[]
    )

    # ============================================================
    # RECARGAR / FILTRAR
    # ============================================================
    def aplicar_filtros():
        lista = obtener_trabajadores()

        # Filtro por estado
        if state["filtro_estado"] != "TODOS":
            lista = [e for e in lista
                     if (e.get('estado') or 'ACTIVO') == state["filtro_estado"]]

        # Filtro por nombre/apellido
        termino = state["termino_busqueda"].strip().lower()
        if termino:
            lista = [
                e for e in lista
                if termino in (e.get('nombre') or '').lower()
                or termino in (e.get('ap_paterno') or '').lower()
                or termino in (e.get('ap_materno') or '').lower()
            ]

        poblar_tabla(lista)

    def on_cambio_estado(e):
        state["filtro_estado"] = filtro_estado.value
        aplicar_filtros()

    def on_cambio_busqueda(e):
        state["termino_busqueda"] = buscador.value
        aplicar_filtros()

    filtro_estado.on_change = on_cambio_estado
    buscador.on_change = on_cambio_busqueda

    # ============================================================
    # DESHABILITAR
    # ============================================================
    def confirmar_baja(emp):
        observacion = ft.TextField(
            label="Motivo de salida",
            multiline=True,
            min_lines=2,
            max_lines=4,
            autofocus=True
        )

        def cerrar(e=None):
            dialog.open = False
            page.update()

        def guardar_baja(e):
            if not observacion.value or not observacion.value.strip():
                observacion.error_text = "El motivo es obligatorio."
                page.update()
                return

            ok = deshabilitar_trabajador(emp['id_trabajador'],
                                         observacion.value.strip())
            cerrar()
            if ok:
                aplicar_filtros()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Deshabilitar a {emp['nombre']} {emp['ap_paterno']}"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Captura el motivo de la baja:",
                            color=ft.Colors.GREY_700),
                    observacion
                ], tight=True),
                width=400
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton("Confirmar baja",
                                  on_click=guardar_baja,
                                  bgcolor=ft.Colors.RED_400,
                                  color=ft.Colors.WHITE)
            ]
        )

        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ============================================================
    # ACTIVAR
    # ============================================================
    def confirmar_activar(emp):
        def cerrar(e=None):
            dialog.open = False
            page.update()

        def hacer_activar(e):
            ok = activar_trabajador(emp['id_trabajador'])
            cerrar()
            if ok:
                aplicar_filtros()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Reactivar trabajador"),
            content=ft.Text(
                f"¿Reactivar a {emp['nombre']} {emp['ap_paterno']}?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton("Sí, reactivar",
                                  on_click=hacer_activar,
                                  bgcolor=ft.Colors.GREEN_500,
                                  color=ft.Colors.WHITE)
            ]
        )

        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ============================================================
    # CONSTRUIR FILAS
    # ============================================================
    def poblar_tabla(lista):
        tabla.rows.clear()

        if not lista:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("—")),
                    ft.DataCell(ft.Text("Sin resultados",
                                        italic=True,
                                        color=ft.Colors.GREY_500)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            for e in lista:
                estado = e.get('estado') or 'ACTIVO'
                nombre_completo = f"{e['nombre']} {e['ap_paterno']} {e.get('ap_materno') or ''}".strip()

                tabla.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(e['id_trabajador']))),
                        ft.DataCell(ft.Text(nombre_completo)),
                        ft.DataCell(ft.Text(e['puesto'] or '—')),
                        ft.DataCell(ft.Text(e['turno'] or '—')),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    estado,
                                    color=ft.Colors.WHITE,
                                    size=11,
                                    weight="bold"
                                ),
                                bgcolor=ft.Colors.GREEN if estado == "ACTIVO"
                                                       else ft.Colors.RED,
                                padding=ft.Padding(8, 4, 8, 4),
                                border_radius=12
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=ft.Colors.BLUE_400,
                                    tooltip="Editar",
                                    on_click=lambda ev, emp=e: ir_a_editar(emp)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CANCEL,
                                    icon_color="red",
                                    tooltip="Deshabilitar",
                                    visible=(estado == "ACTIVO"),
                                    on_click=lambda ev, emp=e: confirmar_baja(emp)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    icon_color="green",
                                    tooltip="Reactivar",
                                    visible=(estado == "INACTIVO"),
                                    on_click=lambda ev, emp=e: confirmar_activar(emp)
                                ),
                            ])
                        ),
                    ])
                )
        page.update()

    # Carga inicial
    aplicar_filtros()

    # ============================================================
    # UI
    # ============================================================
    return ft.View(
        route="/gestion_personal",
        appbar=crear_appbar("Gestión de Personal", volver),
        controls=[
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Text("Gestión de Personal", size=28, weight="bold"),
                            ft.ElevatedButton("Nuevo", icon=ft.Icons.ADD,
                                              on_click=ir_a_alta)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(),
                    ft.Row([
                        buscador,
                        filtro_estado,
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Recargar",
                            on_click=lambda _: aplicar_filtros()
                        )
                    ]),
                    ft.Container(
                        content=ft.Column(
                            [tabla],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True
                        ),
                        expand=True
                    ),
                ], expand=True)
            )
        ]
    )