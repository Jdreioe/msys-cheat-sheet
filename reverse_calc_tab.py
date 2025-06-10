import tkinter as tk
from tkinter import ttk, messagebox
# Import constants.py for prescaler and WGM bits
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T0, WGM_BITS_T1, WGM_BITS_T2

class ReverseCalculatorTab:
    def __init__(self, master):
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # --- Common Settings ---
        common_frame = ttk.LabelFrame(self.master, text="Fælles Indstillinger")
        common_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(common_frame, text="CPU Clock Freq (MHz):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.cpu_freq_entry = ttk.Entry(common_frame)
        self.cpu_freq_entry.insert(0, str(CPU_FREQ_DEFAULT / 1_000_000)) # Default to 16.0 MHz
        self.cpu_freq_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # --- Timer Selection ---
        timer_selection_frame = ttk.LabelFrame(self.master, text="Vælg Timer")
        timer_selection_frame.pack(padx=10, pady=5, fill="x")

        self.timer_selection_var = tk.StringVar(value="Timer0")
        ttk.Radiobutton(timer_selection_frame, text="Timer0", variable=self.timer_selection_var, value="Timer0", command=self._show_timer_settings).pack(side="left", padx=5)
        ttk.Radiobutton(timer_selection_frame, text="Timer1", variable=self.timer_selection_var, value="Timer1", command=self._show_timer_settings).pack(side="left", padx=5)
        ttk.Radiobutton(timer_selection_frame, text="Timer2", variable=self.timer_selection_var, value="Timer2", command=self._show_timer_settings).pack(side="left", padx=5)

        # --- Timer-Specific Settings Frames ---
        self.timer0_frame = ttk.LabelFrame(self.master, text="Timer0 Register Indstillinger")
        self.timer1_frame = ttk.LabelFrame(self.master, text="Timer1 Register Indstillinger")
        self.timer2_frame = ttk.LabelFrame(self.master, text="Timer2 Register Indstillinger")

        self._setup_timer0_widgets()
        self._setup_timer1_widgets()
        self._setup_timer2_widgets()

        self._show_timer_settings() # Show initial timer settings

        # --- Calculate Button ---
        ttk.Button(self.master, text="Beregn Frekvens", command=self.calculate_frequency_from_registers).pack(pady=10)

        # --- Results Display ---
        results_frame = ttk.LabelFrame(self.master, text="Beregnet Resultat")
        results_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(results_frame, text="Beregnet Frekvens:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.calculated_freq_var = tk.StringVar()
        ttk.Label(results_frame, textvariable=self.calculated_freq_var, font=("TkDefaultFont", 10, "bold")).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(results_frame, text="Timer Mode:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.calculated_mode_var = tk.StringVar()
        ttk.Label(results_frame, textvariable=self.calculated_mode_var).grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(results_frame, text="Prescaler:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.calculated_prescaler_var = tk.StringVar()
        ttk.Label(results_frame, textvariable=self.calculated_prescaler_var).grid(row=2, column=1, padx=5, pady=2, sticky="w")


    def _setup_timer0_widgets(self):
        frame = self.timer0_frame
        
        ttk.Label(frame, text="TCCR0A (bin/hex/dec):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.tccr0a_entry = ttk.Entry(frame)
        self.tccr0a_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="TCCR0B (bin/hex/dec):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.tccr0b_entry = ttk.Entry(frame)
        self.tccr0b_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="OCR0A (dec):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.ocr0a_entry = ttk.Entry(frame)
        self.ocr0a_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # You might also want OCR0B if relevant for Timer0 modes
        # ttk.Label(frame, text="OCR0B (dec):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        # self.ocr0b_entry = ttk.Entry(frame)
        # self.ocr0b_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")


    def _setup_timer1_widgets(self):
        frame = self.timer1_frame
        
        ttk.Label(frame, text="TCCR1A (bin/hex/dec):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.tccr1a_entry = ttk.Entry(frame)
        self.tccr1a_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="TCCR1B (bin/hex/dec):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.tccr1b_entry = ttk.Entry(frame)
        self.tccr1b_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="ICR1 (dec):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.icr1_entry = ttk.Entry(frame)
        self.icr1_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(frame, text="OCR1A (dec):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.ocr1a_entry = ttk.Entry(frame)
        self.ocr1a_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # You might also want OCR1B, OCR1C if relevant
        # ttk.Label(frame, text="OCR1B (dec):").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        # self.ocr1b_entry = ttk.Entry(frame)
        # self.ocr1b_entry.grid(row=4, column=1, padx=5, pady=2, sticky="ew")

    def _setup_timer2_widgets(self):
        frame = self.timer2_frame
        
        ttk.Label(frame, text="TCCR2A (bin/hex/dec):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.tccr2a_entry = ttk.Entry(frame)
        self.tccr2a_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="TCCR2B (bin/hex/dec):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.tccr2b_entry = ttk.Entry(frame)
        self.tccr2b_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(frame, text="OCR2A (dec):").grid(row=2, column=0, padx=5, pady=2, sticky="ew")
        self.ocr2a_entry = ttk.Entry(frame)
        self.ocr2a_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # You might also want OCR2B if relevant
        # ttk.Label(frame, text="OCR2B (dec):").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        # self.ocr2b_entry = ttk.Entry(frame)
        # self.ocr2b_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")


    def _show_timer_settings(self):
        # Hide all timer frames
        self.timer0_frame.pack_forget()
        self.timer1_frame.pack_forget()
        self.timer2_frame.pack_forget()

        # Show the selected timer frame
        selected_timer = self.timer_selection_var.get()
        if selected_timer == "Timer0":
            self.timer0_frame.pack(padx=10, pady=5, fill="x")
        elif selected_timer == "Timer1":
            self.timer1_frame.pack(padx=10, pady=5, fill="x")
        elif selected_timer == "Timer2":
            self.timer2_frame.pack(padx=10, pady=5, fill="x")

    def _parse_hex_bin_int(self, value_str):
        """Helper to parse hex (0x...), binary (0b...), or decimal strings."""
        value_str = value_str.strip()
        if not value_str:
            return 0 # Default to 0 for empty input to avoid ValueError
        try:
            if value_str.lower().startswith("0x"):
                return int(value_str, 16)
            elif value_str.lower().startswith("0b"):
                return int(value_str, 2)
            else:
                return int(value_str)
        except ValueError:
            raise ValueError(f"Ugyldigt talformat: '{value_str}'")

    def calculate_frequency_from_registers(self):
        try:
            # Get CPU Frequency
            cpu_freq_mhz = float(self.cpu_freq_entry.get())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000

            selected_timer = self.timer_selection_var.get()

            # --- Logic for Timer0 ---
            if selected_timer == "Timer0":
                tccr0a_val = self._parse_hex_bin_int(self.tccr0a_entry.get())
                tccr0b_val = self._parse_hex_bin_int(self.tccr0b_entry.get())
                ocr0a_val = self._parse_hex_bin_int(self.ocr0a_entry.get()) # Use _parse_hex_bin_int for robustness
                # Assuming OCR0B might be needed for some modes, add a field if so
                # ocr0b_val = self._parse_hex_bin_int(self.ocr0b_entry.get())

                # Extract WGM bits (WGM02 from TCCR0B, WGM01/WGM00 from TCCR0A)
                wgm02 = (tccr0b_val >> 3) & 0x01
                wgm01 = (tccr0a_val >> 1) & 0x01
                wgm00 = tccr0a_val & 0x01

                # Extract CS bits (CS02, CS01, CS00 from TCCR0B)
                cs_bits = tccr0b_val & 0x07

                # Find the matching WGM mode
                current_mode_name = "Ukendt Tilstand"
                top_value = 0 # Default TOP
                for mode_name, bits in WGM_BITS_T0.items():
                    if (bits["WGM02"] == wgm02 and
                        bits["WGM01"] == wgm01 and
                        bits["WGM00"] == wgm00):
                        current_mode_name = mode_name
                        if mode_name == "CTC":
                            top_value = ocr0a_val # TOP is OCR0A for Timer0 CTC
                        elif mode_name == "Normal" or "PWM" in mode_name:
                            top_value = 0xFF # Fixed TOP for 8-bit modes (Normal, Fast PWM, Phase Correct PWM)
                        break

                # Find the prescaler value
                prescaler_val = 0
                for p_str, p_bits in PRESCALERS_T0_T1_T2["T0_T1"].items():
                    if p_bits == cs_bits:
                        prescaler_val = int(p_str)
                        break
                
                if prescaler_val == 0:
                    messagebox.showwarning("Fejl", "Ugyldig prescaler indstilling for Timer0. Timeren er muligvis stoppet.")
                    self._display_results("N/A", "N/A", "N/A", "Fejl")
                    return

                # Calculate Frequency
                actual_freq = 0
                if current_mode_name in ["Normal", "CTC"]:
                    # F_OVF = F_CPU / (N * (TOP + 1))
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif "PWM" in current_mode_name:
                    # F_PWM = F_CPU / (N * (TOP + 1))
                    # Note: For Phase Correct PWM, it's often 2*N*(TOP+1)
                    # For Fast PWM, it's N*(TOP+1)
                    # This simplified logic assumes Fast PWM for now. Adjust based on specific WGM details.
                    if "Phase Correct" in current_mode_name:
                        actual_freq = cpu_freq_hz / (2 * prescaler_val * (top_value + 1))
                    else: # Fast PWM
                        actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                
                self._display_results(f"{actual_freq:.2f} Hz", current_mode_name, prescaler_val, "OK")


            # --- Logic for Timer1 ---
            elif selected_timer == "Timer1":
                tccr1a_val = self._parse_hex_bin_int(self.tccr1a_entry.get())
                tccr1b_val = self._parse_hex_bin_int(self.tccr1b_entry.get())
                icr1_val = self._parse_hex_bin_int(self.icr1_entry.get())
                ocr1a_val = self._parse_hex_bin_int(self.ocr1a_entry.get())

                # Extract WGM bits (WGM13, WGM12 from TCCR1B; WGM11, WGM10 from TCCR1A)
                wgm13 = (tccr1b_val >> 4) & 0x01
                wgm12 = (tccr1b_val >> 3) & 0x01
                wgm11 = (tccr1a_val >> 1) & 0x01
                wgm10 = tccr1a_val & 0x01

                # Extract CS bits (CS12, CS11, CS10 from TCCR1B)
                cs_bits = tccr1b_val & 0x07

                # Find the matching WGM mode and determine TOP value
                current_mode_name = "Ukendt Tilstand"
                top_value = 0
                for mode_name, bits in WGM_BITS_T1.items():
                    if (bits.get("WGM13", 0) == wgm13 and
                        bits.get("WGM12", 0) == wgm12 and
                        bits.get("WGM11", 0) == wgm11 and
                        bits.get("WGM10", 0) == wgm10):
                        
                        current_mode_name = mode_name
                        if "TOP_fixed" in bits:
                            top_value = bits["TOP_fixed"]
                        elif "TOP=OCR1A" in mode_name:
                            top_value = ocr1a_val
                        elif "TOP=ICR1" in mode_name:
                            top_value = icr1_val
                        elif mode_name == "Normal":
                            top_value = 0xFFFF # 16-bit
                        break
                
                if current_mode_name == "Ukendt Tilstand":
                    messagebox.showwarning("Ukendt WGM", "Kombinationen af WGM-bits svarer ikke til en kendt tilstand. Antager Normal Mode (TOP=0xFFFF).")
                    top_value = 0xFFFF


                # Find the prescaler value
                prescaler_val = 0
                for p_str, p_bits in PRESCALERS_T0_T1_T2["T0_T1"].items():
                    if p_bits == cs_bits:
                        prescaler_val = int(p_str)
                        break
                
                if prescaler_val == 0:
                    messagebox.showwarning("Fejl", "Ugyldig prescaler indstilling for Timer1. Timeren er muligvis stoppet.")
                    self._display_results("N/A", "N/A", "N/A", "Fejl")
                    return

                # Calculate Frequency based on identified mode
                actual_freq = 0
                if "PWM" in current_mode_name and "Phase Correct" in current_mode_name:
                    # Phase Correct PWM frequency: F_PWM = F_CPU / (2 * N * TOP)
                    # Note: TOP is usually (TOP+1) for these formulas.
                    # The formulas in datasheets can be tricky.
                    # Common formula is F_PWM = F_CPU / (2 * N * TOP) for Phase Correct
                    # And F_PWM = F_CPU / (N * (TOP + 1)) for Fast PWM
                    # We'll use (TOP + 1) for consistency in our formulas if it applies.
                    actual_freq = cpu_freq_hz / (2 * prescaler_val * (top_value + 1))
                elif "PWM" in current_mode_name and "Fast PWM" in current_mode_name:
                     actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif "CTC" in current_mode_name:
                    # CTC frequency: F_OCnx = F_CPU / (2 * N * (TOP + 1)) when using toggle output
                    actual_freq = cpu_freq_hz / (2 * prescaler_val * (top_value + 1))
                elif current_mode_name == "Normal":
                    # Normal mode (Overflow): F_OVF = F_CPU / (N * (MAX_VALUE + 1))
                    actual_freq = cpu_freq_hz / (prescaler_val * (0xFFFF + 1)) # 16-bit timer max value
                else:
                    messagebox.showwarning("Advarsel", "Ukendt tilstand for frekvensberegning. Antager Normal Mode.")
                    actual_freq = cpu_freq_hz / (prescaler_val * (0xFFFF + 1))


                self._display_results(f"{actual_freq:.2f} Hz", current_mode_name, prescaler_val, "OK")


            # --- Logic for Timer2 ---
            elif selected_timer == "Timer2":
                tccr2a_val = self._parse_hex_bin_int(self.tccr2a_entry.get())
                tccr2b_val = self._parse_hex_bin_int(self.tccr2b_entry.get())
                ocr2a_val = self._parse_hex_bin_int(self.ocr2a_entry.get())

                # Extract WGM bits (WGM22 from TCCR2B, WGM21/WGM20 from TCCR2A)
                wgm22 = (tccr2b_val >> 6) & 0x01 # WGM22 is bit 6 in TCCR2B
                wgm21 = (tccr2a_val >> 1) & 0x01
                wgm20 = tccr2a_val & 0x01

                # Extract CS bits (CS22, CS21, CS20 from TCCR2B)
                cs_bits = tccr2b_val & 0x07

                # Find the matching WGM mode
                current_mode_name = "Ukendt Tilstand"
                top_value = 0 # Default TOP
                for mode_name, bits in WGM_BITS_T2.items():
                    if (bits["WGM22"] == wgm22 and
                        bits["WGM21"] == wgm21 and
                        bits["WGM20"] == wgm20):
                        current_mode_name = mode_name
                        if mode_name == "CTC":
                            top_value = ocr2a_val
                        elif mode_name == "Normal" or "PWM" in mode_name:
                            top_value = 0xFF # Fixed TOP for 8-bit modes (Normal, Fast PWM, Phase Correct PWM)
                        break

                # Find the prescaler value (using T2 specific prescalers)
                prescaler_val = 0
                for p_str, p_bits in PRESCALERS_T0_T1_T2["T2"].items():
                    if p_bits == cs_bits:
                        prescaler_val = int(p_str)
                        break

                if prescaler_val == 0:
                    messagebox.showwarning("Fejl", "Ugyldig prescaler indstilling for Timer2. Timeren er muligvis stoppet.")
                    self._display_results("N/A", "N/A", "N/A", "Fejl")
                    return

                # Calculate Frequency
                actual_freq = 0
                if current_mode_name in ["Normal", "CTC"]:
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif "PWM" in current_mode_name:
                    if "Phase Correct" in current_mode_name:
                        actual_freq = cpu_freq_hz / (2 * prescaler_val * (top_value + 1))
                    else: # Fast PWM
                        actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                
                self._display_results(f"{actual_freq:.2f} Hz", current_mode_name, prescaler_val, "OK")


        except ValueError as ve:
            messagebox.showerror("Input Fejl", f"Ugyldigt input: {ve}. Sørg for, at alle felter indeholder gyldige tal eller binære/hex værdier.")
            self._display_results("N/A", "N/A", "N/A", "Fejl")
        except KeyError as ke:
            messagebox.showerror("Konfigurationsfejl", f"Ukendt konfiguration: {ke}. Kontroller WGM-bits eller prescaler-indstillinger.")
            self._display_results("N/A", "N/A", "N/A", "Fejl")
        except Exception as e:
            messagebox.showerror("Fejl", f"En uventet fejl opstod: {e}")
            self._display_results("N/A", "N/A", "N/A", "Fejl")

    def _display_results(self, freq, mode, prescaler, error=""):
        self.calculated_freq_var.set(freq)
        self.calculated_mode_var.set(mode)
        self.calculated_prescaler_var.set(str(prescaler))
        # Assuming you have an error status label
        # self.error_status_var.set(error)