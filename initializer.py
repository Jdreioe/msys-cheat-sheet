import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

# Ensure these are adapted for GTK4 or are simple Python constants/functions
from utils import parse_hex_bin_int, show_error, show_warning # show_error/warning need GTK4 adaptation
from constants import WGM_BITS_T0, WGM_BITS_T1, WGM_BITS_T2, PRESCALERS_T0_T1_T2, COM_BITS_T0, COM_BITS_T1, COM_BITS_T2

class InitializerTab(Gtk.Box):

    """
    GTK4 panel to initialize ATmega2560 timer registers based on user selection.
    Generates C-like initialization code for Timer0, Timer1, and Timer2.
    """
    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)

        self.cpu_freq_entry = cpu_freq_entry # Reference to the shared CPU frequency entry
        self.current_timer = None # Stores the currently selected timer (e.g., "Timer0", "Timer1", "Timer2")

        self._create_widgets()

    def _create_widgets(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.append(grid)

        # --- Timer Selection ---
        grid.attach(Gtk.Label(label="Vælg hvilken Timer det er:"), 0, 0, 1, 1)
        self.timer_select_combobox = Gtk.ComboBoxText()
        self.timer_select_combobox.append_text("Timer0 (8-bit)")
        self.timer_select_combobox.append_text("Timer1 (16-bit)")
        self.timer_select_combobox.append_text("Timer2 (8-bit)")
        # Set default selection and connect signal
        self.timer_select_combobox.set_active_id("Timer0 (8-bit)")
        self.timer_select_combobox.connect("changed", self._on_timer_selected)
        grid.attach(self.timer_select_combobox, 1, 0, 1, 1)
        self.timer_select_combobox.set_hexpand(True)

        # --- Mode Selection (WGM) ---
        grid.attach(Gtk.Label(label="Timer Mode (WGM):"), 0, 1, 1, 1)
        self.mode_combobox = Gtk.ComboBoxText()
        self.mode_combobox.connect("changed", self._on_mode_change)
        grid.attach(self.mode_combobox, 1, 1, 1, 1)
        self.mode_combobox.set_hexpand(True)

        # --- Prescaler Selection (CS) ---
        grid.attach(Gtk.Label(label="Prescaler (CS):"), 0, 2, 1, 1)
        self.prescaler_combobox = Gtk.ComboBoxText()
        grid.attach(self.prescaler_combobox, 1, 2, 1, 1)
        self.prescaler_combobox.set_hexpand(True)

        # --- Output Compare Mode (COM) - OCxA ---
        grid.attach(Gtk.Label(label="Output Compare Mode (OCxA):"), 0, 3, 1, 1)
        self.com_a_combobox = Gtk.ComboBoxText()
        self.com_a_combobox.connect("changed", self._on_com_change)
        grid.attach(self.com_a_combobox, 1, 3, 1, 1)
        self.com_a_combobox.set_hexpand(True)

        # --- Output Compare Mode (COM) - OCxB ---
        grid.attach(Gtk.Label(label="Output Compare Mode (OCxB):"), 0, 4, 1, 1)
        self.com_b_combobox = Gtk.ComboBoxText()
        self.com_b_combobox.connect("changed", self._on_com_change)
        grid.attach(self.com_b_combobox, 1, 4, 1, 1)
        self.com_b_combobox.set_hexpand(True)

        # --- Output Compare Mode (COM) - OCxC (Timer1 only) ---
        grid.attach(Gtk.Label(label="Output Compare Mode (OCxC):"), 0, 5, 1, 1)
        self.com_c_combobox = Gtk.ComboBoxText()
        self.com_c_combobox.connect("changed", self._on_com_change)
        grid.attach(self.com_c_combobox, 1, 5, 1, 1)
        self.com_c_combobox.set_hexpand(True)

        # --- OCRx Inputs ---
        grid.attach(Gtk.Label(label="OCRxA (dec):"), 0, 6, 1, 1)
        self.ocra_entry = Gtk.Entry()
        self.ocra_entry.set_text("0")
        self.ocra_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.ocra_entry.connect("changed", lambda x: self.generate_init_code(None))
        grid.attach(self.ocra_entry, 1, 6, 1, 1)
        self.ocra_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="OCRxB (dec):"), 0, 7, 1, 1)
        self.ocrb_entry = Gtk.Entry()
        self.ocrb_entry.set_text("0")
        self.ocrb_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.ocrb_entry.connect("changed", lambda x: self.generate_init_code(None))
        grid.attach(self.ocrb_entry, 1, 7, 1, 1)
        self.ocrb_entry.set_hexpand(True)

        grid.attach(Gtk.Label(label="OCRxC (dec):"), 0, 8, 1, 1)
        self.ocrc_entry = Gtk.Entry()
        self.ocrc_entry.set_text("0")
        self.ocrc_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.ocrc_entry.connect("changed", lambda x: self.generate_init_code(None))
        grid.attach(self.ocrc_entry, 1, 8, 1, 1)
        self.ocrc_entry.set_hexpand(True)

        # --- ICR1 Input (Timer1 only) ---
        grid.attach(Gtk.Label(label="ICR1(dec):"), 0, 9, 1, 1)
        self.icr_entry = Gtk.Entry()
        self.icr_entry.set_text("0")
        self.icr_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.icr_entry.connect("changed", lambda x: self.generate_init_code(None))
        grid.attach(self.icr_entry, 1, 9, 1, 1)
        self.icr_entry.set_hexpand(True)
        self.icr_entry.set_sensitive(False) # Default to disabled

        # --- General Overflow Frequency Input ---
        grid.attach(Gtk.Label(label="Desired Overflow Freq (Hz):"), 0, 10, 1, 1)
        self.overflow_freq_entry = Gtk.Entry()
        self.overflow_freq_entry.set_text("0") # Default to 0, indicating not in use
        self.overflow_freq_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.overflow_freq_entry.connect("changed", self._on_overflow_freq_changed)
        grid.attach(self.overflow_freq_entry, 1, 10, 1, 1)
        self.overflow_freq_entry.set_hexpand(True)
        self.overflow_freq_entry.set_sensitive(True) # Always enabled, but only applies to Normal mode

        # --- Generate Button (also triggered by combobox changes) ---
        generate_button = Gtk.Button(label="Generer C Initialiseringskode")
        generate_button.connect("clicked", self.generate_init_code)
        grid.attach(generate_button, 0, 11, 2, 1)
        generate_button.set_margin_top(10)
        generate_button.set_margin_bottom(10)

        # --- Output Code Display ---
        output_frame = Gtk.Frame(label="Genereret C Initialiseringskode")
        self.append(output_frame)
        output_frame.set_hexpand(True)
        output_frame.set_vexpand(True)

        self.output_buffer = Gtk.TextBuffer()
        self.output_view = Gtk.TextView(buffer=self.output_buffer)
        self.output_view.set_editable(False)
        self.output_view.set_cursor_visible(False)
        self.output_view.set_monospace(True) # Important for code readability

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.output_view)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        output_frame.set_child(scrolled_window)

        # Initial call to populate options for default timer
        self._on_timer_selected(self.timer_select_combobox)
        # Initial calculation for the specific Timer0 request (now generalized)
        self._on_overflow_freq_changed(self.overflow_freq_entry)

    def _clear_combobox(self, combobox):
        """Helper to robustly clear a Gtk.ComboBoxText by manipulating its model."""
        model = combobox.get_model()
        if model is not None:
            # Clear all rows from the ListStore
            model.clear()
            # After clearing, explicitly set active to -1 or None
            # to ensure no lingering selection, though clear() usually handles this.
            combobox.set_active(-1) # -1 means no item selected

    def _populate_combobox(self, combobox, values_dict):
        """Helper to populate a Gtk.ComboBoxText."""
        self._clear_combobox(combobox) # Ensure this is always the first step
        for key in values_dict.keys():
            combobox.append_text(key)
        if values_dict:
            combobox.set_active(0) # Set first item as active if there are any

    def _get_selected_timer(self):
        """Helper to get the selected timer name (e.g., 'Timer0', 'Timer1')."""
        selected_timer_str = self.timer_select_combobox.get_active_text()
        if selected_timer_str:
            return selected_timer_str.split(" ")[0] # e.g., "Timer0" from "Timer0 (8-bit)"
        return None

    def _on_timer_selected(self, combobox):
        selected_timer = self._get_selected_timer()
        if not selected_timer:
            self.output_buffer.set_text("// Select a timer.")
            return

        self.current_timer = selected_timer.lower() # Store as "timer0", "timer1", etc.

        # --- Update WGM Modes based on the selected timer ---
        modes_dict = {}
        if selected_timer == "Timer0":
            modes_dict = WGM_BITS_T0
            prescaler_key = "T0_T1"
        elif selected_timer == "Timer1":
            modes_dict = WGM_BITS_T1
            prescaler_key = "T0_T1"
        elif selected_timer == "Timer2":
            modes_dict = WGM_BITS_T2
            prescaler_key = "T2"
        
        self._populate_combobox(self.mode_combobox, modes_dict)
        self._populate_combobox(self.prescaler_combobox, PRESCALERS_T0_T1_T2[prescaler_key])

        # --- Update COM Modes and OCR/ICR sensitivity ---
        com_options_map = {
            "timer0": COM_BITS_T0,
            "timer1": COM_BITS_T1,
            "timer2": COM_BITS_T2
        }
        current_com_options = com_options_map.get(self.current_timer, {})

        self._populate_combobox(self.com_a_combobox, current_com_options)
        self._populate_combobox(self.com_b_combobox, current_com_options)
        
        # OCxC and ICR are only for Timer1
        if self.current_timer == "timer1":
            self.com_c_combobox.set_sensitive(True)
            self._populate_combobox(self.com_c_combobox, COM_BITS_T1)
        else:
            self.com_c_combobox.set_sensitive(False)
            self._clear_combobox(self.com_c_combobox) # Clear options if not Timer1
        
        # Trigger mode change to update OCR/ICR visibility/sensitivity correctly
        self._on_mode_change(self.mode_combobox) 
        self.generate_init_code(None) # Regenerate code on timer change

    def _on_mode_change(self, combobox):
        selected_mode = combobox.get_active_text()
        if not selected_mode or not self.current_timer:
            self.output_buffer.set_text("// Select a mode.")
            return

        wgm_data = {}
        if self.current_timer == "timer1":
            wgm_data = WGM_BITS_T1.get(selected_mode, {})
        elif self.current_timer == "timer0": # Use specific WGM_BITS for Timer0
            wgm_data = WGM_BITS_T0.get(selected_mode, {})
        elif self.current_timer == "timer2": # Use specific WGM_BITS for Timer2
            wgm_data = WGM_BITS_T2.get(selected_mode, {})


        # Determine if OCR/ICR are used as TOP or for general output compare
        is_ctc_mode = "CTC" in selected_mode
        is_pwm_mode = "PWM" in selected_mode
        uses_icr_as_top = wgm_data.get("TOP_value_reg") == "ICR1" and self.current_timer == "timer1"
        uses_ocra_as_top = wgm_data.get("TOP_value_reg", "").endswith("A") # OCRxA for any timer A

        # OCRA, OCRB, OCRC entries (generally active for CTC/PWM)
        ocra_active = is_ctc_mode or is_pwm_mode or uses_ocra_as_top
        ocrb_active = is_ctc_mode or is_pwm_mode # OCRB usually only for output compare
        ocrc_active = self.current_timer == "timer1" and (is_ctc_mode or is_pwm_mode)

        self.ocra_entry.set_sensitive(ocra_active)
        self.ocrb_entry.set_sensitive(ocrb_active)
        self.ocrc_entry.set_sensitive(ocrc_active)

        # ICR entry is only active for Timer1 when used as TOP
        self.icr_entry.set_sensitive(uses_icr_as_top)
        
        # COM boxes are generally always relevant for output control
        self.com_a_combobox.set_sensitive(True)
        self.com_b_combobox.set_sensitive(True)
        # COM C is only for Timer1
        self.com_c_combobox.set_sensitive(self.current_timer == "timer1") 

        self.generate_init_code(None) # Regenerate code on mode change

    def _on_com_change(self, combobox):
        """Called when a COM combobox value changes."""
        self.generate_init_code(None) # Regenerate code

    def _calculate_prescaler_for_overflow(self, cpu_freq, desired_overflow_freq, timer_bit_width, prescaler_options):
        """
        Calculates the ideal and closest standard prescaler for a given overflow frequency.
        Returns (ideal_prescaler, best_prescaler_value, best_prescaler_name).
        """
        if desired_overflow_freq <= 0 or cpu_freq <= 0:
            return 0, None, None

        max_counts = 2**timer_bit_width # 256 for 8-bit, 65536 for 16-bit
        
        # Formula: f_overflow = f_CPU / (Prescaler * max_counts)
        # Therefore: Prescaler = f_CPU / (f_overflow * max_counts)
        ideal_prescaler_float = cpu_freq / (desired_overflow_freq * max_counts)

        best_prescaler_value = None
        best_prescaler_name = None
        min_diff = float('inf')

        for name, value in prescaler_options.items():
            if value == 0: # Skip 'No Clock Source' or 'Stopped'
                continue
            
            diff = abs(ideal_prescaler_float - value)
            if diff < min_diff:
                min_diff = diff
                best_prescaler_value = value
                best_prescaler_name = name
            elif diff == min_diff and value < best_prescaler_value: # Prefer smaller prescaler if difference is same
                 best_prescaler_value = value
                 best_prescaler_name = name

        return ideal_prescaler_float, best_prescaler_value, best_prescaler_name

    def _on_overflow_freq_changed(self, entry):
        """
        Handles changes in the Desired Overflow Frequency entry.
        Calculates and suggests the prescaler if in Normal Mode.
        """
        selected_timer = self._get_selected_timer()
        selected_mode_name = self.mode_combobox.get_active_text()
        
        if not selected_timer or selected_mode_name != "Normal":
            # Only apply this logic in Normal Mode
            self.generate_init_code(None) # Just regenerate if something else changes
            return

        try:
            cpu_freq_str = self.cpu_freq_entry.get_text().strip()
            overflow_freq_str = entry.get_text().strip()

            if not cpu_freq_str or not overflow_freq_str:
                self.generate_init_code(None) # Regenerate, but don't try calculation if empty
                return

            cpu_freq = int(cpu_freq_str)
            desired_overflow_freq = float(overflow_freq_str)

            if cpu_freq <= 0 or desired_overflow_freq <= 0:
                self.generate_init_code(None) # Regenerate, but don't try calculation if <= 0
                return

            timer_num = selected_timer[-1] # '0', '1', '2'
            timer_bit_width = 16 if timer_num == '1' else 8
            prescaler_key = "T0_T1" if timer_num in ['0', '1'] else "T2"
            prescaler_options = PRESCALERS_T0_T1_T2[prescaler_key]

            ideal_prescaler, best_prescaler_value, best_prescaler_name = \
                self._calculate_prescaler_for_overflow(cpu_freq, desired_overflow_freq, timer_bit_width, prescaler_options)

            if best_prescaler_name:
                self.prescaler_combobox.set_active_id(best_prescaler_name)
            else:
                show_warning("Calculation Warning", "Could not find a suitable prescaler for the desired overflow frequency.")

            self.generate_init_code(None) # Regenerate code
        except ValueError as e:
            # show_warning("Input Error", f"Invalid frequency or CPU value: {e}")
            pass # Suppress constant warnings during typing
        except Exception as e:
            show_error("Error", f"An error occurred during prescaler calculation: {e}")

    def generate_init_code(self, button):
        """Generates the C-like initialization code for the selected timer."""
        output_lines = []
        try:
            # Use current_timer property, which is set by _on_timer_selected
            timer_num = self.current_timer[-1] # '0', '1', '2'
            is_16_bit = (timer_num == '1')
            
            selected_mode_name = self.mode_combobox.get_active_text()
            selected_prescaler_name = self.prescaler_combobox.get_active_text()
            selected_com_a_name = self.com_a_combobox.get_active_text()
            selected_com_b_name = self.com_b_combobox.get_active_text()
            selected_com_c_name = self.com_c_combobox.get_active_text() if is_16_bit else None

            # Basic validation for essential selections
            if not all([selected_mode_name, selected_prescaler_name, selected_com_a_name, selected_com_b_name]):
                self.output_buffer.set_text("// Please select all primary options (Timer, Mode, Prescaler, COM Modes) to generate code.")
                return
            if is_16_bit and not selected_com_c_name and self.com_c_combobox.get_sensitive():
                self.output_buffer.set_text("// Please select COM Mode for OCxC for Timer1.")
                return


            # Get WGM bits based on explicit timer WGM_BITS
            wgm_config = {}
            if self.current_timer == "timer1":
                wgm_config = WGM_BITS_T1.get(selected_mode_name, {})
            elif self.current_timer == "timer0":
                wgm_config = WGM_BITS_T0.get(selected_mode_name, {})
            elif self.current_timer == "timer2":
                wgm_config = WGM_BITS_T2.get(selected_mode_name, {})

            # Get Prescaler bits (Clock Select - CS)
            prescaler_key = "T0_T1" if timer_num in ['0', '1'] else "T2"
            prescaler_value = PRESCALERS_T0_T1_T2[prescaler_key].get(selected_prescaler_name, 0b000) # Default to stopped

            # Get COM bits (Output Compare Mode)
            com_options_map = {
                "timer0": COM_BITS_T0,
                "timer1": COM_BITS_T1,
                "timer2": COM_BITS_T2
            }
            current_com_options = com_options_map.get(self.current_timer, {})

            com_a_data = current_com_options.get(selected_com_a_name, {})
            com_b_data = current_com_options.get(selected_com_b_name, {})
            com_c_data = current_com_options.get(selected_com_c_name, {}) if is_16_bit else {}


            # Initialize TCCRx registers
            tccrxa = 0
            tccrxb = 0
            tccrxc = 0 # Only for Timer1

            # Set WGM bits
            # WGM bits are scattered across TCCRxA and TCCRxB
            if is_16_bit: # Timer1 has WGM13, WGM12 in TCCR1B; WGM11, WGM10 in TCCR1A
                tccrxa |= (wgm_config.get("WGM11",0) << 1) | wgm_config.get("WGM10",0)
                tccrxb |= (wgm_config.get("WGM13",0) << 4) | (wgm_config.get("WGM12",0) << 3)
                tccrxb |= prescaler_value # Set prescaler bits in TCCR1B
            elif self.current_timer == "timer2": # Timer2 has WGM21, WGM20 in TCCRxA, WGM22 in TCCRxB
                wgm_x0_val = wgm_config.get("WGM20", 0) # Use WGM20, WGM21, WGM22 as per your dict
                wgm_x1_val = wgm_config.get("WGM21", 0)
                wgm_x2_val = wgm_config.get("WGM22", 0)
                tccrxa |= (wgm_x1_val << 1) | wgm_x0_val
                tccrxb |= (wgm_x2_val << 3)
                tccrxb |= prescaler_value
            else: # Timer0 has WGM01, WGM00 in TCCRxA, WGM02 in TCCRxB
                tccrxa |= (wgm_config.get("WGM01",0) << 1) | wgm_config.get("WGM00",0)
                tccrxb |= (wgm_config.get("WGM02",0) << 3)
                tccrxb |= prescaler_value

            # Set COM bits in TCCRxA (and TCCRxC if applicable, but TCCRxC is usually FOC)
            if timer_num == '0':
                tccrxa |= (com_a_data.get("COM0A1",0) << 7) | (com_a_data.get("COM0A0",0) << 6)
                tccrxa |= (com_b_data.get("COM0B1",0) << 5) | (com_b_data.get("COM0B0",0) << 4)
                
            elif timer_num == '1':
                tccrxa |= (com_a_data.get("COM1A1",0) << 7) | (com_a_data.get("COM1A0",0) << 6)
                tccrxa |= (com_b_data.get("COM1B1",0) << 5) | (com_b_data.get("COM1B0",0) << 4)
                # COM1C bits are specifically placed for Timer1
                tccrxa |= (com_c_data.get("COM1C1",0) << 3) | (com_c_data.get("COM1C0",0) << 2)
            elif timer_num == '2':
                tccrxa |= (com_a_data.get("COM2A1",0) << 7) | (com_a_data.get("COM2A0",0) << 6)
                tccrxa |= (com_b_data.get("COM2B1",0) << 5) | (com_b_data.get("COM2B0",0) << 4)

            # Get OCRx and ICRx values from entries
            ocra_val = parse_hex_bin_int(self.ocra_entry.get_text()) if self.ocra_entry.get_sensitive() else 0
            ocrb_val = parse_hex_bin_int(self.ocrb_entry.get_text()) if self.ocrb_entry.get_sensitive() else 0
            ocrc_val = parse_hex_bin_int(self.ocrc_entry.get_text()) if self.ocrc_entry.get_sensitive() else 0
            icr_val = parse_hex_bin_int(self.icr_entry.get_text()) if self.icr_entry.get_sensitive() else 0

            # Generate C code output
            output_lines.append(f"// --- Timer{timer_num} Initialization for ATmega2560 ---")
            output_lines.append(f"// Mode: {selected_mode_name}")
            output_lines.append(f"// Prescaler: {selected_prescaler_name}")
            output_lines.append(f"// Output Compare OC{timer_num}A: {selected_com_a_name}")
            output_lines.append(f"// Output Compare OC{timer_num}B: {selected_com_b_name}")
            if is_16_bit:
                output_lines.append(f"// Output Compare OC{timer_num}C: {selected_com_c_name}")
            output_lines.append("")

            # Add the calculation formula if in Normal mode and overflow frequency is specified
            try:
                cpu_freq = int(self.cpu_freq_entry.get_text())
                desired_overflow_freq = float(self.overflow_freq_entry.get_text())

                if selected_mode_name == "Normal" and desired_overflow_freq > 0:
                    timer_bit_width = 16 if timer_num == '1' else 8
                    max_counts = 2**timer_bit_width
                    output_lines.append(f"// Calculation for Timer{timer_num} Normal Mode Overflow:")
                    output_lines.append(f"// f_overflow = f_CPU / (Prescaler * {max_counts})")
                    output_lines.append(f"// Prescaler = f_CPU / (f_overflow * {max_counts})")
                    output_lines.append(f"// Prescaler = {cpu_freq} / ({desired_overflow_freq} * {max_counts}) = {cpu_freq / (desired_overflow_freq * max_counts):.2f}")
                    output_lines.append("")
            except ValueError:
                # Ignore if CPU freq or overflow freq are not valid numbers
                pass


            output_lines.append(f"// Stop Timer{timer_num} (clear CS bits) before configuration")
            output_lines.append(f"TCCR{timer_num}B &= ~((1 << CS{timer_num}2) | (1 << CS{timer_num}1) | (1 << CS{timer_num}0));")
            output_lines.append("")

            output_lines.append(f"TCCR{timer_num}A = 0b{tccrxa:08b}; // {hex(tccrxa)}")
            output_lines.append(f"TCCR{timer_num}B = 0b{tccrxb:08b}; // {hex(tccrxb)}")
            if is_16_bit:
                output_lines.append(f"TCCR{timer_num}C = 0b{tccrxc:08b}; // {hex(tccrxc)} (Often used for Force Output Compare, usually 0 initially)")
            
            if self.ocra_entry.get_sensitive():
                output_lines.append(f"OCR{timer_num}A = {ocra_val};")
            if self.ocrb_entry.get_sensitive():
                output_lines.append(f"OCR{timer_num}B = {ocrb_val};")
            if self.ocrc_entry.get_sensitive():
                output_lines.append(f"OCR{timer_num}C = {ocrc_val};")
            if self.icr_entry.get_sensitive() and is_16_bit: # ICR only for 16-bit timers
                output_lines.append(f"ICR{timer_num} = {icr_val};")
            
            # Always initialize TCNT to 0 for a clean start
            output_lines.append(f"TCNT{timer_num} = 0;")


            output_lines.append(f"\n// Optional: Enable Timer/Counter Interrupts (uncomment as needed)")
            output_lines.append(f"// TIMSK{timer_num} |= (1 << TOIE{timer_num});   // Timer Overflow Interrupt Enable")
            output_lines.append(f"// TIMSK{timer_num} |= (1 << OCIE{timer_num}A);  // Output Compare Match A Interrupt Enable")
            if timer_num != '0': # Timer0 doesn't have OCIE0B directly on Mega2560 TIMSK0
                output_lines.append(f"// TIMSK{timer_num} |= (1 << OCIE{timer_num}B);  // Output Compare Match B Interrupt Enable")
            if is_16_bit: # Timer1 has OCIE1C and ICIE1
                output_lines.append(f"// TIMSK{timer_num} |= (1 << OCIE{timer_num}C);  // Output Compare Match C Interrupt Enable")
                output_lines.append(f"// TIMSK{timer_num} |= (1 << ICIE{timer_num});   // Input Capture Interrupt Enable")
            
            output_lines.append("\n// Don't forget to enable global interrupts: sei();")
            output_lines.append("\n// Set appropriate DDR for OCx pins if using output compare functionality.")

            # General ISR example for overflow if in Normal mode and overflow freq > 0
            try:
                desired_overflow_freq = float(self.overflow_freq_entry.get_text())
                if selected_mode_name == "Normal" and desired_overflow_freq > 0:
                    output_lines.append(f"\n// ISR example for Timer{timer_num} Overflow at ~{desired_overflow_freq:.2f} Hz:")
                    output_lines.append(f"ISR(TIMER{timer_num}_OVF_vect) {{")
                    output_lines.append(f"    // Your code to be executed here")
                    output_lines.append(f"}}")
            except ValueError:
                pass
                
            self.output_buffer.set_text("\n".join(output_lines))

        except ValueError as e:
            show_error("Invalid Input", f"Please enter valid numerical values for OCR/ICR. Details: {e}")
            self.output_buffer.set_text("// Error: Invalid input values. See console for details.")
        except KeyError as e:
            show_error("Configuration Error", f"Missing configuration for selected option: {e}. Check WGM_BITS, PRESCALERS, COM_BITS definitions.")
            self.output_buffer.set_text("// Error: Configuration data missing. See console for details.")
        except Exception as e:
            show_error("Unexpected Error", f"An unexpected error occurred: {e}")
            self.output_buffer.set_text(f"// An unexpected error occurred: {e}. See console for details.")