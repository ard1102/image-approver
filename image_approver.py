"""
ImageSorter - A tool for quickly sorting images through approval/disapproval.

Version: 1.0
Author: Qwen Code
License: MIT

This tool helps users quickly review large collections of images and sort them
into "approved" and "disapproved" categories using an intuitive UI with keyboard shortcuts.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from collections import deque

class ImageApprover:
    def __init__(self, root):
        self.root = root
        self.root.title("ApproveIT v2.0")
        self.root.geometry("1000x700")

        # Set a modern theme
        self.style = ttk.Style()
        self.theme = 'dark'  # Default theme

        # Initialize variables
        self.image_files = []
        self.current_index = 0
        self.approved_folder = ""
        self.disapproved_folder = ""
        self.original_folder = ""
        
        # Zoom variables
        self.zoom_factor = 0.4  # Start with 40% zoom
        self.zoom_step = 0.1
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Undo stack (max 10 operations)
        self.undo_stack = deque(maxlen=10)
        
        # Create UI
        self.create_widgets()
        
        # Bind keyboard events
        self.root.bind('<Left>', lambda event: self.disapprove_image())
        self.root.bind('<Right>', lambda event: self.approve_image())
        self.root.bind('<Up>', lambda event: self.previous_image())
        self.root.bind('<Down>', lambda event: self.next_image())
        self.root.bind('<z>', lambda event: self.undo_last_action())
        self.root.bind('<plus>', lambda event: self.zoom_in())
        self.root.bind('<minus>', lambda event: self.zoom_out())
        self.root.bind('<space>', lambda event: self.reset_zoom())
        self.root.bind('<KeyRelease-space>', lambda event: self.reset_zoom())

        self.apply_theme()

    def apply_theme(self):
        font_family = "Segoe UI" if os.name == 'nt' else "SF Pro" if os.name == 'posix' else "Arial"

        # Theme settings
        if self.theme == 'dark':
            bg_color = "#222222"
            fg_color = "#CCCCCC"
            header_fg_color = "#FFFFFF"
            btn_bg = "#333333"
            btn_fg = "white"
            btn_active_bg = "#555555"
            img_frame_bg = "#000000"
        else: # Light theme
            bg_color = "#F0F0F0"
            fg_color = "#333333"
            header_fg_color = "#000000"
            btn_bg = "#E1E1E1"
            btn_fg = "black"
            btn_active_bg = "#D1D1D1"
            img_frame_bg = "#FFFFFF"

        self.style.theme_use('clam')

        # General styles
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color, font=(font_family, 10))
        self.style.configure("Header.TLabel", font=(font_family, 14, "bold"), foreground=header_fg_color)

        # Button styles
        self.style.configure("TButton", padding=8, relief="flat", font=(font_family, 10), background=btn_bg, foreground=btn_fg)
        self.style.map("TButton",
            background=[('active', btn_active_bg)],
            foreground=[('active', btn_fg)]
        )

        # Approve/Disapprove button styles
        if self.theme == 'dark':
            approve_bg = "#2a7e2a"
            approve_active_bg = "#3a9e3a"
            disapprove_bg = "#a02c2c"
            disapprove_active_bg = "#c03c3c"
        else:
            approve_bg = "#90EE90"
            approve_active_bg = "#7CFC00"
            disapprove_bg = "#F08080"
            disapprove_active_bg = "#FF6347"

        self.style.configure("Approve.TButton", background=approve_bg, foreground='white')
        self.style.map("Approve.TButton", background=[('active', approve_active_bg)])

        self.style.configure("Disapprove.TButton", background=disapprove_bg, foreground='white')
        self.style.map("Disapprove.TButton", background=[('active', disapprove_active_bg)])
        
        # Apply background to root window
        self.root.configure(bg=bg_color)

        # Update existing widget colors
        if hasattr(self, 'image_frame'):
            self.image_frame.config(bg=img_frame_bg)
            self.canvas.config(bg=img_frame_bg)

    def toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.apply_theme()

    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Folder selection frame
        self.folder_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.select_btn = ttk.Button(self.folder_frame, text="📂 Select Folder", command=self.select_folder, style="TButton")
        self.select_btn.pack(side=tk.LEFT)

        self.theme_btn = ttk.Button(self.folder_frame, text="Toggle Theme", command=self.toggle_theme, style="TButton")
        self.theme_btn.pack(side=tk.LEFT, padx=(5,0))
        
        self.folder_label = ttk.Label(self.folder_frame, text="No folder selected", style="TLabel")
        self.folder_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Image name display
        self.image_name_label = ttk.Label(self.main_frame, text="", style="Header.TLabel")
        self.image_name_label.pack(pady=(0, 10))
        
        # Image display frame
        self.image_frame = tk.Frame(self.main_frame, relief='sunken', bd=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Canvas for image display
        self.canvas = tk.Canvas(self.image_frame, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Zoom controls
        self.zoom_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.zoom_frame.pack(pady=(0, 10))
        
        self.zoom_out_btn = ttk.Button(self.zoom_frame, text="－", command=self.zoom_out, style="TButton")
        self.zoom_out_btn.pack(side=tk.LEFT, padx=5)
        
        self.zoom_label = ttk.Label(self.zoom_frame, text="40%", style="TLabel")
        self.zoom_label.pack(side=tk.LEFT, padx=15)
        
        self.zoom_in_btn = ttk.Button(self.zoom_frame, text="＋", command=self.zoom_in, style="TButton")
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        self.nav_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.nav_frame.pack(pady=(0, 10))
        
        self.prev_btn = ttk.Button(self.nav_frame, text="↑", command=self.previous_image, style="TButton", state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(self.nav_frame, text="↓", command=self.next_image, style="TButton", state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.progress_frame.pack(fill=tk.X, pady=(0, 15))
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X, expand=True, side=tk.LEFT)
        self.progress_label = ttk.Label(self.progress_frame, text=" 0/0", style="TLabel")
        self.progress_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons frame
        self.control_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.control_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.undo_btn = ttk.Button(self.control_frame, text="↩ Undo", command=self.undo_last_action, style="TButton", state=tk.DISABLED)
        self.undo_btn.pack(side=tk.LEFT)
        
        # Spacer
        ttk.Frame(self.control_frame).pack(side=tk.LEFT, expand=True)
        
        self.disapprove_btn = ttk.Button(self.control_frame, text="❌ Disapprove", command=self.disapprove_image, style="Disapprove.TButton", state=tk.DISABLED)
        self.disapprove_btn.pack(side=tk.LEFT)
        
        self.approve_btn = ttk.Button(self.control_frame, text="✔ Approve", command=self.approve_image, style="Approve.TButton", state=tk.DISABLED)
        self.approve_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Bind hover events to all buttons
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.original_folder = folder_path
            self.folder_label.config(text=folder_path)
            
            # Create approved and disapproved folders
            self.approved_folder = os.path.join(folder_path, "approved")
            self.disapproved_folder = os.path.join(folder_path, "disapproved")
            
            os.makedirs(self.approved_folder, exist_ok=True)
            os.makedirs(self.disapproved_folder, exist_ok=True)
            
            # Load images
            self.load_images()
            
    def load_images(self):
        # Get all files in the folder
        all_files = [f for f in os.listdir(self.original_folder) 
                    if os.path.isfile(os.path.join(self.original_folder, f))]
        
        # Filter for image files using Pillow
        self.image_files = []
        for file in all_files:
            file_path = os.path.join(self.original_folder, file)
            try:
                # Try to open the image with Pillow to verify it's a valid image
                with Image.open(file_path) as img:
                    # Exclude files already in approved/disapproved folders
                    if "approved" not in file_path and "disapproved" not in file_path:
                        self.image_files.append(file)
            except Exception:
                # Not a valid image file, skip it
                continue
        
        if not self.image_files:
            messagebox.showinfo("No Images", "No valid image files found in the selected folder.")
            return
            
        self.current_index = 0
        self.progress_bar['maximum'] = len(self.image_files)
        self.progress_bar['value'] = 0
        # Don't reset zoom when loading new folder - keep the default 40%
        self.display_image()
        
        # Enable buttons
        self.disapprove_btn.state(['!disabled'])
        self.approve_btn.state(['!disabled'])
        self.update_navigation_buttons()
        
        self.update_progress()
        
    def display_image(self):
        if not self.image_files:
            return
            
        # Clear previous image
        self.canvas.delete("all")
        
        # Get current image filename
        current_image = self.image_files[self.current_index]
        
        # Display the image filename
        self.image_name_label.config(text=current_image)
        
        # Load and display current image
        image_path = os.path.join(self.original_folder, current_image)
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Apply zoom
            width, height = image.size
            new_width = int(width * self.zoom_factor)
            new_height = int(height * self.zoom_factor)
            image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(image)
            
            # Center image on canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # If window dimensions are not properly set yet, use reasonable defaults
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 700
                canvas_height = 400
                
            x = max(0, (canvas_width - new_width) // 2)
            y = max(0, (canvas_height - new_height) // 2)
            
            # Draw image on canvas
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
            
            # Update zoom label
            self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {str(e)}")
            
        self.update_progress()
        self.update_navigation_buttons()
        
    def zoom_in(self):
        if not self.image_files:
            return
            
        # Don't allow zooming in above 500%
        if self.zoom_factor < self.max_zoom:
            self.zoom_factor += self.zoom_step
        else:
            self.zoom_factor = self.max_zoom
            
        self.display_image()
        
    def zoom_out(self):
        if not self.image_files:
            return
            
        # Don't allow zooming out below 10%
        if self.zoom_factor > self.min_zoom:
            self.zoom_factor -= self.zoom_step
        else:
            self.zoom_factor = self.min_zoom
            
        self.display_image()
        
    def reset_zoom(self):
        if not self.image_files:
            return
            
        self.zoom_factor = 0.4  # Reset to 40% instead of 100%
        self.display_image()
        
    def previous_image(self):
        if not self.image_files or self.current_index <= 0:
            return
            
        self.current_index -= 1
        # Don't reset zoom when navigating - keep current zoom level
        self.display_image()
        
    def next_image(self):
        if not self.image_files or self.current_index >= len(self.image_files) - 1:
            return
            
        self.current_index += 1
        # Don't reset zoom when navigating - keep current zoom level
        self.display_image()
        
    def update_navigation_buttons(self):
        # Enable/disable navigation buttons based on current position
        if not self.image_files:
            self.prev_btn.state(['disabled'])
            self.next_btn.state(['disabled'])
            return
            
        # Previous button
        if self.current_index > 0:
            self.prev_btn.state(['!disabled'])
        else:
            self.prev_btn.state(['disabled'])
            
        # Next button
        if self.current_index < len(self.image_files) - 1:
            self.next_btn.state(['!disabled'])
        else:
            self.next_btn.state(['disabled'])
            
    def approve_image(self):
        if not self.image_files:
            return
            
        self.move_image(self.approved_folder, "approved")
        
    def disapprove_image(self):
        if not self.image_files:
            return
            
        self.move_image(self.disapproved_folder, "disapproved")
        
    def move_image(self, destination_folder, action):
        if not self.image_files:
            return
            
        # Get current image
        current_image = self.image_files[self.current_index]
        source_path = os.path.join(self.original_folder, current_image)
        destination_path = os.path.join(destination_folder, current_image)
        
        try:
            # Save operation to undo stack
            self.undo_stack.append({
                'file': current_image,
                'from': self.original_folder,
                'to': destination_folder,
                'action': action
            })
            
            # Enable undo button
            self.undo_btn.state(['!disabled'])
            
            # Move file
            shutil.move(source_path, destination_path)
            
            # Don't reset zoom - keep current zoom level
            
            # Remove from list
            self.image_files.pop(self.current_index)
            
            # Adjust index if needed
            if self.current_index >= len(self.image_files) and self.image_files:
                self.current_index = len(self.image_files) - 1
                
            # Display next image or finish
            if self.image_files:
                self.display_image()
            else:
                self.canvas.delete("all")
                self.image_name_label.config(text="")
                self.progress_label.config(text="All images processed!")
                self.progress_bar['value'] = self.progress_bar['maximum']
                self.disapprove_btn.state(['disabled'])
                self.approve_btn.state(['disabled'])
                self.undo_btn.state(['disabled'])
                self.prev_btn.state(['disabled'])
                self.next_btn.state(['disabled'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not move file: {str(e)}")
            
    def undo_last_action(self):
        if not self.undo_stack:
            return
            
        # Get last operation
        last_operation = self.undo_stack.pop()
        
        try:
            # Move file back
            source_path = os.path.join(last_operation['to'], last_operation['file'])
            destination_path = os.path.join(last_operation['from'], last_operation['file'])
            shutil.move(source_path, destination_path)
            
            # Add back to image list
            self.image_files.append(last_operation['file'])
            
            # Set current index to the restored image
            self.current_index = len(self.image_files) - 1
            
            # Don't reset zoom - keep current zoom level
            
            # Display image
            self.display_image()
            
            # Re-enable buttons if needed
            if 'disabled' in self.disapprove_btn.state():
                self.disapprove_btn.state(['!disabled'])
                self.approve_btn.state(['!disabled'])
                self.update_navigation_buttons()
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not undo operation: {str(e)}")
            
        # Disable undo button if stack is empty
        if not self.undo_stack:
            self.undo_btn.state(['disabled'])
            
    def update_progress(self):
        total_processed = len(self.undo_stack)
        total_images = len(self.image_files) + total_processed
        remaining = len(self.image_files)
        
        if total_images > 0:
            progress_value = (total_processed / total_images) * 100
            self.progress_bar['value'] = progress_value
        else:
            self.progress_bar['value'] = 0

        self.progress_label.config(text=f" {remaining}/{total_images}")

def main():
    root = tk.Tk()
    app = ImageApprover(root)
    root.mainloop()

if __name__ == "__main__":
    main()
