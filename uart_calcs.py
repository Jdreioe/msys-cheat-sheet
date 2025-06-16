import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango, Gdk
import math

# Helper function for message dialogs, passed to sub-tabs
def _show_message_dialog_helper(parent_widget, title, message, message_type):
    full_message_text = f"<b>{title}</b>\n\n{message}"
    dialog = Gtk.MessageDialog(
        transient_for=parent_widget.get_root() if parent_widget.get_root() else None,
        modal=True,
        message_type=message_type,
        buttons=Gtk.ButtonsType.OK,
        text=full_message_text
    )
    dialog.connect("response", lambda d, r: d.destroy())
    dialog.present()


class UartBaudRateCalculatorTab(Gtk.Box):
    def __init__(self, cpu_freq_entry, show_message_dialog_func):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.cpu_freq_entry = cpu_freq_entry # Direct reference to the CPU frequency entry
        self._show_message_dialog = show_message_dialog_func
        self._setup_ui()

    def _setup_ui(self):
        grid_baud = Gtk.Grid()
        grid_baud.set_row_spacing(5)
        grid_baud.set_column_spacing(10)
        grid_baud.set_margin_start(10)
        grid_baud.set_margin_end(10)
        grid_baud.set_margin_top(10)
        grid_baud.set_margin_bottom(10)
        self.append(grid_baud)

        formula_explanation_label = Gtk.Label()
        formula_explanation_label.set_markup("<b>BAUD = f_cpu / (16 * (UBRRn + 1))</b>")
        formula_explanation_label.set_wrap(True)
        formula_explanation_label.set_justify(Gtk.Justification.CENTER)
        grid_baud.attach(formula_explanation_label, 0, 0, 2, 1)

        desired_baud_label = Gtk.Label(label="Ønsket Baud Rate (bps):", xalign=0)
        grid_baud.attach(desired_baud_label, 0, 1, 1, 1)
        self.uart_desired_baud_entry = Gtk.Entry()

        self.uart_desired_baud_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.uart_desired_baud_entry.connect("changed", self._on_baud_input_changed)
        grid_baud.attach(self.uart_desired_baud_entry, 1, 1, 1, 1)

        ubrr_input_label = Gtk.Label(label="UBRRn Værdi:", xalign=0)
        grid_baud.attach(ubrr_input_label, 0, 2, 1, 1)
        self.uart_ubrr_input_entry = Gtk.Entry()
        self.uart_ubrr_input_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.uart_ubrr_input_entry.connect("changed", self._on_baud_input_changed)
        grid_baud.attach(self.uart_ubrr_input_entry, 1, 2, 1, 1)

        note_label = Gtk.Label(label="<i>Bemærk: Antager U2Xn-bit er 0 (Normal tilstand).</i>")
        note_label.set_use_markup(True)
        note_label.set_halign(Gtk.Align.START)
        grid_baud.attach(note_label, 0, 3, 2, 1)

        grid_baud.attach(Gtk.Label(label="Beregnet UBRRn (fra ønsket):", xalign=0), 0, 4, 1, 1)
        self.uart_result_ubrr_label = Gtk.Label(label="", xalign=0)
        self.uart_result_ubrr_label.set_css_classes(["monospace", "dim-label"])
        grid_baud.attach(self.uart_result_ubrr_label, 1, 4, 1, 1)

        grid_baud.attach(Gtk.Label(label="Faktisk Baud Rate:", xalign=0), 0, 5, 1, 1)
        self.uart_result_actual_baud_label = Gtk.Label(label="", xalign=0)
        self.uart_result_actual_baud_label.set_css_classes(["success", "monospace"])
        grid_baud.attach(self.uart_result_actual_baud_label, 1, 5, 1, 1)

        grid_baud.attach(Gtk.Label(label="Baud Rate Fejl:", xalign=0), 0, 6, 1, 1)
        self.uart_result_baud_error_label = Gtk.Label(label="", xalign=0)
        self.uart_result_baud_error_label.set_css_classes(["error", "monospace"])
        grid_baud.attach(self.uart_result_baud_error_label, 1, 6, 1, 1)

        self.baud_message_label = Gtk.Label(label="", xalign=0)
        self.baud_message_label.set_hexpand(True)
        self.baud_message_label.get_style_context().add_class("error-label")
        grid_baud.attach(self.baud_message_label, 0, 7, 2, 1)

        self._on_baud_input_changed(None)

    def _calculate_ubrr_from_baud(self, cpu_freq_hz, desired_baud_rate):
        if desired_baud_rate <= 0:
            return None
        ubrr_float = (cpu_freq_hz / (16 * desired_baud_rate)) - 1
        if ubrr_float < 0:
            return None
        ubrr_int = round(ubrr_float)
        if not (0 <= ubrr_int <= 4095):
            return None
        return ubrr_int

    def _calculate_baud_from_ubrr(self, cpu_freq_hz, ubrr_value):
        if ubrr_value < 0:
            return None
        actual_baud_rate = cpu_freq_hz / (16 * (ubrr_value + 1))
        return actual_baud_rate

    def _on_baud_input_changed(self, widget):
        self.baud_message_label.set_label("")
        self.uart_result_ubrr_label.set_text("N/A")
        self.uart_result_actual_baud_label.set_text("N/A")
        self.uart_result_baud_error_label.set_text("N/A")

        try:
            cpu_freq_mhz = float(self.cpu_freq_entry.get_text().replace(',', '.'))
            cpu_freq_hz = cpu_freq_mhz * 1_000_000

            desired_baud_text = self.uart_desired_baud_entry.get_text().replace(',', '.')
            ubrr_input_text = self.uart_ubrr_input_entry.get_text().replace(',', '.')

            if desired_baud_text and ubrr_input_text:
                self.baud_message_label.set_label("Ugyldig input: Angiv enten 'Ønsket Baud Rate' ELLER 'UBRRn Værdi', ikke begge.")
                self.uart_desired_baud_entry.set_sensitive(True)
                self.uart_ubrr_input_entry.set_sensitive(True)
                return
            
            if not desired_baud_text and not ubrr_input_text:
                self.baud_message_label.set_label("Angiv venligst en værdi for Baud Rate eller UBRRn.")
                self.uart_desired_baud_entry.set_sensitive(True)
                self.uart_ubrr_input_entry.set_sensitive(True)
                return

            if desired_baud_text:
                desired_baud_rate = float(desired_baud_text)
                self.uart_ubrr_input_entry.set_sensitive(False)
                
                ubrr_int = self._calculate_ubrr_from_baud(cpu_freq_hz, desired_baud_rate)
                if ubrr_int is None:
                    self.baud_message_label.set_label("Ønsket Baud Rate er for høj/lav, eller resultatet er uden for UBRRn-intervallet (0-4095).")
                    return

                actual_baud_rate = self._calculate_baud_from_ubrr(cpu_freq_hz, ubrr_int)
                error_percent = ((actual_baud_rate - desired_baud_rate) / desired_baud_rate) * 100 if desired_baud_rate != 0 else float('inf')

                self.uart_result_ubrr_label.set_text(f"{ubrr_int}")
                self.uart_result_actual_baud_label.set_text(f"{actual_baud_rate:.2f} bps")
                self.uart_result_baud_error_label.set_text(f"{error_percent:.2f}%")

                if abs(error_percent) > 2:
                    self._show_message_dialog("Baud Rate Advarsel",
                                           f"Den beregnede fejl er {error_percent:.2f}%.\n"
                                           "Dette kan være for højt til pålidelig kommunikation.",
                                           Gtk.MessageType.WARNING)

            elif ubrr_input_text:
                ubrr_value = int(float(ubrr_input_text))
                self.uart_desired_baud_entry.set_sensitive(False)

                if not (0 <= ubrr_value <= 4095):
                    self.baud_message_label.set_label("UBRRn værdi skal være mellem 0 og 4095.")
                    return

                actual_baud_rate = self._calculate_baud_from_ubrr(cpu_freq_hz, ubrr_value)
                if actual_baud_rate is None:
                    self.baud_message_label.set_label("UBRRn værdi er ugyldig for beregning af baud rate.")
                    return
                
                self.uart_result_actual_baud_label.set_text(f"{actual_baud_rate:.2f} bps")
                self.uart_result_ubrr_label.set_text(str(ubrr_value))
                self.uart_result_baud_error_label.set_text("N/A (Intet ønsket)")

            # Ensure correct sensitivity state if user clears one field
            if not self.uart_desired_baud_entry.get_text() and not self.uart_ubrr_input_entry.get_text():
                self.uart_desired_baud_entry.set_sensitive(True)
                self.uart_ubrr_input_entry.set_sensitive(True)

        except ValueError:
            self.baud_message_label.set_label("Indtast venligst gyldige numeriske værdier.")
            self.uart_desired_baud_entry.set_sensitive(True)
            self.uart_ubrr_input_entry.set_sensitive(True)
        except Exception as e:
            self.baud_message_label.set_label(f"Der opstod en uventet fejl: {e}")
            self.uart_desired_baud_entry.set_sensitive(True)
            self.uart_ubrr_input_entry.set_sensitive(True)


class UartTransmissionTimeCalculatorTab(Gtk.Box):
    def __init__(self, uart_baud_calculator_tab_instance, show_message_dialog_func):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.uart_baud_calculator_tab = uart_baud_calculator_tab_instance
        self._show_message_dialog = show_message_dialog_func
        self._setup_ui()

    def _setup_ui(self):
        grid_time = Gtk.Grid()
        grid_time.set_row_spacing(5)
        grid_time.set_column_spacing(10)
        grid_time.set_margin_start(10)
        grid_time.set_margin_end(10)
        grid_time.set_margin_top(10)
        grid_time.set_margin_bottom(10)
        self.append(grid_time)

        # Formula Explanation for Transmission Time
        formula_explanation_label = Gtk.Label()
        formula_explanation_label.set_markup("<b>Tid = ((dataBit + startBit + stopBit + paritet) * karakterer) / Baudrate</b>")
        formula_explanation_label.set_wrap(True)
        formula_explanation_label.set_justify(Gtk.Justification.CENTER)
        grid_time.attach(formula_explanation_label, 0, 0, 2, 1)

        grid_time.attach(Gtk.Label(label="Databits:", xalign=0), 0, 1, 1, 1)
        self.data_bits_entry = Gtk.Entry()
        self.data_bits_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.data_bits_entry.connect("changed", self._on_calculate_time_clicked)
        grid_time.attach(self.data_bits_entry, 1, 1, 1, 1)

        grid_time.attach(Gtk.Label(label="Startbits:", xalign=0), 0, 2, 1, 1)
        self.start_bits_entry = Gtk.Entry()
        self.start_bits_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.start_bits_entry.connect("changed", self._on_calculate_time_clicked)
        grid_time.attach(self.start_bits_entry, 1, 2, 1, 1)

        grid_time.attach(Gtk.Label(label="Stopbits:", xalign=0), 0, 3, 1, 1)
        self.stop_bits_entry = Gtk.Entry()
        self.stop_bits_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.stop_bits_entry.connect("changed", self._on_calculate_time_clicked)
        grid_time.attach(self.stop_bits_entry, 1, 3, 1, 1)

        grid_time.attach(Gtk.Label(label="Paritet (0=Ingen, 1=Brugt):", xalign=0), 0, 4, 1, 1)
        self.parity_combo = Gtk.ComboBoxText()
        self.parity_combo.append_text("0 (Ingen)")
        self.parity_combo.append_text("1 (Lige/Ulige)")
        self.parity_combo.set_active(1)
        self.parity_combo.connect("changed", self._on_calculate_time_clicked)
        grid_time.attach(self.parity_combo, 1, 4, 1, 1)
        
        grid_time.attach(Gtk.Label(label="Karakterer:", xalign=0), 0, 5, 1, 1)
        self.characters_entry = Gtk.Entry()
        self.characters_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.characters_entry.connect("changed", self._on_calculate_time_clicked)
        grid_time.attach(self.characters_entry, 1, 5, 1, 1)

        grid_time.attach(Gtk.Label(label="Baud Rate (bps):", xalign=0), 0, 6, 1, 1)
        self.time_baud_rate_entry = Gtk.Entry()
        self.time_baud_rate_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.time_baud_rate_entry.connect("changed", self._on_calculate_time_clicked)
        grid_time.attach(self.time_baud_rate_entry, 1, 6, 1, 1)


        grid_time.attach(Gtk.Label(label="Transmissionstid (s):", xalign=0), 0, 8, 1, 1)
        self.transmission_time_label = Gtk.Label(label="N/A", xalign=0)
        self.transmission_time_label.set_css_classes(["success", "monospace"])
        grid_time.attach(self.transmission_time_label, 1, 8, 1, 1)

        self.time_message_label = Gtk.Label(label="", xalign=0)
        self.time_message_label.set_hexpand(True)
        self.time_message_label.get_style_context().add_class("error-label")
        grid_time.attach(self.time_message_label, 0, 9, 2, 1)

        self._on_calculate_time_clicked(None)

    def _on_calculate_time_clicked(self, widget):
        self.time_message_label.set_label("")
        self.transmission_time_label.set_label("N/A")

        try:
            data_bits = int(self.data_bits_entry.get_text().replace(',', '.'))
            start_bits = int(self.start_bits_entry.get_text().replace(',', '.'))
            stop_bits = int(self.stop_bits_entry.get_text().replace(',', '.'))
            
            parity_selection = self.parity_combo.get_active_text()
            parity_bit = int(parity_selection[0]) 

            characters = int(self.characters_entry.get_text().replace(',', '.'))
            baud_rate = float(self.time_baud_rate_entry.get_text().replace(',', '.'))

            if data_bits <= 0 or start_bits <= 0 or stop_bits < 0 or characters <= 0:
                self.time_message_label.set_label("Data, start, stop bits og karakterer skal være positive heltal.")
                return
            if not (baud_rate > 0):
                self.time_message_label.set_label("Baud Rate skal være større end 0.")
                return
            if not (0 <= parity_bit <= 1):
                 self.time_message_label.set_label("Ugyldigt paritetsvalg.")
                 return

            total_bits_per_character = data_bits + start_bits + stop_bits + parity_bit

            transmission_time = (total_bits_per_character * characters) / baud_rate
            self.transmission_time_label.set_text(f"{transmission_time:.6f} s")

        except ValueError:
            self.time_message_label.set_label("Indtast venligst gyldige numeriske værdier for alle inputfelter.")
        except Exception as e:
            self.time_message_label.set_label(f"Der opstod en uventet fejl: {e}")


class UartCalculator(Gtk.Box):
    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.cpu_freq_entry = cpu_freq_entry

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_hexpand(True)
        header_box.set_vexpand(False)
        self.append(header_box)

        title_label = Gtk.Label(label="UART Beregner", xalign=0)
        title_label.get_style_context().add_class("title-label")
        header_box.append(title_label)

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.append(self.stack)

        self.stack_switcher = Gtk.StackSwitcher(stack=self.stack)
        self.stack_switcher.set_halign(Gtk.Align.CENTER)
        header_box.append(self.stack_switcher)

        # Pass the message dialog helper function to sub-tabs
        _bound_show_message_dialog = self._show_message_dialog

        # Pass the cpu_freq_entry directly to the UartBaudRateCalculatorTab
        self.baud_rate_tab = UartBaudRateCalculatorTab(cpu_freq_entry, _bound_show_message_dialog)
        self.stack.add_titled(self.baud_rate_tab, "baud_rate_calc", "Baud Rate Beregning")

        # Pass the baud_rate_tab instance to the transmission time tab
        self.transmission_time_tab = UartTransmissionTimeCalculatorTab(self.baud_rate_tab, _bound_show_message_dialog)
        self.stack.add_titled(self.transmission_time_tab, "transmission_time_calc", "Transmissionstid Beregning")

        self.stack.set_visible_child_name("baud_rate_calc") # Set default tab

    def _show_message_dialog(self, title, message, message_type):
        _show_message_dialog_helper(self, title, message, message_type)
