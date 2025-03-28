import os
import shutil
import imagehash
import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

exact_duplicates = []
similar_images = []
current_list = []
current_index = 0

def get_image_hash(image_path):
    try:
        img = Image.open(image_path).convert("L")
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def calculate_similarity(hash1, hash2):
    return (1 - (hash1 - hash2) / len(hash1.hash)**2) * 100

def find_duplicates_and_similars(folder_path, threshold=70):
    global exact_duplicates, similar_images
    image_hashes = {}
    exact_duplicates = []
    similar_images = []
    found_images = False

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            img_hash = get_image_hash(file_path)
            if img_hash:
                found_images = True
                for existing_hash, existing_path in image_hashes.items():
                    similarity = calculate_similarity(img_hash, existing_hash)
                    if similarity == 100:
                        exact_duplicates.append((file_path, existing_path))
                    elif similarity >= threshold:
                        similar_images.append((file_path, existing_path, round(similarity, 2)))
                image_hashes[img_hash] = file_path

    if not found_images:
        messagebox.showwarning("Warning", "No valid images found in the selected folder!")

root = tk.Tk()
root.title("Duplicate Image Finder")
root.geometry("900x700")
root.configure(bg="#f0f0f0")

def display_image(image_path, label, text_label):
    img = Image.open(image_path)
    img.thumbnail((350, 350))
    img = ImageTk.PhotoImage(img)
    label.config(image=img)
    label.image = img
    text_label.config(text=os.path.basename(image_path))

def update_display():
    global current_index, current_list
    if current_list and 0 <= current_index < len(current_list):
        img1, img2, *sim = current_list[current_index]
        display_image(img1, img_label1, img_text1)
        display_image(img2, img_label2, img_text2)
        similarity_label.config(text=f"Similarity: {sim[0]}%" if sim else "Identical")

def next_image():
    global current_index
    if current_list and current_index < len(current_list) - 1:
        current_index += 1
        update_display()

def prev_image():
    global current_index
    if current_list and current_index > 0:
        current_index -= 1
        update_display()

def delete_image():
    global current_list, current_index
    if current_list:
        img1, img2, *sim = current_list[current_index]
        os.remove(img1)
        messagebox.showinfo("Deleted", f"Deleted: {img1}")
        current_list.pop(current_index)
        if current_index >= len(current_list):
            current_index = max(0, len(current_list) - 1)
        update_display()

def skip_image():
    next_image()

def select_folder():
    global current_list, current_index
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        find_duplicates_and_similars(folder_selected)
        choose_mode()

def choose_mode():
    global current_list, current_index
    def set_mode(mode):
        global current_list, current_index
        if mode == "exact":
            current_list = exact_duplicates
        else:
            current_list = similar_images
        
        if not current_list:
            messagebox.showwarning("Warning", "No matches found in the selected category!")
            return
        
        current_index = 0
        update_display()
        mode_window.destroy()

    mode_window = tk.Toplevel(root)
    mode_window.title("Choose Mode")
    tk.Label(mode_window, text="Which images do you want to check?", font=("Arial", 14)).pack(pady=10)
    tk.Button(mode_window, text="Exact Duplicates", command=lambda: set_mode("exact"), font=("Arial", 14), bg="#4CAF50", fg="white").pack(pady=5)
    tk.Button(mode_window, text="Similar Images", command=lambda: set_mode("similar"), font=("Arial", 14), bg="#2196F3", fg="white").pack(pady=5)

tk.Button(root, text="Select Folder", command=select_folder, font=("Arial", 16), bg="#FFC107", fg="black", padx=10, pady=5).pack(pady=10)

frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=20)

img_label1 = tk.Label(frame)
img_label1.grid(row=0, column=0, padx=10)
img_text1 = tk.Label(frame, text="", font=("Arial", 12))
img_text1.grid(row=1, column=0)

img_label2 = tk.Label(frame)
img_label2.grid(row=0, column=1, padx=10)
img_text2 = tk.Label(frame, text="", font=("Arial", 12))
img_text2.grid(row=1, column=1)

similarity_label = tk.Label(root, text="Similarity: ", font=("Arial", 16), bg="#f0f0f0")
similarity_label.pack(pady=10)

control_frame = tk.Frame(root, bg="#f0f0f0")
control_frame.pack(pady=20)

tk.Button(control_frame, text="⏪ Prev", command=prev_image, font=("Arial", 14), bg="#9E9E9E", fg="white", padx=10, pady=5).grid(row=0, column=0, padx=5)
tk.Button(control_frame, text="⏩ Next", command=next_image, font=("Arial", 14), bg="#9E9E9E", fg="white", padx=10, pady=5).grid(row=0, column=1, padx=5)
tk.Button(control_frame, text="🗑 Delete", command=delete_image, font=("Arial", 14), bg="#F44336", fg="white", padx=10, pady=5).grid(row=0, column=2, padx=5)
tk.Button(control_frame, text="➡ Skip", command=skip_image, font=("Arial", 14), bg="#607D8B", fg="white", padx=10, pady=5).grid(row=0, column=3, padx=5)

root.mainloop()
