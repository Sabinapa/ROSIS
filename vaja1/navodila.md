# Vaja 1: Osnove obdelave signalov

## Namen
Spoznati osnove obdelave signalov s programskim jezikom Python.

## Zahtevano okolje
- Python (Jupyter Notebook `.ipynb`)
- Notebook deluje kot **frontend**, zaledne funkcije so v ločenih `.py` datotekah

---

## Naloge

### 1–3: Snemanje samoglasnikov
Posnemite **3 sekunde dolge** zvočne signale pri:

| # | Zvok | Opis |
|---|------|------|
| 1a | Samoglasnik **»a«** | visok ton |
| 1b | Samoglasnik **»a«** | nizek ton |
| 2a | Samoglasnik **»i«** | visok ton |
| 2b | Samoglasnik **»i«** | nizek ton |
| 3a | Samoglasnik **»o«** | visok ton |
| 3b | Samoglasnik **»o«** | nizek ton |

Konstantna intenzivnost in ton pri vsakem posnetku.

### 4: Snemanje besede »erozija«
| # | Zvok | Opis |
|---|------|------|
| 4a | Beseda **»erozija«** | počasna izgovorjava |
| 4b | Beseda **»erozija«** | hitra izgovorjava |

Obe z **enako višino tona**, ki naj bo podoben eni višini tona pri črkah.

---

## Prikaz signalov
Za vsakega od 8 posnetkov prikažite **2 grafa drug ob drugem** (levo–desno):
- **Levi graf:** celoten signal
- **Desni graf:** kratki odsek signala na 3–4 periode

Zahteve za grafe:
- Osi pravilno označene po inženirskih standardih (ne premajhne črke)
- **Os X izražena v sekundah [s]**

---

## Analiza in vprašanja

### Vprašanje 1
Primerjajte oblike signalov samostojnih samoglasnikov (točke 1–3) s posnetki samoglasnikov v besedi »erozija«. **Kaj opazite?**

### Vprašanje 2
Ali lahko s pomočjo **križne korelacije** v besedi »erozija« na podlagi predposnetih glasov »a«, »i«, »o« določimo čas nastopa posameznih črk?

---

## Simulacija signalov
Dodajte možnost simulacije sestavljenega signala s **poljubnim številom sinusoid** s parametri:
- frekvenca [Hz]
- faza [rad]
- amplituda
- dolžina [s]

Za vsako sinusoido podprite **dodajanje naravnega šuma s poljubnim SNR**.  
Končna dolžina signala = dolžina najdaljše sinusoide.

---

## Napotki za snemanje
- Snemajte z **veliko natančnostjo** (brez šuma iz okolice)
- Noise cancellation mikrofonov → nastavite gonilnike ali odrežite nenavadni začetek signala
- Posnetki se bodo uporabljali **tudi pri prihodnjih vajah**
- Za zajem **obvezno** uporabite knjižnico **OpenDAQ**

---

## Oddaja
Datoteka `naloga.zip` vsebuje:
- `porocilo.ipynb`
- vse lastne `.py` datoteke

**Ne oddajajte:** WAV datotek, slik, ostalih datotek.

Poročilo mora vsebovati:
- Odgovore na vprašanja
- Vse grafe
- Komentirane ključne dele kode
