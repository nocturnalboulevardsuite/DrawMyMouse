import io
import struct
import base64
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw
import streamlit.components.v1 as components
from streamlit_drawable_canvas import st_canvas

# Generador de archivos .CUR reales con cabecera de Windows
def image_to_cur_bytes(img: Image.Image, hotspot=(0, 0)) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="ICO", sizes=[(img.width, img.height)])
    data = bytearray(buf.getvalue())
    if len(data) >= 14:
        data[2] = 2
        data[3] = 0
        data[10] = hotspot[0] & 0xFF
        data[11] = (hotspot[0] >> 8) & 0xFF
        data[12] = hotspot[1] & 0xFF
        data[13] = (hotspot[1] >> 8) & 0xFF
    return bytes(data)

# Generador de archivos .ANI (Contenedor RIFF para cursores de Windows)
def image_to_ani_bytes(img: Image.Image, hotspot=(0, 0)) -> bytes:
    cur_data = image_to_cur_bytes(img, hotspot)
    if len(cur_data) % 2 != 0:
        cur_data += b'\x00'
        
    icon_chunk = b'icon' + struct.pack('<I', len(cur_data)) + cur_data
    list_content = b'fram' + icon_chunk
    list_chunk = b'LIST' + struct.pack('<I', len(list_content)) + list_content
    
    anih_data = struct.pack('<IIIIIIIII', 36, 1, 1, 0, 0, 0, 0, 10, 1)
    anih_chunk = b'anih' + struct.pack('<I', 36) + anih_data
    
    riff_content = b'ACON' + anih_chunk + list_chunk
    return b'RIFF' + struct.pack('<I', len(riff_content)) + riff_content

# Generador de archivos .ICO
def image_to_ico_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="ICO")
    return buf.getvalue()

# Generador de archivos .PNG
def image_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

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
        st.session_state.community_cursors.append({
            "title": title,
            "author": author,
            "ani_bytes": image_to_ani_bytes(demo_img),
            "cur_bytes": image_to_cur_bytes(demo_img),
            "ico_bytes": image_to_ico_bytes(demo_img),
            "png_bytes": image_to_png_bytes(demo_img),
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
    st.write("Sube cualquier imagen para transformarla en puntero de mouse o icono de carpeta.")
    
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
        
        ani_bytes = image_to_ani_bytes(cursor_img)
        cur_bytes = image_to_cur_bytes(cursor_img)
        ico_bytes = image_to_ico_bytes(cursor_img)
        png_bytes = image_to_png_bytes(cursor_img)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="✨ Descargar (.ani) [Recomendado]",
                data=ani_bytes,
                file_name="cursor.ani",
                mime="application/x-navi-animation",
                use_container_width=True
            )
            st.download_button(
                label="📁 Descargar (.ico) [Personalizar carpetas]",
                data=ico_bytes,
                file_name="cursor.ico",
                mime="image/x-icon",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="🖱️ Descargar (.cur)",
                data=cur_bytes,
                file_name="cursor.cur",
                mime="image/x-win-bitmap",
                use_container_width=True
            )
            st.download_button(
                label="🖼️ Descargar (.png) [Previsualizar]",
                data=png_bytes,
                file_name="cursor.png",
                mime="image/png",
                use_container_width=True
            )
        
        encoded_png = base64.b64encode(png_bytes).decode()
        with st.expander("🌐 Código CSS para tu Web"):
            st.code(
                f"body {{\n  cursor: url('data:image/png;base64,{encoded_png}'), auto;\n}}", 
                language="css"
            )


# =========================================================
# PESTAÑA 2: EDITOR DE DISEÑO
# =========================================================
with tab2:
    st.subheader("Editor de Diseño")
    
    col_mode, col_zoom = st.columns([2, 1])
    with col_mode:
        draw_mode_type = st.radio(
            "Modo de creación:",
            ["👾 Modo Píxeles (Matriz 8-Bit)", "🎨 Modo Paint (Trazo Libre)"],
            horizontal=True
        )
    with col_zoom:
        canvas_dim = st.slider("🔍 Zoom del Lienzo (px):", min_value=320, max_value=520, value=400, step=40)

    st.divider()

    if "8-Bit" in draw_mode_type:
        st.caption("Pinta con Click Izquierdo y Borra con Click Derecho sobre la cuadrícula.")

        pixel_editor_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ font-family: system-ui, sans-serif; color: #ffffff; background: transparent; margin: 0; padding: 0; overflow: hidden; }}
            .editor-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; gap: 14px; padding-bottom: 20px; }}
            .toolbar {{ display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 10px; background: #1e222a; padding: 10px 16px; border-radius: 8px; width: 100%; max-width: {canvas_dim}px; box-sizing: border-box; }}
            .toolbar label {{ font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; cursor: pointer; }}
            .toolbar input[type="color"] {{ border: none; width: 28px; height: 28px; border-radius: 4px; cursor: pointer; background: none; }}
            .toolbar select, .toolbar button {{ background: #2b303c; color: white; border: 1px solid #3d4454; padding: 6px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: 0.2s; }}
            .toolbar button.active {{ background: #ff4b4b; border-color: #ff4b4b; font-weight: bold; }}
            .toolbar button:hover {{ background: #3d4454; }}
            .canvas-box {{ position: relative; width: {canvas_dim}px; height: {canvas_dim}px; border: 2px solid #3d4454; border-radius: 8px; overflow: hidden; background: #ffffff; cursor: crosshair; box-sizing: border-box; }}
            canvas {{ display: block; image-rendering: pixelated; image-rendering: crisp-edges; }}
            
            .action-btns {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; width: 100%; max-width: {canvas_dim}px; box-sizing: border-box; }}
            .btn-dl {{ display: flex; align-items: center; justify-content: center; background: #2b303c; color: white; border: 1px solid #3d4454; padding: 10px 8px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 12px; text-align: center; text-decoration: none; transition: 0.2s; }}
            .btn-dl:hover {{ background: #3d4454; border-color: #ff4b4b; }}
            .btn-rec {{ background: #ff4b4b; border-color: #ff4b4b; font-weight: bold; color: #ffffff; }}
            .btn-rec:hover {{ background: #e03e3e; }}
        </style>
        </head>
        <body>

        <div class="editor-container">
            <div class="toolbar">
                <label>Color: <input type="color" id="colorPicker" value="#8A0303"></label>
                <button id="btnPencil" class="active" onclick="setTool('pencil')">✏️ Pincel (Izquierdo)</button>
                <button id="btnEraser" onclick="setTool('eraser')">🧹 Borrador (Derecho)</button>
                <button id="btnClear" onclick="clearCanvas()">🗑️ Limpiar</button>
                <select id="gridSizeSelect" onchange="changeGridSize(this.value)">
                    <option value="16" selected>Grid: 16x16 (Clásico)</option>
                    <option value="24">Grid: 24x24</option>
                    <option value="32">Grid: 32x32</option>
                </select>
            </div>

            <div class="canvas-box">
                <canvas id="pixelCanvas" width="{canvas_dim}" height="{canvas_dim}"></canvas>
            </div>

            <div class="action-btns">
                <a id="downloadAni" class="btn-dl btn-rec" download="cursor_8bit.ani">✨ .ANI (Recomendado)</a>
                <a id="downloadCur" class="btn-dl" download="cursor_8bit.cur">🖱️ .CUR</a>
                <a id="downloadIco" class="btn-dl" download="cursor_8bit.ico">📁 .ICO (Carpetas)</a>
                <a id="downloadPng" class="btn-dl" download="cursor_8bit.png">🖼️ .PNG (Vista Previa)</a>
            </div>
        </div>

        <script>
            let gridSize = 16;
            const displaySize = {canvas_dim};
            let isDrawing = false;
            let currentTool = 'pencil';
            
            const offCanvas = document.createElement('canvas');
            offCanvas.width = gridSize;
            offCanvas.height = gridSize;
            const offCtx = offCanvas.getContext('2d', {{ willReadFrequently: true }});

            const canvas = document.getElementById('pixelCanvas');
            const ctx = canvas.getContext('2d');

            canvas.addEventListener('contextmenu', (e) => e.preventDefault());

            function initGrid() {{
                offCanvas.width = gridSize;
                offCanvas.height = gridSize;
                offCtx.clearRect(0, 0, gridSize, gridSize);
                render();
            }}

            function render() {{
                ctx.clearRect(0, 0, displaySize, displaySize);
                
                ctx.imageSmoothingEnabled = false;
                ctx.drawImage(offCanvas, 0, 0, displaySize, displaySize);

                const cellSize = displaySize / gridSize;
                ctx.strokeStyle = 'rgba(180, 180, 180, 0.5)';
                ctx.lineWidth = 1;

                ctx.beginPath();
                for (let i = 0; i <= gridSize; i++) {{
                    let pos = Math.floor(i * cellSize) + 0.5;
                    ctx.moveTo(pos, 0);
                    ctx.lineTo(pos, displaySize);
                    ctx.moveTo(0, pos);
                    ctx.lineTo(displaySize, pos);
                }}
                ctx.stroke();

                updateDownloadLinks();
            }}

            function paintCell(e) {{
                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const cellSize = displaySize / gridSize;
                const gridX = Math.floor(mouseX / cellSize);
                const gridY = Math.floor(mouseY / cellSize);

                if (gridX >= 0 && gridX < gridSize && gridY >= 0 && gridY < gridSize) {{
                    if (e.buttons === 2 || e.button === 2) {{
                        offCtx.clearRect(gridX, gridY, 1, 1);
                    }} else if (e.buttons === 1 || e.button === 0) {{
                        if (currentTool === 'pencil') {{
                            const color = document.getElementById('colorPicker').value;
                            offCtx.fillStyle = color;
                            offCtx.fillRect(gridX, gridY, 1, 1);
                        }} else if (currentTool === 'eraser') {{
                            offCtx.clearRect(gridX, gridY, 1, 1);
                        }}
                    }}
                    render();
                }}
            }}

            canvas.addEventListener('mousedown', (e) => {{
                if (e.button === 0 || e.button === 2) {{
                    isDrawing = true;
                    paintCell(e);
                }}
            }});
            canvas.addEventListener('mousemove', (e) => {{ if (isDrawing) paintCell(e); }});
            window.addEventListener('mouseup', () => {{ isDrawing = false; }});

            function setTool(tool) {{
                currentTool = tool;
                document.getElementById('btnPencil').classList.toggle('active', tool === 'pencil');
                document.getElementById('btnEraser').classList.toggle('active', tool === 'eraser');
            }}

            function clearCanvas() {{
                offCtx.clearRect(0, 0, gridSize, gridSize);
                render();
            }}

            function changeGridSize(val) {{
                gridSize = parseInt(val);
                initGrid();
            }}

            async function updateDownloadLinks() {{
                offCanvas.toBlob(async (blob) => {{
                    if (!blob) return;
                    const pngArrayBuffer = await blob.arrayBuffer();
                    const pngBytes = new Uint8Array(pngArrayBuffer);
                    const pngSize = pngBytes.length;

                    // 1. PNG Blob
                    const pngBlob = new Blob([pngBytes], {{ type: 'image/png' }});
                    document.getElementById('downloadPng').href = URL.createObjectURL(pngBlob);

                    // 2. CUR Binary
                    const curHeader = new Uint8Array([
                        0,0, 2,0, 1,0,
                        gridSize >= 256 ? 0 : gridSize, gridSize >= 256 ? 0 : gridSize, 0, 0,
                        0,0, 0,0,
                        pngSize & 0xFF, (pngSize >> 8) & 0xFF, (pngSize >> 16) & 0xFF, (pngSize >> 24) & 0xFF,
                        22, 0, 0, 0
                    ]);
                    const curBuffer = new Uint8Array(22 + pngSize);
                    curBuffer.set(curHeader, 0);
                    curBuffer.set(pngBytes, 22);

                    const curBlob = new Blob([curBuffer], {{ type: 'image/x-win-bitmap' }});
                    document.getElementById('downloadCur').href = URL.createObjectURL(curBlob);

                    // 3. ANI RIFF Binary
                    let pad = (curBuffer.length % 2 !== 0) ? 1 : 0;
                    let iconChunkLen = curBuffer.length + pad;
                    let listContentLen = 4 + 8 + iconChunkLen;
                    let listChunkLen = 8 + listContentLen;
                    let anihLen = 36;
                    let riffContentLen = 4 + 8 + anihLen + listChunkLen;

                    const aniBuffer = new Uint8Array(8 + riffContentLen);
                    let view = new DataView(aniBuffer.buffer);
                    let pos = 0;

                    aniBuffer.set([82, 73, 70, 70], pos); pos += 4;
                    view.setUint32(pos, riffContentLen, true); pos += 4;
                    aniBuffer.set([65, 67, 79, 78], pos); pos += 4;
                    aniBuffer.set([97, 110, 105, 104], pos); pos += 4;
                    view.setUint32(pos, 36, true); pos += 4;
                    
                    view.setUint32(pos, 36, true); view.setUint32(pos+4, 1, true); view.setUint32(pos+8, 1, true);
                    view.setUint32(pos+12, 0, true); view.setUint32(pos+16, 0, true); view.setUint32(pos+20, 0, true);
                    view.setUint32(pos+24, 0, true); view.setUint32(pos+28, 10, true); view.setUint32(pos+32, 1, true);
                    pos += 36;

                    aniBuffer.set([76, 73, 83, 84], pos); pos += 4;
                    view.setUint32(pos, listContentLen, true); pos += 4;
                    aniBuffer.set([102, 114, 97, 109], pos); pos += 4;
                    aniBuffer.set([105, 99, 111, 110], pos); pos += 4;
                    view.setUint32(pos, curBuffer.length, true); pos += 4;
                    aniBuffer.set(curBuffer, pos);

                    const aniBlob = new Blob([aniBuffer], {{ type: 'application/x-navi-animation' }});
                    document.getElementById('downloadAni').href = URL.createObjectURL(aniBlob);

                    // 4. ICO Binary
                    const icoHeader = new Uint8Array([
                        0,0, 1,0, 1,0,
                        gridSize >= 256 ? 0 : gridSize, gridSize >= 256 ? 0 : gridSize, 0, 0,
                        1,0, 32,0,
                        pngSize & 0xFF, (pngSize >> 8) & 0xFF, (pngSize >> 16) & 0xFF, (pngSize >> 24) & 0xFF,
                        22, 0, 0, 0
                    ]);
                    const icoBuffer = new Uint8Array(22 + pngSize);
                    icoBuffer.set(icoHeader, 0);
                    icoBuffer.set(pngBytes, 22);

                    const icoBlob = new Blob([icoBuffer], {{ type: 'image/x-icon' }});
                    document.getElementById('downloadIco').href = URL.createObjectURL(icoBlob);
                }}, 'image/png');
            }}

            initGrid();
        </script>
        </body>
        </html>
        """
        # Altura del iframe holgada para garantizar la visibilidad de los 4 botones de descarga
        components.html(pixel_editor_html, height=canvas_dim + 230)

    else:
        st.caption("🎨 Dibuja libremente trazos suaves con el pincel:")
        
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            draw_color = st.color_picker("Color del pincel:", "#8A0303", key="paint_color")
            tool = st.radio("Herramienta:", ["Pincel", "Borrador"], horizontal=True, key="paint_tool")
        
        with col_ctrl2:
            export_res = st.selectbox("Resolución de exportación (px):", [16, 32, 48, 64], index=1, key="paint_res")
            brush_size = st.slider("Grosor del pincel:", min_value=2, max_value=32, value=12, step=2, key="paint_brush")

        stroke_color = draw_color if tool == "Pincel" else "rgba(0,0,0,0)"

        _, col_canvas_center, _ = st.columns([1, 6, 1])
        
        with col_canvas_center:
            st.markdown(f"<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
            
            canvas_result = st_canvas(
                fill_color="rgba(0, 0, 0, 0)",
                stroke_width=brush_size,
                stroke_color=stroke_color,
                background_color="#FFFFFF",
                height=canvas_dim,
                width=canvas_dim,
                drawing_mode="freedraw",
                key="canvas_freedraw_mode",
            )
            
            st.markdown("</div>", unsafe_allow_html=True)

        if canvas_result is not None:
            try:
                canvas_data = canvas_result.image_data
                if canvas_data is not None and np.any(canvas_data):
                    img_drawn = Image.fromarray(canvas_data.astype(np.uint8), "RGBA")
                    cursor_paint = img_drawn.resize((export_res, export_res), Image.Resampling.BILINEAR)

                    st.divider()
                    col_p1, col_p2 = st.columns(2)
                    
                    with col_p1:
                        st.write("**Vista Previa del Cursor:**")
                        st.image(cursor_paint, caption=f"Tamaño exportado: {export_res}x{export_res}px", width=128)
                    
                    with col_p2:
                        st.write("**Exportar diseño:**")
                        buf_p_ani = image_to_ani_bytes(cursor_paint)
                        buf_p_cur = image_to_cur_bytes(cursor_paint)
                        buf_p_ico = image_to_ico_bytes(cursor_paint)
                        buf_p_png = image_to_png_bytes(cursor_paint)
                        
                        col_p_d1, col_p_d2 = st.columns(2)
                        with col_p_d1:
                            st.download_button(
                                label="✨ (.ani) [Recomendado]",
                                data=buf_p_ani,
                                file_name="cursor_paint.ani",
                                mime="application/x-navi-animation",
                                use_container_width=True
                            )
                            st.download_button(
                                label="📁 (.ico) [Carpetas]",
                                data=buf_p_ico,
                                file_name="cursor_paint.ico",
                                mime="image/x-icon",
                                use_container_width=True
                            )
                        with col_p_d2:
                            st.download_button(
                                label="🖱️ (.cur)",
                                data=buf_p_cur,
                                file_name="cursor_paint.cur",
                                mime="image/x-win-bitmap",
                                use_container_width=True
                            )
                            st.download_button(
                                label="🖼️ (.png) [Vista Previa]",
                                data=buf_p_png,
                                file_name="cursor_paint.png",
                                mime="image/png",
                                use_container_width=True
                            )
            except Exception:
                pass


# =========================================================
# PESTAÑA 3: CURSORES DE LA COMUNIDAD
# =========================================================
with tab3:
    st.subheader("🌐 Cursores Creados por la Comunidad")
    st.write("Explora, descarga gratis o publica tus propios diseños hechos en DrawMyMouse.")
    
    with st.expander("📤 Subir un archivo de Mouse (.ani / .cur / .ico / .png) a la comunidad"):
        with st.form("upload_community_form"):
            comm_file = st.file_uploader("Elige tu imagen de cursor:", type=["ani", "cur", "ico", "png"])
            comm_title = st.text_input("Título del Cursor:", "Neon Pointer")
            comm_author = st.text_input("Autor:", "DiseñadorWeb")
            submit_upload = st.form_submit_button("Subir a la Comunidad")
            
            if submit_upload and comm_file:
                upload_img = Image.open(comm_file).convert("RGBA").resize((32, 32), Image.Resampling.NEAREST)
                
                st.session_state.community_cursors.append({
                    "title": comm_title,
                    "author": comm_author,
                    "ani_bytes": image_to_ani_bytes(upload_img),
                    "cur_bytes": image_to_cur_bytes(upload_img),
                    "ico_bytes": image_to_ico_bytes(upload_img),
                    "png_bytes": image_to_png_bytes(upload_img),
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
                    label="✨ .ANI (Recomendado)",
                    data=item['ani_bytes'],
                    file_name=f"{item['title'].lower().replace(' ', '_')}.ani",
                    mime="application/x-navi-animation",
                    key=f"dl_ani_{idx}",
                    use_container_width=True
                )
                st.download_button(
                    label="🖱️ .CUR",
                    data=item['cur_bytes'],
                    file_name=f"{item['title'].lower().replace(' ', '_')}.cur",
                    mime="image/x-win-bitmap",
                    key=f"dl_cur_{idx}",
                    use_container_width=True
                )
                st.download_button(
                    label="📁 .ICO (Carpetas)",
                    data=item['ico_bytes'],
                    file_name=f"{item['title'].lower().replace(' ', '_')}.ico",
                    mime="image/x-icon",
                    key=f"dl_ico_{idx}",
                    use_container_width=True
                )
                st.download_button(
                    label="🖼️ .PNG (Previsualización)",
                    data=item['png_bytes'],
                    file_name=f"{item['title'].lower().replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"dl_png_{idx}",
                    use_container_width=True
                )
                st.markdown("---")
