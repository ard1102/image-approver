"""
ImageSorter - A tool for quickly sorting images through approval/disapproval.

Version: 1.0
Author: Qwen Code
License: MIT

This tool helps users quickly review large collections of images and sort them
into "approved" and "disapproved" categories using an intuitive UI with keyboard shortcuts.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from collections import deque

class ImageApprover:
    def __init__(self, root):
        self.root = root
        self.root.title("ApproveIT v1.0")
        self.root.geometry("800x600")
        
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
        
    def create_widgets(self):
        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Folder selection frame
        self.folder_frame = tk.Frame(self.main_frame)
        self.folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.select_btn = tk.Button(self.folder_frame, text="Select Folder", command=self.select_folder)
        self.select_btn.pack(side=tk.LEFT)
        
        self.folder_label = tk.Label(self.folder_frame, text="No folder selected")
        self.folder_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Image name display
        self.image_name_label = tk.Label(self.main_frame, text="", font=("Arial", 10, "bold"))
        self.image_name_label.pack(pady=(0, 5))
        
        # Image display frame (no scrollbars, constrain image to window)
        self.image_frame = tk.Frame(self.main_frame, bg='white', relief='sunken', bd=1)
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for image display with fixed size
        self.canvas = tk.Canvas(self.image_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Zoom controls
        self.zoom_frame = tk.Frame(self.main_frame)
        self.zoom_frame.pack(pady=(5, 0))
        
        self.zoom_out_btn = tk.Button(self.zoom_frame, text="Zoom Out (-)", command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT)
        
        self.zoom_label = tk.Label(self.zoom_frame, text="40%")
        self.zoom_label.pack(side=tk.LEFT, padx=10)
        
        self.zoom_in_btn = tk.Button(self.zoom_frame, text="Zoom In (+)", command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT)
        
        # Navigation buttons
        self.nav_frame = tk.Frame(self.main_frame)
        self.nav_frame.pack(pady=(5, 0))
        
        self.prev_btn = tk.Button(self.nav_frame, text="Previous (↑)", command=self.previous_image, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(self.nav_frame, text="Next (↓)", command=self.next_image, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Progress label
        self.progress_label = tk.Label(self.main_frame, text="0/0 images processed")
        self.progress_label.pack(pady=(5, 0))
        
        # Control buttons frame
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.undo_btn = tk.Button(self.control_frame, text="Undo (Z)", command=self.undo_last_action, state=tk.DISABLED)
        self.undo_btn.pack(side=tk.LEFT)
        
        # Spacer
        tk.Frame(self.control_frame).pack(side=tk.LEFT, expand=True)
        
        self.disapprove_btn = tk.Button(self.control_frame, text="Disapprove (←)", command=self.disapprove_image, state=tk.DISABLED)
        self.disapprove_btn.pack(side=tk.LEFT)
        
        self.approve_btn = tk.Button(self.control_frame, text="Approve (→)", command=self.approve_image, state=tk.DISABLED)
        self.approve_btn.pack(side=tk.LEFT, padx=(5, 0))
        
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
        # Don't reset zoom when loading new folder - keep the default 40%
        self.display_image()
        
        # Enable buttons
        self.disapprove_btn.config(state=tk.NORMAL)
        self.approve_btn.config(state=tk.NORMAL)
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
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            return
            
        # Previous button
        if self.current_index > 0:
            self.prev_btn.config(state=tk.NORMAL)
        else:
            self.prev_btn.config(state=tk.DISABLED)
            
        # Next button
        if self.current_index < len(self.image_files) - 1:
            self.next_btn.config(state=tk.NORMAL)
        else:
            self.next_btn.config(state=tk.DISABLED)
            
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
            self.undo_btn.config(state=tk.NORMAL)
            
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
                self.disapprove_btn.config(state=tk.DISABLED)
                self.approve_btn.config(state=tk.DISABLED)
                self.undo_btn.config(state=tk.DISABLED)  # Also disable undo when no images left
                self.prev_btn.config(state=tk.DISABLED)
                self.next_btn.config(state=tk.DISABLED)
                
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
            if self.disapprove_btn.cget('state') == 'disabled':
                self.disapprove_btn.config(state=tk.NORMAL)
                self.approve_btn.config(state=tk.NORMAL)
                self.update_navigation_buttons()
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not undo operation: {str(e)}")
            
        # Disable undo button if stack is empty
        if not self.undo_stack:
            self.undo_btn.config(state=tk.DISABLED)
            
    def update_progress(self):
        total_processed = len(self.undo_stack)
        total_images = len(self.image_files) + total_processed
        remaining = len(self.image_files)
        
        self.progress_label.config(text=f"{remaining}/{total_images} images remaining")

def main():
    root = tk.Tk()
    app = ImageApprover(root)
    root.mainloop()

if __name__ == "__main__":
    main()
