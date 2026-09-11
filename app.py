import io
import base64
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# Configuración de la página
st.set_page_config(
    page_title="DrawMyMouse — Pixel Cursor Studio",
    page_icon="🖱️",
    layout="centered"
)

# Encabezado e identidad de marca
st.title("🖱️ DrawMyMouse")
st.caption("Diseña, dibuja y convierte tus propias imágenes en cursores para mouse.")

# Pestañas principales
tab1, tab2 = st.tabs(["🖼️ Convertir Imagen", "🎨 Dibujar Píxel Art"])


# =========================================================
# PESTAÑA 1: CONVERTIR IMAGEN EXISTENTE
# =========================================================
with tab1:
    st.subheader("Convertir imagen a cursor")
    st.write("Sube cualquier imagen para transformarla en un puntero `.ico` o `.png`.")
    
    uploaded_file = st.file_uploader(
        "Carga tu imagen (PNG con transparencia recomendado):",
        type=["png", "jpg", "jpeg", "webp"]
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
            
            # Elegir algoritmo de reescalado
            resample_flag = Image.Resampling.NEAREST if "Retro" in resampling_method else Image.Resampling.BILINEAR
            cursor_img = image.resize((size, size), resample=resample_flag)
            
            st.image(cursor_img, caption=f"Vista previa ({size}x{size}px)", width=128)

        st.divider()
        st.markdown("### 📥 Descargas y Exportación")
        
        # Guardar en memoria (BytesIO) para descarga
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
        
        # Extra: Generador de snippet para web
        encoded_png = base64.b64encode(buf_png.getvalue()).decode()
        with st.expander("🌐 ¿Quieres usarlo en tu sitio web? (Código CSS)"):
            st.code(
                f"/* Agrega este código a tu CSS */\nbody {{\n  cursor: url('data:image/png;base64,{encoded_png}'), auto;\n}}", 
                language="css"
            )


# =========================================================
# PESTAÑA 2: LIENZO PARA DIBUJAR PÍXEL ART
# =========================================================
with tab2:
    st.subheader("Crea tu propio cursor píxel por píxel")
    st.write("Usa el lienzo para dibujar la forma de tu cursor estilo Paint.NET.")

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        draw_color = st.color_picker("Color de pincel:", "#000000")
        tool = st.radio("Herramienta:", ["Pincel", "Borrador"], horizontal=True)
    
    with col_ctrl2:
        grid_size = st.selectbox("Resolución de salida:", [16, 32], index=1)
        brush_size = st.slider("Grosor del trazo:", min_value=8, max_value=24, value=12, step=2)

    # Configuración de trazo según herramienta
    stroke_color = draw_color if tool == "Pincel" else "rgba(0,0,0,0)"

    st.caption("🎨 Dibuja dentro del recuadro:")
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",
        stroke_width=brush_size,
        stroke_color=stroke_color,
        background_color="#F0F2F6",
        height=320,
        width=320,
        drawing_mode="freedraw",
        key="pixel_art_canvas",
    )

    if canvas_result.image_data is not None:
        # Convertir datos del canvas a imagen PIL
        drawn_data = canvas_result.image_data.astype(np.uint8)
        img_drawn = Image.fromarray(drawn_data, "RGBA")
        
        # Reducir imagen manteniendo el estilo de píxel
        pixel_cursor = img_drawn.resize((grid_size, grid_size), Image.Resampling.NEAREST)
        
        st.divider()
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.write("**Resultado escala real:**")
            st.image(pixel_cursor, caption=f"Cursor Final ({grid_size}x{grid_size}px)", width=128)
            
        with col_res2:
            st.write("**Exportar diseño:**")
            
            buf_art_ico = io.BytesIO()
            pixel_cursor.save(buf_art_ico, format="ICO")
            
            buf_art_png = io.BytesIO()
            pixel_cursor.save(buf_art_png, format="PNG")
            
            st.download_button(
                label="📥 Descargar (.ico)",
                data=buf_art_ico.getvalue(),
                file_name="drawmymouse_custom.ico",
                mime="image/x-icon",
                use_container_width=True
            )
            
            st.download_button(
                label="🖼️ Descargar PNG",
                data=buf_art_png.getvalue(),
                file_name="drawmymouse_custom.png",
                mime="image/png",
                use_container_width=True
            )
            
            encoded_art = base64.b64encode(buf_art_png.getvalue()).decode()
            with st.expander("🌐 Código CSS"):
                st.code(
                    f"body {{\n  cursor: url('data:image/png;base64,{encoded_art}'), auto;\n}}", 
                    language="css"
                )
