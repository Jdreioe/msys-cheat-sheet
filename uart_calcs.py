# uart_calcs.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from constants import CPU_FREQ_DEFAULT

class UartCalculator:
    def __init__(self, notebook, cpu_freq_default=CPU_FREQ_DEFAULT):
        self.notebook = notebook
        self.cpu_freq_default = cpu_freq_default
        self._setup_uart_tab()

    def _setup_uart_tab(self):
        uart_tab = ttk.Frame(self.notebook)
        self.notebook.add(uart_tab, text="UART")

        uart_frame = tk.LabelFrame(uart_tab, text="UART Baud Rate Calculation (Normal Mode)", padx=10, pady=10)
        uart_frame.pack(padx=10, pady=10, fill="x")

        # UART StringVars
        self.uart_result_ubrr = tk.StringVar()
        self.uart_result_actual_baud = tk.StringVar()
        self.uart_result_baud_error = tk.StringVar()

        tk.Label(uart_frame, text="CPU Clock Frequency (MHz):").grid(row=0, column=0, sticky="w", pady=2)
        self.uart_cpu_freq_entry = tk.Entry(uart_frame)
        self.uart_cpu_freq_entry.insert(0, str(self.cpu_freq_default / 1_000_000))
        self.uart_cpu_freq_entry.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(uart_frame, text="Desired Baud Rate (bps):").grid(row=1, column=0, sticky="w", pady=2)
        self.uart_desired_baud_entry = tk.Entry(uart_frame)
        uart_desired_baud_rate_default = 9600
        self.uart_desired_baud_entry.insert(0, str(uart_desired_baud_rate_default))
        self.uart_desired_baud_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(uart_frame, text="Note: Assumes U2Xn bit is 0 (Normal Mode).").grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        btn_calculate_uart = tk.Button(uart_frame, text="Calculate Baud Rate Settings", command=self._calculate_uart)
        btn_calculate_uart.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Label(uart_frame, text="UBRRn Value (approx.):").grid(row=4, column=0, sticky="w", pady=2)
        tk.Label(uart_frame, textvariable=self.uart_result_ubrr, fg="blue").grid(row=4, column=1, sticky="w", pady=2)

        tk.Label(uart_frame, text="Actual Baud Rate:").grid(row=5, column=0, sticky="w", pady=2)
        tk.Label(uart_frame, textvariable=self.uart_result_actual_baud, fg="green").grid(row=5, column=1, sticky="w", pady=2)

        tk.Label(uart_frame, text="Baud Rate Error:").grid(row=6, column=0, sticky="w", pady=2)
        tk.Label(uart_frame, textvariable=self.uart_result_baud_error, fg="red").grid(row=6, column=1, sticky="w", pady=2)

    def _calculate_ubrr(self, cpu_freq_hz, desired_baud_rate):
        """Calculates UBRRn, actual baud rate, and error for UART."""
        ubrr_float = (cpu_freq_hz / (16 * desired_baud_rate)) - 1

        if ubrr_float < 0:
            return None, None, None # Indicate error if result is negative

        ubrr_int = round(ubrr_float)
        actual_baud_rate = cpu_freq_hz / (16 * (ubrr_int + 1))
        error_percent = ((actual_baud_rate - desired_baud_rate) / desired_baud_rate) * 100

        return ubrr_int, actual_baud_rate, error_percent

    def _calculate_uart(self):
        try:
            cpu_freq_mhz = float(self.uart_cpu_freq_entry.get())
            desired_baud_rate = float(self.uart_desired_baud_entry.get())

            cpu_freq_hz = cpu_freq_mhz * 1_000_000

            ubrr_int, actual_baud_rate, error_percent = self._calculate_ubrr(cpu_freq_hz, desired_baud_rate)

            if ubrr_int is None:
                messagebox.showerror("Error", "Desired Baud Rate is too high for the given CPU Frequency, or other issue.")
                self.uart_result_ubrr.set("N/A")
                self.uart_result_actual_baud.set("N/A")
                self.uart_result_baud_error.set("N/A")
                return

            self.uart_result_ubrr.set(f"{ubrr_int}")
            self.uart_result_actual_baud.set(f"{actual_baud_rate:.2f} Hz")
            self.uart_result_baud_error.set(f"{error_percent:.2f}%")

            if abs(error_percent) > 2: # Common tolerance for UART baud rates
                messagebox.showwarning("Baud Rate Warning",
                                       f"The calculated baud rate error is {error_percent:.2f}%.\n"
                                       "This might be too high for reliable communication.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for CPU Frequency and Desired Baud Rate.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")