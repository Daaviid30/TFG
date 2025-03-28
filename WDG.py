import dearpygui.dearpygui as dpg
from tkinter import filedialog
import tkinter as tk
import os
import asyncio
from main import main

# === Funciones ===

def select_file_callback():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Extensiones", "*.crx *.zip")])
    root.destroy()

    if file_path:
        dpg.set_value("selected_file", file_path)
        dpg.set_value("status_text", "Archivo seleccionado, listo para analizar.")
    else:
        dpg.set_value("status_text", "No se seleccionó ningún archivo.")

def execute_analysis():
    file_path = dpg.get_value("selected_file")
    if not file_path or not os.path.exists(file_path):
        dpg.set_value("status_text", "Error: Selecciona un archivo válido primero.")
        return

    # Aquí irá tu lógica de análisis
    dpg.set_value("status_text", "Analizando...")
    asyncio.run(main(file_path))
    # Simulación de análisis...
    dpg.set_value("status_text", "Análisis completado correctamente.")

# === Inicio ===

dpg.create_context()

# Fuente personalizada (Segoe UI de Windows)
with dpg.font_registry():
    try:
        default_font = dpg.add_font("C:\\Windows\\Fonts\\segoeui.ttf", 18)
    except:
        default_font = None

# Tema moderno y minimalista
with dpg.theme() as custom_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (235, 235, 235, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 60, 60, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (100, 100, 100, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (120, 120, 120, 255))

# Viewport
dpg.create_viewport(title="Analizador de Extensiones", width=1000, height=700, resizable=True)

# Ventana principal
with dpg.window(tag="main_window", no_title_bar=True, no_resize=True, no_move=True,
                pos=(0, 0), width=1000, height=700):
    with dpg.tab_bar():

        # TAB 1 - Análisis
        with dpg.tab(label="🔧 Análisis de Extensión"):
            dpg.add_spacer(height=20)
            dpg.add_text("Selecciona una extensión (.crx o .zip)", bullet=True)
            dpg.add_button(label="Seleccionar archivo", callback=select_file_callback, width=220)
            dpg.add_input_text(tag="selected_file", readonly=True, width=500, hint="Ruta del archivo")
            dpg.add_spacer(height=10)
            dpg.add_button(label="Ejecutar análisis", callback=execute_analysis, width=220)
            dpg.add_spacer(height=20)
            dpg.add_text("Estado:")
            dpg.add_text("Esperando archivo...", tag="status_text")

        # TAB 2 - Resultados
        with dpg.tab(label="Resultados del Análisis"):
            dpg.add_text("Aquí se mostrarán los resultados del análisis.")
            dpg.add_spacer(height=10)

# Auto-resize con el viewport
def resize_main_window():
    width = dpg.get_viewport_client_width()
    height = dpg.get_viewport_client_height()
    dpg.set_item_width("main_window", width)
    dpg.set_item_height("main_window", height)
    dpg.set_item_pos("main_window", (0, 0))

# Chequeo en loop
def check_viewport_resize():
    global last_w, last_h
    w = dpg.get_viewport_client_width()
    h = dpg.get_viewport_client_height()
    if w != last_w or h != last_h:
        resize_main_window()
        last_w, last_h = w, h

# === Lanzar UI ===
last_w, last_h = 0, 0
dpg.setup_dearpygui()

# Estilos y fuentes
dpg.bind_theme(custom_theme)
if default_font:
    dpg.bind_font(default_font)

resize_main_window()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    check_viewport_resize()
    dpg.render_dearpygui_frame()

dpg.destroy_context()
