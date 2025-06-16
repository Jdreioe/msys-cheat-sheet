import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

# Ensure these are adapted for GTK4 or are simple Python constants/functions
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T2
from utils import parse_hex_bin_int, show_error, show_warning # show_error/warning need GTK4 adaptation

class Timer2Calculator(Gtk.Box):
    """
    GTK4 Calculator for Timer2 settings.
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
        self.timer2_mode_combobox = Gtk.ComboBoxText()
        for mode_name in WGM_BITS_T2.keys():
            self.timer2_mode_combobox.append_text(mode_name)
        self.timer2_mode_combobox.set_active_id("Normal") # Set initial mode to Normal
        self.timer2_mode_combobox.connect("changed", self._on_timer2_mode_change)
        self.timer2_mode_combobox.set_hexpand(True) # Expand horizontally
        self.timer2_mode_combobox.set_halign(Gtk.Align.FILL)
        grid.attach(self.timer2_mode_combobox, 1, 0, 1, 1)

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
        self.timer2_prescaler_combobox = Gtk.ComboBoxText()
        # Exclude "0" for stopped prescaler
        prescaler_values = [str(p) for p in PRESCALERS_T0_T1_T2["T2"].keys() if p != "0"]
        for p_val in prescaler_values:
            self.timer2_prescaler_combobox.append_text(p_val)
        self.timer2_prescaler_combobox.set_active_id("1024") # Set initial value
        self.timer2_prescaler_combobox.set_hexpand(True)
        self.timer2_prescaler_combobox.set_halign(Gtk.Align.FILL)
        grid.attach(self.timer2_prescaler_combobox, 1, 2, 1, 1) # Shifted from row 1 to 2

        # --- Input fields (toggle visibility based on mode) ---
        self.timer2_delay_label = Gtk.Label(label="Ønsket Forsinkelse (ms):")
        self.timer2_delay_label.set_halign(Gtk.Align.START)
        grid.attach(self.timer2_delay_label, 0, 3, 1, 1) # Shifted from row 2 to 3
        self.timer2_delay_entry_widget = Gtk.Entry()
        self.timer2_delay_entry_widget.set_hexpand(True)
        self.timer2_delay_entry_widget.set_halign(Gtk.Align.FILL)
        self.timer2_delay_entry_widget.set_width_chars(10)
        grid.attach(self.timer2_delay_entry_widget, 1, 3, 1, 1) # Shifted from row 2 to 3

        self.timer2_freq_label = Gtk.Label(label="Ønsket Frekvens (Hz):")
        self.timer2_freq_label.set_halign(Gtk.Align.START)
        grid.attach(self.timer2_freq_label, 0, 4, 1, 1) # Shifted from row 3 to 4
        self.timer2_freq_entry_widget = Gtk.Entry()
        self.timer2_freq_entry_widget.set_hexpand(True)
        self.timer2_freq_entry_widget.set_halign(Gtk.Align.FILL)
        self.timer2_freq_entry_widget.set_width_chars(10)
        grid.attach(self.timer2_freq_entry_widget, 1, 4, 1, 1) # Shifted from row 3 to 4

        self.timer2_duty_label = Gtk.Label(label="Ønsket Duty Cycle (%):")
        self.timer2_duty_label.set_halign(Gtk.Align.START)
        grid.attach(self.timer2_duty_label, 0, 5, 1, 1) # Shifted from row 4 to 5
        self.timer2_duty_entry_widget = Gtk.Entry()
        self.timer2_duty_entry_widget.set_hexpand(True)
        self.timer2_duty_entry_widget.set_halign(Gtk.Align.FILL)
        self.timer2_duty_entry_widget.set_width_chars(10)
        grid.attach(self.timer2_duty_entry_widget, 1, 5, 1, 1) # Shifted from row 4 to 5

        # --- Calculate Button (shifted down by 1 row) ---
        calculate_button = Gtk.Button(label="Beregn Timer2 Indstillinger")
        calculate_button.connect("clicked", self.calculate_timer2)
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
        self.timer2_actual_freq_label = Gtk.Label(label="N/A", xalign=0) # xalign for left align
        self.timer2_error_label = Gtk.Label(label="N/A", xalign=0)
        self.timer2_tccr2a_label = Gtk.Label(label="N/A", xalign=0)
        self.timer2_tccr2b_label = Gtk.Label(label="N/A", xalign=0)
        self.timer2_ocr2a_label = Gtk.Label(label="N/A", xalign=0)
        self.timer2_tcnt2_label = Gtk.Label(label="N/A", xalign=0)
        self.timer2_actual_duty_label = Gtk.Label(label="N/A", xalign=0)

        # Apply bold font to actual_freq_label (Pango markup for GTK labels)
        self.timer2_actual_freq_label.set_markup("<span weight='bold'>N/A</span>")
        
        results_grid.attach(Gtk.Label(label="Faktisk Frekvens/Tid:", xalign=0), 0, 0, 1, 1)
        results_grid.attach(self.timer2_actual_freq_label, 1, 0, 1, 1)
        
        results_grid.attach(Gtk.Label(label="Fejl (%):", xalign=0), 0, 1, 1, 1)
        results_grid.attach(self.timer2_error_label, 1, 1, 1, 1)

        results_grid.attach(Gtk.Label(label="TCCR2A (bin):", xalign=0), 0, 2, 1, 1)
        results_grid.attach(self.timer2_tccr2a_label, 1, 2, 1, 1)

        results_grid.attach(Gtk.Label(label="TCCR2B (bin):", xalign=0), 0, 3, 1, 1)
        results_grid.attach(self.timer2_tccr2b_label, 1, 3, 1, 1)
        
        results_grid.attach(Gtk.Label(label="OCR2A (dec):", xalign=0), 0, 4, 1, 1)
        results_grid.attach(self.timer2_ocr2a_label, 1, 4, 1, 1)

        results_grid.attach(Gtk.Label(label="TCNT2 Start (dec):", xalign=0), 0, 5, 1, 1)
        results_grid.attach(self.timer2_tcnt2_label, 1, 5, 1, 1)

        results_grid.attach(Gtk.Label(label="Faktisk Duty Cycle (%):", xalign=0), 0, 6, 1, 1)
        results_grid.attach(self.timer2_actual_duty_label, 1, 6, 1, 1)
        
        # Call initial visibility setup
        self._on_timer2_mode_change(self.timer2_mode_combobox)

    def _on_timer2_mode_change(self, combobox):
        selected_mode = combobox.get_active_text()
        
        if selected_mode is None:
            selected_mode = "Normal" # Fallback if no mode is active initially

        # --- Update Formula Label ---
        wgm_bits = WGM_BITS_T2.get(selected_mode, {})
        formula_text = "<b>N/A</b>"

        if selected_mode == "Normal":
            formula_text = "<b>TCNT2 = 256 - (Ønsket Forsinkelse * f_CPU / Prescaler)</b>"
        elif selected_mode == "CTC":
            formula_text = "<b>OCR2A = (f_CPU / (2 * Prescaler * Ønsket Frekvens)) - 1</b>"
        elif selected_mode == "Fast PWM":
            top_fixed = wgm_bits.get("TOP_fixed") # Should be 0xFF for Timer2 Fast PWM
            formula_text = f"<b>OCR2A = (Ønsket Duty Cycle / 100) * ({top_fixed} + 1) - 1</b>"
        elif selected_mode == "Phase Correct PWM":
            top_fixed = wgm_bits.get("TOP_fixed") # Should be 0xFF for Timer2 Phase Correct PWM
            formula_text = f"<b>OCR2A = (Ønsket Duty Cycle / 100) * {top_fixed}</b>"
        
        self.formula_label.set_markup(formula_text)


        # --- Update visibility of input fields and their labels ---
        is_normal_mode = (selected_mode == "Normal")
        is_freq_mode = (selected_mode == "CTC" or "PWM" in selected_mode)
        is_pwm_mode = ("PWM" in selected_mode)

        self.timer2_delay_label.set_visible(is_normal_mode)
        self.timer2_delay_entry_widget.set_visible(is_normal_mode)

        self.timer2_freq_label.set_visible(is_freq_mode)
        self.timer2_freq_entry_widget.set_visible(is_freq_mode)

        self.timer2_duty_label.set_visible(is_pwm_mode)
        self.timer2_duty_entry_widget.set_visible(is_pwm_mode)

        # Clear input entries when they become hidden
        if not is_normal_mode:
            self.timer2_delay_entry_widget.set_text("")
        if not is_freq_mode:
            self.timer2_freq_entry_widget.set_text("")
        if not is_pwm_mode:
            self.timer2_duty_entry_widget.set_text("")

    def calculate_timer2(self, button): # GTK passes the button object to the callback
        try:
            cpu_freq_mhz = float(self.cpu_freq_entry.get_text().replace(',', '.'))
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            selected_mode = self.timer2_mode_combobox.get_active_text()
            selected_prescaler_str = self.timer2_prescaler_combobox.get_active_text()

            if selected_prescaler_str is None:
                show_error("Fejl", "Prescaler er ikke valgt.")
                return

            prescaler_int = int(selected_prescaler_str)
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
            wgm_bits = WGM_BITS_T2.get(selected_mode, {})
            if not wgm_bits:
                show_error("Konfigurationsfejl", f"Ukendt timermodus: {selected_mode}. Kontroller indstillingerne i constants.py")
                return

            tccr2a |= (wgm_bits.get("WGM21", 0) << 1) | wgm_bits.get("WGM20", 0)
            tccr2b |= (wgm_bits.get("WGM22", 0) << 3) # WGM22 is in TCCR2B, bit 3 for Atmega328P, check datasheet if different

            # Set CS bits
            cs_bits = PRESCALERS_T0_T1_T2["T2"].get(selected_prescaler_str)
            if cs_bits is None:
                show_error("Konfigurationsfejl", f"Ukendt prescaler: {selected_prescaler_str}. Kontroller indstillingerne i constants.py")
                return
            tccr2b |= cs_bits

            max_top_val = 255 # 8-bit timer default max (0xFF)

            if selected_mode == "Normal":
                desired_delay_str = self.timer2_delay_entry_widget.get_text().replace(',', '.')
                if not desired_delay_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket forsinkelse (ms).")
                    return
                desired_delay_ms = float(desired_delay_str)
                desired_delay_s = desired_delay_ms / 1000.0
                
                required_count_float = desired_delay_s * cpu_freq_hz / prescaler_int
                
                if required_count_float > (max_top_val + 1) or required_count_float <= 0:
                    show_warning("Ugyldig Forsinkelse", f"Den ønskede forsinkelse er for lang eller for kort for disse indstillinger. Max ticks: {max_top_val + 1}.")
                    return

                tcnt2_float = (max_top_val + 1) - required_count_float
                if tcnt2_float < 0: tcnt2_float = 0
                tcnt2 = round(tcnt2_float)
                
                actual_delay_s = prescaler_int * ((max_top_val + 1) - tcnt2) / cpu_freq_hz
                actual_freq = 1.0 / actual_delay_s
                calc_error = abs(actual_delay_s - desired_delay_s) / desired_delay_s * 100

            elif selected_mode == "CTC":
                desired_freq_str = self.timer2_freq_entry_widget.get_text().replace(',', '.')
                if not desired_freq_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket frekvens (Hz).")
                    return
                desired_freq = float(desired_freq_str)
                
                denominator = wgm_bits["formula_factor"] * prescaler_int * desired_freq
                if denominator == 0:
                    show_error("Fejl", "Den ønskede frekvens er for lav eller nul.")
                    return

                ocr2a_float = (cpu_freq_hz / denominator) - 1
                if ocr2a_float < 0 or ocr2a_float > max_top_val:
                    show_warning("Ugyldig Frekvens", f"Den ønskede frekvens kan ikke opnås med disse indstillinger (OCR2A uden for rækkevidde 0-{max_top_val}).")
                    return
                ocr2a = round(ocr2a_float)

                actual_freq = cpu_freq_hz / (wgm_bits["formula_factor"] * prescaler_int * (ocr2a + 1))
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            elif "PWM" in selected_mode:
                desired_freq_str = self.timer2_freq_entry_widget.get_text().replace(',', '.')
                desired_duty_cycle_perc_str = self.timer2_duty_entry_widget.get_text().replace(',', '.')

                if not desired_freq_str or not desired_duty_cycle_perc_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket frekvens (Hz) og Duty Cycle (%).")
                    return

                desired_freq = float(desired_freq_str)
                desired_duty_cycle_perc = float(desired_duty_cycle_perc_str)

                if not (0 <= desired_duty_cycle_perc <= 100):
                    show_warning("Ugyldig Duty Cycle", "Duty Cycle skal være mellem 0 og 100%.")
                    return
                desired_duty_cycle = desired_duty_cycle_perc / 100.0

                top_value = wgm_bits["TOP_fixed"] # TOP is fixed to 0xFF for these modes in Timer2

                if selected_mode == "Fast PWM":
                    actual_freq = cpu_freq_hz / (prescaler_int * (top_value + 1))
                    ocr2a_float = (top_value + 1) * desired_duty_cycle - 1
                    actual_duty = ((ocr2a_float + 1) / (top_value + 1)) * 100 if (top_value + 1) > 0 else 0
                elif selected_mode == "Phase Correct PWM":
                    actual_freq = cpu_freq_hz / (2 * prescaler_int * top_value)
                    ocr2a_float = top_value * desired_duty_cycle
                    actual_duty = (ocr2a_float / top_value) * 100 if top_value > 0 else 0
                else:
                    show_error("Fejl", "Ukendt PWM-tilstand for Timer2.")
                    return

                if ocr2a_float < 0 or ocr2a_float > top_value:
                    show_warning("Ugyldig Duty Cycle", f"Den ønskede Duty Cycle kan ikke opnås (OCR2A ({ocr2a_float:.0f}) uden for rækkevidde 0-{top_value}).")
                    return
                ocr2a = round(ocr2a_float)
                
                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            else:
                show_warning("Ugyldig Tilstand", "Vælg venligst en gyldig timertilstand.")
                return

            self.timer2_actual_freq_label.set_markup(f"<span weight='bold'>{actual_freq:.2f} Hz / {actual_delay_s*1000:.2f} ms</span>" if selected_mode == "Normal" else f"<span weight='bold'>{actual_freq:.2f} Hz</span>")
            self.timer2_error_label.set_label(f"{calc_error:.4f}%")
            self.timer2_tccr2a_label.set_label(f"0b{tccr2a:08b}")
            self.timer2_tccr2b_label.set_label(f"0b{tccr2b:08b}")
            self.timer2_ocr2a_label.set_label(f"{ocr2a}")
            self.timer2_tcnt2_label.set_label(f"{tcnt2}")
            self.timer2_actual_duty_label.set_label(f"{actual_duty:.2f}%" if actual_duty != "N/A" else "N/A")

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
        self.timer2_actual_freq_label.set_markup("<span weight='bold'>N/A</span>")
        self.timer2_error_label.set_label("N/A")
        self.timer2_tccr2a_label.set_label("N/A")
        self.timer2_tccr2b_label.set_label("N/A")
        self.timer2_ocr2a_label.set_label("N/A")
        self.timer2_tcnt2_label.set_label("N/A")
        self.timer2_actual_duty_label.set_label("N/A")
