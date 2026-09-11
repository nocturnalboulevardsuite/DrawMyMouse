import io
import base64
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw
import streamlit.components.v1 as components
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
tab1, tab2, tab3 = st.tabs(["🖼️ Convertir Imagen", "🎨 Editor de Diseño", "🌐 Cursores de la Comunidad"])


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
        st.markdown("**📥 Descargas y Exportación**")
        
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
# PESTAÑA 2: EDITOR DE DISEÑO (MODO 8-BIT Y MODO PAINT)
# =========================================================
with tab2:
    st.subheader("Editor de Diseño")
    
    draw_mode_type = st.radio(
        "Modo de creación:",
        ["👾 Modo Píxeles (Matriz 8-Bit)", "🎨 Modo Paint (Trazo Libre)"],
        horizontal=True
    )

    if "8-Bit" in draw_mode_type:
        st.caption("Pinta directamente cuadro por cuadro sobre la cuadrícula.")

        pixel_editor_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body { font-family: system-ui, sans-serif; color: #ffffff; background: transparent; margin: 0; padding: 0; }
            .editor-container { display: flex; flex-direction: column; align-items: center; gap: 12px; }
            .toolbar { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 10px; background: #1e222a; padding: 10px 16px; border-radius: 8px; width: 100%; max-width: 360px; box-sizing: border-box; }
            .toolbar label { font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; cursor: pointer; }
            .toolbar input[type="color"] { border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; background: none; }
            .toolbar select, .toolbar button { background: #2b303c; color: white; border: 1px solid #3d4454; padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: 0.2s; }
            .toolbar button.active { background: #ff4b4b; border-color: #ff4b4b; font-weight: bold; }
            .toolbar button:hover { background: #3d4454; }
            .canvas-box { position: relative; width: 320px; height: 320px; border: 2px solid #3d4454; border-radius: 8px; overflow: hidden; background: #ffffff; cursor: crosshair; }
            canvas { display: block; image-rendering: pixelated; image-rendering: crisp-edges; }
            .action-btns { display: flex; gap: 10px; width: 100%; max-width: 360px; }
            .btn-dl { flex: 1; background: #ff4b4b; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px; text-align: center; text-decoration: none; }
            .btn-dl:hover { background: #e03e3e; }
        </style>
        </head>
        <body>

        <div class="editor-container">
            <div class="toolbar">
                <label>Color: <input type="color" id="colorPicker" value="#8A0303"></label>
                <button id="btnPencil" class="active" onclick="setTool('pencil')">✏️ Pincel</button>
                <button id="btnEraser" onclick="setTool('eraser')">🧹 Borrador</button>
                <button id="btnClear" onclick="clearCanvas()">🗑️ Limpiar</button>
                <select id="gridSizeSelect" onchange="changeGridSize(this.value)">
                    <option value="16" selected>Grid: 16x16 (Clásico)</option>
                    <option value="24">Grid: 24x24</option>
                    <option value="32">Grid: 32x32</option>
                </select>
            </div>

            <div class="canvas-box">
                <canvas id="pixelCanvas" width="320" height="320"></canvas>
            </div>

            <div class="action-btns">
                <a id="downloadPng" class="btn-dl" download="cursor_8bit.png">🖼️ Descargar PNG</a>
                <a id="downloadIco" class="btn-dl" download="cursor_8bit.ico">📥 Descargar .ICO</a>
            </div>
        </div>

        <script>
            let gridSize = 16;
            const displaySize = 320;
            let isDrawing = false;
            let currentTool = 'pencil';
            
            const offCanvas = document.createElement('canvas');
            offCanvas.width = gridSize;
            offCanvas.height = gridSize;
            const offCtx = offCanvas.getContext('2d', { willReadFrequently: true });

            const canvas = document.getElementById('pixelCanvas');
            const ctx = canvas.getContext('2d');

            function initGrid() {
                offCanvas.width = gridSize;
                offCanvas.height = gridSize;
                offCtx.clearRect(0, 0, gridSize, gridSize);
                render();
            }

            function render() {
                ctx.clearRect(0, 0, displaySize, displaySize);
                
                ctx.imageSmoothingEnabled = false;
                ctx.drawImage(offCanvas, 0, 0, displaySize, displaySize);

                const cellSize = displaySize / gridSize;
                ctx.strokeStyle = 'rgba(180, 180, 180, 0.5)';
                ctx.lineWidth = 1;

                ctx.beginPath();
                for (let i = 0; i <= gridSize; i++) {
                    let pos = Math.floor(i * cellSize) + 0.5;
                    ctx.moveTo(pos, 0);
                    ctx.lineTo(pos, displaySize);
                    ctx.moveTo(0, pos);
                    ctx.lineTo(displaySize, pos);
                }
                ctx.stroke();

                updateDownloadLinks();
            }

            function paintCell(e) {
                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const cellSize = displaySize / gridSize;
                const gridX = Math.floor(mouseX / cellSize);
                const gridY = Math.floor(mouseY / cellSize);

                if (gridX >= 0 && gridX < gridSize && gridY >= 0 && gridY < gridSize) {
                    if (currentTool === 'pencil') {
                        const color = document.getElementById('colorPicker').value;
                        offCtx.fillStyle = color;
                        offCtx.fillRect(gridX, gridY, 1, 1);
                    } else if (currentTool === 'eraser') {
                        offCtx.clearRect(gridX, gridY, 1, 1);
                    }
                    render();
                }
            }

            canvas.addEventListener('mousedown', (e) => { isDrawing = true; paintCell(e); });
            canvas.addEventListener('mousemove', (e) => { if (isDrawing) paintCell(e); });
            window.addEventListener('mouseup', () => { isDrawing = false; });

            function setTool(tool) {
                currentTool = tool;
                document.getElementById('btnPencil').classList.toggle('active', tool === 'pencil');
                document.getElementById('btnEraser').classList.toggle('active', tool === 'eraser');
            }

            function clearCanvas() {
                offCtx.clearRect(0, 0, gridSize, gridSize);
                render();
            }

            function changeGridSize(val) {
                gridSize = parseInt(val);
                initGrid();
            }

            function updateDownloadLinks() {
                const dataUrl = offCanvas.toDataURL('image/png');
                document.getElementById('downloadPng').href = dataUrl;
                document.getElementById('downloadIco').href = dataUrl;
            }

            initGrid();
        </script>
        </body>
        </html>
        """
        components.html(pixel_editor_html, height=480)

    else:
        st.caption("🎨 Dibuja libremente trazos suaves con el pincel:")
        
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            draw_color = st.color_picker("Color del pincel:", "#8A0303", key="paint_color")
            tool = st.radio("Herramienta:", ["Pincel", "Borrador"], horizontal=True, key="paint_tool")
        
        with col_ctrl2:
            grid_size = st.selectbox("Resolución final (px):", [16, 32, 48, 64], index=1, key="paint_res")
            brush_size = st.slider("Grosor del pincel:", min_value=2, max_value=28, value=10, step=2, key="paint_brush")

        stroke_color = draw_color if tool == "Pincel" else "rgba(0,0,0,0)"

        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=brush_size,
            stroke_color=stroke_color,
            background_color="#FFFFFF",
            height=320,
            width=320,
            drawing_mode="freedraw",
            key="canvas_freedraw_mode",
        )

        if canvas_result is not None and canvas_result.image_data is not None:
            canvas_data = canvas_result.image_data
            if np.any(canvas_data):
                img_drawn = Image.fromarray(canvas_data.astype(np.uint8), "RGBA")
                cursor_paint = img_drawn.resize((grid_size, grid_size), Image.Resampling.BILINEAR)

                st.divider()
                col_p1, col_p2 = st.columns(2)
                
                with col_p1:
                    st.write("**Vista Previa del Cursor:**")
                    st.image(cursor_paint, caption=f"Tamaño: {grid_size}x{grid_size}px", width=128)
                
                with col_p2:
                    st.write("**Exportar diseño:**")
                    buf_p_ico = io.BytesIO()
                    cursor_paint.save(buf_p_ico, format="ICO")
                    
                    buf_p_png = io.BytesIO()
                    cursor_paint.save(buf_p_png, format="PNG")
                    
                    st.download_button(
                        label="📥 Descargar (.ico)",
                        data=buf_p_ico.getvalue(),
                        file_name="cursor_paint.ico",
                        mime="image/x-icon",
                        use_container_width=True
                    )
                    st.download_button(
                        label="🖼️ Descargar PNG",
                        data=buf_p_png.getvalue(),
                        file_name="cursor_paint.png",
                        mime="image/png",
                        use_container_width=True
                    )


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
                st.markdown(f"**{item['title']}**")
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
