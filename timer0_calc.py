# timer0_calc.py
import tkinter as tk
from tkinter import ttk
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T0
from utils import parse_hex_bin_int, show_error, show_warning

class Timer0Calculator:
    def __init__(self, master_frame, cpu_freq_var):
        self.master_frame = master_frame
        self.cpu_freq_entry_var = cpu_freq_var # Use shared CPU freq var

        # Timer0 StringVars
        self.timer0_mode_selection = tk.StringVar(value="Normal")
        self.timer0_prescaler_var = tk.StringVar(value="1")
        self.timer0_delay_entry = tk.StringVar()
        self.timer0_freq_entry = tk.StringVar()
        self.timer0_duty_entry = tk.StringVar()
        self.timer0_actual_freq_label = tk.StringVar()
        self.timer0_error_label = tk.StringVar()
        self.timer0_tccr0a_label = tk.StringVar()
        self.timer0_tccr0b_label = tk.StringVar()
        self.timer0_ocr0a_label = tk.StringVar()
        self.timer0_tcnt0_label = tk.StringVar()
        self.timer0_actual_duty_label = tk.StringVar()
        self.timer0_com0a_bits_label = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        frame = self.master_frame
        
        # Mode Selection
        ttk.Label(frame, text="Timer Mode:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.timer0_mode_combobox = ttk.Combobox(frame, textvariable=self.timer0_mode_selection, state="readonly")
        self.timer0_mode_combobox['values'] = list(WGM_BITS_T0.keys())
        self.timer0_mode_combobox.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.timer0_mode_combobox.bind("<<ComboboxSelected>>", self._on_timer0_mode_change)

        # Prescaler Selection
        ttk.Label(frame, text="Prescaler:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.timer0_prescaler_combobox = ttk.Combobox(frame, textvariable=self.timer0_prescaler_var, state="readonly")
        self.timer0_prescaler_combobox['values'] = [p for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"] # Exclude "0" for stopped
        self.timer0_prescaler_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # Input fields (toggle visibility based on mode)
        ttk.Label(frame, text="Ønsket Forsinkelse (ms):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.timer0_delay_entry_widget = ttk.Entry(frame, textvariable=self.timer0_delay_entry)
        self.timer0_delay_entry_widget.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="Ønsket Frekvens (Hz):").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.timer0_freq_entry_widget = ttk.Entry(frame, textvariable=self.timer0_freq_entry)
        self.timer0_freq_entry_widget.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="Ønsket Duty Cycle (%):").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.timer0_duty_entry_widget = ttk.Entry(frame, textvariable=self.timer0_duty_entry)
        self.timer0_duty_entry_widget.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        # Calculate Button
        ttk.Button(frame, text="Beregn Timer0 Indstillinger", command=self.calculate_timer0).grid(row=6, column=0, columnspan=2, pady=10)

        # Results Display
        results_frame = ttk.LabelFrame(frame, text="Beregnet Resultat")
        results_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Label(results_frame, text="Faktisk Frekvens/Tid:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_actual_freq_label, font=("TkDefaultFont", 10, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="Fejl (%):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_error_label).grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCCR0A (bin):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_tccr0a_label).grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCCR0B (bin):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_tccr0b_label).grid(row=3, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="OCR0A (dec):").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_ocr0a_label).grid(row=4, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="TCNT0 Start (dec):").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_tcnt0_label).grid(row=5, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="Faktisk Duty Cycle (%):").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_actual_duty_label).grid(row=6, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="COM0A Bits:").grid(row=7, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(results_frame, textvariable=self.timer0_com0a_bits_label).grid(row=7, column=1, padx=5, pady=2, sticky="w")
        
        self._on_timer0_mode_change() # Set initial visibility

    def _on_timer0_mode_change(self, event=None):
        selected_mode = self.timer0_mode_selection.get()
        # Toggle visibility of delay/freq/duty entry fields
        if selected_mode == "Normal":
            self.timer0_delay_entry_widget.grid()
            self.timer0_freq_entry_widget.grid_remove()
            self.timer0_duty_entry_widget.grid_remove()
        elif selected_mode == "CTC":
            self.timer0_delay_entry_widget.grid_remove()
            self.timer0_freq_entry_widget.grid()
            self.timer0_duty_entry_widget.grid_remove()
        elif "PWM" in selected_mode:
            self.timer0_delay_entry_widget.grid_remove()
            self.timer0_freq_entry_widget.grid()
            self.timer0_duty_entry_widget.grid()

    def calculate_timer0(self):
        try:
            cpu_freq_mhz = float(self.cpu_freq_entry_var.get())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            selected_mode = self.timer0_mode_selection.get()
            selected_prescaler_str = self.timer0_prescaler_var.get()
            prescaler_int = int(selected_prescaler_str)

            # Clear previous results
            self._clear_results()

            tccr0a = 0
            tccr0b = 0
            ocr0a = -1
            tcnt0 = -1
            actual_freq = 0
            actual_delay_s = 0
            actual_duty = 0
            calc_error = 0
            com0a_bits = "N/A"

            # Set WGM bits
            wgm_bits = WGM_BITS_T0[selected_mode]
            tccr0a |= (wgm_bits["WGM01"] << 1) | wgm_bits["WGM00"]
            tccr0b |= (wgm_bits["WGM02"] << 3)

            # Set CS bits
            cs_bits = PRESCALERS_T0_T1_T2["T0_T1"][selected_prescaler_str]
            tccr0b |= cs_bits

            if selected_mode == "Normal":
                desired_delay_ms = float(self.timer0_delay_entry.get())
                desired_delay_s = desired_delay_ms / 1000.0
                
                required_count_float = desired_delay_s * cpu_freq_hz / prescaler_int
                
                if required_count_float > 256 or required_count_float <= 0:
                    show_warning("Ugyldig Forsinkelse", "Den ønskede forsinkelse er for lang eller for kort for disse indstillinger.")
                    return

                tcnt0_float = 256 - required_count_float
                if tcnt0_float < 0: tcnt0_float = 0 # Cannot be negative
                tcnt0 = round(tcnt0_float)
                
                actual_delay_s = prescaler_int * (256 - tcnt0) / cpu_freq_hz
                actual_freq = 1.0 / actual_delay_s
                calc_error = abs(actual_delay_s - desired_delay_s) / desired_delay_s * 100

            elif selected_mode == "CTC":
                desired_freq = float(self.timer0_freq_entry.get())
                
                denominator = 2 * prescaler_int * desired_freq
                if denominator == 0:
                    show_error("Fejl", "Den ønskede frekvens er for lav eller nul.")
                    return

                ocr0a_float = (cpu_freq_hz / denominator) - 1
                if ocr0a_float < 0 or ocr0a_float > 255:
                    show_warning("Ugyldig Frekvens", "Den ønskede frekvens kan ikke opnås med disse indstillinger (OCR0A uden for rækkevidde).")
                    return
                ocr0a = round(ocr0a_float)

                actual_freq = cpu_freq_hz / (2 * prescaler_int * (ocr0a + 1))
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100
                com0a_bits = "01 (Toggle OC0A on Compare Match)" # For CTC output

            elif "PWM" in selected_mode:
                desired_freq = float(self.timer0_freq_entry.get())
                desired_duty_cycle_perc = float(self.timer0_duty_entry.get())
                if not (0 <= desired_duty_cycle_perc <= 100):
                    show_warning("Ugyldig Duty Cycle", "Duty Cycle skal være mellem 0 og 100%.")
                    return
                desired_duty_cycle = desired_duty_cycle_perc / 100.0

                top_value = 255 # TOP is fixed to 0xFF for these modes

                if selected_mode == "Fast PWM":
                    actual_freq = cpu_freq_hz / (prescaler_int * (top_value + 1))
                    ocr0a_float = top_value * desired_duty_cycle
                    com0a_bits = "10 (Clear OC0A on Compare Match, Set at TOP)"
                elif selected_mode == "Phase Correct PWM":
                    actual_freq = cpu_freq_hz / (2 * prescaler_int * top_value)
                    ocr0a_float = top_value * desired_duty_cycle
                    com0a_bits = "10 (Clear OC0A on Compare Match when up-counting, Set when down-counting)"
                else:
                    show_error("Fejl", "Ukendt PWM-tilstand for Timer0.")
                    return

                if ocr0a_float < 0 or ocr0a_float > top_value:
                    show_warning("Ugyldig Duty Cycle", "Den ønskede Duty Cycle kan ikke opnås (OCR0A uden for rækkevidde).")
                    return
                ocr0a = round(ocr0a_float)

                # Recalculate actual duty cycle based on rounded OCR0A
                if selected_mode == "Fast PWM":
                    actual_duty = (ocr0a / (top_value + 1)) * 100
                elif selected_mode == "Phase Correct PWM":
                    actual_duty = (ocr0a / top_value) * 100
                
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            else:
                show_warning("Ugyldig Tilstand", "Vælg venligst en gyldig timertilstand.")
                return

            self.timer0_actual_freq_label.set(f"{actual_freq:.2f} Hz / {actual_delay_s*1000:.2f} ms" if selected_mode == "Normal" else f"{actual_freq:.2f} Hz")
            self.timer0_error_label.set(f"{calc_error:.4f}%")
            self.timer0_tccr0a_label.set(f"0b{tccr0a:08b}")
            self.timer0_tccr0b_label.set(f"0b{tccr0b:08b}")
            self.timer0_ocr0a_label.set(f"{ocr0a}")
            self.timer0_tcnt0_label.set(f"{tcnt0}")
            self.timer0_actual_duty_label.set(f"{actual_duty:.2f}%")
            self.timer0_com0a_bits_label.set(com0a_bits)

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
        self.timer0_actual_freq_label.set("N/A")
        self.timer0_error_label.set("N/A")
        self.timer0_tccr0a_label.set("N/A")
        self.timer0_tccr0b_label.set("N/A")
        self.timer0_ocr0a_label.set("N/A")
        self.timer0_tcnt0_label.set("N/A")
        self.timer0_actual_duty_label.set("N/A")
        self.timer0_com0a_bits_label.set("N/A")