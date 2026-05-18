import flet as ft
import asyncio
import smtplib
import os
import subprocess
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from database.consultas import (
    buscar_clientes_por_apellido,
    buscar_medicamentos_bd,
    guardar_historial_bd,
    obtener_historial_bd,
    obtener_medico_por_id,
)
from logic.validators import filtrar_letras
from theme.estilos import crear_appbar

# ============================================================
# CONFIGURACIÓN DE CORREO — cambia estos datos por los tuyos
# ============================================================
CORREO_REMITENTE = "jorgecocohh@gmail.com"
CONTRASENA_APP = "Herrera939"
NOMBRE_CLINICA = "MediLink"


def receta_completa_view(page: ft.Page, volver):

    now = datetime.now()
    fecha_actual = now.strftime("%Y-%m-%d")
    hora_actual = now.strftime("%H:%M")

    # ================== DATOS MÉDICO ==================
    id_medico = ft.TextField(
        label="ID Médico",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="Ej: 1"
    )
    nombre_medico = ft.TextField(
        label="Nombre Médico", expand=True, read_only=True)
    cedula_medico = ft.TextField(
        label="Cédula Profesional", read_only=True, expand=True)

    # Estado para evitar múltiples consultas innecesarias
    medico_state = {"ultimo_id_consultado": None, "task_pendiente": None}

    async def buscar_medico_async(valor_id: str):
        """Espera un poco para no consultar la BD en cada tecla, luego busca y valida."""
        await asyncio.sleep(0.4)  # debounce: espera 400ms

        # Si mientras esperaba el usuario siguió escribiendo, abortamos
        if id_medico.value.strip() != valor_id:
            return

        if not valor_id.isdigit():
            nombre_medico.value = ""
            cedula_medico.value = ""
            id_medico.error_text = None
            id_medico.border_color = None
            page.update()
            return

        # Si ya consultamos este mismo ID, no repetimos
        if medico_state["ultimo_id_consultado"] == valor_id:
            return

        medico_state["ultimo_id_consultado"] = valor_id
        med = obtener_medico_por_id(int(valor_id))

        # --- Caso 1: no existe ---
        if not med:
            id_medico.error_text = "No existe un trabajador con ese ID"
            id_medico.border_color = "red"
            nombre_medico.value = ""
            cedula_medico.value = ""
            page.update()
            return

        # --- Caso 2: existe pero NO es Médico General ---
        if med.get('puesto') != "Médico General":
            id_medico.error_text = f"Ese ID es de {med.get('puesto', 'otro puesto')}, no de un Médico"
            id_medico.border_color = "red"
            nombre_medico.value = ""
            cedula_medico.value = ""
            page.update()
            return

        # --- Caso 3: es médico pero está INACTIVO ---
        if med.get('estado') == "INACTIVO":
            nombre_completo = f"{med['nombre']} {med['ap_paterno']}".strip()
            id_medico.error_text = f"El médico {nombre_completo} está dado de baja (INACTIVO)"
            id_medico.border_color = "red"
            nombre_medico.value = ""
            cedula_medico.value = ""
            page.update()
            return

        # --- Todo OK: limpiar errores y cargar datos ---
        id_medico.error_text = None
        id_medico.border_color = None
        nombre_completo = f"{med['nombre']} {med['ap_paterno']} {med.get('ap_materno', '') or ''}".strip(
        )
        nombre_medico.value = nombre_completo
        cedula_medico.value = med.get('cedula_profesional', '') or ''

        page.update()

    def cargar_medico(e):
        """Se dispara con CADA tecla. Usamos un task con debounce."""
        valor = (id_medico.value or "").strip()

        # Si el campo está vacío, limpia inmediatamente
        if not valor:
            nombre_medico.value = ""
            cedula_medico.value = ""
            medico_state["ultimo_id_consultado"] = None
            page.update()
            return

        # Lanzar búsqueda con debounce
        page.run_task(buscar_medico_async, valor)

    # USAR on_change para que se dispare con cada tecla (más confiable que on_blur)
    id_medico.on_change = cargar_medico

    # ================== BÚSQUEDA DE PACIENTE ==================
    buscador_paciente = ft.TextField(
        label="Buscar paciente por apellido...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True
    )
    lista_resultados_paciente = ft.Column(spacing=2)

    # ================== DATOS PACIENTE ==================
    # Datos identificadores: read_only (no se deben cambiar en la receta)
    id_paciente = ft.TextField(label="ID Paciente",
                               width=120,   read_only=True)
    nombre_paciente = ft.TextField(
        label="Nombre(s)",         expand=True, read_only=True)
    ap_paterno_paciente = ft.TextField(
        label="Apellido Paterno",  expand=True, read_only=True)
    ap_materno_paciente = ft.TextField(
        label="Apellido Materno",  expand=True, read_only=True)
    edad_paciente = ft.TextField(
        label="Edad",              width=100,   read_only=True)

    # Signos vitales: EDITABLES (cambian en cada consulta)
    peso_paciente = ft.TextField(label="Peso (kg)",         expand=True,
                                 keyboard_type=ft.KeyboardType.NUMBER)
    talla_paciente = ft.TextField(label="Talla (cm)",        expand=True,
                                        keyboard_type=ft.KeyboardType.NUMBER)
    oxigenacion_paciente = ft.TextField(label="Oxigenación (%)",   expand=True,
                                        keyboard_type=ft.KeyboardType.NUMBER)
    presion_paciente = ft.TextField(label="Presión",           expand=True)
    temperatura_paciente = ft.TextField(label="Temperatura (°C)",  expand=True,
                                        keyboard_type=ft.KeyboardType.NUMBER)

    # Estado del paciente actual
    correo_paciente_actual = {"valor": ""}

    # ================== DIÁLOGO DE HISTORIAL ==================
    contenido_historial = ft.Column(
        scroll=ft.ScrollMode.AUTO, height=400, width=600, spacing=15
    )

    def cerrar_historial(e):
        dialogo_historial.open = False
        page.update()

    dialogo_historial = ft.AlertDialog(
        title=ft.Text("Historial Médico", weight="bold"),
        content=contenido_historial,
        actions=[ft.TextButton("Cerrar", on_click=cerrar_historial)],
        actions_alignment=ft.MainAxisAlignment.END
    )
    page.overlay.append(dialogo_historial)

    def ver_historial(e):
        """Muestra el historial del paciente seleccionado."""
        if not id_paciente.value:
            mensaje.value = "Primero selecciona un paciente."
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar)
            return

        contenido_historial.controls.clear()
        registros = obtener_historial_bd(int(id_paciente.value))

        if not registros:
            contenido_historial.controls.append(
                ft.Text(
                    "Este paciente no tiene historial médico registrado.", italic=True)
            )
        else:
            for reg in registros:
                medico_txt = reg.get('nombre_medico') or "Médico no registrado"
                cedula_txt = reg.get('cedula_profesional') or "—"

                tarjeta = ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_MONTH,
                                        color=ft.Colors.BLUE_700, size=18),
                                ft.Text(
                                    f"Fecha: {reg['fecha']}", weight="bold", color=ft.Colors.BLUE_700),
                            ]),
                            ft.Text(f"Médico: {medico_txt}  |  Cédula: {cedula_txt}",
                                    size=12, color=ft.Colors.GREY_700),
                            ft.Divider(height=5),
                            ft.Text("Diagnóstico:", weight="bold"),
                            ft.Text(reg['diagnostico'] or "Sin diagnóstico"),
                            ft.Text("Tratamiento:", weight="bold"),
                            ft.Text(reg['tratamiento'] or "Sin tratamiento"),
                        ], spacing=5)
                    )
                )
                contenido_historial.controls.append(tarjeta)

        nombre_completo_pac = f"{nombre_paciente.value} {ap_paterno_paciente.value}".strip(
        )
        dialogo_historial.title = ft.Text(
            f"Historial Médico: {nombre_completo_pac}", weight="bold"
        )
        dialogo_historial.open = True
        page.update()

    # ================== SELECCIONAR PACIENTE ==================
    def seleccionar_paciente(paciente):
        id_paciente.value = str(paciente["id_cliente"])
        nombre_paciente.value = paciente["nombre"]
        ap_paterno_paciente.value = paciente["ap_paterno"]
        ap_materno_paciente.value = paciente.get("ap_materno", "") or ""
        edad_paciente.value = str(paciente["edad"])
        # Precargamos los signos vitales actuales del paciente, pero el médico puede modificarlos
        peso_paciente.value = str(
            paciente["peso"]) if paciente.get("peso") else ""
        talla_paciente.value = str(
            paciente["talla"]) if paciente.get("talla") else ""
        oxigenacion_paciente.value = str(
            paciente["oxigenacion"]) if paciente.get("oxigenacion") else ""
        presion_paciente.value = paciente["presion"] if paciente.get(
            "presion") else ""
        temperatura_paciente.value = str(
            paciente["temperatura"]) if paciente.get("temperatura") else ""

        # Guardar correo y actualizar label del checkbox
        correo = paciente.get("correo") or ""
        correo_paciente_actual["valor"] = correo

        if correo:
            chk_enviar_correo.label = f"Enviar receta por correo al paciente ({correo})"
            chk_enviar_correo.disabled = False
        else:
            chk_enviar_correo.label = "Enviar receta por correo (el paciente no tiene correo registrado)"
            chk_enviar_correo.disabled = True
            chk_enviar_correo.value = False

        # Habilitar el botón de ver historial
        btn_ver_historial.disabled = False

        buscador_paciente.value = ""
        lista_resultados_paciente.controls.clear()
        page.update()

    def buscar_paciente(e):
        termino = buscador_paciente.value.strip()
        lista_resultados_paciente.controls.clear()

        if len(termino) >= 2:
            resultados = buscar_clientes_por_apellido(termino)

            # Filtrar solo pacientes ACTIVOS
            activos = [p for p in resultados
                       if (p.get('estado') or 'ACTIVO') == 'ACTIVO']

            if activos:
                for pac in activos:
                    nombre_completo = (
                        f"{pac['nombre']} {pac['ap_paterno']} "
                        f"{pac.get('ap_materno', '') or ''}".strip()
                    )
                    lista_resultados_paciente.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON,
                                            color=ft.Colors.BLUE),
                            title=ft.Text(nombre_completo),
                            subtitle=ft.Text(f"Edad: {pac['edad']}"),
                            on_click=lambda e, p=pac: seleccionar_paciente(p)
                        )
                    )
            else:
                lista_resultados_paciente.controls.append(
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

    buscador_paciente.on_change = buscar_paciente

    btn_ver_historial = ft.ElevatedButton(
        "Ver Historial",
        icon=ft.Icons.HISTORY,
        on_click=ver_historial,
        disabled=True,
        bgcolor=ft.Colors.GREEN_50,
        color=ft.Colors.GREEN_900
    )

    # ================== DIAGNÓSTICO Y FIRMA ==================
    diagnostico = ft.TextField(
        label="Diagnóstico", multiline=True, expand=True,
        hint_text="Escribir Diagnostico (solo letras, espacios y signos básicos)"
    )

    def filtrar_diagnostico(e):
        limpio = filtrar_letras(diagnostico.value)
        if limpio != diagnostico.value:
            diagnostico.value = limpio
            diagnostico.update()

    diagnostico.on_change = filtrar_diagnostico

    firma = ft.TextField(label="Firma", expand=True)

    # ================== PRESCRIPCIÓN ==================
    lista_medicamentos = ft.Column()

    def crear_fila():
        med_nombre = ft.TextField(label="Medicamento", expand=True)
        dosis = ft.TextField(label="Dosis",       width=150)
        frecuencia = ft.TextField(label="Frecuencia",  width=150)
        duracion = ft.TextField(label="Duración",    width=150)

        sugerencias = ft.Column(spacing=0)
        bloque = ft.Column(spacing=0, expand=True)

        def buscar_med(e):
            termino = med_nombre.value.strip()
            sugerencias.controls.clear()
            if len(termino) >= 1:
                resultados = buscar_medicamentos_bd(termino)
                for med in resultados:
                    sugerencias.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.MEDICATION,
                                            color=ft.Colors.GREEN_400, size=18),
                            title=ft.Text(med[1], size=13),
                            subtitle=ft.Text(
                                f"${med[2]:.2f}  |  Stock: {med[3]}", size=11),
                            dense=True,
                            on_click=lambda e, m=med: seleccionar_med(m)
                        )
                    )
            page.update()

        def seleccionar_med(med):
            med_nombre.value = med[1]
            sugerencias.controls.clear()
            page.update()

        med_nombre.on_change = buscar_med
        bloque.controls = [med_nombre, sugerencias]

        fila = ft.Row(vertical_alignment=ft.CrossAxisAlignment.START)

        def eliminar_fila(e):
            lista_medicamentos.controls.remove(fila)
            page.update()

        fila.controls = [
            bloque, dosis, frecuencia, duracion,
            ft.IconButton(icon=ft.Icons.DELETE, icon_color="red",
                          on_click=eliminar_fila)
        ]
        lista_medicamentos.controls.append(fila)
        page.update()

    # ================== CHECKBOX CORREO ==================
    chk_enviar_correo = ft.Checkbox(
        label="Enviar receta por correo (selecciona un paciente primero)",
        value=False,
        disabled=True
    )

    # ================== MENSAJE ==================
    mensaje = ft.Text()

    async def limpiar():
        """Solo limpia el mensaje después de unos segundos."""
        await asyncio.sleep(4)
        mensaje.value = ""
        page.update()

    def limpiar_paciente():
        """Limpia todos los campos del paciente para la siguiente consulta.
        NO toca los campos del médico (id_medico, nombre_medico, cedula_medico)."""

        # Buscador y datos del paciente
        buscador_paciente.value = ""
        id_paciente.value = ""
        nombre_paciente.value = ""
        ap_paterno_paciente.value = ""
        ap_materno_paciente.value = ""
        edad_paciente.value = ""

        # Signos vitales
        peso_paciente.value = ""
        talla_paciente.value = ""
        oxigenacion_paciente.value = ""
        presion_paciente.value = ""
        temperatura_paciente.value = ""

        # Diagnóstico y firma
        diagnostico.value = ""
        firma.value = ""

        # Historial del paciente
        contenido_historial.controls.clear()

        # Medicamentos: limpiar y dejar una fila vacía
        lista_medicamentos.controls.clear()
        crear_fila()

        page.update()
    # ================== HELPER: signos vitales como texto ==================

    def signos_vitales_texto():
        """Construye un bloque de texto con los signos vitales de esta consulta."""
        partes = []
        if peso_paciente.value:
            partes.append(f"Peso: {peso_paciente.value} kg")
        if talla_paciente.value:
            partes.append(f"Talla: {talla_paciente.value} cm")
        if oxigenacion_paciente.value:
            partes.append(f"Oxigenación: {oxigenacion_paciente.value}%")
        if presion_paciente.value:
            partes.append(f"Presión: {presion_paciente.value}")
        if temperatura_paciente.value:
            partes.append(f"Temperatura: {temperatura_paciente.value}°C")
        return " | ".join(partes) if partes else ""

    # ================== GENERAR PDF ==================
    PDF_PATH = "receta.pdf"

    def generar_pdf_archivo():
        """Genera el PDF de la receta y devuelve True si tuvo éxito."""
        try:
            doc = SimpleDocTemplate(PDF_PATH, rightMargin=2*cm, leftMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)
            styles = getSampleStyleSheet()
            bold = ParagraphStyle(
                "bold", parent=styles["Normal"], fontName="Helvetica-Bold")
            elems = []

            # Encabezado
            elems.append(Paragraph(NOMBRE_CLINICA, styles["Title"]))
            elems.append(Paragraph("Receta Médica", styles["Heading2"]))
            elems.append(
                Paragraph(f"Fecha: {fecha_actual}   Hora: {hora_actual}", styles["Normal"]))
            elems.append(Spacer(1, 0.4*cm))

            # Datos médico
            elems.append(Paragraph("Médico", bold))
            elems.append(Paragraph(
                f"Nombre: {nombre_medico.value}   |   Cédula: {cedula_medico.value}", styles["Normal"]))
            elems.append(Spacer(1, 0.3*cm))

            # Datos paciente
            elems.append(Paragraph("Paciente", bold))
            nombre_completo = f"{nombre_paciente.value} {ap_paterno_paciente.value} {ap_materno_paciente.value}".strip(
            )
            elems.append(Paragraph(
                f"Nombre: {nombre_completo}   |   Edad: {edad_paciente.value}", styles["Normal"]))
            elems.append(Paragraph(
                f"Peso: {peso_paciente.value} kg   Talla: {talla_paciente.value} cm   "
                f"Oxigenación: {oxigenacion_paciente.value}%   "
                f"Presión: {presion_paciente.value}   Temp: {temperatura_paciente.value}°C",
                styles["Normal"]
            ))
            elems.append(Spacer(1, 0.3*cm))

            # Diagnóstico
            elems.append(Paragraph("Diagnóstico", bold))
            elems.append(Paragraph(diagnostico.value or "—", styles["Normal"]))
            elems.append(Spacer(1, 0.3*cm))

            # Prescripción
            elems.append(Paragraph("Prescripción", bold))
            tabla_data = [["Medicamento", "Dosis", "Frecuencia", "Duración"]]
            for fila in lista_medicamentos.controls:
                tabla_data.append([
                    fila.controls[0].controls[0].value,
                    fila.controls[1].value,
                    fila.controls[2].value,
                    fila.controls[3].value,
                ])

            t = Table(tabla_data, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#2D6A9F")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.whitesmoke, colors.white]),
                ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ]))
            elems.append(t)
            elems.append(Spacer(1, 0.5*cm))

            # Firma
            elems.append(Paragraph(f"Firma: {firma.value}", styles["Normal"]))

            doc.build(elems)

            # Abrir el PDF automáticamente según el sistema operativo
            ruta_absoluta = os.path.abspath(PDF_PATH)
            if sys.platform == "win32":
                os.startfile(ruta_absoluta)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", ruta_absoluta])
            else:
                subprocess.Popen(["xdg-open", ruta_absoluta])

            return True

        except Exception as ex:
            print(f"Error al generar PDF: {ex}")
            return False

    # ================== ENVIAR CORREO ==================
    def enviar_correo_con_pdf(destinatario: str):
        """Envía el PDF generado al correo del paciente."""
        try:
            msg = MIMEMultipart()
            msg["From"] = CORREO_REMITENTE
            msg["To"] = destinatario
            msg["Subject"] = f"Tu receta médica - {NOMBRE_CLINICA}"

            cuerpo = (
                f"Estimado/a {nombre_paciente.value} {ap_paterno_paciente.value},\n\n"
                f"Adjuntamos tu receta médica generada el {fecha_actual} a las {hora_actual}.\n\n"
                f"Atentamente,\n{nombre_medico.value}\n{NOMBRE_CLINICA}"
            )
            msg.attach(MIMEText(cuerpo, "plain"))

            with open(PDF_PATH, "rb") as f:
                parte = MIMEBase("application", "octet-stream")
                parte.set_payload(f.read())
                encoders.encode_base64(parte)
                parte.add_header("Content-Disposition",
                                 f'attachment; filename="receta.pdf"')
                msg.attach(parte)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
                servidor.login(CORREO_REMITENTE, CONTRASENA_APP)
                servidor.sendmail(CORREO_REMITENTE,
                                  destinatario, msg.as_string())

            return True, f"Receta enviada correctamente a {destinatario}"

        except Exception as ex:
            return False, f"Error al enviar correo: {ex}"

    # ================== BOTONES PRINCIPALES ==================
    def generar_pdf(e):
        ok = generar_pdf_archivo()
        if ok:
            if chk_enviar_correo.value and correo_paciente_actual["valor"]:
                mensaje.value = "PDF generado. Enviando correo..."
                mensaje.color = "blue"
                page.update()

                exito_mail, msj_mail = enviar_correo_con_pdf(
                    correo_paciente_actual["valor"])
                mensaje.value = msj_mail
                mensaje.color = "green" if exito_mail else "red"
            else:
                mensaje.value = "PDF generado correctamente."
                mensaje.color = "green"
        else:
            mensaje.value = "Error al generar el PDF."
            mensaje.color = "red"

        page.update()
        page.run_task(limpiar)

    def guardar(e):
        """Guarda la receta en el historial médico vinculado al paciente."""

        # ===== 0. Capturar valor_id ANTES DE TODO =====
        valor_id = (id_medico.value or "").strip()

        # ===== 1. Validar paciente =====
        if not id_paciente.value:
            mensaje.value = "Selecciona un paciente para guardar el historial."
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar)
            return

        # ===== 2. Validar diagnóstico =====
        if not diagnostico.value or not diagnostico.value.strip():
            mensaje.value = "Captura el diagnóstico antes de guardar."
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar)
            return

        # ===== 3. Validar médico (ID válido, es médico, está activo) =====
        if not valor_id.isdigit():
            mensaje.value = "Ingresa un ID de médico válido."
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar)
            return

        med_check = obtener_medico_por_id(int(valor_id))
        if not med_check:
            mensaje.value = "No existe un trabajador con ese ID."
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar)
            return

        if med_check.get('puesto') != "Médico General":
            mensaje.value = (f"El ID ingresado pertenece a {med_check.get('puesto')}, "
                             f"no a un Médico General.")
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar)
            return

        if med_check.get('estado') == "INACTIVO":
            nom = f"{med_check['nombre']} {med_check['ap_paterno']}".strip()
            mensaje.value = f"El médico {nom} está INACTIVO. No puede generar recetas."
            mensaje.color = "red"
            page.update()
            page.run_task(limpiar)
            return

        # ===== 4. Recopilar todos los medicamentos =====
        detalles_meds = []
        for fila in lista_medicamentos.controls:
            med_nombre = fila.controls[0].controls[0].value
            dosis = fila.controls[1].value
            frecuencia = fila.controls[2].value
            duracion = fila.controls[3].value

            if med_nombre:
                detalles_meds.append(
                    f"• {med_nombre} | Dosis: {dosis or '—'} | Frec: {frecuencia or '—'} | Dur: {duracion or '—'}"
                )

        # ===== 5. Construir el tratamiento incluyendo signos vitales =====
        bloques = []

        signos = signos_vitales_texto()
        if signos:
            bloques.append(f"[Signos vitales]\n{signos}")

        if detalles_meds:
            bloques.append("[Medicamentos prescritos]\n" +
                           "\n".join(detalles_meds))
        else:
            bloques.append("Sin medicamentos prescritos")

        tratamiento_str = "\n\n".join(bloques)

        # ===== 6. Convertir IDs y guardar en base de datos =====
        id_cli = int(id_paciente.value)
        id_med = int(valor_id)

        exito = guardar_historial_bd(
            id_cliente=id_cli,
            id_medico=id_med,
            fecha=fecha_actual,
            diagnostico=diagnostico.value,
            tratamiento=tratamiento_str
        )

        if exito:
            mensaje.value = "✓ Historial guardado. Listo para el siguiente paciente."
            mensaje.color = "green"
            limpiar_paciente()          # ← limpia todo EXCEPTO el médico
        else:
            mensaje.value = "Error al guardar el historial en la BD."
            mensaje.color = "red"

        page.update()
        page.run_task(limpiar)          # ← solo borra el mensaje después de 4s
    # ================== UI ==================
    return ft.View(
        route="/receta_completa",
        appbar=crear_appbar("Receta Médica", volver),
        scroll=ft.ScrollMode.AUTO,          # ← scroll en la vista directamente
        controls=[
            ft.Container(
                expand=True,
                padding=ft.Padding(left=40, top=20, right=40, bottom=20),
                content=ft.Card(            # ← Card directo, sin ft.Row envolviendo
                    elevation=4,
                    content=ft.Container(
                        padding=25,
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                # --- MÉDICO ---
                                ft.Text("Datos del Médico", weight="bold", size=15),
                                ft.Row([id_medico, nombre_medico], spacing=15),
                                ft.Row([cedula_medico]),

                                ft.Divider(),

                                # --- PACIENTE ---
                                ft.Row([
                                    ft.Text("Datos del Paciente", weight="bold",
                                            size=15, expand=True),
                                    btn_ver_historial,
                                ]),
                                ft.Row([buscador_paciente]),
                                lista_resultados_paciente,
                                ft.Row([id_paciente, nombre_paciente], spacing=15),
                                ft.Row([ap_paterno_paciente, ap_materno_paciente],
                                       spacing=15),

                                ft.Container(height=4),
                                ft.Text(
                                    "Signos vitales de esta consulta (editables):",
                                    size=12, italic=True,
                                    color=ft.Colors.GREY_700
                                ),
                                ft.Row([edad_paciente, peso_paciente, talla_paciente],
                                       spacing=15),
                                ft.Row([oxigenacion_paciente, presion_paciente,
                                        temperatura_paciente], spacing=15),

                                ft.Divider(),

                                # --- DIAGNÓSTICO ---
                                ft.Text("Diagnóstico", weight="bold", size=15),
                                diagnostico,

                                ft.Divider(),

                                # --- PRESCRIPCIÓN ---
                                ft.Text("Prescripción", weight="bold", size=15),
                                ft.Row([
                                    ft.Text("Medicamento", expand=True),
                                    ft.Text("Dosis",      width=150),
                                    ft.Text("Frecuencia", width=150),
                                    ft.Text("Duración",   width=150),
                                ]),
                                lista_medicamentos,
                                ft.ElevatedButton(
                                    "Agregar medicamento",
                                    icon=ft.Icons.ADD,
                                    on_click=lambda e: crear_fila()
                                ),

                                firma,
                                ft.Divider(),

                                # --- CHECKBOX CORREO ---
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.EMAIL,
                                                color=ft.Colors.BLUE_400),
                                        chk_enviar_correo,
                                    ]),
                                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
                                    border_radius=8,
                                    padding=ft.Padding(10, 8, 10, 8)
                                ),

                                ft.Row(
                                    [
                                        ft.ElevatedButton("Guardar",
                                                          on_click=guardar),
                                        ft.ElevatedButton("Generar PDF",
                                                          on_click=generar_pdf),
                                    ],
                                    alignment=ft.MainAxisAlignment.END
                                ),

                                mensaje,
                            ]
                        )
                    )
                )
            )
        ]
    )
