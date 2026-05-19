import flet as ft
import asyncio
import os
import tempfile
import webbrowser
from datetime import datetime
from database.consultas import (
    buscar_medicamentos_bd,
    procesar_venta_completa,
    obtener_stock_medicamento,
    obtener_trabajador_por_id,
    buscar_clientes_por_apellido,
    obtener_historial_bd,
)
from theme.estilos import crear_appbar


def caja_view(page: ft.Page, volver):

    # ============================================================
    # 1. ESTADO
    # ============================================================
    carrito = []
    state = {
        "farmaceutico":          None,
        "paciente_seleccionado": None,
        "receta_seleccionada":   None,
        "ids_desde_receta":      set(),
    }

    # ============================================================
    # 2. CONTROLES VISUALES
    # ============================================================
    mensaje = ft.Text()
    txt_total = ft.Text("Total: $0.00", size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700)
    txt_cambio = ft.Text("Cambio: $0.00", size=20,
                         weight=ft.FontWeight.BOLD,
                         color=ft.Colors.GREEN_700,
                         visible=False)
    lista_resultados = ft.ListView(expand=True, spacing=5)

    tabla_ticket = ft.DataTable(
        column_spacing=15, horizontal_margin=10,
        columns=[
            ft.DataColumn(ft.Text("Concepto")),
            ft.DataColumn(ft.Text("Cant."),   numeric=True),
            ft.DataColumn(ft.Text("Importe"), numeric=True),
            ft.DataColumn(ft.Text("+/-")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[]
    )

    buscador = ft.TextField(
        label="Buscar medicamento por nombre o código...",
        prefix_icon=ft.Icons.SEARCH, expand=True
    )
    txt_pago = ft.TextField(
        label="Con cuánto paga ($)",
        prefix_icon=ft.Icons.ATTACH_MONEY,
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
    )
    switch_consulta = ft.Switch(
        label="Consulta General ($500)",      value=False)
    switch_emergencia = ft.Switch(
        label="Consulta de Emergencia ($800)", value=False)

    txt_cita_label = ft.Text("Tipo de Cita:", weight=ft.FontWeight.BOLD,
                             color=ft.Colors.BLUE_GREY_800)
    txt_cita_valor = ft.Text("")
    txt_cita_costo = ft.Text("", weight=ft.FontWeight.W_500)
    fila_cita_desglose = ft.Row(
        controls=[txt_cita_label, txt_cita_valor, txt_cita_costo],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        visible=False
    )

    txt_id_farm = ft.TextField(
        label="ID del Farmacéutico", prefix_icon=ft.Icons.BADGE,
        keyboard_type=ft.KeyboardType.NUMBER, width=180, hint_text="Ej: 3"
    )
    lbl_farm = ft.Text("", italic=True, color=ft.Colors.BLUE_GREY_600)
    farm_error = ft.Text("", color=ft.Colors.RED_400, size=12)

    buscador_paciente = ft.TextField(
        label="Buscar paciente por apellido...",
        prefix_icon=ft.Icons.PERSON_SEARCH, expand=True
    )
    lista_pacientes = ft.ListView(spacing=4, height=140)
    lbl_paciente_sel = ft.Text("", weight=ft.FontWeight.BOLD,
                               color=ft.Colors.BLUE_700)
    col_recetas = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=260)
    panel_recetas = ft.Container(
        content=col_recetas,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
        border_radius=8, padding=10, visible=False
    )
    lbl_recetas_titulo = ft.Text("Recetas del paciente:",
                                 weight=ft.FontWeight.BOLD, visible=False)

    # ============================================================
    # 3. UTILS
    # ============================================================
    async def limpiar_mensaje():
        await asyncio.sleep(3)
        mensaje.value = ""
        page.update()

    def mostrar_mensaje(texto, color="red"):
        mensaje.value = texto
        mensaje.color = color
        page.update()
        page.run_task(limpiar_mensaje)

    def calcular_total():
        total_meds = sum(item["subtotal"] for item in carrito)
        costo_cita = (800.0 if switch_emergencia.value else
                      500.0 if switch_consulta.value else 0.0)
        return total_meds + costo_cita

    # ============================================================
    # 4. CARRITO  (definido ANTES de actualizar_ticket)
    # ============================================================
    def eliminar_del_carrito(id_medicamento):
        for item in carrito:
            if item["id_medicamento"] == id_medicamento:
                carrito.remove(item)
                state["ids_desde_receta"].discard(id_medicamento)
                break
        actualizar_ticket()

    def incrementar_cantidad(id_medicamento):
        for item in carrito:
            if item["id_medicamento"] == id_medicamento:
                if item["cantidad"] + 1 > item["stock_max"]:
                    mostrar_mensaje(
                        f"Stock máximo de '{item['nombre']}': "
                        f"{item['stock_max']}.", "red"
                    )
                    return
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio"]
                break
        actualizar_ticket()

    def decrementar_cantidad(id_medicamento):
        for item in carrito:
            if item["id_medicamento"] == id_medicamento:
                if item["cantidad"] <= 1:
                    # Si llega a 0 se elimina directamente
                    eliminar_del_carrito(id_medicamento)
                    return
                item["cantidad"] -= 1
                item["subtotal"] = item["cantidad"] * item["precio"]
                break
        actualizar_ticket()

    def agregar_al_carrito(medicamento, silencioso=False, desde_receta=False):
        id_med = medicamento[0]
        nombre_med = medicamento[1]
        precio_med = float(medicamento[2])
        stock_med = int(medicamento[3])

        lote_med = medicamento[4] if len(
            medicamento) > 4 and medicamento[4] else "N/A"

        for item in carrito:
            if item["id_medicamento"] == id_med:
                if item["cantidad"] + 1 > stock_med:
                    if not silencioso:
                        mostrar_mensaje(
                            f"Stock máximo de '{nombre_med}': {stock_med}.", "red")
                    return
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio"]
                if not desde_receta:
                    state["ids_desde_receta"].discard(id_med)
                break
        else:
            if stock_med < 1:
                if not silencioso:
                    mostrar_mensaje(f"'{nombre_med}' está sin stock.", "red")
                return
            carrito.append({
                "id_medicamento": id_med,
                "nombre":         nombre_med,
                "precio":         precio_med,
                "cantidad":       1,
                "subtotal":       precio_med,
                "stock_max":      stock_med,
                "desde_receta":   desde_receta,
                "lote ":          lote_med,
            })

        if not silencioso:
            buscador.value = ""
            lista_resultados.controls.clear()
            actualizar_ticket()

    def _limpiar_meds_de_receta():
        for id_med in list(state["ids_desde_receta"]):
            for item in carrito:
                if item["id_medicamento"] == id_med:
                    carrito.remove(item)
                    break
        state["ids_desde_receta"].clear()

    # ============================================================
    # 5. TICKET EN PANTALLA
    # ============================================================
    def actualizar_ticket(e=None):
        tabla_ticket.rows.clear()
        total_productos = 0.0

        for item in carrito:
            mid = item["id_medicamento"]

            nombre_con_lote = f"{item['nombre']} (Lote: {item.get('lote', 'N/A')})"

            tabla_ticket.rows.append(ft.DataRow(cells=[
                # celda nombre lote
                ft.DataCell(ft.Text(nombre_con_lote)),
                # celda cantidad
                ft.DataCell(ft.Text(str(item["cantidad"]))),
                # celda subtotal
                ft.DataCell(ft.Text(f"${item['subtotal']:.2f}")),
                # Botones + y -
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                            icon_color=ft.Colors.ORANGE_400,
                            icon_size=20,
                            tooltip="Quitar uno",
                            on_click=lambda _, m=mid: decrementar_cantidad(m)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            icon_color=ft.Colors.GREEN_600,
                            icon_size=20,
                            tooltip="Agregar uno más",
                            on_click=lambda _, m=mid: incrementar_cantidad(m)
                        ),
                    ], spacing=0, tight=True)
                ),
                # Botón eliminar
                ft.DataCell(
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED_400,
                        icon_size=20,
                        tooltip="Eliminar",
                        on_click=lambda _, m=mid: eliminar_del_carrito(m)
                    )
                ),
            ]))
            total_productos += item["subtotal"]

        # Switches mutuamente exclusivos
        if e and e.control == switch_emergencia and switch_emergencia.value:
            switch_consulta.value = False
        elif e and e.control == switch_consulta and switch_consulta.value:
            switch_emergencia.value = False

        costo_cita = 0.0
        if switch_emergencia.value:
            costo_cita = 60.0
            txt_cita_valor.value = "Emergencia"
            txt_cita_costo.value = "$60.00"
            fila_cita_desglose.visible = True
        elif switch_consulta.value:
            costo_cita = 120.0
            txt_cita_valor.value = "General"
            txt_cita_costo.value = "$60.00"
            fila_cita_desglose.visible = True
        else:
            fila_cita_desglose.visible = False

        txt_total.value = f"Total: ${total_productos + costo_cita:.2f}"
        page.update()
        tabla_ticket.update()
    # ============================================================
    # 6. PAGO Y CAMBIO
    # ============================================================

    def on_cambio_pago(e):
        try:
            pago = float(txt_pago.value or 0)
            total = calcular_total()
            if pago > 0 and total > 0:
                cambio = pago - total
                txt_cambio.value = (f"Cambio: ${cambio:.2f}" if cambio >= 0
                                    else f"Falta: ${abs(cambio):.2f}")
                txt_cambio.color = (ft.Colors.GREEN_700 if cambio >= 0
                                    else ft.Colors.RED_700)
                txt_cambio.visible = True
            else:
                txt_cambio.visible = False
        except (ValueError, TypeError):
            txt_cambio.visible = False
        page.update()

    txt_pago.on_change = on_cambio_pago

    # ============================================================
    # 7. FARMACÉUTICO
    # ============================================================
    async def buscar_farmaceutico_async(valor: str):
        await asyncio.sleep(0.4)
        if txt_id_farm.value.strip() != valor:
            return
        farm_error.value = ""
        lbl_farm.value = ""
        state["farmaceutico"] = None
        if not valor or not valor.isdigit():
            page.update()
            return
        trab = obtener_trabajador_por_id(int(valor))
        if not trab:
            farm_error.value = "No existe un trabajador con ese ID."
        elif trab.get("estado") == "INACTIVO":
            farm_error.value = (f"{trab['nombre']} {trab['ap_paterno']} "
                                f"está dado de baja (INACTIVO).")
        else:
            if trab.get("puesto") != "Farmacéutico":
                farm_error.value = (
                    f"{trab['nombre']} {trab['ap_paterno']} "
                    f"es {trab.get('puesto', 'otro puesto')}. "
                    f"Solo los Farmacéuticos pueden atender la caja."
                )
            else:
                state["farmaceutico"] = trab
                lbl_farm.value = (
                    f"✓  {trab['nombre']} {trab['ap_paterno']} "
                    f"— Farmacéutico"
                )
        page.update()

    txt_id_farm.on_change = lambda e: page.run_task(
        buscar_farmaceutico_async, txt_id_farm.value.strip()
    )

    # ============================================================
    # 8. BÚSQUEDA DE PACIENTE
    # ============================================================
    def buscar_pacientes(e):
        termino = buscador_paciente.value.strip()
        lista_pacientes.controls.clear()

        if len(termino) >= 2:
            resultados = buscar_clientes_por_apellido(termino)

            # Filtrar solo pacientes ACTIVOS
            activos = [p for p in resultados
                       if (p.get('estado') or 'ACTIVO') == 'ACTIVO']

            if activos:
                for pac in activos:
                    lista_pacientes.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON,
                                            color=ft.Colors.BLUE_400),
                            title=ft.Text(
                                f"{pac['nombre']} {pac['ap_paterno']} "
                                f"{pac.get('ap_materno') or ''}".strip()
                            ),
                            subtitle=ft.Text(
                                f"ID: {pac['id_cliente']}  |  "
                                f"Edad: {pac.get('edad', '—')}",
                                size=11, color=ft.Colors.GREY_600
                            ),
                            on_click=lambda _, p=pac: seleccionar_paciente(p)
                        )
                    )
            else:
                lista_pacientes.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.INFO_OUTLINE,
                                        color=ft.Colors.GREY_500),
                        title=ft.Text(
                            "No se encontraron pacientes activos.",
                            italic=True, color=ft.Colors.GREY_600
                        )
                    )
                )

        page.update()

    def seleccionar_paciente(pac):
        if state["paciente_seleccionado"]:
            _limpiar_meds_de_receta()
        state["paciente_seleccionado"] = pac
        state["receta_seleccionada"] = None
        nombre_completo = (f"{pac['nombre']} {pac['ap_paterno']} "
                           f"{pac.get('ap_materno') or ''}".strip())
        lbl_paciente_sel.value = f"Paciente: {nombre_completo}"
        lista_pacientes.controls.clear()
        buscador_paciente.value = ""
        cargar_recetas(pac["id_cliente"])
        actualizar_ticket()
        page.update()

    buscador_paciente.on_change = buscar_pacientes

    # ============================================================
    # 9. RECETAS
    # ============================================================
    def _extraer_nombres_medicamentos(tratamiento: str) -> list:
        nombres, en_seccion = [], False
        for linea in tratamiento.splitlines():
            linea = linea.strip()
            if "[Medicamentos prescritos]" in linea:
                en_seccion = True
                continue
            if linea.startswith("[") and en_seccion:
                break
            if en_seccion and linea.startswith("•"):
                parte = linea.lstrip("• ").split("|")[0].strip()
                if parte:
                    nombres.append(parte)
        return nombres

    def cargar_recetas(id_cliente):
        col_recetas.controls.clear()
        historial = obtener_historial_bd(id_cliente)
        if not historial:
            col_recetas.controls.append(
                ft.Text("Este paciente no tiene recetas registradas.",
                        italic=True, color=ft.Colors.GREY_500)
            )
            lbl_recetas_titulo.visible = True
            panel_recetas.visible = True
            page.update()
            return

        historial_ord = sorted(
            historial, key=lambda r: str(r.get("fecha") or ""), reverse=True
        )

        for idx, rec in enumerate(historial_ord):
            es_ultima = (idx == 0)
            medico_txt = rec.get("nombre_medico") or "Médico no registrado"
            fecha_txt = str(rec.get("fecha") or "—")
            diag_txt = (rec.get("diagnostico") or "Sin diagnóstico")[:80]
            meds_lista = _extraer_nombres_medicamentos(
                rec.get("tratamiento") or "")
            meds_prev = ", ".join(
                meds_lista[:3]) if meds_lista else "Sin medicamentos"
            if len(meds_lista) > 3:
                meds_prev += f" (+{len(meds_lista)-3} más)"

            col_recetas.controls.append(
                ft.Container(
                    border=ft.border.all(
                        2 if es_ultima else 1,
                        ft.Colors.BLUE_700 if es_ultima else ft.Colors.BLUE_GREY_200
                    ),
                    border_radius=10, padding=12,
                    bgcolor=ft.Colors.BLUE_50 if es_ultima else None,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(
                                ft.Icons.STAR if es_ultima else ft.Icons.RECEIPT_LONG,
                                color=ft.Colors.BLUE_700 if es_ultima
                                      else ft.Colors.GREY_500, size=18
                                      ),
                            ft.Text(
                                f"{'⭐ ÚLTIMA RECETA — ' if es_ultima else ''}{fecha_txt}",
                                weight="bold" if es_ultima else ft.FontWeight.NORMAL,
                                color=ft.Colors.BLUE_700 if es_ultima else None,
                                size=13
                            ),
                        ], spacing=6),
                        ft.Text(f"Dr. {medico_txt}", size=12,
                                color=ft.Colors.GREY_700),
                        ft.Text(f"Dx: {diag_txt}", size=12),
                        ft.Text(f"💊 {meds_prev}", size=11,
                                color=ft.Colors.BLUE_GREY_600),
                        ft.ElevatedButton(
                            "Cargar esta receta al carrito",
                            icon=ft.Icons.ADD_SHOPPING_CART,
                            on_click=lambda _, r=rec: cargar_receta_al_carrito(
                                r),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_700 if es_ultima
                                else ft.Colors.BLUE_GREY_300,
                                color=ft.Colors.WHITE,
                                padding=ft.Padding(10, 6, 10, 6)
                            )
                        )
                    ], spacing=4)
                )
            )

        lbl_recetas_titulo.visible = True
        panel_recetas.visible = True
        page.update()

    def cargar_receta_al_carrito(receta):
        """Limpia meds de la receta anterior y carga los de la nueva."""
        _limpiar_meds_de_receta()
        state["receta_seleccionada"] = receta
        nombres = _extraer_nombres_medicamentos(
            receta.get("tratamiento") or "")

        if not nombres:
            mostrar_mensaje(
                "Esta receta no tiene medicamentos prescritos.", "orange")
            actualizar_ticket()
            return

        no_encontrados, agregados = [], 0
        for nombre_med in nombres:
            termino = " ".join(nombre_med.split()[:2])
            resultados = buscar_medicamentos_bd(termino)
            if resultados:
                med = resultados[0]
                agregar_al_carrito(med, silencioso=True, desde_receta=True)
                state["ids_desde_receta"].add(med[0])
                agregados += 1
            else:
                no_encontrados.append(nombre_med)

        msg = f"✓ {agregados} medicamento(s) cargados desde la receta."
        if no_encontrados:
            msg += f" No encontrados: {', '.join(no_encontrados)}"
        mostrar_mensaje(msg, "green" if not no_encontrados else "orange")
        actualizar_ticket()

    # ============================================================
    # 10. COBRO
    # ============================================================
    def realizar_cobro(e):
        if not state["farmaceutico"]:
            mostrar_mensaje(
                "Debes ingresar el ID de un Farmacéutico activo para cobrar.",
                "red"
            )
            return

        tipo_consulta = ("Consulta de Emergencia" if switch_emergencia.value else
                         "Consulta General" if switch_consulta.value else
                         "Ninguna")
        costo_cita = (800.0 if switch_emergencia.value else
                      500.0 if switch_consulta.value else 0.0)
        total_final = sum(i["subtotal"] for i in carrito) + costo_cita

        if total_final == 0:
            mostrar_mensaje(
                "Agrega productos o selecciona una consulta.", "red")
            return

        try:
            pago = float(txt_pago.value or 0)
        except ValueError:
            pago = 0.0

        if pago < total_final:
            mostrar_mensaje(
                f"El pago (${pago:.2f}) es menor al total (${total_final:.2f}).",
                "red"
            )
            return

        for item in carrito:
            stock_actual = obtener_stock_medicamento(item["id_medicamento"])
            if stock_actual is None:
                mostrar_mensaje(f"'{item['nombre']}' ya no existe.", "red")
                return
            if stock_actual < item["cantidad"]:
                mostrar_mensaje(
                    f"Stock insuficiente de '{item['nombre']}'. "
                    f"Disponibles: {stock_actual}.", "red"
                )
                return

        ok, msj_res = procesar_venta_completa(
            total_final, tipo_consulta, carrito)

        if ok:
            cambio = pago - total_final
            _imprimir_recibo(total_final, pago, cambio,
                             tipo_consulta, costo_cita, list(carrito))
            carrito.clear()
            state["ids_desde_receta"].clear()
            state["paciente_seleccionado"] = None
            state["receta_seleccionada"] = None
            switch_consulta.value = False
            switch_emergencia.value = False
            txt_pago.value = ""
            txt_cambio.visible = False
            lbl_paciente_sel.value = ""
            lbl_recetas_titulo.visible = False
            panel_recetas.visible = False
            col_recetas.controls.clear()
            actualizar_ticket()
            mostrar_mensaje("✓ Cobro realizado. Recibo generado.", "green")
        else:
            mostrar_mensaje(msj_res, "red")

    # ============================================================
    # 11. BÚSQUEDA MANUAL DE MEDICAMENTOS
    # ============================================================
    def realizar_busqueda(e):
        termino = buscador.value.strip()
        lista_resultados.controls.clear()
        if len(termino) > 0:
            for med in buscar_medicamentos_bd(termino):
                stock_color = (ft.Colors.GREEN if med[3] > 5 else
                               ft.Colors.ORANGE if med[3] > 0 else ft.Colors.RED)

                lote_med = med[4] if len(med) > 4 and med[4] else "N/A"
                farm_med = med[5] if len(med) > 5 and med[5] else "N/A"

                lista_resultados.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{med[1]} — ${med[2]:.2f}"),
                        subtitle=ft.Text(
                            f"Stock: {med[3]} | Lote: {lote_med} | Lab: {farm_med}", color=stock_color),
                        leading=ft.Icon(ft.Icons.MEDICAL_SERVICES,
                                        color=ft.Colors.GREEN),
                        on_click=lambda _, m=med: agregar_al_carrito(m)
                    )
                )
        page.update()

    buscador.on_change = realizar_busqueda
    switch_consulta.on_change = actualizar_ticket
    switch_emergencia.on_change = actualizar_ticket

    # ============================================================
    # 12. IMPRIMIR RECIBO
    # ============================================================
    def _imprimir_recibo(total, pago, cambio, tipo_consulta,
                         costo_cita, items_carrito):
        farm = state["farmaceutico"]
        pac = state["paciente_seleccionado"]
        receta = state["receta_seleccionada"]

        farm_nombre = (f"{farm['nombre']} {farm['ap_paterno']}"
                       if farm else "No registrado")
        pac_nombre = (f"{pac['nombre']} {pac['ap_paterno']} "
                      f"{pac.get('ap_materno') or ''}".strip()
                      if pac else "—")
        rec_fecha = str(receta.get("fecha") or "—") if receta else "—"
        rec_diag = (receta.get("diagnostico") or "—") if receta else "—"
        fecha_venta = datetime.now().strftime("%d/%m/%Y %H:%M")

        filas_meds = ""
        for item in items_carrito:
            lote_impreso = item.get('lote', 'N/A')

            filas_meds += (
                # <--- LOTE AGREGADO DEBAJO DEL NOMBRE
                f"<tr><td>{item['nombre']} <br><span style='font-size:10px; color:#555;'>Lote: {lote_impreso}</span></td>"
                f"<td style='text-align:center'>{item['cantidad']}</td>"
                f"<td style='text-align:right'>${item['precio']:.2f}</td>"
                f"<td style='text-align:right'>${item['subtotal']:.2f}</td></tr>"
            )

        fila_cita = ""
        if costo_cita > 0:
            fila_cita = (
                f"<tr><td>{tipo_consulta}</td>"
                f"<td style='text-align:center'>1</td>"
                f"<td style='text-align:right'>${costo_cita:.2f}</td>"
                f"<td style='text-align:right'>${costo_cita:.2f}</td></tr>"
            )

        fila_receta = ""
        if receta:
            fila_receta = (
                f"<div class='receta-info'>"
                f"<p><strong>📋 Receta del:</strong> {rec_fecha}</p>"
                f"<p><strong>Diagnóstico:</strong> {rec_diag}</p>"
                f"</div>"
            )

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Recibo MediLink</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Courier New',monospace;font-size:13px;
     max-width:380px;margin:20px auto;padding:20px;
     border:1px dashed #999;}}
.header{{text-align:center;margin-bottom:12px;}}
.header h1{{font-size:22px;letter-spacing:2px;}}
.header p{{font-size:11px;color:#555;}}
.divider{{border-top:1px dashed #999;margin:8px 0;}}
.info-row{{display:flex;justify-content:space-between;margin:3px 0;font-size:12px;}}
table{{width:100%;border-collapse:collapse;margin:8px 0;font-size:12px;}}
th{{border-bottom:1px solid #333;padding:4px 2px;text-align:left;}}
td{{padding:3px 2px;}}
.totales .row{{display:flex;justify-content:space-between;margin:3px 0;}}
.totales .row.total{{font-size:16px;font-weight:bold;
                     border-top:1px solid #333;padding-top:4px;margin-top:6px;}}
.totales .row.cambio{{color:#1a7a1a;font-weight:bold;}}
.footer{{text-align:center;margin-top:14px;font-size:11px;color:#777;}}
.receta-info{{background:#f0f7ff;border-left:3px solid #2196f3;
              padding:6px 10px;margin:8px 0;font-size:11px;}}
@media print{{body{{border:none;margin:0;}}.no-print{{display:none;}}}}
</style>
</head>
<body>
<div class="header">
  <h1>🏥 MediLink</h1>
  <p>Farmacia y Consultorios</p>
  <p>{fecha_venta}</p>
</div>
<div class="divider"></div>
<div class="info-row"><span>Atendido por:</span>
  <span><strong>{farm_nombre}</strong></span></div>
<div class="info-row"><span>Paciente:</span>
  <span><strong>{pac_nombre}</strong></span></div>
{fila_receta}
<div class="divider"></div>
<table>
  <thead><tr>
    <th>Concepto</th>
    <th style="text-align:center">Cant.</th>
    <th style="text-align:right">P.U.</th>
    <th style="text-align:right">Importe</th>
  </tr></thead>
  <tbody>{filas_meds}{fila_cita}</tbody>
</table>
<div class="divider"></div>
<div class="totales">
  <div class="row total"><span>TOTAL</span><span>${total:.2f}</span></div>
  <div class="row"><span>Pago con</span><span>${pago:.2f}</span></div>
  <div class="row cambio"><span>CAMBIO</span><span>${cambio:.2f}</span></div>
</div>
<div class="divider"></div>
<div class="footer">
  <p>¡Gracias por su preferencia!</p>
  <p>Conserve este recibo</p>
</div>
<br>
<div class="no-print" style="text-align:center">
  <button onclick="window.print()"
          style="padding:10px 30px;font-size:14px;background:#1565c0;
                 color:white;border:none;border-radius:6px;cursor:pointer">
    🖨️ Imprimir
  </button>
</div>
</body>
</html>"""

        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="w", encoding="utf-8"
        )
        tmp.write(html)
        tmp.close()
        webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")

    # ============================================================
    # 13. LAYOUT
    # ============================================================
    btn_cobrar = ft.ElevatedButton(
        "Realizar Cobro", icon=ft.Icons.PAYMENTS,
        on_click=realizar_cobro,
        style=ft.ButtonStyle(padding=20), expand=True
    )

    panel_izquierdo = ft.Column(
        expand=2, scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Card(elevation=3, content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Farmacéutico en turno",
                        weight=ft.FontWeight.BOLD, size=15),
                ft.Row([txt_id_farm, lbl_farm], spacing=12,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
                farm_error,
            ], spacing=6))),
            ft.Card(elevation=3, content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Buscar receta del paciente",
                        weight=ft.FontWeight.BOLD, size=15),
                buscador_paciente, lista_pacientes,
                lbl_paciente_sel, lbl_recetas_titulo, panel_recetas,
            ], spacing=8))),
            ft.Card(elevation=3, content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Agregar medicamento manualmente",
                        weight=ft.FontWeight.BOLD, size=15),
                ft.Row([buscador,
                        ft.IconButton(icon=ft.Icons.ADD_SHOPPING_CART)]),
                lista_resultados,
            ], spacing=8))),
            ft.Card(elevation=3, content=ft.Container(padding=15, content=ft.Column([
                ft.Text("Servicios Médicos", size=15,
                        weight=ft.FontWeight.W_600),
                switch_consulta, switch_emergencia,
            ], spacing=6))),
        ]
    )

    panel_derecho = ft.Card(
        expand=1, elevation=5,
        content=ft.Container(padding=20, content=ft.Column(controls=[
            ft.Text("Resumen de Venta", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Column(
                controls=[ft.Row([tabla_ticket], scroll=ft.ScrollMode.AUTO)],
                scroll=ft.ScrollMode.AUTO, expand=True
            ),
            ft.Divider(),
            fila_cita_desglose,
            ft.Row([txt_total], alignment=ft.MainAxisAlignment.END),
            ft.Divider(),
            ft.Text("Pago", weight=ft.FontWeight.BOLD),
            ft.Row([txt_pago, txt_cambio], spacing=12,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([btn_cobrar]),
            mensaje
        ]))
    )

    return ft.View(
        route="/caja",
        appbar=crear_appbar("Módulo de Caja", volver),
        controls=[
            ft.Container(
                expand=True, padding=20,
                content=ft.Column(expand=True, controls=[
                    ft.Row(
                        expand=True,
                        controls=[panel_izquierdo, ft.VerticalDivider(),
                                  panel_derecho]
                    )
                ])
            )
        ]
    )
