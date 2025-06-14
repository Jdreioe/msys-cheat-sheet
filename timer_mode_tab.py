import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

class TimerModesInfoTab(Gtk.ScrolledWindow):
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
        self.sub_heading_tag = self.text_buffer.create_tag("sub_heading", weight=Pango.Weight.BOLD)

        self.set_child(self.text_view)
        self._populate_content()

    def append_text_with_tags(self, text_segment, bold_keywords=[], monospace_segments=[], is_heading=False, is_sub_heading=False):
        start_iter = self.text_buffer.get_end_iter()
        self.text_buffer.insert(start_iter, text_segment)
        end_iter = self.text_buffer.get_end_iter()

        if is_heading:
            self.text_buffer.apply_tag(self.heading_tag, start_iter, end_iter)
        elif is_sub_heading:
            self.text_buffer.apply_tag(self.sub_heading_tag, start_iter, end_iter)

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
            "Konfiguration af Timer Tilstande (WGM)\n",
            is_heading=True
        )
        self.append_text_with_tags(
            "Waveform Generation Mode (WGM) bits bestemmer timerens funktionalitet (Normal, CTC, PWM, Fast PWM, Phase Correct PWM). Disse bits findes i TCCRxA og TCCRxB registre.\n\n"
            "Generel Struktur af WGM Bits:\n",
            bold_keywords=["Waveform Generation Mode (WGM)", "Normal", "CTC", "PWM", "Fast PWM", "Phase Correct PWM", "TCCRxA", "TCCRxB", "Generel Struktur af WGM Bits"]
        )
        self.append_text_with_tags(
            "* Timer0/Timer2 (8-bit): WGMx2 (TCCRxB), WGMx1, WGMx0 (TCCRxA)\n"
            "* Timer1 (16-bit): WGMx3, WGMx2 (TCCRxB), WGMx1, WGMx0 (TCCRxA)\n\n"
            "Fremgangsmåde:\n",
            bold_keywords=["Timer0", "Timer2", "Timer1", "WGMx2", "WGMx1", "WGMx0", "WGMx3", "TCCRxB", "TCCRxA", "Fremgangsmåde"]
        )
        self.append_text_with_tags(
            "1. Sæt WGM-bits: Se databladet for de specifikke bitkombinationer for hver tilstand. Vores 'constants.py' fil indeholder også disse informationer.\n"
            "2. Sæt Prescaler: Vælg en prescaler via Clock Select (CS) bits i TCCRxB for at styre timerens hastighed.\n"
            "3. Sæt TOP-værdi (hvis relevant): I CTC og PWM tilstande skal en TOP-værdi defineres. Dette kan være et fast tal (f.eks. 0xFF for 8-bit timere), OCRxA/ICRx, eller programmeres via TCNTx.\n\n",
            bold_keywords=["Sæt WGM-bits", "Sæt Prescaler", "Clock Select (CS)", "TCCRxB", "Sæt TOP-værdi", "CTC", "PWM", "OCRxA/ICRx", "TCNTx"]
        )

        # Mode A: Normal Mode
        self.append_text_with_tags(
            "A. Normal Mode:\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til MAX (`0xFF` for 8-bit, `0xFFFF` for 16-bit) og starter forfra.\n"
            "* WGM-bits: `0b000` (alle 0).\n"
            "* Frekvens (Overflow): `F_CPU / (Prescaler * (MAX_VALUE + 1))`\n",
            bold_keywords=["MAX", "0xFF", "0xFFFF", "Frekvens (Overflow)"],
            monospace_segments=["`0b000`", "`F_CPU / (Prescaler * (MAX_VALUE + 1))`"]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 Normal Mode):\n",
            bold_keywords=["Eksempel (Timer0 Normal Mode)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = 0x00; // WGM01=0, WGM00=0`\n"
            "`TCCR0B = 0x00; // WGM02=0`\n"
            "`// Optional: TCNT0 = 0; // Nulstil tæller`\n"
            "`// Indstil prescaler, f.eks. clk/1024 (CS02=1, CS01=0, CS00=1 -> 0b101)`\n"
            "`TCCR0B |= (1 << CS02) | (1 << CS00);`\n\n",
            monospace_segments=[
                "`TCCR0A = 0x00; // WGM01=0, WGM00=0`",
                "`TCCR0B = 0x00; // WGM02=0`",
                "`// Optional: TCNT0 = 0; // Nulstil tæller`",
                "`// Indstil prescaler, f.eks. clk/1024 (CS02=1, CS01=0, CS00=1 -> 0b101)`",
                "`TCCR0B |= (1 << CS02) | (1 << CS00);`"
            ]
        )

        # Mode B: CTC Mode
        self.append_text_with_tags(
            "B. CTC Mode (Clear Timer on Compare Match):\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til en defineret TOP-værdi (f.eks. OCRxA), hvorefter den nulstilles.\n"
            "* Frekvens (OCF-flag/toggle): `F_CPU / (2 * Prescaler * (TOP + 1))`\n"
            "* WGM-bits: `0b010` (WGMx2=0, WGMx1=1, WGMx0=0)\n",
            bold_keywords=["TOP-værdi", "OCRxA", "Frekvens (OCF-flag/toggle)"],
            monospace_segments=["`F_CPU / (2 * Prescaler * (TOP + 1))`", "`0b010`"]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 CTC Mode, TOP=OCR0A):\n",
            bold_keywords=["Eksempel (Timer0 CTC Mode, TOP=OCR0A)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = (1 << WGM01); // WGM01=1, WGM00=0`\n"
            "`TCCR0B = 0x00;         // WGM02=0`\n"
            "`OCR0A = 124;           // Sæt TOP-værdi for 1ms med 16MHz/1024`\n"
            "`// Indstil prescaler, f.eks. clk/1024`\n"
            "`TCCR0B |= (1 << CS02) | (1 << CS00);`\n"
            "`// Aktiver interrupt (valgfrit)`\n"
            "`TIMSK0 |= (1 << OCIE0A);`\n\n",
            monospace_segments=[
                "`TCCR0A = (1 << WGM01); // WGM01=1, WGM00=0`",
                "`TCCR0B = 0x00;         // WGM02=0`",
                "`OCR0A = 124;           // Sæt TOP-værdi for 1ms med 16MHz/1024`",
                "`// Indstil prescaler, f. एग्जांपल clk/1024`",
                "`TCCR0B |= (1 << CS02) | (1 << CS00);`",
                "`// Aktiver interrupt (valgfrit)`",
                "`TIMSK0 |= (1 << OCIE0A);`"
            ]
        )

        # Mode C: Fast PWM Mode
        self.append_text_with_tags(
            "C. Fast PWM Mode:\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til TOP (`0xFF` for 8-bit, eller OCRx/ICRx for 16-bit), tæller hurtigt op.\n"
            "* Duty Cycle styres af OCRxB (eller OCRxA for Timer0/2).\n"
            "* Frekvens: `F_CPU / (Prescaler * (TOP + 1))`\n"
            "* WGM-bits for Timer0/2: `0b011` (WGMx2=0, WGMx1=1, WGMx0=1)\n"
            "* WGM-bits for Timer1 (TOP=0x03FF): `0b0111` (WGM13=0, WGM12=1, WGM11=1, WGM10=1)\n",
            bold_keywords=["TOP", "0xFF", "OCRx/ICRx", "Duty Cycle", "OCRxB", "OCRxA", "Frekvens"],
            monospace_segments=[
                "`F_CPU / (Prescaler * (TOP + 1))`", "`0b011`",
                "`0b0111`"
            ]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 Fast PWM, Non-Inverting på OC0A):\n",
            bold_keywords=["Eksempel (Timer0 Fast PWM, Non-Inverting på OC0A)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = (1 << COM0A1) | (1 << WGM01) | (1 << WGM00); // Non-inv, WGM01=1, WGM00=1`\n"
            "`TCCR0B = 0x00; // WGM02=0`\n"
            "`OCR0A = 127;   // 50% duty cycle (127/255)`\n"
            "`// Indstil prescaler, f.eks. clk/64`\n"
            "`TCCR0B |= (1 << CS01) | (1 << CS00);`\n"
            "`// DDRD |= (1 << PD6); // Sæt OC0A (PD6) som output`\n\n",
            monospace_segments=[
                "`TCCR0A = (1 << COM0A1) | (1 << WGM01) | (1 << WGM00);`",
                "`TCCR0B = 0x00; // WGM02=0`",
                "`OCR0A = 127;   // 50% duty cycle (127/255)`",
                "`// Indstil prescaler, f.eks. clk/64`",
                "`TCCR0B |= (1 << CS01) | (1 << CS00);`",
                "`// DDRD |= (1 << PD6); // Sæt OC0A (PD6) som output`"
            ]
        )

        # Mode D: Phase Correct PWM Mode
        self.append_text_with_tags(
            "D. Phase Correct PWM Mode:\n",
            is_sub_heading=True
        )
        self.append_text_with_tags(
            "* Tæller fra 0 til TOP, derefter ned til 0. Symmetrisk bølgeform.\n"
            "* Frekvens: `F_CPU / (2 * Prescaler * TOP)` (Bemærk: TOP, ikke TOP+1)\n"
            "* WGM-bits for Timer0/2: `0b001` (WGMx2=0, WGMx1=0, WGMx0=1)\n"
            "* WGM-bits for Timer1 (TOP=0x03FF): `0b0011` (WGM13=0, WGM12=0, WGM11=1, WGM10=1)\n",
            bold_keywords=["TOP", "Frekvens", "Bemærk"],
            monospace_segments=[
                "`F_CPU / (2 * Prescaler * TOP)`", "`0b001`",
                "`0b0011`"
            ]
        )
        self.append_text_with_tags(
            "Eksempel (Timer0 Phase Correct PWM, Non-Inverting på OC0B):\n",
            bold_keywords=["Eksempel (Timer0 Phase Correct PWM, Non-Inverting på OC0B)"]
        )
        self.append_text_with_tags(
            "`TCCR0A = (1 << COM0B1) | (1 << WGM00); // Non-inv, WGM00=1, WGM01=0`\n"
            "`TCCR0B = 0x00; // WGM02=0`\n"
            "`OCR0B = 63;   // 25% duty cycle (63/255)`\n"
            "`// Indstil prescaler, f.eks. clk/8`\n"
            "`TCCR0B |= (1 << CS01);`\n"
            "`// DDRD |= (1 << PD5); // Sæt OC0B (PD5) som output`\n\n",
            monospace_segments=[
                "`TCCR0A = (1 << COM0B1) | (1 << WGM00);`",
                "`TCCR0B = 0x00; // WGM02=0`",
                "`OCR0B = 63;   // 25% duty cycle (63/255)`",
                "`// Indstil prescaler, f.eks. clk/8`",
                "`TCCR0B |= (1 << CS01);`",
                "`// DDRD |= (1 << PD5); // Sæt OC0B (PD5) som output`"
            ]
        )