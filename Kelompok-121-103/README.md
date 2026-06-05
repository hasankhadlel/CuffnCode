# Parallel Blood Pressure Signal Processing

## Kelompok 121-103

### Mata Kuliah
IFB 206 Komputasi Paralel

### Anggota Kelompok
- Hasan Khadlel Qostholani
- Muhammad Adrian Maulana

### Deskripsi Proyek
Proyek ini mensimulasikan pemrosesan sinyal tekanan darah (blood pressure signal processing) menggunakan Python. Program membandingkan performa pemrosesan sinyal secara serial dan paralel dengan memanfaatkan multiprocessing.

### Fitur
- Low Pass Filter
- Envelope Detection
- Peak Detection
- Perbandingan Eksekusi Serial dan Paralel
- Perhitungan Speedup dan Efisiensi

### Teknologi yang Digunakan
- Python 3
- Multiprocessing
- Math Library
- Time Library

### Cara Menjalankan Program

```bash
python main.py
```

### Hasil Program
Program menampilkan:
- Waktu eksekusi serial
- Waktu eksekusi paralel
- Speedup
- Efisiensi penggunaan core
- Hasil pemrosesan sinyal tekanan darah

### Kesimpulan
Implementasi multiprocessing memungkinkan beberapa proses pemrosesan sinyal dijalankan secara bersamaan sehingga waktu eksekusi lebih cepat dibandingkan metode serial.
