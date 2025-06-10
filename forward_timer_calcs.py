# forward_timer_main.py
import tkinter as tk
from tkinter import ttk
from constants import CPU_FREQ_DEFAULT
from timer0_calc import Timer0Calculator
from timer1_calc import Timer1Calculator
from timer2_calc import Timer2Calculator
from prescaler_top_calc import PrescalerTOPCalculator

class ForwardTimerCalculations:
    def __init__(self, master_tab):
        self.master_tab = master_tab
        self.cpu_freq_var = tk.StringVar(value=str(CPU_FREQ_DEFAULT / 1_000_000))

        self._create_widgets()

    def _create_widgets(self):
        # Frame for CPU Freq shared by all timers in this section
        cpu_freq_frame = ttk.LabelFrame(self.master_tab, text="Fælles CPU Frekvens")
        cpu_freq_frame.pack(padx=10, pady=5, fill="x")
        ttk.Label(cpu_freq_frame, text="CPU Clock Freq (MHz):").pack(side="left", padx=5, pady=2)
        ttk.Entry(cpu_freq_frame, textvariable=self.cpu_freq_var).pack(side="left", padx=5, pady=2, expand=True, fill="x")

        # Notebook for individual timers
        self.notebook = ttk.Notebook(self.master_tab)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Timer0 Tab
        self.timer0_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timer0_tab, text="Timer0")
        self.timer0_calculator = Timer0Calculator(self.timer0_tab, self.cpu_freq_var)

        # Timer1 Tab
        self.timer1_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timer1_tab, text="Timer1")
        self.timer1_calculator = Timer1Calculator(self.timer1_tab, self.cpu_freq_var)

        # Timer2 Tab
        self.timer2_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timer2_tab, text="Timer2")
        self.timer2_calculator = Timer2Calculator(self.timer2_tab, self.cpu_freq_var)

        # Separate section for Prescaler & TOP Calculation
        prescaler_top_frame = ttk.LabelFrame(self.master_tab, text="Beregn Optimal Prescaler & TOP")
        prescaler_top_frame.pack(padx=10, pady=10, fill="x")
        self.prescaler_top_calculator = PrescalerTOPCalculator(prescaler_top_frame, self.cpu_freq_var)