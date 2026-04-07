import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageFile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- ESTILO VENEZUELA (ARCO, LETRAS NEGRAS Y SEGURIDAD TOTAL) ---
st.markdown("""
    <style>
    /* OCULTAMIENTO TOTAL DE INTERFAZ DE STREAMLIT (GESTIÓN Y HERRAMIENTAS) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    .stAppToolbar {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    
    /* ELIMINAR BOTÓN 'MANAGE APP' Y MARCOS FLOTANTES */
    button[title="Manage app"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    #styled-link-icon {display: none !important;}
    
    /* Fondo general */
    .stApp { background-color: #111827; color: #ffffff; }
    
    /* Panel lateral */
    [data-testid="stSidebar"] { background-color: #1f2937; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: bold;
    }

    /* Encabezado Tricolor en forma de ARCO */
    .venezuela-header {
        text-align: center;
        padding: 60px 10px 40px 10px;
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
    }
    .stars-arc { 
        color: white; 
        font-size: 2.5em; 
        letter-spacing: 15px; 
        font-weight: bold; 
        text-shadow: 3px 3px 6px #000;
        margin-top: -15px;
    }
    
    /* RECUADROS DE TEXTO: Letras Negras sobre Fondo Blanco */
    input, textarea, [data-baseweb="select"] { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important;
    }
    
    .stTextInput input, .stTextArea textarea {
        color: #000000 !important;
    }

    .share-link-box {
        background-color: #1f2937;
        border: 2px dashed #3b82f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }

    .footer-willian { background: #000; color: #fff; padding: 30px; text-align: center; border-top: 4px solid #ffcc00; margin-top: 50px; }
    
    /* Estilo para los comentarios */
    .comment-box {
        background-color: #374151;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        border-left: 5px solid #ffcc00;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS comercios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, comentario TEXT, estrellas_u INTEGER, fecha TEXT)')
# Tabla para ajustes de la app (Logo)
c.execute('CREATE TABLE IF NOT EXISTS ajustes (id INTEGER PRIMARY KEY, logo_url TEXT)')
conn.commit()

# --- CARGA DE DATOS REALES ---
c.execute("SELECT COUNT(*) FROM comercios")
if c.fetchone()[0] == 0:
    comercios_iniciales = [
        ("Farmatodo", "Farmacias", "Av. Ayacucho", "https://images.unsplash.com/photo-1587854692152-cbe660fe0870?q=80&w=600", "Excelente atención y variedad.", 5),
        ("Supermercado Unicasa", "Supermercados", "C.C. Paseo Tuy", "https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=600", "Productos frescos y buena ubicación.", 5),
        ("Panadería La Mansión del Tuy", "Otros", "Casco Central", "https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=600", "El mejor pan de la zona.", 5),
        ("Ferretería El Águila", "Ferreterias", "Sector El Rincón", "https://images.unsplash.com/photo-1581244276891-8bb499b0f918?q=80&w=600", "Todo para la construcción.", 5),
        ("Clínica Pasqualini", "Salud", "Calle Falcón", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?q=80&w=600", "Atención médica especializada.", 5),
        ("Farmacia Saas", "Farmacias", "Av. Bolívar", "https://images.unsplash.com/photo-1576602976047-174e57a47881?q=80&w=600", "Medicamentos garantizados.", 5),
        ("Supermercado Hiper Líder", "Supermercados", "Carretera Nacional", "https://images.unsplash.com/photo-1604719312563-8912e93d5c33?q=80&w=600", "Precios competitivos.", 5),
        ("Pollo a la Broaster Santa Teresa", "Otros", "Cerca de la Plaza Bolívar", "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?q=80&w=600", "Sabor tradicional.", 5),
        ("Ferretería El Constructor", "Ferreterias", "Sector Las Flores", "https://images.unsplash.com/photo-1530124560676-41bc1275d813?q=80&w=600", "Herramientas de calidad.", 5),
        ("Centro Médico Tuy", "Salud", "Urb. Independencia", "https://images.unsplash.com/photo-1516549655169-df83a0774514?q=80&w=600", "Servicio de emergencias 24h.", 5),
        ("Repuestos El Catire", "Otros", "Av. Principal", "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?q=80&w=600", "Especialistas en frenos y tren delantero.", 5),
        ("Librería El Estudiante", "Otros", "Calle Comercio", "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?q=80&w=600", "Artículos de oficina y escolares.", 5),
        ("Zapatería La Bota de Oro", "Otros", "Casco Central", "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600", "Calzado nacional e importado.", 5),
        ("Inversiones Nassif", "Otros", "Zona Industrial", "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=600", "Distribución de alimentos.", 5),
        ("Bodegón El Canario", "Otros", "Calle Ayacucho", "https://images.unsplash.com/photo-1534527489986-3e33beae29aa?q=80&w=600", "Bebidas y snacks nacionales.", 5),
        ("Óptica Santa Teresa", "Salud", "C.C. El Recreo", "https://images.unsplash.com/photo-1511499767390-90342f16b20a?q=80&w=600", "Examen visual y monturas.", 5),
        ("Carnicería La Ternera", "Supermercados", "Sector Mameyal", "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?q=80&w=600", "Carnes de primera.", 5),
        ("Taller Mecánico El Chamo", "Otros", "Entrada a Santa Teresa", "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?q=80&w=600", "Mecánica general.", 5),
        ("Peluquería Estilo y Clase", "Otros", "Casco Central", "https://images.unsplash.com/photo-1560066984-138dadb4c035?q=80&w=600", "Cortes y tintes modernos.", 5),
        ("Agencia de Loterías La Suerte", "Otros", "Frente a la Plaza", "https://images.unsplash.com/photo-1518133295144-c79ac1976030?q=80&w=600", "Prueba tu suerte diariamente.", 5)
    ]
    for nom, cat, ubi, img, res, est in comercios_iniciales:
        c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", 
                  (nom, cat, ubi, img, res, est))
    conn.commit()

# --- VERIFICACIÓN DE AJUSTES (LOGO) ---
c.execute("SELECT COUNT(*) FROM ajustes")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO ajustes (id, logo_url) VALUES (1, 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png')")
    conn.commit()

# --- PANEL ADMIN CON CLAVE ÚNICA ---
st.sidebar.title("🛠️ Administración")
admin_pass = st.sidebar.text_input("Clave de Acceso", type="password")

if admin_pass == "Juan*316*":
    st.sidebar.success("Acceso Concedido")
    menu = st.sidebar.radio("Acción:", ["Ver/Buscar", "Añadir", "Modificar", "Borrar", "Ajustes Logo"])
    
    if menu == "Ajustes Logo":
        st.sidebar.subheader("Actualizar Logo Principal")
        logo_file = st.sidebar.file_uploader("Subir foto del logo", type=['png', 'jpg', 'jpeg'])
        logo_url_manual = st.sidebar.text_input("O pega URL del logo")
        if st.sidebar.button("Guardar Logo"):
            final_logo = logo_url_manual if logo_url_manual else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            c.execute("UPDATE ajustes SET logo_url=? WHERE id=1", (final_logo,))
            conn.commit()
            st.sidebar.success("Logo actualizado")
            st.rerun()

    elif menu == "Añadir":
        with st.sidebar.form("add_form"):
            n = st.text_input("Nombre del Negocio")
            cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermercados", "Ferreterias", "Otros"])
            ub = st.text_input("Ubicación")
            url_img = st.text_input("URL de la Foto (Link)", placeholder="https://ejemplo.com/foto.jpg")
            res = st.text_area("Reseña")
            est = st.slider("Estrellas", 1, 5, 5)
            if st.form_submit_button("Guardar Negocio"):
                final_img = url_img if url_img else "https://via.placeholder.com/600x300?text=Negocio+en+Santa+Teresa"
                c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (n, cat, ub, final_img, res, est))
                conn.commit()
                st.sidebar.success("¡Guardado!")
                st.rerun()

    elif menu == "Modificar":
        df_mod = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_mod.empty:
            target = st.sidebar.selectbox("Elegir Negocio para Editar", df_mod['nombre'].tolist())
            row = df_mod[df_mod['nombre'] == target].iloc[0]
            with st.sidebar.form("edit_form"):
                new_n = st.text_input("Nombre", value=row['nombre'])
                new_res = st.text_area("Reseña", value=row['reseña_willian'])
                new_img = st.text_input("Nueva URL de Foto", value=row['foto_url'])
                if st.form_submit_button("Actualizar"):
                    c.execute("UPDATE comercios SET nombre=?, reseña_willian=?, foto_url=? WHERE id=?", (new_n, new_res, new_img, int(row['id'])))
                    conn.commit()
                    st.sidebar.success("¡Actualizado!")
                    st.rerun()

    elif menu == "Borrar":
        df_del = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_del.empty:
            target_del = st.sidebar.selectbox("Negocio a ELIMINAR", df_del['nombre'].tolist())
            if st.sidebar.button("⚠️ ELIMINAR DEFINITIVAMENTE"):
                c.execute("DELETE FROM comercios WHERE nombre=?", (target_del,))
                conn.commit()
                st.sidebar.error(f"{target_del} eliminado.")
                st.rerun()
elif admin_pass != "":
    st.sidebar.error("Clave Incorrecta")

# --- CUERPO PRINCIPAL ---
c.execute("SELECT logo_url FROM ajustes WHERE id=1")
result = c.fetchone()
current_logo = result[0] if result else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)

col_logo_1, col_logo_2, col_logo_3 = st.columns([2,1,2])
with col_logo_2:
    st.image(current_logo, width=150)

st.title("🚀 Guía Comercial Almenar")
st.write("#### Santa Teresa del Tuy: Información confiable para nuestra gente")

# --- SECCIÓN PARA COMPARTIR ---
link_app = "https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app"
whatsapp_url = f"https://api.whatsapp.com/send?text=¡Mira la Guía Comercial de Santa Teresa! 🚀 Accede aquí: {link_app}"

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.1em;">📲 Compartir por WhatsApp</div></a>', unsafe_allow_html=True)
with col_s2:
    st.markdown(f'<div class="share-link-box"><small>🔗 Enlace Directo:</small><br><b style="color:#ffcc00;">{link_app}</b></div>', unsafe_allow_html=True)

# --- BUSCADOR Y MOSTRADOR EN TIEMPO REAL ---
busq = st.text_input("🔍 ¿Qué buscas hoy?", placeholder="Ej: Farmacia, Repuestos...")
df = pd.read_sql_query("SELECT * FROM comercios", conn)

if not df.empty:
    filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
    for _, r in filtrado.iterrows():
        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(r['foto_url'], use_container_width=True)
                st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                st.write(f"⭐ **Calificación:** {'⭐' * r['estrellas_w']}")
                st.info(f"**Reseña:** {r['reseña_willian']}")
            
            with col2:
                st.subheader("💬 Opiniones de la comunidad")
                
                with st.form(key=f"form_op_{r['id']}"):
                    user = st.text_input("Tu Nombre", key=f"user_{r['id']}")
                    comm = st.text_area("¿Qué te pareció?", key=f"comm_{r['id']}")
                    stars_u = st.slider("Tu calificación", 1, 5, 5, key=f"stars_{r['id']}")
                    if st.form_submit_button("Publicar Opinión"):
                        if user and comm:
                            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                            c.execute("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (?,?,?,?,?)", 
                                      (int(r['id']), user, comm, stars_u, fecha_hoy))
                            conn.commit()
                            st.success("¡Gracias por tu opinión!")
                            st.rerun()
                        else:
                            st.warning("Por favor escribe tu nombre y un comentario.")

                ops = pd.read_sql_query(f"SELECT * FROM opiniones WHERE comercio_id={int(r['id'])} ORDER BY id DESC", conn)
                if not ops.empty:
                    for _, op in ops.iterrows():
                        st.markdown(f"""
                        <div class="comment-box">
                            <b>👤 {op['usuario']}</b> <small>({op['fecha']})</small><br>
                            {'⭐' * op['estrellas_u']}<br>
                            {op['comentario']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("Sé el primero en opinar sobre este negocio.")

# --- PIE DE PÁGINA ACTUALIZADO ---
st.markdown(f"<div class='footer-willian'>📍 Santa Teresa del Tuy, Venezuela.<br>© {datetime.now().year} - Esta App fue creada y diseñada por Willian Almenar, Todos los derechos reservados, prohibida la reproduccion parcial o total. Santa Teresa del Tuy 2026</div>", unsafe_allow_html=True)
