from django.shortcuts import render
from django.http import HttpResponse
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import os
import tempfile
import matplotlib
matplotlib.use('Agg')
from django import forms


class ReportForm(forms.Form):
    csv_file = forms.FileField(label='Selecciona el archivo CSV', required=True)
    pptx_template = forms.FileField(label='Selecciona la plantilla de PowerPoint', required=True)
    no_process = forms.BooleanField(label='No Procesar Salidas', required=False)
    nombre_evento = forms.CharField(label='Nombre del Evento', max_length=100, required=True)
    pase_nombre = forms.CharField(label='Nombre del Pase', max_length=100, required=True)
    fecha_evento = forms.DateField(label='Fecha del Evento', required=True)


def power_report(request):
    return render(request, 'generate_report.html')


def cargar_archivo_csv(csv_file, pptx_template, no_process, nombre_evento, pase_nombre, fecha_evento, request):
    try:
        print("Inicio del procesamiento del archivo CSV...")
        csv_file = request.FILES.get('csv_file', None)
        pptx_template = request.FILES.get('pptx_template', None)

        if not csv_file:
            print("No se proporcionó ningún archivo CSV.")
            return HttpResponse("Error: No se proporcionó ningún archivo CSV.")

        print(f"Archivo CSV: {csv_file.name}")
        print(f"Plantilla PPTX: {pptx_template.name if pptx_template else 'No se proporcionó'}")

        # Verificar parámetros antes de procesar
        print(f"Nombre del evento: {nombre_evento}")
        print(f"Pase nombre: {pase_nombre}")
        print(f"Fecha del evento: {fecha_evento}")

        archivo_pptx = procesar_archivo_csv(csv_file, pptx_template, no_process, nombre_evento, pase_nombre, fecha_evento, request)

        if isinstance(archivo_pptx, HttpResponse):
            return archivo_pptx
        else:
            response = HttpResponse(archivo_pptx.getvalue(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = 'attachment; filename="informe.pptx"'
            archivo_pptx.close()
            print("Archivo PPTX generado y enviado como respuesta.")
            return response
    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")
        return HttpResponse(f"Error al procesar el archivo CSV. Detalles del error: {e}")


def procesar_archivo_csv(csv_file, pptx_template, no_process, nombre_evento, pase_nombre, fecha_evento, request):
    try:
        print("Procesando archivo CSV...")
        if pptx_template:
            prs = Presentation(io.BytesIO(pptx_template.read()))  # Leer la plantilla PPTX proporcionada desde memoria
            print("Plantilla PPTX cargada correctamente.")
        else:
            prs = Presentation()  # Si no se proporciona una plantilla, crear una presentación vacía
            print("Se creó una presentación vacía.")

        csv_content = csv_file.read().decode('latin1').splitlines()
        print(f"Contenido del CSV cargado, número de líneas: {len(csv_content)}")
        lines = csv_content[7:]  # Saltar las primeras 7 líneas

        if len(lines) < 3:
            print("Error: El archivo CSV no tiene suficientes líneas.")
            return HttpResponse("Error: El archivo CSV no tiene suficientes líneas.")

        print(f"Número de líneas a procesar después de saltar 7 primeras líneas: {len(lines)}")

        reader = csv.DictReader(lines, delimiter=';')

        puertas_unicas = {}
        categorias_unicas = {}
        suma_tipo_acceso = 0
        fechas_grafico = []
        entradas = []
        salidas = []

        # Procesar las filas del CSV
        for row in reader:
            print(f"Procesando fila del CSV: {row}")
            puerta = row.get('Puerta', '').strip()
            tipo_acceso_str = row.get('Tipo acceso', '').strip()
            fecha_str = row.get('Fecha', '').strip()

            if not puerta or not tipo_acceso_str or not fecha_str:
                print("Fila incompleta, saltando.")
                continue

            # Procesamos las entradas y salidas para el gráfico
            try:
                fecha = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")
                if tipo_acceso_str == "Entrada":
                    entradas.append(fecha)
                    print(f"Entrada registrada en: {fecha}")
                elif tipo_acceso_str == "Salida" and not no_process:
                    salidas.append(fecha)
                    print(f"Salida registrada en: {fecha}")
            except ValueError:
                print(f"Error al procesar la fecha: {fecha_str}")
                continue

            if no_process and tipo_acceso_str == "Salida":
                print("No procesar salidas activado, saltando esta fila.")
                continue

            if puerta not in puertas_unicas:
                puertas_unicas[puerta] = 0
            puertas_unicas[puerta] += 1
            print(f"Puerta '{puerta}' acumulada: {puertas_unicas[puerta]}")

            categoria = row.get('Categoría', '').strip()
            if categoria not in categorias_unicas:
                categorias_unicas[categoria] = 0
            categorias_unicas[categoria] += 1
            print(f"Categoría '{categoria}' acumulada: {categorias_unicas[categoria]}")

            if tipo_acceso_str in ["Entrada", "Salida"]:
                suma_tipo_acceso += 1
                print(f"Tipo de acceso '{tipo_acceso_str}' sumado. Total hasta ahora: {suma_tipo_acceso}")

        print(f"Suma total de ingresos y salidas procesados: {suma_tipo_acceso}")

        # Generar la tabla PUERTAS e INGRESOS
        if len(prs.slides) >= 3:
            slide3 = prs.slides[2]
            print("Slide 3 cargada.")
        else:
            while len(prs.slides) < 3:
                prs.slides.add_slide(prs.slide_layouts[0])
                print("Añadida una nueva diapositiva para llegar a la diapositiva 3.")
            slide3 = prs.slides[2]
            print("Slide 3 cargada después de añadir diapositivas.")

        if len(prs.slides) >= 4:
            slide4 = prs.slides[3]
            print("Slide 4 cargada.")
        else:
            while len(prs.slides) < 4:
                prs.slides.add_slide(prs.slide_layouts[0])
                print("Añadida una nueva diapositiva para llegar a la diapositiva 4.")
            slide4 = prs.slides[3]
            print("Slide 4 cargada después de añadir diapositivas.")

        if len(prs.slides) >= 5:
            slide5 = prs.slides[4]
            print("Slide 5 cargada.")
        else:
            while len(prs.slides) < 5:
                prs.slides.add_slide(prs.slide_layouts[0])
                print("Añadida una nueva diapositiva para llegar a la diapositiva 5.")
            slide5 = prs.slides[4]
            print("Slide 5 cargada después de añadir diapositivas.")

        slide_width = Inches(10)
        slide_height = Inches(5.625)
        table_top = Inches(1)
        available_height = slide_height - Inches(1)

        num_rows = len(puertas_unicas) + 2
        num1_rows = len(categorias_unicas) + 2

        table_width = Inches(8)
        table_height = min(Inches(4), available_height)
        table_left = (slide_width - table_width) / 2

        # Tabla PUERTAS
        print("Generando la tabla de PUERTAS e INGRESOS.")
        shape3 = slide3.shapes.add_table(num_rows, 2, table_left, table_top, table_width, table_height).table
        shape3.cell(0, 0).text = "PUERTAS"
        shape3.cell(0, 1).text = "INGRESOS"
        # Encabezados centrados y en negrita
        for col in range(2):
            header = shape3.cell(0, col)
            header.fill.solid()
            header.fill.fore_color.rgb = RGBColor(224, 224, 224)  # Fondo gris claro
            header.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)  # Letra negra
            header.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER  # Centrando el texto
            header.text_frame.paragraphs[0].font.bold = True  # Negrita
            print(f"Encabezado de tabla PUERTAS en columna {col} establecido.")

        for i, puerta in enumerate(puertas_unicas.keys()):
            shape3.cell(i + 1, 0).text = puerta
            shape3.cell(i + 1, 1).text = str(puertas_unicas[puerta])
            print(f"Fila {i+1} de la tabla PUERTAS rellenada con: {puerta} - {puertas_unicas[puerta]}")
            # Centrando celdas
            for col in range(2):
                cell = shape3.cell(i + 1, col)
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(224, 224, 224)  # Fondo gris claro
                cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER  # Centrando el texto
                cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
                print(f"Celda de tabla PUERTAS (fila {i+1}, columna {col}) centrada y coloreada.")

        # Fila de Totales para PUERTAS
        shape3.cell(num_rows - 1, 0).text = "TOTAL"
        shape3.cell(num_rows - 1, 1).text = str(sum(puertas_unicas.values()))
        for col in range(2):
            cell = shape3.cell(num_rows - 1, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(224, 224, 224)
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER  # Centrando el texto
            cell.text_frame.paragraphs[0].font.bold = True
            print(f"Fila de totales de PUERTAS en columna {col} establecida.")

        # Tabla CATEGORIAS
        print("Generando la tabla de CATEGORIAS e INGRESOS.")
        shape4 = slide4.shapes.add_table(num1_rows, 2, table_left, table_top, table_width, table_height).table
        shape4.cell(0, 0).text = "CATEGORIAS"
        shape4.cell(0, 1).text = "INGRESOS"
        # Encabezados centrados y en negrita
        for col in range(2):
            header = shape4.cell(0, col)
            header.fill.solid()
            header.fill.fore_color.rgb = RGBColor(224, 224, 224)
            header.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
            header.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            header.text_frame.paragraphs[0].font.bold = True
            print(f"Encabezado de tabla CATEGORIAS en columna {col} establecido.")

        for i, categoria in enumerate(categorias_unicas.keys()):
            shape4.cell(i + 1, 0).text = categoria
            shape4.cell(i + 1, 1).text = str(categorias_unicas[categoria])
            print(f"Fila {i+1} de la tabla CATEGORIAS rellenada con: {categoria} - {categorias_unicas[categoria]}")
            for col in range(2):
                cell = shape4.cell(i + 1, col)
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(224, 224, 224)
                cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
                cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)
                print(f"Celda de tabla CATEGORIAS (fila {i+1}, columna {col}) centrada y coloreada.")

        # Fila de Totales para CATEGORIAS
        shape4.cell(num1_rows - 1, 0).text = "TOTAL"
        shape4.cell(num1_rows - 1, 1).text = str(sum(categorias_unicas.values()))
        for col in range(2):
            cell = shape4.cell(num1_rows - 1, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(224, 224, 224)
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            cell.text_frame.paragraphs[0].font.bold = True
            print(f"Fila de totales de CATEGORIAS en columna {col} establecida.")

        # Generar el gráfico
        print("Generando el gráfico de ingresos y salidas.")
        if entradas or salidas:
            fecha_inicial = min(entradas + salidas)
            fecha_final = max(entradas + salidas)
            print(f"Fecha inicial para el gráfico: {fecha_inicial}")
            print(f"Fecha final para el gráfico: {fecha_final}")

            fechas_grafico = [fecha_inicial + timedelta(minutes=30 * i) for i in range(int((fecha_final - fecha_inicial).total_seconds() / 1800) + 1)]
            entradas_graf = [0] * len(fechas_grafico)
            salidas_graf = [0] * len(fechas_grafico)

            print(f"Fechas para el gráfico (intervalos de 30 minutos): {fechas_grafico}")

            for i, fecha in enumerate(fechas_grafico):
                for entrada in entradas:
                    if fecha <= entrada < fecha + timedelta(minutes=30):
                        entradas_graf[i] += 1
                for salida in salidas:
                    if fecha <= salida < fecha + timedelta(minutes=30):
                        salidas_graf[i] += 1
            print(f"Entradas por intervalo: {entradas_graf}")
            print(f"Salidas por intervalo: {salidas_graf}")

            # Crear el gráfico
            with io.BytesIO() as image_stream:
                plt.figure(figsize=(10, 6))
                plt.plot(fechas_grafico, entradas_graf, color='orange', label='Entradas')
                if not no_process:
                    plt.plot(fechas_grafico, salidas_graf, color='skyblue', label='Salidas')
                plt.xlabel('Fecha y Hora')
                plt.ylabel('Cantidad')
                plt.title('Ingresos y Salidas por Intervalo de 30 minutos')
                plt.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(image_stream, format='png')
                image_stream.seek(0)
                print("Gráfico generado.")

                # Insertar el gráfico en la diapositiva 5
                if len(prs.slides) >= 5:
                    slide5 = prs.slides[4]
                    print("Slide 5 cargada para insertar el gráfico.")
                else:
                    slide5 = prs.slides.add_slide(prs.slide_layouts[0])
                    print("Añadida una nueva diapositiva para el gráfico.")

                left = Inches(1)
                top = Inches(1)
                width = Inches(8)
                height = Inches(4.5)
                slide5.shapes.add_picture(image_stream, left, top, width=width, height=height)
                print("Gráfico insertado en la diapositiva 5.")
                plt.close()
        else:
            print("No se encontraron entradas o salidas para generar el gráfico.")

        # Reemplazo de marcadores de posición en el PowerPoint
        print("Reemplazando los marcadores de posición en el PowerPoint.")
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.text == "{{NOMBRE_EVENTO}}":
                                print(f"Reemplazando {{NOMBRE_EVENTO}} con '{nombre_evento}'.")
                                run.text = nombre_evento
                            elif run.text == "{{PASE_NOMBRE}}":
                                print(f"Reemplazando {{PASE_NOMBRE}} con '{pase_nombre}'.")
                                run.text = pase_nombre
                            elif run.text == "{{FECHA_EVENTO}}":
                                fecha_evento_str = fecha_evento.strftime('%Y-%m-%d')
                                print(f"Reemplazando {{FECHA_EVENTO}} con '{fecha_evento_str}'.")
                                run.text = fecha_evento_str
                            elif run.text == "{{INGRESO_NUMERO}}":
                                print(f"Reemplazando {{INGRESO_NUMERO}} con '{suma_tipo_acceso}'.")
                                run.text = str(suma_tipo_acceso)

        # Guardar la presentación en memoria
        pptx_in_memory = io.BytesIO()
        prs.save(pptx_in_memory)
        pptx_in_memory.seek(0)
        print("Presentación de PowerPoint generada correctamente.")
        return pptx_in_memory

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")
        return HttpResponse("Error al procesar el archivo CSV. Por favor, inténtalo de nuevo.")


def generate_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            pptx_template = request.FILES['pptx_template']
            no_process = form.cleaned_data['no_process']
            nombre_evento = form.cleaned_data['nombre_evento']
            pase_nombre = form.cleaned_data['pase_nombre']
            fecha_evento = form.cleaned_data['fecha_evento']

            # Imprimir los valores recibidos
            print(f"Formulario recibido - Nombre evento: {nombre_evento}, Pase nombre: {pase_nombre}, Fecha evento: {fecha_evento}")

            archivo_pptx = cargar_archivo_csv(csv_file, pptx_template, no_process, nombre_evento, pase_nombre, fecha_evento, request)
            if isinstance(archivo_pptx, HttpResponse):
                return archivo_pptx
            else:
                print("Reporte generado correctamente, renderizando la página.")
                return render(request, 'generate_report.html', {'informe_generado': archivo_pptx})
        else:
            print("Formulario no válido.")
            return render(request, 'generate_report.html', {'error': 'Formulario no válido.'})
    else:
        return render(request, 'generate_report.html')

