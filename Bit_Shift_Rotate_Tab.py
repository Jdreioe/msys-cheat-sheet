import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango


class BitShiftRotateTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self._create_widgets()

    def _create_widgets(self):
        title_label = Gtk.Label()
        title_label.set_markup("<span font_desc='Arial Bold 16'>Bit Skift & Rotering Instruktioner (AVR)</span>")
        title_label.set_halign(Gtk.Align.START)
        self.append(title_label)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        info_text_view = Gtk.TextView()
        info_text_view.set_editable(False)
        info_text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        info_text_view.set_cursor_visible(False)

        # Set font

        text_buffer = info_text_view.get_buffer()
        # Use Pango markup for bold, but Gtk.TextView does not render HTML or Pango markup directly.
        # Instead, use tags for formatting.
        text = (
            "Bit skift- og roteringsinstruktioner er grundlæggende operationer i mikrokontrollerprogrammering til at manipulere individuelle bits i et register eller til at udføre hurtige multiplikationer/divisioner med potenser af 2.\n\n"
            "AVR-arkitekturen inkluderer flere sådanne instruktioner:\n\n"
            "1.  LSL (Logical Shift Left)\n"
            "    Beskrivelse: Skubber alle bits i et register én position til venstre. Den mest venstre bit (MSB) flyttes ind i Carry-flagget (C i SREG), og den mest højre bit (LSB) fyldes med en nul.\n"
            "    Formål: Ækvivalent med at multiplicere et usignedt tal med 2 (for hver skift).\n"
            "    Instruktion: LSL Rd\n"
            "    Cycles: 1\n"
            "    Eksempel (8-bit register, før = 0b10010010):\n\n"
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            ".  1 0 0 1 0 0 1 0  (Before LSL)\n"
            "     |\n"
            "     v\n"
            "1  0 0 1 0 0 1 0 0  (After LSL)\n\n"
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til hurtig multiplikation af usignerede tal med 2.\n"
            "    Når du skal flytte en bit fra MSB-positionen ind i Carry-flagget for senere inspektion eller brug i en multi-byte operation (f.eks. ved overførsel til et andet register via Carry).\n"
            "    Carry-flaggets tidligere værdi har ingen betydning for denne instruktion; det bruges kun som output.\n\n"
            "2.  LSR (Logical Shift Right)\n"
            "    Beskrivelse: Skubber alle bits i et register én position til højre. Den mest højre bit (LSB) flyttes ind i Carry-flagget (C i SREG), og den mest venstre bit (MSB) fyldes med en nul.\n"
            "    Formål: Ækvivalent med at dividere et usignedt tal med 2 (for hver skift).\n"
            "    Instruktion: LSR Rd\n"
            "    Cycles: 1\n"
            "    Eksempel (8-bit register, før = 0b10010010):\n\n"
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    0  1 0 0 1 0 0 1 0  (Before LSR)\n"
            "    ^\n"
            "    |\n"
            "    0  0 1 0 0 1 0 0 1  (After LSR)\n\n"
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til hurtig division af usignerede tal med 2.\n"
            "    Når du skal flytte en bit fra LSB-positionen ind i Carry-flagget (f.eks. for at tjekke, om et tal er ulige, eller for at forberede en multi-byte operation).\n"
            "    Carry-flaggets tidligere værdi har ingen betydning for denne instruktion; det bruges kun som output.\n\n"
            "3.  ROL (Rotate Left Through Carry)\n"
            "    Beskrivelse: Roterer alle bits i et register én position til venstre. Den mest venstre bit (MSB) flyttes ind i Carry-flagget (C i SREG), OG det eksisterende Carry-flag flyttes ind i den mest højre bit (LSB). Dette er en \"rotation gennem Carry\".\n"
            "    Instruktion: ROL Rd (Eller ADC Rd, Rd som er en ækvivalent instruktion for ROL i mange tilfælde, da den udfører Rd = Rd + Rd + C)\n"
            "    Cycles: 1\n"
            "    Eksempel (8-bit register, før = 0b10010010, C-flag = 0):\n\n"
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    0  1 0 0 1 0 0 1 0  (Before ROL)\n"
            "    |<-             <-|  (Rotation path)\n"
            "    v               ^\n"
            "    1  0 0 1 0 0 1 0 0  (After ROL)\n\n"
            "    Eksempel (8-bit register, før = 0b10010010, C-flag = 1):\n\n"
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    1  1 0 0 1 0 0 1 0  (Before ROL)\n"
            "    |<-             <-|  (Rotation path)\n"
            "    v               ^\n"
            "    1  0 0 1 0 0 1 0 1  (After ROL)\n\n"
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til at udføre multi-byte venstreskift: Start med LSL på det laveste register, derefter ROL på de højere registre. Dette sikrer, at Carry-flagget (som indeholder den bit, der \"skiftede ud\" fra det lavere register) roteres ind i LSB af det næste register.\n"
            "    Til at udføre cirkulære rotationer hvor alle bits (inklusive Carry-flagget) deltager.\n"
            "    Vigtigt: Hvis Carry-flaggets tilstand er ukendt, og du ikke ønsker, at det skal påvirke rotationen, skal du eksplicit rydde det (CLC) eller sætte det (SEC) FØR du udfører ROL. Ellers kan resultatet være uforudsigeligt.\n\n"
            "4.  ROR (Rotate Right Through Carry)\n"
            "    Beskrivelse: Roterer alle bits i et register én position til højre. Den mest højre bit (LSB) flyttes ind i Carry-flagget (C i SREG), OG det eksisterende Carry-flag flyttes ind i den mest venstre bit (MSB). Dette er en \"rotation gennem Carry\".\n"
            "    Instruktion: ROR Rd\n"
            "    Cycles: 1\n"
            "    Eksempel (8-bit register, før = 0b10010010, C-flag = 1):\n\n"
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    1  1 0 0 1 0 0 1 0  (Before ROR)\n"
            "    ^               ^\n"
            "    |->             ->|  (Rotation path)\n"
            "    0  1 1 0 0 1 0 0 1  (After ROR)\n\n"
            "    Eksempel (8-bit register, før = 0b10010010, C-flag = 0):\n\n"
            "C  7 6 5 4 3 2 1 0  (Bit positions)\n"
            "    0  1 0 0 1 0 0 1 0  (Before ROR)\n"
            "    ^               ^\n"
            "    |->             ->|  (Rotation path)\n"
            "    0  0 1 0 0 1 0 0 1  (After ROR)\n\n"
            "    Effekt på flags: Z, N, C, H, V (alle påvirkes)\n"
            "    Hvornår skal den bruges?\n"
            "    Til at udføre multi-byte højreskift: Start med LSR på det højeste register, derefter ROR på de lavere registre. Dette sikrer, at Carry-flagget (som indeholder den bit, der \"skiftede ud\" fra det højere register) roteres ind i MSB af det næste register.\n"
            "    Til at udføre cirkulære rotationer hvor alle bits (inklusive Carry-flagget) deltager.\n"
            "    Vigtigt: Hvis Carry-flaggets tilstand er ukendt, og du ikke ønsker, at det skal påvirke rotationen, skal du eksplicit rydde det (CLC) eller sætte det (SEC) FØR du udfører ROR. Ellers kan resultatet være uforudsigeligt.\n\n"
            "Vigtighed af Carry Flag (C):\n"
            "For ROL og ROR er Carry-flagget ikke bare en destination for en skubbet bit, men også en kilde for den bit, der roteres ind i den modsatte ende af registret. Dette gør dem yderst nyttige til at håndtere skift og rotationer af tal, der er bredere end et enkelt 8-bit register (f.eks. 16-bit eller 32-bit tal gemt i flere 8-bit registre). Hvis du kun ønsker en simpel bitrotation inden for et 8-bit register uden involvering af Carry-flagget (dvs. den udskiftede bit roteres direkte tilbage til den anden ende af registret), skal du sørge for at rydde Carry-flagget før operationen (CLC).\n"
        )
        text_buffer.set_text(text)
        # Optionally, set a monospace font for better formatting of diagrams

        scrolled_window.set_child(info_text_view)
        self.append(scrolled_window)