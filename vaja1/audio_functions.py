"""
audio_functions.py
Zaledne funkcije za Vajo 1: Osnove obdelave zvočnih signalov (ROSIS).
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sp_signal
from scipy.io import wavfile
import os

# ── OpenDAQ ────────────────────────────────────────────────────────────────
try:
    import opendaq as daq
    _OPENDAQ = True
except ImportError:
    _OPENDAQ = False

# ── sounddevice (rezerva) ──────────────────────────────────────────────────
try:
    import sounddevice as sd
    _SOUNDDEVICE = True
except ImportError:
    _SOUNDDEVICE = False


# ══════════════════════════════════════════════════════════════════════════════
# SIMULACIJA
# ══════════════════════════════════════════════════════════════════════════════

def simulate_composite_signal(components, fs=44100, duration=None):
    """
    Simulira sestavljeni signal iz več sinusoid.

    Parametri
    ---------
    components : list[dict]
        Vsak element ima ključe:
          'frequency'  – frekvenca [Hz] (obvezno)
          'amplitude'  – amplituda (privzeto 1.0)
          'phase'      – začetna faza [rad] (privzeto 0.0)
          'duration'   – dolžina te sinusoide [s] (privzeto = skupna dolžina)
          'snr_db'     – SNR v dB za dodajanje šuma tej sinusoidi (opcijsko)
    fs       : vzorčevalna frekvenca [Hz]
    duration : skupna dolžina [s]; če None, vzame max(duration) iz komponent

    Vrne
    ----
    t         : np.ndarray  – časovna os [s]
    composite : np.ndarray  – sestavljeni signal
    """
    if duration is None:
        duration = max(float(c.get('duration', 1.0)) for c in components)

    n = int(round(fs * duration))
    t = np.arange(n) / fs
    composite = np.zeros(n)

    for c in components:
        f   = float(c['frequency'])
        A   = float(c.get('amplitude', 1.0))
        phi = float(c.get('phase', 0.0))
        d   = float(c.get('duration', duration))

        n_c = min(int(round(fs * d)), n)
        component = A * np.sin(2.0 * np.pi * f * t[:n_c] + phi)

        if 'snr_db' in c:
            component = add_noise(component, float(c['snr_db']))

        composite[:n_c] += component

    return t, composite


def add_noise(signal, snr_db):
    """
    Doda Gaussov (naravni) šum signalu z določenim SNR.

    SNR_dB = 10 * log10(P_signal / P_noise)
    => P_noise = P_signal / 10^(SNR_dB / 10)
    => sigma_noise = sqrt(P_noise)

    Parametri
    ---------
    signal : np.ndarray
    snr_db : float – razmerje signal/šum [dB]

    Vrne
    ----
    np.ndarray – signal z dodanim šumom
    """
    P_s = np.mean(signal ** 2)
    if P_s == 0.0:
        return signal.copy()
    P_n = P_s / (10.0 ** (snr_db / 10.0))
    rng = np.random.default_rng()
    noise = rng.normal(0.0, np.sqrt(P_n), len(signal))
    return signal + noise


# ══════════════════════════════════════════════════════════════════════════════
# SNEMANJE
# ══════════════════════════════════════════════════════════════════════════════

def record_signal(duration, fs=44100, connection_string=None):
    """
    Posname zvočni signal.
    Prednostno uporabi OpenDAQ, sicer sounddevice.

    Parametri
    ---------
    duration          : dolžina snemanja [s]
    fs                : vzorčevalna frekvenca [Hz]
    connection_string : OpenDAQ connection string (None = samodejno)

    Vrne
    ----
    (signal, fs) – np.ndarray float64, vzorčevalna frekvenca
    """
    if _OPENDAQ:
        return _record_opendaq(duration, fs, connection_string)
    elif _SOUNDDEVICE:
        print("[OPOZORILO] OpenDAQ ni na voljo – uporaba sounddevice kot rezerve.")
        return _record_sounddevice(duration, fs)
    else:
        raise RuntimeError(
            "Namestite OpenDAQ ali sounddevice:\n"
            "  pip install opendaq\n"
            "  pip install sounddevice"
        )


def _record_opendaq(duration, fs, connection_string=None):
    instance = daq.Instance()

    if connection_string is None:
        available = instance.available_devices
        if not available:
            raise RuntimeError(
                "Ni najdenih OpenDAQ naprav. Preverite povezavo naprave."
            )
        connection_string = available[0].connection_string
        print(f"[OpenDAQ] Naprava: {available[0].name}  ({connection_string})")

    device = instance.add_device(connection_string)

    if not device.channels:
        raise RuntimeError("OpenDAQ naprava nima razpoložljivih kanalov.")

    channel = device.channels[0]

    # Nastavi vzorčevalno frekvenco, če je podprto
    try:
        channel.set_sample_rate(fs)
    except Exception:
        pass

    sig_obj = channel.signals[0]
    reader = daq.StreamReader(sig_obj)

    n_total = int(round(duration * fs))
    samples = np.empty(n_total, dtype=np.float64)
    collected = 0

    print(f"[OpenDAQ] Snemal {duration:.1f} s ...")
    while collected < n_total:
        chunk_size = min(4096, n_total - collected)
        chunk, count = reader.read(chunk_size, timeout=5000)
        samples[collected:collected + count] = np.asarray(
            chunk[:count], dtype=np.float64
        )
        collected += count

    print("[OpenDAQ] Snemanje končano.")
    return samples, fs


def _record_sounddevice(duration, fs):
    print(f"[sounddevice] Snemanje {duration:.1f} s pri {fs} Hz ...")
    rec = sd.rec(
        int(round(duration * fs)),
        samplerate=fs,
        channels=1,
        dtype='float64'
    )
    sd.wait()
    print("[sounddevice] Snemanje končano.")
    return rec[:, 0], int(fs)


# ══════════════════════════════════════════════════════════════════════════════
# SHRANJEVANJE / NALAGANJE
# ══════════════════════════════════════════════════════════════════════════════

def save_wav(signal, fs, filepath):
    """Shrani signal kot 16-bitni PCM WAV."""
    peak = np.max(np.abs(signal))
    if peak > 0:
        norm = (signal / peak * 32767.0).astype(np.int16)
    else:
        norm = signal.astype(np.int16)
    wavfile.write(filepath, int(fs), norm)
    print(f"Shranjeno: {filepath}")


def load_wav(filepath):
    """
    Naloži WAV datoteko in normalizira v float64 [-1, 1].

    Vrne: (signal, fs)
    """
    fs, data = wavfile.read(filepath)
    if data.ndim > 1:
        data = data[:, 0]  # vzemi samo prvi kanal (mono)
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    else:
        data = data.astype(np.float64)
    return data, int(fs)


def extract_stable_segment(signal, fs, duration=0.5):
    """
    Izvleče stabilen (sredinski) odsek signala določene dolžine.
    Uporabno za pripravo predloge za križno korelacijo.
    """
    n = int(round(fs * duration))
    center = len(signal) // 2
    start = max(0, center - n // 2)
    end = min(len(signal), start + n)
    return signal[start:end]


# ══════════════════════════════════════════════════════════════════════════════
# VIZUALIZACIJA
# ══════════════════════════════════════════════════════════════════════════════

def _estimate_f0(signal, fs, f_min=60, f_max=800):
    """
    Oceni osnovno frekvenco (F0) z avtokorelacijsko metodo.
    Vrne oceno v Hz; privzeto 150 Hz ob neuspehu.
    """
    lag_min = max(1, int(round(fs / f_max)))
    lag_max = int(round(fs / f_min))

    # Vzemi stabilen sredinski odsek
    start = len(signal) // 4
    seg = signal[start: start + min(8192, len(signal) // 2)]

    if len(seg) < lag_max * 2:
        return 150.0

    corr = np.correlate(seg, seg, mode='full')
    corr = corr[len(corr) // 2:]

    lag_max = min(lag_max, len(corr) - 1)
    peak = np.argmax(corr[lag_min: lag_max + 1]) + lag_min

    return float(fs) / peak if peak > 0 else 150.0


def plot_signal_pair(signal, fs, title, n_periods=4, f0=None, figsize=(14, 4)):
    """
    Izriše celoten signal in kratki odsek (n_periods period) eden ob drugem.

    Parametri
    ---------
    signal    : np.ndarray
    fs        : vzorčevalna frekvenca [Hz]
    title     : naslov grafa
    n_periods : število period v kratkem odseku
    f0        : osnovna frekvenca [Hz]; če None, se oceni samodejno
    figsize   : velikost slike

    Vrne
    ----
    (fig, (ax_full, ax_short))
    """
    if f0 is None:
        f0 = _estimate_f0(signal, fs)

    period_samples = int(round(fs / f0))
    t_full = np.arange(len(signal)) / fs

    # Kratki odsek: začni pri 10 % signala za stabilnost
    start = max(len(signal) // 10, period_samples)
    end   = min(start + n_periods * period_samples, len(signal))
    t_short = t_full[start:end]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Levi graf: celoten signal
    ax1.plot(t_full, signal, lw=0.7, color='steelblue')
    ax1.axvspan(t_short[0], t_short[-1],
                color='orange', alpha=0.25, label='Prikazan odsek')
    ax1.set_xlabel('Čas [s]', fontsize=12)
    ax1.set_ylabel('Amplituda [-]', fontsize=12)
    ax1.set_title(f'{title} – celoten signal', fontsize=13, fontweight='bold')
    ax1.tick_params(labelsize=11)
    ax1.grid(True, alpha=0.35)
    ax1.legend(fontsize=10)

    # Desni graf: kratki odsek
    ax2.plot(t_short, signal[start:end], lw=1.3, color='darkorange')
    ax2.set_xlabel('Čas [s]', fontsize=12)
    ax2.set_ylabel('Amplituda [-]', fontsize=12)
    ax2.set_title(
        f'{title} – {n_periods} periode  (f₀ ≈ {f0:.0f} Hz)',
        fontsize=13, fontweight='bold'
    )
    ax2.tick_params(labelsize=11)
    ax2.grid(True, alpha=0.35)

    plt.tight_layout()
    return fig, (ax1, ax2)


# ══════════════════════════════════════════════════════════════════════════════
# KRIŽNA KORELACIJA
# ══════════════════════════════════════════════════════════════════════════════

def cross_correlate(template, recording, fs, normalize=True):
    """
    Izračuna križno korelacijo med predlogo in posnetkom.

    Parametri
    ---------
    template  : np.ndarray – kratka referenca (npr. samoglasnik 'a')
    recording : np.ndarray – daljši signal (npr. 'erozija')
    fs        : vzorčevalna frekvenca [Hz]
    normalize : normalizacija na vrednosti [-1, 1]

    Vrne
    ----
    lags_s      : np.ndarray – zamiki [s]
    correlation : np.ndarray – vrednosti korelacije
    """
    corr = sp_signal.correlate(recording, template, mode='full')
    lags = sp_signal.correlation_lags(len(recording), len(template), mode='full')

    if normalize:
        denom = np.std(template) * np.std(recording) * np.sqrt(
            len(template) * len(recording)
        )
        if denom > 0:
            corr = corr / denom

    return lags / fs, corr


def find_vowel_onsets(template, recording, fs, threshold=0.25):
    """
    Poišče časovne nastope glasu (template) v posnetku (recording).

    Vrne
    ----
    onset_times : list[float] – časi nastopov [s] (samo pozitivni zamiki)
    lags_pos    : np.ndarray  – pozitivni zamiki [s]
    corr_pos    : np.ndarray  – korelacija pri pozitivnih zamikih
    """
    lags_s, corr = cross_correlate(template, recording, fs)

    mask = lags_s >= 0
    lags_pos = lags_s[mask]
    corr_pos = corr[mask]

    min_dist = int(0.08 * fs)  # minimalna razdalja med vrhovi: 80 ms
    peaks, _ = sp_signal.find_peaks(
        corr_pos, height=threshold, distance=min_dist
    )
    return lags_pos[peaks].tolist(), lags_pos, corr_pos
