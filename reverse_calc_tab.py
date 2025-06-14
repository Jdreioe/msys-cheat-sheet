import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango, Gdk

# Import constants.py for prescaler and WGM bits
from constants import CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2, WGM_BITS_T0, WGM_BITS_T1, WGM_BITS_T2
from utils import parse_hex_bin_int, show_error, show_warning  # Ensure these are GTK4 compatible


class ReverseCalculatorTab(Gtk.Box):
    """
    GTK4 tab for reverse calculation (registers to frequency).
    """
    def __init__(self, cpu_freq_entry):  # Renamed parameter to clarify it's a Gtk.Entry
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)

        self.cpu_freq_entry = cpu_freq_entry  # Store the Gtk.Entry widget for CPU frequency

        self._create_widgets()

    def _create_widgets(self):
        # --- Common Settings ---
        common_frame = Gtk.Frame(label="Fælles Indstillinger")
        self.append(common_frame)
        common_frame.set_margin_bottom(10)

        common_grid = Gtk.Grid()
        common_grid.set_row_spacing(5)
        common_grid.set_column_spacing(5)
        common_grid.set_margin_start(5)
        common_grid.set_margin_end(5)
        common_grid.set_margin_top(5)
        common_grid.set_margin_bottom(5)
        common_frame.set_child(common_grid)

        # --- Timer Selection ---
        timer_selection_frame = Gtk.Frame(label="Vælg Timer")
        self.append(timer_selection_frame)
        timer_selection_frame.set_margin_bottom(10)

        timer_selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        timer_selection_box.set_margin_start(5)
        timer_selection_box.set_margin_end(5)
        timer_selection_box.set_margin_top(5)
        timer_selection_box.set_margin_bottom(5)
        timer_selection_frame.set_child(timer_selection_box)

        self.timer_radio_group = None  # To manage radio button group
        
        # Timer0 Radio Button
        self.timer0_radio = Gtk.CheckButton(label="Timer0")
        self.timer0_radio.set_group(self.timer_radio_group)
        self.timer_radio_group = self.timer0_radio
        self.timer0_radio.set_active(True)  # Set as default selected
        self.timer0_radio.connect("toggled", self._on_timer_selected, "Timer0")
        timer_selection_box.append(self.timer0_radio)

        # Timer1 Radio Button
        self.timer1_radio = Gtk.CheckButton(label="Timer1")
        self.timer1_radio.set_group(self.timer_radio_group)
        self.timer1_radio.connect("toggled", self._on_timer_selected, "Timer1")
        timer_selection_box.append(self.timer1_radio)

        # Timer2 Radio Button
        self.timer2_radio = Gtk.CheckButton(label="Timer2")
        self.timer2_radio.set_group(self.timer_radio_group)
        self.timer2_radio.connect("toggled", self._on_timer_selected, "Timer2")
        timer_selection_box.append(self.timer2_radio)

        # --- Timer-Specific Settings Frames (will be children of a Gtk.Stack) ---
        self.timer_stack = Gtk.Stack()
        self.append(self.timer_stack)
        self.timer_stack.set_hexpand(True)
        self.timer_stack.set_vexpand(True)

        self._setup_timer0_widgets()
        self._setup_timer1_widgets()
        self._setup_timer2_widgets()

        # Set initial visible child
        self.timer_stack.set_visible_child_name("Timer0")

        # --- Calculate Button ---
        calculate_button = Gtk.Button(label="Beregn Frekvens")
        calculate_button.connect("clicked", self.calculate_frequency_from_registers)
        self.append(calculate_button)
        calculate_button.set_margin_top(10)
        calculate_button.set_margin_bottom(10)

        # --- Results Display ---
        results_frame = Gtk.Frame(label="Beregnet Resultat")
        self.append(results_frame)
        results_frame.set_hexpand(True)

        results_grid = Gtk.Grid()
        results_grid.set_row_spacing(5)
        results_grid.set_column_spacing(5)
        results_grid.set_margin_start(5)
        results_grid.set_margin_end(5)
        results_grid.set_margin_top(5)
        results_grid.set_margin_bottom(5)
        results_frame.set_child(results_grid)

        results_grid.attach(Gtk.Label(label="Beregnet Frekvens:", xalign=0), 0, 0, 1, 1)
        self.calculated_freq_label = Gtk.Label(label="N/A", xalign=0)
        self.calculated_freq_label.set_markup("<span weight='bold'>N/A</span>")  # Bold text
        results_grid.attach(self.calculated_freq_label, 1, 0, 1, 1)
        
        results_grid.attach(Gtk.Label(label="Timer Mode:", xalign=0), 0, 1, 1, 1)
        self.calculated_mode_label = Gtk.Label(label="N/A", xalign=0)
        results_grid.attach(self.calculated_mode_label, 1, 1, 1, 1)

        results_grid.attach(Gtk.Label(label="Prescaler:", xalign=0), 0, 2, 1, 1)
        self.calculated_prescaler_label = Gtk.Label(label="N/A", xalign=0)
        results_grid.attach(self.calculated_prescaler_label, 1, 2, 1, 1)

    def _setup_timer0_widgets(self):
        timer0_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        timer0_content_box.set_margin_start(10)
        timer0_content_box.set_margin_end(10)
        timer0_content_box.set_margin_top(10)
        timer0_content_box.set_margin_bottom(10)

        frame = Gtk.Frame(label="Timer0 Register Indstillinger")
        frame.set_child(timer0_content_box)
        self.timer_stack.add_named(frame, "Timer0")  # Add to stack with a name

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        timer0_content_box.append(grid)
        
        grid.attach(Gtk.Label(label="TCCR0A (bin/hex/dec):", xalign=0), 0, 0, 1, 1)
        self.tccr0a_entry = Gtk.Entry()
        grid.attach(self.tccr0a_entry, 1, 0, 1, 1)
        self.tccr0a_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="TCCR0B (bin/hex/dec):", xalign=0), 0, 1, 1, 1)
        self.tccr0b_entry = Gtk.Entry()
        grid.attach(self.tccr0b_entry, 1, 1, 1, 1)
        self.tccr0b_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="OCR0A (dec):", xalign=0), 0, 2, 1, 1)
        self.ocr0a_entry = Gtk.Entry()
        grid.attach(self.ocr0a_entry, 1, 2, 1, 1)
        self.ocr0a_entry.set_hexpand(True)

    def _setup_timer1_widgets(self):
        timer1_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        timer1_content_box.set_margin_start(10)
        timer1_content_box.set_margin_end(10)
        timer1_content_box.set_margin_top(10)
        timer1_content_box.set_margin_bottom(10)
        
        frame = Gtk.Frame(label="Timer1 Register Indstillinger")
        frame.set_child(timer1_content_box)
        self.timer_stack.add_named(frame, "Timer1")

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        timer1_content_box.append(grid)

        grid.attach(Gtk.Label(label="TCCR1A (bin/hex/dec):", xalign=0), 0, 0, 1, 1)
        self.tccr1a_entry = Gtk.Entry()
        grid.attach(self.tccr1a_entry, 1, 0, 1, 1)
        self.tccr1a_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="TCCR1B (bin/hex/dec):", xalign=0), 0, 1, 1, 1)
        self.tccr1b_entry = Gtk.Entry()
        grid.attach(self.tccr1b_entry, 1, 1, 1, 1)
        self.tccr1b_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="ICR1 (dec):", xalign=0), 0, 2, 1, 1)
        self.icr1_entry = Gtk.Entry()
        grid.attach(self.icr1_entry, 1, 2, 1, 1)
        self.icr1_entry.set_hexpand(True)
        
        grid.attach(Gtk.Label(label="OCR1A (dec):", xalign=0), 0, 3, 1, 1)
        self.ocr1a_entry = Gtk.Entry()
        grid.attach(self.ocr1a_entry, 1, 3, 1, 1)
        self.ocr1a_entry.set_hexpand(True)

    def _setup_timer2_widgets(self):
        timer2_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        timer2_content_box.set_margin_start(10)
        timer2_content_box.set_margin_end(10)
        timer2_content_box.set_margin_top(10)
        timer2_content_box.set_margin_bottom(10)
        
        frame = Gtk.Frame(label="Timer2 Register Indstillinger")
        frame.set_child(timer2_content_box)
        self.timer_stack.add_named(frame, "Timer2")

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        timer2_content_box.append(grid)

        grid.attach(Gtk.Label(label="TCCR2A (bin/hex/dec):", xalign=0), 0, 0, 1, 1)
        self.tccr2a_entry = Gtk.Entry()
        grid.attach(self.tccr2a_entry, 1, 0, 1, 1)
        self.tccr2a_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="TCCR2B (bin/hex/dec):", xalign=0), 0, 1, 1, 1)
        self.tccr2b_entry = Gtk.Entry()
        grid.attach(self.tccr2b_entry, 1, 1, 1, 1)
        self.tccr2b_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="OCR2A (dec):", xalign=0), 0, 2, 1, 1)
        self.ocr2a_entry = Gtk.Entry()
        grid.attach(self.ocr2a_entry, 1, 2, 1, 1)
        self.ocr2a_entry.set_hexpand(True)

    def _on_timer_selected(self, button, timer_name):
        # Only change visible child if the button is active (selected)
        if button.get_active():
            self.timer_stack.set_visible_child_name(timer_name)
            self._clear_results()  # Clear results when changing timer selection

    def calculate_frequency_from_registers(self, button):
        try:
            # Get CPU Frequency from the Gtk.Entry widget
            cpu_freq_mhz_text = self.cpu_freq_entry.get_text()
            if not cpu_freq_mhz_text:
                show_warning("Input Mangel", "Indtast venligst en CPU frekvens.")
                return
            cpu_freq_mhz = float(cpu_freq_mhz_text)
            cpu_freq_hz = cpu_freq_mhz * 1_000_000

            # Determine selected timer from the active radio button
            selected_timer = ""
            if self.timer0_radio.get_active():
                selected_timer = "Timer0"
            elif self.timer1_radio.get_active():
                selected_timer = "Timer1"
            elif self.timer2_radio.get_active():
                selected_timer = "Timer2"
            
            if not selected_timer:
                show_error("Fejl", "Vælg venligst en timer.")
                self._clear_results()
                return

            self._clear_results()  # Clear previous results

            # --- Logic for Timer0 ---
            if selected_timer == "Timer0":
                tccr0a_val = parse_hex_bin_int(self.tccr0a_entry.get_text())
                tccr0b_val = parse_hex_bin_int(self.tccr0b_entry.get_text())
                ocr0a_val = parse_hex_bin_int(self.ocr0a_entry.get_text())

                # Extract WGM bits (WGM02 from TCCR0B, WGM01/WGM00 from TCCR0A)
                wgm02 = (tccr0b_val >> 3) & 0x01
                wgm01 = (tccr0a_val >> 1) & 0x01
                wgm00 = tccr0a_val & 0x01

                # Extract CS bits (CS02, CS01, CS00 from TCCR0B)
                cs_bits = tccr0b_val & 0x07

                # Find the matching WGM mode
                current_mode_name = "Ukendt Tilstand"
                top_value = 0  # Default TOP
                for mode_name, bits in WGM_BITS_T0.items():
                    if (bits["WGM02"] == wgm02 and
                        bits["WGM01"] == wgm01 and
                        bits["WGM00"] == wgm00):
                        current_mode_name = mode_name
                        if mode_name == "CTC":
                            top_value = ocr0a_val  # TOP is OCR0A for Timer0 CTC
                        elif mode_name == "Normal" or "PWM" in mode_name:
                            top_value = 0xFF  # Fixed TOP for 8-bit modes
                        break
                
                if current_mode_name == "Ukendt Tilstand":
                    show_warning("Ukendt WGM", "Kombinationen af WGM-bits svarer ikke til en kendt tilstand for Timer0. Antager Normal Mode (TOP=0xFF).")
                    top_value = 0xFF  # Default to Normal mode TOP for safety

                # Find the prescaler value
                prescaler_val = 0
                for p_str, p_bits in PRESCALERS_T0_T1_T2["T0_T1"].items():
                    if p_bits == cs_bits:
                        prescaler_val = int(p_str)
                        break
                
                if prescaler_val == 0:
                    show_warning("Fejl", "Ugyldig prescaler indstilling for Timer0. Timeren er muligvis stoppet.")
                    self._display_results("N/A", "N/A", "N/A")
                    return

                # Calculate Frequency
                actual_freq = 0
                if current_mode_name == "Normal":
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif current_mode_name == "CTC":
                    actual_freq = cpu_freq_hz / (2 * prescaler_val * (top_value + 1))
                elif "Fast PWM" in current_mode_name:
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif "Phase Correct PWM" in current_mode_name:
                    actual_freq = cpu_freq_hz / (2 * prescaler_val * top_value) if top_value > 0 else 0
                else:
                    show_warning("Advarsel", "Ukendt tilstand for frekvensberegning. Resultatet kan være unøjagtigt.")
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))  # Fallback

                self._display_results(f"{actual_freq:.2f} Hz", current_mode_name, prescaler_val)

            # --- Logic for Timer1 ---
            elif selected_timer == "Timer1":
                tccr1a_val = parse_hex_bin_int(self.tccr1a_entry.get_text())
                tccr1b_val = parse_hex_bin_int(self.tccr1b_entry.get_text())
                icr1_val = parse_hex_bin_int(self.icr1_entry.get_text())
                ocr1a_val = parse_hex_bin_int(self.ocr1a_entry.get_text())

                # Extract WGM bits (WGM13, WGM12 from TCCR1B; WGM11, WGM10 from TCCR1A)
                wgm13 = (tccr1b_val >> 4) & 0x01
                wgm12 = (tccr1b_val >> 3) & 0x01
                wgm11 = (tccr1a_val >> 1) & 0x01
                wgm10 = tccr1a_val & 0x01

                # Extract CS bits (CS12, CS11, CS10 from TCCR1B)
                cs_bits = tccr1b_val & 0x07

                # Find the matching W WGM mode and determine TOP value
                current_mode_name = "Ukendt Tilstand"
                top_value = 0
                max_16bit_val = 0xFFFF  # Max value for 16-bit timer
                
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
                            top_value = max_16bit_val  # 16-bit max for Normal mode
                        break
                
                if current_mode_name == "Ukendt Tilstand":
                    show_warning("Ukendt WGM", "Kombinationen af WGM-bits svarer ikke til en kendt tilstand for Timer1. Antager Normal Mode (TOP=0xFFFF).")
                    top_value = max_16bit_val  # Default to Normal mode TOP

                # Find the prescaler value
                prescaler_val = 0
                for p_str, p_bits in PRESCALERS_T0_T1_T2["T0_T1"].items():
                    if p_bits == cs_bits:
                        prescaler_val = int(p_str)
                        break
                
                if prescaler_val == 0:
                    show_warning("Fejl", "Ugyldig prescaler indstilling for Timer1. Timeren er muligvis stoppet.")
                    self._display_results("N/A", "N/A", "N/A")
                    return

                # Calculate Frequency based on identified mode
                actual_freq = 0
                if "PWM" in current_mode_name:
                    if "Phase Correct" in current_mode_name:
                        actual_freq = cpu_freq_hz / (2 * prescaler_val * top_value) if top_value > 0 else 0
                    elif "Fast PWM" in current_mode_name:
                        actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif "CTC" in current_mode_name:
                    actual_freq = cpu_freq_hz / (2 * prescaler_val * (top_value + 1))
                elif current_mode_name == "Normal":
                    actual_freq = cpu_freq_hz / (prescaler_val * (max_16bit_val + 1))
                else:
                    show_warning("Advarsel", "Ukendt tilstand for frekvensberegning. Resultatet kan være unøjagtigt.")
                    actual_freq = cpu_freq_hz / (prescaler_val * (max_16bit_val + 1))  # Fallback

                self._display_results(f"{actual_freq:.2f} Hz", current_mode_name, prescaler_val)

            # --- Logic for Timer2 ---
            elif selected_timer == "Timer2":
                tccr2a_val = parse_hex_bin_int(self.tccr2a_entry.get_text())
                tccr2b_val = parse_hex_bin_int(self.tccr2b_entry.get_text())
                ocr2a_val = parse_hex_bin_int(self.ocr2a_entry.get_text())

                # Extract WGM bits (WGM22 from TCCR2B, WGM21/WGM20 from TCCR2A)
                wgm22 = (tccr2b_val >> 6) & 0x01  # WGM22 is bit 6 in TCCR2B
                wgm21 = (tccr2a_val >> 1) & 0x01
                wgm20 = tccr2a_val & 0x01

                # Extract CS bits (CS22, CS21, CS20 from TCCR2B)
                cs_bits = tccr2b_val & 0x07

                # Find the matching WGM mode
                current_mode_name = "Ukendt Tilstand"
                top_value = 0  # Default TOP
                for mode_name, bits in WGM_BITS_T2.items():
                    if (bits["WGM22"] == wgm22 and
                        bits["WGM21"] == wgm21 and
                        bits["WGM20"] == wgm20):
                        current_mode_name = mode_name
                        if mode_name == "CTC":
                            top_value = ocr2a_val
                        elif mode_name == "Normal" or "PWM" in mode_name:
                            top_value = 0xFF  # Fixed TOP for 8-bit modes
                        break
                
                if current_mode_name == "Ukendt Tilstand":
                    show_warning("Ukendt WGM", "Kombinationen af WGM-bits svarer ikke til en kendt tilstand for Timer2. Antager Normal Mode (TOP=0xFF).")
                    top_value = 0xFF  # Default to Normal mode TOP

                # Find the prescaler value (using T2 specific prescalers)
                prescaler_val = 0
                for p_str, p_bits in PRESCALERS_T0_T1_T2["T2"].items():
                    if p_bits == cs_bits:
                        prescaler_val = int(p_str)
                        break

                if prescaler_val == 0:
                    show_warning("Fejl", "Ugyldig prescaler indstilling for Timer2. Timeren er muligvis stoppet.")
                    self._display_results("N/A", "N/A", "N/A")
                    return

                # Calculate Frequency
                actual_freq = 0
                if current_mode_name == "Normal":
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif current_mode_name == "CTC":
                    actual_freq = cpu_freq_hz / (2 * prescaler_val * (top_value + 1))
                elif "Fast PWM" in current_mode_name:
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))
                elif "Phase Correct PWM" in current_mode_name:
                    actual_freq = cpu_freq_hz / (2 * prescaler_val * top_value) if top_value > 0 else 0
                else:
                    show_warning("Advarsel", "Ukendt tilstand for frekvensberegning. Resultatet kan være unøjagtigt.")
                    actual_freq = cpu_freq_hz / (prescaler_val * (top_value + 1))  # Fallback

                self._display_results(f"{actual_freq:.2f} Hz", current_mode_name, prescaler_val)

        except ValueError as ve:
            show_error("Input Fejl", f"Ugyldigt input: {ve}. Sørg for, at alle felter indeholder gyldige tal eller binære/hex værdier.")
            self._clear_results()
        except KeyError as ke:
            show_error("Konfigurationsfejl", f"Ukendt konfiguration: {ke}. Kontroller WGM-bits eller prescaler-indstillinger i constants.py.")
            self._clear_results()
        except Exception as e:
            show_error("Fejl", f"En uventet fejl opstod: {e}")
            self._clear_results()

    def _display_results(self, freq, mode, prescaler):
        self.calculated_freq_label.set_markup(f"<span weight='bold'>{freq}</span>")
        self.calculated_mode_label.set_label(mode)
        self.calculated_prescaler_label.set_label(str(prescaler))

    def _clear_results(self):
        self.calculated_freq_label.set_markup("<span weight='bold'>N/A</span>")
        self.calculated_mode_label.set_label("N/A")
        self.calculated_prescaler_label.set_label("N/A")