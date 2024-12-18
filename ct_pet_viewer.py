import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os
from PIL import Image, ImageTk
import numpy as np
import pydicom

def load_folder():
    folder_selected = filedialog.askdirectory()
    return folder_selected

def update_viewers():
    """Function to update viewers based on the current slice index."""
    global ct_images, pet_images, current_slice

    if ct_images:
        ct_image = ct_images[current_slice]
        ct_image = normalize_image(ct_image)
        ct_image_tk = ImageTk.PhotoImage(Image.fromarray(ct_image).resize((400, 400)))
        ct_viewer.configure(image=ct_image_tk)
        ct_viewer.image = ct_image_tk

    if pet_images:
        pet_image = pet_images[current_slice]
        pet_image = normalize_image(pet_image)
        pet_image_tk = ImageTk.PhotoImage(Image.fromarray(pet_image).resize((400, 400)))
        pet_viewer.configure(image=pet_image_tk)
        pet_viewer.image = pet_image_tk

def normalize_image(image):
    """Normalize image data to 0-255 range for display."""
    image = (image - np.min(image)) / (np.max(image) - np.min(image)) * 255
    return image.astype(np.uint8)

def on_slice_change(value):
    global current_slice
    current_slice = int(float(value))
    update_viewers()

def load_ct_images():
    global ct_images, slice_slider

    folder = load_folder()
    if folder:
        ct_images = load_dicom_images_from_folder(folder)
        slice_slider.configure(to=len(ct_images) - 1)
        update_viewers()

def load_pet_images():
    global pet_images, slice_slider

    folder = load_folder()
    if folder:
        pet_images = load_dicom_images_from_folder(folder)
        slice_slider.configure(to=len(pet_images) - 1)
        update_viewers()

def load_dicom_images_from_folder(folder):
    images = []
    for file_name in sorted(os.listdir(folder)):
        file_path = os.path.join(folder, file_name)
        try:
            dicom_file = pydicom.dcmread(file_path)
            image = dicom_file.pixel_array
            images.append(image)
        except Exception as e:
            print(f"Error loading DICOM file {file_name}: {e}")
    return images

# Initialize global variables
ct_images = []
pet_images = []
current_slice = 0

# Create main application window
root = tk.Tk()
root.title("CT and PET Scan Viewer")
root.geometry("1100x500")  # Set window size
root.resizable(False, False)
root.configure(bg="#A7BBEC")  # Set the background color of the main window

# Create frames for layout
control_frame = tk.Frame(root, bg="#A7BBEC", padx=10, pady=10)
control_frame.pack(side=tk.LEFT, fill=tk.Y)

viewer_frame = tk.Frame(root, bg="#A7BBEC", padx=10, pady=10)
viewer_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# CT Viewer
ct_label = tk.Label(viewer_frame, text="CT Scan", font=("Helvetica", 14, "bold"), bg="#A7BBEC")
ct_label.grid(row=0, column=0, padx=10, pady=(0, 10))
ct_viewer = tk.Label(viewer_frame, text="CT Viewer", bg="#A7BBEC", width=400, anchor="center")
ct_viewer.grid(row=1, column=0, padx=10, pady=10)

# PET Viewer
pet_label = tk.Label(viewer_frame, text="PET Scan", font=("Helvetica", 14, "bold"), bg="#A7BBEC", fg="#0A2342")
pet_label.grid(row=0, column=1, padx=10, pady=(0, 10))
pet_viewer = tk.Label(viewer_frame, text="PET Viewer", bg="#A7BBEC", width=400, anchor="center")
pet_viewer.grid(row=1, column=1, padx=10, pady=10)

image_path = "logo.png"  # Replace with your image file
image = Image.open(image_path)
image = image.resize((80, 80))
photo = ImageTk.PhotoImage(image)

image_label = tk.Label(control_frame, image=photo, bg="#A7BBEC")
image_label.pack(padx=10) 


# Slice Selector
slice_label = tk.Label(control_frame, text="OncoScope\nViewer", font=("Helvetica", 18, "bold"), bg="#A7BBEC", fg="#0A2342")
slice_label.pack(pady=10)

# Buttons to load images
ct_button = tk.Button(control_frame, text="Load CT Images", command=load_ct_images,font=("Helvetica", 11, "bold"), width="14", fg="#FFFFFF", bg="#0A2342")
ct_button.pack(pady=10)

pet_button = tk.Button(control_frame, text="Load PET Images", command=load_pet_images,font=("Helvetica", 11, "bold"),width="14", fg="#FFFFFF", bg="#0A2342")
pet_button.pack(pady=10)



slice_slider = tk.Scale(control_frame, from_=0, to=0, orient=tk.VERTICAL, command=on_slice_change,
                         bg="#FFFFFF",  # Background color of the slider
                         troughcolor="#0A2342",  # Color of the trough (the background bar)
                         fg="#0A2342",  # Color of the slider itself (the "thumb")
                         sliderlength=30)  # Length of the slider (you can adjust this as well)
slice_slider.pack(pady=20, fill=tk.Y)

root.mainloop()

