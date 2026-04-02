import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Configuración de la página y Estilo
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- DISEÑO HERMOSO (CSS MODERNO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .business-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 8px solid #007bff;
    }
    h1 { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .stButton>button { border-radius: 20px; font-weight: bold; transition: 0.3s; width: 100%; }
    .share-button>button { 
        background-color: #25d366 !important; 
        color: white !important; 
        border: none !important;
    }
    .stImage > img { border-radius: 15px; object-fit: cover; border: 2px solid #e2e8f0; }
    .footer-container {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px 20px 0 0;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.05);
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('guia_santa_teresa.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comercios 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, categoria TEXT, 
                  ubicacion TEXT, foto_url TEXT, reseña_willian TEXT, estrellas_w INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS opiniones 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, comercio_id INTEGER, usuario TEXT, 
                  comentario TEXT, estrellas_u INTEGER, fecha TEXT)''')
    conn.commit()
    return conn

def precargar_datos(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM comercios")
    if c.fetchone()[0] == 0:
        comercios_iniciales = [
            ("Panadería El Samán", "Comercios de viveres", "Casco Central", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500", "El mejor pan de sal de la zona, siempre calientito.", 5),
            ("Pizzería La Nonna", "comidas rapidas", "Sector El Rincón", "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500", "Pizzas a la leña con sabor auténtico.", 4),
            ("Farmacia Santa Teresa", "farmacias", "Av. Ayacucho", "https://images.unsplash.com/photo-1586015555751-63bb00993e2c?w=500", "Atención rápida y gran variedad de medicinas.", 5),
            ("Ferretería El Tuy", "ferreteria", "Las Flores", "https://images.unsplash.com/photo-1581141849291-1125c7b692b5?w=500", "Tienen de todo para la construcción.", 4),
            ("Inversiones El Momoy", "Comercios de viveres", "Valles del Tuy", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500", "Charcutería fresca y buenos precios.", 5),
            ("Electro-Ventas Will", "electrodomesticos", "Casco Central", "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=500", "Calidad en equipos para el hogar.", 4),
            ("Taxi Express Santa Teresa", "taxi", "Terminal de Pasajeros", "https://images.unsplash.com/photo-1549194388-2469d59ec69c?w=500", "Seguridad y puntualidad garantizada.", 5),
            ("Óptica Mirada Clara", "salud", "C.C. El Tuy", "https://images.unsplash.com/photo-1511499767390-a73359580bc8?w=500", "Exámenes de la vista gratuitos por temporada.", 4),
            ("Súper Fibra Almenar", "servicios de fibra optica", "Urbanización Independencia", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=500", "El internet más estable de Santa Teresa.", 5),
            ("Burguer Rey", "comidas rapidas", "Plaza Bolívar", "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500", "Hamburguesas gigantes con mucha sazón.", 4),
            ("Clínica El Tuy", "salud", "Av. Principal", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=500", "Emergencias 24 horas.", 4),
            ("Abasto Los Hermanos", "Comercios de viveres", "Sector Paraíso", "https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=500", "Buenos combos de comida.", 3),
            ("Heladería Boconó", "diversion y paseos", "Casco Central", "https://images.unsplash.com/photo-1501443762994-82bd5dabb892?w=500", "Sabores artesanales que encantan.", 5),
            ("Repuestos Miranda", "servicios", "Zona Industrial", "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=500", "Repuestos originales para todas las marcas.", 4),
            ("Salón de Belleza Estilo", "servicios", "C.C. Paseo Tuy", "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=500", "Cortes modernos y tintes de calidad.", 5),
            ("Gimnasio Iron Body", "salud", "Calle El Sol", "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500", "Máquinas nuevas y buen ambiente.", 4),
            ("Centro de Copiado Rapid", "servicios", "Frente a la Alcaldía", "https://images.unsplash.com/photo-1564419320461-6870880221ad?w=500", "Impresiones nítidas y anillados.", 4),
            ("Carnicería La Finca", "Comercios de viveres", "Mercado Municipal", "https://images.unsplash.com/photo-1607623814075-e512199b4515?w=500", "Cortes premium de primera.", 5),
            ("Reparaciones El Mago", "servicios", "Sector La Esperanza", "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=500", "Arreglan cualquier equipo electrónico.", 4),
            ("Pollos El Canario", "comidas rapidas", "Entrada del Pueblo", "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500", "Pollo asado con hallaquitas divinas.", 5)
        ]
        c.executemany("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", comercios_iniciales)
        conn.commit()

conn = init_db()
precargar_datos(conn)

# --- PANEL ADMIN (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.title("🔐 Acceso Admin")
admin_pass = st.sidebar.text_input("Contraseña", type="password")

if admin_pass == "Juan*316*":
    st.sidebar.success("Bienvenido Willian")
    menu_admin = st.sidebar.radio("Acción:", ["Añadir Nuevo", "Modificar / Editar", "Eliminar"])
    
    if menu_admin == "Añadir Nuevo":
        with st.sidebar.expander("📝 Nuevo Registro", expanded=True):
            ad_nom = st.text_input("Nombre")
            ad_cat = st.selectbox("Categoría", ["Comercios de viveres", "comidas rapidas", "diversion y paseos", "salud", "servicios", "taxi", "farmacias", "ferreteria", "electrodomesticos", "servicios de fibra optica"])
            ad_ub = st.text_input("Ubicación")
            ad_url = st.text_input("URL Foto")
            ad_res = st.text_area("Reseña")
            ad_est = st.slider("Estrellas", 1, 5, 5)
            if st.button("Guardar"):
                c = conn.cursor()
                c.execute("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES (?,?,?,?,?,?)", (ad_nom, ad_cat, ad_ub, ad_url, ad_res, ad_est))
                conn.commit()
                st.rerun()

    elif menu_admin == "Modificar / Editar":
        df_edit = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_edit.empty:
            sel_edit = st.sidebar.selectbox("Elegir para editar:", df_edit['nombre'].tolist())
            datos_neg = df_edit[df_edit['nombre'] == sel_edit].iloc[0]
            with st.sidebar.expander("✏️ Editar Datos", expanded=True):
                ed_nom = st.text_input("Nombre", value=datos_neg['nombre'])
                ed_ub = st.text_input("Ubicación", value=datos_neg['ubicacion'])
                ed_url = st.text_input("URL Foto", value=datos_neg['foto_url'])
                ed_res = st.text_area("Reseña", value=datos_neg['reseña_willian'])
                ed_est = st.slider("Estrellas", 1, 5, int(datos_neg['estrellas_w']))
                if st.button("Actualizar"):
                    c = conn.cursor()
                    c.execute("UPDATE comercios SET nombre=?, ubicacion=?, foto_url=?, reseña_willian=?, estrellas_w=? WHERE id=?", (ed_nom, ed_ub, ed_url, ed_res, ed_est, datos_neg['id']))
                    conn.commit()
                    st.rerun()
    
    elif menu_admin == "Eliminar":
        df_del = pd.read_sql_query("SELECT * FROM comercios", conn)
        if not df_del.empty:
            sel_del = st.sidebar.selectbox("Elegir para borrar:", df_del['nombre'].tolist())
            if st.sidebar.button("SÍ, ELIMINAR"):
                c = conn.cursor()
                c.execute("DELETE FROM comercios WHERE nombre=?", (sel_del,))
                conn.commit()
                st.rerun()

# --- CUERPO PRINCIPAL ---
col_logo, col_share = st.columns([4, 1])

with col_logo:
    st.title("🚀 Guía Comercial Almenar")
    st.markdown("#### *Santa Teresa del Tuy en la palma de tu mano*")

with col_share:
    # URL ACTUALIZADA PARA EL NUEVO REPOSITORIO
    url_publica = "https://guia-comercial-almenar.streamlit.app"
    compartir_js = f"""
        <script>
        function compartirApp() {{
            const shareData = {{
                title: 'Guía Comercial Almenar',
                text: 'Mira los mejores comercios de Santa Teresa del Tuy aquí:',
                url: '{url_publica}'
            }};
            if (navigator.share) {{
                navigator.share(shareData).catch(console.error);
            }} else {{
                navigator.clipboard.writeText('{url_publica}');
                alert("Enlace copiado al portapapeles: {url_publica}");
            }}
        }}
        </script>
        <div class="share-button">
            <button onclick="compartirApp()" style="cursor:pointer; padding:10px; border-radius:20px; width:100%; font-weight:bold; background-color:#25d366; color:white; border:none;">
                📲 Compartir Guía
            </button>
        </div>
    """
    st.components.v1.html(compartir_js, height=60)

tab_explorar, tab_opinar = st.tabs(["🔍 Explorador", "✍️ Opinar"])

with tab_explorar:
    df_negocios = pd.read_sql_query("SELECT * FROM comercios", conn)
    if not df_negocios.empty:
        busqueda = st.text_input("🔍 ¿Qué buscas hoy?", placeholder="Escribe el nombre o categoría...", key="main_search")
        filtered = df_negocios[df_negocios['nombre'].str.contains(busqueda, case=False) | df_negocios['categoria'].str.contains(busqueda, case=False)]
        negocio_sel = st.selectbox("Resultados encontrados:", ["Seleccionar un comercio..."] + filtered['nombre'].tolist())
        
        if negocio_sel != "Seleccionar un comercio...":
            row = df_negocios[df_negocios['nombre'] == negocio_sel].iloc[0]
            st.divider()
            col_titulo, col_voto = st.columns([3, 1])
            with col_titulo:
                st.header(f"🏢 {row['nombre']}")
                st.subheader(f"📍 {row['ubicacion']}")
            with col_voto:
                st.markdown(f"### {'⭐' * int(row['estrellas_w'])}")
                st.caption("Calificación Willian")

            col_img, col_info = st.columns([1, 1])
            with col_img:
                st.image(row['foto_url'], use_container_width=True, caption=row['nombre'])
            with col_info:
                st.markdown("### 📝 Reseña del Autor")
                st.info(row['reseña_willian'])
                maps_url = f"https://www.google.com/maps/search/{row['nombre'].replace(' ', '+')}+{row['ubicacion'].replace(' ', '+')}"
                st.link_button("📍 Ver en Google Maps", maps_url)

            st.divider()
            st.subheader("💬 Lo que dicen los usuarios")
            ops_df = pd.read_sql_query(f"SELECT * FROM opiniones WHERE comercio_id = {row['id']}", conn)
            if not ops_df.empty:
                for _, op in ops_df.iterrows():
                    st.markdown(f"**{op['usuario']}** - {'⭐'*op['estrellas_u']}")
                    st.write(op['comentario'])
                    st.caption(f"Publicado el: {op['fecha']}")
                    st.markdown("---")
            else:
                st.write("Aún no hay opiniones de usuarios.")
    else:
        st.info("No hay datos.")

with tab_opinar:
    st.header("✍️ Deja tu testimonio")
    if not df_negocios.empty:
        neg_op = st.selectbox("¿A qué comercio fuiste?", df_negocios['nombre'].tolist())
        usr_nom = st.text_input("Tu Nombre")
        usr_est = st.select_slider("¿Cómo calificarías tu experiencia?", options=[1,2,3,4,5], value=5)
        usr_com = st.text_area("Cuéntanos más...")
        if st.button("Publicar Opinión"):
            id_neg = int(df_negocios[df_negocios['nombre'] == neg_op].iloc[0]['id'])
            fecha = datetime.now().strftime("%d/%m/%Y")
            c = conn.cursor()
            c.execute("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (?,?,?,?,?)", (id_neg, usr_nom, usr_com, usr_est, fecha))
            conn.commit()
            st.success("¡Gracias por compartir!")
            st.rerun()

# --- FOOTER ---
st.markdown(f"""
<div class='footer-container'>
    <div style='text-align: center;'>
        <p style='font-size: 1.2em;'><b>Reflexiones de Willian Almenar</b></p>
        <p>® Marca Registrada - Santa Teresa del Tuy</p>
        <p>Esta plataforma y su contenido es propiedad exclusiva de <b>Willian Almenar</b>.</p>
        <p><small>© {datetime.now().year} Todos los derechos reservados.</small></p>
    </div>
</div>
""", unsafe_allow_html=True)
