import tkinter as tk
from tkinter import ttk, scrolledtext

class NumberSystemsTab:
    def __init__(self, notebook, tab_title="Number Systems"):
        self.notebook = notebook
        self.tab_frame = ttk.Frame(notebook)
        notebook.add(self.tab_frame, text=tab_title)

        self._create_widgets()

    def _create_widgets(self):
        title_label = tk.Label(self.tab_frame, text="Talsystemer i Digital Elektronik", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        info_text = scrolledtext.ScrolledText(self.tab_frame, wrap=tk.WORD, width=80, height=25, font=("Arial", 10))
        info_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        content = """
        1.  **Usigned (Unsigned Integer)**
            * **Beskrivelse:** Repræsenterer kun ikke-negative heltal (fra 0 og op). Alle bits bruges til at repræsentere værdien.
            * **Eksempel (8-bit):**
                * Binary: `00000000` = 0
                * Binary: `11111111` = 255
            * **Range (N bits):** 0 to $2^N - 1$
            * **Anvendelse:** Tællere, adresseværdier, og andre situationer hvor negative tal ikke er relevante.

        2.  **Signed Magnitude (Fortegns-magnitude)**
            * **Beskrivelse:** Den mest venstre bit (Most Significant Bit, MSB) bruges som fortegnsbit (0 for positiv, 1 for negativ). De resterende bits repræsenterer tallets absolutte værdi (magnitude).
            * **Eksempel (8-bit):**
                * Binary: `00000001` = +1
                * Binary: `10000001` = -1
                * **Ulemper:** Har to repræsentationer for nul (`00000000` og `10000000`). Komplicerer addition/subtraktion.
            * **Range (N bits):** $-(2^{N-1} - 1)$ to $2^{N-1} - 1$

        3.  **1's Complement (1-Komplement)**
            * **Beskrivelse:** Positive tal repræsenteres som i usigned. Negative tal dannes ved at invertere alle bits (0 bliver 1, 1 bliver 0) af det tilsvarende positive tal.
            * **Eksempel (8-bit):**
                * Binary: `00000001` = +1
                * For -1: Tag +1 (`00000001`), inverter alle bits -> `11111110`
                * **Ulemper:** Har også to repræsentationer for nul (`00000000` og `11111111`). Kræver "end-around carry" ved addition.
            * **Range (N bits):** $-(2^{N-1} - 1)$ to $2^{N-1} - 1$

        4.  **2's Complement (2-Komplement)**
            * **Beskrivelse:** Den mest udbredte metode til repræsentation af fortegnsbestemte heltal i computere. Positive tal er som usigned. Negative tal dannes ved at tage 1's komplement og derefter lægge 1 til.
            * **Fordele:** Har kun én repræsentation for nul. Addition og subtraktion udføres ved standard binær addition, hvilket forenkler hardware.
            * **Eksempel (8-bit):**
                * Binary: `00000001` = +1
                * For -1:
                    1.  Start med +1: `00000001`
                    2.  Inverter (1's complement): `11111110`
                    3.  Læg 1 til: `11111110 + 1 = 11111111`
                * `11111111` = -1
                * `10000000` = -128 (for 8-bit) - dette er det mest negative tal.
            * **Range (N bits):** $-2^{N-1}$ to $2^{N-1} - 1$

        **Tabeloversigt (8-bit eksempel):**
        | Decimal | Usigned | Signed Magnitude | 1's Complement | 2's Complement |
        |---------|---------|------------------|----------------|----------------|
        | 0       | 00000000| 00000000         | 00000000       | 00000000       |
        | +1      | 00000001| 00000001         | 00000001       | 00000001       |
        | +127    | 01111111| 01111111         | 01111111       | 01111111       |
        | -1      | N/A     | 10000001         | 11111110       | 11111111       |
        | -127    | N/A     | 11111111         | 10000000       | 10000001       |
        | -128    | N/A     | N/A              | N/A            | 10000000       |
        | 255     | 11111111| N/A              | N/A            | N/A            |

        """
        info_text.insert(tk.END, content)
        info_text.config(state=tk.DISABLED) # Make it read-only
