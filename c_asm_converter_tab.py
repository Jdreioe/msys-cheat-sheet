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
        self.c_input_buffer.set_text("PORTC = (~PINA) + PINB;")

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
        self.asm_input_buffer.set_text("")

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

    def define_conversion_rules(self):
        # Regex-based C to ASM conversion
        self.conversion_map_c_to_asm = {
            r"(\w+)\s*=\s*(\w+);":           lambda m: f"MOV {m.group(1)}, {m.group(2)}",
            r"(\w+)\s*=\s*(\w+)\s*\+\s*(\w+);": lambda m: f"ADD {m.group(1)}, {m.group(3)}",
            r"(\w+)\s*=\s*(\w+)\s*-\s*(\w+);": lambda m: f"SUB {m.group(1)}, {m.group(3)}",
            r"(\w+)\s*=\s*(\w+)\s*&\s*(\w+);": lambda m: f"AND {m.group(1)}, {m.group(3)}",
            r"(\w+)\s*=\s*(\w+)\s*\|\s*(\w+);": lambda m: f"OR {m.group(1)}, {m.group(3)}",
            r"(\w+)\s*=\s*(\w+)\s*\^\s*(\w+);": lambda m: f"EOR {m.group(1)}, {m.group(3)}",
            r"(\w+)\s*=\s*0;":                lambda m: f"CLR {m.group(1)}",
            r"(\w+)\s*=\s*0xFF;":             lambda m: f"SER {m.group(1)}",
            r"(\w+)\s*\+\+;":                 lambda m: f"INC {m.group(1)}",
            r"(\w+)\s*=\s*\1\s*\+\s*1;":      lambda m: f"INC {m.group(1)}",
            r"(\w+)\s*--;":                   lambda m: f"DEC {m.group(1)}",
            r"(\w+)\s*=\s*\1\s*-\s*1;":       lambda m: f"DEC {m.group(1)}",
            r"(\w+)\s*=\s*\1\s*<<\s*1;":      lambda m: f"LSL {m.group(1)}",
            r"(\w+)\s*=\s*\1\s*>>\s*1;":      lambda m: f"LSR {m.group(1)}",
        }

        # Assembly to C line-by-line patterns
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
            matched = False
            for pattern, asm_code in self.conversion_map_c_to_asm.items():
                if re.fullmatch(pattern, line.strip()):
                    output.append(asm_code)
                    matched = True
                    break
            if not matched:
                output.append(f"; TODO: Konvertering for '{line.strip()}' ikke implementeret")
        self._set_text(self.asm_output_buffer, "\n".join(output))

    def convert_asm_to_c(self, button):
        code = self._get_text(self.asm_input_buffer)
        lines = code.splitlines()
        output = []

        for line in lines:
            if not line.strip():
                continue
            parts = re.split(r'\s+', line.strip(), maxsplit=1)
            instr = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ""
            args = [a.strip() for a in args.split(",") if a.strip()]

            if instr in self.conversion_map_asm_to_c:
                try:
                    c_line = self.conversion_map_asm_to_c[instr](*args)
                    output.append(c_line)
                except Exception:
                    output.append(f"// Fejl i konvertering: {line}")
            else:
                output.append(f"// Ukendt instruktion: {line}")
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

            # Simplify Rn = Rn + 1; → Rn++;
            m = re.match(r"(\w+)\s*=\s*\1\s*\+\s*1;", original_line)
            if m:
                simplified_lines.append(f"{m.group(1)}++;")
                continue

            # Simplify Rn = Rn - 1; → Rn--;
            m = re.match(r"(\w+)\s*=\s*\1\s*-\s*1;", original_line)
            if m:
                simplified_lines.append(f"{m.group(1)}--;")
                continue

            # Add more patterns here as needed...

            simplified_lines.append(original_line)  # default case

        return '\n'.join(simplified_lines)
    



