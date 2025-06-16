import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T0
from utils import parse_hex_bin_int, show_error, show_warning

class Timer0Calculator(Gtk.Box):
    """
    GTK4 Calculator for Timer0 settings.
    """
    def __init__(self, master_box, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_hexpand(True)
        self.set_vexpand(True)
        
        self.master_box = master_box
        self.cpu_freq_entry = cpu_freq_entry

        self._create_widgets()

    def _create_widgets(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_vexpand(False)
        grid.set_column_homogeneous(False)
        self.append(grid)

        # --- Mode Selection ---
        label = Gtk.Label(label="Timer Mode:")
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 0, 1, 1)
        self.timer0_mode_combobox = Gtk.ComboBoxText()
        for mode_name in WGM_BITS_T0.keys():
            self.timer0_mode_combobox.append_text(mode_name)
        self.timer0_mode_combobox.set_active_id("Normal") # Set default mode to "Normal"
        self.timer0_mode_combobox.connect("changed", self._on_timer0_mode_change)
        self.timer0_mode_combobox.set_hexpand(True)
        self.timer0_mode_combobox.set_halign(Gtk.Align.FILL)
        grid.attach(self.timer0_mode_combobox, 1, 0, 1, 1)

        # --- Formula Label (Dynamic) ---
        self.formula_label = Gtk.Label(label="", xalign=0.5) # Centered
        self.formula_label.set_markup("<b>N/A</b>")
        self.formula_label.set_wrap(True)
        self.formula_label.set_justify(Gtk.Justification.CENTER)
        grid.attach(self.formula_label, 0, 1, 2, 1) # Placed at row 1, spanning 2 columns

        # --- Prescaler Selection (shifted down by 1 row) ---
        label = Gtk.Label(label="Prescaler:")
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 2, 1, 1) # Shifted from row 1 to 2
        self.timer0_prescaler_combobox = Gtk.ComboBoxText()
        prescaler_values = [str(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
        for p_val in prescaler_values:
            self.timer0_prescaler_combobox.append_text(p_val)
        self.timer0_prescaler_combobox.set_active_id("1024") # Set default prescaler to "1024"
        self.timer0_prescaler_combobox.set_hexpand(True)
        self.timer0_prescaler_combobox.set_halign(Gtk.Align.FILL)
        grid.attach(self.timer0_prescaler_combobox, 1, 2, 1, 1) # Shifted from row 1 to 2

        # --- Input Fields (all shifted down by 1 row) ---
        label = Gtk.Label(label="Ønsket Forsinkelse (ms):")
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 3, 1, 1) # Shifted from row 2 to 3
        self.timer0_delay_entry_widget = Gtk.Entry()
        self.timer0_delay_entry_widget.set_hexpand(True)
        self.timer0_delay_entry_widget.set_halign(Gtk.Align.FILL)
        self.timer0_delay_entry_widget.set_width_chars(10)
        grid.attach(self.timer0_delay_entry_widget, 1, 3, 1, 1) # Shifted from row 2 to 3

        label = Gtk.Label(label="Ønsket Frekvens (Hz):")
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 4, 1, 1) # Shifted from row 3 to 4
        self.timer0_freq_entry_widget = Gtk.Entry()
        self.timer0_freq_entry_widget.set_hexpand(True)
        self.timer0_freq_entry_widget.set_halign(Gtk.Align.FILL)
        self.timer0_freq_entry_widget.set_width_chars(10)
        grid.attach(self.timer0_freq_entry_widget, 1, 4, 1, 1) # Shifted from row 3 to 4

        label = Gtk.Label(label="Ønsket Duty Cycle (%):")
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 5, 1, 1) # Shifted from row 4 to 5
        self.timer0_duty_entry_widget = Gtk.Entry()
        self.timer0_duty_entry_widget.set_hexpand(True)
        self.timer0_duty_entry_widget.set_halign(Gtk.Align.FILL)
        self.timer0_duty_entry_widget.set_width_chars(10)
        grid.attach(self.timer0_duty_entry_widget, 1, 5, 1, 1) # Shifted from row 4 to 5

        # --- Calculate Button (shifted down by 1 row) ---
        calculate_button = Gtk.Button(label="Beregn Timer0 Indstillinger")
        calculate_button.connect("clicked", self.calculate_timer0)
        calculate_button.set_size_request(200, 40)
        calculate_button.set_halign(Gtk.Align.CENTER)
        grid.attach(calculate_button, 0, 6, 2, 1) # Shifted from row 5 to 6

        # --- Results Display ---
        results_frame = Gtk.Frame(label="Beregnet Resultat")
        results_frame.set_hexpand(True)
        results_frame.set_vexpand(False)

        results_scrolled = Gtk.ScrolledWindow()
        results_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        results_scrolled.set_min_content_height(150)
        results_scrolled.set_hexpand(True)
        results_scrolled.set_vexpand(True)
        self.append(results_scrolled)

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

        self.timer0_actual_freq_label = Gtk.Label(label="N/A", xalign=0)
        self.timer0_error_label = Gtk.Label(label="N/A", xalign=0)
        self.timer0_tccr0a_label = Gtk.Label(label="N/A", xalign=0)
        self.timer0_tccr0b_label = Gtk.Label(label="N/A", xalign=0)
        self.timer0_ocr0a_label = Gtk.Label(label="N/A", xalign=0)
        self.timer0_tcnt0_label = Gtk.Label(label="N/A", xalign=0)
        self.timer0_actual_duty_label = Gtk.Label(label="N/A", xalign=0)
        self.timer0_com0a_bits_label = Gtk.Label(label="N/A", xalign=0)

        self.timer0_actual_freq_label.set_markup("<span weight='bold'>N/A</span>")
        
        results_grid.attach(Gtk.Label(label="Faktisk Frekvens/Tid:", xalign=0), 0, 0, 1, 1)
        results_grid.attach(self.timer0_actual_freq_label, 1, 0, 1, 1)
        results_grid.attach(Gtk.Label(label="Fejl (%):", xalign=0), 0, 1, 1, 1)
        results_grid.attach(self.timer0_error_label, 1, 1, 1, 1)
        results_grid.attach(Gtk.Label(label="TCCR0A (bin):", xalign=0), 0, 2, 1, 1)
        results_grid.attach(self.timer0_tccr0a_label, 1, 2, 1, 1)
        results_grid.attach(Gtk.Label(label="TCCR0B (bin):", xalign=0), 0, 3, 1, 1)
        results_grid.attach(self.timer0_tccr0b_label, 1, 3, 1, 1)
        results_grid.attach(Gtk.Label(label="OCR0A (dec):", xalign=0), 0, 4, 1, 1)
        results_grid.attach(self.timer0_ocr0a_label, 1, 4, 1, 1)
        results_grid.attach(Gtk.Label(label="TCNT0 Start (dec):", xalign=0), 0, 5, 1, 1)
        results_grid.attach(self.timer0_tcnt0_label, 1, 5, 1, 1)
        results_grid.attach(Gtk.Label(label="Faktisk Duty Cycle (%):", xalign=0), 0, 6, 1, 1)
        results_grid.attach(self.timer0_actual_duty_label, 1, 6, 1, 1)
        results_grid.attach(Gtk.Label(label="COM0A Bits:", xalign=0), 0, 7, 1, 1)
        results_grid.attach(self.timer0_com0a_bits_label, 1, 7, 1, 1)

        self._on_timer0_mode_change(self.timer0_mode_combobox) # Initial call to set formula and visibility

    def _on_timer0_mode_change(self, combobox):
        selected_mode = combobox.get_active_text() or "Normal"
        
        # Update formula label based on selected mode
        if selected_mode == "Normal":
            formula_text = "<b>TCNT0 = 256 - (Ønsket Forsinkelse * f_CPU / Prescaler)</b>"
        elif selected_mode == "CTC":
            formula_text = "<b>OCR0A = (f_CPU / (2 * Prescaler * Ønsket Frekvens)) - 1</b>"
        elif selected_mode == "Fast PWM":
            formula_text = "<b>OCR0A = (Ønsket Duty Cycle / 100) * (255 + 1)</b>"
        elif selected_mode == "Phase Correct PWM":
            formula_text = "<b>OCR0A = (Ønsket Duty Cycle / 100) * 255</b>"
        else:
            formula_text = "<b>N/A</b>"
        self.formula_label.set_markup(formula_text)

        # Update visibility of input fields
        self.timer0_delay_entry_widget.set_visible(selected_mode == "Normal")
        self.timer0_freq_entry_widget.set_visible(selected_mode == "CTC" or "PWM" in selected_mode)
        self.timer0_duty_entry_widget.set_visible("PWM" in selected_mode)

    def calculate_timer0(self, button):
        try:
            if not isinstance(self.cpu_freq_entry, Gtk.Entry):
                raise TypeError(f"ERROR: self.cpu_freq_entry is not a Gtk.Entry! It's {type(self.cpu_freq_entry)}")

            cpu_freq_mhz = float(self.cpu_freq_entry.get_text())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            selected_mode = self.timer0_mode_combobox.get_active_text()
            selected_prescaler_str = self.timer0_prescaler_combobox.get_active_text()

            if selected_prescaler_str is None:
                show_error("Fejl", "Prescaler er ikke valgt.")
                return

            prescaler_int = int(selected_prescaler_str)
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

            wgm_bits = WGM_BITS_T0[selected_mode]
            tccr0a |= (wgm_bits["WGM01"] << 1) | wgm_bits["WGM00"]
            tccr0b |= (wgm_bits["WGM02"] << 3)
            cs_bits = PRESCALERS_T0_T1_T2["T0_T1"][selected_prescaler_str]
            tccr0b |= cs_bits

            if selected_mode == "Normal":
                if not isinstance(self.timer0_delay_entry_widget, Gtk.Entry):
                    raise TypeError(f"ERROR: self.timer0_delay_entry_widget is not a Gtk.Entry! It's {type(self.timer0_delay_entry_widget)}")
                desired_delay_str = self.timer0_delay_entry_widget.get_text()
                if not desired_delay_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket forsinkelse (ms).")
                    return
                desired_delay_ms = float(desired_delay_str)
                desired_delay_s = desired_delay_ms / 1000.0

                required_count_float = desired_delay_s * cpu_freq_hz / prescaler_int
                if required_count_float > 256 or required_count_float <= 0:
                    show_warning("Ugyldig Forsinkelse", "Den ønskede forsinkelse er for lang eller for kort for disse indstillinger.")
                    return

                tcnt0_float = 256 - required_count_float
                if tcnt0_float < 0:
                    tcnt0_float = 0
                tcnt0 = round(tcnt0_float)

                actual_delay_s = prescaler_int * (256 - tcnt0) / cpu_freq_hz
                actual_freq = 1.0 / actual_delay_s
                calc_error = abs(actual_delay_s - desired_delay_s) / desired_delay_s * 100

            elif selected_mode == "CTC":
                if not isinstance(self.timer0_freq_entry_widget, Gtk.Entry):
                    raise TypeError(f"ERROR: self.timer0_freq_entry_widget is not a Gtk.Entry! It's {type(self.timer0_freq_entry_widget)}")
                desired_freq_str = self.timer0_freq_entry_widget.get_text()
                if not desired_freq_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket frekvens (Hz).")
                    return
                desired_freq = float(desired_freq_str)

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
                com0a_bits = "01 (Toggle OC0A on Compare Match)"

            elif "PWM" in selected_mode:
                if not isinstance(self.timer0_freq_entry_widget, Gtk.Entry):
                    raise TypeError(f"ERROR: self.timer0_freq_entry_widget (PWM) is not a Gtk.Entry! It's {type(self.timer0_freq_entry_widget)}")
                if not isinstance(self.timer0_duty_entry_widget, Gtk.Entry):
                    raise TypeError(f"ERROR: self.timer0_duty_entry_widget (PWM) is not a Gtk.Entry! It's {type(self.timer0_duty_entry_widget)}")
                desired_freq_str = self.timer0_freq_entry_widget.get_text()
                desired_duty_cycle_perc_str = self.timer0_duty_entry_widget.get_text()

                if not desired_freq_str or not desired_duty_cycle_perc_str:
                    show_warning("Input Mangel", "Indtast venligst ønsket frekvens (Hz) og Duty Cycle (%).")
                    return

                desired_freq = float(desired_freq_str)
                desired_duty_cycle_perc = float(desired_duty_cycle_perc_str)

                if not (0 <= desired_duty_cycle_perc <= 100):
                    show_warning("Ugyldig Duty Cycle", "Duty Cycle skal være mellem 0 og 100%.")
                    return
                desired_duty_cycle = desired_duty_cycle_perc / 100.0

                top_value = 255
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
                    show_warning("Ugyldig Duty Cycle", "Den ønskede Duty Cycle kan ikke opnås (OCR0A uden for rækkevidde for fast TOP).")
                    return
                ocr0a = round(ocr0a_float)

                if selected_mode == "Fast PWM":
                    actual_duty = (ocr0a / (top_value + 1)) * 100
                elif selected_mode == "Phase Correct PWM":
                    actual_duty = (ocr0a / top_value) * 100

                calc_error = abs(actual_freq - desired_freq) / desired_freq * 100

            else:
                show_warning("Ugyldig Tilstand", "Vælg venligst en gyldig timertilstand.")
                return

            self.timer0_actual_freq_label.set_markup(f"<span weight='bold'>{actual_freq:.2f} Hz / {actual_delay_s*1000:.2f} ms</span>" if selected_mode == "Normal" else f"<span weight='bold'>{actual_freq:.2f} Hz</span>")
            self.timer0_error_label.set_label(f"{calc_error:.4f}%")
            self.timer0_tccr0a_label.set_label(f"0b{tccr0a:08b}")
            self.timer0_tccr0b_label.set_label(f"0b{tccr0b:08b}")
            self.timer0_ocr0a_label.set_label(f"{ocr0a}")
            self.timer0_tcnt0_label.set_label(f"{tcnt0}")
            self.timer0_actual_duty_label.set_label(f"{actual_duty:.2f}%")
            self.timer0_com0a_bits_label.set_label(com0a_bits)

        except ValueError as e:
            show_error("Ugyldigt Input", f"Indtast venligst gyldige tal for CPU Frekvens eller andre inputfelter. Detaljer: {e}")
            self._clear_results()
        except KeyError as e:
            show_error("Konfigurationsfejl", f"Ukendt mode eller prescaler: {e}. Kontroller indstillingerne i constants.py")
            self._clear_results()
        except TypeError as e:
            show_error("PROGRAMFEJL (TYPE)", f"En brugerflade-widget er af forkert type. Detaljer: {e}. Dette er en intern fejl, rapportér venligst.")
            self._clear_results()
        except Exception as e:
            show_error("Fejl", f"En uventet fejl opstod: {e}")
            self._clear_results()

    def _clear_results(self):
        self.timer0_actual_freq_label.set_markup("<span weight='bold'>N/A</span>")
        self.timer0_error_label.set_label("N/A")
        self.timer0_tccr0a_label.set_label("N/A")
        self.timer0_tccr0b_label.set_label("N/A")
        self.timer0_ocr0a_label.set_label("N/A")
        self.timer0_tcnt0_label.set_label("N/A")
        self.timer0_actual_duty_label.set_label("N/A")
        self.timer0_com0a_bits_label.set_label("N/A")
