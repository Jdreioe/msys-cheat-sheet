import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

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

        self.cpu_freq_entry_var = CPU_FREQ_DEFAULT # Use shared CPU freq var

        self.prescaler_desired_freq_buffer = Gtk.EntryBuffer()
        self.prescaler_desired_top_buffer = Gtk.EntryBuffer(text="0") # Default 0

        self.prescaler_timer_selection_store = Gtk.StringList.new(["Timer0", "Timer1", "Timer2"])
        self.prescaler_timer_selection_dropdown = Gtk.DropDown.new(self.prescaler_timer_selection_store, None)
        self.prescaler_timer_selection_dropdown.set_selected(0) # Default to Timer0
        self.prescaler_timer_selection_dropdown.connect("notify::selected", self._update_prescaler_mode_options)

        self.prescaler_mode_selection_store = Gtk.StringList.new([])
        self.prescaler_mode_selection_dropdown = Gtk.DropDown.new(self.prescaler_mode_selection_store, None)
        self.prescaler_mode_selection_dropdown.set_property("width-request", 200)

        self._create_widgets()
        self._update_prescaler_mode_options() # Initial population of mode dropdown

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
        timer_radio_box.append(self.radio_timer0)

        self.radio_timer1 = Gtk.CheckButton(label="Timer1")
        self.radio_timer1.set_group(self.radio_timer0)
        self.radio_timer1.connect("toggled", self._update_prescaler_mode_options)
        timer_radio_box.append(self.radio_timer1)

        self.radio_timer2 = Gtk.CheckButton(label="Timer2")
        self.radio_timer2.set_group(self.radio_timer0)
        self.radio_timer2.connect("toggled", self._update_prescaler_mode_options)
        timer_radio_box.append(self.radio_timer2)
        
        # Calculate Button
        calculate_button = Gtk.Button(label="Beregn Prescaler")
        calculate_button.connect("clicked", self.calculate_prescaler_and_top)
        grid.attach(calculate_button, 0, 4, 4, 1)

        # Outputs
        self.calculated_prescaler_label = Gtk.Label(label="N/A", xalign=0)
        self.calculated_prescaler_label.set_markup("<span weight='bold'>N/A</span>")
        grid.attach(Gtk.Label(label="Optimal Prescaler:", xalign=0), 0, 5, 1, 1)
        grid.attach(self.calculated_prescaler_label, 1, 5, 3, 1)

        self.calculated_top_label = Gtk.Label(label="N/A", xalign=0)
        self.calculated_top_label.set_markup("<span weight='bold'>N/A</span>")
        grid.attach(Gtk.Label(label="Anbefalet TOP-værdi:", xalign=0), 0, 6, 1, 1)
        grid.attach(self.calculated_top_label, 1, 6, 3, 1)

        self.calculated_actual_freq_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(Gtk.Label(label="Faktisk Frekvens:", xalign=0), 0, 7, 1, 1)
        grid.attach(self.calculated_actual_freq_label, 1, 7, 3, 1)
        
        self.calculated_error_percent_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(Gtk.Label(label="Fejl (%):", xalign=0), 0, 8, 1, 1)
        grid.attach(self.calculated_error_percent_label, 1, 8, 3, 1)

    def _get_selected_timer(self):
        if self.radio_timer0.get_active():
            return "Timer0"
        elif self.radio_timer1.get_active():
            return "Timer1"
        elif self.radio_timer2.get_active():
            return "Timer2"
        return ""

    def _update_prescaler_mode_options(self, *args):
        selected_timer = self._get_selected_timer()
        modes = []
        if selected_timer == "Timer0":
            modes = list(WGM_BITS_T0.keys())
        elif selected_timer == "Timer1":
            modes = list(WGM_BITS_T1.keys())
        elif selected_timer == "Timer2":
            modes = list(WGM_BITS_T2.keys())
        
        # --- FIX START ---
        # Create a new Gtk.StringList with the updated modes
        new_mode_store = Gtk.StringList.new(modes)
        # Set the new model to the dropdown
        self.prescaler_mode_selection_dropdown.set_model(new_mode_store)
        self.prescaler_mode_selection_store = new_mode_store # Update internal reference
        # --- FIX END ---

        if modes:
            self.prescaler_mode_selection_dropdown.set_selected(0) # Set default to first mode
        else:
            self.prescaler_mode_selection_dropdown.set_selected(-1) # No selection
    def calculate_prescaler_and_top(self, button):
        # Pass the parent window to the error/warning dialogs
        parent_window = self.get_root()

        try:
            cpu_freq_mhz = float(self.cpu_freq_entry_var.get_text())
            cpu_freq_hz = cpu_freq_mhz * 1_000_000
            desired_freq = float(self.prescaler_desired_freq_buffer.get_text())
            selected_timer = self._get_selected_timer()
            
            selected_index = self.prescaler_mode_selection_dropdown.get_selected()
            if selected_index == -1:
                show_error("Input Fejl", "Vælg venligst en Timer Mode.", parent_window)
                self._clear_results()
                return

            selected_mode = self.prescaler_mode_selection_store.get_string(selected_index)
            desired_top_input = parse_hex_bin_int(self.prescaler_desired_top_buffer.get_text())

            if desired_freq <= 0:
                show_error("Ugyldig Frekvens", "Ønsket frekvens skal være større end nul.", parent_window)
                self._clear_results()
                return

            best_prescaler = None
            best_top = None
            min_freq_error = float('inf') 
            actual_achieved_freq = 0.0

            prescaler_options = []
            max_top = 0
            wgm_map = {}

            if selected_timer == "Timer0":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
                max_top = 255 
                wgm_map = WGM_BITS_T0
            elif selected_timer == "Timer1":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T0_T1"].keys() if p != "0"]
                max_top = 65535 
                wgm_map = WGM_BITS_T1
            elif selected_timer == "Timer2":
                prescaler_options = [int(p) for p in PRESCALERS_T0_T1_T2["T2"].keys() if p != "0"]
                max_top = 255
                wgm_map = WGM_BITS_T2

            prescaler_options.sort() 

            for prescaler in prescaler_options:
                divisor = 1 
                
                mode_info = wgm_map.get(selected_mode, {})
                
                if "Phase Correct" in selected_mode:
                    divisor = 2
                if selected_timer == "Timer1" and "formula_factor" in mode_info:
                    divisor = mode_info["formula_factor"]
                elif "CTC" in selected_mode or "Fast PWM" in selected_mode:
                    divisor = 1


                fixed_top_mode = mode_info.get("TOP_fixed")
                if fixed_top_mode is not None:
                    top_candidate = fixed_top_mode
                elif selected_mode == "Normal":
                    top_candidate = max_top
                elif mode_info.get("TOP_variable"):
                    denominator_calc_top = divisor * prescaler * desired_freq
                    if denominator_calc_top == 0: continue
                    
                    if "Phase Correct" in selected_mode:
                        calculated_top_float = (cpu_freq_hz / (divisor * prescaler * desired_freq))
                        top_candidate = round(calculated_top_float)
                    else:
                        calculated_top_float = (cpu_freq_hz / denominator_calc_top) - 1
                        top_candidate = round(calculated_top_float)
                else:
                    continue

                if top_candidate < 0 or top_candidate > max_top:
                    continue 

                if "Phase Correct" in selected_mode:
                    if top_candidate == 0: continue
                    actual_freq_candidate = cpu_freq_hz / (divisor * prescaler * top_candidate)
                else:
                    if (top_candidate + 1) == 0: continue
                    actual_freq_candidate = cpu_freq_hz / (divisor * prescaler * (top_candidate + 1))

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
            else:
                show_warning("Intet Match", "Kunne ikke finde en passende prescaler og TOP-værdi for den ønskede frekvens med de valgte indstillinger. Prøv en anden frekvens eller tilstand.", parent_window)
                self._clear_results()

        except ValueError as ve:
            show_error("Input Fejl", f"Ugyldigt input: {ve}. Sørg for, at alle felter indeholder gyldige tal.", parent_window)
            self._clear_results()
        except KeyError as ke:
            show_error("Konfigurationsfejl", f"Ukendt mode eller prescaler: {ke}. Kontroller indstillingerne.", parent_window)
            self._clear_results()
        except Exception as e:
            show_error("Fejl", f"En uventet fejl opstod: {e}", parent_window)
            self._clear_results()

    def _clear_results(self):
        self.calculated_prescaler_label.set_markup("<span weight='bold'>N/A</span>")
        self.calculated_top_label.set_markup("<span weight='bold'>N/A</span>")
        self.calculated_actual_freq_label.set_text("N/A")
        self.calculated_error_percent_label.set_text("N/A")