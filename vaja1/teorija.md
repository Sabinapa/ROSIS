# Teorija za Vajo 1 — Osnove obdelave zvočnih signalov
### (Za pisni zagovor / kolokvij)

---

## 1. Kaj je signal?

**Signal** je fizična veličina, ki se spreminja s časom in prenaša informacijo.

- **Analogni signal** — neprekinjen v času in vrednosti (npr. napetost mikrofona)
- **Digitalni signal** — diskreten v času in vrednosti (zaporedje števil v računalniku)

Zvočni signal nastane, ko glasilke (ali drug vir) ustvarijo nihanje zraka (tlačne valove), ki jih mikrofon pretvori v električni signal.

---

## 2. Vzorčevanje in Nyquistov teorem

Da analogni signal shranimo v računalnik, ga moramo **vzorčiti** — izmeriti v enakih časovnih razmakih.

**Vzorčevalna frekvenca:** `fs` [Hz] = število vzorcev na sekundo

**Nyquistov (Shannon–Nyquistov) teorem:**
> Da signal rekonstruiramo brez napake, mora veljati:
> **fs ≥ 2 · f_max**

kjer je `f_max` najvišja frekvenca v signalu.

**Primer:**
- Človeški sluh: 20 Hz – 20 000 Hz
- Telefonija: fs = 8 000 Hz → zaznamo do 4 000 Hz (dovolj za razumljiv govor)
- CD kakovost: fs = 44 100 Hz → zaznamo do 22 050 Hz (prekrije celoten slušni spekter)

**Aliasing** — napaka, ki nastane, ko je `fs < 2 · f_max`:
- Visokofrekvenčne komponente se "prepišejo" v nižje frekvence
- Rešitev: antialiasingov filter (nizkopreprustni filter) pred vzorčenjem

**Perioda vzorčenja:** `T_s = 1 / fs`  
Primer: fs = 44 100 Hz → Ts = 1/44 100 ≈ 22.7 μs

---

## 3. Sinusoida in njeni parametri

Osnovna matematična oblika periodičnega signala:

```
x(t) = A · sin(2π · f · t + φ)
```

| Parameter | Simbol | Enota | Opis |
|-----------|--------|-------|------|
| Amplituda | A | [-] ali [V] | Maksimalna vrednost (višina) signala |
| Frekvenca | f | Hz | Število period na sekundo |
| Kotna frekvenca | ω = 2π·f | rad/s | Hitrost nihanja v radianih |
| Faza | φ | rad | Začetni zamik v radianih |
| Perioda | T = 1/f | s | Čas ene periode |

**Primer:** `x(t) = 2 · sin(2π · 440 · t + π/4)`
- A = 2, f = 440 Hz (ton A4), φ = π/4 rad, T = 1/440 ≈ 2.27 ms

### Sestavljeni signal (superpozicija)

Vsak periodični signal je mogoče zapisati kot **vsoto sinusoid** z različnimi frekvencami, amplitudami in fazami (Fourierova vrsta):

```
x(t) = Σ Aₙ · sin(2π · fₙ · t + φₙ)
```

**Primer:** signal sestavljen iz treh sinusoid:
```python
x(t) = 1.0 · sin(2π·200·t) + 0.5 · sin(2π·600·t + π/4) + 0.25 · sin(2π·1200·t + π/2)
```

---

## 4. Moč signala in SNR (razmerje signal/šum)

### Moč signala
Moč diskretnega signala x[n] z N vzorci:

```
P_signal = (1/N) · Σ x[n]²
```

Za sinusoido `x(t) = A · sin(...)`:
```
P = A² / 2
```

### SNR — Signal-to-Noise Ratio (razmerje signal/šum)

Meri, kako "glasen" je signal v primerjavi s šumom:

```
SNR = P_signal / P_noise             (linearno razmerje)
SNR_dB = 10 · log₁₀(P_signal / P_noise)   (v decibelih)
```

Ker je moč proporcionalna kvadratu amplitude:
```
SNR_dB = 20 · log₁₀(A_signal / A_noise)
```

**Primer izračuna:** Imamo signal z močjo P_s = 1 W in šum z močjo P_n = 0.001 W.
```
SNR = 1 / 0.001 = 1000
SNR_dB = 10 · log₁₀(1000) = 10 · 3 = 30 dB
```

**Praktične vrednosti SNR:**
| SNR [dB] | Kakovost |
|----------|----------|
| < 10 dB | Signal komaj ločljiv od šuma |
| 20 dB | Slabša kakovost (telefonija) |
| 30–40 dB | Dobra kakovost govora |
| > 60 dB | Odlična kakovost (studijski posnetek) |

### Dodajanje šuma z določenim SNR

Če želimo signalu dodati šum z danim SNR_dB:

1. Izračunaj moč signala: `P_s = mean(x²)`
2. Izračunaj želeno moč šuma: `P_n = P_s / 10^(SNR_dB/10)`
3. Izračunaj standardno deviacijo šuma: `σ = sqrt(P_n)`
4. Generiraj Gaussov šum: `n ~ N(0, σ²)`
5. Seštej: `x_noisy = x + n`

**Primer:** Signal z P_s = 0.5, SNR = 20 dB:
```
P_n = 0.5 / 10^(20/10) = 0.5 / 100 = 0.005
σ = sqrt(0.005) ≈ 0.0707
```

---

## 5. Korelacija

Korelacija meri **stopnjo podobnosti** med dvema signaloma.

### Avtokorelacija

Korelacija signala samega s seboj ob zamiku τ:

```
R_xx(τ) = ∫ x(t) · x(t + τ) dt        (zvezna oblika)
R_xx[k] = Σ x[n] · x[n+k]             (diskretna oblika)
```

**Lastnosti:**
- R_xx(0) = moč signala (maksimalna vrednost)
- Za periodičen signal s periodo T velja: R_xx(T) = R_xx(0)
- Avtokorelacija je **soda funkcija**: R_xx(τ) = R_xx(-τ)

**Uporaba:** Zaznavanje periodičnosti signala, ocena osnovne frekvence (F0).

**Primer:** Če je avtokorelacija visoka pri zamiku k=220 vzorcev (pri fs=44100 Hz):
```
f0 = fs / k = 44100 / 220 ≈ 200 Hz
```

### Križna korelacija

Korelacija med **dvema različnima** signaloma:

```
R_xy(τ) = ∫ x(t) · y(t + τ) dt
R_xy[k] = Σ x[n] · y[n+k]
```

**Normalizirana križna korelacija** (vrednosti med -1 in 1):
```
r_xy[k] = R_xy[k] / (σ_x · σ_y · N)
```
kjer σ_x in σ_y sta standardni deviaciji signalov.

**Interpretacija:**
- r_xy[k] ≈ 1 → signala sta si zelo podobna pri zamiku k
- r_xy[k] ≈ 0 → signala si nista podobna
- r_xy[k] ≈ -1 → signala sta obratna

**Praktična uporaba:** Iskanje vzorca (predloge) v daljšem signalu.  
Vrh korelacije `R_xy[k_max]` nam pove, pri katerem zamiku je predloga najboljše poravnana s signalom → to je **čas nastopa** vzorca.

**Primer za zagovor:**
```
Predloga: 0.5-sekundni posnetek samoglasnika 'a' (N_t = 22050 vzorcev pri 44100 Hz)
Signal:   3-sekundni posnetek besede 'erozija' (N_s = 132300 vzorcev)

Korelacija ima N_s + N_t - 1 vrednosti.
Vrh korelacije pri k = 88200 vzorcev:
čas nastopa 'a' = k / fs = 88200 / 44100 = 2.0 s
```

---

## 6. Samoglasniki in govorni signali

### Kako nastanejo glasovi

1. **Glasilke** v grlu vibrirajo in ustvarjajo osnovno frekvenco **F0** (ton glasu)
2. **Resonančne votline** (žrelo, ustna votlina, nosna votlina) ojačijo določene frekvence
3. Te ojačane frekvence se imenujejo **formanti** (F1, F2, F3 ...)

### Osnovna frekvenca govora (F0)

| Govorec | F0 [Hz] |
|---------|---------|
| Moški glas | 85–180 Hz |
| Ženski glas | 165–255 Hz |
| Otroški glas | 250–400 Hz |

### Formanti samoglasnikov

Vsak samoglasnik ima **karakteristične frekvence formantov**:

| Samoglasnik | F1 [Hz] | F2 [Hz] | Opis |
|-------------|---------|---------|------|
| »a« | 800 | 1200 | Odprta usta, nizek F1, srednji F2 |
| »i« | 300 | 2300 | Ozka reža, nizek F1, visok F2 |
| »o« | 450 | 750 | Zaokrožena usta, srednji F1, nizek F2 |
| »e« | 600 | 1800 | Vmesen med 'a' in 'i' |
| »u« | 300 | 750 | Ozka reža + zaokrožena usta |

**Zakaj ima vsak samoglasnik drugačno obliko valovne oblike?**  
Različne resonančne votline ojačijo različne harmonske komponente — zato se spekter (in posledično oblika valovne oblike) razlikuje med samoglasniki.

### Koartikulacija

Ko izgovarjamo besedo, se govorne organe **ne prestavljajo neodvisno** — prehod med glasovi je posteposten. Zato:
- Samoglasnik v besedi **ni enak** osamljenemu samoglasniku
- Amplituda variira na začetku in koncu vsakega glasu
- Spektralna vsebina se med glasom rahlo spreminja

---

## 7. OpenDAQ — osnove knjižnice

**OpenDAQ** je Python knjižnica za zajem podatkov iz merilnih naprav.

### Osnovna vzorčevalna veriga:
```
Mikrofon → OpenDAQ naprava (ADC) → Python
```

**ADC (Analog-to-Digital Converter)** pretvori analogni signal v digitalne vzorce pri frekvenci `fs`.

### Ključni koncepti:
- **Naprava (Device):** fizična merilna enota, priključena na USB/mrežo
- **Kanal (Channel):** en vhod naprave (npr. mikrofonski vhod)
- **Signal:** zaporedje vzorcev, ki ga kanal oddaja
- **StreamReader:** Python objekt za branje vzorcev v realnem času

### Vzorčevalna frekvenca in resolucija:
- Višja `fs` → boljša časovna ločljivost, več podatkov
- Resolucija ADC (npr. 16-bit) → 2¹⁶ = 65536 različnih vrednosti

---

## 8. Ključne formule za zagovor

| Formula | Pomen |
|---------|-------|
| `fs ≥ 2 · f_max` | Nyquistov pogoj za vzorčevanje |
| `T = 1/f` | Perioda sinusoide |
| `ω = 2πf` | Kotna frekvenca |
| `x(t) = A·sin(2πft + φ)` | Splošna enačba sinusoide |
| `P = A²/2` | Moč sinusoide |
| `P = (1/N)·Σx²[n]` | Moč diskretnega signala |
| `SNR_dB = 10·log₁₀(P_s/P_n)` | SNR v decibelih |
| `σ_n = sqrt(P_s / 10^(SNR/10))` | Standardna deviacija šuma pri danem SNR |
| `R_xy[k] = Σ x[n]·y[n+k]` | Diskretna križna korelacija |
| `t_nastop = k_vrh / fs` | Čas nastopa iz korelacije |

---

## 9. Tipična vprašanja na zagovoru

**V: Zakaj moramo vzorčiti pri vsaj dvakratni frekvenci signala?**  
O: Da preprečimo aliasing — napačno rekonstrukcijo visokih frekvenc. Nyquistov teorem zahteva fs ≥ 2·f_max, sicer se visoke frekvence "zrcalijo" v nižji del spektra.

**V: Kaj je SNR 20 dB? Koliko je šum v primerjavi s signalom?**  
O: SNR = 10^(20/10) = 100. Moč signala je 100-krat večja od moči šuma. Amplitudno razmerje: √100 = 10.

**V: Kako izračunate standardno deviacijo šuma za SNR = 30 dB pri signalu z amplitudo A = 1?**  
O: P_s = A²/2 = 0.5; P_n = P_s / 10^3 = 0.0005; σ = √0.0005 ≈ 0.0224.

**V: Kaj pomeni vrh v križni korelaciji pri zamiku k = 4410 vzorcev (fs = 44100 Hz)?**  
O: Predloga je najbol podobna signalu pri zamiku t = 4410/44100 = 0.1 s — predloga se pojavi 0.1 sekunde po začetku signala.

**V: Zakaj je samoglasnik v besedi drugačen od osamljenega samoglasnika?**  
O: Koartikulacija — govorne organe se ne premikajo neodvisno, prehodi med glasovi so postopni. V besedi je samoglasnik krajši, ima amplitudne prehode in je spektralno rahlo modificiran z vplivi sosednjih glasov.

**V: Kateri dve frekvenci najbolj ločujeta samoglasnike med seboj?**  
O: F1 in F2 — prva in druga formantna frekvenca. Pri »i« je F2 visok (~2300 Hz), pri »u« in »o« je nizek (~750 Hz). F1 je nizek pri zaprtih samoglasnikih (i, u) in visok pri odprtih (a).
