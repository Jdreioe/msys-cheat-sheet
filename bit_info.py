import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

class BitManipulationInfoTab(Gtk.ScrolledWindow):
    def __init__(self):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_buffer = self.text_view.get_buffer()

        self.bold_tag = self.text_buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.monospace_tag = self.text_buffer.create_tag("monospace", family="monospace")
        self.heading_tag = self.text_buffer.create_tag("heading", weight=Pango.Weight.BOLD, size_points=14)

        self.set_child(self.text_view)
        self._populate_content()

    def append_text_with_tags(self, text_segment, bold_keywords=[], monospace_segments=[], is_heading=False):
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, text_segment)
        end_iter = self.text_buffer.get_end_iter()

        if is_heading:
            self.text_buffer.apply_tag(self.heading_tag, start_iter, end_iter)

        for keyword in bold_keywords:
            search_start_iter = self.text_buffer.get_iter_at_offset(start_iter.get_offset())
            while True:
                found_tuple = search_start_iter.forward_search(keyword, 0, end_iter)
                if found_tuple:
                    found, match_start, match_end = found_tuple
                    if found and match_start.get_offset() < end_iter.get_offset():
                        self.text_buffer.apply_tag(self.bold_tag, match_start, match_end)
                        search_start_iter = match_end.copy()
                    else:
                        break
                else:
                    break

        for mono_segment in monospace_segments:
            search_start_iter = self.text_buffer.get_iter_at_offset(start_iter.get_offset())
            while True:
                found_tuple = search_start_iter.forward_search(mono_segment, 0, end_iter)
                if found_tuple:
                    found, match_start, match_end = found_tuple
                    if found and match_start.get_offset() < end_iter.get_offset():
                        self.text_buffer.apply_tag(self.monospace_tag, match_start, match_end)
                        search_start_iter = match_end.copy()
                    else:
                        break
                else:
                    break
        self.text_buffer.insert(self.text_buffer.get_end_iter(), "\n")

    def _populate_content(self):
        self.text_buffer.set_text("")
        self.append_text_with_tags(
            "Hvordan man Sætter Bits i Timere (f.eks. WGM, CS)\n",
            is_heading=True
        )
        self.append_text_with_tags(
            "Registerkonfiguration i AVR er primært baseret på bitmanipulation.\n"
            "Du bruger bitvise operatorer til at sætte, cleare eller læse individuelle bits uden at påvirke andre bits i registret.\n\n"
            "Generelle Bitvise Operatorer:\n",
            bold_keywords=["bitmanipulation", "bitvise operatorer", "Generelle Bitvise Operatorer"]
        )
        self.append_text_with_tags(
            "* Sæt en bit: `REGISTER |= (1 << BIT_NUMMER);`\n"
            "  * Eksempel: `TCCR0A |= (1 << WGM01);` (Sætter WGM01-biten i TCCR0A)\n",
            bold_keywords=["Sæt en bit", "Eksempel"],
            monospace_segments=["`REGISTER |= (1 << BIT_NUMMER);`", "`TCCR0A |= (1 << WGM01);`"]
        )
        
        self.append_text_with_tags(
            "* Binær alternativ til at sætte specifikke bits:\n"
            "  I stedet for at bruge bit-shift (`1 << BIT_NUMMER`), kan du direkte skrive den binære værdi til registret, hvis du ønsker at sætte alle bits på én gang eller et kendt mønster.\n"
            "  Dette er ofte mindre fleksibelt, hvis du kun vil ændre en enkelt bit uden at påvirke andre, men kan være klarere for komplette registerindstillinger.\n"
            "  * Eksempel (sæt TOIE0 i TIMSK0, hvor TOIE0 er bit 0):\n"
            "    `TIMSK0 = 0b00000001; // Sætter kun TOIE0 (bit 0) og cleares alle andre.`\n"
            "    `// Eller hvis du vil bevare andre bits og kun sætte TOIE0:`\n"
            "    `TIMSK0 = TIMSK0 | 0b00000001;`\n"
            "    `// Dette svarer til TIMSK0 |= (1 << TOIE0); hvis TOIE0 er 0.`\n"
            "  * Eksempel (sæt prescaler til clk/64, WGM01=1, WGM00=1 for Fast PWM i TCCR0A):\n"
            "    `TCCR0A = 0b01000011; // COM0A1=1, WGM01=1, WGM00=1 for Fast PWM på OC0A`\n"
            "    `TCCR0B = 0b00000011; // CS01=1, CS00=1 for clk/64 prescaler`\n\n",
            bold_keywords=["Binær alternativ", "bit-shift", "binære værdi", "komplette registerindstillinger", "Eksempel"],
            monospace_segments=[
                "`TIMSK0 = 0b00000001;`", "`// Sætter kun TOIE0 (bit 0) og cleares alle andre.`",
                "`TIMSK0 = TIMSK0 | 0b00000001;`", "`// Dette svarer til TIMSK0 |= (1 << TOIE0); hvis TOIE0 er 0.`",
                "`TCCR0A = 0b01000011;`", "`TCCR0B = 0b00000011;`"
            ]
        )
        
        self.append_text_with_tags(
            "* Clear en bit: `REGISTER &= ~(1 << BIT_NUMMER);`\n"
            "  * Eksempel: `TCCR0B &= ~(1 << WGM02);` (Cleares WGM02-biten i TCCR0B)\n",
            bold_keywords=["Clear en bit", "Eksempel"],
            monospace_segments=["`REGISTER &= ~(1 << BIT_NUMMER);`", "`TCCR0B &= ~(1 << WGM02);`"]
        )
        self.append_text_with_tags(
            "* Clear flere bits (f.eks. prescaler): `REGISTER &= ~((1 << BIT0) | (1 << BIT1) | ...);`\n"
            "  * Eksempel (clear CS02, CS01, CS00): `TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00));`\n",
            bold_keywords=["Clear flere bits", "prescaler", "Eksempel"],
            monospace_segments=["`REGISTER &= ~((1 << BIT0) | (1 << BIT1) | ...);`", "`TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00));`"]
        )
        self.append_text_with_tags(
            "* Sæt flere bits (prescaler): Først clear, så sæt de nye bits.\n"
            "  * Eksempel (sæt til clk/64):\n",
            bold_keywords=["Sæt flere bits", "prescaler", "Eksempel"]
        )
        self.append_text_with_tags(
            "    `TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00)); // Clear eksisterende prescaler bits`\n"
            "    `TCCR0B |= (1 << CS01) | (1 << CS00);                   // Sæt nye bits for clk/64 (0b011)`\n\n",
            monospace_segments=[
                "`TCCR0B &= ~((1 << CS02) | (1 << CS01) | (1 << CS00)); // Clear eksisterende prescaler bits`",
                "`TCCR0B |= (1 << CS01) | (1 << CS00);                   // Sæt nye bits for clk/64 (0b011)`"
            ]
        )
        self.append_text_with_tags(
            "Vigtige Bit Grupper:\n",
            bold_keywords=["Vigtige Bit Grupper"]
        )
        self.append_text_with_tags(
            "* WGM bits: Styrer Waveform Generation Mode (WGMx0, WGMx1, WGMx2, WGMx3).\n"
            "* COM bits (Compare Output Mode): Styrer output på OCx pins (COMx1, COMx0). Bruges i PWM tilstande.\n"
            "* CS bits (Clock Select): Styrer prescaler og timer start/stop (CSx2, CSx1, CSx0).\n",
            bold_keywords=["WGM bits", "Waveform Generation Mode", "WGMx0", "WGMx1", "WGMx2", "WGMx3", "COM bits (Compare Output Mode)", "OCx", "COMx1", "COMx0", "PWM", "CS bits (Clock Select)", "CSx2", "CSx1", "CSx0"]
        )