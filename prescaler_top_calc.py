import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

# Import from your separate files
from constants import (
    CPU_FREQ_DEFAULT, PRESCALERS_T0_T1_T2,
    WGM_BITS_T0, WGM_BITS_T1, WGM_BITS_T2
)
from utils import parse_hex_bin_int, show_error, show_warning

class PrescalerTOPCalculator(Gtk.Box):
    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)

        self.cpu_freq_entry_var = cpu_freq_entry

        self.prescaler_desired_freq_buffer = Gtk.EntryBuffer()
        self.prescaler_desired_top_buffer = Gtk.EntryBuffer(text="0") # Default 0

        # These are used for the main mode dropdown, not the radio buttons for timer selection
        self.prescaler_timer_selection_store = Gtk.StringList.new(["Timer0", "Timer1", "Timer2"])
        self.prescaler_timer_selection_dropdown = Gtk.DropDown.new(self.prescaler_timer_selection_store, None)
        self.prescaler_timer_selection_dropdown.set_selected(0) # Default to Timer0
        # The dropdown is not used directly for timer selection in this tab's UI,
        # but the model is updated, so its `selected` property might still be triggered.
        # It's safer to connect the radio buttons to the update logic.
        # self.prescaler_timer_selection_dropdown.connect("notify::selected", self._update_prescaler_mode_options)

        self.prescaler_mode_selection_store = Gtk.StringList.new([])
        self.prescaler_mode_selection_dropdown = Gtk.DropDown.new(self.prescaler_mode_selection_store, None)
        self.prescaler_mode_selection_dropdown.set_property("width-request", 200)
        self.prescaler_mode_selection_dropdown.connect("notify::selected", self._update_formula_label_on_mode_change)


        self._create_widgets()
        self._update_prescaler_mode_options() # Initial population of mode dropdown
        self._update_formula_label() # Initial formula display

    def _create_widgets(self):
        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)
        self.append(grid)

        # Inputs
        grid.attach(Gtk.Label(label="Ønsket Frekvens (Hz):", xalign=0), 0, 0, 1, 1)
        self.prescaler_desired_freq_entry = Gtk.Entry(buffer=self.prescaler_desired_freq_buffer)
        grid.attach(self.prescaler_desired_freq_entry, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Timer Mode:", xalign=0), 0, 1, 1, 1)
        grid.attach(self.prescaler_mode_selection_dropdown, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Ønsket TOP værdi (hvis relevant):", xalign=0), 0, 2, 1, 1)
        self.prescaler_desired_top_entry = Gtk.Entry(buffer=self.prescaler_desired_top_buffer)
        grid.attach(self.prescaler_desired_top_entry, 1, 2, 1, 1)

        # Timer selection for this section (using RadioButtons within a Box)
        grid.attach(Gtk.Label(label="Vælg Timer:", xalign=0), 0, 3, 1, 1)
        timer_radio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        grid.attach(timer_radio_box, 1, 3, 3, 1)

        self.radio_timer0 = Gtk.CheckButton(label="Timer0")
        self.radio_timer0.set_group(None)
        self.radio_timer0.set_active(True)
        self.radio_timer0.connect("toggled", self._update_prescaler_mode_options)
        self.radio_timer0.connect("toggled", self._update_formula_label_on_timer_change) # Connect for formula update
        timer_radio_box.append(self.radio_timer0)

        self.radio_timer1 = Gtk.CheckButton(label="Timer1")
        self.radio_timer1.set_group(self.radio_timer0)
        self.radio_timer1.connect("toggled", self._update_prescaler_mode_options)
        self.radio_timer1.connect("toggled", self._update_formula_label_on_timer_change) # Connect for formula update
        timer_radio_box.append(self.radio_timer1)

        self.radio_timer2 = Gtk.CheckButton(label="Timer2")
        self.radio_timer2.set_group(self.radio_timer0)
        self.radio_timer2.connect("toggled", self._update_prescaler_mode_options)
        self.radio_timer2.connect("toggled", self._update_formula_label_on_timer_change) # Connect for formula update
        timer_radio_box.append(self.radio_timer2)
        
        # Formula Label (Dynamic)
        self.formula_label = Gtk.Label(label="<b>Formel: N/A</b>", xalign=0.5)
        self.formula_label.set_wrap(True)
        self.formula_label.set_justify(Gtk.Justification.CENTER)
        grid.attach(self.formula_label, 0, 4, 4, 1) # Position below radio buttons, spanning columns
        self.formula_label.set_margin_top(10)
        self.formula_label.set_margin_bottom(10)

        # Calculate Button (shifted down by 1 row due to formula label)
        calculate_button = Gtk.Button(label="Beregn Prescaler")
        calculate_button.connect("clicked", self.calculate_prescaler_and_top)
        grid.attach(calculate_button, 0, 5, 4, 1) # Shifted from row 4 to 5

        # Outputs (all shifted down by 1 row)
        self.calculated_prescaler_label = Gtk.Label(label="N/A", xalign=0)
        self.calculated_prescaler_label.set_markup("<span weight='bold'>N/A</span>")
        grid.attach(Gtk.Label(label="Optimal Prescaler:", xalign=0), 0, 6, 1, 1)
        grid.attach(self.calculated_prescaler_label, 1, 6, 3, 1)

        self.calculated_top_label = Gtk.Label(label="N/A", xalign=0)
        self.calculated_top_label.set_markup("<span weight='bold'>N/A</span>")
        grid.attach(Gtk.Label(label="Anbefalet TOP-værdi:", xalign=0), 0, 7, 1, 1)
        grid.attach(self.calculated_top_label, 1, 7, 3, 1)

        self.calculated_actual_freq_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(Gtk.Label(label="Faktisk Frekvens:", xalign=0), 0, 8, 1, 1)
        grid.attach(self.calculated_actual_freq_label, 1, 8, 3, 1)
        
        self.calculated_error_percent_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(Gtk.Label(label="Fejl (%):", xalign=0), 0, 9, 1, 1)
        grid.attach(self.calculated_error_percent_label, 1, 9, 3, 1)

    def _get_selected_timer(self):
        if self.radio_timer0.get_active():
            return "Timer0"
        elif self.radio_timer1.get_active():
            return "Timer1"
        elif self.radio_timer2.get_active():
            return "Timer2"
        return ""

    def _update_prescaler_mode_options(self, *_):
        selected_timer = self._get_selected_timer()
        modes = []
        if selected_timer == "Timer0":
            modes = list(WGM_BITS_T0.keys())
        elif selected_timer == "Timer1":
            modes = list(WGM_BITS_T1.keys())
        elif selected_timer == "Timer2":
            modes = list(WGM_BITS_T2.keys())
        
        # Create a new Gtk.StringList with the updated modes
        new_mode_store = Gtk.StringList.new(modes)
        # Set the new model to the dropdown
        self.prescaler_mode_selection_dropdown.set_model(new_mode_store)
        self.prescaler_mode_selection_store = new_mode_store # Update internal reference

        if modes:
            self.prescaler_mode_selection_dropdown.set_selected(0) # Set default to first mode
        # Removed the `else: self.prescaler_mode_selection_dropdown.set_selected(-1)` line
        # Setting an empty model automatically deselects.

    def _update_formula_label_on_timer_change(self, button):
        if button.get_active():
            selected_timer = self._get_selected_timer()
            # Defer to _update_formula_label, which will get the current mode from dropdown
            self._update_formula_label(selected_timer=selected_timer)

    def _update_formula_label_on_mode_change(self, dropdown, pspec):
        # This callback fires when the selected property of the dropdown changes
        selected_timer = self._get_selected_timer()
        self._update_formula_label(selected_timer=selected_timer)

    def _update_formula_label(self, selected_timer=None, current_mode_name=None, inferred_top_value=None):
        """Updates the formula label based on the selected timer and mode."""
        # Ensure selected_timer is always a string
        if selected_timer is None:
            selected_timer = self._get_selected_timer()
        selected_timer = str(selected_timer) # Defensive conversion

        # Ensure current_mode_name is always a string
        if current_mode_name is None:
            selected_index = self.prescaler_mode_selection_dropdown.get_selected()
            # Check if selected_index is valid before trying to get_string
            if selected_index != -1 and self.prescaler_mode_selection_store is not None and \
               selected_index < self.prescaler_mode_selection_store.get_n_items():
                current_mode_name = self.prescaler_mode_selection_store.get_string(selected_index)
            else:
                current_mode_name = "" # Default to empty string
        current_mode_name = str(current_mode_name) # Defensive conversion

        formula_text = "<b>Formel: N/A</b>"

        cpu_freq_str = "f_CPU" 
        prescaler_str = "Prescaler"
        desired_freq_str = "Ønsket Frekvens"
        desired_top_str = "Ønsket TOP" # Refers to the input TOP entry value

        if selected_timer == "Timer0":
            if current_mode_name == "Normal":
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / ({desired_freq_str} * (0xFF + 1))</b>"
            elif current_mode_name == "CTC":
                # For CTC, user provides desired_freq and desired_top (OCR0A)
                # We need to solve for Prescaler.
                top_val_in_formula = str(inferred_top_value) if inferred_top_value is not None and inferred_top_value != -1 else "OCR0A"
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / (2 * {desired_freq_str} * ({top_val_in_formula} + 1))</b>"
                # You could also show TOP = (f_CPU / (2 * Prescaler * f_out)) - 1 if solving for TOP
            elif "Fast PWM" in current_mode_name:
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / ({desired_freq_str} * (0xFF + 1))</b>"
            elif "Phase Correct PWM" in current_mode_name:
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / (2 * {desired_freq_str} * 0xFF)</b>"
            else:
                formula_text = f"<b>Generel Formel for Timer0: Afhænger af mode.</b>"

        elif selected_timer == "Timer1":
            max_16bit_val = 0xFFFF
            wgm_bits_t1_info = WGM_BITS_T1.get(current_mode_name, {})
            
            if current_mode_name == "Normal":
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / ({desired_freq_str} * ({max_16bit_val} + 1))</b>"
            elif "CTC" in current_mode_name:
                # For CTC, user provides desired_freq and desired_top (OCR1A or ICR1)
                top_register_name = "ICR1" if "TOP=ICR1" in current_mode_name else "OCR1A"
                top_val_in_formula = str(inferred_top_value) if inferred_top_value is not None and inferred_top_value != -1 else top_register
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / (2 * {desired_freq_str} * ({top_val_in_formula} + 1))</b>"
            elif "Fast PWM" in current_mode_name:
                if "TOP_fixed" in wgm_bits_t1_info:
                    top_fixed_val = wgm_bits_t1_info["TOP_fixed"]
                    formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / ({desired_freq_str} * ({top_fixed_val} + 1))</b>"
                else: # Variable TOP (ICR1 or OCR1A)
                    top_register_name = "ICR1" if "TOP=ICR1" in current_mode_name else "OCR1A"
                    top_val_in_formula = str(inferred_top_value) if inferred_top_value is not None and inferred_top_value != -1 else top_register
                    formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / ({desired_freq_str} * ({top_val_in_formula} + 1))</b>"
            elif "Phase Correct PWM" in current_mode_name:
                if "TOP_fixed" in wgm_bits_t1_info:
                    top_fixed_val = wgm_bits_t1_info["TOP_fixed"]
                    formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / (2 * {desired_freq_str} * {top_fixed_val})</b>"
                else: # Variable TOP (ICR1 or OCR1A)
                    top_register_name = "ICR1" if "TOP=ICR1" in current_mode_name else "OCR1A"
                    top_val_in_formula = str(inferred_top_value) if inferred_top_value is not None and inferred_top_value != -1 else top_register
                    formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / (2 * {desired_freq_str} * {top_val_in_formula})</b>"
            else:
                formula_text = f"<b>Generel Formel for Timer1: Afhænger af mode.</b>"

        elif selected_timer == "Timer2":
            if current_mode_name == "Normal":
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / ({desired_freq_str} * (0xFF + 1))</b>"
            elif current_mode_name == "CTC":
                top_val_in_formula = str(inferred_top_value) if inferred_top_value is not None and inferred_top_value != -1 else "OCR2A"
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / (2 * {desired_freq_str} * ({top_val_in_formula} + 1))</b>"
            elif "Fast PWM" in current_mode_name:
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / ({desired_freq_str} * (0xFF + 1))</b>"
            elif "Phase Correct PWM" in current_mode_name:
                formula_text = f"<b>Formel: {prescaler_str} = {cpu_freq_str} / (2 * {desired_freq_str} * 0xFF)</b>"
            else:
                formula_text = f"<b>Generel Formel for Timer2: Afhænger af mode og registre.</b>"

        self.formula_label.set_markup(formula_text)


    def calculate_prescaler_and_top(self, _):
        # Pass the parent window to the error/warning dialogs
        parent_window = self.get_root()

        try:
            cpu_freq_mhz = float(self.cpu_freq_entry_var.get_text())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            desired_freq = float(self.prescaler_desired_freq_buffer.get_text())
            selected_timer = self._get_selected_timer()
            
            selected_index = self.prescaler_mode_selection_dropdown.get_selected()
            if selected_index == -1:
                show_error("Input Fejl", "Vælg venligst en Timer Mode.")
                self._clear_results()
                self._update_formula_label(selected_timer, "", "N/A") # Update formula on error
                return

            selected_mode = self.prescaler_mode_selection_store.get_string(selected_index)
            # The desired_top_buffer text needs to be parsed if it's used as an input TOP
            desired_top_input = parse_hex_bin_int(self.prescaler_desired_top_buffer.get_text())


            if desired_freq <= 0:
                show_error("Ugyldig Frekvens", "Ønsket frekvens skal være større end nul.")
                self._clear_results()
                self._update_formula_label(selected_timer, selected_mode, "N/A") # Update formula on error
                return

            best_prescaler = None
            best_top = None
            min_freq_error = float('inf') 
            actual_achieved_freq = 0.0

            prescaler_options = []
            max_timer_top_value = 0 # Max value for the timer (0xFF or 0xFFFF)
            wgm_map = {}

            if selected_timer == "Timer0":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
                max_timer_top_value = 255 
                wgm_map = WGM_BITS_T0
            elif selected_timer == "Timer1":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
                max_timer_top_value = 65535 
                wgm_map = WGM_BITS_T1
            elif selected_timer == "Timer2":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T2"].keys() if p != "0"]
                max_timer_top_value = 255
                wgm_map = WGM_BITS_T2

            prescaler_options.sort() 

            mode_info = wgm_map.get(selected_mode, {})
            if not mode_info:
                show_error("Konfigurationsfejl", f"Ukendt mode: {selected_mode}. Kontroller indstillingerne.")
                self._clear_results()
                self._update_formula_label(selected_timer, selected_mode, "N/A") # Update formula on error
                return

            # Determine the divisor (1 or 2) based on mode type
            divisor = 1
            if "Phase Correct" in selected_mode or "CTC" in selected_mode:
                divisor = 2 # For CTC and Phase Correct, formula factor is 2*Prescaler*TOP

            # For Timer1, use specific formula_factor if present
            if selected_timer == "Timer1" and "formula_factor" in mode_info:
                divisor = mode_info["formula_factor"]


            # Iterate through prescalers to find the best match
            for prescaler in prescaler_options:
                top_candidate = 0 # Calculated TOP value for this prescaler

                fixed_top_mode = mode_info.get("TOP_fixed")
                top_variable_mode = mode_info.get("TOP_variable")

                if current_mode_name == "Normal":
                    top_candidate = max_timer_top_value
                elif fixed_top_mode is not None:
                    top_candidate = fixed_top_mode
                elif top_variable_mode: # CTC and Variable TOP PWM modes
                    # Use desired_top_input if provided and applicable, otherwise calculate
                    if desired_top_input is not None and desired_top_input != 0: # If user provided a TOP value
                        top_candidate = desired_top_input
                    else: # Calculate TOP based on desired frequency
                        denominator_calc_top = divisor * prescaler * desired_freq
                        if denominator_calc_top == 0: continue # Avoid division by zero
                        
                        if "Phase Correct" in selected_mode: # Phase Correct formula for TOP calculation
                            calculated_top_float = (cpu_freq_hz / (divisor * prescaler * desired_freq))
                            top_candidate = round(calculated_top_float)
                        else: # Fast PWM / CTC formula for TOP calculation (includes +1)
                            calculated_top_float = (cpu_freq_hz / denominator_calc_top) - 1
                            top_candidate = round(calculated_top_float)
                else:
                    continue # Skip modes not supported or improperly configured

                # Validate TOP candidate
                if top_candidate < 0 or top_candidate > max_timer_top_value:
                    continue 

                # Calculate actual frequency with this prescaler and TOP
                actual_freq_candidate = 0.0
                if "Phase Correct" in selected_mode and top_candidate > 0:
                    actual_freq_candidate = cpu_freq_hz / (divisor * prescaler * top_candidate)
                elif (top_candidate + 1) > 0: # For Normal, CTC, Fast PWM
                    actual_freq_candidate = cpu_freq_hz / (divisor * prescaler * (top_candidate + 1))
                else:
                    continue # Avoid division by zero

                freq_error = abs(actual_freq_candidate - desired_freq)

                if freq_error < min_freq_error:
                    min_freq_error = freq_error
                    best_prescaler = prescaler
                    best_top = top_candidate
                    actual_achieved_freq = actual_freq_candidate

            if best_prescaler is not None:
                error_percent = (abs(actual_achieved_freq - desired_freq) / desired_freq) * 100
                self.calculated_prescaler_label.set_markup(f"<span weight='bold'>{best_prescaler}</span>")
                self.calculated_top_label.set_markup(f"<span weight='bold'>{best_top}</span>")
                self.calculated_actual_freq_label.set_text(f"{actual_achieved_freq:.2f} Hz")
                self.calculated_error_percent_label.set_text(f"{error_percent:.4f}%")
                # Update formula based on actual calculated values
                self._update_formula_label(selected_timer, selected_mode, best_top)
            else:
                show_warning("Intet Match", "Kunne ikke finde en passende prescaler og TOP-værdi for den ønskede frekvens med de valgte indstillinger. Prøv en anden frekvens eller tilstand.")
                self._clear_results()
                self._update_formula_label(selected_timer, selected_mode, "N/A") # Reset formula if no match found


        except ValueError as ve:
            show_error("Input Fejl", f"Ugyldigt input: {ve}. Sørg for, at alle felter indeholder gyldige tal.")
            self._clear_results()
            self._update_formula_label(selected_timer, selected_mode, "N/A") # Update formula on error
        except KeyError as ke:
            show_error("Konfigurationsfejl", f"Ukendt mode eller prescaler: {ke}. Kontroller indstillingerne.")
            self._clear_results()
            self._update_formula_label(selected_timer, selected_mode, "N/A") # Update formula on error
        except Exception as e:
            show_error("Fejl", f"En uventet fejl opstod: {e}")
            self._clear_results()
            self._update_formula_label(selected_timer, selected_mode, "N/A") # Update formula on error

    def _clear_results(self):
        self.calculated_prescaler_label.set_markup("<span weight='bold'>N/A</span>")
        self.calculated_top_label.set_markup("<span weight='bold'>N/A</span>")
        self.calculated_actual_freq_label.set_text("N/A")
        self.calculated_error_percent_label.set_text("N/A")
