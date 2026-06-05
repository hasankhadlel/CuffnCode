"""
=============================================================
OPSI A — Parallel Blood Pressure Signal Processing
Mata Kuliah: IFB 206 Komputasi Paralel - Itenas Bandung
=============================================================

Konsep:
- Simulasi sinyal tekanan darah oscillometric (seperti di CuffnCode)
- Proses filter sinyal secara SERIAL vs PARALEL
- Bandingkan waktu eksekusi keduanya

Sinyal yang diproses:
1. Raw pressure signal  -> Low-pass filter (buang noise frekuensi tinggi)
2. Oscillometric pulse  -> Envelope detection (cari puncak osilasi)
3. Derived HR signal    -> Peak detection (hitung detak jantung)
"""

import time
import random
import math
import multiprocessing
from multiprocessing import Pool

# ──────────────────────────────────────────────
# 1. PEMBUAT SINYAL SIMULASI (meniru sensor CuffnCode)
# ──────────────────────────────────────────────

def generate_pressure_signal(n_samples=5000):
    """Simulasi raw pressure signal dari sensor MPS20N0040D."""
    signal = []
    for i in range(n_samples):
        t = i / 1000.0  # waktu dalam detik
        # Tekanan dasar yang turun perlahan (deflation)
        baseline = 160 * math.exp(-0.3 * t)
        # Osilasi akibat detak jantung (~70 bpm = ~1.17 Hz)
        pulse = 5 * math.sin(2 * math.pi * 1.17 * t) * math.exp(-0.1 * t)
        # Noise random
        noise = random.gauss(0, 0.5)
        signal.append(baseline + pulse + noise)
    return signal

def generate_oscillometric_signal(n_samples=5000):
    """Simulasi sinyal osilometrik (amplitudo osilasi)."""
    signal = []
    for i in range(n_samples):
        t = i / 1000.0
        envelope = 8 * math.exp(-((t - 1.5)**2) / 0.5)  # bentuk lonceng
        pulse = envelope * math.sin(2 * math.pi * 1.17 * t)
        noise = random.gauss(0, 0.2)
        signal.append(pulse + noise)
    return signal

def generate_hr_signal(n_samples=5000):
    """Simulasi sinyal detak jantung dari sensor."""
    signal = []
    for i in range(n_samples):
        t = i / 1000.0
        hr = math.sin(2 * math.pi * 1.17 * t) + 0.3 * math.sin(2 * math.pi * 2.34 * t)
        noise = random.gauss(0, 0.1)
        signal.append(hr + noise)
    return signal


# ──────────────────────────────────────────────
# 2. FUNGSI PEMROSESAN SINYAL
# ──────────────────────────────────────────────

def low_pass_filter(signal, cutoff=0.3):
    """
    Low-pass filter sederhana (moving average + exponential smoothing).
    Tujuan: buang noise frekuensi tinggi dari sinyal tekanan.
    """
    print(f"  [Filter] Memproses Low-Pass Filter ({len(signal)} sampel)...")
    time.sleep(1.5)  # simulasi waktu komputasi berat

    filtered = []
    alpha = cutoff  # smoothing factor
    prev = signal[0]
    for val in signal:
        smoothed = alpha * val + (1 - alpha) * prev
        filtered.append(smoothed)
        prev = smoothed

    # Hitung statistik
    mean_val = sum(filtered) / len(filtered)
    max_val = max(filtered)
    min_val = min(filtered)
    print(f"  [Filter] Selesai! Mean={mean_val:.2f}, Max={max_val:.2f}, Min={min_val:.2f}")
    return {"type": "low_pass", "mean": mean_val, "max": max_val, "min": min_val}


def envelope_detection(signal):
    """
    Envelope detection untuk sinyal osilometrik.
    Tujuan: temukan amplitudo osilasi maksimum (MAP = Mean Arterial Pressure).
    """
    print(f"  [Envelope] Memproses Envelope Detection ({len(signal)} sampel)...")
    time.sleep(2.0)  # simulasi waktu komputasi berat

    # Rectify (ambil nilai absolut) lalu smoothing
    rectified = [abs(v) for v in signal]
    envelope = []
    window = 50
    for i in range(len(rectified)):
        start = max(0, i - window)
        avg = sum(rectified[start:i+1]) / (i - start + 1)
        envelope.append(avg)

    max_envelope = max(envelope)
    idx_max = envelope.index(max_envelope)
    print(f"  [Envelope] Selesai! Amplitudo max={max_envelope:.2f} pada indeks={idx_max}")
    return {"type": "envelope", "max_amplitude": max_envelope, "index_max": idx_max}


def peak_detection(signal, threshold=0.5):
    """
    Peak detection untuk menghitung Heart Rate.
    Tujuan: hitung jumlah detak per menit dari sinyal HR.
    """
    print(f"  [Peak] Memproses Peak Detection ({len(signal)} sampel)...")
    time.sleep(1.8)  # simulasi waktu komputasi berat

    peaks = []
    for i in range(1, len(signal) - 1):
        if signal[i] > threshold and signal[i] > signal[i-1] and signal[i] > signal[i+1]:
            peaks.append(i)

    # Hitung HR (asumsikan sampling rate 1000 Hz, sinyal 5 detik)
    duration_sec = len(signal) / 1000.0
    heart_rate = (len(peaks) / duration_sec) * 60
    print(f"  [Peak] Selesai! Ditemukan {len(peaks)} puncak, Heart Rate ≈ {heart_rate:.1f} bpm")
    return {"type": "peak", "n_peaks": len(peaks), "heart_rate_bpm": heart_rate}


# ──────────────────────────────────────────────
# 3. WRAPPER untuk multiprocessing
# ──────────────────────────────────────────────

def task_low_pass(signal):
    return low_pass_filter(signal)

def task_envelope(signal):
    return envelope_detection(signal)

def task_peak(signal):
    return peak_detection(signal)


# ──────────────────────────────────────────────
# 4. EKSEKUSI SERIAL
# ──────────────────────────────────────────────

def run_serial(signals):
    print("\n" + "="*55)
    print("  MODE SERIAL — Satu per satu")
    print("="*55)
    start = time.time()

    result1 = low_pass_filter(signals[0])
    result2 = envelope_detection(signals[1])
    result3 = peak_detection(signals[2])

    elapsed = time.time() - start
    print(f"\n  ✅ Serial selesai dalam {elapsed:.2f} detik")
    return elapsed, [result1, result2, result3]


# ──────────────────────────────────────────────
# 5. EKSEKUSI PARALEL
# ──────────────────────────────────────────────

def run_parallel(signals):
    print("\n" + "="*55)
    print("  MODE PARALEL — Semua sekaligus (multiprocessing)")
    print("="*55)
    start = time.time()

    with Pool(processes=3) as pool:
        # Jalankan ketiga fungsi secara paralel
        r1 = pool.apply_async(task_low_pass, (signals[0],))
        r2 = pool.apply_async(task_envelope, (signals[1],))
        r3 = pool.apply_async(task_peak, (signals[2],))

        result1 = r1.get()
        result2 = r2.get()
        result3 = r3.get()

    elapsed = time.time() - start
    print(f"\n  ✅ Paralel selesai dalam {elapsed:.2f} detik")
    return elapsed, [result1, result2, result3]


# ──────────────────────────────────────────────
# 6. MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║   CuffnCode — Parallel Signal Processing Demo       ║")
    print("║   IFB 206 Komputasi Paralel — Itenas Bandung        ║")
    print("╚══════════════════════════════════════════════════════╝")

    print("\n📡 Membuat sinyal simulasi dari sensor CuffnCode...")
    signals = [
        generate_pressure_signal(),
        generate_oscillometric_signal(),
        generate_hr_signal()
    ]
    print(f"   Sinyal 1 (Pressure): {len(signals[0])} sampel")
    print(f"   Sinyal 2 (Oscillometric): {len(signals[1])} sampel")
    print(f"   Sinyal 3 (Heart Rate): {len(signals[2])} sampel")

    # Jalankan Serial
    serial_time, serial_results = run_serial(signals)

    # Jalankan Paralel
    parallel_time, parallel_results = run_parallel(signals)

    # ── Ringkasan Perbandingan ──
    speedup = serial_time / parallel_time
    print("\n" + "="*55)
    print("  📊 RINGKASAN PERBANDINGAN")
    print("="*55)
    print(f"  Waktu Serial   : {serial_time:.2f} detik")
    print(f"  Waktu Paralel  : {parallel_time:.2f} detik")
    print(f"  Speedup        : {speedup:.2f}x lebih cepat")
    print(f"  Efisiensi      : {(speedup/3)*100:.1f}% (dari 3 core)")
    print()
    print("  Hasil Pemrosesan:")
    for r in parallel_results:
        if r["type"] == "low_pass":
            print(f"    🩺 Tekanan Darah — Mean: {r['mean']:.1f} mmHg")
        elif r["type"] == "envelope":
            print(f"    📈 Osilasi MAP   — Amplitudo Max: {r['max_amplitude']:.2f}")
        elif r["type"] == "peak":
            print(f"    ❤️  Heart Rate    — {r['heart_rate_bpm']:.1f} bpm")
    print("="*55)