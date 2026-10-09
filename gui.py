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
    subtract_signals,
    generate_sinusoidal_signal
)

# Design Palette (Modern Slate Dark Theme)
BG_DARK = "#121212"
CARD_BG = "#1E1E1E"
SIDEBAR_BG = "#181818"
ACCENT_BLUE = "#00ADB5"
ACCENT_GREEN = "#10B981"
ACCENT_PURPLE = "#6366F1"
ACCENT_RED = "#EF4444"
TEXT_PRIMARY = "#EEEEEE"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

COLOR_PALETTE = [
    '#00ADB5',  # Cyan
    '#10B981',  # Emerald
    '#6366F1',  # Indigo
    '#F59E0B',  # Amber
    '#EC4899',  # Pink
    '#8B5CF6',  # Violet
    '#3B82F6',  # Blue
    '#14B8A6'   # Teal
]


class SignalGeneratorModal(ctk.CTkToplevel):
    """Modal window for Sinusoidal / Cosinusoidal Signal Generation."""
    def __init__(self, parent, on_generate):
        super().__init__(parent)
        self.title("Signal Generator")
        self.geometry("400x480")
        self.configure(fg_color=BG_DARK)
        self.grab_set()

        self.on_generate = on_generate

        ctk.CTkLabel(self, text="Generate Waveform", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_PRIMARY).pack(pady=(18, 10))

        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10)
        form.pack(padx=20, pady=10, fill="both", expand=True)

        ctk.CTkLabel(form, text="Wave Type:").grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.wave_type = ctk.CTkOptionMenu(form, values=["Sine Wave", "Cosine Wave"], fg_color=ACCENT_BLUE, button_color=ACCENT_BLUE)
        self.wave_type.grid(row=0, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Amplitude (A):").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.amp_entry = ctk.CTkEntry(form, width=120, fg_color=BG_DARK)
        self.amp_entry.insert(0, "1.0")
        self.amp_entry.grid(row=1, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Phase Shift (θ °):").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.phase_entry = ctk.CTkEntry(form, width=120, fg_color=BG_DARK)
        self.phase_entry.insert(0, "0.0")
        self.phase_entry.grid(row=2, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Analog Freq f (Hz):").grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.freq_entry = ctk.CTkEntry(form, width=120, fg_color=BG_DARK)
        self.freq_entry.insert(0, "10.0")
        self.freq_entry.grid(row=3, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Sampling Freq fs (Hz):").grid(row=4, column=0, padx=15, pady=10, sticky="w")
        self.fs_entry = ctk.CTkEntry(form, width=120, fg_color=BG_DARK)
        self.fs_entry.insert(0, "100.0")
        self.fs_entry.grid(row=4, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Duration (sec):").grid(row=5, column=0, padx=15, pady=10, sticky="w")
        self.dur_entry = ctk.CTkEntry(form, width=120, fg_color=BG_DARK)
        self.dur_entry.insert(0, "1.0")
        self.dur_entry.grid(row=5, column=1, padx=15, pady=10)

        ctk.CTkButton(self, text="Generate Signal", command=self._confirm, fg_color=ACCENT_GREEN, hover_color="#059669", height=38, font=ctk.CTkFont(weight="bold")).pack(pady=18)

    def _confirm(self):
        try:
            wave = "sine" if "Sine" in self.wave_type.get() else "cosine"
            amp = float(self.amp_entry.get())
            phase = float(self.phase_entry.get())
            f = float(self.freq_entry.get())
            fs = float(self.fs_entry.get())
            dur = float(self.dur_entry.get())

            if fs < 2 * f:
                proceed = messagebox.askyesno(
                    "Nyquist Warning",
                    f"fs ({fs} Hz) is less than 2*f ({2*f} Hz).\n"
                    "This violates Sampling Theorem and causes Aliasing!\n\nGenerate anyway?"
                )
                if not proceed:
                    return

            self.destroy()
            self.on_generate(wave, amp, phase, f, fs, dur)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric parameters.")


class AddSelectionModal(ctk.CTkToplevel):
    """Modal dialog to select signals for addition."""
    def __init__(self, parent, signal_keys, on_confirm):
        super().__init__(parent)
        self.title("Select Signals to Add")
        self.geometry("380x320")
        self.configure(fg_color=BG_DARK)
        self.grab_set()

        self.on_confirm = on_confirm
        self.checkbox_vars = {}

        ctk.CTkLabel(self, text="Select signals to add:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=12)

        scroll_frame = ctk.CTkScrollableFrame(self, width=320, height=180, fg_color=CARD_BG)
        scroll_frame.pack(pady=5, padx=15, fill="both", expand=True)

        for key in signal_keys:
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(scroll_frame, text=key, variable=var, fg_color=ACCENT_BLUE)
            chk.pack(anchor="w", pady=6, padx=8)
            self.checkbox_vars[key] = var

        ctk.CTkButton(self, text="➕ Perform Addition", command=self._confirm, fg_color=ACCENT_BLUE, height=36).pack(pady=12)

    def _confirm(self):
        selected = [key for key, var in self.checkbox_vars.items() if var.get()]
        if len(selected) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 signals to perform addition.")
            return
        self.destroy()
        self.on_confirm(selected)


class SubtractionSelectionModal(ctk.CTkToplevel):
    """Modal dialog to select Signal 1 - Signal 2."""
    def __init__(self, parent, signal_keys, on_confirm):
        super().__init__(parent)
        self.title("Select Signals to Subtract")
        self.geometry("380x250")
        self.configure(fg_color=BG_DARK)
        self.grab_set()

        self.on_confirm = on_confirm

        ctk.CTkLabel(self, text="Subtraction Order (Signal 1 - Signal 2):", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=12)

        frame = ctk.CTkFrame(self, fg_color=CARD_BG)
        frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(frame, text="First Signal (Minuend):").grid(row=0, column=0, padx=12, pady=10, sticky="w")
        self.combo1 = ctk.CTkOptionMenu(frame, values=signal_keys, fg_color=ACCENT_PURPLE, button_color=ACCENT_PURPLE)
        self.combo1.grid(row=0, column=1, padx=12, pady=10)
        if len(signal_keys) > 0:
            self.combo1.set(signal_keys[0])

        ctk.CTkLabel(frame, text="Second Signal (Subtrahend):").grid(row=1, column=0, padx=12, pady=10, sticky="w")
        self.combo2 = ctk.CTkOptionMenu(frame, values=signal_keys, fg_color=ACCENT_PURPLE, button_color=ACCENT_PURPLE)
        self.combo2.grid(row=1, column=1, padx=12, pady=10)
        if len(signal_keys) > 1:
            self.combo2.set(signal_keys[1])

        ctk.CTkButton(self, text="➖ Perform Subtraction", command=self._confirm, fg_color=ACCENT_PURPLE, height=36).pack(pady=15)

    def _confirm(self):
        sig1 = self.combo1.get()
        sig2 = self.combo2.get()
        self.destroy()
        self.on_confirm(sig1, sig2)


class DSPSignalProcessorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DSP Signal Processing Studio")
        self.geometry("1300x820")
        self.configure(fg_color=BG_DARK)

        # Main Data Dictionary: {title: {'indices': [...], 'values': [...], 'color': '#...'}}
        self.signals = {}

        self._build_gui()

    def _build_gui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar Frame
        self.sidebar = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color=SIDEBAR_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Title Header
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=18, pady=(18, 10))
        ctk.CTkLabel(header_frame, text="DSP Studio", font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")

        # Load / Generate Section
        ctk.CTkButton(self.sidebar, text="📁 Load Signal File", command=self.load_signal_file, fg_color=ACCENT_BLUE, hover_color="#008B92", height=36, font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=18, pady=4)
        ctk.CTkButton(self.sidebar, text="🌊 Signal Generation", command=self.open_signal_generator, fg_color="#14B8A6", hover_color="#0D9488", height=36, font=ctk.CTkFont(weight="bold")).pack(fill="x", padx=18, pady=4)

        # Active Target Selector Box
        target_card = ctk.CTkFrame(self.sidebar, fg_color=CARD_BG, corner_radius=10)
        target_card.pack(fill="x", padx=18, pady=(12, 6))

        ctk.CTkLabel(target_card, text="Active Target Signal", font=ctk.CTkFont(size=12, weight="bold"), text_color="#A1A1AA").pack(anchor="w", padx=12, pady=(10, 2))
        self.target_dropdown = ctk.CTkOptionMenu(target_card, values=["None"], fg_color=BG_DARK, button_color="#3F3F46")
        self.target_dropdown.pack(fill="x", padx=12, pady=(0, 10))

        # Representation Segmented Toggle
        ctk.CTkLabel(self.sidebar, text="Plot Representation", font=ctk.CTkFont(size=12, weight="bold"), text_color="#A1A1AA").pack(anchor="w", padx=18, pady=(10, 2))
        self.rep_mode = ctk.CTkSegmentedButton(self.sidebar, values=["Discrete (Stem)", "Continuous (Line)"], command=lambda _: self.plot_all_signals(), selected_color=ACCENT_BLUE)
        self.rep_mode.set("Discrete (Stem)")
        self.rep_mode.pack(fill="x", padx=18, pady=4)

        # Operations Section Header
        ctk.CTkLabel(self.sidebar, text="Single Operations", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(14, 4))

        # Multiply
        mult_card = ctk.CTkFrame(self.sidebar, fg_color=CARD_BG, corner_radius=8)
        mult_card.pack(fill="x", padx=18, pady=4)
        ctk.CTkLabel(mult_card, text="Factor:").pack(side="left", padx=10)
        self.multiply_entry = ctk.CTkEntry(mult_card, width=65, fg_color=BG_DARK)
        self.multiply_entry.insert(0, "2.0")
        self.multiply_entry.pack(side="left", padx=5)
        ctk.CTkButton(mult_card, text="Multiply", command=self.handle_multiply, width=90, fg_color="#3B82F6").pack(side="right", padx=8, pady=6)

        # Shift
        shift_card = ctk.CTkFrame(self.sidebar, fg_color=CARD_BG, corner_radius=8)
        shift_card.pack(fill="x", padx=18, pady=4)
        ctk.CTkLabel(shift_card, text="Shift k:").pack(side="left", padx=10)
        self.shift_entry = ctk.CTkEntry(shift_card, width=65, fg_color=BG_DARK)
        self.shift_entry.insert(0, "2")
        self.shift_entry.pack(side="left", padx=5)
        ctk.CTkButton(shift_card, text="Shift", command=self.handle_shift, width=90, fg_color="#3B82F6").pack(side="right", padx=8, pady=6)

        # Fold
        ctk.CTkButton(self.sidebar, text="🔄 Fold / Reverse x(-n)", command=self.handle_fold, fg_color="#3B82F6", height=34).pack(fill="x", padx=18, pady=4)

        # Multi-Signal Operations Header
        ctk.CTkLabel(self.sidebar, text="Multi-Signal Operations", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(14, 4))
        ctk.CTkButton(self.sidebar, text="➕ Add Selected Signals", command=self.handle_add, fg_color=ACCENT_PURPLE, height=34).pack(fill="x", padx=18, pady=3)
        ctk.CTkButton(self.sidebar, text="➖ Subtract Signals", command=self.handle_subtract, fg_color=ACCENT_PURPLE, height=34).pack(fill="x", padx=18, pady=3)

        # Management
        ctk.CTkLabel(self.sidebar, text="Workspace", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(14, 4))
        ctk.CTkButton(self.sidebar, text="❌ Remove Target", command=self.remove_target_signal, fg_color=ACCENT_RED, hover_color="#DC2626", height=32).pack(fill="x", padx=18, pady=3)
        ctk.CTkButton(self.sidebar, text="🧹 Clear Workspace", command=self.clear_all_signals, fg_color="#4B5563", hover_color="#374151", height=32).pack(fill="x", padx=18, pady=3)

        # Right Plot Area Card
        self.plot_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

        self.fig, self.ax = plt.subplots(figsize=(7, 5), dpi=100)
        self.fig.patch.set_facecolor(CARD_BG)
        self.ax.set_facecolor(BG_DARK)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)

        self.plot_all_signals()

    def get_unique_signal_title(self, base_title):
        title = base_title
        counter = 1
        while title in self.signals:
            title = f"{base_title} ({counter})"
            counter += 1
        return title

    def add_signal_to_workspace(self, base_title, indices, values):
        unique_title = self.get_unique_signal_title(base_title)
        color = COLOR_PALETTE[len(self.signals) % len(COLOR_PALETTE)]

        self.signals[unique_title] = {
            'indices': indices,
            'values': values,
            'color': color
        }

        self.update_target_dropdown(select_title=unique_title)
        self.plot_all_signals()

    def update_target_dropdown(self, select_title=None):
        keys = list(self.signals.keys())
        if keys:
            self.target_dropdown.configure(values=keys)
            if select_title and select_title in keys:
                self.target_dropdown.set(select_title)
            elif self.target_dropdown.get() not in keys:
                self.target_dropdown.set(keys[0])
        else:
            self.target_dropdown.configure(values=["None"])
            self.target_dropdown.set("None")

    def plot_all_signals(self):
        self.ax.clear()
        self.fig.patch.set_facecolor(CARD_BG)
        self.ax.set_facecolor(BG_DARK)

        mode = "continuous" if "Continuous" in self.rep_mode.get() else "discrete"

        if self.signals:
            all_indices = []
            all_values = []

            for title, sig in self.signals.items():
                ind, val, color = sig['indices'], sig['values'], sig['color']
                all_indices.extend(ind)
                all_values.extend(val)

                if mode == "discrete":
                    mline, sline, _ = self.ax.stem(ind, val, linefmt=color, markerfmt='o', basefmt=' ', label=title)
                    # Slightly smaller markers so dense 100-sample signals render clearly
                    plt.setp(mline, color=color, markersize=3.5)
                    plt.setp(sline, color=color, linewidth=1.2)
                else:
                    self.ax.plot(ind, val, color=color, linewidth=1.8, marker='o', markersize=3, label=title)

            min_n, max_n = min(all_indices), max(all_indices)
            min_val, max_val = min(all_values), max(all_values)

            # SMART X-AXIS BOUNDS (stretches generated signals cleanly instead of wasting empty negative space)
            if min_n < 0 and max_n > 0:
                bound_x = max(abs(min_n), abs(max_n)) + 1
                self.ax.set_xlim(-bound_x, bound_x)
                x_span = 2 * bound_x
            elif min_n >= 0:
                self.ax.set_xlim(-2, max_n + 2)
                x_span = max_n + 4
            else:
                self.ax.set_xlim(min_n - 2, 2)
                x_span = abs(min_n) + 4

            # DYNAMIC X-AXIS TICKS (prevents text overlapping when sample count is high)
            if x_span <= 25:
                self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
            elif x_span <= 60:
                self.ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
            elif x_span <= 120:
                self.ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
            else:
                self.ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=12, integer=True))

            # Y-AXIS BOUNDS & TICKS
            abs_max_y = max(abs(min_val), abs(max_val))
            y_margin = max(0.5, abs_max_y * 0.15)
            self.ax.set_ylim(-abs_max_y - y_margin, abs_max_y + y_margin)

            if abs_max_y <= 15:
                self.ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
            else:
                self.ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=8, integer=True))

            self.ax.legend(facecolor=CARD_BG, edgecolor='#3F3F46', labelcolor=TEXT_PRIMARY, loc='upper right', fontsize=9)
        else:
            self.ax.set_xlim(-5, 5)
            self.ax.set_ylim(-5, 5)
            self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

        # Origin reference lines
        self.ax.axhline(0, color='white', linewidth=1.2, alpha=0.8)
        self.ax.axvline(0, color='white', linewidth=1.2, alpha=0.8)

        self.ax.set_title("Signal Visualization", color=TEXT_PRIMARY, fontsize=13, pad=12, fontweight='bold')
        self.ax.set_xlabel("Sample Index (n)", color=TEXT_PRIMARY, fontsize=10)
        self.ax.set_ylabel("Amplitude x(n)", color=TEXT_PRIMARY, fontsize=10)
        self.ax.grid(True, linestyle=':', alpha=0.25, color='#A1A1AA')
        self.ax.tick_params(colors=TEXT_PRIMARY, labelsize=9)

        self.fig.tight_layout()
        self.canvas.draw()

    def get_active_signal(self):
        target = self.target_dropdown.get()
        if not target or target not in self.signals:
            messagebox.showwarning("Warning", "Please select a valid target signal first.")
            return None, None, None
        sig = self.signals[target]
        return target, sig['indices'], sig['values']

    def load_signal_file(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if file_paths:
            for path in file_paths:
                try:
                    filename = os.path.basename(path)
                    indices, values = read_signal_file(path)
                    self.add_signal_to_workspace(filename, indices, values)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read file {path}:\n{e}")

    def open_signal_generator(self):
        def on_gen(wave, amp, phase, f, fs, dur):
            ind, val = generate_sinusoidal_signal(wave, amp, phase, f, fs, dur)
            title = f"{wave.title()} (f={f}Hz)"
            self.add_signal_to_workspace(title, ind, val)

        SignalGeneratorModal(self, on_gen)

    def remove_target_signal(self):
        target = self.target_dropdown.get()
        if target in self.signals:
            del self.signals[target]
            self.update_target_dropdown()
            self.plot_all_signals()

    def clear_all_signals(self):
        self.signals.clear()
        self.update_target_dropdown()
        self.plot_all_signals()

    # --- Operation Handlers ---
    def handle_multiply(self):
        target, indices, values = self.get_active_signal()
        if indices is None:
            return
        try:
            factor = float(self.multiply_entry.get())
            ind, val = multiply_signal(indices, values, factor)
            self.add_signal_to_workspace(f"{target} * {factor}", ind, val)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric constant.")

    def handle_shift(self):
        target, indices, values = self.get_active_signal()
        if indices is None:
            return
        try:
            k = int(self.shift_entry.get())
            ind, val = shift_signal(indices, values, k)
            self.add_signal_to_workspace(f"{target} (Shift {k})", ind, val)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer for shift k.")

    def handle_fold(self):
        target, indices, values = self.get_active_signal()
        if indices is None:
            return
        ind, val = fold_signal(indices, values)
        self.add_signal_to_workspace(f"Folded {target}", ind, val)

    def handle_add(self):
        if len(self.signals) < 2:
            messagebox.showwarning("Warning", "Load or generate at least 2 signals to perform addition.")
            return

        def execute_addition(selected_keys):
            subset_dict = {key: self.signals[key] for key in selected_keys}
            ind, val = add_signals(subset_dict)
            self.add_signal_to_workspace("Addition Result", ind, val)

        AddSelectionModal(self, list(self.signals.keys()), execute_addition)

    def handle_subtract(self):
        if len(self.signals) < 2:
            messagebox.showwarning("Warning", "Load or generate at least 2 signals to perform subtraction.")
            return

        def execute_subtraction(sig1_key, sig2_key):
            ind, val = subtract_signals(self.signals[sig1_key], self.signals[sig2_key])
            self.add_signal_to_workspace(f"Sub ({sig1_key} - {sig2_key})", ind, val)

        SubtractionSelectionModal(self, list(self.signals.keys()), execute_subtraction)


if __name__ == "__main__":
    app = DSPSignalProcessorApp()
    app.mainloop()