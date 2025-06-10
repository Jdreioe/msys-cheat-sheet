import tkinter as tk
from tkinter import ttk, scrolledtext

class BitShiftRotateTab:
    def __init__(self, notebook, tab_title="Bit Shift & Rotate"):
        self.notebook = notebook
        self.tab_frame = ttk.Frame(notebook)
        notebook.add(self.tab_frame, text=tab_title)

        self._create_widgets()

    def _create_widgets(self):
        title_label = tk.Label(self.tab_frame, text="Bit Skift & Rotering Instruktioner (AVR)", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        info_text = scrolledtext.ScrolledText(self.tab_frame, wrap=tk.WORD, width=80, height=25, font=("Arial", 10))
        info_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        content = """
        Bit skift- og roteringsinstruktioner er grundlæggende operationer i mikrokontrollerprogrammering til at manipulere individuelle bits i et register eller til at udføre hurtige multiplikationer/divisioner med potenser af 2.

        AVR-arkitekturen inkluderer flere sådanne instruktioner:

        1.  **LSL (Logical Shift Left)**
            * **Beskrivelse:** Skubber alle bits i et register én position til venstre. Den mest venstre bit (MSB) flyttes ind i Carry-flagget (C i SREG), og den mest højre bit (LSB) fyldes med en nul.
            * **Formål:** Ækvivalent med at multiplicere et usignedt tal med 2 (for hver skift).
            * **Instruktion:** `LSL Rd`
            * **Cycles:** 1
            * **Eksempel (8-bit register, før = 0b10010010):**
                ```
                C  7 6 5 4 3 2 1 0  (Bit positions)
                .  1 0 0 1 0 0 1 0  (Before LSL)
                |
                v
                1  0 0 1 0 0 1 0 0  (After LSL)
                ```
            * **Effekt på flags:** Z, N, C, H, V (alle påvirkes)
            * **Hvornår skal den bruges?**
                * Til hurtig *multiplikation af usignerede tal med 2*.
                * Når du skal *flytte en bit fra MSB-positionen ind i Carry-flagget* for senere inspektion eller brug i en multi-byte operation (f.eks. ved overførsel til et andet register via Carry).
                * Carry-flaggets *tidligere værdi har ingen betydning* for denne instruktion; det bruges kun som output.

        2.  **LSR (Logical Shift Right)**
            * **Beskrivelse:** Skubber alle bits i et register én position til højre. Den mest højre bit (LSB) flyttes ind i Carry-flagget (C i SREG), og den mest venstre bit (MSB) fyldes med en nul.
            * **Formål:** Ækvivalent med at dividere et usignedt tal med 2 (for hver skift).
            * **Instruktion:** `LSR Rd`
            * **Cycles:** 1
            * **Eksempel (8-bit register, før = 0b10010010):**
                ```
                C  7 6 5 4 3 2 1 0  (Bit positions)
                0  1 0 0 1 0 0 1 0  (Before LSR)
                ^
                |
                0  0 1 0 0 1 0 0 1  (After LSR)
                ```
            * **Effekt på flags:** Z, N, C, H, V (alle påvirkes)
            * **Hvornår skal den bruges?**
                * Til hurtig *division af usignerede tal med 2*.
                * Når du skal *flytte en bit fra LSB-positionen ind i Carry-flagget* (f.eks. for at tjekke, om et tal er ulige, eller for at forberede en multi-byte operation).
                * Carry-flaggets *tidligere værdi har ingen betydning* for denne instruktion; det bruges kun som output.

        3.  **ROL (Rotate Left Through Carry)**
            * **Beskrivelse:** Roterer alle bits i et register én position til venstre. Den mest venstre bit (MSB) flyttes ind i Carry-flagget (C i SREG), OG det eksisterende Carry-flag flyttes ind i den mest højre bit (LSB). Dette er en "rotation gennem Carry".
            * **Instruktion:** `ROL Rd` (Eller `ADC Rd, Rd` som er en ækvivalent instruktion for ROL i mange tilfælde, da den udfører `Rd = Rd + Rd + C`)
            * **Cycles:** 1
            * **Eksempel (8-bit register, før = 0b10010010, C-flag = 0):**
                ```
                C  7 6 5 4 3 2 1 0  (Bit positions)
                0  1 0 0 1 0 0 1 0  (Before ROL)
                |<-             <-|  (Rotation path)
                v               ^
                1  0 0 1 0 0 1 0 0  (After ROL)
                ```
            * **Eksempel (8-bit register, før = 0b10010010, C-flag = 1):**
                ```
                C  7 6 5 4 3 2 1 0  (Bit positions)
                1  1 0 0 1 0 0 1 0  (Before ROL)
                |<-             <-|  (Rotation path)
                v               ^
                1  0 0 1 0 0 1 0 1  (After ROL)
                ```
            * **Effekt på flags:** Z, N, C, H, V (alle påvirkes)
            * **Hvornår skal den bruges?**
                * Til at udføre *multi-byte venstreskift*: Start med `LSL` på det laveste register, derefter `ROL` på de højere registre. Dette sikrer, at Carry-flagget (som indeholder den bit, der "skiftede ud" fra det lavere register) roteres ind i LSB af det næste register.
                * Til at udføre *cirkulære rotationer* hvor alle bits (inklusive Carry-flagget) deltager.
                * **Vigtigt: Hvis Carry-flaggets tilstand er ukendt, og du ikke ønsker, at det skal påvirke rotationen, skal du eksplicit rydde det (`CLC`) eller sætte det (`SEC`) FØR du udfører `ROL`.** Ellers kan resultatet være uforudsigeligt.

        4.  **ROR (Rotate Right Through Carry)**
            * **Beskrivelse:** Roterer alle bits i et register én position til højre. Den mest højre bit (LSB) flyttes ind i Carry-flagget (C i SREG), OG det eksisterende Carry-flag flyttes ind i den mest venstre bit (MSB). Dette er en "rotation gennem Carry".
            * **Instruktion:** `ROR Rd`
            * **Cycles:** 1
            * **Eksempel (8-bit register, før = 0b10010010, C-flag = 1):**
                ```
                C  7 6 5 4 3 2 1 0  (Bit positions)
                1  1 0 0 1 0 0 1 0  (Before ROR)
                ^               ^
                |->             ->|  (Rotation path)
                0  1 1 0 0 1 0 0 1  (After ROR)
                ```
            * **Eksempel (8-bit register, før = 0b10010010, C-flag = 0):**
                ```
                C  7 6 5 4 3 2 1 0  (Bit positions)
                0  1 0 0 1 0 0 1 0  (Before ROR)
                ^               ^
                |->             ->|  (Rotation path)
                0  0 1 0 0 1 0 0 1  (After ROR)
                ```
            * **Effekt på flags:** Z, N, C, H, V (alle påvirkes)
            * **Hvornår skal den bruges?**
                * Til at udføre *multi-byte højreskift*: Start med `LSR` på det højeste register, derefter `ROR` på de lavere registre. Dette sikrer, at Carry-flagget (som indeholder den bit, der "skiftede ud" fra det højere register) roteres ind i MSB af det næste register.
                * Til at udføre *cirkulære rotationer* hvor alle bits (inklusive Carry-flagget) deltager.
                * **Vigtigt: Hvis Carry-flaggets tilstand er ukendt, og du ikke ønsker, at det skal påvirke rotationen, skal du eksplicit rydde det (`CLC`) eller sætte det (`SEC`) FØR du udfører `ROR`.** Ellers kan resultatet være uforudsigeligt.

        **Vigtighed af Carry Flag (C):**
        For `ROL` og `ROR` er Carry-flagget ikke bare en destination for en skubbet bit, men også en kilde for den bit, der roteres ind i den modsatte ende af registret. Dette gør dem yderst nyttige til at håndtere skift og rotationer af tal, der er bredere end et enkelt 8-bit register (f.eks. 16-bit eller 32-bit tal gemt i flere 8-bit registre). Hvis du kun ønsker en simpel bitrotation inden for et 8-bit register *uden* involvering af Carry-flagget (dvs. den udskiftede bit roteres direkte tilbage til den anden ende af registret), skal du sørge for at rydde Carry-flagget før operationen (`CLC`).
        """
        info_text.insert(tk.END, content)
        info_text.config(state=tk.DISABLED) # Make it read-only