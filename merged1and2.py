import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np

from matplotlib.figure import Figure
from matplotlib.artist import setp
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import operations from dsp_operations.py (must be in the same folder)
from dsp_operations import (
    read_signal_file,
    multiply_signal,
    shift_signal,
    fold_signal,
    add_signals,
    subtract_signals
)


class SignalProcessingGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Signal Processing Framework")
        self.root.geometry("1000x720")
        self.root.minsize(1000, 720)
        self.root.resizable(True, True)

        # =========================
        # COLORS
        # =========================
        self.bg_color = "#0B1F3A"
        self.panel_color = "#163A5F"
        self.control_color = "#DCEEFF"
        self.white = "#FFFFFF"

        # Graph colors
        self.signal_colors = {
            1: "#1F77B4",
            2: "#FF7F0E"
        }
        self.result_color = "#2CA02C"

        self.root.configure(bg=self.bg_color)

        # =========================
        # DATA
        # =========================
        # Each signal is a dict:
        # {"indices": [...], "values": [...], "kind": "file" / "generate", ...}
        self.signals = {1: None, 2: None}
        self.result = None

        # =========================
        # CONTROL STORAGE
        # =========================
        self.source_vars = {}
        self.file_labels = {}
        self.file_frames = {}
        self.generate_frames = {}
        self.controls = {1: {}, 2: {}}

        self.target_var = tk.IntVar(value=1)

        self.create_menu()
        self.create_gui()
        self.create_graphs()

    # =========================
    # MENU
    # =========================
    def create_menu(self):

        menu_bar = tk.Menu(self.root)

        # =========================
        # SIGNAL GENERATION MENU
        # =========================
        signal_menu = tk.Menu(
            menu_bar,
            tearoff=0
        )

        signal_menu.add_command(
            label="Sine Wave",
            command=lambda: self.select_signal_from_menu("Sine")
        )

        signal_menu.add_command(
            label="Cosine Wave",
            command=lambda: self.select_signal_from_menu("Cosine")
        )

        menu_bar.add_cascade(
            label="Signal Generation",
            menu=signal_menu
        )

        # =========================
        # DISPLAY TYPE MENU
        # =========================
        display_menu = tk.Menu(
            menu_bar,
            tearoff=0
        )

        display_menu.add_command(
            label="Continuous",
            command=lambda: self.select_display_from_menu("Continuous")
        )

        display_menu.add_command(
            label="Discrete",
            command=lambda: self.select_display_from_menu("Discrete")
        )

        menu_bar.add_cascade(
            label="Display Type",
            menu=display_menu
        )

        self.root.config(menu=menu_bar)

    # =========================
    # SIGNAL MENU SELECTION  (controls both signals)
    # =========================
    def select_signal_from_menu(self, signal_type):

        self.controls[1]["type"].set(signal_type)
        self.controls[2]["type"].set(signal_type)

    # =========================
    # DISPLAY MENU SELECTION  (controls both signals)
    # =========================
    def select_display_from_menu(self, display_type):

        self.controls[1]["display"].set(display_type)
        self.controls[2]["display"].set(display_type)

    # =========================
    # GUI
    # =========================
    def create_gui(self):

        main_frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )

        main_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        # =========================
        # TITLE
        # =========================
        title = tk.Label(
            main_frame,
            text="Signal Processing Framework",
            font=("Arial", 22, "bold"),
            bg=self.bg_color,
            fg=self.white
        )

        title.pack(pady=8)

        # =========================
        # CONTENT
        # =========================
        content_frame = tk.Frame(
            main_frame,
            bg=self.bg_color
        )

        content_frame.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(0, 10)
        )

        # =========================
        # LEFT CONTROL PANEL
        # =========================
        self.control_frame = tk.Frame(
            content_frame,
            bg=self.control_color,
            width=440,
            height=650,
            relief="ridge",
            bd=2
        )

        self.control_frame.pack(
            side=tk.LEFT,
            fill=tk.Y,
            padx=10
        )

        self.control_frame.pack_propagate(False)

        # Signal 1
        self.create_signal_controls(
            self.control_frame,
            1
        )

        # Signal 2
        self.create_signal_controls(
            self.control_frame,
            2
        )

        # =========================
        # BUTTONS
        # =========================
        button_frame = tk.Frame(
            self.control_frame,
            bg=self.control_color
        )

        button_frame.pack(pady=4)

        # Generate Both
        generate_both_button = tk.Button(
            button_frame,
            text="Generate Both Signals",
            command=self.generate_both_signals,
            font=("Arial", 11, "bold"),
            bg=self.panel_color,
            fg="white",
            width=20,
            height=1
        )

        generate_both_button.grid(
            row=0,
            column=0,
            padx=5
        )

        # Clear
        clear_button = tk.Button(
            button_frame,
            text="Clear All",
            command=self.clear,
            font=("Arial", 11, "bold"),
            bg="#B22222",
            fg="white",
            width=10,
            height=1
        )

        clear_button.grid(
            row=0,
            column=1,
            padx=5
        )

        # Operations
        self.create_operation_controls(
            self.control_frame
        )

        # =========================
        # RIGHT GRAPH PANEL
        # =========================
        self.graph_frame = tk.Frame(
            content_frame,
            bg=self.panel_color,
            width=520,
            height=650,
            relief="ridge",
            bd=2
        )

        self.graph_frame.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True,
            padx=10
        )

        self.graph_frame.pack_propagate(False)

    # =========================
    # SMALL WIDGET HELPERS
    # =========================
    def add_field(self, parent, text, default, row, column):

        tk.Label(
            parent,
            text=text,
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=row,
            column=column,
            padx=4,
            pady=2,
            sticky="w"
        )

        entry = tk.Entry(
            parent,
            width=9
        )

        entry.insert(0, default)

        entry.grid(
            row=row,
            column=column + 1,
            padx=4,
            pady=2
        )

        return entry

    def add_combo(self, parent, text, values, default, row, column):

        tk.Label(
            parent,
            text=text,
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=row,
            column=column,
            padx=4,
            pady=2,
            sticky="w"
        )

        combo = ttk.Combobox(
            parent,
            values=values,
            state="readonly",
            width=10
        )

        combo.set(default)

        combo.grid(
            row=row,
            column=column + 1,
            padx=4,
            pady=2
        )

        return combo

    # =========================
    # SIGNAL CONTROLS
    # =========================
    def create_signal_controls(self, parent, signal_number):

        frame = tk.LabelFrame(
            parent,
            text=f"Signal {signal_number}",
            font=("Arial", 12, "bold"),
            bg=self.control_color,
            fg=self.bg_color
        )

        frame.pack(
            padx=15,
            pady=3,
            fill="x"
        )

        # =========================
        # SOURCE CHOICE
        # =========================
        source_var = tk.StringVar(value="Load")

        self.source_vars[signal_number] = source_var

        source_row = tk.Frame(
            frame,
            bg=self.control_color
        )

        source_row.pack(
            anchor="w",
            padx=8,
            pady=1
        )

        tk.Label(
            source_row,
            text="Source:",
            bg=self.control_color,
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            source_row,
            text="Load from file",
            variable=source_var,
            value="Load",
            bg=self.control_color,
            activebackground=self.control_color,
            command=lambda: self.change_source(signal_number)
        ).pack(
            side=tk.LEFT,
            padx=8
        )

        tk.Radiobutton(
            source_row,
            text="Generate",
            variable=source_var,
            value="Generate",
            bg=self.control_color,
            activebackground=self.control_color,
            command=lambda: self.change_source(signal_number)
        ).pack(
            side=tk.LEFT,
            padx=8
        )

        # =========================
        # SWITCHABLE AREA
        # =========================
        container = tk.Frame(
            frame,
            bg=self.control_color,
            width=390,
            height=112
        )

        container.pack(
            padx=8,
            pady=1
        )

        container.pack_propagate(False)

        # =========================
        # LOAD FROM FILE
        # =========================
        file_frame = tk.Frame(
            container,
            bg=self.control_color
        )

        browse_button = tk.Button(
            file_frame,
            text="Browse...",
            command=lambda: self.browse_file(signal_number),
            font=("Arial", 10, "bold"),
            bg=self.panel_color,
            fg="white",
            width=16
        )

        browse_button.pack(
            pady=(20, 8)
        )

        file_label = tk.Label(
            file_frame,
            text="File: (none)",
            bg=self.control_color,
            font=("Arial", 10)
        )

        file_label.pack()

        self.file_frames[signal_number] = file_frame
        self.file_labels[signal_number] = file_label

        # =========================
        # GENERATE
        # =========================
        generate_frame = tk.Frame(
            container,
            bg=self.control_color
        )

        controls = self.controls[signal_number]

        controls["type"] = self.add_combo(
            generate_frame,
            "Type:",
            ["Sine", "Cosine"],
            "Sine" if signal_number == 1 else "Cosine",
            0,
            0
        )

        controls["display"] = self.add_combo(
            generate_frame,
            "Display:",
            ["Continuous", "Discrete"],
            "Continuous" if signal_number == 1 else "Discrete",
            0,
            2
        )

        controls["amplitude"] = self.add_field(
            generate_frame,
            "Amplitude A:",
            "1",
            1,
            0
        )

        controls["frequency"] = self.add_field(
            generate_frame,
            "Frequency f:",
            "5",
            1,
            2
        )

        controls["phase"] = self.add_field(
            generate_frame,
            "Phase θ (deg):",
            "0",
            2,
            0
        )

        controls["sampling"] = self.add_field(
            generate_frame,
            "Sampling Fs:",
            "20",
            2,
            2
        )

        generate_button = tk.Button(
            generate_frame,
            text=f"Generate Signal {signal_number}",
            command=lambda: self.generate_signal(signal_number),
            font=("Arial", 10, "bold"),
            bg=self.panel_color,
            fg="white",
            width=22
        )

        generate_button.grid(
            row=3,
            column=0,
            columnspan=4,
            pady=4
        )

        self.generate_frames[signal_number] = generate_frame

        # Show the correct area at start
        self.show_source_frame(signal_number)

    # =========================
    # OPERATION CONTROLS
    # =========================
    def create_operation_controls(self, parent):

        frame = tk.LabelFrame(
            parent,
            text="Operations",
            font=("Arial", 12, "bold"),
            bg=self.control_color,
            fg=self.bg_color
        )

        frame.pack(
            padx=15,
            pady=3,
            fill="x"
        )

        # =========================
        # APPLY TO
        # =========================
        target_row = tk.Frame(
            frame,
            bg=self.control_color
        )

        target_row.pack(
            anchor="w",
            padx=8,
            pady=1
        )

        tk.Label(
            target_row,
            text="Apply to:",
            bg=self.control_color,
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            target_row,
            text="Signal 1",
            variable=self.target_var,
            value=1,
            bg=self.control_color,
            activebackground=self.control_color
        ).pack(
            side=tk.LEFT,
            padx=8
        )

        tk.Radiobutton(
            target_row,
            text="Signal 2",
            variable=self.target_var,
            value=2,
            bg=self.control_color,
            activebackground=self.control_color
        ).pack(
            side=tk.LEFT,
            padx=8
        )

        # =========================
        # NUMBER
        # =========================
        number_row = tk.Frame(
            frame,
            bg=self.control_color
        )

        number_row.pack(
            anchor="w",
            padx=8,
            pady=1
        )

        tk.Label(
            number_row,
            text="Number:",
            bg=self.control_color,
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)

        self.number_entry = tk.Entry(
            number_row,
            width=10
        )

        self.number_entry.insert(0, "2")

        self.number_entry.pack(
            side=tk.LEFT,
            padx=8
        )

        tk.Label(
            number_row,
            text="(constant, or shift k for Shift)",
            bg=self.control_color,
            font=("Arial", 9, "italic")
        ).pack(side=tk.LEFT)

        # =========================
        # BUTTONS
        # =========================
        button_frame = tk.Frame(
            frame,
            bg=self.control_color
        )

        button_frame.pack(
            pady=2
        )

        buttons = [
            ("Multiply", self.handle_multiply, self.panel_color, 0, 0),
            ("Shift", self.handle_shift, self.panel_color, 0, 1),
            ("Fold", self.handle_fold, self.panel_color, 0, 2),
            ("Add Number", self.handle_add_number, self.panel_color, 1, 0),
            ("Subtract Number", self.handle_subtract_number, self.panel_color, 1, 1),
            ("Reset Result", self.reset_result, "#6C757D", 1, 2),
            ("Add 1 + 2", self.handle_add, self.panel_color, 2, 0),
            ("Subtract 1 - 2", self.handle_subtract, self.panel_color, 2, 1)
        ]

        for text, command, color, row, column in buttons:

            tk.Button(
                button_frame,
                text=text,
                command=command,
                font=("Arial", 10, "bold"),
                bg=color,
                fg="white",
                width=15
            ).grid(
                row=row,
                column=column,
                padx=3,
                pady=3
            )

    # =========================
    # GRAPHS
    # =========================
    def create_graphs(self):

        # Graph 1 : input signals
        self.figure1 = Figure(
            figsize=(5, 2.9),
            dpi=100
        )

        self.ax1 = self.figure1.add_subplot(111)

        self.canvas1 = FigureCanvasTkAgg(
            self.figure1,
            master=self.graph_frame
        )

        self.canvas1.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=6
        )

        self.canvas1.get_tk_widget().bind(
            "<Configure>",
            lambda event: self.fit_graph(self.figure1, self.canvas1),
            add="+"
        )

        # Graph 2 : result
        self.figure2 = Figure(
            figsize=(5, 2.9),
            dpi=100
        )

        self.ax2 = self.figure2.add_subplot(111)

        self.canvas2 = FigureCanvasTkAgg(
            self.figure2,
            master=self.graph_frame
        )

        self.canvas2.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=6
        )

        self.canvas2.get_tk_widget().bind(
            "<Configure>",
            lambda event: self.fit_graph(self.figure2, self.canvas2),
            add="+"
        )

        self.draw_inputs()
        self.draw_result()

    # =========================
    # KEEP GRAPH LAYOUT NEAT WHEN THE WINDOW IS RESIZED
    # =========================
    def fit_graph(self, figure, canvas):

        try:

            figure.tight_layout()

            canvas.draw_idle()

        except Exception:

            pass

    # =========================
    # SOURCE SWITCHING
    # =========================
    def show_source_frame(self, signal_number):

        self.file_frames[signal_number].pack_forget()
        self.generate_frames[signal_number].pack_forget()

        if self.source_vars[signal_number].get() == "Load":

            self.file_frames[signal_number].pack(
                fill="both",
                expand=True
            )

        else:

            self.generate_frames[signal_number].pack(
                fill="both",
                expand=True
            )

    def change_source(self, signal_number):

        # Switching the source removes the old signal
        self.signals[signal_number] = None

        self.file_labels[signal_number].config(
            text="File: (none)"
        )

        self.show_source_frame(signal_number)

        self.draw_inputs()

    # =========================
    # LOAD FROM FILE
    # =========================
    def browse_file(self, signal_number):

        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )

        if not path:
            return

        try:

            indices, values = read_signal_file(path)

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to read file:\n{path}\n\n{e}"
            )

            return

        filename = os.path.basename(path)

        self.signals[signal_number] = {
            "kind": "file",
            "name": filename,
            "indices": list(indices),
            "values": list(values)
        }

        self.file_labels[signal_number].config(
            text=f"File: {filename}"
        )

        self.draw_inputs()

    # =========================
    # GENERATE ONE SIGNAL
    # =========================
    def generate_signal(self, signal_number):

        controls = self.controls[signal_number]

        try:

            signal_type = controls["type"].get()

            A = float(
                controls["amplitude"].get()
            )

            f = float(
                controls["frequency"].get()
            )

            theta = float(
                controls["phase"].get()
            )

            Fs = float(
                controls["sampling"].get()
            )

            display = controls["display"].get()

            # =========================
            # VALIDATION
            # =========================
            if A < 0:

                messagebox.showerror(
                    "Error",
                    "Amplitude must be positive."
                )

                return False

            if f <= 0:

                messagebox.showerror(
                    "Error",
                    "Frequency must be greater than 0."
                )

                return False

            if Fs <= 0:

                messagebox.showerror(
                    "Error",
                    "Sampling frequency must be greater than 0."
                )

                return False

            # =========================
            # SAMPLING THEOREM
            # =========================
            if Fs < 2 * f:

                messagebox.showerror(
                    "Sampling Theorem",
                    f"Sampling frequency must satisfy:\n\n"
                    f"Fs ≥ 2f\n\n"
                    f"Fs = {Fs}\n"
                    f"2f = {2 * f}"
                )

                return False

            # =========================
            # PHASE
            # =========================
            theta_rad = np.deg2rad(theta)

            duration = 1

            if signal_type == "Sine":
                wave = np.sin
            else:
                wave = np.cos

            # Continuous time
            t_continuous = np.linspace(
                0,
                duration,
                1000
            )

            y_continuous = A * wave(
                2 * np.pi * f * t_continuous
                + theta_rad
            )

            # Sampled points  n = 0, 1, 2, ...
            samples = max(
                int(round(Fs * duration)),
                1
            )

            n = np.arange(samples)

            t_sampled = n / Fs

            y_sampled = A * wave(
                2 * np.pi * f * t_sampled
                + theta_rad
            )

            # =========================
            # STORE SIGNAL
            # =========================
            # Continuous curve is drawn on the sample-index axis (t * Fs)
            # so it lines up with the sampled points used by the operations.
            self.signals[signal_number] = {
                "kind": "generate",
                "type": signal_type,
                "A": A,
                "f": f,
                "theta": theta,
                "Fs": Fs,
                "display": display,
                "x_continuous": t_continuous * Fs,
                "y_continuous": y_continuous,
                "indices": n.tolist(),
                "values": y_sampled.tolist()
            }

            # Make sure the panel shows "Generate" (needed for Generate Both)
            self.source_vars[signal_number].set("Generate")

            self.file_labels[signal_number].config(
                text="File: (none)"
            )

            self.show_source_frame(signal_number)

            self.draw_inputs()

            return True

        except ValueError:

            messagebox.showerror(
                "Error",
                "Please enter valid numerical values."
            )

            return False

    # =========================
    # GENERATE BOTH
    # =========================
    def generate_both_signals(self):

        if not self.generate_signal(1):
            return

        if not self.generate_signal(2):
            return

    # =========================
    # DRAWING HELPERS
    # =========================
    def draw_stem(self, ax, indices, values, color, label):

        markerline, stemlines, baseline = ax.stem(
            indices,
            values,
            basefmt=" ",
            label=label
        )

        setp(markerline, color=color)
        setp(stemlines, color=color)

    def style_axes(self, ax, title):

        ax.axhline(0, color="black", linewidth=0.8)

        ax.xaxis.set_major_locator(
            MaxNLocator(integer=True)
        )

        ax.set_title(title)
        ax.set_xlabel("Sample Index (n)")
        ax.set_ylabel("Amplitude")

        ax.grid(True)

    # =========================
    # DRAW GRAPH 1  (INPUTS)
    # =========================
    def draw_inputs(self):

        self.ax1.clear()

        has_signal = False

        for number in (1, 2):

            signal = self.signals[number]

            if signal is None:
                continue

            has_signal = True

            color = self.signal_colors[number]

            label = f"Signal {number}"

            if signal["kind"] == "generate" and signal["display"] == "Continuous":

                self.ax1.plot(
                    signal["x_continuous"],
                    signal["y_continuous"],
                    color=color,
                    label=label
                )

            else:

                self.draw_stem(
                    self.ax1,
                    signal["indices"],
                    signal["values"],
                    color,
                    label
                )

        self.style_axes(
            self.ax1,
            "Graph 1 - Input Signals"
        )

        if has_signal:
            self.ax1.legend(
                loc="upper right",
                fontsize=8
            )

        self.figure1.tight_layout()

        self.canvas1.draw()

    # =========================
    # DRAW GRAPH 2  (RESULT)
    # =========================
    def draw_result(self):

        self.ax2.clear()

        if self.result is None:

            self.style_axes(
                self.ax2,
                "Graph 2 - Result"
            )

        else:

            self.draw_stem(
                self.ax2,
                self.result["indices"],
                self.result["values"],
                self.result_color,
                self.result["title"]
            )

            self.style_axes(
                self.ax2,
                f"Graph 2 - {self.result['title']}"
            )

        self.figure2.tight_layout()

        self.canvas2.draw()

    # =========================
    # RESULT
    # =========================
    def show_result(self, indices, values, title):

        self.result = {
            "indices": list(indices),
            "values": list(values),
            "title": title
        }

        self.draw_result()

    def reset_result(self):

        self.result = None

        self.draw_result()

    # =========================
    # OPERATION HELPERS
    # =========================
    def get_target_signal(self):

        number = self.target_var.get()

        signal = self.signals[number]

        if signal is None:

            messagebox.showwarning(
                "Warning",
                f"Signal {number} is not loaded or generated yet."
            )

            return None, None

        return number, signal

    def get_both_signals(self):

        if self.signals[1] is None or self.signals[2] is None:

            messagebox.showwarning(
                "Warning",
                "Load or generate both Signal 1 and Signal 2 first."
            )

            return None, None

        return self.signals[1], self.signals[2]

    def get_number(self, integer=False):

        text = self.number_entry.get().strip()

        try:

            value = float(text)

        except ValueError:

            messagebox.showerror(
                "Error",
                "Please enter a valid number in the Number box."
            )

            return None

        if integer:

            if not value.is_integer():

                messagebox.showerror(
                    "Error",
                    "Shift k must be an integer."
                )

                return None

            return int(value)

        return value

    def operation_data(self, signal):

        return {
            "indices": signal["indices"],
            "values": signal["values"]
        }

    # =========================
    # OPERATION HANDLERS
    # =========================
    def handle_multiply(self):

        number, signal = self.get_target_signal()

        if signal is None:
            return

        factor = self.get_number()

        if factor is None:
            return

        try:

            ind, val = multiply_signal(
                signal["indices"],
                signal["values"],
                factor
            )

            self.show_result(
                ind,
                val,
                f"Signal {number} * {factor:g}"
            )

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def handle_shift(self):

        number, signal = self.get_target_signal()

        if signal is None:
            return

        k = self.get_number(integer=True)

        if k is None:
            return

        try:

            ind, val = shift_signal(
                signal["indices"],
                signal["values"],
                k
            )

            self.show_result(
                ind,
                val,
                f"Signal {number} shifted by {k}"
            )

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def handle_fold(self):

        number, signal = self.get_target_signal()

        if signal is None:
            return

        try:

            ind, val = fold_signal(
                signal["indices"],
                signal["values"]
            )

            self.show_result(
                ind,
                val,
                f"Signal {number} folded x(-n)"
            )

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def handle_add_number(self):

        number, signal = self.get_target_signal()

        if signal is None:
            return

        constant = self.get_number()

        if constant is None:
            return

        values = [v + constant for v in signal["values"]]

        self.show_result(
            signal["indices"],
            values,
            f"Signal {number} + {constant:g}"
        )

    def handle_subtract_number(self):

        number, signal = self.get_target_signal()

        if signal is None:
            return

        constant = self.get_number()

        if constant is None:
            return

        values = [v - constant for v in signal["values"]]

        self.show_result(
            signal["indices"],
            values,
            f"Signal {number} - {constant:g}"
        )

    def handle_add(self):

        signal1, signal2 = self.get_both_signals()

        if signal1 is None:
            return

        try:

            ind, val = add_signals(
                {
                    "Signal 1": self.operation_data(signal1),
                    "Signal 2": self.operation_data(signal2)
                }
            )

            self.show_result(
                ind,
                val,
                "Signal 1 + Signal 2"
            )

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def handle_subtract(self):

        signal1, signal2 = self.get_both_signals()

        if signal1 is None:
            return

        try:

            ind, val = subtract_signals(
                self.operation_data(signal1),
                self.operation_data(signal2)
            )

            self.show_result(
                ind,
                val,
                "Signal 1 - Signal 2"
            )

        except Exception as e:

            messagebox.showerror("Error", str(e))

    # =========================
    # CLEAR
    # =========================
    def clear(self):

        self.signals = {1: None, 2: None}
        self.result = None

        for number in (1, 2):

            self.file_labels[number].config(
                text="File: (none)"
            )

        self.draw_inputs()
        self.draw_result()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    root = tk.Tk()

    app = SignalProcessingGUI(root)

    root.mainloop()