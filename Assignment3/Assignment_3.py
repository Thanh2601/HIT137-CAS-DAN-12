import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Processing Application")
        self.root.geometry("800x600")  # Smaller initial window
        
        # Image storage
        self.original_image = None
        self.displayed_image = None
        self.cropped_image = None
        self.crop_rect = None
        
        # Crop coordinates
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.is_cropping = False
        
        # Dynamic resize variables
        self.is_resizing = False
        self.resize_start_x = None
        self.resize_start_y = None
        
        # Crop window
        self.crop_window = None
        self.crop_canvas = None
        
        # Effect flags
        self.is_gray = False
        self.is_blur = False
        self.is_inverted = False
        
        # Max display size
        self.MAX_DISPLAY_SIZE = 800
        
        # History for undo/redo
        self.history = []
        self.history_position = -1
        
        # Drawing settings
        self.brush_size = 2
        self.brush_color = "#000000"
        self.is_drawing = False
        self.last_x = None
        self.last_y = None
        
        # Image position on canvas
        self.image_x = None
        self.image_y = None
        self.image_width = None
        self.image_height = None
        
        self.setup_ui()
        self.bind_shortcuts()
        
        # Show welcome window after main window is ready
        self.root.after(100, self.show_welcome_window)
        
    def setup_ui(self):
        # Create menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open...", command=self.load_image, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        
        # Image menu
        self.image_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Image", menu=self.image_menu)
        
        # Resize submenu
        resize_menu = tk.Menu(self.image_menu, tearoff=0)
        self.image_menu.add_cascade(label="Resize", menu=resize_menu)
        resize_menu.add_command(label="Dialog Resize", command=self.open_resize_window, accelerator="Ctrl+R")
        resize_menu.add_command(label="Dynamic Resize", command=self.start_dynamic_resize, accelerator="Ctrl+D")
        
        self.image_menu.add_command(label="Crop", command=self.open_crop_window, accelerator="Ctrl+X")
        self.image_menu.add_separator()
        self.image_menu.add_command(label="Grayscale", command=self.apply_grayscale, accelerator="Ctrl+G")
        self.image_menu.add_command(label="Blur", command=self.apply_blur, accelerator="Ctrl+B")
        self.image_menu.add_command(label="Invert Colors", command=self.apply_invert, accelerator="Ctrl+I")
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
    def open_crop_window(self):
        if self.displayed_image is not None:
            # Create new window for cropping
            self.crop_window = tk.Toplevel(self.root)
            self.crop_window.title("Crop Image")
            self.crop_window.geometry("600x500")  # Smaller crop window
            
            # Create canvas in new window with white background
            self.crop_canvas = tk.Canvas(self.crop_window, bg='white')
            self.crop_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            
            # Store original image dimensions
            self.original_height, self.original_width = self.displayed_image.shape[:2]
            
            # Show current image in new canvas
            image = Image.fromarray(self.displayed_image)
            # Scale the image to fit the window while maintaining aspect ratio
            display_size = (580, 420)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Store scale factors for coordinate conversion
            self.scale_x = self.original_width / photo.width()
            self.scale_y = self.original_height / photo.height()
            
            # Center the image in the canvas
            x_center = (600 - photo.width()) // 2
            y_center = (500 - photo.height()) // 2
            self.crop_canvas.config(width=photo.width(), height=photo.height())
            self.crop_canvas.create_image(x_center, y_center, anchor=tk.NW, image=photo)
            self.crop_canvas.image = photo
            
            # Store canvas offset for coordinate conversion
            self.canvas_offset_x = x_center
            self.canvas_offset_y = y_center
            
            # Bind mouse events for cropping
            self.crop_canvas.bind("<ButtonPress-1>", self.start_crop)
            self.crop_canvas.bind("<B1-Motion>", self.update_crop)
            self.crop_canvas.bind("<ButtonRelease-1>", self.end_crop)
            
            # Add confirmation button
            ttk.Button(self.crop_window, text="Confirm Crop", command=self.confirm_crop).pack(side=tk.BOTTOM, pady=5)
            
    def start_crop(self, event):
        # Get coordinates relative to the crop canvas
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        
        # Create or update crop rectangle
        if self.crop_rect:
            self.crop_canvas.delete(self.crop_rect)
        self.crop_rect = self.crop_canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y, 
            self.crop_start_x, self.crop_start_y, 
            outline='red', width=2
        )
        self.is_cropping = True
        
    def update_crop(self, event):
        if self.is_cropping:
            # Update rectangle as mouse moves
            self.crop_canvas.coords(
                self.crop_rect,
                self.crop_start_x, self.crop_start_y,
                event.x, event.y
            )
            
    def end_crop(self, event):
        if self.is_cropping:
            # Just update the final coordinates but don't crop yet
            self.crop_end_x = event.x
            self.crop_end_y = event.y
            self.is_cropping = False
            
    def confirm_crop(self):
        if self.crop_rect:
            # Get coordinates from the rectangle
            x1, y1, x2, y2 = self.crop_canvas.coords(self.crop_rect)
            
            # Adjust coordinates for canvas offset
            x1 = (x1 - self.canvas_offset_x) * self.scale_x
            y1 = (y1 - self.canvas_offset_y) * self.scale_y
            x2 = (x2 - self.canvas_offset_x) * self.scale_x
            y2 = (y2 - self.canvas_offset_y) * self.scale_y
            
            # Ensure coordinates are within bounds and in correct order
            x1 = max(0, min(x1, self.original_width))
            y1 = max(0, min(y1, self.original_height))
            x2 = max(0, min(x2, self.original_width))
            y2 = max(0, min(y2, self.original_height))
            
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Convert to integers
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            
            # Create cropped image
            cropped = self.displayed_image[y1:y2, x1:x2].copy()
            
            # Show preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Crop Preview")
            preview_window.transient(self.root)
            
            # Create canvas for preview
            preview_canvas = tk.Canvas(preview_window, bg='white')
            preview_canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            
            # Convert image to PhotoImage
            image = Image.fromarray(cropped)
            # Scale the image to fit the window while maintaining aspect ratio
            display_size = (400, 300)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Center the image
            x_center = (400 - photo.width()) // 2
            y_center = (300 - photo.height()) // 2
            preview_canvas.create_image(x_center, y_center, anchor=tk.NW, image=photo)
            preview_canvas.image = photo
            
            def apply_crop():
                self.displayed_image = cropped
                self.original_image = cropped.copy()
                # Reset effect flags
                self.is_gray = False
                self.is_blur = False
                self.is_inverted = False
                # Update display
                self.update_canvas()
                self.add_to_history()
                preview_window.destroy()
                self.crop_window.destroy()
            
            def cancel_crop():
                preview_window.destroy()
            
            # Buttons
            button_frame = ttk.Frame(preview_window)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            ttk.Button(button_frame, text="Apply", command=apply_crop).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=cancel_crop).pack(side=tk.RIGHT, padx=5)
            
    def start_dynamic_resize(self):
        if self.displayed_image is None:
            return
            
        self.is_resizing = True
        self.resize_start_x = None
        self.resize_start_y = None
        
        # Store original dimensions and image
        self.original_width = self.displayed_image.shape[1]
        self.original_height = self.displayed_image.shape[0]
        self.resize_original = self.displayed_image.copy()
        
        # Create finish 
        self.finish_button = tk.Button(
            self.root,
            text="Finish Resize",
            command=self.finish_resize_button,
            bg='white',     # White background
            fg='black',     # Black text
            font=('Arial', 10),
            relief=tk.SOLID,
            padx=20,
            pady=5
        )
        
        # Position button at bottom center
        self.finish_button.pack(side=tk.BOTTOM, pady=10)
        
        # Bind mouse events
        self.canvas.bind("<Motion>", self.check_resize_area)
        self.canvas.bind("<Button-1>", self.start_resize_drag)
        self.canvas.bind("<B1-Motion>", self.resize_from_edge)
        self.canvas.bind("<ButtonRelease-1>", self.finish_drag)
        
    def finish_resize_button(self):
        """Called when finish button is clicked"""
        if hasattr(self, 'finish_button'):
            self.finish_button.destroy()
        self.finish_resize(None)
        
    def finish_drag(self, event):
        """Called when mouse is released during drag"""
        if self.drag_active:
            self.drag_active = False
            # Don't finish resize yet, wait for button click
            
    def finish_resize(self, event):
        """Complete the resize operation"""
        if not self.is_resizing:
            return
            
        self.is_resizing = False
        self.drag_active = False
        
        # Reset cursor
        self.canvas.config(cursor="arrow")
        
        # Remove finish button if it exists
        if hasattr(self, 'finish_button'):
            self.finish_button.destroy()
        
        # Unbind events
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        
        # Add to history if image was changed
        if self.displayed_image is not None:
            self.add_to_history()
            
    def check_resize_area(self, event):
        if not self.is_resizing or not hasattr(self, 'image_on_canvas'):
            return
            
        # Get image bounds
        bbox = self.canvas.bbox(self.image_on_canvas)
        if not bbox:
            return
            
        x1, y1, x2, y2 = bbox
        mouse_x, mouse_y = event.x, event.y
        edge_size = 10  # Size of edge detection area
        
        # Check which edges the cursor is near
        near_left = abs(mouse_x - x1) < edge_size
        near_right = abs(mouse_x - x2) < edge_size
        near_top = abs(mouse_y - y1) < edge_size
        near_bottom = abs(mouse_y - y2) < edge_size
        
        # Set appropriate cursor
        if (near_left and near_top) or (near_right and near_bottom):
            self.canvas.config(cursor="size_nw_se")
        elif (near_right and near_top) or (near_left and near_bottom):
            self.canvas.config(cursor="size_ne_sw")
        elif near_left or near_right:
            self.canvas.config(cursor="size_we")
        elif near_top or near_bottom:
            self.canvas.config(cursor="size_ns")
        else:
            self.canvas.config(cursor="arrow")
            
        # Store edge information
        self.resize_edges = {
            'left': near_left,
            'right': near_right,
            'top': near_top,
            'bottom': near_bottom
        }
        
    def start_resize_drag(self, event):
        if not self.is_resizing:
            return
            
        # Check if we're near any edge
        if hasattr(self, 'resize_edges') and any(self.resize_edges.values()):
            self.resize_start_x = event.x
            self.resize_start_y = event.y
            self.drag_active = True
        
    def resize_from_edge(self, event):
        if not self.is_resizing or not hasattr(self, 'resize_start_x'):
            return
            
        # Calculate the change in position
        dx = event.x - self.resize_start_x
        dy = event.y - self.resize_start_y
        
        # Get current dimensions
        new_width = self.original_width
        new_height = self.original_height
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Adjust dimensions based on which edges are being dragged
        if self.resize_edges['right']:
            new_width = max(50, min(canvas_width, self.original_width + int(dx)))
        elif self.resize_edges['left']:
            new_width = max(50, min(canvas_width, self.original_width - int(dx)))
            
        if self.resize_edges['bottom']:
            new_height = max(50, min(canvas_height, self.original_height + int(dy)))
        elif self.resize_edges['top']:
            new_height = max(50, min(canvas_height, self.original_height - int(dy)))
            
        # Maintain aspect ratio if Shift is held
        if event.state & 0x1:  # Shift is held
            aspect_ratio = self.original_width / self.original_height
            if abs(dx) > abs(dy):
                new_height = int(new_width / aspect_ratio)
                # Check if height exceeds canvas
                if new_height > canvas_height:
                    new_height = canvas_height
                    new_width = int(new_height * aspect_ratio)
            else:
                new_width = int(new_height * aspect_ratio)
                # Check if width exceeds canvas
                if new_width > canvas_width:
                    new_width = canvas_width
                    new_height = int(new_width / aspect_ratio)
        
        try:
            # Create resized image from original
            resized = cv2.resize(
                self.resize_original,
                (new_width, new_height),
                interpolation=cv2.INTER_LINEAR
            )
            
            # Update display without converting color space
            self.show_image_resize(resized)
            
        except Exception as e:
            print(f"Resize error: {e}")
            self.cancel_dynamic_resize()
            
    def show_image_resize(self, image):
        """Special version of show_image that preserves color space during resize"""
        if image is None:
            return
            
        # Convert to PIL Image directly without color space conversion
        image_pil = Image.fromarray(image)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image_pil)
        
        # Clear previous image
        self.canvas.delete("all")
        
        # Calculate center position
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_center = (canvas_width - photo.width()) // 2
        y_center = (canvas_height - photo.height()) // 2
        
        # Create image on canvas
        self.image_on_canvas = self.canvas.create_image(
            x_center, y_center,
            anchor=tk.NW,
            image=photo
        )
        
        # Keep a reference to prevent garbage collection
        self.canvas.image = photo
        
        # Store current image
        self.displayed_image = image
        
        # Update canvas
        self.canvas.update()
            
    def cancel_dynamic_resize(self):
        self.is_resizing = False
        self.drag_active = False
        
        # Reset cursor
        self.canvas.config(cursor="arrow")
        
        # Remove finish button if it exists
        if hasattr(self, 'finish_button'):
            self.finish_button.destroy()
        
        # Unbind events
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        
        # Restore original image
        self.show_image(self.displayed_image)
        
    def bind_shortcuts(self):
        # File shortcuts
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.load_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        
        # Edit shortcuts
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        
        # Image shortcuts
        self.root.bind("<Control-r>", lambda e: self.open_resize_window())
        self.root.bind("<Control-d>", lambda e: self.start_dynamic_resize())
        self.root.bind("<Control-x>", lambda e: self.open_crop_window())
        self.root.bind("<Control-g>", lambda e: self.apply_grayscale())
        self.root.bind("<Control-b>", lambda e: self.apply_blur())
        self.root.bind("<Control-i>", lambda e: self.apply_invert())
        
    def open_resize_window(self):
        if self.displayed_image is not None:
            resize_window = tk.Toplevel(self.root)
            resize_window.title("Resize Image")
            resize_window.geometry("300x250")
            resize_window.resizable(False, False)
            resize_window.transient(self.root)
            resize_window.grab_set()
            
            # Current dimensions
            current_height, current_width = self.displayed_image.shape[:2]
            
            # Size frame
            size_frame = ttk.LabelFrame(resize_window, text="New Size", padding=(10, 5))
            size_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Width
            ttk.Label(size_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5)
            width_var = tk.StringVar(value=str(current_width))
            width_entry = ttk.Entry(size_frame, textvariable=width_var, width=10)
            width_entry.grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(size_frame, text="pixels").grid(row=0, column=2, padx=5, pady=5)
            
            # Height
            ttk.Label(size_frame, text="Height:").grid(row=1, column=0, padx=5, pady=5)
            height_var = tk.StringVar(value=str(current_height))
            height_entry = ttk.Entry(size_frame, textvariable=height_var, width=10)
            height_entry.grid(row=1, column=1, padx=5, pady=5)
            ttk.Label(size_frame, text="pixels").grid(row=1, column=2, padx=5, pady=5)
            
            # Maintain aspect ratio
            aspect_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(size_frame, text="Maintain aspect ratio", variable=aspect_var).grid(row=2, column=0, columnspan=3, pady=5)
            
            def update_height(*args):
                if aspect_var.get():
                    try:
                        new_width = int(width_var.get())
                        new_height = int(new_width * current_height / current_width)
                        height_var.set(str(new_height))
                    except ValueError:
                        pass
            
            def update_width(*args):
                if aspect_var.get():
                    try:
                        new_height = int(height_var.get())
                        new_width = int(new_height * current_width / current_height)
                        width_var.set(str(new_width))
                    except ValueError:
                        pass
            
            width_var.trace_add("write", update_height)
            height_var.trace_add("write", update_width)
            
            # Preset sizes frame
            presets_frame = ttk.LabelFrame(resize_window, text="Preset Sizes", padding=(10, 5))
            presets_frame.pack(fill=tk.X, padx=10, pady=5)
            
            def set_preset(width, height):
                width_var.set(str(width))
                if not aspect_var.get():
                    height_var.set(str(height))
            
            ttk.Button(presets_frame, text="640x480", command=lambda: set_preset(640, 480)).pack(side=tk.LEFT, padx=5, pady=5)
            ttk.Button(presets_frame, text="800x600", command=lambda: set_preset(800, 600)).pack(side=tk.LEFT, padx=5, pady=5)
            ttk.Button(presets_frame, text="1024x768", command=lambda: set_preset(1024, 768)).pack(side=tk.LEFT, padx=5, pady=5)
            
            def apply_resize():
                try:
                    new_width = int(width_var.get())
                    new_height = int(height_var.get())
                    if new_width <= 0 or new_height <= 0:
                        raise ValueError("Dimensions must be positive")
                    if new_width > 3000 or new_height > 3000:
                        raise ValueError("Maximum size is 3000x3000 pixels")
                    
                    self.displayed_image = cv2.resize(self.displayed_image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                    self.original_image = self.displayed_image.copy()
                    self.update_canvas()
                    self.add_to_history()
                    resize_window.destroy()
                    
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
            
            # Buttons
            button_frame = ttk.Frame(resize_window)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            ttk.Button(button_frame, text="Apply", command=apply_resize).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=resize_window.destroy).pack(side=tk.RIGHT, padx=5)
            
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            # Load and convert to RGB immediately
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.original_image = self.resize_if_large(self.original_image)
                self.displayed_image = self.original_image.copy()
                self.update_canvas()
                self.add_to_history()

    def resize_if_large(self, image):
        height, width = image.shape[:2]
        if width > 800 or height > 600:
            # Calculate aspect ratio
            aspect_ratio = width / height
            if width > height:
                new_width = 800
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = 600
                new_width = int(new_height * aspect_ratio)
            return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return image
        
    def apply_grayscale(self):
        if self.displayed_image is not None:
            if not self.is_gray:
                gray = cv2.cvtColor(self.displayed_image, cv2.COLOR_RGB2GRAY)
                self.displayed_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            else:
                self.displayed_image = self.original_image.copy()
                if self.is_blur:
                    self.displayed_image = cv2.GaussianBlur(self.displayed_image, (5, 5), 0)
                if self.is_inverted:
                    self.displayed_image = cv2.bitwise_not(self.displayed_image)
            
            self.is_gray = not self.is_gray
            self.update_canvas()
            self.add_to_history()
            
    def apply_blur(self):
        if self.displayed_image is None:
            return
            
        # Create blur adjustment window
        self.blur_window = tk.Toplevel(self.root)
        self.blur_window.title("Adjust Blur")
        self.blur_window.geometry("400x200")
        self.blur_window.resizable(False, False)
        
        # Store original image for preview
        self.blur_original = self.displayed_image.copy()
        
        # Create frame for controls
        control_frame = tk.Frame(self.blur_window)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add blur strength label
        tk.Label(
            control_frame,
            text="Blur Strength:",
            font=('Arial', 10)
        ).pack(pady=5)
        
        # Add blur slider
        self.blur_slider = tk.Scale(
            control_frame,
            from_=0,
            to=20,
            orient=tk.HORIZONTAL,
            length=300,
            resolution=1,
            command=self.update_blur_preview
        )
        self.blur_slider.set(0)
        self.blur_slider.pack(pady=10)
        
        # Add buttons frame
        button_frame = tk.Frame(control_frame)
        button_frame.pack(pady=20)
        
        # Add Apply button
        tk.Button(
            button_frame,
            text="Apply",
            command=self.apply_blur_final,
            bg='white',
            fg='black',
            width=10,
            relief=tk.SOLID
        ).pack(side=tk.LEFT, padx=5)
        
        # Add Cancel button
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_blur,
            bg='white',
            fg='black',
            width=10,
            relief=tk.SOLID
        ).pack(side=tk.LEFT, padx=5)
        
    def update_blur_preview(self, value):
        if not hasattr(self, 'blur_original'):
            return
            
        # Get blur kernel size (must be odd)
        kernel_size = 2 * int(float(value)) + 1
        
        try:
            # Apply blur
            if kernel_size > 1:
                # Apply blur directly to RGB image
                blurred = cv2.GaussianBlur(
                    self.blur_original,
                    (kernel_size, kernel_size),
                    0
                )
            else:
                blurred = self.blur_original.copy()
                
            # Update display
            self.show_image(blurred)
            
        except Exception as e:
            print(f"Blur error: {e}")
            
    def apply_blur_final(self):
        if hasattr(self, 'blur_window'):
            # Get final blur value
            kernel_size = 2 * int(self.blur_slider.get()) + 1
            
            if kernel_size > 1:
                # Apply blur directly to RGB image
                self.displayed_image = cv2.GaussianBlur(
                    self.blur_original,
                    (kernel_size, kernel_size),
                    0
                )
                
                # Add to history
                self.add_to_history()
                
            # Close window
            self.blur_window.destroy()
            delattr(self, 'blur_original')
            
    def cancel_blur(self):
        if hasattr(self, 'blur_window'):
            # Restore original image
            self.show_image(self.blur_original)
            
            # Close window
            self.blur_window.destroy()
            delattr(self, 'blur_original')
            
    def apply_invert(self):
        if self.displayed_image is not None:
            if not self.is_inverted:
                self.displayed_image = cv2.bitwise_not(self.displayed_image)
            else:
                self.displayed_image = self.original_image.copy()
                if self.is_gray:
                    gray = cv2.cvtColor(self.displayed_image, cv2.COLOR_RGB2GRAY)
                    self.displayed_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                if self.is_blur:
                    self.displayed_image = cv2.GaussianBlur(self.displayed_image, (5, 5), 0)
            
            self.is_inverted = not self.is_inverted
            self.update_canvas()
            self.add_to_history()
            
    def show_image(self, image):
        """Display an image on the canvas"""
        if image is None:
            return
            
        # Convert numpy array to PIL Image (assuming image is in RGB)
        image_pil = Image.fromarray(image)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image_pil)
        
        # Clear previous image
        self.canvas.delete("all")
        
        # Calculate center position
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_center = (canvas_width - photo.width()) // 2
        y_center = (canvas_height - photo.height()) // 2
        
        # Create image on canvas
        self.image_on_canvas = self.canvas.create_image(
            x_center, y_center,
            anchor=tk.NW,
            image=photo
        )
        
        # Keep a reference to prevent garbage collection
        self.canvas.image = photo
        
        # Update canvas
        self.canvas.update()

    def update_canvas(self):
        if self.displayed_image is not None:
            # Convert image to PhotoImage
            image = Image.fromarray(self.displayed_image)
            # Scale the image to fit the window while maintaining aspect ratio
            display_size = (780, 520)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Clear previous image
            self.canvas.delete("all")
            
            # Calculate center position
            x_center = (self.canvas.winfo_width() - photo.width()) // 2
            y_center = (self.canvas.winfo_height() - photo.height()) // 2
            
            # Store image position for drawing calculations
            self.image_x = x_center
            self.image_y = y_center
            self.image_width = photo.width()
            self.image_height = photo.height()
            
            # Create image on canvas
            self.image_on_canvas = self.canvas.create_image(x_center, y_center, anchor=tk.NW, image=photo)
            self.canvas.image = photo
            
    def get_image_coordinates(self, event):
        # Get relative position within the image
        x = event.x - self.image_x
        y = event.y - self.image_y
        
        # Ensure coordinates are within image bounds
        x = max(0, min(x, self.image_width))
        y = max(0, min(y, self.image_height))
        
        # Convert to actual image coordinates
        img_height, img_width = self.displayed_image.shape[:2]
        x = int(x * (img_width / self.image_width))
        y = int(y * (img_height / self.image_height))
        
        return x, y
        
    def start_drawing(self, event):
        if self.displayed_image is not None:
            self.is_drawing = True
            x, y = self.get_image_coordinates(event)
            self.last_x = x
            self.last_y = y
        
    def draw(self, event):
        if self.is_drawing and self.displayed_image is not None:
            # Get current coordinates
            x, y = self.get_image_coordinates(event)
            
            # Draw line on image
            rgb = tuple(int(self.brush_color[i:i+2], 16) for i in (1, 3, 5))
            cv2.line(self.displayed_image, (self.last_x, self.last_y), (x, y), rgb, self.brush_size)
            
            # Update last position
            self.last_x = x
            self.last_y = y
            
            # Update display
            self.update_canvas()
            
    def stop_drawing(self, event):
        if self.is_drawing:
            self.is_drawing = False
            self.add_to_history()
            
    def save_image(self):
        if self.displayed_image is not None:
            try:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")]
                )
                if file_path:
                    # Use PIL to save the image instead of OpenCV
                    img_to_save = Image.fromarray(self.displayed_image)
                    img_to_save.save(file_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save the image: {str(e)}")
                
    def add_to_history(self):
        # Create a state object with all necessary information
        state = {
            'displayed_image': self.displayed_image.copy() if self.displayed_image is not None else None,
            'cropped_image': self.cropped_image.copy() if self.cropped_image is not None else None,
            'is_gray': self.is_gray,
            'is_blur': self.is_blur,
            'is_inverted': self.is_inverted
        }
        
        # Remove any redo history
        self.history = self.history[:self.history_position + 1]
        self.history.append(state)
        self.history_position = len(self.history) - 1
        
    def undo(self):
        if self.history_position > 0:
            self.history_position -= 1
            self.restore_state(self.history[self.history_position])
            
    def redo(self):
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            self.restore_state(self.history[self.history_position])
            
    def restore_state(self, state):
        self.displayed_image = state['displayed_image'].copy() if state['displayed_image'] is not None else None
        self.cropped_image = state['cropped_image'].copy() if state['cropped_image'] is not None else None
        self.is_gray = state['is_gray']
        self.is_blur = state['is_blur']
        self.is_inverted = state['is_inverted']
        self.update_canvas()
        
    def new_file(self):
        # Create settings dialog
        settings_window = tk.Toplevel(self.root)
        settings_window.title("New Canvas Settings")
        settings_window.geometry("300x400")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Canvas size frame
        size_frame = ttk.LabelFrame(settings_window, text="Canvas Size", padding=(10, 5))
        size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Width
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.StringVar(value="800")
        width_entry = ttk.Entry(size_frame, textvariable=width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(size_frame, text="pixels").grid(row=0, column=2, padx=5, pady=5)
        
        # Height
        ttk.Label(size_frame, text="Height:").grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.StringVar(value="600")
        height_entry = ttk.Entry(size_frame, textvariable=height_var, width=10)
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(size_frame, text="pixels").grid(row=1, column=2, padx=5, pady=5)
        
        # Background color frame
        color_frame = ttk.LabelFrame(settings_window, text="Background Color", padding=(10, 5))
        color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        bg_color_var = tk.StringVar(value="#FFFFFF")
        
        def choose_color():
            color = colorchooser.askcolor(color=bg_color_var.get())[1]
            if color:
                bg_color_var.set(color)
                color_btn.configure(bg=color)
        
        color_btn = tk.Button(color_frame, text="Choose Color", command=choose_color, bg=bg_color_var.get())
        color_btn.pack(padx=5, pady=5)
        
        # Drawing tools frame
        tools_frame = ttk.LabelFrame(settings_window, text="Drawing Tools", padding=(10, 5))
        tools_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Brush size
        ttk.Label(tools_frame, text="Brush Size:").grid(row=0, column=0, padx=5, pady=5)
        brush_size_var = tk.IntVar(value=2)
        brush_size = ttk.Scale(tools_frame, from_=1, to=20, orient=tk.HORIZONTAL, variable=brush_size_var)
        brush_size.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Brush color
        brush_color_var = tk.StringVar(value="#000000")
        
        def choose_brush_color():
            color = colorchooser.askcolor(color=brush_color_var.get())[1]
            if color:
                brush_color_var.set(color)
                brush_color_btn.configure(bg=color)
        
        ttk.Label(tools_frame, text="Brush Color:").grid(row=1, column=0, padx=5, pady=5)
        brush_color_btn = tk.Button(tools_frame, text="Choose Color", command=choose_brush_color, bg=brush_color_var.get())
        brush_color_btn.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        def create_canvas():
            try:
                width = int(width_var.get())
                height = int(height_var.get())
                if width <= 0 or height <= 0:
                    raise ValueError("Width and height must be positive")
                if width > 3000 or height > 3000:
                    raise ValueError("Maximum size is 3000x3000 pixels")
                
                # Create new blank image
                self.original_image = np.full((height, width, 3), 255, dtype=np.uint8)
                # Fill with background color
                rgb = tuple(int(bg_color_var.get()[i:i+2], 16) for i in (1, 3, 5))
                self.original_image[:] = rgb
                
                self.displayed_image = self.original_image.copy()
                self.brush_size = brush_size_var.get()
                self.brush_color = brush_color_var.get()
                
                # Reset state
                self.cropped_image = None
                self.crop_rect = None
                self.is_gray = False
                self.is_blur = False
                self.is_inverted = False
                self.history = []
                self.history_position = -1
                
                # Enable drawing
                self.setup_drawing()
                
                # Update display
                self.update_canvas()
                self.add_to_history()
                settings_window.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Create", command=create_canvas).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
        
    def setup_drawing(self):
        self.is_drawing = False
        self.last_x = None
        self.last_y = None
        
        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        
    def show_welcome_window(self):
        welcome = tk.Toplevel(self.root)
        welcome.title("Welcome to Image Editor")
        welcome.geometry("600x500")
        welcome.transient(self.root)
        welcome.grab_set()
        welcome.resizable(False, False)
        
        # Create main frame with padding
        main_frame = ttk.Frame(welcome, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, width=550)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        # Create frame for content
        content_frame = ttk.Frame(canvas)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create canvas window
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content_frame.bind('<Configure>', configure_scroll_region)
        
        # Configure canvas width
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_canvas_width)
        
        # Configure mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Welcome message
        ttk.Label(
            content_frame,
            text="Welcome to Image Processing Application",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        # Features explanation
        features = {
            "File Menu": {
                "New (Ctrl+N)": "Create a new canvas with custom size and background color",
                "Open (Ctrl+O)": "Open an existing image file",
                "Save (Ctrl+S)": "Save the current image",
            },
            "Edit Menu": {
                "Undo (Ctrl+Z)": "Undo the last action",
                "Redo (Ctrl+Y)": "Redo the previously undone action"
            },
            "Image Menu": {
                "Resize": {
                    "Dialog Resize (Ctrl+R)": "Open a dialog to enter exact dimensions",
                    "Dynamic Resize (Ctrl+D)": "Drag image corners to resize visually"
                },
                "Crop (Ctrl+X)": "Select and crop a portion of the image",
                "Grayscale (Ctrl+G)": "Convert image to grayscale",
                "Blur (Ctrl+B)": "Apply Gaussian blur effect with scaler",
                "Invert Colors (Ctrl+I)": "Invert all colors in the image"
            },
            "Drawing Tools": {
                "New Canvas": "When creating a new canvas, you can set:",
                "• Brush Size": "Adjust the thickness of the drawing brush",
                "• Brush Color": "Choose any color for drawing",
                "• Canvas Size": "Set custom width and height",
                "• Background Color": "Choose canvas background color"
            },
            "Resize Features": {
                "Dialog Resize": "Enter exact width and height values",
                "• Maintain Ratio": "Keep image proportions while resizing",
                "• Preset Sizes": "Quick access to common dimensions",
                "Dynamic Resize": "Visual resize by dragging corners",
                "• Corner Handles": "Grab and drag any corner to resize",
                "• Live Preview": "See the result as you drag",
                "• Aspect Lock": "Hold Shift to maintain proportions"
            }
        }
        
        # Configure styles
        style = ttk.Style()
        style.configure("Section.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Feature.TLabel", font=("Helvetica", 10))
        style.configure("Description.TLabel", font=("Helvetica", 10), wraplength=500)
        
        # Add features to content frame
        for section, items in features.items():
            # Section header
            ttk.Label(
                content_frame,
                text=section,
                style="Section.TLabel"
            ).pack(anchor="w", pady=(15, 5))
            
            # Features and descriptions
            for feature, description in items.items():
                frame = ttk.Frame(content_frame)
                frame.pack(fill="x", padx=20)
                
                if isinstance(description, dict):
                    # Subsection
                    ttk.Label(
                        frame,
                        text=feature,
                        style="Feature.TLabel"
                    ).pack(anchor="w")
                    
                    for subfeature, subdesc in description.items():
                        subframe = ttk.Frame(frame)
                        subframe.pack(fill="x", padx=20)
                        ttk.Label(
                            subframe,
                            text=subfeature,
                            style="Feature.TLabel"
                        ).pack(anchor="w")
                        ttk.Label(
                            subframe,
                            text=subdesc,
                            style="Description.TLabel"
                        ).pack(anchor="w", padx=20)
                else:
                    ttk.Label(
                        frame,
                        text=feature,
                        style="Feature.TLabel"
                    ).pack(anchor="w")
                    
                    ttk.Label(
                        frame,
                        text=description,
                        style="Description.TLabel"
                    ).pack(anchor="w", padx=20)
        
        # Add close button at the bottom
        button_frame = ttk.Frame(welcome)
        button_frame.pack(fill="x", pady=10)
        ttk.Button(
            button_frame,
            text="Get Started",
            command=welcome.destroy
        ).pack()
        
        # Center the window
        welcome.update_idletasks()
        width = welcome.winfo_width()
        height = welcome.winfo_height()
        x = (welcome.winfo_screenwidth() // 2) - (width // 2)
        y = (welcome.winfo_screenheight() // 2) - (height // 2)
        welcome.geometry(f"{width}x{height}+{x}+{y}")
        
        # Clean up mouse wheel binding when window closes
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            welcome.destroy()
        welcome.protocol("WM_DELETE_WINDOW", on_close)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageProcessor()
    app.run()