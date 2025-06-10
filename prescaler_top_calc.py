import tkinter as tk
from tkinter import ttk
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T0, WGM_BITS_T1, WGM_BITS_T2
from utils import parse_hex_bin_int, show_error, show_warning

class PrescalerTOPCalculator:
    def __init__(self, master_frame, cpu_freq_var):
        self.master_frame = master_frame
        self.cpu_freq_entry_var = cpu_freq_var # Use shared CPU freq var

        self.prescaler_desired_freq_var = tk.StringVar()
        self.prescaler_mode_selection_var = tk.StringVar()
        self.prescaler_desired_top_var = tk.StringVar(value="0") # Default 0
        self.prescaler_timer_selection_var = tk.StringVar(value="Timer0")
        self.calculated_prescaler_var = tk.StringVar()
        self.calculated_top_var = tk.StringVar()
        self.calculated_actual_freq_var = tk.StringVar()
        self.calculated_error_percent_var = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        prescaler_calc_frame = self.master_frame

        # Inputs
        ttk.Label(prescaler_calc_frame, text="Ønsket Frekvens (Hz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.prescaler_desired_freq_entry = ttk.Entry(prescaler_calc_frame, textvariable=self.prescaler_desired_freq_var)
        self.prescaler_desired_freq_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(prescaler_calc_frame, text="Timer Mode:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.prescaler_mode_selection_combobox = ttk.Combobox(prescaler_calc_frame, textvariable=self.prescaler_mode_selection_var, state="readonly")
        self.prescaler_mode_selection_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(prescaler_calc_frame, text="Ønsket TOP værdi (hvis relevant):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.prescaler_desired_top_entry = ttk.Entry(prescaler_calc_frame, textvariable=self.prescaler_desired_top_var)
        self.prescaler_desired_top_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Timer selection for this section
        ttk.Label(prescaler_calc_frame, text="Vælg Timer:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(prescaler_calc_frame, text="Timer0", variable=self.prescaler_timer_selection_var, value="Timer0", command=self._update_prescaler_mode_options).grid(row=3, column=1, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(prescaler_calc_frame, text="Timer1", variable=self.prescaler_timer_selection_var, value="Timer1", command=self._update_prescaler_mode_options).grid(row=3, column=2, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(prescaler_calc_frame, text="Timer2", variable=self.prescaler_timer_selection_var, value="Timer2", command=self._update_prescaler_mode_options).grid(row=3, column=3, padx=5, pady=2, sticky="w")
        
        # Calculate Button
        ttk.Button(prescaler_calc_frame, text="Beregn Prescaler", command=self.calculate_prescaler_and_top).grid(row=4, column=0, columnspan=4, pady=10)

        # Outputs
        ttk.Label(prescaler_calc_frame, text="Optimal Prescaler:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(prescaler_calc_frame, textvariable=self.calculated_prescaler_var, font=("TkDefaultFont", 10, "bold")).grid(row=5, column=1, columnspan=3, padx=5, pady=2, sticky="w")

        ttk.Label(prescaler_calc_frame, text="Anbefalet TOP-værdi:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(prescaler_calc_frame, textvariable=self.calculated_top_var, font=("TkDefaultFont", 10, "bold")).grid(row=6, column=1, columnspan=3, padx=5, pady=2, sticky="w")

        ttk.Label(prescaler_calc_frame, text="Faktisk Frekvens:").grid(row=7, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(prescaler_calc_frame, textvariable=self.calculated_actual_freq_var).grid(row=7, column=1, columnspan=3, padx=5, pady=2, sticky="w")
        
        ttk.Label(prescaler_calc_frame, text="Fejl (%):").grid(row=8, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(prescaler_calc_frame, textvariable=self.calculated_error_percent_var).grid(row=8, column=1, columnspan=3, padx=5, pady=2, sticky="w")

        self._update_prescaler_mode_options() # Initial population of mode combobox


    def _update_prescaler_mode_options(self):
        selected_timer = self.prescaler_timer_selection_var.get()
        modes = []
        if selected_timer == "Timer0":
            modes = list(WGM_BITS_T0.keys())
        elif selected_timer == "Timer1":
            modes = list(WGM_BITS_T1.keys())
        elif selected_timer == "Timer2":
            modes = list(WGM_BITS_T2.keys())
        
        self.prescaler_mode_selection_combobox['values'] = modes
        if modes:
            self.prescaler_mode_selection_combobox.set(modes[0]) # Set default to first mode
        else:
            self.prescaler_mode_selection_combobox.set("")


    def calculate_prescaler_and_top(self):
        try:
            cpu_freq_mhz = float(self.cpu_freq_entry_var.get())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            desired_freq = float(self.prescaler_desired_freq_var.get())
            selected_timer = self.prescaler_timer_selection_var.get()
            selected_mode = self.prescaler_mode_selection_var.get()
            desired_top_input = parse_hex_bin_int(self.prescaler_desired_top_var.get())

            if desired_freq <= 0:
                show_error("Ugyldig Frekvens", "Ønsket frekvens skal være større end nul.")
                self._clear_results()
                return

            best_prescaler = None
            best_top = None
            min_freq_error = float('inf') 
            actual_achieved_freq = 0.0

            prescaler_options = []
            max_top = 0

            if selected_timer == "Timer0":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
                max_top = 255 
                wgm_map = WGM_BITS_T0
            elif selected_timer == "Timer1":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
                max_top = 65535 
                wgm_map = WGM_BITS_T1
            elif selected_timer == "Timer2":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T2"].keys() if p != "0"]
                max_top = 255
                wgm_map = WGM_BITS_T2

            prescaler_options.sort() 

            for prescaler in prescaler_options:
                divisor = 1 
                
                # Determine divisor based on mode type
                if "Phase Correct" in selected_mode or "CTC" in selected_mode:
                    divisor = 2
                
                # Check for fixed TOP modes first
                fixed_top_mode = wgm_map.get(selected_mode, {}).get("TOP_fixed")
                if fixed_top_mode is not None:
                    top_candidate = fixed_top_mode
                elif selected_mode == "Normal":
                    top_candidate = max_top
                else: # Modes where TOP is calculable (CTC, Fast PWM with variable TOP, Phase Correct with variable TOP)
                    denominator_calc_top = divisor * prescaler * desired_freq
                    if denominator_calc_top == 0: continue
                    calculated_top_float = (cpu_freq_hz / denominator_calc_top) - 1
                    top_candidate = round(calculated_top_float)

                if top_candidate < 0 or top_candidate > max_top:
                    continue 

                # Calculate actual frequency with this (prescaler, top_candidate) pair
                if "Phase Correct" in selected_mode:
                    if top_candidate == 0: continue
                    actual_freq_candidate = cpu_freq_hz / (2 * prescaler * top_candidate)
                else: # Normal, CTC, Fast PWM
                    if (top_candidate + 1) == 0: continue
                    actual_freq_candidate = cpu_freq_hz / (divisor * prescaler * (top_candidate + 1))


                freq_error = abs(actual_freq_candidate - desired_freq)

                if freq_error < min_freq_error:
                    min_freq_error = freq_error
                    best_prescaler = prescaler
                    best_top = top_candidate
                    actual_achieved_freq = actual_freq_candidate

            if best_prescaler is not None:
                error_percent = (abs(actual_achieved_freq - desired_freq) / desired_freq) * 100
                self.calculated_prescaler_var.set(str(best_prescaler))
                self.calculated_top_var.set(str(best_top))
                self.calculated_actual_freq_var.set(f"{actual_achieved_freq:.2f} Hz")
                self.calculated_error_percent_var.set(f"{error_percent:.4f}%")
            else:
                show_warning("Intet Match", "Kunne ikke finde en passende prescaler og TOP-værdi for den ønskede frekvens med de valgte indstillinger. Prøv en anden frekvens eller tilstand.")
                self._clear_results()

        except ValueError as ve:
            show_error("Input Fejl", f"Ugyldigt input: {ve}. Sørg for, at alle felter indeholder gyldige tal.")
            self._clear_results()
        except KeyError as ke:
            show_error("Konfigurationsfejl", f"Ukendt mode eller prescaler: {ke}. Kontroller indstillingerne i constants.py")
            self._clear_results()
        except Exception as e:
            show_error("Fejl", f"En uventet fejl opstod: {e}")
            self._clear_results()

    def _clear_results(self):
        self.calculated_prescaler_var.set("N/A")
        self.calculated_top_var.set("N/A")
        self.calculated_actual_freq_var.set("N/A")
        self.calculated_error_percent_var.set("N/A")