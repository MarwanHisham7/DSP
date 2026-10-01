import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import operations from dsp_operations.py
from dsp_operations import (
    read_signal_file,
    multiply_signal,
    shift_signal,
    fold_signal,
    add_signals,
    subtract_signals
)

# Configure theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AddSelectionModal(ctk.CTkToplevel):
    """Modal dialog with checkboxes to select signals for addition."""
    def __init__(self, parent, signal_keys, on_confirm):
        super().__init__(parent)
        self.title("Select Signals to Add")
        self.geometry("380x320")
        self.grab_set()  # Make window modal

        self.on_confirm = on_confirm
        self.checkbox_vars = {}

        ctk.CTkLabel(self, text="Choose signals to add:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        # Scrollable frame for checkboxes
        scroll_frame = ctk.CTkScrollableFrame(self, width=320, height=180)
        scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

        for key in signal_keys:
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(scroll_frame, text=key, variable=var)
            chk.pack(anchor="w", pady=4, padx=5)
            self.checkbox_vars[key] = var

        ctk.CTkButton(self, text="➕ Perform Addition", command=self._confirm).pack(pady=10)

    def _confirm(self):
        selected = [key for key, var in self.checkbox_vars.items() if var.get()]
        if len(selected) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 signals to perform addition.")
            return
        self.destroy()
        self.on_confirm(selected)


class SubtractionSelectionModal(ctk.CTkToplevel):
    """Modal dialog with dropdowns to select Signal 1 - Signal 2."""
    def __init__(self, parent, signal_keys, on_confirm):
        super().__init__(parent)
        self.title("Select Signals to Subtract")
        self.geometry("380x250")
        self.grab_set()

        self.on_confirm = on_confirm

        ctk.CTkLabel(self, text="Select operation order (Signal 1 - Signal 2):", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10)

        frame = ctk.CTkFrame(self)
        frame.pack(padx=15, pady=10, fill="x")

        ctk.CTkLabel(frame, text="First Signal (Minuend):").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.combo1 = ctk.CTkOptionMenu(frame, values=signal_keys)
        self.combo1.grid(row=0, column=1, padx=10, pady=8)
        if len(signal_keys) > 0:
            self.combo1.set(signal_keys[0])

        ctk.CTkLabel(frame, text="Second Signal (Subtrahend):").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.combo2 = ctk.CTkOptionMenu(frame, values=signal_keys)
        self.combo2.grid(row=1, column=1, padx=10, pady=8)
        if len(signal_keys) > 1:
            self.combo2.set(signal_keys[1])

        ctk.CTkButton(self, text="➖ Perform Subtraction", command=self._confirm).pack(pady=15)

    def _confirm(self):
        sig1 = self.combo1.get()
        sig2 = self.combo2.get()
        self.destroy()
        self.on_confirm(sig1, sig2)


class DSPSignalProcessorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DSP Task 1 - Signal Processor (Tabbed Interface)")
        self.geometry("1200x750")

        # Dictionary mapping tab_title -> {'indices': [...], 'values': [...]}
        self.tab_signals = {}

        self._build_gui()

    def _build_gui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar Controls
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="DSP Operations", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        # File Load Button
        ctk.CTkButton(self.sidebar, text="📁 Load Signal File", command=self.load_signal_file).pack(fill="x", padx=15, pady=5)

        # Active Signal Information
        ctk.CTkLabel(self.sidebar, text="Operations Target:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.active_tab_label = ctk.CTkLabel(self.sidebar, text="Active Tab: None", font=ctk.CTkFont(size=12, slant="italic"), text_color="#00a8e8")
        self.active_tab_label.pack(anchor="w", padx=15, pady=(2, 10))

        ctk.CTkLabel(self.sidebar, text="Single Signal Operations", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(5, 5))

        # Multiply
        multiply_frame = ctk.CTkFrame(self.sidebar)
        multiply_frame.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(multiply_frame, text="Multiply Const:").pack(side="left", padx=5)
        self.multiply_entry = ctk.CTkEntry(multiply_frame, width=60)
        self.multiply_entry.insert(0, "2.0")
        self.multiply_entry.pack(side="left", padx=5)
        ctk.CTkButton(multiply_frame, text="Multiply", command=self.handle_multiply).pack(side="right", padx=5)

        # Time Shifting
        shift_frame = ctk.CTkFrame(self.sidebar)
        shift_frame.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(shift_frame, text="Shift k steps:").pack(side="left", padx=5)
        self.shift_entry = ctk.CTkEntry(shift_frame, width=60)
        self.shift_entry.insert(0, "2")
        self.shift_entry.pack(side="left", padx=5)
        ctk.CTkButton(shift_frame, text="Shift", command=self.handle_shift).pack(side="right", padx=5)

        # Folding
        ctk.CTkButton(self.sidebar, text="🔄 Fold / Reverse x(-n)", command=self.handle_fold).pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(self.sidebar, text="Multi-Signal Operations", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(15, 5))

        # Addition / Subtraction with selection modals
        ctk.CTkButton(self.sidebar, text="➕ Add Selected Signals...", command=self.handle_add).pack(fill="x", padx=15, pady=4)
        ctk.CTkButton(self.sidebar, text="➖ Subtract Signals...", command=self.handle_subtract).pack(fill="x", padx=15, pady=4)

        # Tab Management
        ctk.CTkButton(self.sidebar, text="❌ Close Current Tab", command=self.close_current_tab, fg_color="#dc3545", hover_color="#c82333").pack(fill="x", padx=15, pady=(20, 5))

        # Right Area - Tabview Container
        self.plot_container = ctk.CTkFrame(self)
        self.plot_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.plot_container.grid_columnconfigure(0, weight=1)
        self.plot_container.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.plot_container, command=self.on_tab_changed)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Default Welcome Tab
        self.add_signal_tab("Welcome", [], [], title="No Signal Loaded")

    def get_unique_tab_title(self, base_title):
        title = base_title
        counter = 1
        while title in self.tab_signals or title in self.tabview._tab_dict:
            title = f"{base_title} ({counter})"
            counter += 1
        return title

    def add_signal_tab(self, base_title, indices, values, title=None):
        """Creates a new tab, plots the signal visually, and switches focus to it."""
        unique_title = self.get_unique_tab_title(base_title)
        tab_frame = self.tabview.add(unique_title)

        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)

        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#1e1e1e')

        if indices and values:
            markerline, stemlines, _ = ax.stem(
                indices, values, linefmt='#00a8e8', markerfmt='o', basefmt=' '
            )
            plt.setp(markerline, color='#00a8e8', markersize=6)
            plt.setp(stemlines, color='#00a8e8', linewidth=1.5)

            max_x = max(abs(min(indices)), abs(max(indices))) + 1
            max_y = max(abs(min(values)), abs(max(values)))

            y_margin = max(3, int(max_y * 0.15))
            ax.set_xlim(-max_x, max_x)
            ax.set_ylim(-max_y - y_margin, max_y + y_margin)

            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

            if max_y <= 15:
                ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
            elif max_y <= 30:
                ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
            elif max_y <= 60:
                ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
            else:
                ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=10))

            for idx, val in zip(indices, values):
                if val != 0:
                    y_offset = 6 if val >= 0 else -14
                    val_color = '#00e676' if val >= 0 else '#ff5252'
                    ax.annotate(
                        f'{val:g}',
                        (idx, val),
                        textcoords="offset points",
                        xytext=(0, y_offset),
                        ha='center',
                        fontsize=9,
                        fontweight='bold',
                        color=val_color
                    )

            self.tab_signals[unique_title] = {'indices': indices, 'values': values}
        else:
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

        ax.axhline(0, color='white', linewidth=1.2, linestyle='-')
        ax.axvline(0, color='white', linewidth=1.2, linestyle='-')

        plot_title = title if title else unique_title
        ax.set_title(plot_title, color='white', fontsize=14, pad=10)
        ax.set_xlabel("Sample Index (n)", color='white', fontsize=11)
        ax.set_ylabel("Amplitude x(n)", color='white', fontsize=11)
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        ax.tick_params(colors='white', labelsize=9)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=tab_frame)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        canvas.draw()

        self.tabview.set(unique_title)
        self.on_tab_changed()

    def on_tab_changed(self):
        current_tab = self.tabview.get()
        if current_tab and current_tab in self.tab_signals:
            self.active_tab_label.configure(text=f"Active Tab: {current_tab}")
        else:
            self.active_tab_label.configure(text="Active Tab: None")

    def get_active_signal(self):
        current_tab = self.tabview.get()
        if not current_tab or current_tab not in self.tab_signals:
            messagebox.showwarning("Warning", "Please select or open a valid signal tab first.")
            return None, None, None
        sig = self.tab_signals[current_tab]
        return current_tab, sig['indices'], sig['values']

    def load_signal_file(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if file_paths:
            for path in file_paths:
                try:
                    filename = os.path.basename(path)
                    indices, values = read_signal_file(path)
                    self.add_signal_tab(filename, indices, values)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read file {path}:\n{e}")

    def close_current_tab(self):
        current_tab = self.tabview.get()
        if current_tab:
            self.tabview.delete(current_tab)
            if current_tab in self.tab_signals:
                del self.tab_signals[current_tab]
            self.on_tab_changed()

    # --- GUI Event Handlers ---
    def handle_multiply(self):
        tab_name, indices, values = self.get_active_signal()
        if indices is None:
            return
        try:
            factor = float(self.multiply_entry.get())
            ind, val = multiply_signal(indices, values, factor)
            self.add_signal_tab(f"{tab_name} * {factor}", ind, val)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric constant.")

    def handle_shift(self):
        tab_name, indices, values = self.get_active_signal()
        if indices is None:
            return
        try:
            k = int(self.shift_entry.get())
            ind, val = shift_signal(indices, values, k)
            self.add_signal_tab(f"{tab_name} (Shift {k})", ind, val)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for shift k.")

    def handle_fold(self):
        tab_name, indices, values = self.get_active_signal()
        if indices is None:
            return
        ind, val = fold_signal(indices, values)
        self.add_signal_tab(f"Folded {tab_name}", ind, val)

    def handle_add(self):
        if len(self.tab_signals) < 2:
            messagebox.showwarning("Warning", "Open at least 2 signal tabs to perform addition.")
            return

        def execute_addition(selected_keys):
            subset_dict = {key: self.tab_signals[key] for key in selected_keys}
            ind, val = add_signals(subset_dict)
            self.add_signal_tab("Addition Result", ind, val)

        # Open selection dialog
        AddSelectionModal(self, list(self.tab_signals.keys()), execute_addition)

    def handle_subtract(self):
        if len(self.tab_signals) < 2:
            messagebox.showwarning("Warning", "Open at least 2 signal tabs to perform subtraction.")
            return

        def execute_subtraction(sig1_key, sig2_key):
            ind, val = subtract_signals(self.tab_signals[sig1_key], self.tab_signals[sig2_key])
            self.add_signal_tab(f"Sub ({sig1_key} - {sig2_key})", ind, val)

        # Open selection dialog
        SubtractionSelectionModal(self, list(self.tab_signals.keys()), execute_subtraction)


if __name__ == "__main__":
    app = DSPSignalProcessorApp()
    app.mainloop()