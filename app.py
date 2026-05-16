# =============================================================
# app.py — Aplicación principal Coffee App OS
# Framework: Streamlit  |  UI optimizada para tablet táctil
#
# Ejecutar con:  streamlit run app.py
# =============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
import sys

# Asegurar que Python encuentre los módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
import pdf_generator as pdf_gen

# =============================================================
# CONFIGURACIÓN DE PÁGINA (debe ser el primer comando Streamlit)
# =============================================================
st.set_page_config(
    page_title="Coffee App OS",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inicializar DB ────────────────────────────────────────────
db.init_db()

# =============================================================
# CSS — Identidad visual "punto café"
# Paleta: Negro #1a1714  |  Beige #b5a48c  |  Blanco #f5f2ed
# Estética: minimalista, limpia, sin gradientes recargados
# =============================================================
st.markdown("""
<style>
/* ── Fuentes ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Tokens de marca ── */
:root {
    --negro:        #1a1714;
    --negro2:       #231f1b;
    --negro3:       #2d2822;
    --negro4:       #38322b;
    --beige:        #b5a48c;
    --beige-claro:  #d4c8b4;
    --beige-oscuro: #7a6e5e;
    --blanco:       #f5f2ed;
    --texto:        #e8e2d8;
    --texto-muted:  #8a7e70;
    --verde:        #4a7c59;
    --rojo:         #8b3a3a;
    --borde:        rgba(181,164,140,0.22);
    --borde-hover:  rgba(181,164,140,0.6);
}

/* ── Reset / base ── */
* { box-sizing: border-box; }
.stApp {
    background-color: var(--negro);
    color: var(--texto);
    font-family: 'DM Sans', sans-serif;
    font-weight: 400;
}
.main .block-container {
    padding: 0.8rem 1.2rem 2rem 1.2rem;
    max-width: 100%;
}

/* ── Barra decorativa superior tipo Vinilo ── */
.pc-vinyl-bar {
    background: linear-gradient(90deg, var(--negro2) 0%, var(--beige) 50%, var(--negro2) 100%);
    height: 6px;
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 999;
}

/* ── Header punto café ── */
.pc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px 16px 20px;
    border-bottom: 4px double var(--borde); /* Doble línea clásica de pizarra */
    margin-bottom: 20px;
}
.pc-logo-area {
    display: flex;
    align-items: center;
    gap: 14px;
}
.pc-isologo {
    width: 44px;
    height: 44px;
    opacity: 0.95;
}
.pc-brand {
    font-family: 'DM Sans', sans-serif;
    font-weight: 300;
    font-size: 24px;
    color: var(--blanco);
    letter-spacing: 0.5px;
    line-height: 1;
    text-transform: lowercase; /* Estética de tu logotipo */
}
.pc-brand span {
    color: var(--beige);
    font-weight: 500;
}
.pc-fecha {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--texto-muted);
    letter-spacing: 0.5px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-radius: 0;
    padding: 0;
    border: none;
    border-bottom: 1px solid var(--borde);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    color: var(--texto-muted) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    border-radius: 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--beige) !important;
    border-bottom: 2px solid var(--beige) !important;
}

/* ── Botones de producto (POS grid) ── */
div[data-testid="stButton"] > button {
    background: var(--negro2) !important;
    color: var(--texto) !important;
    border: 1px solid var(--borde) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    min-height: 68px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    font-family: 'DM Sans', sans-serif !important;
    white-space: pre-wrap !important;
    line-height: 1.4 !important;
    letter-spacing: 0.2px !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--negro3) !important;
    border-color: var(--borde-hover) !important;
    color: var(--blanco) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
    background: var(--negro4) !important;
}

/* ── Botón COBRAR (primary) ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: var(--verde) !important;
    border: 1px solid rgba(74,124,89,0.6) !important;
    color: var(--blanco) !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    min-height: 72px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #5a9469 !important;
    box-shadow: 0 8px 24px rgba(74,124,89,0.35) !important;
}

/* ── Métricas ── */
[data-testid="stMetric"] {
    background: var(--negro2);
    border: 1px solid var(--borde);
    border-radius: 8px;
    padding: 18px 22px;
}
[data-testid="stMetricLabel"] {
    color: var(--texto-muted) !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
[data-testid="stMetricValue"] {
    color: var(--blanco) !important;
    font-size: 26px !important;
    font-weight: 300 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; color: var(--beige) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: var(--negro2) !important;
    color: var(--texto) !important;
    border: 1px solid var(--borde) !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--beige) !important;
    box-shadow: 0 0 0 2px rgba(181,164,140,0.15) !important;
}
label, .stSelectbox label, .stNumberInput label, .stTextInput label {
    color: var(--texto-muted) !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: var(--negro2);
    border-radius: 8px;
    border: 1px solid var(--borde);
    overflow: hidden;
}

/* ── Alerta stock bajo ── */
.alerta-stock {
    background: var(--negro2);
    border: 1px solid var(--rojo);
    border-left: 3px solid var(--rojo);
    border-radius: 6px;
    padding: 10px 16px;
    margin: 0 0 12px 0;
    color: #d4a0a0;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.3px;
}

/* ── Total del carrito ── */
.total-badge {
    font-family: 'DM Sans', sans-serif;
    font-weight: 300;
    font-size: 32px;
    color: var(--blanco);
    text-align: center;
    background: var(--negro2);
    border: 1px solid var(--borde);
    border-radius: 8px;
    padding: 14px;
    margin: 10px 0;
    letter-spacing: 1px;
}
.total-badge small {
    font-size: 12px;
    color: var(--texto-muted);
    display: block;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
    font-weight: 500;
}

/* ── Badges tipo consumo ── */
.badge-tipo {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}
.badge-local    { background: transparent; color: var(--beige); border: 1px solid var(--beige-oscuro); }
.badge-takeaway { background: transparent; color: var(--blanco); border: 1px solid var(--texto-muted); }

/* ── Separadores ── */
hr { border-color: var(--borde) !important; margin: 12px 0 !important; }

/* ── Sección de categoría ── */
.cat-header {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: var(--beige);
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 16px 0 8px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--borde);
}

/* ── Alerts ── */
.stAlert {
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: var(--negro2) !important;
    border: 1px solid var(--borde) !important;
    border-radius: 6px !important;
    color: var(--texto) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Sidebar oculto ── */
[data-testid="collapsedControl"] { display: none; }

/* ── Scrollbar minimalista ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--negro); }
::-webkit-scrollbar-thumb { background: var(--negro4); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--beige-oscuro); }

/* ── Headings internos ── */
h3, h4 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    color: var(--blanco) !important;
    letter-spacing: 0.3px !important;
}
</style>
""", unsafe_allow_html=True)


# =============================================================
# ESTADO DE SESIÓN
# =============================================================
def _init_session():
    """Inicializa todas las variables de estado de sesión."""
    defaults = {
        'carrito':        [],        # ítems en el pedido actual
        'tipo_consumo':   'local',   # 'local' | 'takeaway'
        'metodo_pago':    'efectivo',# 'efectivo' | 'debito' | 'billetera'
        'venta_exitosa':  None,      # dict con info de la última venta
        'pdf_path':       None,      # ruta al PDF del último ticket
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()


# =============================================================
# HELPERS DE CARRITO
# =============================================================
def agregar_al_carrito(prod: dict):
    """Agrega producto al carrito o incrementa cantidad si ya existe."""
    for item in st.session_state.carrito:
        if item['producto_id'] == prod['id']:
            item['cantidad'] += 1
            return
    st.session_state.carrito.append({
        'producto_id':    prod['id'],
        'nombre_producto':prod['nombre'],
        'grid_index':     len(st.session_state.carrito),
        'cantidad':       1,
        'precio_unitario':prod['precio'],
        'almibar_extra':  False,
        'cafe_molido_g':  prod['cafe_molido_g'],
    })


def quitar_del_carrito(prod_id: int):
    st.session_state.carrito = [
        i for i in st.session_state.carrito if i['producto_id'] != prod_id
    ]


def decrementar_item(prod_id: int):
    for item in st.session_state.carrito:
        if item['producto_id'] == prod_id:
            item['cantidad'] -= 1
            if item['cantidad'] <= 0:
                quitar_del_carrito(prod_id)
            return


def limpiar_carrito():
    st.session_state.carrito = []


def calcular_total() -> float:
    return sum(i['cantidad'] * i['precio_unitario'] for i in st.session_state.carrito)


def _emoji_cat(cat: str) -> str:
    return {'cafe': '☕', 'comida': '🥐', 'bebida': '🥤'}.get(cat, '•')


# =============================================================
# HEADER PRINCIPAL — Identidad punto café
# =============================================================
now_str = datetime.now().strftime('%d/%m/%Y  %H:%M')

# Inyección de la guarda superior decorativa de vinilo
st.markdown('<div class="pc-vinyl-bar"></div>', unsafe_allow_html=True)

_header_html = (
    '<div class="pc-header">'
    '<div class="pc-logo-area">'
    '<svg class="pc-isologo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="50" cy="50" r="46" fill="none" stroke="#f5f5f0" stroke-width="5"/>'
    '<circle cx="50" cy="50" r="30" fill="#f5f5f0"/>'
    '<circle cx="50" cy="50" r="22" fill="#2a2520"/>'
    '<path d="M 40 40 Q 44 36 50 38" fill="none" stroke="#f5f5f0" stroke-width="2.5" stroke-linecap="round"/>'
    '<circle cx="50" cy="50" r="4" fill="none" stroke="#f5f5f0" stroke-width="2"/>'
    '<circle cx="50" cy="50" r="1.5" fill="#f5f5f0"/>'
    '<rect x="78" y="44" width="10" height="12" rx="3" fill="#f5f5f0"/>'
    '</svg>'
    '<div class="pc-brand">punto <span>caf\u00e9</span></div>'
    '</div>'
    f'<div class="pc-fecha">{now_str}</div>'
    '</div>'
)
st.markdown(_header_html, unsafe_allow_html=True)

# =============================================================
# ALERTA DE STOCK BAJO (visible en todas las pantallas)
# =============================================================
stock_bajo = db.get_stock_bajo()
if stock_bajo:
    alertas = "  |  ".join(
        f"⚠ {s['insumo']}: {s['cantidad_actual']:.0f} {s['unidad']}"
        for s in stock_bajo
    )
    st.markdown(
        f'<div class="alerta-stock">🚨 STOCK BAJO — {alertas}</div>',
        unsafe_allow_html=True
    )

# =============================================================
# NAVEGACIÓN POR TABS
# =============================================================
tab_pos, tab_stock, tab_dash, tab_cfg = st.tabs([
    "Venta",
    "Stock",
    "Dashboard",
    "Configuración",
])


# ─────────────────────────────────────────────────────────────
# TAB 1 ── PUNTO DE VENTA
# ─────────────────────────────────────────────────────────────
with tab_pos:

    col_left, col_right = st.columns([3, 2], gap="medium")

    # ══ COLUMNA IZQUIERDA: Selector de productos ══════════════
    with col_left:

        # ── Tipo de consumo ──
        st.markdown("#### 📍 Tipo de Consumo")
        c1, c2 = st.columns(2)
        with c1:
            lbl_local = "🏠 En Local  ✅" if st.session_state.tipo_consumo == 'local' else "🏠 En Local"
            if st.button(lbl_local, key="btn_local", use_container_width=True):
                st.session_state.tipo_consumo = 'local'
                st.rerun()
        with c2:
            lbl_ta = "🥡 Take-Away  ✅" if st.session_state.tipo_consumo == 'takeaway' else "🥡 Take-Away"
            if st.button(lbl_ta, key="btn_ta", use_container_width=True):
                st.session_state.tipo_consumo = 'takeaway'
                st.rerun()

        st.markdown("---")

        # ── Grid de productos ──
        productos = db.get_productos_activos()

        # Agrupar por categoría
        cats: dict = {}
        for p in productos:
            cats.setdefault(p['categoria'], []).append(p)

        for cat, prods in cats.items():
            st.markdown(
                f'<div class="cat-header">{_emoji_cat(cat)} {cat.upper()}</div>',
                unsafe_allow_html=True
            )
            cols = st.columns(3)
            for idx, prod in enumerate(prods):
                with cols[idx % 3]:
                    precio_fmt = f"${prod['precio']:,.0f}"
                    btn_label  = f"{prod['nombre']}\n{precio_fmt}"
                    if st.button(btn_label, key=f"p_{prod['id']}", use_container_width=True):
                        agregar_al_carrito(prod)
                        st.rerun()

    # ══ COLUMNA DERECHA: Carrito y cobro ══════════════════════
    with col_right:

        # ── Badge tipo consumo ──
        tipo_class = 'local' if st.session_state.tipo_consumo == 'local' else 'takeaway'
        tipo_label = '🏠 Consumo en Local' if tipo_class == 'local' else '🥡 Take-Away'
        st.markdown(
            f'<span class="badge-tipo badge-{tipo_class}">{tipo_label}</span>',
            unsafe_allow_html=True
        )

        st.markdown("#### 🛍️ Pedido Actual")

        if not st.session_state.carrito:
            st.markdown("""
            <div style="text-align:center; padding:40px 20px; color: var(--text-muted);">
                <div style="font-size:48px;">☕</div>
                <div style="font-size:15px; margin-top:10px;">El pedido está vacío</div>
                <div style="font-size:12px; margin-top:4px;">Tocá un producto para agregar</div>
            </div>
            """, unsafe_allow_html=True)

        else:
            # ── Lista de ítems ──
            for idx, item in enumerate(st.session_state.carrito):
                nombre     = item['nombre_producto']
                cant      = item['cantidad']
                precio    = item['precio_unitario']
                subtotal_i = cant * precio

                with st.container():
                    ca, cb, cc, cd, ce = st.columns([4, 1, 1, 2, 1])
                    with ca:
                        st.markdown(f"**{nombre}**")
                    with cb:
                        if st.button("−", key=f"dec_{idx}"):
                            decrementar_item(item['producto_id'])
                            st.rerun()
                    with cc:
                        st.markdown(f"**x{cant}**")
                    with cd:
                        st.markdown(f"${subtotal_i:,.0f}")
                    with ce:
                        if st.button("✕", key=f"del_{idx}"):
                            quitar_del_carrito(item['producto_id'])
                            st.rerun()

                    st.markdown('<hr style="margin:6px 0;">', unsafe_allow_html=True)

            # ── Total ──
            total = calcular_total()
            st.markdown(
                f'<div class="total-badge"><small>total</small>${total:,.0f}</div>',
                unsafe_allow_html=True
            )

            # ── Método de pago ──
            st.markdown("#### 💳 Forma de Pago")
            cp1, cp2, cp3 = st.columns(3)

            with cp1:
                lbl_ef = "💵 Efectivo ✅" if st.session_state.metodo_pago == 'efectivo' else "💵 Efectivo"
                if st.button(lbl_ef, key="pay_ef", use_container_width=True):
                    st.session_state.metodo_pago = 'efectivo'
                    st.rerun()
            with cp2:
                lbl_deb = "💳 Débito ✅" if st.session_state.metodo_pago == 'debito' else "💳 Débito"
                if st.button(lbl_deb, key="pay_deb", use_container_width=True):
                    st.session_state.metodo_pago = 'debito'
                    st.rerun()
            with cp3:
                lbl_bil = "📱 Billetera ✅" if st.session_state.metodo_pago == 'billetera' else "📱 Billetera"
                if st.button(lbl_bil, key="pay_bil", use_container_width=True):
                    st.session_state.metodo_pago = 'billetera'
                    st.rerun()

            # ── Notas ──
            notas_key = st.text_input(
                "📝 Notas del pedido",
                placeholder="Sin azúcar, extra caliente, para llevar en bolsa...",
                key="nota_pedido",
            )

            st.markdown("---")

            # ── Botones de acción ──
            bc1, bc2 = st.columns([1, 2])
            with bc1:
                if st.button("🗑️ Cancelar", use_container_width=True, key="btn_cancel"):
                    limpiar_carrito()
                    st.rerun()
            with bc2:
                if st.button(
                    f"✅  COBRAR  ${total:,.0f}",
                    key="btn_cobrar",
                    use_container_width=True,
                    type="primary",
                    disabled=(len(st.session_state.carrito) == 0),
                ):
                    try:
                        venta_id, ticket_num, subtotal, total_v = db.registrar_venta(
                            tipo_consumo = st.session_state.tipo_consumo,
                            metodo_pago  = st.session_state.metodo_pago,
                            items        = st.session_state.carrito,
                            notas        = notas_key,
                        )
                        # Generar ticket PDF
                        pdf_path = pdf_gen.generar_ticket(
                            venta_id     = venta_id,
                            ticket_num   = ticket_num,
                            tipo_consumo = st.session_state.tipo_consumo,
                            metodo_pago  = st.session_state.metodo_pago,
                            items        = st.session_state.carrito,
                            subtotal     = subtotal,
                            total        = total_v,
                            nombre_local = db.get_config('nombre_local'),
                            direccion    = db.get_config('direccion_local'),
                            telefono     = db.get_config('telefono_local'),
                            notas        = notas_key,
                            ancho_mm     = int(db.get_config('ancho_ticket_mm') or 80),
                        )
                        st.session_state.venta_exitosa = {
                            'ticket_num': ticket_num,
                            'total':      total_v,
                        }
                        st.session_state.pdf_path = pdf_path
                        limpiar_carrito()
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error al procesar la venta: {e}")

        # ── Confirmación post-venta ──────────────────────────
        if st.session_state.venta_exitosa:
            v = st.session_state.venta_exitosa
            st.success(
                f"✅ ¡Venta registrada!  Ticket N° **{v['ticket_num']:04d}** —  "
                f"Total: **${v['total']:,.0f}**"
            )

            # Descarga del PDF
            pdf_path = st.session_state.pdf_path
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label    = "🖨️ Descargar / Imprimir Ticket PDF",
                    data     = pdf_bytes,
                    file_name= f"ticket_{v['ticket_num']:04d}.pdf",
                    mime     = "application/pdf",
                    use_container_width=True,
                )

            if st.button("🆕 Nuevo Pedido", use_container_width=True, key="btn_nuevo"):
                st.session_state.venta_exitosa = None
                st.session_state.pdf_path      = None
                st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 2 ── GESTIÓN DE STOCK
# ─────────────────────────────────────────────────────────────
with tab_stock:
    st.markdown("### 📦 Gestión de Stock")

    col_st1, col_st2 = st.columns([3, 2], gap="large")

    with col_st1:

        # ── Tabla de stock actual ──
        st.markdown("#### Estado Actual del Stock")
        stock_data = db.get_stock()

        if stock_data:
            df_stock = pd.DataFrame(stock_data)

            def _estado(row):
                if row['cantidad_actual'] <= 0:
                    return "🔴 Sin stock"
                elif row['cantidad_actual'] <= row['cantidad_alerta']:
                    return "🟡 Bajo"
                return "🟢 OK"

            df_stock['Estado']      = df_stock.apply(_estado, axis=1)
            df_stock['Disponible']  = df_stock.apply(lambda r: f"{r['cantidad_actual']:.1f} {r['unidad']}", axis=1)
            df_stock['Umbral alerta']= df_stock.apply(lambda r: f"{r['cantidad_alerta']:.1f} {r['unidad']}", axis=1)

            st.dataframe(
                df_stock[['insumo', 'Disponible', 'Umbral alerta', 'Estado']].rename(
                    columns={'insumo': 'Insumo'}
                ),
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("---")

        # ── Cargar stock ──
        st.markdown("#### ➕ Cargar Stock")
        insumos = [s['insumo'] for s in stock_data]

        csk1, csk2, csk3 = st.columns([2, 1, 1])
        with csk1:
            ins_sel  = st.selectbox("Insumo", insumos, key="ins_cargar")
        with csk2:
            unidad_sel = next((s['unidad'] for s in stock_data if s['insumo'] == ins_sel), '')
            cant_cargar = st.number_input(
                f"Cantidad ({unidad_sel})", min_value=0.1, value=500.0,
                step=100.0, key="cant_cargar"
            )
        with csk3:
            st.markdown("&nbsp;", unsafe_allow_html=True)
            st.markdown("&nbsp;", unsafe_allow_html=True)
            if st.button("✅ Cargar", use_container_width=True, key="btn_cargar"):
                db.actualizar_stock(ins_sel, cant_cargar)
                st.success(f"✅ +{cant_cargar:.0f} {unidad_sel} de **{ins_sel}**")
                st.rerun()

        st.markdown("---")

        # ── Modificar umbral de alerta ──
        st.markdown("#### 🔔 Modificar Umbral de Alerta")
        ins_umbral = st.selectbox("Insumo", insumos, key="ins_umbral")
        nuevo_umbral = st.number_input("Nuevo umbral", min_value=0.0, value=200.0,
                                       step=50.0, key="nuevo_umbral")
        if st.button("💾 Guardar umbral", use_container_width=True, key="btn_umbral"):
            db.actualizar_umbral_stock(ins_umbral, nuevo_umbral)
            st.success(f"✅ Umbral de **{ins_umbral}** actualizado a {nuevo_umbral:.0f}")
            st.rerun()

    with col_st2:

        # ── Registrar merma ──
        st.markdown("#### 🗑️ Registrar Merma / Desperdicio")

        ins_merma   = st.selectbox("Insumo", insumos, key="ins_merma")
        unidad_merma = next((s['unidad'] for s in stock_data if s['insumo'] == ins_merma), '')
        cant_merma  = st.number_input(
            f"Cantidad ({unidad_merma})", min_value=0.1, value=10.0,
            step=1.0, key="cant_merma"
        )
        motivo_merma = st.text_area(
            "Motivo de la merma",
            placeholder="Ej: Café pasado, derrame, producto vencido...",
            height=90, key="motivo_merma"
        )
        if st.button("🗑️ Registrar Merma", use_container_width=True, key="btn_merma"):
            if motivo_merma.strip():
                db.registrar_merma(ins_merma, cant_merma, motivo_merma.strip())
                st.success(f"✅ Merma registrada: {cant_merma:.0f} {unidad_merma} de {ins_merma}")
                st.rerun()
            else:
                st.warning("⚠️ Por favor ingresá el motivo de la merma.")

        st.markdown("---")

        # ── Últimas mermas ──
        st.markdown("#### 📋 Últimas Mermas (7 días)")
        mermas = db.get_mermas(7)
        if mermas:
            for m in mermas[:8]:
                fecha_str = m['fecha'][:16]
                st.markdown(
                    f"• **{m['insumo']}**: {m['cantidad']:.1f}  "
                    f"— _{m['motivo']}_"
                )
                st.caption(fecha_str)
        else:
            st.info("Sin mermas registradas en los últimos 7 días.")


# ─────────────────────────────────────────────────────────────
# TAB 3 ── DASHBOARD / MÉTRICAS
# ─────────────────────────────────────────────────────────────
with tab_dash:

    # ── CSS extra solo para el dashboard ──
    st.markdown("""
    <style>
    .dash-section {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--beige);
        margin: 20px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--borde);
    }
    .kpi-card {
        background: var(--negro2);
        border: 1px solid var(--borde);
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 8px;
    }
    .kpi-label {
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--texto-muted);
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 300;
        color: var(--blanco);
        line-height: 1;
    }
    .kpi-sub {
        font-size: 12px;
        color: var(--beige);
        margin-top: 4px;
    }
    .prod-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        background: var(--negro2);
        border: 1px solid var(--borde);
        border-radius: 6px;
        margin-bottom: 5px;
    }
    .prod-nombre { font-size: 14px; color: var(--texto); font-weight: 500; }
    .prod-cant   { font-size: 13px; color: var(--beige); font-weight: 600; }
    .prod-monto  { font-size: 13px; color: var(--texto-muted); }
    .bar-fill {
        height: 4px;
        background: var(--beige);
        border-radius: 2px;
        margin-top: 6px;
        opacity: 0.6;
    }
    .selector-fecha {
        background: var(--negro2);
        border: 1px solid var(--borde);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 16px;
    }
    .ticket-row {
        display: flex;
        gap: 10px;
        align-items: center;
        padding: 8px 12px;
        border-bottom: 1px solid var(--borde);
        font-size: 13px;
    }
    .ticket-num  { color: var(--beige); font-weight: 600; min-width: 50px; }
    .ticket-hora { color: var(--texto-muted); min-width: 55px; }
    .ticket-tipo { color: var(--texto-muted); min-width: 70px; font-size: 11px; }
    .ticket-items{ color: var(--texto); flex: 1; }
    .ticket-total{ color: var(--blanco); font-weight: 600; min-width: 80px; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

    # ══ SELECTOR DE FECHA ════════════════════════════════════
    st.markdown('<div class="dash-section">Período</div>', unsafe_allow_html=True)

    fechas_disponibles = db.get_fechas_con_ventas(30)
    hoy_str = date.today().strftime('%Y-%m-%d')

    # Variable intermedia para los botones rápidos
    from datetime import timedelta
    if 'dash_fecha_valor' not in st.session_state:
        st.session_state.dash_fecha_valor = date.today()

    sel_col1, sel_col2, sel_col3 = st.columns([2, 2, 3])

    with sel_col1:
        modo_fecha = st.radio(
            "Ver",
            ["Día específico", "Rango de días"],
            horizontal=False,
            key="dash_modo",
            label_visibility="collapsed",
        )

    with sel_col2:
        if modo_fecha == "Día específico":

            # Botones rápidos ANTES del date_input para cambiar el estado de sesión sin crashes
            qa, qb = st.columns(2)
            with qa:
                if st.button("Hoy", key="q_hoy", use_container_width=True):
                    st.session_state.dash_fecha_valor = date.today()
                    st.rerun()
            with qb:
                if st.button("Ayer", key="q_ayer", use_container_width=True):
                    st.session_state.dash_fecha_valor = date.today() - timedelta(days=1)
                    st.rerun()

            # El date_input se alimenta del estado de sesión
            fecha_sel = st.date_input(
                "Fecha",
                value=st.session_state.dash_fecha_valor,
                key="dash_fecha_unica",
                label_visibility="visible",
            )
            st.session_state.dash_fecha_valor = fecha_sel
            fecha_inicio = fecha_fin = fecha_sel.strftime('%Y-%m-%d')

        else:
            fecha_rango = st.date_input(
                "Desde / Hasta",
                value=(date.today() - timedelta(days=6), date.today()),
                key="dash_rango",
                label_visibility="visible",
            )
            if isinstance(fecha_rango, (list, tuple)) and len(fecha_rango) == 2:
                fecha_inicio = fecha_rango[0].strftime('%Y-%m-%d')
                fecha_fin    = fecha_rango[1].strftime('%Y-%m-%d')
            else:
                fecha_inicio = fecha_fin = date.today().strftime('%Y-%m-%d')

    with sel_col3:
        if fechas_disponibles:
            st.caption("Días con ventas registradas:")
            dias_str = "  ·  ".join(
                f.replace('-', '/')[5:] for f in fechas_disponibles[:10]
            )
            st.markdown(f"<span style='font-size:12px;color:var(--texto-muted)'>{dias_str}</span>",
                        unsafe_allow_html=True)
        else:
            st.info("Aún no hay ventas registradas.")

    # ══ OBTENER DATOS DEL PERÍODO ════════════════════════════
    conn_dash = db.get_connection()

    # Ventas del período
    ventas_periodo = conn_dash.execute('''
        SELECT v.*,
               GROUP_CONCAT(dv.nombre_producto || ' x' || dv.cantidad, ', ') AS items_str
        FROM ventas v
        LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
        WHERE v.fecha BETWEEN ? AND ?
        GROUP BY v.id
        ORDER BY v.fecha DESC, v.hora DESC
    ''', (fecha_inicio, fecha_fin)).fetchall()
    ventas_periodo = [dict(r) for r in ventas_periodo]

    # Productos del período
    productos_periodo = conn_dash.execute('''
        SELECT dv.nombre_producto,
               SUM(dv.cantidad)      AS unidades,
               SUM(dv.subtotal_item) AS monto_total,
               SUM(dv.almibar_extra) AS almibares
        FROM detalle_ventas dv
        JOIN ventas v ON dv.venta_id = v.id
        WHERE v.fecha BETWEEN ? AND ?
        GROUP BY dv.nombre_producto
        ORDER BY unidades DESC
    ''', (fecha_inicio, fecha_fin)).fetchall()
    productos_periodo = [dict(r) for r in productos_periodo]

    # Horas pico del período
    horas_periodo = conn_dash.execute('''
        SELECT CAST(SUBSTR(hora, 1, 2) AS INTEGER) AS hora_num,
               COUNT(*)   AS cantidad,
               SUM(total) AS monto_total
        FROM ventas
        WHERE fecha BETWEEN ? AND ?
        GROUP BY hora_num
        ORDER BY hora_num
    ''', (fecha_inicio, fecha_fin)).fetchall()
    horas_periodo = [dict(r) for r in horas_periodo]

    # Tendencia diaria del período (para rango)
    tendencia = conn_dash.execute('''
        SELECT fecha,
               COUNT(*)   AS cantidad,
               SUM(total) AS monto_total
        FROM ventas
        WHERE fecha BETWEEN ? AND ?
        GROUP BY fecha
        ORDER BY fecha
    ''', (fecha_inicio, fecha_fin)).fetchall()
    tendencia = [dict(r) for r in tendencia]

    # Pagos del período
    pagos_periodo = conn_dash.execute('''
        SELECT metodo_pago, COUNT(*) AS pedidos, SUM(total) AS monto
        FROM ventas
        WHERE fecha BETWEEN ? AND ?
        GROUP BY metodo_pago
    ''', (fecha_inicio, fecha_fin)).fetchall()
    pagos_periodo = [dict(r) for r in pagos_periodo]

    # Tipo local/takeaway del período
    tipos_periodo = conn_dash.execute('''
        SELECT tipo_consumo, COUNT(*) AS pedidos, SUM(total) AS monto
        FROM ventas
        WHERE fecha BETWEEN ? AND ?
        GROUP BY tipo_consumo
    ''', (fecha_inicio, fecha_fin)).fetchall()
    tipos_periodo = [dict(r) for r in tipos_periodo]

    conn_dash.close()

    # Calcular KPIs globales del período
    total_periodo    = sum(v['total'] for v in ventas_periodo)
    pedidos_periodo  = len(ventas_periodo)
    ticket_prom      = total_periodo / pedidos_periodo if pedidos_periodo > 0 else 0
    prod_top         = productos_periodo[0] if productos_periodo else None

    # ══ KPIs ════════════════════════════════════════════════
    st.markdown('<div class="dash-section">Resumen</div>', unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)

    _plotly_layout = dict(
        plot_bgcolor  = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        font_color    = '#8a7e70',
        font_family   = 'DM Sans',
        margin        = dict(l=0, r=0, t=8, b=8),
    )

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">Recaudado</div>
          <div class="kpi-value">${total_periodo:,.0f}</div>
          <div class="kpi-sub">{pedidos_periodo} pedidos</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">Ticket promedio</div>
          <div class="kpi-value">${ticket_prom:,.0f}</div>
          <div class="kpi-sub">por pedido</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        top_nombre = prod_top['nombre_producto'] if prod_top else "—"
        top_u      = prod_top['unidades'] if prod_top else 0
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">Más vendido</div>
          <div class="kpi-value" style="font-size:20px;padding-top:4px">{top_nombre}</div>
          <div class="kpi-sub">{top_u} unidades</div>
        </div>""", unsafe_allow_html=True)

    # ══ PRODUCTOS VENDIDOS ═══════════════════════════════════
    st.markdown('<div class="dash-section">Productos vendidos</div>', unsafe_allow_html=True)

    if productos_periodo:
        pd_col1, pd_col2 = st.columns([3, 2], gap="large")

        with pd_col1:
            max_u = productos_periodo[0]['unidades'] if productos_periodo else 1
            for p in productos_periodo:
                pct = int((p['unidades'] / max_u) * 100)
                st.markdown(f"""
                <div class="prod-row">
                  <div>
                    <div class="prod-nombre">{p['nombre_producto']}</div>
                    <div class="bar-fill" style="width:{pct}%"></div>
                  </div>
                  <div style="text-align:right">
                    <div class="prod-cant">{int(p['unidades'])} u.</div>
                    <div class="prod-monto">${p['monto_total']:,.0f}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        with pd_col2:
            df_prod = pd.DataFrame(productos_periodo)
            palette = ['#b5a48c','#d4c8b4','#8a7e70','#6e6560','#4a3f35','#c4b49c','#a09080']
            fig_prod = px.pie(
                df_prod, values='unidades', names='nombre_producto',
                color_discrete_sequence=palette,
                hole=0.5,
            )
            fig_prod.update_layout(
                **_plotly_layout,
                legend=dict(font=dict(color='#e8e2d8', size=11), orientation='v'),
                showlegend=True,
            )
            fig_prod.update_traces(
                textinfo='percent',
                textfont_size=12,
                textfont_color='white',
                marker=dict(line=dict(color='#1a1714', width=2)),
            )
            st.plotly_chart(fig_prod, use_container_width=True)
    else:
        st.info("Sin ventas en el período seleccionado.")

    # ══ HORAS PICO + PAGOS ═══════════════════════════════════
    st.markdown('<div class="dash-section">Distribución</div>', unsafe_allow_html=True)

    hc1, hc2 = st.columns([3, 2], gap="large")

    with hc1:
        st.caption("Horas pico")
        horas_all  = list(range(6, 23))
        hora_dict  = {v['hora_num']: v for v in horas_periodo}
        df_horas   = pd.DataFrame([{
            'Hora':   f"{h:02d}:00",
            'Ventas': hora_dict.get(h, {}).get('cantidad', 0),
            'Monto':  hora_dict.get(h, {}).get('monto_total', 0),
        } for h in horas_all])

        if df_horas['Ventas'].sum() > 0:
            fig_h = px.bar(
                df_horas, x='Hora', y='Ventas',
                color='Ventas',
                color_continuous_scale=[[0,'#2d2822'],[0.5,'#7a6e5e'],[1,'#b5a48c']],
                hover_data={'Monto': ':,.0f'},
            )
            fig_h.update_layout(
                **_plotly_layout,
                coloraxis_showscale=False,
                xaxis=dict(tickangle=45, gridcolor='rgba(255,255,255,0.03)', tickfont=dict(size=10)),
                yaxis=dict(gridcolor='rgba(255,255,255,0.03)', tickfont=dict(size=10)),
            )
            fig_h.update_traces(marker_line_width=0)
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.info("Sin datos de horas para el período.")

    with hc2:
        st.caption("Forma de pago")
        if pagos_periodo:
            df_pagos = pd.DataFrame(pagos_periodo)
            df_pagos['metodo_pago'] = df_pagos['metodo_pago'].str.capitalize()
            fig_pago = px.pie(
                df_pagos, values='monto', names='metodo_pago',
                color_discrete_sequence=['#b5a48c','#d4c8b4','#7a6e5e'],
                hole=0.45,
            )
            fig_pago.update_layout(
                **_plotly_layout,
                legend=dict(font=dict(color='#e8e2d8', size=11)),
            )
            fig_pago.update_traces(
                textinfo='percent+label',
                textfont_size=11,
                textfont_color='white',
                marker=dict(line=dict(color='#1a1714', width=2)),
            )
            st.plotly_chart(fig_pago, use_container_width=True)

        st.caption("Local vs. Take-Away")
        if tipos_periodo:
            for t in tipos_periodo:
                lbl = "En local" if t['tipo_consumo'] == 'local' else "Take-Away"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;
                            padding:7px 12px;background:var(--negro2);
                            border:1px solid var(--borde);border-radius:6px;margin-bottom:4px">
                  <span style="font-size:13px;color:var(--texto)">{lbl}</span>
                  <span style="font-size:13px;color:var(--beige);font-weight:600">
                    {t['pedidos']} · ${t['monto']:,.0f}
                  </span>
                </div>""", unsafe_allow_html=True)

    # ══ TENDENCIA (solo visible en modo rango) ═══════════════
    if modo_fecha == "Rango de días" and len(tendencia) > 1:
        st.markdown('<div class="dash-section">Evolución diaria</div>', unsafe_allow_html=True)
        df_tend = pd.DataFrame(tendencia)
        df_tend['fecha'] = pd.to_datetime(df_tend['fecha'])
        df_tend['Día']   = df_tend['fecha'].dt.strftime('%d/%m')

        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=df_tend['Día'], y=df_tend['monto_total'],
            mode='lines+markers',
            line=dict(color='#b5a48c', width=2),
            marker=dict(size=7, color='#d4c8b4', line=dict(width=1.5, color='#1a1714')),
            fill='tozeroy',
            fillcolor='rgba(181,164,140,0.07)',
            hovertemplate='%{x}<br>$%{y:,.0f}<extra></extra>',
        ))
        fig_t.add_trace(go.Bar(
            x=df_tend['Día'], y=df_tend['cantidad'],
            name='Pedidos',
            marker_color='rgba(181,164,140,0.15)',
            yaxis='y2',
            hovertemplate='%{x}<br>%{y} pedidos<extra></extra>',
        ))
        
        # Copia y modificación de layout segura para evitar error por clave duplicada
        t_layout = _plotly_layout.copy()
        t_layout['margin'] = dict(l=0, r=40, t=8, b=30)
        
        fig_t.update_layout(
            **t_layout,
            yaxis =dict(gridcolor='rgba(255,255,255,0.03)', tickprefix='$',
                        tickformat=',.0f', tickfont=dict(size=11)),
            yaxis2=dict(overlaying='y', side='right', showgrid=False,
                        tickfont=dict(size=10, color='#6e6560')),
            xaxis =dict(gridcolor='rgba(255,255,255,0.03)', tickfont=dict(size=11)),
            showlegend=False,
        )
        st.plotly_chart(fig_t, use_container_width=True)

    # ══ LISTADO DE VENTAS ════════════════════════════════════
    st.markdown('<div class="dash-section">Detalle de ventas</div>', unsafe_allow_html=True)

    if ventas_periodo:
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filtro_pago = st.selectbox(
                "Filtrar por pago", ["Todos", "Efectivo", "Débito", "Billetera"],
                key="filtro_pago"
            )
        with fc2:
            filtro_tipo = st.selectbox(
                "Filtrar por tipo", ["Todos", "En local", "Take-Away"],
                key="filtro_tipo"
            )
        with fc3:
            filtro_orden = st.selectbox(
                "Ordenar por", ["Más reciente", "Mayor monto", "Menor monto"],
                key="filtro_orden"
            )

        # Aplicar filtros
        vf = ventas_periodo.copy()
        if filtro_pago != "Todos":
            mapa = {"Efectivo": "efectivo", "Débito": "debito", "Billetera": "billetera"}
            vf = [v for v in vf if v['metodo_pago'] == mapa.get(filtro_pago, '')]
        if filtro_tipo != "Todos":
            mapa_t = {"En local": "local", "Take-Away": "takeaway"}
            vf = [v for v in vf if v['tipo_consumo'] == mapa_t.get(filtro_tipo, '')]
        if filtro_orden == "Mayor monto":
            vf = sorted(vf, key=lambda x: x['total'], reverse=True)
        elif filtro_orden == "Menor monto":
            vf = sorted(vf, key=lambda x: x['total'])

        # Encabezado de tabla
        st.markdown(f"""
        <div style="display:flex;gap:10px;padding:6px 12px;
                    font-size:10px;font-weight:600;letter-spacing:1.5px;
                    text-transform:uppercase;color:var(--texto-muted);
                    border-bottom:1px solid var(--borde);">
          <span style="min-width:50px">Ticket</span>
          <span style="min-width:80px">Fecha</span>
          <span style="min-width:55px">Hora</span>
          <span style="min-width:70px">Tipo</span>
          <span style="flex:1">Productos</span>
          <span style="min-width:80px;text-align:right">Total</span>
        </div>""", unsafe_allow_html=True)

        for v in vf:
            tipo_lbl = "Local" if v['tipo_consumo'] == 'local' else "Take-Away"
            notas_txt = f" · {v['notas']}" if v.get('notas') else ""
            fecha_fmt = v['fecha'][8:10] + '/' + v['fecha'][5:7]
            st.markdown(f"""
            <div class="ticket-row">
              <span class="ticket-num">#{v['ticket_num']:04d}</span>
              <span class="ticket-hora">{fecha_fmt}</span>
              <span class="ticket-hora">{v['hora'][:5]}</span>
              <span class="ticket-tipo">{tipo_lbl}</span>
              <span class="ticket-items">{v.get('items_str','') or ''}{notas_txt}</span>
              <span class="ticket-total">${v['total']:,.0f}</span>
            </div>""", unsafe_allow_html=True)

        # Totalizador
        total_visible = sum(v['total'] for v in vf)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:10px 12px;
                    background:var(--negro3);border-radius:0 0 8px 8px;
                    font-size:13px;font-weight:600;color:var(--blanco);">
          <span>{len(vf)} ventas</span>
          <span>${total_visible:,.0f}</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Sin ventas en el período seleccionado.")


# ─────────────────────────────────────────────────────────────
# TAB 4 ── CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
with tab_cfg:
    st.markdown("### ⚙️ Configuración del Sistema")

    cc1, cc2 = st.columns(2, gap="large")

    with cc1:

        # ── Datos del local ──
        st.markdown("#### 🏪 Datos del Local")

        n_local  = st.text_input("Nombre del local",  db.get_config('nombre_local'))
        dir_local= st.text_input("Dirección",          db.get_config('direccion_local'))
        tel_local= st.text_input("Teléfono",           db.get_config('telefono_local'))
        ancho_tk = st.selectbox(
            "Ancho de ticket (mm)",
            [80, 58],
            index=0 if db.get_config('ancho_ticket_mm') == '80' else 1,
        )

        if st.button("💾 Guardar Datos del Local", use_container_width=True, key="btn_save_local"):
            db.set_config('nombre_local',    n_local)
            db.set_config('direccion_local', dir_local)
            db.set_config('telefono_local',  tel_local)
            db.set_config('ancho_ticket_mm', str(ancho_tk))
            st.success("✅ Datos del local guardados.")

        st.markdown("---")

        # ── Nuevo producto ──
        st.markdown("#### ➕ Agregar Nuevo Producto")

        np_nombre = st.text_input("Nombre del producto",  key="np_nombre")
        npc1, npc2 = st.columns(2)
        with npc1:
            np_precio = st.number_input("Precio ($)", min_value=0.0, step=100.0, key="np_precio")
        with npc2:
            np_cat    = st.selectbox("Categoría", ['cafe', 'comida', 'bebida'], key="np_cat")
        np_cafe_g = st.number_input(
            "Gramos de café molido por unidad (0 si no usa)",
            min_value=0.0, max_value=50.0, value=18.0, step=1.0, key="np_cafe_g"
        )

        if st.button("➕ Agregar Producto", use_container_width=True, key="btn_add_prod"):
            if np_nombre.strip():
                db.agregar_producto(np_nombre.strip(), np_precio, np_cat, np_cafe_g)
                st.success(f"✅ Producto **{np_nombre}** agregado al menú.")
                st.rerun()
            else:
                st.warning("⚠️ Ingresá el nombre del producto.")

    with cc2:

        # ── Lista de productos ──
        st.markdown("#### 📋 Editar Productos Existentes")

        todos = db.get_todos_productos()
        for prod in todos:
            estado_ico = "✅" if prod['activo'] else "❌"
            with st.expander(f"{estado_ico} {prod['nombre']}  —  ${prod['precio']:,.0f}"):
                ep1, ep2 = st.columns(2)
                with ep1:
                    ep_nom = st.text_input("Nombre",    prod['nombre'],       key=f"en_{prod['id']}")
                    ep_pre = st.number_input("Precio",  prod['precio'], step=100.0, key=f"ep_{prod['id']}")
                with ep2:
                    cats_list  = ['cafe', 'comida', 'bebida']
                    ep_cat = st.selectbox(
                        "Categoría", cats_list,
                        index=cats_list.index(prod['categoria']) if prod['categoria'] in cats_list else 0,
                        key=f"ec_{prod['id']}"
                    )
                    ep_g   = st.number_input("Gramos café", prod['cafe_molido_g'],
                                             step=1.0, key=f"eg_{prod['id']}")

                ep_act = st.checkbox("Activo (visible en POS)", bool(prod['activo']),
                                     key=f"ea_{prod['id']}")

                if st.button("💾 Guardar cambios", key=f"es_{prod['id']}", use_container_width=True):
                    db.actualizar_producto(
                        prod['id'], ep_nom, ep_pre, ep_cat, ep_g, int(ep_act)
                    )
                    st.success(f"✅ **{ep_nom}** actualizado.")
                    st.rerun()

    st.markdown("---")
    st.markdown("#### ℹ️ Información del Sistema")
    info1, info2 = st.columns(2)
    with info1:
        st.info(f"📁 Base de datos: `{db.DB_PATH}`")
        st.info(f"🎫 Próximo ticket N°: `{db.get_config('ticket_counter')}`")
    with info2:
        stock_d = db.get_stock()
        cafe_row = next((s for s in stock_d if s['insumo'] == 'Café Molido'), None)
        if cafe_row:
            gramos = cafe_row['cantidad_actual']
            tazas_est = int(gramos / 18)
            st.info(f"☕ Café molido: `{gramos:.0f}g`  (~{tazas_est} cafés)")