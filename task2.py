import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SignalProcessingGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Signal Processing Framework")
        self.root.geometry("1000x720")
        self.root.resizable(False, False)

        # =========================
        # COLORS
        # =========================
        self.bg_color = "#0B1F3A"
        self.panel_color = "#163A5F"
        self.control_color = "#DCEEFF"
        self.white = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        self.signal1 = None
        self.signal2 = None

        self.create_menu()
        self.create_gui()
        self.create_graphs()

    # =========================
    # MENU
    # =========================
    def create_menu(self):

        menu_bar = tk.Menu(self.root)

        # =========================
        # FILE MENU (NEW)
        # =========================
        file_menu = tk.Menu(
            menu_bar,
            tearoff=0
        )

        file_menu.add_command(
            label="Load Signal 1 from File...",
            command=lambda: self.load_signal_from_file(1)
        )

        file_menu.add_command(
            label="Load Signal 2 from File...",
            command=lambda: self.load_signal_from_file(2)
        )

        menu_bar.add_cascade(
            label="File",
            menu=file_menu
        )

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
    # SIGNAL MENU SELECTION
    # =========================
    def select_signal_from_menu(self, signal_type):

        self.signal1_type.set(signal_type)
        self.signal2_type.set(signal_type)

    # =========================
    # DISPLAY MENU SELECTION
    # =========================
    def select_display_from_menu(self, display_type):

        self.signal1_display.set(display_type)
        self.signal2_display.set(display_type)

    # =========================
    # GUI
    # =========================
    def create_gui(self):

        main_frame = tk.Frame(
            self.root,
            bg=self.bg_color,
            width=1000,
            height=720
        )

        main_frame.pack()
        main_frame.pack_propagate(False)

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
            bg=self.bg_color,
            width=980,
            height=690
        )

        content_frame.pack()
        content_frame.pack_propagate(False)

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

        button_frame.pack(pady=5)

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
            text="Clear",
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
            padx=10
        )

        self.graph_frame.pack_propagate(False)

    # =========================
    # SIGNAL CONTROLS
    # =========================
    def create_signal_controls(self, parent, signal_number):

        frame = tk.LabelFrame(
            parent,
            text=f"Signal {signal_number}",
            font=("Arial", 12, "bold"),
            bg=self.control_color,
            fg=self.bg_color,
            width=400,
            height=225
        )

        frame.pack(
            padx=15,
            pady=3
        )

        frame.pack_propagate(False)

        # =========================
        # SIGNAL TYPE
        # =========================
        tk.Label(
            frame,
            text="Signal Type:",
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=0,
            column=0,
            padx=8,
            pady=3,
            sticky="w"
        )

        signal_type = ttk.Combobox(
            frame,
            values=["Sine", "Cosine"],
            state="readonly",
            width=18
        )

        signal_type.set("Sine")

        signal_type.grid(
            row=0,
            column=1,
            padx=8,
            pady=3
        )

        if signal_number == 1:
            self.signal1_type = signal_type
        else:
            self.signal2_type = signal_type

        # =========================
        # AMPLITUDE
        # =========================
        tk.Label(
            frame,
            text="Amplitude A:",
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=1,
            column=0,
            padx=8,
            pady=3,
            sticky="w"
        )

        amplitude = tk.Entry(
            frame,
            width=20
        )

        amplitude.insert(0, "1")

        amplitude.grid(
            row=1,
            column=1,
            padx=8,
            pady=3
        )

        # =========================
        # FREQUENCY
        # =========================
        tk.Label(
            frame,
            text="Analog Frequency f:",
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=2,
            column=0,
            padx=8,
            pady=3,
            sticky="w"
        )

        frequency = tk.Entry(
            frame,
            width=20
        )

        frequency.insert(0, "5")

        frequency.grid(
            row=2,
            column=1,
            padx=8,
            pady=3
        )

        # =========================
        # PHASE
        # =========================
        tk.Label(
            frame,
            text="Phase θ (degrees):",
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=3,
            column=0,
            padx=8,
            pady=3,
            sticky="w"
        )

        phase = tk.Entry(
            frame,
            width=20
        )

        phase.insert(0, "0")

        phase.grid(
            row=3,
            column=1,
            padx=8,
            pady=3
        )

        # =========================
        # SAMPLING FREQUENCY
        # =========================
        tk.Label(
            frame,
            text="Sampling Frequency Fs:",
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=4,
            column=0,
            padx=8,
            pady=3,
            sticky="w"
        )

        sampling_frequency = tk.Entry(
            frame,
            width=20
        )

        sampling_frequency.insert(0, "20")

        sampling_frequency.grid(
            row=4,
            column=1,
            padx=8,
            pady=3
        )

        # =========================
        # DISPLAY TYPE
        # =========================
        tk.Label(
            frame,
            text="Display:",
            bg=self.control_color,
            font=("Arial", 10)
        ).grid(
            row=5,
            column=0,
            padx=8,
            pady=3,
            sticky="w"
        )

        display_type = ttk.Combobox(
            frame,
            values=["Continuous", "Discrete"],
            state="readonly",
            width=18
        )

        display_type.set("Continuous")

        display_type.grid(
            row=5,
            column=1,
            padx=8,
            pady=3
        )

        # =========================
        # GENERATE + LOAD BUTTONS
        # =========================
        button_row = tk.Frame(
            frame,
            bg=self.control_color
        )

        button_row.grid(
            row=6,
            column=0,
            columnspan=2,
            pady=4
        )

        generate_button = tk.Button(
            button_row,
            text=f"Generate Signal {signal_number}",
            command=lambda: self.generate_signal(signal_number),
            font=("Arial", 10, "bold"),
            bg=self.panel_color,
            fg="white",
            width=18
        )

        generate_button.grid(
            row=0,
            column=0,
            padx=4
        )

        load_button = tk.Button(
            button_row,
            text="Load File",
            command=lambda: self.load_signal_from_file(signal_number),
            font=("Arial", 10, "bold"),
            bg="#2E7D32",
            fg="white",
            width=12
        )

        load_button.grid(
            row=0,
            column=1,
            padx=4
        )

        # =========================
        # STORE CONTROLS
        # =========================
        if signal_number == 1:

            self.signal1_amplitude = amplitude
            self.signal1_frequency = frequency
            self.signal1_phase = phase
            self.signal1_sampling = sampling_frequency
            self.signal1_display = display_type

        else:

            self.signal2_amplitude = amplitude
            self.signal2_frequency = frequency
            self.signal2_phase = phase
            self.signal2_sampling = sampling_frequency
            self.signal2_display = display_type

    # =========================
    # GRAPHS
    # =========================
    def create_graphs(self):

        # Signal 1
        self.figure1 = Figure(
            figsize=(5, 2.55),
            dpi=100
        )

        self.ax1 = self.figure1.add_subplot(111)

        self.canvas1 = FigureCanvasTkAgg(
            self.figure1,
            master=self.graph_frame
        )

        self.canvas1.get_tk_widget().pack(
            padx=8,
            pady=6
        )

        # Signal 2
        self.figure2 = Figure(
            figsize=(5, 2.55),
            dpi=100
        )

        self.ax2 = self.figure2.add_subplot(111)

        self.canvas2 = FigureCanvasTkAgg(
            self.figure2,
            master=self.graph_frame
        )

        self.canvas2.get_tk_widget().pack(
            padx=8,
            pady=6
        )

        self.ax1.set_title("Signal 1")
        self.ax2.set_title("Signal 2")

        self.ax1.grid(True)
        self.ax2.grid(True)

        self.canvas1.draw()
        self.canvas2.draw()

    # =========================
    # READ NUMERIC DATA FILE (NEW)
    # =========================
    def read_signal_file(self, path):
        """
        Supported files:
          .npy               -> NumPy array
          .txt .csv .dat ... -> numbers separated by spaces, commas,
                                semicolons or tabs. Header/text lines
                                are skipped automatically.

        Returns a 1-D array (samples only) or a 2-D array (columns).
        """

        if path.lower().endswith(".npy"):
            return np.load(path)

        rows = []

        with open(path, "r", encoding="utf-8-sig") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                parts = line.replace(",", " ").replace(";", " ").split()

                try:
                    rows.append([float(p) for p in parts])
                except ValueError:
                    # header or comment line
                    continue

        if not rows:
            raise ValueError("No numeric data found in the file.")

        # -------------------------
        # Skip a 3-line header such as:
        #   SignalType, IsPeriodic, N (number of samples)
        # followed by N data rows.
        # -------------------------
        if (
            len(rows) > 3
            and all(len(r) == 1 for r in rows[:3])
            and len(rows[3]) > 1
            and int(rows[2][0]) == len(rows) - 3
        ):
            rows = rows[3:]

        # Keep the most common row width (ignores stray lines)
        widths = [len(r) for r in rows]
        width = max(set(widths), key=widths.count)

        rows = [r for r in rows if len(r) == width]

        data = np.array(rows, dtype=float)

        if width == 1:
            return data[:, 0]

        return data

    # =========================
    # LOAD SIGNAL FROM FILE (NEW)
    # =========================
    def load_signal_from_file(self, signal_number):

        path = filedialog.askopenfilename(
            title=f"Load Signal {signal_number}",
            filetypes=[
                ("Signal files", "*.txt *.csv *.dat *.npy"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return False

        try:

            data = self.read_signal_file(path)

            if signal_number == 1:
                fs_entry = self.signal1_sampling
                display = self.signal1_display.get()
            else:
                fs_entry = self.signal2_sampling
                display = self.signal2_display.get()

            # -------------------------
            # ONE COLUMN: samples only
            # -------------------------
            if data.ndim == 1:

                y = data

                Fs = float(fs_entry.get())

                if Fs <= 0:
                    raise ValueError(
                        "Sampling frequency must be greater than 0."
                    )

                t = np.arange(len(y)) / Fs

            # -------------------------
            # TWO COLUMNS: time, value
            # -------------------------
            else:

                if data.shape[1] < 2:
                    raise ValueError("Unsupported file layout.")

                t = data[:, 0]
                y = data[:, 1]

                # First column is a sample index (0, 1, 2, ...)
                is_index = (
                    len(t) > 0
                    and np.allclose(t, np.round(t))
                    and np.allclose(np.diff(t), 1)
                )

                if is_index:

                    # Use the Fs entered in the GUI
                    Fs = float(fs_entry.get())

                    if Fs <= 0:
                        raise ValueError(
                            "Sampling frequency must be greater than 0."
                        )

                    t = (t - t[0]) / Fs

                else:

                    if len(t) < 2:
                        raise ValueError("File needs at least 2 samples.")

                    dt = np.diff(t)

                    if np.any(dt <= 0):
                        raise ValueError(
                            "Time column must be strictly increasing."
                        )

                    Fs = 1 / np.mean(dt)

                    fs_entry.delete(0, tk.END)
                    fs_entry.insert(0, f"{Fs:g}")

            if len(y) == 0:
                raise ValueError("The file contains no samples.")

            name = os.path.basename(path)

            signal_data = {
                "type": f"File ({name})",
                "A": float(np.max(np.abs(y))),
                "f": None,
                "theta": None,
                "Fs": Fs,
                "display": display,
                "t_continuous": t,
                "y_continuous": y,
                "t_sampled": t,
                "y_sampled": y
            }

            if signal_number == 1:
                self.signal1 = signal_data
                self.draw_signal1()
            else:
                self.signal2 = signal_data
                self.draw_signal2()

            return True

        except ValueError as error:

            messagebox.showerror(
                "Load Error",
                f"Could not load the file:\n\n{error}"
            )

            return False

        except Exception as error:

            messagebox.showerror(
                "Load Error",
                f"Could not read the file:\n\n{error}"
            )

            return False

    # =========================
    # GENERATE ONE SIGNAL
    # =========================
    def generate_signal(self, signal_number):

        try:

            if signal_number == 1:

                signal_type = self.signal1_type.get()

                A = float(
                    self.signal1_amplitude.get()
                )

                f = float(
                    self.signal1_frequency.get()
                )

                theta = float(
                    self.signal1_phase.get()
                )

                Fs = float(
                    self.signal1_sampling.get()
                )

                display = self.signal1_display.get()

            else:

                signal_type = self.signal2_type.get()

                A = float(
                    self.signal2_amplitude.get()
                )

                f = float(
                    self.signal2_frequency.get()
                )

                theta = float(
                    self.signal2_phase.get()
                )

                Fs = float(
                    self.signal2_sampling.get()
                )

                display = self.signal2_display.get()

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

            # Continuous time
            t_continuous = np.linspace(
                0,
                duration,
                1000
            )

            # Sampled time
            t_sampled = np.arange(
                0,
                duration,
                1 / Fs
            )

            # =========================
            # SINE / COSINE
            # =========================
            if signal_type == "Sine":

                y_continuous = A * np.sin(
                    2 * np.pi * f * t_continuous
                    + theta_rad
                )

                y_sampled = A * np.sin(
                    2 * np.pi * f * t_sampled
                    + theta_rad
                )

            else:

                y_continuous = A * np.cos(
                    2 * np.pi * f * t_continuous
                    + theta_rad
                )

                y_sampled = A * np.cos(
                    2 * np.pi * f * t_sampled
                    + theta_rad
                )

            # =========================
            # STORE SIGNAL
            # =========================
            signal_data = {
                "type": signal_type,
                "A": A,
                "f": f,
                "theta": theta,
                "Fs": Fs,
                "display": display,
                "t_continuous": t_continuous,
                "y_continuous": y_continuous,
                "t_sampled": t_sampled,
                "y_sampled": y_sampled
            }

            if signal_number == 1:

                self.signal1 = signal_data
                self.draw_signal1()

            else:

                self.signal2 = signal_data
                self.draw_signal2()

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
    # DRAW SIGNAL 1
    # =========================
    def draw_signal1(self):

        if self.signal1 is None:
            return

        self.ax1.clear()

        signal = self.signal1

        if signal["display"] == "Continuous":

            self.ax1.plot(
                signal["t_continuous"],
                signal["y_continuous"],
                label=signal["type"]
            )

        else:

            self.ax1.stem(
                signal["t_sampled"],
                signal["y_sampled"],
                basefmt=" ",
                label=signal["type"]
            )

        self.ax1.set_title(
            f"Signal 1 - {signal['type']} - "
            f"{signal['display']}"
        )

        self.ax1.set_xlabel("Time")
        self.ax1.set_ylabel("Amplitude")

        self.ax1.grid(True)
        self.ax1.legend()

        self.figure1.tight_layout()

        self.canvas1.draw()

    # =========================
    # DRAW SIGNAL 2
    # =========================
    def draw_signal2(self):

        if self.signal2 is None:
            return

        self.ax2.clear()

        signal = self.signal2

        if signal["display"] == "Continuous":

            self.ax2.plot(
                signal["t_continuous"],
                signal["y_continuous"],
                label=signal["type"]
            )

        else:

            self.ax2.stem(
                signal["t_sampled"],
                signal["y_sampled"],
                basefmt=" ",
                label=signal["type"]
            )

        self.ax2.set_title(
            f"Signal 2 - {signal['type']} - "
            f"{signal['display']}"
        )

        self.ax2.set_xlabel("Time")
        self.ax2.set_ylabel("Amplitude")

        self.ax2.grid(True)
        self.ax2.legend()

        self.figure2.tight_layout()

        self.canvas2.draw()

    # =========================
    # CLEAR
    # =========================
    def clear(self):

        self.signal1 = None
        self.signal2 = None

        self.ax1.clear()
        self.ax2.clear()

        self.ax1.set_title("Signal 1")
        self.ax2.set_title("Signal 2")

        self.ax1.grid(True)
        self.ax2.grid(True)

        self.canvas1.draw()
        self.canvas2.draw()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    root = tk.Tk()

    app = SignalProcessingGUI(root)

    root.mainloop()