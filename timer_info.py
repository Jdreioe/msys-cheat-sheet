import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango

class ReadSettingsInfoTab(Gtk.ScrolledWindow):
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
            "Aflæsning af Timerindstillinger\n",
            is_heading=True
        )
        self.append_text_with_tags(
            "For at aflæse en timers nuværende indstillinger skal du læse indholdet af dens kontrol- og tællerregistre.\n\n"
            "Vigtigste Registre at Aflæse:\n",
            bold_keywords=["Vigtigste Registre at Aflæse"]
        )
        self.append_text_with_tags(
            "* TCCRxA, TCCRxB, TCCRxC: Timer/Counter Control Register. Indeholder Waveform Generation Mode (WGM) bits, Compare Output Mode (COM) bits og Clock Select (CS) bits (prescaler).\n"
            "* TCNTx: Timer/Counter Register. Den aktuelle tællerstand.\n"
            "* OCRxA, OCRxB, OCRxC: Output Compare Register. Bruges til at sætte en sammenligningsværdi for Output Compare Match interrupts og PWM-cyklus.\n"
            "* ICRx: Input Capture Register (kun 16-bit timere). Bruges til at gemme tællerstanden ved et Input Capture Event.\n"
            "* TIMSKx: Timer Interrupt Mask Register. Viser hvilke interrupts der er aktiveret for timeren.\n"
            "* TIFRx: Timer Interrupt Flag Register. Indeholder flag, der sættes, når et interrupt udløses. Disse skal ofte cleares manuelt (ved at skrive en 1 til flag-biten).\n\n"
            "Eksempel (Aflæsning af Timer1):\n",
            bold_keywords=["TCCRxA", "TCCRxB", "TCCRxC", "Timer/Counter Control Register", "Waveform Generation Mode", "WGM", "Compare Output Mode", "COM", "Clock Select", "CS", "prescaler", "TCNTx", "Timer/Counter Register", "OCRxA", "OCRxB", "OCRxC", "Output Compare Register", "ICRx", "Input Capture Register", "TIMSKx", "Timer Interrupt Mask Register", "TIFRx", "Timer Interrupt Flag Register", "Eksempel (Aflæsning af Timer1)"]
        )
        self.append_text_with_tags(
            "`unsigned char tccr1a_val = TCCR1A;`\n"
            "`unsigned char tccr1b_val = TCCR1B;`\n"
            "`unsigned int tcnt1_val = TCNT1;   // Læs LAV så HØJ for 16-bit`\n"
            "`unsigned int ocr1a_val = OCR1A;`\n"
            "`unsigned int icr1_val = ICR1;`\n"
            "`unsigned char timsk1_val = TIMSK1;`\n"
            "`unsigned char tifr1_val = TIFR1;`\n\n",
            monospace_segments=["`unsigned char tccr1a_val = TCCR1A;`", "`unsigned char tccr1b_val = TCCR1B;`", "`unsigned int tcnt1_val = TCNT1;`", "`unsigned int ocr1a_val = OCR1A;`", "`unsigned int icr1_val = ICR1;`", "`unsigned char timsk1_val = TIMSK1;`", "`unsigned char tifr1_val = TIFR1;`"]
        )
        self.append_text_with_tags(
            "Bemærk: For 16-bit timere (Timer1, Timer3, Timer4, Timer5) skal du læse TCNTx, OCRx og ICRx på en specifik måde for at undgå datakorruption, da registrene er to 8-bit registre, der aflæses som ét 16-bit ord. Det anbefales at læse LAV-byte først og derefter HØJ-byte, eller bruge de indbyggede C-makroer hvis tilgængelige.\n",
            bold_keywords=["Bemærk", "Timer1", "Timer3", "Timer4", "Timer5", "TCNTx", "OCRx", "ICRx", "datakorruption", "LAV-byte", "HØJ-byte"]
        )