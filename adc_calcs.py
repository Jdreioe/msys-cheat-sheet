import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class AdcCalculator(Gtk.Box): # Inherit from Gtk.Box for overall layout
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._setup_adc_tab()

    def _setup_adc_tab(self):
        # Create a new Gtk.Box for the ADC tab content
        adc_tab_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        adc_tab_content.set_margin_start(10)
        adc_tab_content.set_margin_end(10)
        adc_tab_content.set_margin_top(10)
        adc_tab_content.set_margin_bottom(10)

        self.append(adc_tab_content)

        # Gtk.LabelFrame equivalent: Gtk.Frame
        adc_frame = Gtk.Frame()
        adc_frame.set_label("ADC Input Voltage Calculation")
        adc_frame.set_margin_top(10)
        adc_frame.set_margin_bottom(10)
        adc_frame.set_margin_start(10)
        adc_frame.set_margin_end(10)
        adc_tab_content.append(adc_frame)

        # Use Gtk.Grid for layout within the frame
        adc_grid = Gtk.Grid()
        adc_grid.set_row_spacing(5)
        adc_grid.set_column_spacing(5)
        adc_grid.set_margin_start(10)
        adc_grid.set_margin_end(10)
        adc_grid.set_margin_top(10)
        adc_grid.set_margin_bottom(10)
        adc_frame.set_child(adc_grid)

        # Formula Label - Correctly placed at row 0
        formula_label = Gtk.Label(label="Vin = (ADCW / (2^N - 1)) * Vref")
        formula_label.set_halign(Gtk.Align.CENTER)
        adc_grid.attach(formula_label, 0, 0, 2, 1) # Column 0, Row 0, span 2 columns

        # ADC Value Entry - Now at Row 1
        adc_grid.attach(Gtk.Label(label="ADC Value (0-1023 for 10-bit):"), 0, 1, 1, 1)
        self.adc_adc_value_entry = Gtk.Entry()
        self.adc_adc_value_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        adc_grid.attach(self.adc_adc_value_entry, 1, 1, 1, 1)
        self.adc_adc_value_entry.set_hexpand(True)

        # ADC Reference Voltage Entry - Now at Row 2
        adc_grid.attach(Gtk.Label(label="ADC Reference Voltage (Vref in Volts):"), 0, 2, 1, 1)
        self.adc_vref_entry = Gtk.Entry()
        self.adc_vref_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        adc_grid.attach(self.adc_vref_entry, 1, 2, 1, 1)
        self.adc_vref_entry.set_hexpand(True)

        # ADC Resolution Entry - Now at Row 3
        adc_grid.attach(Gtk.Label(label="ADC Resolution (bits):"), 0, 3, 1, 1)
        self.adc_resolution_entry = Gtk.Entry()
        self.adc_resolution_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        adc_grid.attach(self.adc_resolution_entry, 1, 3, 1, 1)
        self.adc_resolution_entry.set_hexpand(True)

        # Calculate Button - Now at Row 4
        btn_calculate_adc = Gtk.Button(label="Calculate Input Voltage")
        btn_calculate_adc.connect("clicked", self._calculate_adc_voltage)
        adc_grid.attach(btn_calculate_adc, 0, 4, 2, 1)
        btn_calculate_adc.set_margin_top(10)
        btn_calculate_adc.set_margin_bottom(10)

        # Input Voltage Result Label - Now at Row 5
        adc_grid.attach(Gtk.Label(label="Input Voltage:"), 0, 5, 1, 1)
        
        self.adc_result_voltage_label = Gtk.Label()
        self.adc_result_voltage_label.set_justify(Gtk.Justification.LEFT)
        self.adc_result_voltage_label.set_xalign(0)
        adc_grid.attach(self.adc_result_voltage_label, 1, 5, 1, 1)
        self.adc_result_voltage_label.set_hexpand(True)
        
        self.adc_result_voltage_label.set_markup("<b>N/A</b>")


    def _calculate_adc_voltage(self, button):
        try:
            adc_value = int(self.adc_adc_value_entry.get_text())
            vref = float(self.adc_vref_entry.get_text())
            resolution_bits = int(self.adc_resolution_entry.get_text())

            max_adc_reading_val = (2**resolution_bits) - 1
            if not (0 <= adc_value <= max_adc_reading_val):
                self._show_message_dialog("Invalid Input", 
                                          f"ADC Value must be between 0 and {max_adc_reading_val} for a {resolution_bits}-bit ADC.", 
                                          Gtk.MessageType.ERROR)
                self.adc_result_voltage_label.set_markup("<b>N/A</b>")
                return

            if vref <= 0:
                self._show_message_dialog("Invalid Input", 
                                          "Reference Voltage (Vref) must be positive.", 
                                          Gtk.MessageType.ERROR)
                self.adc_result_voltage_label.set_markup("<b>N/A</b>")
                return

            input_voltage = (adc_value / max_adc_reading_val) * vref

            self.adc_result_voltage_label.set_markup(f"<span foreground='blue'><b>{input_voltage:.4f} V</b></span>")

        except ValueError:
            self._show_message_dialog("Invalid Input", 
                                      "Please enter valid numbers for ADC Value, Reference Voltage, and Resolution.", 
                                      Gtk.MessageType.ERROR)
            self.adc_result_voltage_label.set_markup("<b>N/A</b>")
        except Exception as e:
            self._show_message_dialog("Error", 
                                      f"An unexpected error occurred: {e}", 
                                      Gtk.MessageType.ERROR)
            self.adc_result_voltage_label.set_markup("<b>N/A</b>")

    def _show_message_dialog(self, title, message, message_type):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.present()
        dialog.connect("response", lambda d, r: d.destroy())
