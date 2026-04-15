import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from PIL import Image, ImageFile
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- CONEXIÓN A NEON (POSTGRESQL) ---
# Usamos Neon para que tus datos no se borren al cerrar la app
conn = st.connection("postgresql", type="sql")

# --- CREACIÓN DE TABLAS ---
with conn.session as s:
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS comercios (
            id SERIAL PRIMARY KEY, 
            nombre VARCHAR(255), 
            categoria VARCHAR(100), 
            ubicacion TEXT, 
            foto_url TEXT, 
            reseña_willian TEXT, 
            estrellas_w INTEGER, 
            maps_url TEXT
        )
    """))
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS opiniones (
            id SERIAL PRIMARY KEY, 
            comercio_id INTEGER, 
            usuario VARCHAR(100), 
            comentario TEXT, 
            estrellas_u INTEGER, 
            fecha VARCHAR(50)
        )
    """))
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY,
            conteo INTEGER
        )
    """))
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS denuncias (
            id SERIAL PRIMARY KEY,
            denunciante VARCHAR(255),
            comercio_afectado VARCHAR(255),
            motivo TEXT,
            fecha VARCHAR(50),
            estatus VARCHAR(50) DEFAULT 'Pendiente'
        )
    """))
    res_v = s.execute(text("SELECT conteo FROM visitas WHERE id = 1")).fetchone()
    if not res_v:
        s.execute(text("INSERT INTO visitas (id, conteo) VALUES (1, 0)"))
    s.commit()

# --- LÓGICA DE VISITAS ---
if 'visitado' not in st.session_state:
    with conn.session as s:
        s.execute(text("UPDATE visitas SET conteo = conteo + 1 WHERE id = 1"))
        s.commit()
    st.session_state.visitado = True

res_visitas = conn.query("SELECT conteo FROM visitas WHERE id = 1", ttl=0)
total_visitas = res_visitas.iloc[0,0] if not res_visitas.empty else 0

def imagen_a_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return f"data:image/png;base64,{base64.b64encode(bytes_data).decode()}"
    return None

# --- ESTILO VENEZUELA (ESCUDO ANTIGITHUB + ARCO PROFESIONAL) ---
st.markdown("""
    <style>
    /* 1. ELIMINACIÓN TOTAL DE MENÚS Y BOTONES TÉCNICOS */
    #MainMenu {display: none !important;}
    footer {display: none !important;}
    .stDeployButton {display: none !important;}
    header {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* 2. FONDO Y PANEL LATERAL */
    .stApp { background-color: #111827; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1f2937; border-right: 2px solid #ffcc00; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #ffffff !important; font-weight: bold; }

    /* 3. ENCABEZADO TRICOLOR EN FORMA DE ARCO */
    .venezuela-header {
        text-align: center;
        padding: 60px 10px 40px 10px;
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        border-radius: 100% 100% 25px 25px / 120% 120% 25px 25px;
        margin-bottom: 30px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.6);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stars-arc { 
        color: white; 
        font-size: 2.5em; 
        letter-spacing: 15px; 
        font-weight: bold; 
        text-shadow: 3px 3px 6px #000; 
        margin-top: -15px;
    }

    /* 4. RECUADROS DE ENTRADA (Fondo Blanco, Letra Negra) */
    input, textarea, [data-baseweb="select"] { 
        background-color: #ffffff !important; 
        color: #000000 !important;
        font-weight: bold !important;
    }
    .stTextInput input, .stTextArea textarea { color: #000000 !important; }

    /* 5. PANELES DE ESTADÍSTICAS Y COMPARTIR */
    .stats-panel {
        background: rgba(31, 41, 55, 0.8);
        padding: 15px;
        border-radius: 20px;
        border: 2px solid #ffcc00;
        text-align: center;
        margin-bottom: 20px;
    }
    .share-link-box {
        background-color: #1f2937;
        border: 2px dashed #3b82f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }

    .footer-willian { 
        background: #000; 
        padding: 30px; 
        text-align: center; 
        border-top: 4px solid #ffcc00; 
        margin-top: 50px; 
    }
    
    /* ESTILO PARA EL PANEL DE CONTROL MAESTRO */
    .master-panel {
        background-color: #0033a0;
        border: 3px solid #ffcc00;
        padding: 20px;
        border-radius: 15px;
        margin-top: 40px;
    }

    /* ESTILO PLACA DE BRONCE */
    .bronze-plaque {
        background: linear-gradient(145deg, #8c6a31, #5d431a);
        border: 4px solid #d4af37;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: inset 2px 2px 5px rgba(255,255,255,0.2), 5px 5px 15px rgba(0,0,0,0.5);
        margin: 40px auto;
        max-width: 800px;
    }
    .bronze-text {
        color: #ffd700;
        font-family: 'Times New Roman', serif;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        letter-spacing: 1px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA ---
def precargar_datos():
    res = conn.query("SELECT count(*) FROM comercios", ttl=0)
    if res.iloc[0,0] == 0:
        with conn.session as s:
            s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w) VALUES ('Panadería El Gran Paseo', 'Otros', 'Av. Ayacucho', 'https://via.placeholder.com/400', 'Tradición tereseña.', 5)"))
            s.commit()

precargar_datos()

# --- PANEL LATERAL ---
with st.sidebar:
    st.title("🇻🇪 Gestión")
    opcion_menu = st.radio("Ir a:", ["🏢 Ver Guía Comercial", "🔐 Administración", "📢 Página de Denuncias"])
    st.markdown("---")
    st.info("Desarrollado por Willian Almenar")

# --- ENCABEZADO ---
st.markdown('<div class="venezuela-header"><div class="stars-arc">★ ★ ★ ★ ★ ★ ★ ★</div></div>', unsafe_allow_html=True)

# --- RELOJ Y VISITAS ---
ahora_vzla = datetime.utcnow() - timedelta(hours=4)
st.markdown(f'''
    <div class="stats-panel">
        <b style="color:#ffcc00;">{ahora_vzla.strftime("%d/%m/%Y")} | {ahora_vzla.strftime("%I:%M %p")}</b><br>
        <span style="font-size:1.2em;">🚀 VISITAS TOTALES: {total_visitas}</span>
    </div>
''', unsafe_allow_html=True)

# --- LÓGICA DE MENÚ ---

# 1. ADMINISTRACIÓN
if opcion_menu == "🔐 Administración":
    clave = st.text_input("Clave de Acceso:", type="password")
    if clave == "Juan*316*":
        st.success("Acceso Maestro Concedido")
        tab1, tab2 = st.tabs(["🏢 Añadir Negocio", "🖼️ Logo"])
        with tab1:
            with st.form("admin_form"):
                n = st.text_input("Nombre del Negocio")
                cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"])
                ub = st.text_input("Ubicación")
                res = st.text_area("Tu Reseña")
                est = st.slider("Estrellas", 1, 5, 5)
                if st.form_submit_button("Guardar en la Base de Datos"):
                    with conn.session as s:
                        s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, reseña_willian, estrellas_w) VALUES (:n, :c, :u, :r, :e)"),
                                    {"n": n, "c": cat, "u": ub, "r": res, "e": est})
                        s.commit()
                    st.success("¡Guardado correctamente!")
        with tab2:
            st.write("Mantenimiento de Imagen")

# 2. DENUNCIAS
elif opcion_menu == "📢 Página de Denuncias":
    st.markdown("## 📢 Centro de Denuncias Ciudadanas")
    with st.form("denuncia_form"):
        com = st.text_input("Comercio afectado")
        mot = st.text_area("Motivo de la denuncia")
        if st.form_submit_button("Enviar Reporte"):
            with conn.session as s:
                s.execute(text("INSERT INTO denuncias (denunciante, comercio_afectado, motivo, fecha) VALUES ('Anónimo', :c, :m, :f)"),
                            {"c": com, "m": mot, "f": ahora_vzla.strftime("%d/%m/%Y")})
                s.commit()
            st.success("Denuncia recibida por Willian Almenar.")

# 3. VER GUÍA (PÚBLICO)
elif opcion_menu == "🏢 Ver Guía Comercial":
    st.title("🚀 Guía Comercial Almenar")
    st.write("#### Santa Teresa del Tuy: Información confiable para nuestra gente")

    # Sistema de compartir
    link_app = "https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app"
    whatsapp_url = f"https://api.whatsapp.com/send?text=¡Mira la Guía Comercial de Santa Teresa! 🚀 {link_app}"
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25d366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">📲 Compartir por WhatsApp</div></a>', unsafe_allow_html=True)
    with col_s2:
        st.markdown(f'<div class="share-link-box"><small>🔗 Enlace Directo:</small><br><b style="color:#ffcc00;">{link_app}</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    busq = st.text_input("🔍 ¿Qué buscas en Santa Teresa?", placeholder="Ej: Panadería, Farmacia...")
    
    df = conn.query("SELECT * FROM comercios", ttl=0)
    if not df.empty:
        filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
        for _, r in filtrado.iterrows():
            with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
                if r['foto_url']:
                    st.image(r['foto_url'], width=300)
                st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                st.write(f"⭐ **Calificación:** {'⭐' * (r['estrellas_w'] if r['estrellas_w'] else 0)}")
                st.info(f"**Reseña de Willian:** {r['reseña_willian']}")
                
                # Sección de Opiniones de Usuarios
                st.markdown("---")
                st.write("💬 **Opiniones de Usuarios:**")
                op_df = conn.query(f"SELECT * FROM opiniones WHERE comercio_id = {r['id']}", ttl=0)
                if not op_df.empty:
                    for _, op in op_df.iterrows():
                        st.write(f"👤 **{op['usuario']}**: {op['comentario']} ({'⭐'*op['estrellas_u']})")
                else:
                    st.write("Sé el primero en opinar.")

# --- AGREGADO: PANEL DE ADMINISTRADOR MAESTRO MEJORADO ---
st.markdown("---")
with st.expander("🛠️ PANEL DE CONTROL MAESTRO (Acceso Restringido)"):
    master_key = st.text_input("Ingrese Contraseña Maestra para gestionar datos:", type="password", key="master_pass")
    if master_key == "Juan*316*":
        st.markdown('<div class="master-panel">', unsafe_allow_html=True)
        st.subheader("📊 GESTIÓN INTEGRAL DE LA GUÍA")
        
        m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs(["📝 Denuncias", "➕ Agregar Comercio", "⚙️ Modificar/Eliminar", "💬 Opiniones"])
        
        # TAB 1: DENUNCIAS
        with m_tab1:
            denuncias_df = conn.query("SELECT * FROM denuncias ORDER BY id DESC", ttl=0)
            if not denuncias_df.empty:
                st.dataframe(denuncias_df, use_container_width=True)
                if st.button("Limpiar historial de denuncias"):
                    with conn.session as s:
                        s.execute(text("DELETE FROM denuncias"))
                        s.commit()
                    st.rerun()
            else:
                st.write("No hay denuncias registradas.")

        # TAB 2: AGREGAR NUEVO (CON FOTO)
        with m_tab2:
            st.write("### Registrar Nuevo Comercio")
            with st.form("master_add_form"):
                add_n = st.text_input("Nombre del Negocio")
                add_cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"], key="add_cat")
                add_ub = st.text_input("Ubicación exacta")
                add_res = st.text_area("Reseña de Willian")
                add_est = st.slider("Calificación (Estrellas)", 1, 5, 5)
                add_foto = st.file_uploader("Subir Imagen del Local", type=["png", "jpg", "jpeg"])
                if st.form_submit_button("🚀 Registrar Comercio"):
                    img_data = imagen_a_base64(add_foto) if add_foto else None
                    with conn.session as s:
                        s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, reseña_willian, estrellas_w, foto_url) VALUES (:n, :c, :u, :r, :e, :f)"),
                                    {"n": add_n, "c": add_cat, "u": add_ub, "r": add_res, "e": add_est, "f": img_data})
                        s.commit()
                    st.success("Negocio añadido con éxito.")
                    st.rerun()
                
        # TAB 3: MODIFICAR / ELIMINAR
        with m_tab3:
            st.write("### Editar Información Existente")
            comercios_master = conn.query("SELECT * FROM comercios", ttl=0)
            
            if not comercios_master.empty:
                opcion_edit = st.selectbox("Seleccione Comercio para editar:", comercios_master['nombre'].tolist(), key="sel_edit")
                target = comercios_master[comercios_master['nombre'] == opcion_edit].iloc[0]
                
                with st.form("master_edit_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_n = st.text_input("Nombre", value=target['nombre'])
                        new_cat = st.selectbox("Categoría", ["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"], index=["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"].index(target['categoria']) if target['categoria'] in ["Salud", "Farmacias", "Supermerkados", "Ferreterias", "Otros"] else 0)
                        new_ub = st.text_input("Ubicación", value=target['ubicacion'])
                    with col2:
                        new_est = st.slider("Estrellas Willian", 1, 5, int(target['estrellas_w']) if target['estrellas_w'] else 5)
                        if target['foto_url']:
                             st.image(target['foto_url'], width=100, caption="Foto actual")
                        new_foto = st.file_uploader("Cambiar Foto (vacío para mantener)", type=["png", "jpg", "jpeg"])
                    
                    new_res_text = st.text_area("Reseña de Willian", value=target['reseña_willian'])
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("✅ Actualizar"):
                        final_foto = target['foto_url']
                        if new_foto:
                            final_foto = imagen_a_base64(new_foto)
                        
                        with conn.session as s:
                            s.execute(text("""
                                UPDATE comercios SET nombre=:n, categoria=:c, ubicacion=:u, 
                                reseña_willian=:r, estrellas_w=:e, foto_url=:f WHERE id=:id
                            """), {"n":new_n, "c":new_cat, "u":new_ub, "r":new_res_text, "e":new_est, "f":final_foto, "id":target['id']})
                            s.commit()
                        st.success("Actualizado correctamente.")
                        st.rerun()
                        
                    if c2.form_submit_button("🗑️ ELIMINAR COMERCIO"):
                        with conn.session as s:
                            s.execute(text("DELETE FROM comercios WHERE id=:id"), {"id":target['id']})
                            s.commit()
                        st.warning("Comercio borrado.")
                        st.rerun()
            else:
                st.write("No hay comercios registrados.")

        # TAB 4: MODERACIÓN Y EDICIÓN DE OPINIONES
        with m_tab4:
            st.write("### Control de Opiniones de Usuarios")
            todas_op = conn.query("SELECT opiniones.id, comercios.nombre as comercio, usuario, comentario, estrellas_u FROM opiniones JOIN comercios ON opiniones.comercio_id = comercios.id", ttl=0)
            if not todas_op.empty:
                sel_op_id = st.selectbox("Seleccione ID de Opinión para editar/borrar", todas_op['id'].tolist())
                op_target = todas_op[todas_op['id'] == sel_op_id].iloc[0]
                
                with st.form("edit_op_form"):
                    edit_user = st.text_input("Usuario", value=op_target['usuario'])
                    edit_comm = st.text_area("Comentario", value=op_target['comentario'])
                    edit_stars = st.slider("Estrellas Usuario", 1, 5, int(op_target['estrellas_u']))
                    
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("💾 Guardar Cambios en Opinión"):
                        with conn.session as s:
                            s.execute(text("UPDATE opiniones SET usuario=:u, comentario=:c, estrellas_u=:s WHERE id=:id"),
                                        {"u": edit_user, "c": edit_comm, "s": edit_stars, "id": sel_op_id})
                            s.commit()
                        st.success("Opinión modificada.")
                        st.rerun()
                    if b2.form_submit_button("🗑️ Borrar Opinión"):
                        with conn.session as s:
                            s.execute(text("DELETE FROM opiniones WHERE id=:id"), {"id": sel_op_id})
                            s.commit()
                        st.rerun()
                st.dataframe(todas_op, use_container_width=True)
            else:
                st.write("No hay opiniones registradas.")
            
        st.markdown('</div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown(f"""
    <div class='footer-willian'>
        📍 Santa Teresa del Tuy, Venezuela.<br>
        <b>Desarrollador Willian Almenar</b><br>
        © 2026 TODOS LOS DERECHOS RESERVADOS.
    </div>
""", unsafe_allow_html=True)

# --- PLACA DE BRONCE FINAL ---
st.markdown("""
    <div class="bronze-plaque">
        <div class="bronze-text">
            <span style="font-size: 1.4em;">Generado por Willian Almenar</span><br>
            <span style="font-size: 1em; opacity: 0.9;">Prohibida la reproducción total o parcial</span><br>
            <span style="font-size: 1.1em; letter-spacing: 3px;">DERECHOS RESERVADOS</span><br>
            <span style="font-size: 1.2em; font-variant: small-caps;">Santa Teresa del Tuy 2.026</span>
        </div>
    </div>
""", unsafe_allow_html=True)
