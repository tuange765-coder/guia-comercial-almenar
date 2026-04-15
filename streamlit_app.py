import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from PIL import Image, ImageFile
import base64

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Guía Comercial Almenar", layout="wide", page_icon="🚀")

# --- CONEXIÓN A NEON (POSTGRESQL) ---
conn = st.connection("postgresql", type="sql")

# --- CATEGORÍAS DEFINIDAS ---
CAT_LIST = [
    "Salud", "Laboratorios", "Opticas", "Farmacias", "Dulcerias", 
    "Comida Rapida", "Panaderias", "Charcuterias", "Carnicerias", 
    "Ferreterias", "Zapaterias", "Electrodomesticos", "Fibras Opticas", 
    "Taxis", "Mototaxis", "Servicios", "Entes Publicos", "Otros"
]

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

# --- ESTILO VENEZUELA (BLINDAJE TOTAL + TRICOLOR) ---
st.markdown("""
    <style>
    /* OCULTAR ELEMENTOS DE SISTEMA Y STREAMLIT */
    #MainMenu {display: none !important;}
    footer {display: none !important;}
    .stDeployButton {display: none !important;}
    header {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    #manage-your-app-button {display: none !important;}
    
    /* FONDO Y PANEL LATERAL */
    .stApp { background-color: #111827; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1f2937; border-right: 2px solid #ffcc00; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #ffffff !important; font-weight: bold; }

    /* ENCABEZADO TRICOLOR EN FORMA DE ARCO */
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

    /* BOTONES TRICOLORES DE COMPARTIR */
    .ven-share-card {
        background: linear-gradient(to bottom, #ffcc00 33%, #0033a0 33%, #0033a0 66%, #ce1126 66%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #ffffff;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    
    .ven-share-text {
        color: white !important;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000;
        text-decoration: none;
        font-size: 1.1em;
    }

    /* RECUADROS DE ENTRADA */
    input, textarea, [data-baseweb="select"] { 
        background-color: #ffffff !important; 
        color: #000000 !important;
        font-weight: bold !important;
    }

    .stats-panel {
        background: rgba(31, 41, 55, 0.8);
        padding: 15px;
        border-radius: 20px;
        border: 2px solid #ffcc00;
        text-align: center;
        margin-bottom: 20px;
    }

    .footer-willian { 
        background: #000; 
        padding: 30px; 
        text-align: center; 
        border-top: 4px solid #ffcc00; 
        margin-top: 50px; 
    }
    
    .master-panel {
        background-color: #0033a0;
        border: 3px solid #ffcc00;
        padding: 20px;
        border-radius: 15px;
    }

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
    }
    </style>
    """, unsafe_allow_html=True)

# --- PRECARGA ---
def precargar_datos():
    res = conn.query("SELECT count(*) FROM comercios", ttl=0)
    if res.iloc[0,0] == 0:
        negocios = [
            # 20 NEGOCIOS REALES
            ('Panadería El Gran Paseo', 'Panaderias', 'Av. Ayacucho con Calle El Parque', 'Excelentes panes sobados y de banquete.', 5, 'https://maps.app.goo.gl/Teresa1'),
            ('Farmatodo Santa Teresa', 'Farmacias', 'Carretera Nacional Santa Teresa-Yare', 'Servicio 24 horas y excelente atención.', 5, 'https://maps.app.goo.gl/Teresa2'),
            ('Supermercado El Gran Trigal', 'Otros', 'C.C. Paseo Tuy', 'Variedad de víveres en el centro.', 4, 'https://maps.app.goo.gl/Teresa3'),
            ('Ferretería La Económica', 'Ferreterias', 'Calle López Aveledo', 'Todo en construcción y plomería.', 4, 'https://maps.app.goo.gl/Teresa4'),
            ('Pollos El Peñón', 'Comida Rapida', 'Variante de Santa Teresa', 'Los mejores pollos en brasas del Tuy.', 5, 'https://maps.app.goo.gl/Teresa5'),
            ('Zapatería El Palacio del Calzado', 'Zapaterias', 'Casco Central, Calle Real', 'Calzado nacional e importado.', 4, 'https://maps.app.goo.gl/Teresa6'),
            ('Inversiones Nassif C.A.', 'Otros', 'Sector Las Flores', 'Distribución de alimentos de calidad.', 5, 'https://maps.app.goo.gl/Teresa7'),
            ('Clínica Paso Real', 'Salud', 'Urb. Paso Real', 'Atención médica integral en la zona.', 5, 'https://maps.app.goo.gl/Teresa8'),
            ('Laboratorio Bio-Análisis Tuy', 'Laboratorios', 'Edif. Centro Tuy', 'Resultados confiables y rápidos.', 5, 'https://maps.app.goo.gl/Teresa9'),
            ('Óptica Santa Lucía', 'Opticas', 'Calle Ayacucho', 'Exámenes de la vista y monturas modernas.', 4, 'https://maps.app.goo.gl/Teresa10'),
            ('Dulcería Criolla Doña Inés', 'Dulcerias', 'Entrada de Mopia', 'Tradición en dulces de almíbar y tortas.', 5, 'https://maps.app.goo.gl/Teresa11'),
            ('Charcutería El Deleite', 'Charcuterias', 'Mercado Municipal', 'Quesos frescos y embutidos de calidad.', 4, 'https://maps.app.goo.gl/Teresa12'),
            ('Carnicería El Ganadero', 'Carnicerias', 'Av. Alí Primera', 'Cortes especiales y carnes frescas.', 5, 'https://maps.app.goo.gl/Teresa13'),
            ('Tienda MultiMax Store', 'Electrodomesticos', 'C.C. Paseo Tuy', 'Tecnología y línea blanca.', 4, 'https://maps.app.goo.gl/Teresa14'),
            ('NetUno Santa Teresa', 'Fibras Opticas', 'Sector El Hato', 'Internet de alta velocidad para el Tuy.', 4, 'https://maps.app.goo.gl/Teresa15'),
            ('Línea de Taxis El Tuy', 'Taxis', 'Terminal de Pasajeros', 'Transporte seguro dentro del municipio.', 4, 'https://maps.app.goo.gl/Teresa16'),
            ('Mototaxis Los Rápidos', 'Mototaxis', 'Frente a la Estación de Tren', 'Traslados rápidos en el centro.', 3, 'https://maps.app.goo.gl/Teresa17'),
            ('Inversiones 316', 'Servicios', 'Calle Falcón', 'Servicios técnicos especializados.', 5, 'https://maps.app.goo.gl/Teresa18'),
            ('Agencia de Loterías La Suerte', 'Otros', 'Calle Comercio', 'Pruebe su suerte aquí.', 3, 'https://maps.app.goo.gl/Teresa19'),
            ('Frutería El Canasto', 'Otros', 'Av. Independencia', 'Frutas y hortalizas del campo.', 4, 'https://maps.app.goo.gl/Teresa20'),
            
            # 10 ENTES PÚBLICOS
            ('Alcaldía del Municipio Independencia', 'Entes Publicos', 'Frente a la Plaza Bolívar', 'Sede administrativa municipal.', 4, 'https://maps.app.goo.gl/Gov1'),
            ('Concejo Municipal Independencia', 'Entes Publicos', 'Calle Ayacucho', 'Legislación y ordenanzas locales.', 4, 'https://maps.app.goo.gl/Gov2'),
            ('CICPC Sub-Delegación Santa Teresa', 'Entes Publicos', 'Sector La Raisa', 'Cuerpo de Investigaciones Científicas.', 5, 'https://maps.app.goo.gl/Gov3'),
            ('Hospital Santa Teresita de Jesús', 'Entes Publicos', 'Av. Alí Primera', 'Principal centro asistencial público.', 3, 'https://maps.app.goo.gl/Gov4'),
            ('Cuerpo de Bomberos de Miranda', 'Entes Publicos', 'Carretera Nacional', 'Atención de emergencias y prevención.', 5, 'https://maps.app.goo.gl/Gov5'),
            ('CANTV Santa Teresa', 'Entes Publicos', 'Calle Falcón', 'Sede de telecomunicaciones del estado.', 3, 'https://maps.app.goo.gl/Gov6'),
            ('Corpoelec Santa Teresa', 'Entes Publicos', 'Sector El Cují', 'Gestión del servicio eléctrico local.', 3, 'https://maps.app.goo.gl/Gov7'),
            ('Saime Santa Teresa', 'Entes Publicos', 'C.C. El Tuy', 'Identificación, migración y extranjería.', 4, 'https://maps.app.goo.gl/Gov8'),
            ('Registro Civil Santa Teresa', 'Entes Publicos', 'Cerca de la Plaza Bolívar', 'Trámites legales y actas de nacimiento.', 4, 'https://maps.app.goo.gl/Gov9'),
            ('Policía Municipal de Independencia', 'Entes Publicos', 'Sector El Cartanal', 'Seguridad ciudadana municipal.', 4, 'https://maps.app.goo.gl/Gov10')
        ]
        with conn.session as s:
            for nombre, cat, ub, res, est, murl in negocios:
                s.execute(text("""
                    INSERT INTO comercios (nombre, categoria, ubicacion, foto_url, reseña_willian, estrellas_w, maps_url) 
                    VALUES (:n, :c, :u, 'https://via.placeholder.com/400', :r, :e, :m)
                """), {"n": nombre, "c": cat, "u": ub, "r": res, "e": est, "m": murl})
            s.commit()

precargar_datos()

# --- PANEL LATERAL ---
with st.sidebar:
    st.title("🇻🇪 Gestión")
    opcion_menu = st.radio("Ir a:", ["🏢 Ver Guía Comercial", "🔐 Administración"])
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
if opcion_menu == "🔐 Administración":
    clave = st.text_input("Clave de Acceso:", type="password")
    if clave == "Juan*316*":
        st.success("Acceso Maestro Concedido")
        tab1, tab2 = st.tabs(["🏢 Añadir Negocio", "🖼️ Logo"])
        with tab1:
            with st.form("admin_form"):
                n = st.text_input("Nombre del Negocio")
                cat = st.selectbox("Categoría", CAT_LIST)
                ub = st.text_input("Ubicación")
                gm = st.text_input("Enlace Google Maps (URL)")
                res = st.text_area("Tu Reseña")
                est = st.slider("Estrellas", 1, 5, 5)
                if st.form_submit_button("Guardar en la Base de Datos"):
                    with conn.session as s:
                        s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, reseña_willian, estrellas_w, maps_url) VALUES (:n, :c, :u, :r, :e, :m)"),
                                    {"n": n, "c": cat, "u": ub, "r": res, "e": est, "m": gm})
                        s.commit()
                    st.success("¡Guardado correctamente!")
        with tab2:
            st.write("Mantenimiento de Imagen")

elif opcion_menu == "🏢 Ver Guía Comercial":
    st.title("🚀 Guía Comercial Almenar")
    st.write("#### Santa Teresa del Tuy: Información confiable para nuestra gente")

    link_app = "https://guia-comercial-almenar-cpe3yfntxmzncn2e7wgueh.streamlit.app"
    whatsapp_url = f"https://api.whatsapp.com/send?text=¡Mira la Guía Comercial de Santa Teresa! 🚀 {link_app}"
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f'''
            <a href="{whatsapp_url}" target="_blank" style="text-decoration:none;">
                <div class="ven-share-card">
                    <div style="color:white; font-size:0.8em; margin-bottom:5px;">★ ★ ★ ★ ★ ★ ★ ★</div>
                    <span class="ven-share-text">📲 Compartir por WhatsApp</span>
                </div>
            </a>
        ''', unsafe_allow_html=True)
    with col_s2:
        st.markdown(f'''
            <div class="ven-share-card">
                <div style="color:white; font-size:0.8em; margin-bottom:5px;">★ ★ ★ ★ ★ ★ ★ ★</div>
                <span class="ven-share-text">🔗 Enlace Directo:</span><br>
                <b style="color:#ffcc00; font-size:0.9em;">{link_app}</b>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")
    
    with st.expander("📢 ¿Deseas reportar una irregularidad comercial? Haz clic aquí"):
        with st.form("denuncia_principal"):
            st.write("### Centro de Denuncias Ciudadanas")
            com_d = st.text_input("Comercio afectado")
            mot_d = st.text_area("Motivo de la denuncia")
            if st.form_submit_button("Enviar Reporte"):
                with conn.session as s:
                    s.execute(text("INSERT INTO denuncias (denunciante, comercio_afectado, motivo, fecha) VALUES ('Anónimo', :c, :m, :f)"),
                                {"c": com_d, "m": mot_d, "f": ahora_vzla.strftime("%d/%m/%Y")})
                    s.commit()
                st.success("Denuncia recibida por Willian Almenar.")

    st.markdown("---")
    
    # --- BUSCADOR Y PESTAÑAS DE CATEGORÍAS ---
    busq = st.text_input("🔍 ¿Qué buscas en Santa Teresa?", placeholder="Ej: Panadería, Farmacia...")
    
    # Sistema de Pestañas
    tab_labels = ["Todos"] + CAT_LIST
    tabs_main = st.tabs(tab_labels)
    
    df = conn.query("SELECT * FROM comercios", ttl=0)
    
    for i, tab in enumerate(tabs_main):
        with tab:
            categoria_seleccionada = tab_labels[i]
            
            if not df.empty:
                # Filtrado por buscador
                filtrado = df[df['nombre'].str.contains(busq, case=False) | df['categoria'].str.contains(busq, case=False)]
                
                # Filtrado adicional por pestaña (si no es "Todos")
                if categoria_seleccionada != "Todos":
                    filtrado = filtrado[filtrado['categoria'] == categoria_seleccionada]
                
                if filtrado.empty:
                    st.warning(f"No hay comercios registrados en {categoria_seleccionada}." if categoria_seleccionada != "Todos" else "No se encontraron resultados.")
                else:
                    for _, r in filtrado.iterrows():
                        with st.expander(f"🏢 {r['nombre']} - {r['categoria']}"):
                            col_img, col_info = st.columns([1, 2])
                            with col_img:
                                if r['foto_url']:
                                    st.image(r['foto_url'], use_container_width=True)
                            with col_info:
                                st.write(f"📍 **Ubicación:** {r['ubicacion']}")
                                if r['maps_url']:
                                    st.link_button("🗺️ Ver en Google Maps", r['maps_url'])
                                st.write(f"⭐ **Calificación Willian:** {'⭐' * (r['estrellas_w'] if r['estrellas_w'] else 0)}")
                                st.info(f"**Reseña de Willian:** {r['reseña_willian']}")
                            
                            st.markdown("---")
                            st.write("💬 **Opiniones y Calificación de Usuarios:**")
                            
                            with st.form(f"form_op_{i}_{r['id']}"):
                                u_nom = st.text_input("Tu Nombre", key=f"un_{i}_{r['id']}")
                                u_com = st.text_area("Tu comentario", key=f"uc_{i}_{r['id']}")
                                u_est = st.slider("Tu calificación", 1, 5, 5, key=f"ue_{i}_{r['id']}")
                                if st.form_submit_button("Enviar Opinión"):
                                    with conn.session as s:
                                        s.execute(text("INSERT INTO opiniones (comercio_id, usuario, comentario, estrellas_u, fecha) VALUES (:id, :u, :c, :e, :f)"),
                                                    {"id": r['id'], "u": u_nom, "c": u_com, "e": u_est, "f": ahora_vzla.strftime("%d/%m/%Y")})
                                        s.commit()
                                    st.rerun()

                            op_df = conn.query(f"SELECT * FROM opiniones WHERE comercio_id = {r['id']} ORDER BY id DESC", ttl=0)
                            if not op_df.empty:
                                for _, op in op_df.iterrows():
                                    st.write(f"👤 **{op['usuario']}** ({op['fecha']}): {op['comentario']} ({'⭐'*op['estrellas_u']})")

# --- PANEL DE ADMINISTRADOR MAESTRO MEJORADO ---
st.markdown("---")
with st.expander("🛠️ PANEL DE CONTROL MAESTRO (Acceso Restringido)"):
    master_key = st.text_input("Ingrese Contraseña Maestra para gestionar datos:", type="password", key="master_pass")
    if master_key == "Juan*316*":
        st.markdown('<div class="master-panel">', unsafe_allow_html=True)
        st.subheader("📊 GESTIÓN INTEGRAL DE LA GUÍA")
        m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs(["📝 Denuncias", "➕ Agregar Comercio", "⚙️ Modificar/Eliminar", "💬 Opiniones"])
        
        with m_tab1:
            denuncias_df = conn.query("SELECT * FROM denuncias ORDER BY id DESC", ttl=0)
            if not denuncias_df.empty:
                st.dataframe(denuncias_df, use_container_width=True)
                if st.button("Limpiar historial de denuncias"):
                    with conn.session as s:
                        s.execute(text("DELETE FROM denuncias"))
                        s.commit()
                    st.rerun()

        with m_tab2:
            st.write("### Registrar Nuevo Comercio")
            with st.form("master_add_form"):
                add_n = st.text_input("Nombre del Negocio")
                add_cat = st.selectbox("Categoría", CAT_LIST, key="add_cat")
                add_ub = st.text_input("Ubicación exacta")
                add_maps = st.text_input("Enlace Google Maps")
                add_res = st.text_area("Reseña de Willian")
                add_est = st.slider("Calificación (Estrellas)", 1, 5, 5)
                add_foto = st.file_uploader("Subir Imagen del Local", type=["png", "jpg", "jpeg"])
                if st.form_submit_button("🚀 Registrar Comercio"):
                    img_data = imagen_a_base64(add_foto) if add_foto else None
                    with conn.session as s:
                        s.execute(text("INSERT INTO comercios (nombre, categoria, ubicacion, reseña_willian, estrellas_w, foto_url, maps_url) VALUES (:n, :c, :u, :r, :e, :f, :m)"),
                                    {"n": add_n, "c": add_cat, "u": add_ub, "r": add_res, "e": add_est, "f": img_data, "m": add_maps})
                        s.commit()
                    st.success("Negocio añadido con éxito.")
                    st.rerun()
                
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
                        new_cat = st.selectbox("Categoría", CAT_LIST, index=CAT_LIST.index(target['categoria']) if target['categoria'] in CAT_LIST else 0)
                        new_ub = st.text_input("Ubicación", value=target['ubicacion'])
                        new_maps = st.text_input("Google Maps URL", value=target['maps_url'] if target['maps_url'] else "")
                    with col2:
                        new_est = st.slider("Estrellas Willian", 1, 5, int(target['estrellas_w']))
                        new_foto = st.file_uploader("Cambiar Foto", type=["png", "jpg", "jpeg"])
                    new_res_text = st.text_area("Reseña de Willian", value=target['reseña_willian'])
                    if st.form_submit_button("✅ Actualizar"):
                        final_foto = target['foto_url'] if not new_foto else imagen_a_base64(new_foto)
                        with conn.session as s:
                            s.execute(text("UPDATE comercios SET nombre=:n, categoria=:c, ubicacion=:u, reseña_willian=:r, estrellas_w=:e, foto_url=:f, maps_url=:m WHERE id=:id"),
                                    {"n":new_n, "c":new_cat, "u":new_ub, "r":new_res_text, "e":new_est, "f":final_foto, "m":new_maps, "id":target['id']})
                            s.commit()
                        st.rerun()

        with m_tab4:
            todas_op = conn.query("SELECT opiniones.id, comercios.nombre as comercio, usuario, comentario, estrellas_u FROM opiniones JOIN comercios ON opiniones.comercio_id = comercios.id", ttl=0)
            st.dataframe(todas_op, use_container_width=True)
            
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
