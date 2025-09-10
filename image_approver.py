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
        
        # Select Folder button style (blue color)
        if self.theme == 'dark':
            select_folder_bg = "#1e3a8a"
            select_folder_active_bg = "#2563eb"
        else:
            select_folder_bg = "#3b82f6"
            select_folder_active_bg = "#2563eb"
            
        self.style.configure("SelectFolder.TButton", background=select_folder_bg, foreground='white', font=(font_family, 10, "bold"))
        self.style.map("SelectFolder.TButton", background=[('active', select_folder_active_bg)])
        
        # Canvas toggle styling is handled in draw_toggle method
        
        # Apply background to root window
        self.root.configure(bg=bg_color)

        # Update existing widget colors
        if hasattr(self, 'image_frame'):
            self.image_frame.config(bg=img_frame_bg)
            self.canvas.config(bg=img_frame_bg)
            
        # Update canvas toggle if it exists
        if hasattr(self, 'toggle_canvas'):
            self.update_canvas_toggle()

    def toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.apply_theme()

    def create_canvas_toggle(self):
        """Create a modern Canvas-based toggle switch"""
        # Create canvas for toggle switch
        self.toggle_canvas = tk.Canvas(
            self.folder_frame, 
            width=60, 
            height=30, 
            highlightthickness=0,
            relief='flat',
            bd=0
        )
        
        # Initialize toggle state
        self.toggle_state = self.theme == 'dark'
        
        # Draw initial toggle
        self.draw_toggle()
        
        # Bind click event
        self.toggle_canvas.bind("<Button-1>", self.on_toggle_click)
        
    def draw_toggle(self):
        """Draw the toggle switch on canvas with moon/sun icons"""
        self.toggle_canvas.delete("all")
        
        # Enhanced colors based on current theme and state
        if self.theme == 'dark':
            bg_color = "#2d2d2d"
            track_on = "#1a5f5a"  # Darker teal for better contrast
            track_off = "#3a3a3a"
            thumb_color = "#f8f9fa"
            thumb_shadow = "#1a1a1a"
            icon_color = "#ffd700"  # Gold for moon
        else:
            bg_color = "#f0f0f0"
            track_on = "#20b2aa"  # Brighter teal for light theme
            track_off = "#d1d5db"
            thumb_color = "#ffffff"
            thumb_shadow = "#9ca3af"
            icon_color = "#f59e0b"  # Amber for sun
            
        # Set canvas background
        self.toggle_canvas.configure(bg=bg_color)
        
        # Draw track shadow for depth
        track_color = track_on if self.toggle_state else track_off
        self.create_rounded_rect(
            self.toggle_canvas, 6, 9, 56, 23, 7, fill=thumb_shadow, outline=""
        )
        
        # Draw main track
        self.track = self.create_rounded_rect(
            self.toggle_canvas, 5, 8, 55, 22, 7, fill=track_color, outline=""
        )
        
        # Draw thumb shadow for depth
        thumb_x = 42 if self.toggle_state else 18
        self.toggle_canvas.create_oval(
            thumb_x-7, 7, thumb_x+9, 25, 
            fill=thumb_shadow, outline=""
        )
        
        # Draw main thumb
        self.thumb = self.toggle_canvas.create_oval(
            thumb_x-8, 6, thumb_x+8, 24, 
            fill=thumb_color, outline="#e5e7eb", width=1
        )
        
        # Draw moon/sun icon on the thumb
        if self.toggle_state:  # Dark theme - show moon
            self.draw_moon_icon(thumb_x, 15, icon_color)
        else:  # Light theme - show sun
            self.draw_sun_icon(thumb_x, 15, icon_color)
        
    def draw_moon_icon(self, center_x, center_y, color):
        """Draw an enhanced crescent moon icon"""
        # Main moon circle with subtle gradient effect
        moon_radius = 4
        # Draw moon base
        self.toggle_canvas.create_oval(
            center_x - moon_radius, center_y - moon_radius,
            center_x + moon_radius, center_y + moon_radius,
            fill=color, outline=""
        )
        
        # Add moon highlight
        self.toggle_canvas.create_oval(
            center_x - moon_radius + 1, center_y - moon_radius + 1,
            center_x + moon_radius - 1, center_y + moon_radius - 1,
            fill="#fff8dc", outline=""
        )
        
        # Create crescent by overlaying a smaller circle
        overlay_x = center_x + 2.5
        overlay_radius = 3.2
        overlay_color = "#f8f9fa" if self.theme == 'dark' else "#f0f0f0"
        self.toggle_canvas.create_oval(
            overlay_x - overlay_radius, center_y - overlay_radius,
            overlay_x + overlay_radius, center_y + overlay_radius,
            fill=overlay_color, outline=""
        )
        
        # Add small stars around moon
        star_positions = [(-2, -3), (3, -2), (-1, 3)]
        for sx, sy in star_positions:
            star_x, star_y = center_x + sx, center_y + sy
            self.toggle_canvas.create_text(
                star_x, star_y, text="✦", fill="#ffd700", font=("Arial", 4)
            )
    
    def draw_sun_icon(self, center_x, center_y, color):
        """Draw an enhanced sun icon with rays"""
        import math
        
        # Draw sun rays first (behind the center)
        ray_length = 2.5
        ray_distance = 4
        ray_color = "#fbbf24"  # Bright yellow for rays
        
        for i in range(8):
            angle = i * math.pi / 4  # 45 degrees apart
            # Inner point (start of ray)
            x1 = center_x + ray_distance * math.cos(angle)
            y1 = center_y + ray_distance * math.sin(angle)
            # Outer point (end of ray)
            x2 = center_x + (ray_distance + ray_length) * math.cos(angle)
            y2 = center_y + (ray_distance + ray_length) * math.sin(angle)
            
            self.toggle_canvas.create_line(
                x1, y1, x2, y2, fill=ray_color, width=2, capstyle="round"
            )
        
        # Sun center circle with gradient effect
        sun_radius = 3.5
        # Draw sun base
        self.toggle_canvas.create_oval(
            center_x - sun_radius, center_y - sun_radius,
            center_x + sun_radius, center_y + sun_radius,
            fill=color, outline=""
        )
        
        # Add sun highlight for 3D effect
        self.toggle_canvas.create_oval(
            center_x - sun_radius + 1, center_y - sun_radius + 1,
            center_x + sun_radius - 1, center_y + sun_radius - 1,
            fill="#fef3c7", outline=""
        )
        
        # Add inner glow
        self.toggle_canvas.create_oval(
            center_x - 2, center_y - 2,
            center_x + 2, center_y + 2,
            fill="#fffbeb", outline=""
        )
    
    def create_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle on canvas"""
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])
        return canvas.create_polygon(points, smooth=True, **kwargs)
        
    def on_toggle_click(self, event):
        """Handle toggle click event with animation"""
        self.toggle_state = not self.toggle_state
        self.animate_toggle()
        self.toggle_theme()
        
    def animate_toggle(self):
        """Animate the toggle switch transition"""
        # Get current and target positions
        current_x = 18 if not self.toggle_state else 42
        target_x = 42 if self.toggle_state else 18
        
        # Animation parameters
        steps = 8
        step_size = (target_x - current_x) / steps
        delay = 20  # milliseconds
        
        # Animate the thumb movement
        self.animate_step(current_x, target_x, step_size, steps, 0)
        
    def animate_step(self, current_x, target_x, step_size, total_steps, current_step):
        """Perform one step of the animation"""
        if current_step >= total_steps:
            # Animation complete, draw final state
            self.draw_toggle()
            return
            
        # Calculate new position
        new_x = current_x + (step_size * current_step)
        
        # Update track color during animation
        if self.theme == 'dark':
            track_on = "#2a9d8f"
            track_off = "#404040"
            thumb_color = "#ffffff"
        else:
            track_on = "#2a9d8f"
            track_off = "#cccccc"
            thumb_color = "#ffffff"
            
        # Interpolate track color
        progress = current_step / total_steps
        if self.toggle_state:
            # Transitioning to ON
            track_color = self.interpolate_color(track_off, track_on, progress)
        else:
            # Transitioning to OFF
            track_color = self.interpolate_color(track_on, track_off, progress)
            
        # Clear and redraw
        self.toggle_canvas.delete("all")
        
        # Set canvas background
        bg_color = "#2d2d2d" if self.theme == 'dark' else "#f0f0f0"
        self.toggle_canvas.configure(bg=bg_color)
        
        # Draw track
        self.create_rounded_rect(
            self.toggle_canvas, 5, 8, 55, 22, 7, fill=track_color, outline=""
        )
        
        # Draw thumb at current position
        self.toggle_canvas.create_oval(
            new_x-8, 6, new_x+8, 24, 
            fill=thumb_color, outline="#dddddd", width=1
        )
        
        # Draw moon/sun icon on the moving thumb
        icon_color = "#ffd700" if self.theme == 'dark' else "#f59e0b"
        if self.toggle_state:  # Dark theme - show moon
            self.draw_moon_icon(new_x, 15, icon_color)
        else:  # Light theme - show sun
            self.draw_sun_icon(new_x, 15, icon_color)
        
        # Schedule next step
        self.toggle_canvas.after(20, lambda: self.animate_step(
            current_x, target_x, step_size, total_steps, current_step + 1
        ))
        
    def interpolate_color(self, color1, color2, progress):
        """Interpolate between two hex colors"""
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * progress)
        g = int(g1 + (g2 - g1) * progress)
        b = int(b1 + (b2 - b1) * progress)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def update_canvas_toggle(self):
        """Update toggle appearance after theme change"""
        self.toggle_state = self.theme == 'dark'
        self.draw_toggle()

    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Folder selection frame
        self.folder_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.select_btn = ttk.Button(self.folder_frame, text="📂 Select Folder", command=self.select_folder, style="SelectFolder.TButton")
        self.select_btn.pack(side=tk.LEFT)
        
        self.folder_label = ttk.Label(self.folder_frame, text="No folder selected", style="TLabel")
        self.folder_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Modern Canvas-based toggle switch positioned on the right
        self.create_canvas_toggle()
        self.toggle_canvas.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Image name display
        self.image_name_label = ttk.Label(self.main_frame, text="", style="Header.TLabel")
        self.image_name_label.pack(pady=(0, 10))

        # Rename frame
        self.rename_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.rename_frame.pack(pady=(0, 5))

        self.rename_entry = ttk.Entry(self.rename_frame, width=40)
        self.rename_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.rename_ext_label = ttk.Label(self.rename_frame, text="", style="TLabel")
        self.rename_ext_label.pack(side=tk.LEFT)

        self.rename_btn = ttk.Button(self.rename_frame, text="Rename", command=self.rename_image, style="TButton", state=tk.DISABLED)
        self.rename_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.rename_entry.bind("<Return>", lambda event: self.rename_image())

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
        
        # Populate rename entry
        name_base, name_ext = os.path.splitext(current_image)
        self.rename_entry.delete(0, tk.END)
        self.rename_entry.insert(0, name_base)
        self.rename_ext_label.config(text=name_ext)
        self.rename_btn.state(['!disabled'])

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
        
    def rename_image(self):
        if not self.image_files:
            return

        old_name_with_ext = self.image_files[self.current_index]
        old_name_base, ext = os.path.splitext(old_name_with_ext)

        new_name_base = self.rename_entry.get().strip()

        if not new_name_base:
            messagebox.showwarning("Invalid Name", "New name cannot be empty.")
            return

        if new_name_base == old_name_base:
            return

        new_name_with_ext = new_name_base + ext

        old_path = os.path.join(self.original_folder, old_name_with_ext)
        new_path = os.path.join(self.original_folder, new_name_with_ext)

        if os.path.exists(new_path):
            messagebox.showerror("Error", f"A file named {new_name_with_ext} already exists.")
            return

        try:
            os.rename(old_path, new_path)

            self.image_files[self.current_index] = new_name_with_ext

            self.undo_stack.append({
                'action': 'rename',
                'old_name': old_name_with_ext,
                'new_name': new_name_with_ext
            })
            self.undo_btn.state(['!disabled'])

            self.image_name_label.config(text=new_name_with_ext)

        except Exception as e:
            messagebox.showerror("Error", f"Could not rename file: {str(e)}")

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
                self.rename_btn.state(['disabled'])
                self.rename_entry.delete(0, tk.END)
                self.rename_ext_label.config(text="")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not move file: {str(e)}")
            
    def undo_last_action(self):
        if not self.undo_stack:
            return
            
        # Get last operation
        last_operation = self.undo_stack.pop()
        
        try:
            action = last_operation.get('action')

            if action == 'rename':
                # Undo a rename operation
                old_path = os.path.join(self.original_folder, last_operation['new_name'])
                new_path = os.path.join(self.original_folder, last_operation['old_name'])
                os.rename(old_path, new_path)

                # Find the index of the renamed file and update it
                try:
                    idx = self.image_files.index(last_operation['new_name'])
                    self.image_files[idx] = last_operation['old_name']
                except ValueError:
                    # If the file is not in the list, it might have been moved.
                    # We need to find it in the approved/disapproved folder.
                    # This case is complex. For now, we assume rename is only undone on the current image.
                    pass

                self.display_image()

            else: # This is a move operation
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
