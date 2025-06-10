# timer2_calc.py
import tkinter as tk
from tkinter import ttk
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T2
from utils import parse_hex_bin_int, show_error, show_warning

class Timer2Calculator:
    def __init__(self, master_frame, cpu_freq_var):
        self.master_frame = master_frame
        self.cpu_freq_entry_var = cpu_freq_var # Use shared CPU freq var

        # Timer2 StringVars
        self.timer2_mode_selection = tk.StringVar(value="Normal")
        self.timer2_prescaler_var = tk.StringVar(value="1")
        self.timer2_delay_entry = tk.StringVar()
        self.timer2_freq_entry = tk.StringVar()
        self.timer2_duty_entry = tk.StringVar()
        self.timer2_actual_freq_label = tk.StringVar()
        self.timer2_error_label = tk.StringVar()
        self.timer2_tccr2a_label = tk.StringVar()
        self.timer2_tccr2b_label = tk.StringVar()
        self.timer2_ocr2a_label = tk.StringVar()
        self.timer2_tcnt2_label = tk.StringVar()
        self.timer2_actual_duty_label = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        frame = self.master_frame
        
        # Mode Selection
        ttk.Label(frame, text="Timer Mode:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.timer2_mode_combobox = ttk.Combobox(frame, textvariable=self.timer2_mode_selection, state="readonly")
        self.timer2_mode_combobox['values'] = list(WGM_BITS_T2.keys())
        self.timer2_mode_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.timer2_mode_combobox.bind("<<ComboboxSelected>>", self._on_timer2_mode_change)

        # Prescaler Selection
        ttk.Label(frame, text="Prescaler:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.timer2_prescaler_combobox = ttk.Combobox(frame, textvariable=self.timer2_prescaler_var, state="readonly")
        self.timer2_prescaler_combobox['values'] = [p for p in PRESCALERS_T0_T1_T2["T2"].keys() if p != "0"]
        self.timer2_prescaler_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # Input fields (toggle visibility based on mode)
        ttk.Label(frame, text="Ønsket Forsinkelse (ms):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.timer2_delay_entry_widget = ttk.Entry(frame, textvariable=self.timer2_delay_entry)
        self.timer2_delay_entry_widget.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="Ønsket Frekvens (Hz):").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.timer2_freq_entry_widget = ttk.Entry(frame, textvariable=self.timer2_freq_entry)
        self.timer2_freq_entry_widget.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="Ønsket Duty Cycle (%):").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.timer2_duty_entry_widget = ttk.Entry(frame, textvariable=self.timer2_duty_entry)
        self.timer2_duty_entry_widget.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        # Calculate Button
        ttk.Button(frame, text="Beregn Timer2 Indstillinger", command=self.calculate_timer2).grid(row=6, column=0, columnspan=2, pady=10)

        # Results Display
        results_frame = ttk.LabelFrame(frame, text="Beregnet Resultat")
        results_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(results_frame, text="Faktisk Frekvens/Tid:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer2_actual_freq_label, font=("TkDefaultFont", 10, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="Fejl (%):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer2_error_label).grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCCR2A (bin):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer2_tccr2a_label).grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCCR2B (bin):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer2_tccr2b_label).grid(row=3, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="OCR2A (dec):").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer2_ocr2a_label).grid(row=4, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCNT2 Start (dec):").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer2_tcnt2_label).grid(row=5, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="Faktisk Duty Cycle (%):").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer2_actual_duty_label).grid(row=6, column=1, padx=5, pady=2, sticky="w")
        
        self._on_timer2_mode_change() # Set initial visibility

    def _on_timer2_mode_change(self, event=None):
        selected_mode = self.timer2_mode_selection.get()
        if selected_mode == "Normal":
            self.timer2_delay_entry_widget.grid()
            self.timer2_freq_entry_widget.grid_remove()
            self.timer2_duty_entry_widget.grid_remove()
        elif selected_mode == "CTC":
            self.timer2_delay_entry_widget.grid_remove()
            self.timer2_freq_entry_widget.grid()
            self.timer2_duty_entry_widget.grid_remove()
        elif "PWM" in selected_mode:
            self.timer2_delay_entry_widget.grid_remove()
            self.timer2_freq_entry_widget.grid()
            self.timer2_duty_entry_widget.grid()

    def calculate_timer2(self):
        try:
            cpu_freq_mhz = float(self.cpu_freq_entry_var.get())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            selected_mode = self.timer2_mode_selection.get()
            selected_prescaler_str = self.timer2_prescaler_var.get()
            prescaler_int = int(selected_prescaler_str)

            # Clear previous results
            self._clear_results()

            tccr2a = 0
            tccr2b = 0
            ocr2a = -1
            tcnt2 = -1
            actual_freq = 0
            actual_delay_s = 0
            actual_duty = 0
            calc_error = 0

            # Set WGM bits
            wgm_bits = WGM_BITS_T2[selected_mode]
            tccr2a |= (wgm_bits["WGM21"] << 1) | wgm_bits["WGM20"]
            tccr2b |= (wgm_bits["WGM22"] << 3) # WGM22 is in TCCR2B, bit 3 for Atmega328P, check datasheet if different

            # Set CS bits
            cs_bits = PRESCALERS_T0_T1_T2["T2"][selected_prescaler_str]
            tccr2b |= cs_bits

            if selected_mode == "Normal":
                desired_delay_ms = float(self.timer2_delay_entry.get())
                desired_delay_s = desired_delay_ms / 1000.0
                
                required_count_float = desired_delay_s * cpu_freq_hz / prescaler_int
                
                if required_count_float > 256 or required_count_float <= 0:
                    show_warning("Ugyldig Forsinkelse", "Den ønskede forsinkelse er for lang eller for kort for disse indstillinger.")
                    return

                tcnt2_float = 256 - required_count_float
                if tcnt2_float < 0: tcnt2_float = 0
                tcnt2 = round(tcnt2_float)
                
                actual_delay_s = prescaler_int * (256 - tcnt2) / cpu_freq_hz
                actual_freq = 1.0 / actual_delay_s
                calc_error = abs(actual_delay_s - desired_delay_s) / desired_delay_s * 100

            elif selected_mode == "CTC":
                desired_freq = float(self.timer2_freq_entry.get())
                
                denominator = 2 * prescaler_int * desired_freq
                if denominator == 0:
                    show_error("Fejl", "Den ønskede frekvens er for lav eller nul.")
                    return

                ocr2a_float = (cpu_freq_hz / denominator) - 1
                if ocr2a_float < 0 or ocr2a_float > 255:
                    show_warning("Ugyldig Frekvens", "Den ønskede frekvens kan ikke opnås med disse indstillinger (OCR2A uden for rækkevidde).")
                    return
                ocr2a = round(ocr2a_float)

                actual_freq = cpu_freq_hz / (2 * prescaler_int * (ocr2a + 1))
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            elif "PWM" in selected_mode:
                desired_freq = float(self.timer2_freq_entry.get())
                desired_duty_cycle_perc = float(self.timer2_duty_entry.get())
                if not (0 <= desired_duty_cycle_perc <= 100):
                    show_warning("Ugyldig Duty Cycle", "Duty Cycle skal være mellem 0 og 100%.")
                    return
                desired_duty_cycle = desired_duty_cycle_perc / 100.0

                top_value = 255 # TOP is fixed to 0xFF for these modes

                if selected_mode == "Fast PWM":
                    actual_freq = cpu_freq_hz / (prescaler_int * (top_value + 1))
                    ocr2a_float = top_value * desired_duty_cycle
                elif selected_mode == "Phase Correct PWM":
                    actual_freq = cpu_freq_hz / (2 * prescaler_int * top_value)
                    ocr2a_float = top_value * desired_duty_cycle
                else:
                    show_error("Fejl", "Ukendt PWM-tilstand for Timer2.")
                    return

                if ocr2a_float < 0 or ocr2a_float > top_value:
                    show_warning("Ugyldig Duty Cycle", "Den ønskede Duty Cycle kan ikke opnås (OCR2A uden for rækkevidde).")
                    return
                ocr2a = round(ocr2a_float)

                if selected_mode == "Fast PWM":
                    actual_duty = (ocr2a / (top_value + 1)) * 100
                elif selected_mode == "Phase Correct PWM":
                    actual_duty = (ocr2a / top_value) * 100
                
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            else:
                show_warning("Ugyldig Tilstand", "Vælg venligst en gyldig timertilstand.")
                return

            self.timer2_actual_freq_label.set(f"{actual_freq:.2f} Hz / {actual_delay_s*1000:.2f} ms" if selected_mode == "Normal" else f"{actual_freq:.2f} Hz")
            self.timer2_error_label.set(f"{calc_error:.4f}%")
            self.timer2_tccr2a_label.set(f"0b{tccr2a:08b}")
            self.timer2_tccr2b_label.set(f"0b{tccr2b:08b}")
            self.timer2_ocr2a_label.set(f"{ocr2a}")
            self.timer2_tcnt2_label.set(f"{tcnt2}")
            self.timer2_actual_duty_label.set(f"{actual_duty:.2f}%")

        except ValueError as e:
            show_error("Ugyldigt Input", f"Indtast venligst gyldige tal for CPU Frekvens eller andre inputfelter. Detaljer: {e}")
            self._clear_results()
        except KeyError as e:
            show_error("Konfigurationsfejl", f"Ukendt mode eller prescaler: {e}. Kontroller indstillingerne i constants.py")
            self._clear_results()
        except Exception as e:
            show_error("Fejl", f"En uventet fejl opstod: {e}")
            self._clear_results()

    def _clear_results(self):
        self.timer2_actual_freq_label.set("N/A")
        self.timer2_error_label.set("N/A")
        self.timer2_tccr2a_label.set("N/A")
        self.timer2_tccr2b_label.set("N/A")
        self.timer2_ocr2a_label.set("N/A")
        self.timer2_tcnt2_label.set("N/A")
        self.timer2_actual_duty_label.set("N/A")