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

        self.master_box = master_box
        self.cpu_freq_entry = cpu_freq_entry # Store the Gtk.Entry widget for CPU frequency

        self._create_widgets()

    def _create_widgets(self):
        # Use Gtk.Grid for precise layout, similar to Tkinter's grid
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.append(grid) # Add the grid to the main vertical box

        # --- Mode Selection ---
        grid.attach(Gtk.Label(label="Timer Mode:"), 0, 1, 1, 1) # col, row, width, height
        self.timer2_mode_combobox = Gtk.ComboBoxText()
        for mode_name in WGM_BITS_T2.keys():
            self.timer2_mode_combobox.append_text(mode_name)
        self.timer2_mode_combobox.set_active_id("Normal") # Set initial value
        self.timer2_mode_combobox.connect("changed", self._on_timer2_mode_change)
        grid.attach(self.timer2_mode_combobox, 1, 1, 1, 1)
        self.timer2_mode_combobox.set_hexpand(True) # Expand horizontally

        # --- Prescaler Selection ---
        grid.attach(Gtk.Label(label="Prescaler:"), 0, 2, 1, 1)
        self.timer2_prescaler_combobox = Gtk.ComboBoxText()
        # Exclude "0" for stopped prescaler
        prescaler_values = [str(p) for p in PRESCALERS_T0_T1_T2["T2"].keys() if p != "0"]
        for p_val in prescaler_values:
            self.timer2_prescaler_combobox.append_text(p_val)
        self.timer2_prescaler_combobox.set_active_id("1") # Set initial value
        grid.attach(self.timer2_prescaler_combobox, 1, 2, 1, 1)
        self.timer2_prescaler_combobox.set_hexpand(True)

        # --- Input fields (toggle visibility based on mode) ---
        grid.attach(Gtk.Label(label="Ønsket Forsinkelse (ms):"), 0, 3, 1, 1)
        self.timer2_delay_entry_widget = Gtk.Entry()
        grid.attach(self.timer2_delay_entry_widget, 1, 3, 1, 1)
        self.timer2_delay_entry_widget.set_hexpand(True)

        grid.attach(Gtk.Label(label="Ønsket Frekvens (Hz):"), 0, 4, 1, 1)
        self.timer2_freq_entry_widget = Gtk.Entry()
        grid.attach(self.timer2_freq_entry_widget, 1, 4, 1, 1)
        self.timer2_freq_entry_widget.set_hexpand(True)

        grid.attach(Gtk.Label(label="Ønsket Duty Cycle (%):"), 0, 5, 1, 1)
        self.timer2_duty_entry_widget = Gtk.Entry()
        grid.attach(self.timer2_duty_entry_widget, 1, 5, 1, 1)
        self.timer2_duty_entry_widget.set_hexpand(True)

        # --- Calculate Button ---
        calculate_button = Gtk.Button(label="Beregn Timer2 Indstillinger")
        calculate_button.connect("clicked", self.calculate_timer2)
        grid.attach(calculate_button, 0, 6, 2, 1) # Span 2 columns
        calculate_button.set_margin_top(10)
        calculate_button.set_margin_bottom(10)

        # --- Results Display ---
        results_frame = Gtk.Frame(label="Beregnet Resultat")
        self.append(results_frame) # Add frame to the main vertical box
        results_frame.set_hexpand(True)
        
        results_grid = Gtk.Grid()
        results_grid.set_row_spacing(5)
        results_grid.set_column_spacing(5)
        results_grid.set_margin_start(5)
        results_grid.set_margin_end(5)
        results_grid.set_margin_top(5)
        results_grid.set_margin_bottom(5)
        results_frame.set_child(results_grid)

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
        
        # FIX: Handle potential None if combobox isn't fully initialized or active_id not set
        if selected_mode is None:
            selected_mode = "Normal"

        if selected_mode == "Normal":
            self.timer2_delay_entry_widget.set_visible(True)
            self.timer2_freq_entry_widget.set_visible(False)
            self.timer2_duty_entry_widget.set_visible(False)
        elif selected_mode == "CTC":
            self.timer2_delay_entry_widget.set_visible(False)
            self.timer2_freq_entry_widget.set_visible(True)
            self.timer2_duty_entry_widget.set_visible(False)
        elif "PWM" in selected_mode:
            self.timer2_delay_entry_widget.set_visible(False)
            self.timer2_freq_entry_widget.set_visible(True)
            self.timer2_duty_entry_widget.set_visible(True)

    def calculate_timer2(self, button): # GTK passes the button object to the callback
        try:
            cpu_freq_mhz = float(self.cpu_freq_entry.get_text())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            selected_mode = self.timer2_mode_combobox.get_active_text()
            selected_prescaler_str = self.timer2_prescaler_combobox.get_active_text()
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
            wgm_bits = WGM_BITS_T2[selected_mode]
            tccr2a |= (wgm_bits["WGM21"] << 1) | wgm_bits["WGM20"]
            tccr2b |= (wgm_bits["WGM22"] << 3) # WGM22 is in TCCR2B, bit 3 for Atmega328P, check datasheet if different

            # Set CS bits
            cs_bits = PRESCALERS_T0_T1_T2["T2"][selected_prescaler_str]
            tccr2b |= cs_bits

            if selected_mode == "Normal":
                desired_delay_ms = float(self.timer2_delay_entry_widget.get_text())
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
                desired_freq = float(self.timer2_freq_entry_widget.get_text())
                
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
                desired_freq = float(self.timer2_freq_entry_widget.get_text())
                desired_duty_cycle_perc = float(self.timer2_duty_entry_widget.get_text())
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

            self.timer2_actual_freq_label.set_markup(f"<span weight='bold'>{actual_freq:.2f} Hz / {actual_delay_s*1000:.2f} ms</span>" if selected_mode == "Normal" else f"<span weight='bold'>{actual_freq:.2f} Hz</span>")
            self.timer2_error_label.set_label(f"{calc_error:.4f}%")
            self.timer2_tccr2a_label.set_label(f"0b{tccr2a:08b}")
            self.timer2_tccr2b_label.set_label(f"0b{tccr2b:08b}")
            self.timer2_ocr2a_label.set_label(f"{ocr2a}")
            self.timer2_tcnt2_label.set_label(f"{tcnt2}")
            self.timer2_actual_duty_label.set_label(f"{actual_duty:.2f}%")

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