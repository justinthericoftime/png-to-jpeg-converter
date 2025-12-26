#!/usr/bin/env python3
"""
PNG to JPEG Batch Converter - GUI Application

A simple macOS/cross-platform GUI for batch converting PNG images to JPEG.
Uses tkinter for the graphical interface and imports conversion logic from png2jpg.py.

Usage:
    python png2jpg_gui.py

Requirements:
    - Python 3.8+
    - Pillow (PIL Fork)
    - tkinter (included with Python)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import Tuple, Optional

# Import conversion functions from CLI tool
from png2jpg import process_directory, get_png_files


class PNGtoJPEGConverter:
    """Main GUI application class for PNG to JPEG batch conversion."""

    def __init__(self, root: tk.Tk):
        """
        Initialize the converter GUI.

        Args:
            root: The tkinter root window.
        """
        self.root = root
        self.root.title("PNG to JPEG Batch Converter")
        
        # Set window size and minimum size
        self.root.geometry("500x550")
        self.root.minsize(400, 450)
        
        # Variables for form inputs
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.quality = tk.IntVar(value=85)
        self.recursive = tk.BooleanVar(value=False)
        self.bg_option = tk.StringVar(value="white")
        self.custom_bg = tk.StringVar(value="255,255,255")
        
        # Conversion state
        self.is_converting = False
        
        self.setup_ui()
        self.update_convert_button_state()

    def setup_ui(self):
        """Build all UI elements."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="PNG to JPEG Batch Converter",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Input folder section
        ttk.Label(main_frame, text="Input Folder:").grid(row=1, column=0, sticky="w", pady=5)
        input_entry = ttk.Entry(main_frame, textvariable=self.input_path)
        input_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_input).grid(row=1, column=2, pady=5)
        
        # Output folder section
        ttk.Label(main_frame, text="Output Folder:").grid(row=2, column=0, sticky="w", pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path)
        output_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # Quality slider section
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        quality_frame.columnconfigure(1, weight=1)
        
        ttk.Label(quality_frame, text="Quality:").grid(row=0, column=0, sticky="w")
        self.quality_slider = ttk.Scale(
            quality_frame, 
            from_=1, 
            to=100, 
            orient="horizontal",
            variable=self.quality,
            command=self.on_quality_change
        )
        self.quality_slider.grid(row=0, column=1, sticky="ew", padx=10)
        self.quality_label = ttk.Label(quality_frame, text="85")
        self.quality_label.grid(row=0, column=2, sticky="e")
        
        # Quality range labels
        ttk.Label(quality_frame, text="(1)", font=('Helvetica', 9)).grid(row=1, column=1, sticky="w", padx=10)
        ttk.Label(quality_frame, text="(100)", font=('Helvetica', 9)).grid(row=1, column=1, sticky="e", padx=10)
        
        # Recursive checkbox
        recursive_check = ttk.Checkbutton(
            main_frame, 
            text="Include subfolders (recursive)",
            variable=self.recursive
        )
        recursive_check.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)
        
        # Background color section
        bg_frame = ttk.LabelFrame(main_frame, text="Background for transparent PNGs", padding="5")
        bg_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Radiobutton(bg_frame, text="White", variable=self.bg_option, value="white").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(bg_frame, text="Black", variable=self.bg_option, value="black").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(bg_frame, text="Custom:", variable=self.bg_option, value="custom").grid(row=0, column=2, sticky="w")
        self.custom_entry = ttk.Entry(bg_frame, textvariable=self.custom_bg, width=12)
        self.custom_entry.grid(row=0, column=3, sticky="w", padx=5)
        ttk.Label(bg_frame, text="(R,G,B)", font=('Helvetica', 9)).grid(row=0, column=4, sticky="w")
        
        # Status/Log area
        log_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.status_text = tk.Text(log_frame, height=10, wrap="word", state="disabled")
        self.status_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial status message
        self.log_message("Ready to convert...")
        
        # Convert button
        self.convert_button = ttk.Button(
            main_frame, 
            text="Convert",
            command=self.start_conversion
        )
        self.convert_button.grid(row=7, column=0, columnspan=3, pady=15)
        
        # Bind path changes to update button state
        self.input_path.trace_add("write", lambda *args: self.update_convert_button_state())
        self.output_path.trace_add("write", lambda *args: self.update_convert_button_state())

    def browse_input(self):
        """Open folder picker for input directory."""
        folder = filedialog.askdirectory(
            title="Select Input Folder",
            mustexist=True
        )
        if folder:
            self.input_path.set(folder)
            self.log_message(f"Input folder selected: {folder}")

    def browse_output(self):
        """Open folder picker for output directory."""
        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )
        if folder:
            self.output_path.set(folder)
            self.log_message(f"Output folder selected: {folder}")

    def on_quality_change(self, value):
        """Update quality label when slider changes."""
        self.quality_label.config(text=str(int(float(value))))

    def update_convert_button_state(self):
        """Enable/disable convert button based on input validation."""
        if self.is_converting:
            return
        
        if self.input_path.get() and self.output_path.get():
            self.convert_button.config(state="normal")
        else:
            self.convert_button.config(state="disabled")

    def validate_inputs(self) -> Tuple[bool, str]:
        """
        Validate all input fields.

        Returns:
            Tuple of (is_valid, error_message).
        """
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        
        # Check input directory exists
        if not os.path.isdir(input_dir):
            return False, f"Input folder does not exist: {input_dir}"
        
        # Check for PNG files
        png_files = get_png_files(input_dir, self.recursive.get())
        if not png_files:
            return False, "No PNG files found in the input folder."
        
        # Validate custom background color if selected
        if self.bg_option.get() == "custom":
            try:
                bg_color = self.parse_bg_color(self.custom_bg.get())
            except ValueError as e:
                return False, str(e)
        
        return True, ""

    def parse_bg_color(self, color_str: str) -> Tuple[int, int, int]:
        """
        Parse background color string to RGB tuple.

        Args:
            color_str: Color string in "R,G,B" format.

        Returns:
            Tuple of (R, G, B) values.

        Raises:
            ValueError: If color format is invalid.
        """
        try:
            parts = color_str.split(",")
            if len(parts) != 3:
                raise ValueError("Background color must have exactly 3 values (R,G,B)")
            rgb = tuple(int(x.strip()) for x in parts)
            for val in rgb:
                if not 0 <= val <= 255:
                    raise ValueError(f"Color values must be between 0 and 255, got: {val}")
            return rgb
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Background color must be three integers separated by commas (e.g., 255,255,255)")
            raise

    def get_bg_color(self) -> Tuple[int, int, int]:
        """Get the selected background color as RGB tuple."""
        option = self.bg_option.get()
        if option == "white":
            return (255, 255, 255)
        elif option == "black":
            return (0, 0, 0)
        else:
            return self.parse_bg_color(self.custom_bg.get())

    def start_conversion(self):
        """Begin threaded conversion process."""
        # Validate inputs first
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg)
            return
        
        # Update UI state
        self.is_converting = True
        self.convert_button.config(state="disabled", text="Converting...")
        self.clear_log()
        self.log_message("Starting conversion...")
        
        # Run conversion in background thread
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()

    def run_conversion(self):
        """Actual conversion logic (runs in separate thread)."""
        try:
            input_dir = self.input_path.get()
            output_dir = self.output_path.get()
            quality = self.quality.get()
            recursive = self.recursive.get()
            bg_color = self.get_bg_color()
            
            self.log_message(f"Input: {input_dir}")
            self.log_message(f"Output: {output_dir}")
            self.log_message(f"Quality: {quality}")
            self.log_message(f"Recursive: {recursive}")
            self.log_message(f"Background: RGB{bg_color}")
            self.log_message("-" * 40)
            
            # Run conversion with progress callback
            converted, skipped = process_directory(
                input_dir=input_dir,
                output_dir=output_dir,
                quality=quality,
                recursive=recursive,
                bg_color=bg_color,
                progress_callback=self.progress_callback
            )
            
            # Show completion message
            self.log_message("-" * 40)
            self.log_message(f"Complete! Converted {converted} files. {skipped} skipped.")
            
        except Exception as e:
            self.log_message(f"Error during conversion: {e}", is_error=True)
        
        finally:
            # Reset UI state (must be done on main thread)
            self.root.after(0, self.conversion_complete)

    def progress_callback(self, message: str, is_error: bool):
        """
        Thread-safe callback for progress updates.

        Args:
            message: The message to log.
            is_error: Whether this is an error message.
        """
        self.root.after(0, lambda: self.log_message(message, is_error))

    def conversion_complete(self):
        """Reset UI after conversion completes."""
        self.is_converting = False
        self.convert_button.config(state="normal", text="Convert")
        self.update_convert_button_state()

    def log_message(self, message: str, is_error: bool = False):
        """
        Add a message to the status log.

        Args:
            message: The message to display.
            is_error: If True, message is displayed as an error.
        """
        self.status_text.config(state="normal")
        if is_error:
            self.status_text.insert("end", f"{message}\n", "error")
            self.status_text.tag_config("error", foreground="red")
        else:
            self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")

    def clear_log(self):
        """Clear the status log."""
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.config(state="disabled")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    
    # Try to set app icon (optional)
    try:
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
    except Exception:
        pass  # Skip if no icon available
    
    app = PNGtoJPEGConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
