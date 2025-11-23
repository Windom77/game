#!/usr/bin/env python3
"""
Character Customization Tool for GLB Models.

A user-friendly GUI application for modifying character appearance
(material colors) in GLB files without needing Blender.

Usage:
    python character_editor.py

Requirements:
    - pygltflib (pip install pygltflib)
    - tkinter (usually included with Python)
"""

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import os
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
import copy

# Check for pygltflib
try:
    from pygltflib import GLTF2
    PYGLTFLIB_AVAILABLE = True
except ImportError:
    PYGLTFLIB_AVAILABLE = False
    print("Warning: pygltflib not installed. Install with: pip install pygltflib")


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class MaterialInfo:
    """Information about a material in the GLB file."""
    index: int
    name: str
    base_color: List[float]  # [R, G, B, A]
    original_color: List[float]  # For reset functionality
    enabled: bool = True


@dataclass
class ColorPreset:
    """Predefined color preset."""
    name: str
    color: List[float]  # [R, G, B, A]


# Skin tone presets
SKIN_PRESETS = [
    ColorPreset("Pale", [0.95, 0.87, 0.82, 1.0]),
    ColorPreset("Fair", [0.92, 0.78, 0.68, 1.0]),
    ColorPreset("Medium", [0.82, 0.64, 0.52, 1.0]),
    ColorPreset("Tan", [0.76, 0.57, 0.45, 1.0]),
    ColorPreset("Brown", [0.55, 0.38, 0.28, 1.0]),
    ColorPreset("Dark", [0.36, 0.24, 0.18, 1.0]),
]

# Hair color presets
HAIR_PRESETS = [
    ColorPreset("Black", [0.05, 0.05, 0.05, 1.0]),
    ColorPreset("Dark Brown", [0.20, 0.12, 0.08, 1.0]),
    ColorPreset("Brown", [0.35, 0.22, 0.15, 1.0]),
    ColorPreset("Auburn", [0.50, 0.25, 0.15, 1.0]),
    ColorPreset("Blonde", [0.85, 0.70, 0.45, 1.0]),
    ColorPreset("Red", [0.60, 0.20, 0.10, 1.0]),
    ColorPreset("Gray", [0.60, 0.60, 0.60, 1.0]),
    ColorPreset("White", [0.95, 0.95, 0.95, 1.0]),
]

# Clothing color presets
CLOTHING_PRESETS = [
    ColorPreset("Black", [0.08, 0.08, 0.08, 1.0]),
    ColorPreset("White", [0.95, 0.95, 0.95, 1.0]),
    ColorPreset("Navy", [0.10, 0.15, 0.30, 1.0]),
    ColorPreset("Burgundy", [0.45, 0.10, 0.15, 1.0]),
    ColorPreset("Forest Green", [0.15, 0.30, 0.15, 1.0]),
    ColorPreset("Victorian Purple", [0.35, 0.20, 0.40, 1.0]),
    ColorPreset("Maid Gray", [0.40, 0.40, 0.42, 1.0]),
    ColorPreset("Cream", [0.95, 0.92, 0.85, 1.0]),
]


# ============================================================================
# Material Widget
# ============================================================================

class MaterialWidget(ttk.Frame):
    """Widget for editing a single material's color."""

    def __init__(self, parent, material: MaterialInfo, on_change_callback=None):
        super().__init__(parent)
        self.material = material
        self.on_change = on_change_callback

        # Variables for sliders
        self.r_var = tk.DoubleVar(value=material.base_color[0])
        self.g_var = tk.DoubleVar(value=material.base_color[1])
        self.b_var = tk.DoubleVar(value=material.base_color[2])
        self.enabled_var = tk.BooleanVar(value=material.enabled)

        self._create_widgets()
        self._update_preview()

    def _create_widgets(self):
        """Create the material editing widgets."""
        # Main container with border
        self.configure(relief="groove", padding=5)

        # Header row: checkbox, name, preview
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 5))

        # Enable checkbox
        self.enable_cb = ttk.Checkbutton(
            header_frame,
            variable=self.enabled_var,
            command=self._on_enable_toggle
        )
        self.enable_cb.pack(side="left")

        # Material name
        name_label = ttk.Label(
            header_frame,
            text=self.material.name,
            font=("TkDefaultFont", 10, "bold"),
            width=25,
            anchor="w"
        )
        name_label.pack(side="left", padx=5)

        # Color preview canvas
        self.preview_canvas = tk.Canvas(
            header_frame,
            width=40,
            height=25,
            relief="sunken",
            borderwidth=1
        )
        self.preview_canvas.pack(side="left", padx=5)

        # Pick color button
        pick_btn = ttk.Button(
            header_frame,
            text="Pick Color...",
            command=self._pick_color,
            width=12
        )
        pick_btn.pack(side="left", padx=5)

        # Reset button
        reset_btn = ttk.Button(
            header_frame,
            text="Reset",
            command=self._reset_color,
            width=6
        )
        reset_btn.pack(side="left")

        # Sliders frame
        sliders_frame = ttk.Frame(self)
        sliders_frame.pack(fill="x", pady=5)

        # R slider
        self._create_slider(sliders_frame, "R", self.r_var, 0, "red")
        # G slider
        self._create_slider(sliders_frame, "G", self.g_var, 1, "green")
        # B slider
        self._create_slider(sliders_frame, "B", self.b_var, 2, "blue")

        # Preset buttons frame
        preset_frame = ttk.Frame(self)
        preset_frame.pack(fill="x", pady=(5, 0))

        # Determine which presets to show based on material name
        presets = self._get_relevant_presets()

        ttk.Label(preset_frame, text="Presets:", width=8).pack(side="left")

        for preset in presets[:6]:  # Show max 6 presets
            btn = ttk.Button(
                preset_frame,
                text=preset.name,
                command=lambda p=preset: self._apply_preset(p),
                width=10
            )
            btn.pack(side="left", padx=2)

    def _create_slider(self, parent, label: str, var: tk.DoubleVar,
                       row: int, color: str):
        """Create a labeled slider for a color component."""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=1)

        # Label
        lbl = ttk.Label(frame, text=f"{label}:", width=3)
        lbl.pack(side="left")

        # Scale/slider
        slider = ttk.Scale(
            frame,
            from_=0.0,
            to=1.0,
            variable=var,
            orient="horizontal",
            command=lambda v: self._on_slider_change()
        )
        slider.pack(side="left", fill="x", expand=True, padx=5)

        # Value label
        value_label = ttk.Label(frame, textvariable=var, width=6)
        value_label.pack(side="left")

        # Entry for precise input
        entry = ttk.Entry(frame, textvariable=var, width=6)
        entry.pack(side="left", padx=5)
        entry.bind("<Return>", lambda e: self._on_slider_change())
        entry.bind("<FocusOut>", lambda e: self._on_slider_change())

    def _get_relevant_presets(self) -> List[ColorPreset]:
        """Get presets relevant to this material based on name."""
        name_lower = self.material.name.lower()

        if any(x in name_lower for x in ["skin", "body", "face", "hand", "arm", "leg"]):
            return SKIN_PRESETS
        elif any(x in name_lower for x in ["hair", "head"]):
            return HAIR_PRESETS
        else:
            return CLOTHING_PRESETS

    def _on_slider_change(self):
        """Handle slider value changes."""
        # Clamp values
        r = max(0.0, min(1.0, self.r_var.get()))
        g = max(0.0, min(1.0, self.g_var.get()))
        b = max(0.0, min(1.0, self.b_var.get()))

        self.r_var.set(round(r, 3))
        self.g_var.set(round(g, 3))
        self.b_var.set(round(b, 3))

        # Update material
        self.material.base_color = [r, g, b, self.material.base_color[3]]

        self._update_preview()

        if self.on_change:
            self.on_change()

    def _on_enable_toggle(self):
        """Handle enable/disable toggle."""
        self.material.enabled = self.enabled_var.get()
        if self.on_change:
            self.on_change()

    def _update_preview(self):
        """Update the color preview canvas."""
        r = int(self.r_var.get() * 255)
        g = int(self.g_var.get() * 255)
        b = int(self.b_var.get() * 255)
        color = f"#{r:02x}{g:02x}{b:02x}"

        self.preview_canvas.delete("all")
        self.preview_canvas.create_rectangle(
            2, 2, 38, 23,
            fill=color,
            outline="black"
        )

    def _pick_color(self):
        """Open color picker dialog."""
        # Convert current color to RGB tuple for colorchooser
        current_rgb = (
            int(self.r_var.get() * 255),
            int(self.g_var.get() * 255),
            int(self.b_var.get() * 255)
        )

        result = colorchooser.askcolor(
            color=current_rgb,
            title=f"Choose color for {self.material.name}"
        )

        if result[0]:  # result is ((r, g, b), "#hexcolor")
            rgb = result[0]
            self.r_var.set(round(rgb[0] / 255, 3))
            self.g_var.set(round(rgb[1] / 255, 3))
            self.b_var.set(round(rgb[2] / 255, 3))
            self._on_slider_change()

    def _reset_color(self):
        """Reset to original color."""
        orig = self.material.original_color
        self.r_var.set(orig[0])
        self.g_var.set(orig[1])
        self.b_var.set(orig[2])
        self._on_slider_change()

    def _apply_preset(self, preset: ColorPreset):
        """Apply a color preset."""
        self.r_var.set(preset.color[0])
        self.g_var.set(preset.color[1])
        self.b_var.set(preset.color[2])
        self._on_slider_change()

    def get_color(self) -> List[float]:
        """Get current color as [R, G, B, A]."""
        return [
            self.r_var.get(),
            self.g_var.get(),
            self.b_var.get(),
            self.material.base_color[3]
        ]


# ============================================================================
# Main Application
# ============================================================================

class CharacterEditorApp:
    """Main application class for the character editor."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Character Customization Tool")
        self.root.geometry("750x700")
        self.root.minsize(650, 500)

        # State
        self.current_file: Optional[str] = None
        self.gltf: Optional[GLTF2] = None
        self.materials: List[MaterialInfo] = []
        self.material_widgets: List[MaterialWidget] = []
        self.undo_stack: List[Dict] = []

        # Output directory
        self.output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "models", "characterdev"
        )

        self._create_ui()

    def _create_ui(self):
        """Create the main UI."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Character Customization Tool",
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="GLB File", padding=10)
        file_frame.pack(fill="x", pady=(0, 10))

        self.file_label = ttk.Label(
            file_frame,
            text="No file loaded",
            font=("TkDefaultFont", 10)
        )
        self.file_label.pack(side="left", fill="x", expand=True)

        browse_btn = ttk.Button(
            file_frame,
            text="Browse...",
            command=self._browse_file
        )
        browse_btn.pack(side="right")

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Load a GLB file to begin editing",
            foreground="gray"
        )
        self.status_label.pack(fill="x")

        # Materials frame with scrollbar
        materials_container = ttk.LabelFrame(
            main_frame,
            text="Materials",
            padding=5
        )
        materials_container.pack(fill="both", expand=True, pady=10)

        # Canvas for scrolling
        self.canvas = tk.Canvas(materials_container)
        scrollbar = ttk.Scrollbar(
            materials_container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Bottom buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))

        # Left side buttons
        left_buttons = ttk.Frame(buttons_frame)
        left_buttons.pack(side="left")

        ttk.Button(
            left_buttons,
            text="Reset All",
            command=self._reset_all
        ).pack(side="left", padx=5)

        ttk.Button(
            left_buttons,
            text="Undo",
            command=self._undo
        ).pack(side="left", padx=5)

        ttk.Button(
            left_buttons,
            text="Random Colors",
            command=self._randomize_colors
        ).pack(side="left", padx=5)

        # Right side buttons
        right_buttons = ttk.Frame(buttons_frame)
        right_buttons.pack(side="right")

        ttk.Button(
            right_buttons,
            text="Save As...",
            command=self._save_file
        ).pack(side="left", padx=5)

        ttk.Button(
            right_buttons,
            text="Quick Save",
            command=self._quick_save
        ).pack(side="left", padx=5)

        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(
            main_frame,
            mode="indeterminate"
        )

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _browse_file(self):
        """Open file browser to select GLB file."""
        initial_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets", "models"
        )

        if not os.path.exists(initial_dir):
            initial_dir = os.path.dirname(os.path.abspath(__file__))

        filename = filedialog.askopenfilename(
            title="Select GLB File",
            initialdir=initial_dir,
            filetypes=[
                ("GLB Files", "*.glb"),
                ("GLTF Files", "*.gltf"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            self._load_file(filename)

    def _load_file(self, filepath: str):
        """Load a GLB file and extract materials."""
        if not PYGLTFLIB_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "pygltflib is not installed.\n\n"
                "Install it with: pip install pygltflib"
            )
            return

        try:
            self.gltf = GLTF2().load(filepath)
            self.current_file = filepath
            self.materials = []
            self.undo_stack = []

            # Extract materials
            if self.gltf.materials:
                for idx, mat in enumerate(self.gltf.materials):
                    name = mat.name or f"Material_{idx}"

                    # Get base color (default white if not present)
                    base_color = [1.0, 1.0, 1.0, 1.0]
                    if mat.pbrMetallicRoughness:
                        if mat.pbrMetallicRoughness.baseColorFactor:
                            base_color = list(mat.pbrMetallicRoughness.baseColorFactor)

                    self.materials.append(MaterialInfo(
                        index=idx,
                        name=name,
                        base_color=base_color.copy(),
                        original_color=base_color.copy(),
                        enabled=True
                    ))

            # Update UI
            self.file_label.config(text=os.path.basename(filepath))
            self.status_label.config(
                text=f"Loaded {len(self.materials)} materials",
                foreground="green"
            )

            self._rebuild_material_widgets()

        except Exception as e:
            messagebox.showerror("Error Loading File", str(e))
            self.status_label.config(text=f"Error: {e}", foreground="red")

    def _rebuild_material_widgets(self):
        """Rebuild all material widgets."""
        # Clear existing widgets
        for widget in self.material_widgets:
            widget.destroy()
        self.material_widgets = []

        # Create new widgets
        for material in self.materials:
            widget = MaterialWidget(
                self.scrollable_frame,
                material,
                on_change_callback=self._on_material_change
            )
            widget.pack(fill="x", pady=5, padx=5)
            self.material_widgets.append(widget)

        # Update scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_material_change(self):
        """Called when any material is changed."""
        # Save state for undo
        self._save_undo_state()

    def _save_undo_state(self):
        """Save current state to undo stack."""
        state = {
            "materials": [
                {
                    "index": m.index,
                    "color": m.base_color.copy()
                }
                for m in self.materials
            ]
        }
        self.undo_stack.append(state)

        # Limit undo stack size
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def _undo(self):
        """Undo last change."""
        if len(self.undo_stack) < 2:
            return

        # Pop current state
        self.undo_stack.pop()

        # Get previous state
        state = self.undo_stack[-1]

        # Restore materials
        for mat_state in state["materials"]:
            for mat in self.materials:
                if mat.index == mat_state["index"]:
                    mat.base_color = mat_state["color"].copy()
                    break

        # Rebuild widgets
        self._rebuild_material_widgets()
        self.status_label.config(text="Undo applied", foreground="blue")

    def _reset_all(self):
        """Reset all materials to original colors."""
        for mat in self.materials:
            mat.base_color = mat.original_color.copy()

        self._rebuild_material_widgets()
        self.status_label.config(text="All materials reset", foreground="blue")

    def _randomize_colors(self):
        """Randomize all material colors."""
        import random

        self._save_undo_state()

        for mat in self.materials:
            mat.base_color = [
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
                random.uniform(0.1, 0.9),
                1.0
            ]

        self._rebuild_material_widgets()
        self.status_label.config(text="Colors randomized", foreground="purple")

    def _save_file(self):
        """Save modified GLB with custom name."""
        if not self.gltf or not self.current_file:
            messagebox.showwarning("No File", "Please load a file first.")
            return

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate default filename
        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{base_name}_custom_{timestamp}.glb"

        # Ask for filename
        output_path = filedialog.asksaveasfilename(
            title="Save Modified GLB",
            initialdir=self.output_dir,
            initialfile=default_name,
            defaultextension=".glb",
            filetypes=[("GLB Files", "*.glb")]
        )

        if output_path:
            self._do_save(output_path)

    def _quick_save(self):
        """Quick save with auto-generated name."""
        if not self.gltf or not self.current_file:
            messagebox.showwarning("No File", "Please load a file first.")
            return

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate filename
        base_name = os.path.splitext(os.path.basename(self.current_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            self.output_dir,
            f"{base_name}_custom_{timestamp}.glb"
        )

        self._do_save(output_path)

    def _do_save(self, output_path: str):
        """Perform the actual save operation."""
        try:
            # Show progress
            self.progress.pack(fill="x", pady=5)
            self.progress.start()
            self.root.update()

            # Apply modifications to GLTF
            for mat_info in self.materials:
                if mat_info.enabled:
                    gltf_mat = self.gltf.materials[mat_info.index]
                    if gltf_mat.pbrMetallicRoughness:
                        gltf_mat.pbrMetallicRoughness.baseColorFactor = mat_info.base_color

            # Save GLB
            self.gltf.save(output_path)

            # Save metadata JSON
            self._save_metadata(output_path)

            # Update modification log
            self._log_modification(output_path)

            # Hide progress
            self.progress.stop()
            self.progress.pack_forget()

            # Success message
            self.status_label.config(
                text=f"Saved: {os.path.basename(output_path)}",
                foreground="green"
            )
            messagebox.showinfo(
                "Save Successful",
                f"File saved to:\n{output_path}\n\n"
                f"Metadata saved to:\n{output_path.replace('.glb', '_meta.json')}"
            )

        except Exception as e:
            self.progress.stop()
            self.progress.pack_forget()
            messagebox.showerror("Save Error", str(e))
            self.status_label.config(text=f"Save failed: {e}", foreground="red")

    def _save_metadata(self, output_path: str):
        """Save metadata JSON alongside the GLB file."""
        meta_path = output_path.replace(".glb", "_meta.json")

        modifications = []
        for mat in self.materials:
            if mat.enabled:
                modifications.append({
                    "material": mat.name,
                    "original_color": mat.original_color,
                    "new_color": mat.base_color
                })

        metadata = {
            "source_file": os.path.basename(self.current_file),
            "output_file": os.path.basename(output_path),
            "timestamp": datetime.now().isoformat(),
            "modifications": modifications,
            "notes": ""
        }

        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _log_modification(self, output_path: str):
        """Append to modification history log."""
        log_path = os.path.join(self.output_dir, "modifications.txt")

        entry = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{os.path.basename(self.current_file)} -> "
            f"{os.path.basename(output_path)}\n"
        )

        with open(log_path, "a") as f:
            f.write(entry)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point."""
    if not PYGLTFLIB_AVAILABLE:
        print("=" * 60)
        print("ERROR: pygltflib is required but not installed.")
        print("Install it with: pip install pygltflib")
        print("=" * 60)

        # Still show GUI with error message
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Missing Dependency",
            "pygltflib is not installed.\n\n"
            "Install it with:\n  pip install pygltflib\n\n"
            "Then run this script again."
        )
        return

    root = tk.Tk()
    app = CharacterEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
