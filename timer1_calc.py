import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

# Ensure these are adapted for GTK4 or are simple Python constants/functions
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T1
from utils import parse_hex_bin_int, show_error, show_warning # show_error/warning need GTK4 adaptation

class Timer1Calculator(Gtk.Box):
    """
    GTK4 Calculator for Timer1 settings.
    """
    def __init__(self, master_box, cpu_freq_entry): # master_box is the parent Gtk.Box/Frame
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_hexpand(True) # Ensure the tab expands
        self.set_vexpand(True) # Ensure the tab expands

        self.master_box = master_box
        self.cpu_freq_entry = cpu_freq_entry # Store the Gtk.Entry widget for CPU frequency

        self._create_widgets()

    def _create_widgets(self):
        # Use Gtk.Grid for precise layout, similar to Tkinter's grid
        grid = Gtk.Grid()
        grid.set_row_spacing(10) # Increased for GNOME-like spacing
        grid.set_column_spacing(10)
        grid.set_hexpand(True) # Expand horizontally
        grid.set_vexpand(False) # Let it expand vertically based on content
        grid.set_column_homogeneous(False)
        self.append(grid) # Add the grid to the main vertical box

        # --- Mode Selection ---
        label = Gtk.Label(label="Timer Mode:")
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 0, 1, 1) # col, row, width, height
        self.timer1_mode_combobox = Gtk.ComboBoxText()
        for mode_name in WGM_BITS_T1.keys():
            self.timer1_mode_combobox.append_text(mode_name)
        self.timer1_mode_combobox.set_active_id("Normal") # Set initial mode to Normal
        self.timer1_mode_combobox.connect("changed", self._on_timer1_mode_change)
        self.timer1_mode_combobox.set_hexpand(True) # Expand horizontally
        self.timer1_mode_combobox.set_halign(Gtk.Align.FILL)
        grid.attach(self.timer1_mode_combobox, 1, 0, 1, 1)

        # --- Formula Label (Dynamic) ---
        self.formula_label = Gtk.Label(label="", xalign=0.5) # Centered
        self.formula_label.set_markup("<b>N/A</b>")
        self.formula_label.set_wrap(True)
        self.formula_label.set_justify(Gtk.Justification.CENTER)
        grid.attach(self.formula_label, 0, 1, 2, 1) # Placed at row 1, spanning 2 columns

        # --- Prescaler Selection (shifted down by 1 row) ---
        self.prescaler_label = Gtk.Label(label="Prescaler:")
        self.prescaler_label.set_halign(Gtk.Align.START)
        grid.attach(self.prescaler_label, 0, 2, 1, 1) # Shifted from row 1 to 2
        self.timer1_prescaler_combobox = Gtk.ComboBoxText()
        # Exclude "0" for stopped prescaler
        prescaler_values = [str(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
        for p_val in prescaler_values:
            self.timer1_prescaler_combobox.append_text(p_val)
        self.timer1_prescaler_combobox.set_active_id("1024") # Set initial value
        self.timer1_prescaler_combobox.set_hexpand(True)
        self.timer1_prescaler_combobox.set_halign(Gtk.Align.FILL)
        grid.attach(self.timer1_prescaler_combobox, 1, 2, 1, 1) # Shifted from row 1 to 2

        # --- Input fields (toggle visibility based on mode) ---
        self.timer1_delay_label = Gtk.Label(label="Ønsket Forsinkelse (ms):")
        self.timer1_delay_label.set_halign(Gtk.Align.START)
        grid.attach(self.timer1_delay_label, 0, 3, 1, 1) # Shifted from row 2 to 3
        self.timer1_delay_entry_widget = Gtk.Entry()
        grid.attach(self.timer1_delay_entry_widget, 1, 3, 1, 1) # Shifted from row 2 to 3
        self.timer1_delay_entry_widget.set_hexpand(True)

        self.timer1_freq_label = Gtk.Label(label="Ønsket Frekvens (Hz):")
        self.timer1_freq_label.set_halign(Gtk.Align.START)
        grid.attach(self.timer1_freq_label, 0, 4, 1, 1) # Shifted from row 3 to 4
        self.timer1_freq_entry_widget = Gtk.Entry()
        grid.attach(self.timer1_freq_entry_widget, 1, 4, 1, 1) # Shifted from row 3 to 4
        self.timer1_freq_entry_widget.set_hexpand(True)

        self.timer1_duty_label = Gtk.Label(label="Ønsket Duty Cycle (%):")
        self.timer1_duty_label.set_halign(Gtk.Align.START)
        grid.attach(self.timer1_duty_label, 0, 5, 1, 1) # Shifted from row 4 to 5
        self.timer1_duty_entry_widget = Gtk.Entry()
        grid.attach(self.timer1_duty_entry_widget, 1, 5, 1, 1) # Shifted from row 4 to 5
        self.timer1_duty_entry_widget.set_hexpand(True)

        # --- Calculate Button (shifted down by 1 row) ---
        calculate_button = Gtk.Button(label="Beregn Timer1 Indstillinger")
        calculate_button.connect("clicked", self.calculate_timer1)
        grid.attach(calculate_button, 0, 6, 2, 1) # Span 2 columns, shifted from row 5 to 6
        calculate_button.set_margin_top(10)
        calculate_button.set_margin_bottom(10)

        # --- Results Display ---
        results_frame = Gtk.Frame(label="Beregnet Resultat")
        self.append(results_frame) # Add frame to the main vertical box
        results_frame.set_hexpand(True)
        results_frame.set_vexpand(False) # Allows vertical shrinking if content is small
        
        results_scrolled = Gtk.ScrolledWindow()
        results_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        results_scrolled.set_min_content_height(150) # Minimum height for GNOME-like panels
        results_scrolled.set_hexpand(True)
        results_scrolled.set_vexpand(True)
        results_frame.set_child(results_scrolled) # Set scrolled window as child of frame

        results_grid = Gtk.Grid()
        results_grid.set_row_spacing(10)
        results_grid.set_column_spacing(10)
        results_grid.set_margin_start(5)
        results_grid.set_margin_end(5)
        results_grid.set_margin_top(5)
        results_grid.set_margin_bottom(5)
        results_grid.set_hexpand(True)
        results_grid.set_vexpand(False)
        results_scrolled.set_child(results_grid)

        # Labels for displaying results
        self.timer1_actual_freq_label = Gtk.Label(label="N/A", xalign=0) # xalign for left align
        self.timer1_error_label = Gtk.Label(label="N/A", xalign=0)
        self.timer1_tccr1a_label = Gtk.Label(label="N/A", xalign=0)
        self.timer1_tccr1b_label = Gtk.Label(label="N/A", xalign=0)
        self.timer1_tccr1c_label = Gtk.Label(label="N/A", xalign=0) # New for Timer1
        self.timer1_ocr1a_label = Gtk.Label(label="N/A", xalign=0)
        self.timer1_icr1_label = Gtk.Label(label="N/A", xalign=0) # New for Timer1
        
        # Labels for TCNT and 'x' as per image
        self.timer1_tcnt_result_label = Gtk.Label(label="N/A", xalign=0) # TCNT = Timer_max - x -> TCNT_value
        self.timer1_x_value_label = Gtk.Label(label="N/A", xalign=0) # x = ...

        self.timer1_actual_duty_label = Gtk.Label(label="N/A", xalign=0)

        # Apply bold font to actual_freq_label (Pango markup for GTK labels)
        self.timer1_actual_freq_label.set_markup("<span weight='bold'>N/A</span>")
        
        results_grid.attach(Gtk.Label(label="Faktisk Frekvens/Tid:", xalign=0), 0, 0, 1, 1)
        results_grid.attach(self.timer1_actual_freq_label, 1, 0, 1, 1)
        
        results_grid.attach(Gtk.Label(label="Fejl (%):", xalign=0), 0, 1, 1, 1)
        results_grid.attach(self.timer1_error_label, 1, 1, 1, 1)

        results_grid.attach(Gtk.Label(label="TCCR1A (bin):", xalign=0), 0, 2, 1, 1)
        results_grid.attach(self.timer1_tccr1a_label, 1, 2, 1, 1)

        results_grid.attach(Gtk.Label(label="TCCR1B (bin):", xalign=0), 0, 3, 1, 1)
        results_grid.attach(self.timer1_tccr1b_label, 1, 3, 1, 1)

        results_grid.attach(Gtk.Label(label="TCCR1C (bin):", xalign=0), 0, 4, 1, 1) # New row for TCCR1C
        results_grid.attach(self.timer1_tccr1c_label, 1, 4, 1, 1)
        
        results_grid.attach(Gtk.Label(label="OCR1A (dec):", xalign=0), 0, 5, 1, 1)
        results_grid.attach(self.timer1_ocr1a_label, 1, 5, 1, 1)

        results_grid.attach(Gtk.Label(label="ICR1 (dec):", xalign=0), 0, 6, 1, 1) # New row for ICR1
        results_grid.attach(self.timer1_icr1_label, 1, 6, 1, 1)
        
        # TCNT and 'x' labels
        results_grid.attach(Gtk.Label(label="TCNT1 (Start):", xalign=0), 0, 7, 1, 1)
        results_grid.attach(self.timer1_tcnt_result_label, 1, 7, 1, 1) # Will show TCNT = Timer_max - x -> Value

        results_grid.attach(Gtk.Label(label="Calculated 'x':", xalign=0), 0, 8, 1, 1)
        results_grid.attach(self.timer1_x_value_label, 1, 8, 1, 1) # Will show x = ...

        results_grid.attach(Gtk.Label(label="Faktisk Duty Cycle (%):", xalign=0), 0, 9, 1, 1) # Shifted down by 1
        results_grid.attach(self.timer1_actual_duty_label, 1, 9, 1, 1) # Shifted down by 1
        
        # Call initial visibility setup
        self._on_timer1_mode_change(self.timer1_mode_combobox)
    
    def _on_timer1_mode_change(self, combobox):
        selected_mode = combobox.get_active_text()
        
        if selected_mode is None:
            selected_mode = "Normal" # Fallback if no mode is active initially

        # --- Update Formula Label ---
        wgm_bits = WGM_BITS_T1.get(selected_mode, {})
        formula_text = "<b>N/A</b>"

        if selected_mode == "Normal":
            formula_text = "<b>TCNT1 = 65536 - (Ønsket Forsinkelse * f_CPU / Prescaler)</b>"
        elif "CTC" in selected_mode:
            top_register_name = "ICR1" if "TOP=ICR1" in selected_mode else "OCR1A"
            formula_text = f"<b>{top_register_name} = (f_CPU / (2 * Prescaler * Ønsket Frekvens)) - 1</b>"
        elif "PWM" in selected_mode:
            top_fixed = wgm_bits.get("TOP_fixed")
            
            if top_fixed is not None: # Fixed TOP PWM modes
                if "Fast PWM" in selected_mode:
                    formula_text = f"<b>OCR1A = (Ønsket Duty Cycle / 100) * ({top_fixed} + 1) - 1</b>"
                elif "Phase Correct PWM" in selected_mode:
                    formula_text = f"<b>OCR1A = (Ønsket Duty Cycle / 100) * {top_fixed}</b>"
            else: # Variable TOP PWM modes (TOP=ICR1 or TOP=OCR1A)
                top_register_name = "ICR1" if "TOP=ICR1" in selected_mode else "OCR1A_TOP"
                
                if "Fast PWM" in selected_mode:
                    formula_text = f"<b>{top_register_name} = (f_CPU / (Prescaler * Ønsket Frekvens)) - 1\nOCR1A = (Ønsket Duty Cycle / 100) * ({top_register_name} + 1) - 1</b>"
                elif "Phase Correct PWM" in selected_mode:
                    formula_text = f"<b>{top_register_name} = f_CPU / (2 * Prescaler * Ønsket Frekvens)\nOCR1A = (Ønsket Duty Cycle / 100) * {top_register_name}</b>"
        
        self.formula_label.set_markup(formula_text)


        # --- Update visibility of input fields and their labels ---
        is_normal_mode = (selected_mode == "Normal")
        is_freq_mode = ("CTC" in selected_mode or "PWM" in selected_mode)
        is_pwm_mode = ("PWM" in selected_mode)

        self.timer1_delay_label.set_visible(is_normal_mode)
        self.timer1_delay_entry_widget.set_visible(is_normal_mode)

        self.timer1_freq_label.set_visible(is_freq_mode)
        self.timer1_freq_entry_widget.set_visible(is_freq_mode)

        self.timer1_duty_label.set_visible(is_pwm_mode)
        self.timer1_duty_entry_widget.set_visible(is_pwm_mode)

        # Clear input entries when they become hidden
        if not is_normal_mode:
            self.timer1_delay_entry_widget.set_text("")
        if not is_freq_mode:
            self.timer1_freq_entry_widget.set_text("")
        if not is_pwm_mode:
            self.timer1_duty_entry_widget.set_text("")


    def calculate_timer1(self, button): # GTK passes the button object to the callback
        try:
            # Get CPU frequency from the shared Gtk.Entry widget
            cpu_freq_mhz = float(self.cpu_freq_entry.get_text().replace(',', '.'))
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            
            selected_mode = self.timer1_mode_combobox.get_active_text()
            if selected_mode is None: # Safety check if nothing is selected
                show_error("Fejl", "Timermodus er ikke valgt.")
                return

            selected_prescaler_str = self.timer1_prescaler_combobox.get_active_text()
            if selected_prescaler_str is None:
                show_error("Fejl", "Prescaler er ikke valgt.")
                return
            prescaler_int = int(selected_prescaler_str)

            # Clear previous results
            self._clear_results()

            tccr1a = 0
            tccr1b = 0
            tccr1c = 0 # For OC1A/B/C force output compare, usually not directly set for calculation
            ocr1a = -1
            icr1 = -1
            tcnt1 = -1 # Initial value for TCNT register
            actual_freq = 0
            actual_delay_s = 0
            actual_duty = 0
            calc_error = 0
            calculated_x_value = 0.0 # Initialize for TCNT-x display

            # Set WGM bits
            wgm_bits = WGM_BITS_T1.get(selected_mode, {})
            if not wgm_bits:
                show_error("Konfigurationsfejl", f"Ukendt timermodus: {selected_mode}. Kontroller indstillingerne i constants.py")
                return

            tccr1a |= (wgm_bits.get("WGM11",0) << 1) | wgm_bits.get("WGM10",0)
            tccr1b |= (wgm_bits.get("WGM13",0) << 4) | (wgm_bits.get("WGM12",0) << 3)

            # Set CS bits
            cs_bits = PRESCALERS_T0_T1_T2["T0_T1"].get(selected_prescaler_str)
            if cs_bits is None:
                show_error("Konfigurationsfejl", f"Ukendt prescaler: {selected_prescaler_str}. Kontroller indstillingerne i constants.py")
                return
            tccr1b |= cs_bits

            max_top_val = 65535 # 16-bit timer default max (0xFFFF)

            if selected_mode == "Normal":
                desired_delay_str = self.timer1_delay_entry_widget.get_text().replace(',', '.')
                if not desired_delay_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket forsinkelse (ms).")
                    return
                desired_delay_ms = float(desired_delay_str)
                desired_delay_s = desired_delay_ms / 1000.0
                
                # Calculate 'x' (required_count_float)
                # This x is the number of timer ticks for the desired delay
                calculated_x_value = desired_delay_s * cpu_freq_hz / prescaler_int
                
                if calculated_x_value > (max_top_val + 1) or calculated_x_value <= 0:
                    show_warning("Ugyldig Forsinkelse", f"Den ønskede forsinkelse er for lang eller for kort for disse indstillinger. Max ticks: {max_top_val + 1}.")
                    return

                # Calculate TCNT1 start value for Normal mode (Overflow)
                tcnt1_float = (max_top_val + 1) - calculated_x_value
                if tcnt1_float < 0: tcnt1_float = 0 # TCNT cannot be negative
                tcnt1 = round(tcnt1_float)

                actual_delay_s = prescaler_int * ((max_top_val + 1) - tcnt1) / cpu_freq_hz
                actual_freq = 1.0 / actual_delay_s
                calc_error = abs(actual_delay_s - desired_delay_s) / desired_delay_s * 100

            elif "CTC" in selected_mode:
                desired_freq_str = self.timer1_freq_entry_widget.get_text().replace(',', '.')
                if not desired_freq_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket frekvens (Hz).")
                    return
                desired_freq = float(desired_freq_str)
                
                # CTC uses formula_factor of 2
                denominator = wgm_bits["formula_factor"] * prescaler_int * desired_freq
                if denominator == 0:
                    show_error("Fejl", "Den ønskede frekvens er for lav eller nul.")
                    return

                top_float = (cpu_freq_hz / denominator) - 1 # Always -1 for CTC

                if "TOP=OCR1A" in selected_mode:
                    if top_float < 0 or top_float > max_top_val:
                        show_warning("Ugyldig Frekvens", f"Den ønskede frekvens kan ikke opnås (OCR1A uden for rækkevidde 0-{max_top_val}).")
                        return
                    ocr1a = round(top_float)
                    actual_freq = cpu_freq_hz / (wgm_bits["formula_factor"] * prescaler_int * (ocr1a + 1))
                elif "TOP=ICR1" in selected_mode:
                    if top_float < 0 or top_float > max_top_val:
                        show_warning("Ugyldig Frekvens", f"Den ønskede frekvens kan ikke opnås (ICR1 uden for rækkevidde 0-{max_top_val}).")
                        return
                    icr1 = round(top_float)
                    actual_freq = cpu_freq_hz / (wgm_bits["formula_factor"] * prescaler_int * (icr1 + 1))
                
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            elif "PWM" in selected_mode:
                desired_freq_str = self.timer1_freq_entry_widget.get_text().replace(',', '.')
                desired_duty_cycle_perc_str = self.timer1_duty_entry_widget.get_text().replace(',', '.')

                if not desired_freq_str or not desired_duty_cycle_perc_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket frekvens (Hz) og Duty Cycle (%).")
                    return

                desired_freq = float(desired_freq_str)
                desired_duty_cycle_perc = float(desired_duty_cycle_perc_str)

                if not (0 <= desired_duty_cycle_perc <= 100):
                    show_warning("Ugyldig Duty Cycle", "Duty Cycle skal være mellem 0 og 100%.")
                    return
                desired_duty_cycle = desired_duty_cycle_perc / 100.0

                top_value = 0 # This will be calculated/set based on mode

                if "TOP_fixed" in wgm_bits: # 8-bit, 9-bit, 10-bit fixed TOP PWM modes
                    top_value = wgm_bits["TOP_fixed"]
                    
                    if "Fast PWM" in selected_mode:
                        actual_freq = cpu_freq_hz / (prescaler_int * (top_value + 1))
                        ocr1a_float = (top_value + 1) * desired_duty_cycle - 1 # OCRn = Duty * (TOP+1) - 1
                        actual_duty = ((ocr1a_float + 1) / (top_value + 1)) * 100 if (top_value + 1) > 0 else 0
                    elif "Phase Correct PWM" in selected_mode:
                        actual_freq = cpu_freq_hz / (2 * prescaler_int * top_value)
                        ocr1a_float = top_value * desired_duty_cycle # OCRn = Duty * TOP
                        actual_duty = (ocr1a_float / top_value) * 100 if top_value > 0 else 0
                    else:
                        show_error("Fejl", "Ukendt Fast/Phase Correct PWM-tilstand for Timer1 (Fast TOP).")
                        return

                    ocr1a = round(ocr1a_float)
                    if ocr1a < 0 or ocr1a > top_value:
                        show_warning("Ugyldig Duty Cycle", f"Den ønskede Duty Cycle kan ikke opnås (OCR1A ({ocr1a}) uden for rækkevidde 0-{top_value} for fast TOP).")
                        return
                    

                elif "TOP_variable" in wgm_bits: # Variable TOP PWM modes (TOP=ICR1 or TOP=OCR1A)
                    
                    if wgm_bits["formula_factor"] == 1: # Fast PWM variable TOP
                        top_float = (cpu_freq_hz / (prescaler_int * desired_freq)) - 1
                    elif wgm_bits["formula_factor"] == 2: # Phase Correct PWM variable TOP
                        top_float = cpu_freq_hz / (2 * prescaler_int * desired_freq)
                    else:
                        show_error("Fejl", "Ukendt formula_factor for Variable TOP PWM.")
                        return

                    if top_float < 0 or top_float > max_top_val:
                        show_warning("Ugyldig Frekvens", f"TOP værdi ({top_float:.0f}) uden for rækkevidde (0-{max_top_val}).")
                        return

                    top_value = round(top_float)
                    
                    if "TOP=ICR1" in selected_mode:
                        icr1 = top_value
                        # OCR1A will be used for duty cycle
                    elif "TOP=OCR1A" in selected_mode:
                        ocr1a = top_value # Here OCR1A IS the TOP value, OC1A output is not for duty cycle
                        actual_duty = "N/A" # Cannot calculate OC1A duty cycle directly
                        show_warning("Bemærk", "Når TOP er sat af OCR1A, bruges OC1A typisk ikke til PWM-udgang. Overvej OC1B/OC1C for duty cycle.")
                    
                    # Actual frequency based on the calculated TOP_value
                    if wgm_bits["formula_factor"] == 1: # Fast PWM
                        actual_freq = cpu_freq_hz / (prescaler_int * (top_value + 1))
                    elif wgm_bits["formula_factor"] == 2: # Phase Correct PWM
                        actual_freq = cpu_freq_hz / (2 * prescaler_int * top_value)

                    # Calculate OCR1A for duty cycle (this applies if TOP is ICR1)
                    if actual_duty != "N/A": # Only calculate if not the OCR1A as TOP case
                        if wgm_bits["formula_factor"] == 1: # Fast PWM
                            ocr1a_duty_float = (top_value + 1) * desired_duty_cycle - 1
                        elif wgm_bits["formula_factor"] == 2: # Phase Correct PWM
                            ocr1a_duty_float = top_value * desired_duty_cycle
                        
                        if ocr1a_duty_float < 0 or ocr1a_duty_float > top_value:
                            show_warning("Ugyldig Duty Cycle", f"OCR1A for duty cycle ({ocr1a_duty_float:.0f}) uden for rækkevidde (0-{top_value}).")
                            return
                        ocr1a = round(ocr1a_duty_float) # This OCR1A is for duty cycle
                        
                        if wgm_bits["formula_factor"] == 1: # Fast PWM
                            actual_duty = ((ocr1a + 1) / (top_value + 1)) * 100 if (top_value + 1) > 0 else 0
                        elif wgm_bits["formula_factor"] == 2: # Phase Correct PWM
                            actual_duty = (ocr1a / top_value) * 100 if top_value > 0 else 0

                else:
                    show_error("Fejl", "Ukendt PWM-tilstand for Timer1.")
                    return

                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            else: # Fallback for unhandled modes
                show_warning("Ugyldig Tilstand", "Vælg venligst en gyldig timertilstand.")
                return

            self.timer1_actual_freq_label.set_markup(f"<span weight='bold'>{actual_freq:.2f} Hz / {actual_delay_s*1000:.2f} ms</span>" if selected_mode == "Normal" else f"<span weight='bold'>{actual_freq:.2f} Hz</span>")
            self.timer1_error_label.set_label(f"{calc_error:.4f}%")
            self.timer1_tccr1a_label.set_label(f"0b{tccr1a:08b}")
            self.timer1_tccr1b_label.set_label(f"0b{tccr1b:08b}")
            self.timer1_tccr1c_label.set_label(f"0b{tccr1c:08b}") # TCCR1C bits will usually be 0 unless COM1C0/1 are set
            self.timer1_ocr1a_label.set_label(f"{ocr1a}") # This is now either TOP or compare value
            self.timer1_icr1_label.set_label(f"{icr1}")
            
            # Update TCNT1 and 'x' display based on mode
            if selected_mode == "Normal":
                self.timer1_tcnt_result_label.set_label(f"TCNT1 = {max_top_val + 1} - {calculated_x_value:.0f} -> {tcnt1}")
                self.timer1_x_value_label.set_label(f"x = {calculated_x_value:.2f}")
            else:
                self.timer1_tcnt_result_label.set_label("N/A") # Clear if not Normal mode
                self.timer1_x_value_label.set_label("N/A")    # Clear if not Normal mode

            self.timer1_actual_duty_label.set_label(f"{actual_duty:.2f}%" if actual_duty != "N/A" else "N/A")

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
        self.timer1_actual_freq_label.set_markup("<span weight='bold'>N/A</span>")
        self.timer1_error_label.set_label("N/A")
        self.timer1_tccr1a_label.set_label("N/A")
        self.timer1_tccr1b_label.set_label("N/A")
        self.timer1_tccr1c_label.set_label("N/A")
        self.timer1_ocr1a_label.set_label("N/A")
        self.timer1_icr1_label.set_label("N/A")
        self.timer1_tcnt_result_label.set_label("N/A")
        self.timer1_x_value_label.set_label("N/A")
        self.timer1_actual_duty_label.set_label("N/A")
