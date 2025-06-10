# timer1_calc.py
import tkinter as tk
from tkinter import ttk
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T1
from utils import parse_hex_bin_int, show_error, show_warning

class Timer1Calculator:
    def __init__(self, master_frame, cpu_freq_var):
        self.master_frame = master_frame
        self.cpu_freq_entry_var = cpu_freq_var # Use shared CPU freq var

        # Timer1 StringVars
        self.timer1_mode_selection = tk.StringVar(value="Normal")
        self.timer1_prescaler_var = tk.StringVar(value="1")
        self.timer1_delay_entry = tk.StringVar()
        self.timer1_freq_entry = tk.StringVar()
        self.timer1_duty_entry = tk.StringVar()
        self.timer1_actual_freq_label = tk.StringVar()
        self.timer1_error_label = tk.StringVar()
        self.timer1_tccr1a_label = tk.StringVar()
        self.timer1_tccr1b_label = tk.StringVar()
        self.timer1_tccr1c_label = tk.StringVar()
        self.timer1_ocr1a_label = tk.StringVar()
        self.timer1_icr1_label = tk.StringVar()
        self.timer1_tcnt1_label = tk.StringVar()
        self.timer1_actual_duty_label = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        frame = self.master_frame
        
        # Mode Selection
        ttk.Label(frame, text="Timer Mode:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.timer1_mode_combobox = ttk.Combobox(frame, textvariable=self.timer1_mode_selection, state="readonly")
        self.timer1_mode_combobox['values'] = list(WGM_BITS_T1.keys())
        self.timer1_mode_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.timer1_mode_combobox.bind("<<ComboboxSelected>>", self._on_timer1_mode_change)

        # Prescaler Selection
        ttk.Label(frame, text="Prescaler:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.timer1_prescaler_combobox = ttk.Combobox(frame, textvariable=self.timer1_prescaler_var, state="readonly")
        self.timer1_prescaler_combobox['values'] = [p for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
        self.timer1_prescaler_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # Input fields (toggle visibility based on mode)
        ttk.Label(frame, text="Ønsket Forsinkelse (ms):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.timer1_delay_entry_widget = ttk.Entry(frame, textvariable=self.timer1_delay_entry)
        self.timer1_delay_entry_widget.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="Ønsket Frekvens (Hz):").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.timer1_freq_entry_widget = ttk.Entry(frame, textvariable=self.timer1_freq_entry)
        self.timer1_freq_entry_widget.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="Ønsket Duty Cycle (%):").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.timer1_duty_entry_widget = ttk.Entry(frame, textvariable=self.timer1_duty_entry)
        self.timer1_duty_entry_widget.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        # Calculate Button
        ttk.Button(frame, text="Beregn Timer1 Indstillinger", command=self.calculate_timer1).grid(row=6, column=0, columnspan=2, pady=10)

        # Results Display
        results_frame = ttk.LabelFrame(frame, text="Beregnet Resultat")
        results_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(results_frame, text="Faktisk Frekvens/Tid:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_actual_freq_label, font=("TkDefaultFont", 10, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="Fejl (%):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_error_label).grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCCR1A (bin):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_tccr1a_label).grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCCR1B (bin):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_tccr1b_label).grid(row=3, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCCR1C (bin):").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_tccr1c_label).grid(row=4, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="OCR1A (dec):").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_ocr1a_label).grid(row=5, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="ICR1 (dec):").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_icr1_label).grid(row=6, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="TCNT1 Start (dec):").grid(row=7, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_tcnt1_label).grid(row=7, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="Faktisk Duty Cycle (%):").grid(row=8, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer1_actual_duty_label).grid(row=8, column=1, padx=5, pady=2, sticky="w")
        
        self._on_timer1_mode_change() # Set initial visibility

    def _on_timer1_mode_change(self, event=None):
        selected_mode = self.timer1_mode_selection.get()
        if selected_mode == "Normal":
            self.timer1_delay_entry_widget.grid()
            self.timer1_freq_entry_widget.grid_remove()
            self.timer1_duty_entry_widget.grid_remove()
        elif "CTC" in selected_mode:
            self.timer1_delay_entry_widget.grid_remove()
            self.timer1_freq_entry_widget.grid()
            self.timer1_duty_entry_widget.grid_remove()
        elif "PWM" in selected_mode:
            self.timer1_delay_entry_widget.grid_remove()
            self.timer1_freq_entry_widget.grid()
            self.timer1_duty_entry_widget.grid()

    def calculate_timer1(self):
        try:
            cpu_freq_mhz = float(self.cpu_freq_entry_var.get())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            selected_mode = self.timer1_mode_selection.get()
            selected_prescaler_str = self.timer1_prescaler_var.get()
            prescaler_int = int(selected_prescaler_str)

            # Clear previous results
            self._clear_results()

            tccr1a = 0
            tccr1b = 0
            tccr1c = 0 # For OC1A/B/C force output compare
            ocr1a = -1
            icr1 = -1
            tcnt1 = -1
            actual_freq = 0
            actual_delay_s = 0
            actual_duty = 0
            calc_error = 0

            # Set WGM bits
            wgm_bits = WGM_BITS_T1[selected_mode]
            tccr1a |= (wgm_bits.get("WGM11",0) << 1) | wgm_bits.get("WGM10",0)
            tccr1b |= (wgm_bits.get("WGM13",0) << 4) | (wgm_bits.get("WGM12",0) << 3)

            # Set CS bits
            cs_bits = PRESCALERS_T0_T1_T2["T0_T1"][selected_prescaler_str]
            tccr1b |= cs_bits

            max_top_val = 65535 # 16-bit timer default max

            if selected_mode == "Normal":
                desired_delay_ms = float(self.timer1_delay_entry.get())
                desired_delay_s = desired_delay_ms / 1000.0
                
                required_count_float = desired_delay_s * cpu_freq_hz / prescaler_int
                
                if required_count_float > (max_top_val + 1) or required_count_float <= 0:
                    show_warning("Ugyldig Forsinkelse", "Den ønskede forsinkelse er for lang eller for kort for disse indstillinger.")
                    return

                tcnt1_float = (max_top_val + 1) - required_count_float
                if tcnt1_float < 0: tcnt1_float = 0
                tcnt1 = round(tcnt1_float)

                actual_delay_s = prescaler_int * ((max_top_val + 1) - tcnt1) / cpu_freq_hz
                actual_freq = 1.0 / actual_delay_s
                calc_error = abs(actual_delay_s - desired_delay_s) / desired_delay_s * 100

            elif "CTC" in selected_mode:
                desired_freq = float(self.timer1_freq_entry.get())
                
                denominator = 2 * prescaler_int * desired_freq
                if denominator == 0:
                    show_error("Fejl", "Den ønskede frekvens er for lav eller nul.")
                    return

                top_float = (cpu_freq_hz / denominator) - 1

                if "TOP=OCR1A" in selected_mode:
                    if top_float < 0 or top_float > max_top_val: # Check against 16-bit max
                        show_warning("Ugyldig Frekvens", "Den ønskede frekvens kan ikke opnås (OCR1A uden for rækkevidde).")
                        return
                    ocr1a = round(top_float)
                    actual_freq = cpu_freq_hz / (2 * prescaler_int * (ocr1a + 1))
                elif "TOP=ICR1" in selected_mode:
                     if top_float < 0 or top_float > max_top_val: # Check against 16-bit max
                        show_warning("Ugyldig Frekvens", "Den ønskede frekvens kan ikke opnås (ICR1 uden for rækkevidde).")
                        return
                     icr1 = round(top_float)
                     actual_freq = cpu_freq_hz / (2 * prescaler_int * (icr1 + 1))
                
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            elif "PWM" in selected_mode:
                desired_freq = float(self.timer1_freq_entry.get())
                desired_duty_cycle_perc = float(self.timer1_duty_entry.get())
                if not (0 <= desired_duty_cycle_perc <= 100):
                    show_warning("Ugyldig Duty Cycle", "Duty Cycle skal være mellem 0 og 100%.")
                    return
                desired_duty_cycle = desired_duty_cycle_perc / 100.0

                top_value = 0 # This will be set based on mode

                if "TOP_fixed" in wgm_bits: # 8-bit, 9-bit, 10-bit PWM
                    top_value = wgm_bits["TOP_fixed"]
                    
                    if "Phase Correct" in selected_mode:
                        actual_freq = cpu_freq_hz / (2 * prescaler_int * top_value)
                    elif "Fast PWM" in selected_mode:
                        actual_freq = cpu_freq_hz / (prescaler_int * (top_value + 1))
                    else:
                        show_error("Fejl", "Ukendt PWM-tilstand for Timer1.")
                        return

                    ocr1a_float = top_value * desired_duty_cycle
                    ocr1a = round(ocr1a_float)
                    if ocr1a < 0 or ocr1a > top_value:
                        show_warning("Ugyldig Duty Cycle", "Den ønskede Duty Cycle kan ikke opnås (OCR1A uden for rækkevidde for fast TOP).")
                        return
                    
                    if "Phase Correct" in selected_mode:
                        actual_duty = (ocr1a / top_value) * 100 if top_value > 0 else 0
                    elif "Fast PWM" in selected_mode:
                        actual_duty = (ocr1a / (top_value + 1)) * 100 if (top_value + 1) > 0 else 0


                elif "TOP=ICR1" in selected_mode or "TOP=OCR1A" in selected_mode: # Variable TOP PWM
                    divisor = 1
                    if "Phase Correct" in selected_mode:
                        divisor = 2

                    denominator = divisor * prescaler_int * desired_freq
                    if denominator == 0:
                        show_error("Fejl", "Den ønskede frekvens er for lav eller nul.")
                        return

                    top_float = (cpu_freq_hz / denominator) - 1
                    if top_float < 0 or top_float > max_top_val:
                        show_warning("Ugyldig Frekvens", "Den ønskede frekvens kan ikke opnås (TOP værdi uden for rækkevidde).")
                        return

                    top_value = round(top_float)
                    
                    if "TOP=ICR1" in selected_mode:
                        icr1 = top_value
                    elif "TOP=OCR1A" in selected_mode:
                        ocr1a = top_value

                    actual_freq = cpu_freq_hz / (divisor * prescaler_int * (top_value + 1))

                    ocr1a_duty_float = top_value * desired_duty_cycle
                    if ocr1a_duty_float < 0 or ocr1a_duty_float > top_value:
                        show_warning("Ugyldig Duty Cycle", "Den ønskede Duty Cycle kan ikke opnås (OCR1A for duty cycle uden for rækkevidde).")
                        return
                    ocr1a = round(ocr1a_duty_float) # This OCR1A is for duty cycle, not TOP

                    if "Phase Correct" in selected_mode:
                        actual_duty = (ocr1a / top_value) * 100 if top_value > 0 else 0
                    elif "Fast PWM" in selected_mode:
                        actual_duty = (ocr1a / (top_value + 1)) * 100 if (top_value + 1) > 0 else 0

                else:
                    show_error("Fejl", "Ukendt PWM-tilstand for Timer1.")
                    return

                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            else:
                show_warning("Ugyldig Tilstand", "Vælg venligst en gyldig timertilstand.")
                return

            self.timer1_actual_freq_label.set(f"{actual_freq:.2f} Hz / {actual_delay_s*1000:.2f} ms" if selected_mode == "Normal" else f"{actual_freq:.2f} Hz")
            self.timer1_error_label.set(f"{calc_error:.4f}%")
            self.timer1_tccr1a_label.set(f"0b{tccr1a:08b}")
            self.timer1_tccr1b_label.set(f"0b{tccr1b:08b}")
            self.timer1_tccr1c_label.set(f"0b{tccr1c:08b}")
            self.timer1_ocr1a_label.set(f"{ocr1a}")
            self.timer1_icr1_label.set(f"{icr1}")
            self.timer1_tcnt1_label.set(f"{tcnt1}")
            self.timer1_actual_duty_label.set(f"{actual_duty:.2f}%")


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
        self.timer1_actual_freq_label.set("N/A")
        self.timer1_error_label.set("N/A")
        self.timer1_tccr1a_label.set("N/A")
        self.timer1_tccr1b_label.set("N/A")
        self.timer1_tccr1c_label.set("N/A")
        self.timer1_ocr1a_label.set("N/A")
        self.timer1_icr1_label.set("N/A")
        self.timer1_tcnt1_label.set("N/A")
        self.timer1_actual_duty_label.set("N/A")