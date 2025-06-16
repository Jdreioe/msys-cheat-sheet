# Standard CPU frequency
CPU_FREQ_DEFAULT = 16_000_000 # 16 MHz

# Prescaler settings for Timer0, Timer1, and Timer2
PRESCALERS_T0_T1_T2 = {
    "T0_T1": { # For Timer0 and Timer1
        "1": 0b001,   # No prescaling (clk/1)
        "8": 0b010,   # clk/8
        "64": 0b011,  # clk/64
        "256": 0b100, # clk/256
        "1024": 0b101 # clk/1024
    },
    "T2": { # For Timer2
        "1": 0b001,
        "8": 0b010,
        "32": 0b011,
        "64": 0b100,
        "128": 0b101,
        "256": 0b110,
        "1024": 0b111
    }
}

# WGM (Waveform Generation Mode) bit configurations for Timer0
# (WGM02 in TCCR0B, WGM01/WGM00 in TCCR0A)
WGM_BITS_T0 = {
    "Normal": {"WGM02": 0, "WGM01": 0, "WGM00": 0},
    "Phase Correct PWM": {"WGM02": 0, "WGM01": 0, "WGM00": 1}, # Mode 1
    "CTC": {"WGM02": 0, "WGM01": 1, "WGM00": 0},              # Mode 2
    "Fast PWM": {"WGM02": 0, "WGM01": 1, "WGM00": 1}          # Mode 3
}

# WGM (Waveform Generation Mode) bit configurations for Timer1
# (WGM13/WGM12 in TCCR1B, WGM11/WGM10 in TCCR1A)
WGM_BITS_T1 = {
    "Normal":                          {"WGM13": 0, "WGM12": 0, "WGM11": 0, "WGM10": 0, "TOP_fixed": 0xFFFF, "formula_factor": 1},
    "Phase Correct PWM (8-bit)":       {"WGM13": 0, "WGM12": 0, "WGM11": 0, "WGM10": 1, "TOP_fixed": 0x00FF, "formula_factor": 2}, # Mode 1 (TOP 0x00FF)
    "Phase Correct PWM (9-bit)":       {"WGM13": 0, "WGM12": 0, "WGM11": 1, "WGM10": 0, "TOP_fixed": 0x01FF, "formula_factor": 2}, # Mode 2 (TOP 0x01FF)
    "Phase Correct PWM (10-bit)":      {"WGM13": 0, "WGM12": 0, "WGM11": 1, "WGM10": 1, "TOP_fixed": 0x03FF, "formula_factor": 2}, # Mode 3 (TOP 0x03FF)
    "CTC (TOP=OCR1A)":                 {"WGM13": 0, "WGM12": 1, "WGM11": 0, "WGM10": 0, "TOP_variable": True, "formula_factor": 2}, # Mode 4
    "Fast PWM (8-bit)":                {"WGM13": 0, "WGM12": 1, "WGM11": 0, "WGM10": 1, "TOP_fixed": 0x00FF, "formula_factor": 1}, # Mode 5 (TOP 0x00FF)
    "Fast PWM (9-bit)":                {"WGM13": 0, "WGM12": 1, "WGM11": 1, "WGM10": 0, "TOP_fixed": 0x01FF, "formula_factor": 1}, # Mode 6 (TOP 0x01FF)
    "Fast PWM (10-bit)":               {"WGM13": 0, "WGM12": 1, "WGM11": 1, "WGM10": 1, "TOP_fixed": 0x03FF, "formula_factor": 1}, # Mode 7 (TOP 0x03FF)
    "Phase Correct PWM (TOP=ICR1)":    {"WGM13": 1, "WGM12": 0, "WGM11": 0, "WGM10": 0, "TOP_variable": True, "formula_factor": 2}, # Mode 8
    "Phase Correct PWM (TOP=OCR1A)":   {"WGM13": 1, "WGM12": 0, "WGM11": 0, "WGM10": 1, "TOP_variable": True, "formula_factor": 2}, # Mode 9
    "Fast PWM (TOP=ICR1)":             {"WGM13": 1, "WGM12": 1, "WGM11": 1, "WGM10": 0, "TOP_variable": True, "formula_factor": 1}, # Mode 14
    "Fast PWM (TOP=OCR1A)":            {"WGM13": 1, "WGM12": 1, "WGM11": 1, "WGM10": 1, "TOP_variable": True, "formula_factor": 1}  # Mode 15
}

# WGM (Waveform Generation Mode) bit configurations for Timer2
# (WGM22 in TCCR2B, WGM21/WGM20 in TCCR2A)
WGM_BITS_T2 = {
    "Normal": {"WGM22": 0, "WGM21": 0, "WGM20": 0},
    "Phase Correct PWM": {"WGM22": 0, "WGM21": 0, "WGM20": 1}, # Mode 1
    "CTC": {"WGM22": 0, "WGM21": 1, "WGM20": 0},              # Mode 2
    "Fast PWM": {"WGM22": 0, "WGM21": 1, "WGM20": 1},          # Mode 3
}

# For Timer0 (COM0A1:0, COM0B1:0)
COM_BITS_T0 = {
    "Normal port operation (OC0A/B disconnected)": {"COM0A1": 0, "COM0A0": 0, "COM0B1": 0, "COM0B0": 0},
    "Toggle OC0A/B on compare match": {"COM0A1": 0, "COM0A0": 1, "COM0B1": 0, "COM0B0": 1}, # Note: OC0B also toggles
    "Clear OC0A/B on compare match (non-inverting) - Fast PWM": {"COM0A1": 1, "COM0A0": 0, "COM0B1": 1, "COM0B0": 0},
    "Set OC0A/B on compare match (inverting) - Fast PWM": {"COM0A1": 1, "COM0A0": 1, "COM0B1": 1, "COM0B0": 1},
    "Clear OC0A/B on compare match when up-counting, Set when down-counting - Phase Correct PWM": {"COM0A1": 1, "COM0A0": 0, "COM0B1": 1, "COM0B0": 0},
    "Set OC0A/B on compare match when up-counting, Clear when down-counting - Phase Correct PWM": {"COM0A1": 1, "COM0A0": 1, "COM0B1": 1, "COM0B0": 1},
}

# For Timer1 (COM1A1:0, COM1B1:0, COM1C1:0)
COM_BITS_T1 = {
    "Normal port operation (OC1A/B/C disconnected)": {"COM1A1": 0, "COM1A0": 0, "COM1B1": 0, "COM1B0": 0, "COM1C1": 0, "COM1C0": 0},
    "Toggle OC1A/B/C on compare match": {"COM1A1": 0, "COM1A0": 1, "COM1B1": 0, "COM1B0": 1, "COM1C1": 0, "COM1C0": 1}, # Note: OC1B, OC1C also toggle
    "Clear OC1A/B/C on compare match (non-inverting) - Fast PWM": {"COM1A1": 1, "COM1A0": 0, "COM1B1": 1, "COM1B0": 0, "COM1C1": 1, "COM1C0": 0},
    "Set OC1A/B/C on compare match (inverting) - Fast PWM": {"COM1A1": 1, "COM1A0": 1, "COM1B1": 1, "COM1B0": 1, "COM1C1": 1, "COM1C0": 1},
    "Clear OC1A/B/C on compare match when up-counting, Set when down-counting - Phase Correct PWM": {"COM1A1": 1, "COM1A0": 0, "COM1B1": 1, "COM1B0": 0, "COM1C1": 1, "COM1C0": 0},
    "Set OC1A/B/C on compare match when up-counting, Clear when down-counting - Phase Correct PWM": {"COM1A1": 1, "COM1A0": 1, "COM1B1": 1, "COM1B0": 1, "COM1C1": 1, "COM1C0": 1},
}

# For Timer2 (COM2A1:0, COM2B1:0)
COM_BITS_T2 = {
    "Normal port operation (OC2A/B disconnected)": {"COM2A1": 0, "COM2A0": 0, "COM2B1": 0, "COM2B0": 0},
    "Toggle OC2A/B on compare match": {"COM2A1": 0, "COM2A0": 1, "COM2B1": 0, "COM2B0": 1}, # Note: OC2B also toggles
    "Clear OC2A/B on compare match (non-inverting) - Fast PWM": {"COM2A1": 1, "COM2A0": 0, "COM2B1": 1, "COM2B0": 0},
    "Set OC2A/B on compare match (inverting) - Fast PWM": {"COM2A1": 1, "COM2A0": 1, "COM2B1": 1, "COM2B0": 1},
    "Clear OC2A/B on compare match when up-counting, Set when down-counting - Phase Correct PWM": {"COM2A1": 1, "COM2A0": 0, "COM2B1": 1, "COM2B0": 0},
    "Set OC2A/B on compare match when up-counting, Clear when down-counting - Phase Correct PWM": {"COM2A1": 1, "COM2A0": 1, "COM2B1": 1, "COM2B0": 1},
}