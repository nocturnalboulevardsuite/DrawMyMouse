# DrawMyMouse

---

<font color="#E53E3E">

## 🇪🇸 Español

### ¿Qué es DrawMyMouse?
DrawMyMouse es una aplicación web interactiva diseñada para la creación y conversión de cursores de ratón personalizados. Permite transformar imágenes existentes en archivos `.ico` y `.png` optimizados para el sistema o dibujar diseños píxel a píxel directamente en el navegador.

### Características principales
* **Conversión de imágenes:** Procesa archivos PNG, JPG y WebP para generar formatos compatibles con el sistema operativo.
* **Escalado Píxel-Perfect:** Utiliza interpolación por vecino más cercano (*nearest-neighbor*) para preservar la nitidez en resoluciones de 16px a 64px.
* **Lienzo interactivo:** Editor estilo píxel art para dibujar cursores desde cero.
* **Exportación CSS:** Genera automáticamente fragmentos de código Base64 para integración directa en desarrollo web.

### Instalación y uso
```bash
git clone [https://github.com/tu-usuario/DrawMyMouse.git](https://github.com/tu-usuario/DrawMyMouse.git)
cd DrawMyMouse
pip install -r requirements.txt
streamlit run app.py
