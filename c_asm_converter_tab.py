import gi
import re
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

class CAsmConverterTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.init_ui()
        self.define_conversion_rules()

    def init_ui(self):
        # --- C to ASM ---
        c_frame = Gtk.Frame(label="C til Assembly")
        c_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        c_frame.set_child(c_box)

        c_box.append(Gtk.Label(label="C-kode:", xalign=0))

        self.c_input = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        self.c_input_buffer = self.c_input.get_buffer()
        # Updated initial text to include generalized examples and lowercase inputs
        self.c_input_buffer.set_text(
            "portb = pina + 117;\n" # Example causing the error
            "my_reg = count - 50;\n"
            "ddrc = pinc & 0b11110000;\n" # Lowercase DDR/PIN example
            "status = sreg | 0x80;\n" # Lowercase SREG example
            "DDRB = 0xFF;\n"
            "PORTA |= (1 << PA0);\n"
            "PORTC &= ~(1 << PC7);\n"
            "my_var = PIND;\n"
            "PORTB = var2;\n"
            "status_reg = _SFR_IO8(0x3F);\n"
            "asm(\"nop\");"
        )

        c_scroll = Gtk.ScrolledWindow()
        c_scroll.set_child(self.c_input)
        c_scroll.set_min_content_height(100)
        c_box.append(c_scroll)

        btn_c_to_asm = Gtk.Button(label="Konverter C til ASM")
        btn_c_to_asm.connect("clicked", self.convert_c_to_asm)
        c_box.append(btn_c_to_asm)

        c_box.append(Gtk.Label(label="Assembly-output:", xalign=0))

        self.asm_output = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.WORD)
        self.asm_output_buffer = self.asm_output.get_buffer()

        asm_scroll = Gtk.ScrolledWindow()
        asm_scroll.set_child(self.asm_output)
        asm_scroll.set_min_content_height(100)
        c_box.append(asm_scroll)

        self.append(c_frame)
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        self.simplify_button = Gtk.Button(label="Forenkle C-kode")
        self.simplify_button.connect("clicked", self.simplify_code)
        c_box.append(self.simplify_button)

        # --- ASM to C ---
        asm_frame = Gtk.Frame(label="Assembly til C")
        asm_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        asm_frame.set_child(asm_box)

        asm_box.append(Gtk.Label(label="Assembly-kode:", xalign=0))

        self.asm_input = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD)
        self.asm_input_buffer = self.asm_input.get_buffer()
        # Initial text for ASM to C examples (no changes for this request)
        self.asm_input_buffer.set_text(
            "LDI R16, 0x0F\n"
            "ORI R17, 0x80\n"
            "ANDI R18, 0x01\n"
            "SBI PORTB, PB0\n"
            "CBI PORTD, PD7\n"
            "NOP\n"
            "IN R20, PINC\n"
            "OUT PORTA, R21\n"
            "IN R22, 0x3F"
        )

        asm_input_scroll = Gtk.ScrolledWindow()
        asm_input_scroll.set_child(self.asm_input)
        asm_input_scroll.set_min_content_height(100)
        asm_box.append(asm_input_scroll)

        btn_asm_to_c = Gtk.Button(label="Konverter ASM til C")
        btn_asm_to_c.connect("clicked", self.convert_asm_to_c)
        asm_box.append(btn_asm_to_c)

        asm_box.append(Gtk.Label(label="C-output:", xalign=0))

        self.c_output = Gtk.TextView(editable=False, wrap_mode=Gtk.WrapMode.WORD)
        self.c_output_buffer = self.c_output.get_buffer()

        c_out_scroll = Gtk.ScrolledWindow()
        c_out_scroll.set_child(self.c_output)
        c_out_scroll.set_min_content_height(100)
        asm_box.append(c_out_scroll)

        self.append(asm_frame)

    # --- Helper methods for generating multi-line Assembly ---
    def _get_arith_op_instr(self, op_symbol, reg1, reg2):
        # Helper to map C operator to ASM instruction
        if op_symbol == '+': return f"ADD {reg1}, {reg2}"
        if op_symbol == '-': return f"SUB {reg1}, {reg2}"
        if op_symbol == '&': return f"AND {reg1}, {reg2}"
        if op_symbol == '|': return f"OR {reg1}, {reg2}"
        if op_symbol == '^': return f"EOR {reg1}, {reg2}"
        return f"; UNKNOWN_OP {op_symbol}" # Fallback for unhandled operators

    def _handle_pin_op_const(self, m):
        # Handles patterns like: destination = PINx OP Constant;
        # Example: PORTB = PINA + 117; or portb = pina + 117;
        dest = m.group(1).upper() # Convert destination to uppercase
        pin_source = f"PIN{m.group(2).upper()}" # Convert PINx to uppercase
        op = m.group(3)
        constant = m.group(4)
        asm = []

        # Read PINx into R24
        asm.append(f"IN R24, {pin_source}")
        # Load constant into R25
        asm.append(f"LDI R25, {constant}")
        # Perform arithmetic/logic operation, result in R24
        asm.append(self._get_arith_op_instr(op, "R24", "R25"))
        
        # Write result to destination (PORT, DDR, SREG or general register)
        if re.fullmatch(r"PORT\w+|DDR\w+|SREG", dest, re.I): # Check for PORT, DDR, SREG case-insensitively
            asm.append(f"OUT {dest}, R24")
        else:
            asm.append(f"MOV {dest}, R24")
        return "\n".join(asm)

    def _handle_reg_op_const(self, m):
        # Handles patterns like: destination = register OP Constant;
        # Example: my_reg = count - 50; or status = sreg | 0x80;
        dest = m.group(1).upper() # Convert destination to uppercase
        reg_source = m.group(2).upper() # Convert source register to uppercase
        op = m.group(3)
        constant = m.group(4)
        asm = []
        
        # Load source register into R24
        asm.append(f"MOV R24, {reg_source}") 
        
        # Handle immediate operations (ANDI, ORI) if possible, otherwise LDI + generic op
        if op == '&':
            asm.append(f"ANDI R24, {constant}")
        elif op == '|':
            asm.append(f"ORI R24, {constant}")
        else: # For ADD, SUB, EOR with constant, need to LDI to another register
            asm.append(f"LDI R25, {constant}")
            asm.append(self._get_arith_op_instr(op, "R24", "R25"))
            
        # Write result to destination (PORT, DDR, SREG or general register)
        if re.fullmatch(r"PORT\w+|DDR\w+|SREG", dest, re.I): # Check for PORT, DDR, SREG case-insensitively
            asm.append(f"OUT {dest}, R24")
        else:
            asm.append(f"MOV {dest}, R24")
        return "\n".join(asm)


    def define_conversion_rules(self):
        # Define complex, multi-line C-to-ASM conversion rules.
        # These are processed first by convert_c_to_asm.
        # Added re.I (re.IGNORECASE) flag to all patterns where case might vary.
        # Also added DDRx and SREG to output destination checks in handlers.
        self.complex_c_to_asm_rules = [
            # C: Destination = PINx Operator Constant; (e.g., PORTB = PINA + 117;)
            (r"(\w+)\s*=\s*PIN(\w+)\s*([\+\-\&\|\^])\s*(0x[0-9a-fA-F]+|[0-9]+);", self._handle_pin_op_const, re.I),
            # C: Destination = Register Operator Constant; (e.g., my_reg = count - 50;)
            (r"(\w+)\s*=\s*(\w+)\s*([\+\-\&\|\^])\s*(0x[0-9a-fA-F]+|[0-9]+);", self._handle_reg_op_const, re.I),
            # Add more complex patterns here later if needed
        ]

        # Define simple, single-line C-to-ASM conversion rules.
        # These are processed if no complex rules match.
        # Order matters: more specific patterns must come before more general ones.
        # Added .upper() to all generated register/port/pin names for consistent ASM output.
        self.conversion_map_c_to_asm = {
            # Specific assignments/operations:
            r"(\w+)\s*=\s*(0x[0-9a-fA-F]+|[0-9]+);": lambda m: f"LDI {m.group(1).upper()}, {m.group(2)}",
            r"(\w+)\s*\|\=\s*\(1\s*<<\s*(\w+)\);":    lambda m: f"SBI {m.group(1).upper()}, {m.group(2).upper()}",
            r"(\w+)\s*&\=\s*~\(1\s*<<\s*(\w+)\);":   lambda m: f"CBI {m.group(1).upper()}, {m.group(2).upper()}",
            r"asm\(\"nop\"\);":                       lambda m: "NOP",
            r"(\w+)\s*=\s*_SFR_IO8\((0x[0-9a-fA-F]+)\);": lambda m: f"IN {m.group(1).upper()}, {m.group(2)}",

            # General IN/OUT rules:
            r"(\w+)\s*=\s*PIN(\w+);":                 lambda m: f"IN {m.group(1).upper()}, PIN{m.group(2).upper()}",
            r"PORT(\w+)\s*=\s*(\w+);":                lambda m: f"OUT PORT{m.group(1).upper()}, {m.group(2).upper()}",

            # Original general rules for register-to-register or direct ops:
            r"(\w+)\s*=\s*(\w+);":                   lambda m: f"MOV {m.group(1).upper()}, {m.group(2).upper()}",
            r"(\w+)\s*=\s*(\w+)\s*\+\s*(\w+);":       lambda m: f"ADD {m.group(1).upper()}, {m.group(3).upper()}",
            r"(\w+)\s*=\s*(\w+)\s*-\s*(\w+);":       lambda m: f"SUB {m.group(1).upper()}, {m.group(3).upper()}",
            r"(\w+)\s*=\s*(\w+)\s*&\s*(\w+);":       lambda m: f"AND {m.group(1).upper()}, {m.group(3).upper()}",
            r"(\w+)\s*=\s*(\w+)\s*\|\s*(\w+);":       lambda m: f"OR {m.group(1).upper()}, {m.group(3).upper()}",
            r"(\w+)\s*=\s*(\w+)\s*\^\s*(\w+);":       lambda m: f"EOR {m.group(1).upper()}, {m.group(3).upper()}",
            r"(\w+)\s*=\s*0;":                        lambda m: f"CLR {m.group(1).upper()}",
            r"(\w+)\s*=\s*0xFF;":                     lambda m: f"SER {m.group(1).upper()}",
            r"(\w+)\s*\+\+;":                         lambda m: f"INC {m.group(1).upper()}",
            r"(\w+)\s*=\s*\1\s*\+\s*1;":              lambda m: f"INC {m.group(1).upper()}",
            r"(\w+)\s*--;":                           lambda m: f"DEC {m.group(1).upper()}",
            r"(\w+)\s*=\s*\1\s*-\s*1;":               lambda m: f"DEC {m.group(1).upper()}",
            r"(\w+)\s*=\s*\1\s*<<\s*1;":              lambda m: f"LSL {m.group(1).upper()}",
            r"(\w+)\s*=\s*\1\s*>>\s*1;":              lambda m: f"LSR {m.group(1).upper()}",
            r"(\w+)\s*=\s*~(\w+);":                   lambda m: f"COM {m.group(1).upper()}",
        }

        # Assembly to C line-by-line patterns (no changes here as they don't involve case-sensitive regex for instructions)
        self.conversion_map_asm_to_c = {
            "IN":     lambda reg, port: f"{reg} = {port};",
            "OUT":    lambda port, reg: f"{port} = {reg};",
            "COM":    lambda reg: f"{reg} = ~{reg};",
            "ADD":    lambda r1, r2: f"{r1} = {r1} + {r2};",
            "SUB":    lambda r1, r2: f"{r1} = {r1} - {r2};",
            "AND":    lambda r1, r2: f"{r1} = {r1} & {r2};",
            "OR":     lambda r1, r2: f"{r1} = {r1} | {r2};",
            "EOR":    lambda r1, r2: f"{r1} = {r1} ^ {r2};",
            "MOV":    lambda r1, r2: f"{r1} = {r2};",
            "LSL":    lambda r1: f"{r1} = {r1} << 1;",
            "LSR":    lambda r1: f"{r1} = {r1} >> 1;",
            "CLR":    lambda r1: f"{r1} = 0;",
            "SER":    lambda r1: f"{r1} = 0xFF;",
            "INC":    lambda r1: f"{r1}++;",
            "DEC":    lambda r1: f"{r1}--;",
            "LDI":    lambda r1, val: f"{r1} = {val};",
            "ORI":    lambda r1, val: f"{r1} = {r1} | {val};",
            "ANDI":   lambda r1, val: f"{r1} = {r1} & {val};",
            "SBI":    lambda port, bit: f"{port} |= (1 << {bit});",
            "CBI":    lambda port, bit: f"{port} &= ~(1 << {bit});",
            "NOP":    lambda: "asm(\"nop\");",
        }

    def _get_text(self, buffer):
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        return buffer.get_text(start, end, True).strip()

    def _set_text(self, buffer, text):
        buffer.set_text(text)

    def convert_c_to_asm(self, button):
        code = self._get_text(self.c_input_buffer)
        lines = code.splitlines()
        output = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            matched = False
            # 1. Try to match against complex multi-line rules first (with case-insensitivity)
            for pattern, handler_func, flags in self.complex_c_to_asm_rules:
                m = re.fullmatch(pattern, line, flags)
                if m:
                    try:
                        # Corrected call: handler_func is already bound to 'self', so only pass 'm'
                        asm_output_line = handler_func(m) 
                        output.append(asm_output_line)
                        matched = True
                        break
                    except Exception as e:
                        output.append(f"; ERROR: Failed to convert (complex rule) '{line}' - {e}")
                        matched = True
                        break

            if matched:
                continue

            # 2. If not matched by complex rules, try simple single-line rules (with case-insensitivity)
            for pattern, asm_code_func in self.conversion_map_c_to_asm.items():
                m = re.fullmatch(pattern, line, re.I) # Apply IGNORECASE to simple rules
                if m:
                    try:
                        if asm_code_func.__code__.co_argcount == 1:
                            asm_output_line = asm_code_func(m)
                        else:
                            asm_output_line = asm_code_func()
                        output.append(asm_output_line)
                        matched = True
                        break
                    except Exception as e:
                        output.append(f"; ERROR: Failed to convert (simple rule) '{line}' - {e}")
                        matched = True
                        break
            if not matched:
                output.append(f"; TODO: Konvertering for '{line}' ikke implementeret")
        self._set_text(self.asm_output_buffer, "\n".join(output))

    def convert_asm_to_c(self, button):
        code = self._get_text(self.asm_input_buffer)
        lines = code.splitlines()
        output = []

        for line in lines:
            if not line.strip():
                continue
            line_no_comment = line.split(';', 1)[0].strip()
            if not line_no_comment:
                output.append(f"// {line.strip()}")
                continue

            parts = re.split(r'\s+', line_no_comment, maxsplit=1)
            instr = parts[0].upper()
            args_str = parts[1] if len(parts) > 1 else ""
            args = [a.strip() for a in args_str.split(",") if a.strip()]

            if instr in self.conversion_map_asm_to_c:
                try:
                    c_line = self.conversion_map_asm_to_c[instr](*args)
                    output.append(c_line)
                except TypeError:
                    if instr == "NOP" and not args:
                        output.append(self.conversion_map_asm_to_c[instr]())
                    else:
                        output.append(f"// Fejl: Argument mismatch for '{line}'")
                except Exception as e:
                    output.append(f"// Fejl i konvertering for '{line}': {e}")
            else:
                output.append(f"// Ukjent instruktion: {line}")
        self._set_text(self.c_output_buffer, "\n".join(output))

    def simplify_code(self, button):
        code = self._get_text(self.c_input_buffer)
        simplified_code = re.sub(r'\s*=\s*0xFF\s*;', ' = 0;', code)
        simplified_code = re.sub(r'\s*=\s*0\s*;', ' = 0xFF;', simplified_code)
        self._set_text(self.c_input_buffer, simplified_code)
        self.convert_c_to_asm(button)

    def simplify_c_code(self, code):
        lines = code.strip().split('\n')
        simplified_lines = []
        for line in lines:
            original_line = line.strip()

            m = re.match(r"(\w+)\s*=\s*\1\s*\+\s*1;", original_line)
            if m:
                simplified_lines.append(f"{m.group(1)}++;")
                continue

            m = re.match(r"(\w+)\s*=\s*\1\s*-\s*1;", original_line)
            if m:
                simplified_lines.append(f"{m.group(1)}--;")
                continue

            simplified_lines.append(original_line)

        return '\n'.join(simplified_lines)