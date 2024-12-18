import tkinter as tk
import subprocess
import sys
from PIL import Image, ImageTk


def open_ct_pet_viewer():
    """Run the CT and PET viewer module."""
    subprocess.Popen([sys.executable, "ct_pet_viewer.py"], stdout=sys.stdout, stderr=sys.stderr)

def open_placeholder_page():
    """Run the placeholder module."""
    subprocess.Popen([sys.executable, "placeholder_page.py"], stdout=sys.stdout, stderr=sys.stderr)


# Main application window
root = tk.Tk()
root.title("Main Page")
root.geometry("600x400")
root.resizable(False, False)
root.configure(bg="#A7BBEC")
#otro color  BCF2DE

# Create a frame for horizontal layout
content_frame = tk.Frame(root, bg="#A7BBEC")
content_frame.pack(pady=20)  # Add vertical padding for the frame

# Load and display the image
image_path = "logo.png"  # Replace with your image file
image = Image.open(image_path)
image = image.resize((150, 150))
photo = ImageTk.PhotoImage(image)

image_label = tk.Label(content_frame, image=photo, bg="#A7BBEC")
image_label.pack(side=tk.LEFT, padx=10)  # Align image to the left with horizontal padding

# Text content
text_frame = tk.Frame(content_frame, bg="#A7BBEC")
text_frame.pack(side=tk.LEFT, padx=10)  # Align text to the right of the image

header_label = tk.Label(text_frame, text="OncoScope", font=("Helvetica", 26, "bold"), bg="#A7BBEC", fg="#0A2342")
header_label.pack(anchor="w")  # Align text to the left within the text frame

sub_label = tk.Label(
    text_frame,
    text="Captures the focus on cancer imaging \nand detailed evaluation",
    font=("Helvetica", 12),
    bg="#A7BBEC",
    justify="left", 
    fg="#0A2342"
)
sub_label.pack(anchor="w")  # Align text to the left within the text frame

# Buttons


button_placeholder = tk.Button(root, text="Segmentation Tool", command=open_placeholder_page, font=("Helvetica", 10, "bold"), height=2, width=25, fg="#FFFFFF", bg="#0A2342")
button_placeholder.pack(pady=20)
button_ct_pet = tk.Button(root, text="CT and PET Viewer", command=open_ct_pet_viewer,font=("Helvetica", 10, "bold"), height=2, width=25, fg="#FFFFFF", bg="#0A2342")
button_ct_pet.pack(pady=20)

root.mainloop()
