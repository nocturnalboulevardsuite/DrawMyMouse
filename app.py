import io
import base64
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas

# Configuración de la página
st.set_page_config(
    page_title="DrawMyMouse — Pixel Cursor Studio",
    page_icon="🖱️",
    layout="centered"
)

# Inicializar almacenamiento de la comunidad en la sesión
if "community_cursors" not in st.session_state:
    st.session_state.community_cursors = []
    
    # Crear cursores de ejemplo estilo 8-bit
    def create_sample_cursor(color, shape_type):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        if shape_type == "sword":
            draw.polygon([(4, 4), (4, 24), (10, 18), (16, 28), (20, 26), (14, 16), (22, 16)], fill=color, outline="black")
        elif shape_type == "cross":
            draw.rectangle([(12, 4), (18, 26)], fill=color, outline="black")
            draw.rectangle([(4, 12), (26, 18)], fill=color, outline="black")
        else:
            draw.polygon([(2, 2), (2, 28), (10, 20), (22, 20)], fill=color, outline="black")
        return img

    demo1 = create_sample_cursor("#FF1E43", "arrow")
    demo2 = create_sample_cursor("#00D2FF", "sword")
    demo3 = create_sample_cursor("#B026FF", "cross")

    for demo_img, title, author in [
        (demo1, "Blood Neon Arrow", "NocturnalSuite"),
        (demo2, "Cyber Blade", "MatrixDev"),
        (demo3, "Gothic Cross", "PixelArtist")
    ]:
        buf_png = io.BytesIO()
        demo_img.save(buf_png, format="PNG")
        buf_ico = io.BytesIO()
        demo_img.save(buf_ico, format="ICO")
        
        st.session_state.community_cursors.append({
            "title": title,
            "author": author,
            "png_bytes": buf_png.getvalue(),
            "ico_bytes": buf_ico.getvalue(),
            "preview_img": demo_img
        })

# Encabezado e identidad de marca
st.title("🖱️ DrawMyMouse")
st.caption("Diseña, dibuja y comparte tus propios cursores en la comunidad.")

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["🖼️ Convertir Imagen", "👾 Dibujar Cursor 8-Bit", "🌐 Cursores de la Comunidad"])


# =========================================================
# PESTAÑA 1: CONVERTIR IMAGEN EXISTENTE
# =========================================================
with tab1:
    st.subheader("Convertir imagen a cursor")
    st.write("Sube cualquier imagen para transformarla en un puntero `.ico` o `.png`.")
    
    uploaded_file = st.file_uploader(
        "Carga tu imagen (PNG con transparencia recomendado):",
        type=["png", "jpg", "jpeg", "webp"],
        key="uploader_tab1"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGBA")
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="Imagen Original", use_container_width=True)
        
        with col2:
            size = st.selectbox("Tamaño del cursor (px):", [16, 32, 48, 64], index=1)
            resampling_method = st.radio(
                "Estilo de escalado:",
                ["Píxel / Retro (Nearest Neighbor)", "Suave (Bilinear)"],
                index=0
            )
            
            resample_flag = Image.Resampling.NEAREST if "Retro" in resampling_method else Image.Resampling.BILINEAR
            cursor_img = image.resize((size, size), resample=resample_flag)
            
            st.image(cursor_img, caption=f"Vista previa ({size}x{size}px)", width=128)

        st.divider()
        st.markdown("### 📥 Descargas y Exportación")
        
        buf_ico = io.BytesIO()
        cursor_img.save(buf_ico, format="ICO")
        
        buf_png = io.BytesIO()
        cursor_img.save(buf_png, format="PNG")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📥 Descargar Cursor (.ico)",
                data=buf_ico.getvalue(),
                file_name="drawmymouse_cursor.ico",
                mime="image/x-icon",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="🖼️ Descargar PNG",
                data=buf_png.getvalue(),
                file_name="drawmymouse_cursor.png",
                mime="image/png",
                use_container_width=True
            )
        
        encoded_png = base64.b64encode(buf_png.getvalue()).decode()
        with st.expander("🌐 Código CSS para tu Web"):
            st.code(
                f"body {{\n  cursor: url('data:image/png;base64,{encoded_png}'), auto;\n}}", 
                language="css"
            )


# =========================================================
# PESTAÑA 2: DIBUJAR CURSOR 8-BITS / PAINT
# =========================================================
with tab2:
    st.subheader("Editor de Diseño")
    
    draw_mode_type = st.radio(
        "Modo de creación:",
        ["👾 Modo Píxeles (Retícula 8-Bit)", "🎨 Modo Paint (Trazo Libre)"],
        horizontal=True
    )

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        draw_color = st.color_picker("Color del pincel:", "#8A0303")
        tool = st.radio("Herramienta:", ["Pincel", "Borrador"], horizontal=True)
    
    with col_ctrl2:
        if "8-Bit" in draw_mode_type:
            grid_size = st.selectbox("Grid Píxeles:", [16, 24, 32], index=0, help="16x16 es el estándar clásico de 8 bits.")
            # Cálculo exacto del tamaño del píxel en un lienzo de 320px
            cell_px = 320 // grid_size
            brush_blocks = st.slider("Tamaño de bloque (Píxeles):", min_value=1, max_value=3, value=1)
            brush_size = cell_px * brush_blocks
        else:
            grid_size = st.selectbox("Resolución final:", [16, 32, 48], index=1)
            brush_size = st.slider("Grosor del pincel libre:", min_value=4, max_value=28, value=12, step=2)

    stroke_color = draw_color if tool == "Pincel" else "rgba(0,0,0,0)"

    # Inyección de cuadrícula visual CSS estilo 8-Bit Painter
    if "8-Bit" in draw_mode_type:
        cell_size_css = 320 / grid_size
        st.markdown(
            f"""
            <style>
            div[data-testid="stCanvas"] {{
                border: 2px solid #555;
            }}
            div[data-testid="stCanvas"] canvas {{
                background-image: 
                    linear-gradient(to right, rgba(0, 0, 0, 0.2) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(0, 0, 0, 0.2) 1px, transparent 1px) !important;
                background-size: {cell_size_css}px {cell_size_css}px !important;
                background-color: #ffffff !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    st.caption("🎨 Dibuja dentro del recuadro:")
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",
        stroke_width=brush_size,
        stroke_color=stroke_color,
        background_color="#ffffff" if "8-Bit" in draw_mode_type else "#F0F2F6",
        height=320,
        width=320,
        drawing_mode="freedraw",
        key=f"pixel_art_canvas_{draw_mode_type}_{grid_size}",
    )

    if canvas_result is not None:
        try:
            canvas_data = canvas_result.image_data
            if canvas_data is not None and np.any(canvas_data):
                drawn_data = canvas_data.astype(np.uint8)
                img_drawn = Image.fromarray(drawn_data, "RGBA")
                
                if "8-Bit" in draw_mode_type:
                    # Reducción sin suavizado (NEAREST)
                    img_small = img_drawn.resize((grid_size, grid_size), Image.Resampling.NEAREST)
                    
                    # Cuantización de transparencia (elimina bordes borrosos)
                    np_small = np.array(img_small)
                    alpha = np_small[:, :, 3]
                    np_small[:, :, 3] = np.where(alpha > 30, 255, 0)
                    pixel_cursor = Image.fromarray(np_small, "RGBA")
                else:
                    pixel_cursor = img_drawn.resize((grid_size, grid_size), Image.Resampling.BILINEAR)
                
                st.divider()
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.write("**Vista previa final (8-Bit Pixel Art):**")
                    # Mostrar la vista previa agrandada pero pixelada
                    preview_large = pixel_cursor.resize((128, 128), Image.Resampling.NEAREST)
                    st.image(preview_large, caption=f"Cursor Resultado ({grid_size}x{grid_size}px)")
                    
                with col_res2:
                    st.write("**Exportar diseño:**")
                    
                    buf_art_ico = io.BytesIO()
                    pixel_cursor.save(buf_art_ico, format="ICO")
                    
                    buf_art_png = io.BytesIO()
                    pixel_cursor.save(buf_art_png, format="PNG")
                    
                    st.download_button(
                        label="📥 Descargar (.ico)",
                        data=buf_art_ico.getvalue(),
                        file_name="cursor_8bit.ico",
                        mime="image/x-icon",
                        use_container_width=True
                    )
                    
                    st.download_button(
                        label="🖼️ Descargar PNG",
                        data=buf_art_png.getvalue(),
                        file_name="cursor_8bit.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                # Publicación a la comunidad
                with st.expander("🚀 ¿Quieres publicar este diseño en la Comunidad?"):
                    with st.form("publish_form"):
                        pub_title = st.text_input("Nombre de tu Mouse:", "Pixel Mouse 8-Bit")
                        pub_author = st.text_input("Tu Nombre/Alias:", "PixelArtist")
                        submit_pub = st.form_submit_button("🌟 Publicar Gratis para Todos")
                        
                        if submit_pub:
                            st.session_state.community_cursors.append({
                                "title": pub_title,
                                "author": pub_author,
                                "png_bytes": buf_art_png.getvalue(),
                                "ico_bytes": buf_art_ico.getvalue(),
                                "preview_img": pixel_cursor
                            })
                            st.success(f"¡Genial! Tu cursor '{pub_title}' se ha publicado en la pestaña Comunidad.")
        except Exception:
            pass


# =========================================================
# PESTAÑA 3: CURSORES DE LA COMUNIDAD (FREE DOWNLOADS)
# =========================================================
with tab3:
    st.subheader("🌐 Cursores Creados por la Comunidad")
    st.write("Explora, descarga gratis o publica tus propios diseños hechos en DrawMyMouse.")
    
    with st.expander("📤 Subir un archivo de Mouse (.png / .ico) a la comunidad"):
        with st.form("upload_community_form"):
            comm_file = st.file_uploader("Elige tu imagen de cursor:", type=["png", "ico"])
            comm_title = st.text_input("Título del Cursor:", "Neon Pointer")
            comm_author = st.text_input("Autor:", "DiseñadorWeb")
            submit_upload = st.form_submit_button("Subir a la Comunidad")
            
            if submit_upload and comm_file:
                upload_img = Image.open(comm_file).convert("RGBA").resize((32, 32), Image.Resampling.NEAREST)
                
                b_png = io.BytesIO()
                upload_img.save(b_png, format="PNG")
                b_ico = io.BytesIO()
                upload_img.save(b_ico, format="ICO")
                
                st.session_state.community_cursors.append({
                    "title": comm_title,
                    "author": comm_author,
                    "png_bytes": b_png.getvalue(),
                    "ico_bytes": b_ico.getvalue(),
                    "preview_img": upload_img
                })
                st.success("¡Cursor subido a la comunidad con éxito!")

    st.divider()
    
    if not st.session_state.community_cursors:
        st.info("Aún no hay cursores en la comunidad. ¡Sé el primero en publicar uno!")
    else:
        cols = st.columns(3)
        for idx, item in enumerate(reversed(st.session_state.community_cursors)):
            col = cols[idx % 3]
            with col:
                st.markdown(f"#### {item['title']}")
                st.caption(f"👤 Por: **{item['author']}**")
                
                preview_large_comm = item['preview_img'].resize((96, 96), Image.Resampling.NEAREST)
                st.image(preview_large_comm)
                
                st.download_button(
                    label="📥 .ICO",
                    data=item['ico_bytes'],
                    file_name=f"{item['title'].lower().replace(' ', '_')}.ico",
                    mime="image/x-icon",
                    key=f"dl_ico_{idx}",
                    use_container_width=True
                )
                st.download_button(
                    label="🖼️ .PNG",
                    data=item['png_bytes'],
                    file_name=f"{item['title'].lower().replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"dl_png_{idx}",
                    use_container_width=True
                )
                st.markdown("---")
