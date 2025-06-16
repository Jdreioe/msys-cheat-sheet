import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

# Duty Cycle Calculator Tab - Mode 1: Freq/Duty Cycle -> TOP/OCRn
class PWMFreqToTimerValuesTab(Gtk.Box):
    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.cpu_freq_entry = cpu_freq_entry

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        self.append(grid) # Append grid directly to this box

        # Input: Desired PWM Frequency
        grid.attach(Gtk.Label(label="Ønsket PWM Frekvens (Hz):", xalign=0), 0, 0, 1, 1)
        self.freq_entry = Gtk.Entry()
        self.freq_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.freq_entry.connect("changed", self.on_calculate_button_clicked)
        grid.attach(self.freq_entry, 1, 0, 1, 1)

        # Input: Duty Cycle Percentage
        grid.attach(Gtk.Label(label="Duty Cycle (%):", xalign=0), 0, 1, 1, 1)
        self.duty_cycle_entry = Gtk.Entry()
        self.duty_cycle_entry.set_placeholder_text("(0-100)")
        self.duty_cycle_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.duty_cycle_entry.connect("changed", self.on_calculate_button_clicked)
        grid.attach(self.duty_cycle_entry, 1, 1, 1, 1)

        # Output: Period
        grid.attach(Gtk.Label(label="Periode (s):", xalign=0), 0, 2, 1, 1)
        self.period_label = Gtk.Label(label="0.0 s", xalign=0)
        grid.attach(self.period_label, 1, 2, 1, 1)

        # Output: ON Time
        grid.attach(Gtk.Label(label="ON Tid (s):", xalign=0), 0, 3, 1, 1)
        self.on_time_label = Gtk.Label(label="0.0 s", xalign=0)
        grid.attach(self.on_time_label, 1, 3, 1, 1)

        # Output: OFF Time
        grid.attach(Gtk.Label(label="OFF Tid (s):", xalign=0), 0, 4, 1, 1)
        self.off_time_label = Gtk.Label(label="0.0 s", xalign=0)
        grid.attach(self.off_time_label, 1, 4, 1, 1)

        # Prescaler selection for OCRn/TOP calculation
        grid.attach(Gtk.Label(label="Prescaler for TOP/OCRn:", xalign=0), 0, 5, 1, 1)
        self.prescaler_combo = Gtk.ComboBoxText()
        for p in ["1", "8", "64", "256", "1024"]:
            self.prescaler_combo.append_text(p)
        self.prescaler_combo.set_active(0) # Default to 1
        self.prescaler_combo.connect("changed", self.on_calculate_button_clicked)
        grid.attach(self.prescaler_combo, 1, 5, 1, 1)

        # Display Global CPU Frequency used for TOP/OCRn calculations
        grid.attach(Gtk.Label(label="Global CPU Freq (Hz):", xalign=0), 0, 6, 1, 1)
        self.calc_cpu_freq_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(self.calc_cpu_freq_label, 1, 6, 1, 1)

        # Outputs for OCRn and TOP
        grid.attach(Gtk.Label(label="Foreslået TOP:", xalign=0), 0, 7, 1, 1)
        self.top_output_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(self.top_output_label, 1, 7, 1, 1)

        grid.attach(Gtk.Label(label="Foreslået OCRn:", xalign=0), 0, 8, 1, 1)
        self.ocrn_output_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(self.ocrn_output_label, 1, 8, 1, 1)

        self.message_label = Gtk.Label(label="", xalign=0)
        self.message_label.set_hexpand(True)
        grid.attach(self.message_label, 0, 9, 2, 1)

        # Connect to the main application's CPU frequency entry's changed signal
        if self.cpu_freq_entry:
            self.cpu_freq_entry.connect("changed", self.on_global_cpu_freq_changed)

        # Initial update and calculation
        self.update_cpu_freq_display()
        self.on_calculate_button_clicked(None)

    def on_global_cpu_freq_changed(self, widget):
        """
        Handles changes in the global CPU frequency entry, updates the display
        within this tab, and triggers a recalculation.
        """
        self.update_cpu_freq_display()
        self.on_calculate_button_clicked(None)

    def update_cpu_freq_display(self):
        """
        Updates the display label for the global CPU frequency.
        """
        if self.cpu_freq_entry:
            try:
                global_freq_mhz = float(self.cpu_freq_entry.get_text().replace(',', '.'))
                self.calc_cpu_freq_label.set_label(f"{global_freq_mhz * 1_000_000:.0f} Hz")
            except ValueError:
                self.calc_cpu_freq_label.set_label("Ugyldig CPU Freq")
        else:
            self.calc_cpu_freq_label.set_label("Ikke tilgængelig")

    def on_calculate_button_clicked(self, widget):
        """
        Calculates and displays the period, ON time, OFF time,
        and suggested TOP/OCRn values based on the entered parameters.
        This uses the common Fast PWM formula (OCRn + 1) / (TOP + 1).
        """
        self.message_label.set_label("") # Clear previous messages

        try:
            freq_text = self.freq_entry.get_text().replace(',', '.')
            duty_cycle_text = self.duty_cycle_entry.get_text().replace(',', '.')

            frequency = float(freq_text)
            duty_cycle_percent = float(duty_cycle_text)

            if frequency <= 0:
                self.message_label.set_label("Ønsket PWM Frekvens skal være større end 0.")
                self.period_label.set_label("Ugyldig")
                self.on_time_label.set_label("Ugyldig")
                self.off_time_label.set_label("Ugyldig")
                self.top_output_label.set_label("N/A")
                self.ocrn_output_label.set_label("N/A")
                return

            if not (0 <= duty_cycle_percent <= 100):
                self.message_label.set_label("Duty Cycle skal være mellem 0 og 100.")
                self.period_label.set_label("Ugyldig")
                self.on_time_label.set_label("Ugyldig")
                self.off_time_label.set_label("Ugyldig")
                self.top_output_label.set_label("N/A")
                self.ocrn_output_label.set_label("N/A")
                return

            # Basic Period, ON/OFF Time calculations
            period = 1 / frequency
            on_time = period * (duty_cycle_percent / 100.0)
            off_time = period - on_time

            self.period_label.set_label(f"{period:.6f} s")
            self.on_time_label.set_label(f"{on_time:.6f} s")
            self.off_time_label.set_label(f"{off_time:.6f} s")

            # OCRn/TOP Calculation
            if not self.cpu_freq_entry:
                self.message_label.set_label("Global CPU frekvens er ikke tilgængelig.")
                self.top_output_label.set_label("N/A")
                self.ocrn_output_label.set_label("N/A")
                return

            global_cpu_freq_mhz = float(self.cpu_freq_entry.get_text().replace(',', '.'))
            cpu_freq_hz = global_cpu_freq_mhz * 1_000_000

            prescaler_text = self.prescaler_combo.get_active_text()
            if not prescaler_text:
                self.message_label.set_label("Vælg venligst en prescaler.")
                self.top_output_label.set_label("N/A")
                self.ocrn_output_label.set_label("N/A")
                return
            prescaler = int(prescaler_text)

            # TOP calculation for Fast PWM (Mode 3, etc.) - non-inverted
            # $F_{PWM} = \frac{F_{CPU}}{Prescaler \cdot (TOP + 1)}$
            # $TOP = \frac{F_{CPU}}{Prescaler \cdot F_{PWM}} - 1$

            if (prescaler * frequency) == 0:
                self.message_label.set_label("Kan ikke beregne TOP/OCRn: Division med nul (Prescaler * Freq).")
                self.top_output_label.set_label("N/A")
                self.ocrn_output_label.set_label("N/A")
                return

            total_timer_ticks_float = cpu_freq_hz / (prescaler * frequency)
            top_float = total_timer_ticks_float - 1
            top_val = round(top_float)

            # Check for typical 16-bit timer range (0-65535)
            if not (0 <= top_val <= 65535):
                self.message_label.set_label(f"Advarsel: Foreslået TOP ({top_val}) er uden for det typiske 16-bit timerområde (0-65535).")

            # OCRn calculation for non-inverted output (Set on Compare Match, Clear at BOTTOM)
            # Duty Cycle = $(OCRn + 1) / (TOP + 1)$
            # $OCRn = \left(\frac{\text{Duty Cycle}}{100.0} \cdot (TOP + 1)\right) - 1$
            ocrn_float = (duty_cycle_percent / 100.0) * (top_val + 1) - 1
            ocrn_val = round(ocrn_float)

            # Adjust OCRn for boundary conditions based on common AVR behavior
            if duty_cycle_percent == 0:
                ocrn_val = -1 # A common way to indicate 0% duty cycle for some AVR modes (OCRn = bottom-1)
            elif duty_cycle_percent == 100:
                ocrn_val = top_val # For 100% duty cycle, OCRn usually equals TOP

            if not (-1 <= ocrn_val <= top_val) and top_val >= 0:
                self.message_label.set_label(f"Advarsel: Foreslået OCRn ({ocrn_val}) er uden for gyldigt område (-1 til {top_val}).")

            self.top_output_label.set_label(str(top_val))
            self.ocrn_output_label.set_label(str(ocrn_val))

        except ValueError:
            self.message_label.set_label("Indtast venligst gyldige numeriske værdier.")
            self.period_label.set_label("Ugyldig")
            self.on_time_label.set_label("Ugyldig")
            self.off_time_label.set_label("Ugyldig")
            self.top_output_label.set_label("N/A")
            self.ocrn_output_label.set_label("N/A")
        except ZeroDivisionError:
            self.message_label.set_label("Division med nul. Tjek frekvens, duty cycle eller prescaler.")
            self.period_label.set_label("Ugyldig")
            self.on_time_label.set_label("Ugyldig")
            self.off_time_label.set_label("Ugyldig")
            self.top_output_label.set_label("N/A")
            self.ocrn_output_label.set_label("N/A")
        except Exception as e:
            self.message_label.set_label(f"En ukendt fejl opstod under beregning: {e}")
            self.period_label.set_label("Ugyldig")
            self.on_time_label.set_label("Ugyldig")
            self.off_time_label.set_label("Ugyldig")
            self.top_output_label.set_label("N/A")
            self.ocrn_output_label.set_label("N/A")

# New: Duty Cycle Calculator Tab - Mode 2: TOP/OCRn -> Duty Cycle (and vice versa)
class TimerValuesToDutyCycleTab(Gtk.Box):
    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        self.append(grid)

        formula_explanation_label = Gtk.Label()
        formula_explanation_label.set_markup("<b>Duty Cycle = 1 - (OCRn / TOP)</b>")
        formula_explanation_label.set_wrap(True)
        formula_explanation_label.set_justify(Gtk.Justification.CENTER)
        grid.attach(formula_explanation_label, 0, 0, 2, 1)

        grid.attach(Gtk.Label(label="TOP Værdi:", xalign=0), 0, 1, 1, 1)
        self.top_input_entry = Gtk.Entry()
        self.top_input_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.top_input_entry.connect("changed", self.on_input_changed)
        grid.attach(self.top_input_entry, 1, 1, 1, 1)


        grid.attach(Gtk.Label(label="OCRn Værdi:", xalign=0), 0, 2, 1, 1)
        self.ocrn_input_entry = Gtk.Entry()
        self.ocrn_input_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.ocrn_input_entry.connect("changed", self.on_input_changed)
        grid.attach(self.ocrn_input_entry, 1, 2, 1, 1)

        # Input: Desired Duty Cycle (only active if OCRn is empty)
        grid.attach(Gtk.Label(label="Ønsket Duty Cycle (%):", xalign=0), 0, 3, 1, 1)
        self.desired_duty_cycle_entry = Gtk.Entry()
        self.desired_duty_cycle_entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
        self.desired_duty_cycle_entry.connect("changed", self.on_input_changed)
        grid.attach(self.desired_duty_cycle_entry, 1, 3, 1, 1)

        # Output: Calculated Duty Cycle
        grid.attach(Gtk.Label(label="Beregnet Duty Cycle (%):", xalign=0), 0, 4, 1, 1)
        self.calculated_duty_cycle_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(self.calculated_duty_cycle_label, 1, 4, 1, 1)

        # Output: Calculated OCRn
        grid.attach(Gtk.Label(label="Beregnet OCRn:", xalign=0), 0, 5, 1, 1)
        self.calculated_ocrn_label = Gtk.Label(label="N/A", xalign=0)
        grid.attach(self.calculated_ocrn_label, 1, 5, 1, 1)

        self.message_label = Gtk.Label(label="", xalign=0)
        self.message_label.set_hexpand(True)
        grid.attach(self.message_label, 0, 6, 2, 1)
        self.message_label.get_style_context().add_class("error-label")

        # Initial calculation
        self.on_input_changed(None)

    def on_input_changed(self, widget):
        """
        Triggers calculations based on which inputs are provided.
        Prioritizes TOP and OCRn for duty cycle calculation.
        If OCRn is empty, it attempts to calculate OCRn from TOP and desired duty cycle.
        Uses the formula: dutycycle = 1 - (OCRn / TOP)
        """
        self.message_label.set_label("") # Clear messages
        self.calculated_duty_cycle_label.set_label("N/A")
        self.calculated_ocrn_label.set_label("N/A")

        try:
            top_text = self.top_input_entry.get_text().replace(',', '.')
            ocrn_text = self.ocrn_input_entry.get_text().replace(',', '.')
            desired_dc_text = self.desired_duty_cycle_entry.get_text().replace(',', '.')

            if not top_text:
                self.message_label.set_label("TOP værdi skal indtastes.")
                self.ocrn_input_entry.set_sensitive(True)
                self.desired_duty_cycle_entry.set_sensitive(True)
                return

            top_val = int(float(top_text)) # Use float then int to handle decimals like "255.0"
            if top_val <= 0: # TOP must be > 0 for this formula to avoid division by zero and make sense
                self.message_label.set_label("TOP værdi skal være større end 0 for denne beregning.")
                self.ocrn_input_entry.set_sensitive(True)
                self.desired_duty_cycle_entry.set_sensitive(True)
                return

            # Case 1: Calculate Duty Cycle from TOP and OCRn
            if ocrn_text:
                ocrn_val = int(float(ocrn_text))
                if not (0 <= ocrn_val <= top_val): # OCRn typically >= 0 for this formula
                    self.message_label.set_label(f"OCRn værdi ({ocrn_val}) er uden for det gyldige område (0 til {top_val}).")
                    self.ocrn_input_entry.set_sensitive(True)
                    self.desired_duty_cycle_entry.set_sensitive(True)
                    return

                # Duty Cycle = (1 - (OCRn / TOP)) * 100
                duty_cycle = (1 - (ocrn_val / top_val)) * 100.0
                self.calculated_duty_cycle_label.set_label(f"{duty_cycle:.2f} %")
                self.desired_duty_cycle_entry.set_sensitive(False) # Disable desired duty cycle input
                self.calculated_ocrn_label.set_label("N/A") # Not calculating OCRn in this mode
                self.message_label.set_label(f"Beregner Duty Cycle fra TOP={top_val}, OCRn={ocrn_val}.")


            # Case 2: Calculate OCRn from TOP and Desired Duty Cycle
            elif desired_dc_text:
                duty_cycle_percent = float(desired_dc_text)
                if not (0 <= duty_cycle_percent <= 100):
                    self.message_label.set_label("Ønsket Duty Cycle skal være mellem 0 og 100.")
                    self.ocrn_input_entry.set_sensitive(True)
                    self.desired_duty_cycle_entry.set_sensitive(True)
                    return

                # OCRn = TOP * (1 - (Duty Cycle / 100.0))
                ocrn_float = top_val * (1 - (duty_cycle_percent / 100.0))
                ocrn_val = round(ocrn_float)

                # Ensure calculated OCRn is within valid range (0 to TOP)
                if not (0 <= ocrn_val <= top_val):
                    self.message_label.set_label(f"Advarsel: Beregnet OCRn ({ocrn_val}) er uden for det gyldige område (0 til {top_val}).")
                    # Continue to show the value but with warning

                self.calculated_ocrn_label.set_label(str(ocrn_val))
                self.ocrn_input_entry.set_sensitive(False) # Disable OCRn input
                self.calculated_duty_cycle_label.set_label("N/A") # Not calculating duty cycle in this mode
                self.message_label.set_label(f"Beregner OCRn fra TOP={top_val}, Ønsket Duty Cycle={duty_cycle_percent}%.")

            else:
                self.message_label.set_label("Indtast enten OCRn Værdi eller Ønsket Duty Cycle.")
                self.ocrn_input_entry.set_sensitive(True) # Re-enable inputs
                self.desired_duty_cycle_entry.set_sensitive(True)


        except ValueError:
            self.message_label.set_label("Indtast venligst gyldige numeriske værdier for TOP, OCRn eller Duty Cycle.")
            self.calculated_duty_cycle_label.set_label("N/A")
            self.calculated_ocrn_label.set_label("N/A")
            self.ocrn_input_entry.set_sensitive(True)
            self.desired_duty_cycle_entry.set_sensitive(True)
        except ZeroDivisionError:
            self.message_label.set_label("Division med nul. TOP værdi skal være større end 0.")
            self.calculated_duty_cycle_label.set_label("N/A")
            self.calculated_ocrn_label.set_label("N/A")
            self.ocrn_input_entry.set_sensitive(True)
            self.desired_duty_cycle_entry.set_sensitive(True)
        except Exception as e:
            self.message_label.set_label(f"En ukendt fejl opstod under beregning: {e}")
            self.calculated_duty_cycle_label.set_label("N/A")
            self.calculated_ocrn_label.set_label("N/A")
            self.ocrn_input_entry.set_sensitive(True)
            self.desired_duty_cycle_entry.set_sensitive(True)

        # After calculation, re-evaluate which inputs should be sensitive based on their content
        # This block ensures that if one field is filled, the other is disabled
        if self.ocrn_input_entry.get_text() and not self.desired_duty_cycle_entry.get_text():
            self.desired_duty_cycle_entry.set_sensitive(False)
            self.ocrn_input_entry.set_sensitive(True) # Keep active so user can modify
        elif not self.ocrn_input_entry.get_text() and self.desired_duty_cycle_entry.get_text():
            self.ocrn_input_entry.set_sensitive(False)
            self.desired_duty_cycle_entry.set_sensitive(True) # Keep active so user can modify
        else: # Both empty or both filled (ambiguous, let user clear one)
            self.ocrn_input_entry.set_sensitive(True)
            self.desired_duty_cycle_entry.set_sensitive(True)

class DutyCycleCalculatorTab(Gtk.Box):

    def __init__(self, cpu_freq_entry):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Frame for the title and switcher
        # Note: In the full app, the title and switcher are often placed
        # in a Gtk.HeaderBar or similar, but for this specific "over-tab" structure,
        # they are placed within its main Gtk.Box.
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_hexpand(True)
        header_box.set_vexpand(False)
        self.append(header_box)

        # Title Label for the Duty Cycle Calculator
        title_label = Gtk.Label(label="Duty Cycle Beregner", xalign=0)
        title_label.get_style_context().add_class("title-label")
        header_box.append(title_label)

        # Gtk.Stack to hold the different calculator modes (sub-tabs)
        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.append(self.stack) # The stack is the main content area below the header

        # Gtk.StackSwitcher to navigate between the modes in the stack
        self.stack_switcher = Gtk.StackSwitcher(stack=self.stack)
        self.stack_switcher.set_halign(Gtk.Align.CENTER)
        header_box.append(self.stack_switcher) # Add switcher to the header box

        try:

            self.pwm_freq_to_timer_tab = PWMFreqToTimerValuesTab(cpu_freq_entry)
            self.stack.add_titled(self.pwm_freq_to_timer_tab, "freq_duty_to_timer", "Frekvens/Duty Cycle til TOP/OCRn")
        except ImportError:
            fallback_label = Gtk.Label(label="Fejl: 'Frekvens/Duty Cycle til TOP/OCRn' tab kunne ikke indlæses.", wrap=True)
            self.stack.add_titled(fallback_label, "freq_duty_to_timer_fallback", "Frekvens/Duty Cycle til TOP/OCRn (Fejl)")

        # Mode 2: TOP/OCRn to Duty Cycle (and vice versa)
        try:
            self.timer_to_duty_cycle_tab = TimerValuesToDutyCycleTab(cpu_freq_entry )
            self.stack.add_titled(self.timer_to_duty_cycle_tab, "timer_to_duty_cycle", "TOP/OCRn til Duty Cycle")
        except ImportError:
            fallback_label = Gtk.Label(label="Fejl: 'TOP/OCRn til Duty Cycle' tab kunne ikke indlæses.", wrap=True)
            self.stack.add_titled(fallback_label, "timer_to_duty_cycle_fallback", "TOP/OCRn til Duty Cycle (Fejl)")


        # Apply CSS for specific elements within this tab (e.g., the title)
        css_provider = Gtk.CssProvider()
        css_data = """
        .title-label {
            font-size: 18pt;
            font-weight: bold;
            margin-bottom: 10px;
        }
        /* .error-label style is defined in the MainWindow's do_startup for global application-wide scope */
        """
        css_provider.load_from_string(css_data)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
