# adc_calcs.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class AdcCalculator:
    def __init__(self, notebook):
        self.notebook = notebook
        self._setup_adc_tab()

    def _setup_adc_tab(self):
        adc_tab = ttk.Frame(self.notebook)
        self.notebook.add(adc_tab, text="ADC Voltage")

        adc_frame = tk.LabelFrame(adc_tab, text="ADC Input Voltage Calculation", padx=10, pady=10)
        adc_frame.pack(padx=10, pady=10, fill="x")

        # ADC StringVars
        self.adc_result_voltage = tk.StringVar()

        tk.Label(adc_frame, text="ADC Value (0-1023 for 10-bit):").grid(row=0, column=0, sticky="w", pady=2)
        self.adc_adc_value_entry = tk.Entry(adc_frame)
        self.adc_adc_value_entry.insert(0, "416") # Default value from your request
        self.adc_adc_value_entry.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(adc_frame, text="ADC Reference Voltage (Vref in Volts):").grid(row=1, column=0, sticky="w", pady=2)
        self.adc_vref_entry = tk.Entry(adc_frame)
        self.adc_vref_entry.insert(0, "5.0") # Common Vref for 5V systems
        self.adc_vref_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(adc_frame, text="ADC Resolution (bits):").grid(row=2, column=0, sticky="w", pady=2)
        self.adc_resolution_entry = tk.Entry(adc_frame)
        self.adc_resolution_entry.insert(0, "10") # Default to 10-bit ADC
        self.adc_resolution_entry.grid(row=2, column=1, sticky="ew", pady=2)

        btn_calculate_adc = tk.Button(adc_frame, text="Calculate Input Voltage", command=self._calculate_adc_voltage)
        btn_calculate_adc.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Label(adc_frame, text="Input Voltage:").grid(row=4, column=0, sticky="w", pady=2)
        tk.Label(adc_frame, textvariable=self.adc_result_voltage, fg="blue", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=1, sticky="w", pady=2)

    def _calculate_adc_voltage(self):
        try:
            adc_value = int(self.adc_adc_value_entry.get())
            vref = float(self.adc_vref_entry.get())
            resolution_bits = int(self.adc_resolution_entry.get())

            if not (0 <= adc_value < (2**resolution_bits)):
                messagebox.showerror("Invalid Input", f"ADC Value must be between 0 and {2**resolution_bits - 1} for a {resolution_bits}-bit ADC.")
                self.adc_result_voltage.set("N/A")
                return

            if vref <= 0:
                messagebox.showerror("Invalid Input", "Reference Voltage (Vref) must be positive.")
                self.adc_result_voltage.set("N/A")
                return

            # For N-bit ADC, the maximum reading is 2^N - 1
            max_adc_reading = (2**resolution_bits) - 1

            # Vin = (ADCW / (2^N - 1)) * Vref
            input_voltage = (adc_value / max_adc_reading) * vref

            self.adc_result_voltage.set(f"{input_voltage:.4f} V")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for ADC Value, Reference Voltage, and Resolution.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")