import datetime as dt
from datetime import timezone, timedelta

# 1. Guardamos el reloj original en una caja fuerte para evitar el bucle infinito
_reloj_original = dt.datetime
_fecha_original = dt.date

# 2. Creamos nuestro reloj modificado que consulta al original de forma segura
class DatetimeArgentina(_reloj_original):
    @classmethod
    def now(cls, tz=None):
        if tz is None:
            # Pide la hora al reloj original en UTC-3
            return _reloj_original.now(timezone(timedelta(hours=-3))).replace(tzinfo=None)
        return _reloj_original.now(tz)

class DateArgentina(_fecha_original):
    @classmethod
    def today(cls):
        return _reloj_original.now(timezone(timedelta(hours=-3))).date()

# 3. Instalamos el parche seguro
dt.datetime = DatetimeArgentina
dt.date = DateArgentina
# =============================================================
# app.py — punto café OS
# Diseño fiel al mockup: panel izquierdo + derecho, barra stock
# Elementos del vinilo como decoración SVG sutil
# =============================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database as db
import pdf_generator as pdf_gen

st.set_page_config(
    page_title="punto café",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)
db.init_db()

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:    #0f0e0c;  --bg2: #1a1815;  --bg3: #232019;
    --bg4:   #2d2a23;  --bg5: #37332b;
    --beige: #b5a48c;  --beige-dim: #8a7a65;  --beige-br: #cfc0a8;
    --white: #f0ece5;  --text: #d8d0c4;  --muted: #6e655a;
    --green: #3d6b4a;
    --b1: rgba(181,164,140,0.12);
    --b2: rgba(181,164,140,0.22);
    --b3: rgba(181,164,140,0.45);
}

*,*::before,*::after { box-sizing: border-box; }
html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
}
.main .block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="collapsedControl"] { display: none !important; }
footer, #MainMenu { display: none !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: var(--bg5); border-radius: 2px; }

/* ── HEADER ─────────────────────────────────────────────── */
.pc-header {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 15px 28px 13px 22px;
    border-bottom: 1px solid var(--b1);
    background: var(--bg);
    position: relative; overflow: hidden;
}
/* Arcos decorativos del vinilo en el header */
.pc-header::after {
    content: ''; position: absolute;
    right: 240px; top: -70px;
    width: 160px; height: 160px;
    border-radius: 50%;
    border: 22px solid rgba(181,164,140,0.04);
    pointer-events: none;
}
.pc-header::before {
    content: ''; position: absolute;
    right: 140px; top: -30px;
    width: 80px; height: 80px;
    border-radius: 50%;
    border: 12px solid rgba(181,164,140,0.03);
    pointer-events: none;
}
.pc-logo { display: flex; align-items: center; gap: 13px; z-index: 1; }
.pc-brand { font-size: 20px; font-weight: 300; color: var(--white); }
.pc-brand b { font-weight: 600; color: var(--beige); }
.pc-sub { font-size: 9px; font-weight: 600; letter-spacing: 2.5px; text-transform: uppercase; color: var(--muted); margin-top: 2px; }
.pc-time { display: flex; align-items: center; gap: 10px; font-family: 'DM Mono', monospace; font-size: 13px; color: var(--muted); z-index: 1; }
.pc-dot { width: 4px; height: 4px; border-radius: 50%; background: var(--beige-dim); opacity: .5; }

/* ── TABS ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--b1) !important;
    padding: 0 24px !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    padding: 14px 22px !important; border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; transition: color .2s !important;
}
.stTabs [aria-selected="true"] {
    color: var(--beige) !important;
    border-bottom: 2px solid var(--beige) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }

/* ── LABELS ─────────────────────────────────────────────── */
.sec-lbl {
    font-size: 9px; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: var(--muted); margin-bottom: 9px;
}
.cat-lbl {
    font-size: 9px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: var(--muted);
    margin: 16px 0 9px 0; padding-bottom: 7px;
    border-bottom: 1px solid var(--b1);
    display: flex; align-items: center; gap: 9px;
}
/* Medio círculo del vinilo antes de cada categoría */
.cat-lbl::before {
    content: ''; display: inline-block;
    width: 11px; height: 6px;
    border-radius: 6px 6px 0 0;
    border: 1.5px solid var(--beige-dim); border-bottom: none;
    opacity: .5; flex-shrink: 0;
}

/* ── BOTONES STREAMLIT ──────────────────────────────────── */
div[data-testid="stButton"] > button {
    background: var(--bg2) !important; color: var(--text) !important;
    border: 1px solid var(--b2) !important; border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: .8px !important; padding: 7px 12px !important;
    transition: all .15s !important; min-height: 34px !important;
    white-space: pre-wrap !important; line-height: 1.3 !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--bg3) !important; border-color: var(--b3) !important;
    color: var(--white) !important; transform: translateY(-1px) !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: var(--beige) !important; color: var(--bg) !important;
    border-color: var(--beige) !important; font-weight: 700 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    min-height: 48px !important; font-size: 11px !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: var(--beige-br) !important; transform: translateY(-1px) !important;
}
/* Botones de producto más grandes */
div[data-testid="stColumn"] div[data-testid="stButton"] > button {
    min-height: 68px !important; font-size: 12px !important;
    position: relative !important; overflow: hidden !important;
}
/* Círculo decorativo del vinilo en cada botón de producto */
div[data-testid="stColumn"] div[data-testid="stButton"] > button::after {
    content: ''; position: absolute; top: -8px; right: -8px;
    width: 24px; height: 24px; border-radius: 50%;
    border: 4px solid rgba(181,164,140,0.07); pointer-events: none;
}

/* ── INPUTS ─────────────────────────────────────────────── */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div {
    background: var(--bg2) !important; color: var(--text) !important;
    border: 1px solid var(--b2) !important; border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus {
    border-color: var(--beige) !important;
    box-shadow: 0 0 0 2px rgba(181,164,140,.1) !important;
}
label, .stSelectbox label, .stNumberInput label,
.stTextInput label, .stTextArea label {
    color: var(--muted) !important; font-size: 9px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}

/* ── MÉTRICAS ───────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg2); border: 1px solid var(--b1);
    border-radius: 8px; padding: 17px 19px;
    position: relative; overflow: hidden;
}
/* Círculo decorativo en cada métrica */
[data-testid="stMetric"]::after {
    content: ''; position: absolute; bottom: -16px; right: -16px;
    width: 50px; height: 50px; border-radius: 50%;
    border: 8px solid rgba(181,164,140,.06);
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important; font-size: 9px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
}
[data-testid="stMetricValue"] {
    color: var(--white) !important; font-size: 27px !important;
    font-weight: 300 !important;
}
[data-testid="stMetricDelta"] { color: var(--beige) !important; font-size: 11px !important; }

/* ── MISC ───────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    background: var(--bg2); border-radius: 8px;
    border: 1px solid var(--b1); overflow: hidden;
}
.stAlert { border-radius: 7px !important; }
.streamlit-expanderHeader {
    background: var(--bg2) !important; border: 1px solid var(--b1) !important;
    border-radius: 7px !important; color: var(--text) !important;
}
.stRadio [data-testid="stMarkdownContainer"] p { color: var(--text) !important; font-size: 13px !important; }
.stCheckbox label p { color: var(--text) !important; font-size: 13px !important; }
.stCaption p { color: var(--muted) !important; font-size: 11px !important; }
hr { border-color: var(--b1) !important; margin: 10px 0 !important; }

/* ── CARRITO ────────────────────────────────────────────── */
.c-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px;
}
.c-title { font-size: 9px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: var(--muted); }
.c-badge {
    font-size: 9px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; padding: 4px 10px;
    border: 1px solid var(--b2); border-radius: 4px; color: var(--beige);
}
.total-wrap { margin: 13px 0 3px 0; padding: 13px 0; border-top: 1px solid var(--b2); }
.total-lbl { font-size: 9px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase; color: var(--muted); margin-bottom: 3px; }
.total-val { font-size: 36px; font-weight: 300; color: var(--white); letter-spacing: .5px; line-height: 1; }

/* ── BARRA STOCK BAJO ───────────────────────────────────── */
.stock-bar {
    background: var(--bg2); border-top: 1px solid rgba(180,80,80,.2);
    padding: 9px 20px; display: flex; align-items: center; gap: 16px;
    font-size: 12px; margin-top: 10px; border-radius: 8px;
}
.stock-bar-alert { display: flex; align-items: center; gap: 7px; color: #c07070; font-weight: 700; font-size: 11px; }
.stock-bar-items { display: flex; gap: 16px; flex: 1; color: var(--muted); }
.stock-bar-items b { color: var(--text); }

/* ── DASHBOARD ──────────────────────────────────────────── */
.d-sep {
    font-size: 9px; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: var(--muted);
    padding: 16px 0 9px 0; border-bottom: 1px solid var(--b1);
    margin-bottom: 13px; display: flex; align-items: center; gap: 9px;
}
/* Arco del vinilo antes de cada sección del dashboard */
.d-sep::before {
    content: ''; display: inline-block;
    width: 14px; height: 7px; border-radius: 7px 7px 0 0;
    border: 1.5px solid var(--beige-dim); border-bottom: none;
    opacity: .35; flex-shrink: 0;
}
.kpi-card {
    background: var(--bg2); border: 1px solid var(--b1);
    border-radius: 8px; padding: 17px 19px;
    position: relative; overflow: hidden; margin-bottom: 4px;
}
.kpi-card::after {
    content: ''; position: absolute; bottom: -20px; right: -20px;
    width: 64px; height: 64px; border-radius: 50%;
    border: 10px solid rgba(181,164,140,.05);
}
.kpi-l { font-size: 9px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin-bottom: 7px; }
.kpi-v { font-size: 29px; font-weight: 300; color: var(--white); line-height: 1; }
.kpi-s { font-size: 11px; color: var(--beige-dim); margin-top: 4px; }
.pr-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 13px; background: var(--bg2); border: 1px solid var(--b1);
    border-radius: 7px; margin-bottom: 5px;
}
.pr-bar { height: 3px; background: var(--beige-dim); border-radius: 2px; margin-top: 5px; opacity: .5; }
.tk-row {
    display: flex; gap: 10px; align-items: center;
    padding: 8px 12px; border-bottom: 1px solid var(--b1); font-size: 12px;
}
.tk-num  { color: var(--beige); font-weight: 600; min-width: 46px; font-family: 'DM Mono', monospace; }
.tk-f    { color: var(--muted); min-width: 46px; font-family: 'DM Mono', monospace; }
.tk-h    { color: var(--muted); min-width: 44px; font-family: 'DM Mono', monospace; }
.tk-t    { color: var(--muted); min-width: 60px; font-size: 10px; }
.tk-i    { color: var(--text); flex: 1; }
.tk-tot  { color: var(--white); font-weight: 500; min-width: 72px; text-align: right; }
.s-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 11px 15px; background: var(--bg2); border: 1px solid var(--b1);
    border-radius: 7px; margin-bottom: 5px;
}
.s-n { font-size: 13px; color: var(--text); }
.s-v { font-size: 13px; color: var(--white); font-weight: 500; font-family: 'DM Mono', monospace; }
.s-ok    { color: #5a9469; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
.s-bajo  { color: #c07070; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
.s-vacio { color: #a04040; font-size: 9px; font-weight: 700; letter-spacing: 1px; }

.pc-footer {
    padding: 8px 24px; display: flex; align-items: center;
    justify-content: space-between; font-size: 10px; color: var(--muted);
    border-top: 1px solid var(--b1); margin-top: 14px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ESTADO
# ─────────────────────────────────────────────────────────────
def _init():
    d = {'carrito': [], 'tipo_consumo': 'local', 'metodo_pago': 'efectivo',
         'venta_ok': None, 'pdf_path': None}
    for k, v in d.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

def agregar(prod):
    for i in st.session_state.carrito:
        if i['producto_id'] == prod['id']:
            i['cantidad'] += 1; return
    st.session_state.carrito.append({
        'producto_id': prod['id'], 'nombre_producto': prod['nombre'],
        'cantidad': 1, 'precio_unitario': prod['precio'],
        'almibar_extra': False, 'cafe_molido_g': prod['cafe_molido_g'],
    })

def quitar(pid):
    st.session_state.carrito = [i for i in st.session_state.carrito if i['producto_id'] != pid]

def decrementar(pid):
    for i in st.session_state.carrito:
        if i['producto_id'] == pid:
            i['cantidad'] -= 1
            if i['cantidad'] <= 0: quitar(pid)
            return

def limpiar(): st.session_state.carrito = []
def total(): return sum(i['cantidad'] * i['precio_unitario'] for i in st.session_state.carrito)
def fmt(n): return f"${n:,.0f}".replace(",", ".")

# ─────────────────────────────────────────────────────────────
# ISOLOGO SVG
# ─────────────────────────────────────────────────────────────
ISO = (
    '<svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="50" cy="50" r="45" fill="none" stroke="#f0ece5" stroke-width="5"/>'
    '<circle cx="50" cy="50" r="29" fill="#f0ece5"/>'
    '<circle cx="50" cy="50" r="21" fill="#0f0e0c"/>'
    '<path d="M40 41 Q44 37 51 39" fill="none" stroke="#f0ece5" stroke-width="2.5" stroke-linecap="round"/>'
    '<circle cx="50" cy="50" r="4" fill="none" stroke="#f0ece5" stroke-width="1.8"/>'
    '<circle cx="50" cy="50" r="1.5" fill="#f0ece5"/>'
    '<rect x="77" y="44" width="10" height="12" rx="2.5" fill="#f0ece5"/>'
    '</svg>'
)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
now = datetime.now()
st.markdown(
    f'<div class="pc-header">'
    f'<div class="pc-logo">{ISO}'
    f'<div><div class="pc-brand">punto <b>caf\u00e9</b></div>'
    f'<div class="pc-sub">Coffee Operating System</div></div></div>'
    f'<div class="pc-time"><span>{now.strftime("%d/%m/%Y")}</span>'
    f'<span class="pc-dot"></span><span>{now.strftime("%H:%M")}</span></div>'
    f'</div>', unsafe_allow_html=True
)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab_pos, tab_stk, tab_dash, tab_cfg = st.tabs([
    "Venta", "Stock", "Dashboard", "Configuraci\u00f3n"
])

# ═════════════════════════════════════════════════════════════
# TAB VENTA
# ═════════════════════════════════════════════════════════════
with tab_pos:
    productos = db.get_productos_activos()
    cats = {}
    for p in productos:
        cats.setdefault(p['categoria'], []).append(p)

    col_izq, col_der = st.columns([3, 2], gap="small")

    # ── IZQUIERDA: productos ──────────────────────────────────
    with col_izq:
        st.markdown('<div style="padding:18px 20px 0 20px">', unsafe_allow_html=True)

        # Tipo de consumo — igual al mockup
        st.markdown('<div class="sec-lbl">Tipo de Consumo</div>', unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        with tc1:
            lbl = "En Local  \u2713" if st.session_state.tipo_consumo == 'local' else "En Local"
            if st.button(lbl, key="btn_local", use_container_width=True):
                st.session_state.tipo_consumo = 'local'; st.rerun()
        with tc2:
            lbl = "Take-Away  \u2713" if st.session_state.tipo_consumo == 'takeaway' else "Take-Away"
            if st.button(lbl, key="btn_ta", use_container_width=True):
                st.session_state.tipo_consumo = 'takeaway'; st.rerun()

        # Grilla de productos
        cat_map = {'cafe': 'Cafe', 'comida': 'Comida', 'bebida': 'Bebidas'}
        for cat, prods in cats.items():
            st.markdown(f'<div class="cat-lbl">{cat_map.get(cat, cat.upper())}</div>', unsafe_allow_html=True)
            cols = st.columns(6)
            for idx, prod in enumerate(prods):
                with cols[idx % 6]:
                    precio_str = fmt(prod['precio'])
                    if st.button(f"{prod['nombre']}\n{precio_str}", key=f"p_{prod['id']}", use_container_width=True):
                        agregar(prod); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Barra de stock bajo — igual al mockup (al fondo del panel izquierdo)
        stock_bajo = db.get_stock_bajo()
        if stock_bajo:
            items_h = "  |  ".join(f"<b>{s['insumo']}:</b> {s['cantidad_actual']:.0f} {s['unidad']}" for s in stock_bajo)
            st.markdown(
                f'<div class="stock-bar">'
                f'<div class="stock-bar-alert">&#9651; Stock Bajo</div>'
                f'<div class="stock-bar-items">{items_h}</div>'
                f'<span style="color:var(--beige-dim);font-size:11px">Ver gesti\u00f3n de stock \u2192</span>'
                f'</div>', unsafe_allow_html=True
            )

    # ── DERECHA: carrito ──────────────────────────────────────
    with col_der:
        st.markdown('<div style="padding:18px 20px 0 16px">', unsafe_allow_html=True)

        tipo_lbl = "En Local" if st.session_state.tipo_consumo == 'local' else "Take-Away"
        st.markdown(
            f'<div class="c-header">'
            f'<div class="c-title">Pedido Actual</div>'
            f'<div class="c-badge">{tipo_lbl}</div>'
            f'</div>', unsafe_allow_html=True
        )

        if not st.session_state.carrito:
            st.markdown(
                '<div style="text-align:center;padding:40px 0;color:var(--muted)">'
                '<svg width="44" height="44" viewBox="0 0 100 100" style="opacity:.15;display:block;margin:0 auto 12px" xmlns="http://www.w3.org/2000/svg">'
                '<circle cx="50" cy="50" r="44" fill="none" stroke="#b5a48c" stroke-width="5"/>'
                '<circle cx="50" cy="50" r="28" fill="#b5a48c" opacity=".25"/>'
                '<circle cx="50" cy="50" r="20" fill="#0f0e0c"/>'
                '<rect x="76" y="44" width="10" height="12" rx="3" fill="#b5a48c" opacity=".4"/>'
                '</svg>'
                '<div style="font-size:12px;letter-spacing:.5px">Pedido vac\u00edo</div>'
                '<div style="font-size:11px;margin-top:4px;opacity:.5">Toc\u00e1 un producto</div>'
                '</div>', unsafe_allow_html=True
            )
        else:
            for idx, item in enumerate(st.session_state.carrito):
                nombre = item['nombre_producto']
                cant   = item['cantidad']
                precio = item['precio_unitario']
                sub    = cant * precio

                ca, cb, cc, cd, ce, cf = st.columns([4, 1, 1, 1, 2, 1])
                with ca:
                    st.markdown(f"<div style='padding:9px 0;font-size:13px'>{nombre}</div>", unsafe_allow_html=True)
                with cb:
                    if st.button("\u2212", key=f"dec_{idx}"):
                        decrementar(item['producto_id']); st.rerun()
                with cc:
                    st.markdown(f"<div style='text-align:center;padding:9px 0;font-size:13px'>{cant}</div>", unsafe_allow_html=True)
                with cd:
                    if st.button("+", key=f"inc_{idx}"):
                        agregar({'id': item['producto_id'], 'nombre': nombre,
                                 'precio': precio, 'cafe_molido_g': item['cafe_molido_g']})
                        st.rerun()
                with ce:
                    st.markdown(f"<div style='text-align:right;padding:9px 0;font-size:13px;color:#cfc0a8'>{fmt(sub)}</div>", unsafe_allow_html=True)
                with cf:
                    if st.button("\u00d7", key=f"del_{idx}"):
                        quitar(item['producto_id']); st.rerun()

                st.markdown("<div style='border-bottom:1px solid var(--b1);margin-bottom:1px'></div>", unsafe_allow_html=True)

        # Total
        t = total()
        st.markdown(
            f'<div class="total-wrap">'
            f'<div class="total-lbl">Total</div>'
            f'<div class="total-val">{fmt(t)}</div>'
            f'</div>', unsafe_allow_html=True
        )

        # Forma de pago
        st.markdown('<div class="sec-lbl">Forma de Pago</div>', unsafe_allow_html=True)
        pp1, pp2, pp3 = st.columns(3)
        with pp1:
            lbl = "Efectivo \u2713" if st.session_state.metodo_pago == 'efectivo' else "Efectivo"
            if st.button(lbl, key="pay_ef", use_container_width=True):
                st.session_state.metodo_pago = 'efectivo'; st.rerun()
        with pp2:
            lbl = "D\u00e9bito \u2713" if st.session_state.metodo_pago == 'debito' else "D\u00e9bito"
            if st.button(lbl, key="pay_db", use_container_width=True):
                st.session_state.metodo_pago = 'debito'; st.rerun()
        with pp3:
            lbl = "Billetera \u2713" if st.session_state.metodo_pago == 'billetera' else "Billetera"
            if st.button(lbl, key="pay_bl", use_container_width=True):
                st.session_state.metodo_pago = 'billetera'; st.rerun()

        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-lbl">Notas del Pedido</div>', unsafe_allow_html=True)
        nota = st.text_input("nota", label_visibility="collapsed",
                             placeholder="Sin az\u00facar, extra caliente...", key="nota_ped")

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        ba, bb = st.columns([1, 2])
        with ba:
            if st.button("\U0001f5d1 Cancelar", key="btn_cancel", use_container_width=True):
                limpiar(); st.rerun()
        with bb:
            if st.button(f"Cobrar  {fmt(t)}", key="btn_cobrar",
                         use_container_width=True, type="primary",
                         disabled=(len(st.session_state.carrito) == 0)):
                try:
                    vid, tnum, sub, tot = db.registrar_venta(
                        st.session_state.tipo_consumo,
                        st.session_state.metodo_pago,
                        st.session_state.carrito, nota
                    )
                    pp = pdf_gen.generar_ticket(
                        venta_id=vid, ticket_num=tnum,
                        tipo_consumo=st.session_state.tipo_consumo,
                        metodo_pago=st.session_state.metodo_pago,
                        items=st.session_state.carrito,
                        subtotal=sub, total=tot,
                        nombre_local=db.get_config('nombre_local') or 'punto caf\u00e9',
                        direccion=db.get_config('direccion_local'),
                        telefono=db.get_config('telefono_local'),
                        notas=nota,
                        ancho_mm=int(db.get_config('ancho_ticket_mm') or 80),
                    )
                    st.session_state.venta_ok  = {'ticket_num': tnum, 'total': tot}
                    st.session_state.pdf_path  = pp
                    limpiar(); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.venta_ok:
            v = st.session_state.venta_ok
            st.success(f"\u2713 Ticket #{v['ticket_num']:04d} — {fmt(v['total'])}")
            pp = st.session_state.pdf_path
            if pp and os.path.exists(pp):
                with open(pp, 'rb') as f:
                    st.download_button("Descargar Ticket PDF", data=f.read(),
                                       file_name=f"ticket_{v['ticket_num']:04d}.pdf",
                                       mime="application/pdf", use_container_width=True)
            if st.button("Nuevo Pedido", use_container_width=True, key="btn_nuevo"):
                st.session_state.venta_ok = None
                st.session_state.pdf_path = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# TAB STOCK
# ═════════════════════════════════════════════════════════════
with tab_stk:
    st.markdown("<div style='padding:20px'>", unsafe_allow_html=True)
    cs1, cs2 = st.columns([3, 2], gap="large")

    with cs1:
        st.markdown('<div class="d-sep">Estado del Stock</div>', unsafe_allow_html=True)
        stock_data = db.get_stock()
        for s in stock_data:
            if s['cantidad_actual'] <= 0:
                est = f'<span class="s-vacio">SIN STOCK</span>'
            elif s['cantidad_actual'] <= s['cantidad_alerta']:
                est = f'<span class="s-bajo">BAJO</span>'
            else:
                est = f'<span class="s-ok">OK</span>'
            st.markdown(
                f'<div class="s-row"><div class="s-n">{s["insumo"]}</div>'
                f'<div style="display:flex;align-items:center;gap:14px">'
                f'<div class="s-v">{s["cantidad_actual"]:.0f} {s["unidad"]}</div>{est}</div></div>',
                unsafe_allow_html=True
            )

        st.markdown('<div class="d-sep" style="margin-top:20px">Cargar Stock</div>', unsafe_allow_html=True)
        insumos = [s['insumo'] for s in stock_data]
        csa, csb = st.columns([2, 1])
        with csa:
            ins_sel = st.selectbox("Insumo", insumos, key="ins_car")
        with csb:
            unidad_s = next((s['unidad'] for s in stock_data if s['insumo'] == ins_sel), '')
            cant_car = st.number_input(f"Cantidad ({unidad_s})", min_value=0.1, value=500.0, step=100.0, key="cant_car")
        if st.button("Cargar Stock", use_container_width=True, key="btn_car", type="primary"):
            db.actualizar_stock(ins_sel, cant_car)
            st.success(f"+{cant_car:.0f} {unidad_s} de {ins_sel}")
            st.rerun()

        st.markdown('<div class="d-sep" style="margin-top:20px">Umbral de Alerta</div>', unsafe_allow_html=True)
        ins_umb = st.selectbox("Insumo", insumos, key="ins_umb")
        nv_umb = st.number_input("Nuevo umbral", min_value=0.0, value=200.0, step=50.0, key="nv_umb")
        if st.button("Guardar Umbral", use_container_width=True, key="btn_umb"):
            db.actualizar_umbral_stock(ins_umb, nv_umb)
            st.success(f"Umbral de {ins_umb} actualizado")
            st.rerun()

    with cs2:
        st.markdown('<div class="d-sep">Registrar Merma</div>', unsafe_allow_html=True)
        ins_mer = st.selectbox("Insumo", insumos, key="ins_mer")
        un_mer  = next((s['unidad'] for s in stock_data if s['insumo'] == ins_mer), '')
        cant_mer= st.number_input(f"Cantidad ({un_mer})", min_value=0.1, value=10.0, step=1.0, key="cant_mer")
        mot_mer = st.text_area("Motivo", placeholder="Caf\u00e9 pasado, derrame...", height=80, key="mot_mer")
        if st.button("Registrar Merma", use_container_width=True, key="btn_mer"):
            if mot_mer.strip():
                db.registrar_merma(ins_mer, cant_mer, mot_mer.strip())
                st.success("Merma registrada"); st.rerun()
            else:
                st.warning("Ingres\u00e1 el motivo.")

        st.markdown('<div class="d-sep" style="margin-top:20px">Mermas Recientes</div>', unsafe_allow_html=True)
        mermas = db.get_mermas(7)
        if mermas:
            for m in mermas[:6]:
                st.markdown(
                    f'<div class="s-row"><div><div class="s-n">{m["insumo"]}</div>'
                    f'<div style="font-size:11px;color:var(--muted);margin-top:2px">{m["motivo"][:38]}</div></div>'
                    f'<div class="s-v">{m["cantidad"]:.0f}</div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown('<div style="color:var(--muted);font-size:13px;padding:8px 0">Sin mermas en 7 d\u00edas</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# TAB DASHBOARD
# ═════════════════════════════════════════════════════════════
with tab_dash:
    st.markdown("<div style='padding:20px 20px 60px 20px'>", unsafe_allow_html=True)

    PL = dict(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
              font_color='#6e655a', font_family='DM Sans',
              margin=dict(l=0, r=0, t=8, b=30))

    # Selector de período
    st.markdown('<div class="d-sep">Per\u00edodo</div>', unsafe_allow_html=True)

    if 'dash_fv' not in st.session_state:
        st.session_state.dash_fv = date.today()

    dc1, dc2, dc3 = st.columns([2, 3, 3])
    with dc1:
        modo = st.radio("Modo", ["D\u00eda", "Rango"], key="dash_modo", label_visibility="collapsed")
    with dc2:
        if modo == "D\u00eda":
            qa, qb = st.columns(2)
            with qa:
                if st.button("Hoy",  key="q_hoy",  use_container_width=True):
                    st.session_state.dash_fv = date.today(); st.rerun()
            with qb:
                if st.button("Ayer", key="q_ayer", use_container_width=True):
                    st.session_state.dash_fv = date.today() - timedelta(days=1); st.rerun()
            fs = st.date_input("Fecha", value=st.session_state.dash_fv, key="dash_fu")
            st.session_state.dash_fv = fs
            fi = ff = fs.strftime('%Y-%m-%d')
        else:
            rng = st.date_input("Rango", value=(date.today() - timedelta(days=6), date.today()), key="dash_rng")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                fi, ff = rng[0].strftime('%Y-%m-%d'), rng[1].strftime('%Y-%m-%d')
            else:
                fi = ff = date.today().strftime('%Y-%m-%d')
    with dc3:
        fechas = db.get_fechas_con_ventas(15)
        if fechas:
            st.caption("D\u00edas con ventas:")
            st.markdown(
                "<span style='font-size:11px;color:var(--muted)'>" +
                "  \u00b7  ".join(f[8:10]+'/'+f[5:7] for f in fechas[:12]) + "</span>",
                unsafe_allow_html=True
            )

    # Datos
    conn_d = db.get_connection()
    vp = conn_d.execute('''
        SELECT v.*, GROUP_CONCAT(dv.nombre_producto||' x'||dv.cantidad,', ') AS items_str
        FROM ventas v LEFT JOIN detalle_ventas dv ON v.id=dv.venta_id
        WHERE v.fecha BETWEEN ? AND ? GROUP BY v.id ORDER BY v.fecha DESC, v.hora DESC
    ''', (fi, ff)).fetchall()
    vp = [dict(r) for r in vp]

    pp2 = conn_d.execute('''
        SELECT dv.nombre_producto, SUM(dv.cantidad) AS u, SUM(dv.subtotal_item) AS m
        FROM detalle_ventas dv JOIN ventas v ON dv.venta_id=v.id
        WHERE v.fecha BETWEEN ? AND ? GROUP BY dv.nombre_producto ORDER BY u DESC
    ''', (fi, ff)).fetchall()
    pp2 = [dict(r) for r in pp2]

    hp = conn_d.execute('''
        SELECT CAST(SUBSTR(hora,1,2) AS INTEGER) AS h, COUNT(*) AS n, SUM(total) AS m
        FROM ventas WHERE fecha BETWEEN ? AND ? GROUP BY h ORDER BY h
    ''', (fi, ff)).fetchall()
    hp = [dict(r) for r in hp]

    pgp = conn_d.execute('''
        SELECT metodo_pago, COUNT(*) AS n, SUM(total) AS m
        FROM ventas WHERE fecha BETWEEN ? AND ? GROUP BY metodo_pago
    ''', (fi, ff)).fetchall()
    pgp = [dict(r) for r in pgp]

    tp2 = conn_d.execute('''
        SELECT tipo_consumo, COUNT(*) AS n, SUM(total) AS m
        FROM ventas WHERE fecha BETWEEN ? AND ? GROUP BY tipo_consumo
    ''', (fi, ff)).fetchall()
    tp2 = [dict(r) for r in tp2]

    tdp = conn_d.execute('''
        SELECT fecha, COUNT(*) AS n, SUM(total) AS m
        FROM ventas WHERE fecha BETWEEN ? AND ? GROUP BY fecha ORDER BY fecha
    ''', (fi, ff)).fetchall()
    tdp = [dict(r) for r in tdp]
    conn_d.close()

    tot_p = sum(v['total'] for v in vp)
    ped_p = len(vp)
    tk_p  = tot_p / ped_p if ped_p else 0
    top   = pp2[0] if pp2 else None

    # KPIs
    st.markdown('<div class="d-sep">Resumen</div>', unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-l">Recaudado</div><div class="kpi-v">{fmt(tot_p)}</div><div class="kpi-s">{ped_p} pedidos</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-l">Ticket Promedio</div><div class="kpi-v">{fmt(tk_p)}</div><div class="kpi-s">por pedido</div></div>', unsafe_allow_html=True)
    with k3:
        tn = top['nombre_producto'] if top else "\u2014"
        tu = top['u'] if top else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-l">M\u00e1s Vendido</div><div class="kpi-v" style="font-size:20px;padding-top:4px">{tn}</div><div class="kpi-s">{tu} u.</div></div>', unsafe_allow_html=True)

    # Productos
    st.markdown('<div class="d-sep">Productos Vendidos</div>', unsafe_allow_html=True)
    pd1, pd2 = st.columns([3, 2], gap="large")
    with pd1:
        if pp2:
            mx = pp2[0]['u']
            for p in pp2:
                pct = int((p['u']/mx)*100) if mx else 0
                st.markdown(
                    f'<div class="pr-row">'
                    f'<div style="flex:1"><div style="font-size:13px;color:var(--text)">{p["nombre_producto"]}</div>'
                    f'<div class="pr-bar" style="width:{pct}%"></div></div>'
                    f'<div style="text-align:right;margin-left:14px">'
                    f'<div style="font-size:13px;color:var(--beige);font-weight:600">{int(p["u"])} u.</div>'
                    f'<div style="font-size:11px;color:var(--muted)">{fmt(p["m"])}</div></div></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Sin ventas en el per\u00edodo.")
    with pd2:
        if pp2:
            df_pr = pd.DataFrame(pp2)
            fig_pr = px.pie(df_pr, values='u', names='nombre_producto', hole=0.48,
                            color_discrete_sequence=['#b5a48c','#d4c8b4','#8a7a65','#6e5f50','#4a3f35'])
            fig_pr.update_layout(**PL, legend=dict(font=dict(color='#d8d0c4', size=10)))
            fig_pr.update_traces(textinfo='percent', textfont_size=11, textfont_color='white',
                                 marker=dict(line=dict(color='#0f0e0c', width=2)))
            st.plotly_chart(fig_pr, use_container_width=True)

    # Horas pico + Pagos
    st.markdown('<div class="d-sep">Distribuci\u00f3n</div>', unsafe_allow_html=True)
    hc1, hc2 = st.columns([3, 2], gap="large")
    with hc1:
        st.caption("Horas pico")
        hd = {v['h']: v for v in hp}
        df_h = pd.DataFrame([{'Hora': f"{h:02d}:00", 'Ventas': hd.get(h, {}).get('n', 0)} for h in range(6, 23)])
        if df_h['Ventas'].sum() > 0:
            fig_h = px.bar(df_h, x='Hora', y='Ventas', color='Ventas',
                           color_continuous_scale=[[0,'#222019'],[.5,'#7a6e5e'],[1,'#b5a48c']])
            fig_h.update_layout(**PL, coloraxis_showscale=False,
                xaxis=dict(tickangle=45, gridcolor='rgba(255,255,255,0.03)', tickfont=dict(size=9)),
                yaxis=dict(gridcolor='rgba(255,255,255,0.03)', tickfont=dict(size=9)))
            fig_h.update_traces(marker_line_width=0)
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.info("Sin datos de horas.")
    with hc2:
        st.caption("Forma de pago")
        if pgp:
            df_pg = pd.DataFrame(pgp)
            df_pg['metodo_pago'] = df_pg['metodo_pago'].str.capitalize()
            fig_pg = px.pie(df_pg, values='m', names='metodo_pago', hole=0.45,
                            color_discrete_sequence=['#b5a48c','#d4c8b4','#7a6e5e'])
            fig_pg.update_layout(**PL, legend=dict(font=dict(color='#d8d0c4', size=10)))
            fig_pg.update_traces(textinfo='percent+label', textfont_size=10, textfont_color='white',
                                 marker=dict(line=dict(color='#0f0e0c', width=2)))
            st.plotly_chart(fig_pg, use_container_width=True)
        st.caption("Local vs. Take-Away")
        for t in tp2:
            lbl = "En Local" if t['tipo_consumo'] == 'local' else "Take-Away"
            st.markdown(
                f'<div class="s-row" style="margin-bottom:5px">'
                f'<span style="font-size:13px;color:var(--text)">{lbl}</span>'
                f'<span style="font-size:13px;color:var(--beige);font-weight:600">{t["n"]} \u00b7 {fmt(t["m"])}</span>'
                f'</div>', unsafe_allow_html=True
            )

    # Tendencia
    if modo == "Rango" and len(tdp) > 1:
        st.markdown('<div class="d-sep">Evoluci\u00f3n Diaria</div>', unsafe_allow_html=True)
        df_t = pd.DataFrame(tdp)
        df_t['fecha'] = pd.to_datetime(df_t['fecha'])
        df_t['D'] = df_t['fecha'].dt.strftime('%d/%m')
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=df_t['D'], y=df_t['m'], mode='lines+markers',
            line=dict(color='#b5a48c', width=2),
            marker=dict(size=7, color='#d4c8b4', line=dict(width=1.5, color='#0f0e0c')),
            fill='tozeroy', fillcolor='rgba(181,164,140,0.06)',
        ))
        fig_t.update_layout(**{**PL, 'margin': dict(l=0, r=40, t=8, b=30)},
            showlegend=False,
            yaxis=dict(gridcolor='rgba(255,255,255,0.03)', tickprefix='$', tickformat=',.0f', tickfont=dict(size=10)),
            xaxis=dict(gridcolor='rgba(255,255,255,0.03)', tickfont=dict(size=10)))
        st.plotly_chart(fig_t, use_container_width=True)

    # Listado ventas
    st.markdown('<div class="d-sep">Detalle de Ventas</div>', unsafe_allow_html=True)
    if vp:
        fa, fb, fc = st.columns(3)
        with fa:
            fp = st.selectbox("Pago", ["Todos","Efectivo","D\u00e9bito","Billetera"], key="fp")
        with fb:
            ft = st.selectbox("Tipo", ["Todos","En local","Take-Away"], key="ft")
        with fc:
            fo = st.selectbox("Orden", ["M\u00e1s reciente","Mayor monto","Menor monto"], key="fo")

        vf = vp.copy()
        if fp != "Todos":
            mp = {"Efectivo":"efectivo","D\u00e9bito":"debito","Billetera":"billetera"}
            vf = [v for v in vf if v['metodo_pago'] == mp.get(fp,'')]
        if ft != "Todos":
            mt = {"En local":"local","Take-Away":"takeaway"}
            vf = [v for v in vf if v['tipo_consumo'] == mt.get(ft,'')]
        if fo == "Mayor monto":   vf = sorted(vf, key=lambda x: x['total'], reverse=True)
        elif fo == "Menor monto": vf = sorted(vf, key=lambda x: x['total'])

        st.markdown(
            '<div style="display:flex;gap:10px;padding:6px 12px;font-size:9px;font-weight:700;'
            'letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);'
            'border-bottom:1px solid var(--b1)">'
            '<span style="min-width:46px">Ticket</span>'
            '<span style="min-width:46px">Fecha</span>'
            '<span style="min-width:44px">Hora</span>'
            '<span style="min-width:60px">Tipo</span>'
            '<span style="flex:1">Productos</span>'
            '<span style="min-width:72px;text-align:right">Total</span>'
            '</div>', unsafe_allow_html=True
        )
        for v in vf:
            tl = "Local" if v['tipo_consumo'] == 'local' else "Take-Away"
            fd = v['fecha'][8:10]+'/'+v['fecha'][5:7]
            nt = f" \u00b7 {v['notas']}" if v.get('notas') else ""
            st.markdown(
                f'<div class="tk-row">'
                f'<span class="tk-num">#{v["ticket_num"]:04d}</span>'
                f'<span class="tk-f">{fd}</span>'
                f'<span class="tk-h">{v["hora"][:5]}</span>'
                f'<span class="tk-t">{tl}</span>'
                f'<span class="tk-i">{v.get("items_str","") or ""}{nt}</span>'
                f'<span class="tk-tot">{fmt(v["total"])}</span>'
                f'</div>', unsafe_allow_html=True
            )
        tv = sum(v['total'] for v in vf)
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:9px 12px;'
            f'background:var(--bg3);border-radius:0 0 7px 7px;font-size:12px;'
            f'font-weight:600;color:var(--white)">'
            f'<span>{len(vf)} ventas</span><span>{fmt(tv)}</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.info("Sin ventas en el per\u00edodo.")

    st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# TAB CONFIGURACIÓN
# ═════════════════════════════════════════════════════════════
with tab_cfg:
    st.markdown("<div style='padding:20px'>", unsafe_allow_html=True)
    cc1, cc2 = st.columns(2, gap="large")

    with cc1:
        st.markdown('<div class="d-sep">Datos del Local</div>', unsafe_allow_html=True)
        nl = st.text_input("Nombre del local",  db.get_config('nombre_local'))
        dl = st.text_input("Direcci\u00f3n",    db.get_config('direccion_local'))
        tl = st.text_input("Tel\u00e9fono",     db.get_config('telefono_local'))
        at = st.selectbox("Ancho ticket (mm)", [80, 58],
                          index=0 if db.get_config('ancho_ticket_mm') == '80' else 1)
        if st.button("Guardar Datos del Local", use_container_width=True, type="primary", key="btn_sl"):
            db.set_config('nombre_local', nl)
            db.set_config('direccion_local', dl)
            db.set_config('telefono_local', tl)
            db.set_config('ancho_ticket_mm', str(at))
            st.success("Guardado.")

        st.markdown('<div class="d-sep" style="margin-top:20px">Agregar Producto</div>', unsafe_allow_html=True)
        np_n = st.text_input("Nombre del producto", key="np_n")
        npa, npb = st.columns(2)
        with npa:
            np_p = st.number_input("Precio ($)", min_value=0.0, step=100.0, key="np_p")
        with npb:
            np_c = st.selectbox("Categor\u00eda", ['cafe','comida','bebida'], key="np_c")
        np_g = st.number_input("Gramos de caf\u00e9 por unidad", min_value=0.0, max_value=50.0, value=18.0, step=1.0, key="np_g")
        if st.button("Agregar Producto", use_container_width=True, type="primary", key="btn_ap"):
            if np_n.strip():
                db.agregar_producto(np_n.strip(), np_p, np_c, np_g)
                st.success(f"{np_n} agregado."); st.rerun()
            else:
                st.warning("Ingres\u00e1 el nombre.")

    with cc2:
        st.markdown('<div class="d-sep">Editar Productos</div>', unsafe_allow_html=True)
        todos = db.get_todos_productos()
        for prod in todos:
            ico = "\u25cf" if prod['activo'] else "\u25cb"
            with st.expander(f"{ico}  {prod['nombre']}  \u2014  {fmt(prod['precio'])}"):
                ea, eb = st.columns(2)
                with ea:
                    en = st.text_input("Nombre", prod['nombre'], key=f"en_{prod['id']}")
                    ep = st.number_input("Precio", prod['precio'], step=100.0, key=f"ep_{prod['id']}")
                with eb:
                    cl = ['cafe','comida','bebida']
                    ec = st.selectbox("Categor\u00eda", cl,
                                      index=cl.index(prod['categoria']) if prod['categoria'] in cl else 0,
                                      key=f"ec_{prod['id']}")
                    eg = st.number_input("Gramos caf\u00e9", prod['cafe_molido_g'], step=1.0, key=f"eg_{prod['id']}")
                ea2 = st.checkbox("Activo (visible en POS)", bool(prod['activo']), key=f"ea_{prod['id']}")
                if st.button("Guardar", key=f"es_{prod['id']}", use_container_width=True, type="primary"):
                    db.actualizar_producto(prod['id'], en, ep, ec, eg, int(ea2))
                    st.success(f"{en} actualizado."); st.rerun()

    st.markdown('<div class="d-sep" style="margin-top:20px">Sistema</div>', unsafe_allow_html=True)
    si1, si2 = st.columns(2)
    with si1:
        st.info(f"Base de datos: `{db.DB_PATH}`")
        st.info(f"Pr\u00f3ximo ticket: `#{db.get_config('ticket_counter')}`")
    with si2:
        sd = db.get_stock()
        cr = next((s for s in sd if 'Caf' in s['insumo']), None)
        if cr:
            st.info(f"Caf\u00e9 molido: `{cr['cantidad_actual']:.0f}g` (~{int(cr['cantidad_actual']/18)} caf\u00e9s)")

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    '<div class="pc-footer">'
    '<span>Sistema punto caf\u00e9 OS</span>'
    '<span>v1.0.0</span>'
    '</div>', unsafe_allow_html=True
)
