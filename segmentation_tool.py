import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel
from tkcalendar import Calendar
from PIL import Image, ImageTk
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
import tempfile


ruta_modelo = r'C:\Users\memil\Documents\python\Segmentacion_cancer_mama.h5'
model = load_model(ruta_modelo)

global_mask = None
imagen_original = None
imagen_prediccion = None
imagen_overlay = None


def cargar_imagen():
    global global_mask, imagen_original, imagen_prediccion, imagen_overlay
    archivo = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if archivo:
        try:
            imagen_original_pil = Image.open(archivo)
            imagen_original_pil.thumbnail((300, 300))
            img_tk = ImageTk.PhotoImage(imagen_original_pil)
            lbl_imagen_cargada.configure(image=img_tk, text="")
            lbl_imagen_cargada.image = img_tk

            imagen_preprocesada, imagen_para_overlay = preprocesar_imagen(archivo)
            if imagen_preprocesada is not None:
                prediccion = model.predict(imagen_preprocesada)
                global_mask = np.squeeze(prediccion, axis=-1)

                imagen_original = imagen_para_overlay
                imagen_prediccion = procesar_prediccion(global_mask, imagen_para_overlay)
                imagen_overlay = crear_overlay(global_mask, imagen_para_overlay)

                mostrar_resultado(imagen_prediccion, lbl_resultado)
                mostrar_resultado(imagen_overlay, lbl_overlay)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process the image: {str(e)}")


def preprocesar_imagen(ruta):
    imagen = cv2.imread(ruta)
    if imagen is not None:
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        imagen_redimensionada = cv2.resize(imagen_rgb, (256, 256))
        imagen_array = np.expand_dims(imagen_redimensionada, axis=0) / 255.0
        return imagen_array, imagen_rgb
    return None, None

def procesar_prediccion(prediccion, imagen_original):
    print("Shape of prediction before squeeze:", prediccion.shape)

    prediccion = np.squeeze(prediccion)


    prediccion = (prediccion * 255).astype(np.uint8)

    h, w = imagen_original.shape[:2]
    return cv2.resize(prediccion, (w, h), interpolation=cv2.INTER_NEAREST)



def crear_overlay(prediccion, imagen_original):
    prediccion = np.squeeze(prediccion) 
    print("Shape of prediction before resize:", prediccion.shape)
    h, w = imagen_original.shape[:2]
    prediccion_resized = cv2.resize(prediccion, (w, h), interpolation=cv2.INTER_NEAREST)
    print("Shape of prediction after resize:", prediccion_resized.shape)


    binary_mask = prediccion_resized > 0.5
    overlay = imagen_original.copy()
    overlay[binary_mask] = [20, 255, 247]
    
    return overlay


def mostrar_resultado(imagen, label):
    imagen_resized = cv2.resize(imagen, (300, 300), interpolation=cv2.INTER_AREA)
    imagen_pil = Image.fromarray(imagen_resized)
    img_tk = ImageTk.PhotoImage(imagen_pil)
    label.configure(image=img_tk)
    label.image = img_tk


def guardar_pdf():
    if not (imagen_original is not None and imagen_prediccion is not None and imagen_overlay is not None):
        messagebox.showwarning("Warning", "No images available to save.")
        return

    filetypes = [("PDF files", "*.pdf")]
    filepath = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".pdf", initialfile="report.pdf")
    if not filepath:
        return

    name = simpledialog.askstring("Input", "Enter patient's name:")
    if not name:
        return

    top = Toplevel()
    top.title("Select Date")
    cal = Calendar(top, date_pattern='dd/MM/yyyy')
    cal.pack(pady=10)

    def confirm_date():
        nonlocal date
        date = cal.get_date()
        top.destroy()

    date = None
    btn_select = tk.Button(top, text="Confirm", command=confirm_date)
    btn_select.pack(pady=5)
    top.wait_window()

    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Segmentation Results")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Patient Name: {name}")
    c.drawString(100, 710, f"Date: {date}")

    temp_files = []
    for idx, img_array in enumerate([imagen_original, imagen_prediccion, imagen_overlay]):
        temp_path = os.path.join(tempfile.gettempdir(), f"temp_{idx}.png")
        Image.fromarray(img_array).save(temp_path)
        temp_files.append(temp_path)

    y_positions = [480, 280, 80] 
    titles = ["Original Image", "Prediction", "Overlay"]
    image_width, image_height = 180, 180 

    for i, (temp_path, title) in enumerate(zip(temp_files, titles)):

        c.drawString(100, y_positions[i] + image_height + 10, title) 

        img = ImageReader(temp_path)
        c.drawImage(img, 100, y_positions[i], width=image_width, height=image_height, preserveAspectRatio=True)

    c.save()

    for temp_path in temp_files:
        os.remove(temp_path)

    messagebox.showinfo("Success", f"PDF saved successfully at: {filepath}")



# MAIN
root = tk.Tk()
root.title("OncoScope Segmentation Tool")
root.geometry("1000x600")
root.configure(bg="#A7BBEC")


header_label = tk.Label(root, text="OncoScope Segmentation Tool", font=("Helvetica", 24, "bold"), bg="#A7BBEC", fg="#0A2342")
header_label.pack(pady=20)

frame_text = tk.Frame(root, bg="#A7BBEC")
frame_text.pack(pady=20)
txt_imagen_cargada = tk.Label(frame_text, text="Original Image", font=("Helvetica", 12), bg="#A7BBEC", fg="#0A2342")
txt_imagen_cargada.pack(side=tk.LEFT, padx=100)
txt_resultado = tk.Label(frame_text, text="Model Result", font=("Helvetica", 12), bg="#A7BBEC", fg="#0A2342")
txt_resultado.pack(side=tk.LEFT, padx=100)
txt_overlay = tk.Label(frame_text, text="Overlay Result", font=("Helvetica", 12), bg="#A7BBEC", fg="#0A2342")
txt_overlay.pack(side=tk.LEFT, padx=100)

frame_imagenes = tk.Frame(root, bg="#A7BBEC")
frame_imagenes.pack(pady=20)
lbl_imagen_cargada = tk.Label(frame_imagenes, text="Original Image", font=("Helvetica", 12), bg="#A7BBEC", fg="#A7BBEC")
lbl_imagen_cargada.pack(side=tk.LEFT, padx=10)
lbl_resultado = tk.Label(frame_imagenes, text="Model Result", font=("Helvetica", 12), bg="#A7BBEC", fg="#A7BBEC")
lbl_resultado.pack(side=tk.LEFT, padx=10)
lbl_overlay = tk.Label(frame_imagenes, text="Overlay: Original + Segmentation", font=("Helvetica", 12), bg="#A7BBEC", fg="#A7BBEC")
lbl_overlay.pack(side=tk.LEFT, padx=10)
frame_botones = tk.Frame(root, bg="#A7BBEC")
frame_botones.pack(pady=20)

btn_cargar_imagen = tk.Button(frame_botones, text="Load Image", command=cargar_imagen, font=("Helvetica", 12, "bold"), height=2, width=20, fg="#FFFFFF", bg="#0A2342")
btn_cargar_imagen.pack(side=tk.LEFT,padx=10)
btn_guardar_mask = tk.Button(frame_botones, text="Save Report", command=guardar_pdf, font=("Helvetica", 12, "bold"), height=2, width=20, fg="#FFFFFF", bg="#0A2342")
btn_guardar_mask.pack(side=tk.LEFT,padx=10)

root.mainloop()