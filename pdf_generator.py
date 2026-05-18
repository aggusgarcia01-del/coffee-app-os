# =============================================================
# pdf_generator.py — Generación de tickets PDF para impresora
# térmica (formato 58 mm y 80 mm) con soporte de Logo
# Librería: fpdf2  →  pip install fpdf2
# =============================================================

from fpdf import FPDF
from datetime import datetime
import os
import tempfile


def generar_ticket(
    venta_id:      int,
    ticket_num:    int,
    tipo_consumo:  str,
    metodo_pago:   str,
    items:         list,
    subtotal:      float,
    total:         float,
    nombre_local:  str  = "",
    direccion:     str  = "",
    telefono:      str  = "",
    notas:         str  = "",
    ancho_mm:      int  = 80,
) -> str:
    """
    Genera un ticket PDF optimizado para impresora térmica con logotipo centrado.

    Retorna
    -------
    str: Ruta absoluta al archivo PDF generado
    """

    # ── Configuración de ancho ────────────────────────────────
    # 80 mm → ~42 caracteres Courier 9pt
    # 58 mm → ~30 caracteres Courier 9pt
    chars = 42 if ancho_mm == 80 else 30
    alto_pagina_mm = 250  # suficiente para cualquier ticket

    now    = datetime.now()
    w_util = ancho_mm - 4   # margen 2mm a cada lado

    # ── Crear instancia FPDF ──────────────────────────────────
    pdf = FPDF(orientation='P', unit='mm', format=(ancho_mm, alto_pagina_mm))
    pdf.set_auto_page_break(auto=False, margin=0)
    pdf.set_margins(2, 2, 2)
    pdf.add_page()

    # ── Helper: sanitizar a latin-1 (Courier no soporta Unicode) ──────
    def _s(text: str) -> str:
        return str(text).encode('latin-1', errors='replace').decode('latin-1')

    # Sanitizar todos los campos de texto
    nombre_local = _s(nombre_local)
    direccion    = _s(direccion)
    telefono     = _s(telefono)
    notas        = _s(notas)
    tipo_consumo = _s(tipo_consumo)
    metodo_pago  = _s(metodo_pago)

    # ── Helpers de renderizado ────────────────────────────────

    def _set_font(size=9, bold=False, italic=False):
        style = ''
        if bold:   style += 'B'
        if italic: style += 'I'
        pdf.set_font('Courier', style, size)

    def _linea_full(texto, size=9, bold=False, align='C'):
        _set_font(size, bold)
        pdf.cell(w_util, 5, str(texto), ln=True, align=align)

    def _dos_col(texto_iz, texto_der, size=9, bold=False):
        """Imprime dos columnas: izquierda (65%) y derecha (35%)."""
        _set_font(size, bold)
        w_iz  = w_util * 0.65
        w_der = w_util * 0.35
        max_iz = int(chars * 0.65)
        pdf.cell(w_iz,  4, str(texto_iz)[:max_iz], ln=False, align='L')
        pdf.cell(w_der, 4, str(texto_der),          ln=True,  align='R')

    def _sep(char='-'):
        _set_font(7)
        pdf.cell(w_util, 3, char * chars, ln=True, align='C')

    def _espacio(h=2):
        pdf.ln(h)

    # ===========================================================
    # ENCABEZADO (CON LOGO AUTOMÁTICO)
    # ===========================================================


    # Buscar la imagen del logo en la misma carpeta del script
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png.png")
    
    if os.path.exists(ruta_logo):
        # Si lo encuentra, lo imprime
        ancho_logo = 30 if ancho_mm == 80 else 15
        pos_x = (ancho_mm - ancho_logo) / 2
        pdf.image(ruta_logo, x=pos_x, y=pdf.get_y(), w=ancho_logo)
        _espacio(ancho_logo * 1)
    else:
        # 🚨 MODO DEPURACIÓN: Si no lo encuentra, escupe el error en el propio ticket
        _set_font(7, bold=True)
        pdf.cell(w_util, 3, "ERROR: FATA ARCHIVO logo.png", ln=True, align='C')
        pdf.cell(w_util, 3, "Buscando en:", ln=True, align='C')
        _set_font(6)
        pdf.cell(w_util, 3, ruta_logo[-40:], ln=True, align='C') 
        _espacio(3)
        
    # Nombre del local y datos comerciales
    _linea_full(nombre_local, size=13, bold=True)
    # ===========================================================
    # INFO DEL TICKET
    # ===========================================================
    _espacio(1)
    _dos_col(f"Ticket N: {ticket_num:04d}", "", size=9, bold=True)
    _dos_col(f"Fecha: {now.strftime('%d/%m/%Y')}", f"{now.strftime('%H:%M')}", size=8)
    tipo_label = "Consumo en Local" if tipo_consumo == 'local' else "Take-Away"
    _dos_col(f"Tipo: {tipo_label}", "", size=8)
    pago_labels = {'efectivo': 'Efectivo', 'debito': 'Debito/Tarjeta', 'billetera': 'Billetera Virtual'}
    _dos_col(f"Pago: {pago_labels.get(metodo_pago, metodo_pago)}", "", size=8)
    _espacio(1)
    _sn = _sep() if hasattr(pdf, '_sep') else _sep('-')

    # ===========================================================
    # DETALLE DE ITEMS
    # ===========================================================
    _espacio(1)
    _dos_col("PRODUCTO", "PRECIO", size=9, bold=True)
    _sep('-')

    for item in items:
        nombre        = _s(item.get('nombre_producto', ''))
        cant          = item.get('cantidad', 1)
        precio_u      = item.get('precio_unitario', 0)
        subtotal_item = cant * precio_u
        almibar       = item.get('almibar_extra', False)

        # Línea principal del producto
        texto_prod  = f"{cant}x {nombre}"
        texto_prec  = f"${subtotal_item:,.0f}"
        max_prod    = int(chars * 0.65) - 1
        _dos_col(texto_prod[:max_prod], texto_prec, size=9)

        # Precio unitario si cantidad > 1
        if cant > 1:
            _set_font(7, italic=True)
            pdf.cell(w_util, 3, f"   (c/u ${precio_u:,.0f})", ln=True, align='L')

        # Almíbar extra (sin costo)
        if almibar:
            _set_font(8, italic=True)
            pdf.cell(w_util, 3, "   + Almibar Extra (sin cargo)", ln=True, align='L')

    _espacio(1)
    _sep('-')

    # ===========================================================
    # SUBTOTAL Y TOTAL
    # ===========================================================
    _espacio(1)
    if subtotal != total:
        _dos_col("Subtotal:", f"${subtotal:,.0f}", size=9)

    _set_font(12, bold=True)
    _dos_col("TOTAL:", f"${total:,.0f}", size=12, bold=True)

    # ===========================================================
    # NOTAS DEL PEDIDO
    # ===========================================================
    if notas and notas.strip():
        _espacio(1)
        _sep('-')
        _set_font(8, italic=True)
        nota_safe = notas.strip().encode('latin-1', errors='replace').decode('latin-1')
        max_nota  = chars - 8
        pdf.cell(w_util, 4, f"Nota: {nota_safe[:max_nota]}", ln=True, align='L')

    # ===========================================================
    # PIE DE TICKET
    # ===========================================================
    _espacio(2)
    _sep('=')
    _espacio(1)
    _linea_full("Gracias por tu visita!", size=10, bold=True)
    _linea_full("Vuelva pronto  :)", size=9)
    _espacio(3)

    # ── Guardar en archivo temporal ───────────────────────────
    tmp_dir  = tempfile.gettempdir()
    filename = f"ticket_{ticket_num:04d}_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(tmp_dir, filename)
    pdf.output(filepath)

    return filepath
