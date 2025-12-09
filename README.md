Modular Blockchain untuk Integritas Rekam Medis  
Proyek Tugas Besar Mata Kuliah **Kriptografi & Blockchain**  
Topik: **Modular Blockchain sebagai Integrity Layer untuk Cloud Data**  
Case yang digunakan: **CASE 2 – Rekam Medis Pasien Antar Klinik**


1. Konsep Umum Project
Sistem ini **tidak menggunakan public blockchain** seperti Bitcoin atau Ethereum.  
Sebagai gantinya, proyek ini membangun:

- Modular blockchain lokal (Python)
- Flask API sebagai layer input/output
- Postman untuk pengujian API
- Google Sheets sebagai *cloud display*
- Google Apps Script untuk sinkronisasi

Tujuan utama sistem adalah memastikan bahwa **rekam medis pasien tidak bisa dimanipulasi**, meskipun data yang berada di cloud (Google Sheets) sengaja diubah oleh pihak lain.

Prinsip:
- Blockchain lokal = **source of truth**
- Google Sheets = **tampilan cloud yang dapat dimanipulasi**
- Sistem harus bisa mendeteksi ketika cloud berubah dan tidak konsisten dengan blockchain lokal 


2. Arsitektur Sistem

POSTMAN (Input)
↓
Flask API (Python)
↓
Modular Blockchain Lokal
↓
Google Apps Script API
↓
Google Sheets (Cloud Display)

Penjelasan:
- Postman digunakan untuk memasukkan data rekam medis melalui endpoint /add_data
- Flask menyimpan data ke blockchain lokal
- Blockchain menghasilkan hash & prev_hash untuk menjamin integritas
- Data dikirim ke Google Sheets sebagai tampilan cloud
- Pada saat verifikasi, sistem membandingkan data blockchain dengan data cloud

 3. Case yang Digunakan: Rekam Medis Antar Klinik (CASE 2)
Skenario project ini mengikuti alur resmi Case 2 pada modul tugas besar:

1. Klinik A melakukan pemeriksaan awal pasien  
2. Data masuk ke blockchain lokal  
3. Data ditampilkan di Google Sheets  
4. Google Sheets dapat diubah manual untuk simulasi manipulasi  
5. Sistem melakukan verifikasi dan mendeteksi ketidaksesuaian 

 Data yang Dicatat
- ID Pasien  
- Klinik Pemeriksa  
- Diagnosa  
- Obat / Penanganan  
- Dokter pemeriksa  
- Tanggal periksa  

 Minimal 4 Blok:
1. Pemeriksaan awal di Klinik A  
2. Rujukan ke Klinik B  
3. Pengobatan lanjutan  
4. Pemeriksaan kontrol  

Memiliki banyak blok diperlukan agar blockchain dapat diuji konsistensinya.


 4. Struktur Blok (Case 2)

{
  "block_id": 3,
  "patient_id": "PSN-001",
  "clinic_name": "Klinik Sehat Sentosa",
  "diagnosis": "Hipertensi",
  "treatment": "Obat Amlodipine",
  "tanggal": "2025-12-08 09:30:00",
  "doctor": "Dr. Andi",
  "prev_hash": "ab91f10c22...",
  "current_hash": "e21cbb90a1..."
}
Elemen penting:
•	current_hash dibuat dari seluruh isi block menggunakan SHA-256
•	prev_hash menghubungkan block sebelumnya → terbentuklah rantai blockchain
5. Endpoint Wajib Sistem
Mengikuti spesifikasi resmi tugas besar :
1. POST /add_data
Menambahkan block baru ke blockchain.
2. GET /get_chain
Mengambil seluruh blockchain (seluruh blok).
3. GET /verify_chain
Memeriksa validitas blockchain (cek prev_hash dan current_hash).
4. GET /detect_cloud_tampering
Mendeteksi apakah data di Google Sheets telah diubah dan berbeda dari blockchain.
6. Cara Kerja Blockchain dalam Sistem
1.	Setiap block memiliki hash unik (SHA-256) berdasarkan isi datanya.
2.	Jika satu karakter dalam block berubah, hash berubah total → Sistem mendeteksinya.
3.	Block berikutnya menyimpan prev_hash dari block sebelumnya.
4.	Ini membentuk rantai yang tidak dapat diubah tanpa merusak seluruh struktur chain.
5.	Sehingga blockchain lokal berfungsi sebagai lapisan integritas bagi data cloud.

7. Instalasi & Menjalankan Program
1. Clone repository
git clone <repository-url>
cd <project-folder>
2. Install dependencies
pip install flask hashlib requests
Jika disediakan file requirements.txt:
pip install -r requirements.txt
3. Jalankan server Flask
python app.py
Server berjalan pada:
http://localhost:5000
8. Dokumentasi Endpoint
POST /add_data
Menambahkan blok baru.
Contoh request body:
{
  "block_id": 1,
  "patient_id": "PSN-001",
  "clinic_name": "Klinik A Sehat",
  "diagnosis": "Hipertensi ringan",
  "treatment": "Amlodipine 5mg",
  "tanggal": "2025-12-01 09:00:00",
  "doctor": "Dr. Budi",
  "prev_hash": "0"
}
GET /get_chain
Mengembalikan isi blockchain.
Contoh response:
[
  { "block_id": 1, ... },
  { "block_id": 2, ... }
]
GET /verify_chain
Mengecek integritas blockchain.
Contoh output:
{
  "status": "valid",
  "message": "All blocks are consistent."
}
Jika ada manipulasi:
{
  "status": "invalid",
  "message": "Hash mismatch at block 3"
}
GET /detect_cloud_tampering
Mendeteksi apakah data Google Sheets sudah diubah.
Contoh output:
{
  "status": "tampered",
  "detail": "Cloud data does not match blockchain at block 2"
}
9. Pengiriman Data ke Google Sheets
Proses sinkronisasi mengikuti alur tugas besar:
1.	Flask mengirim data menggunakan requests.post() ke Google Apps Script
2.	Apps Script menerima request dan memasukkan data ke Google Sheets
3.	Google Sheets menjadi tampilan cloud yang bisa dimanipulasi
4.	Sistem melakukan pengecekan perbedaan antara blockchain & cloud
10. Uji Normal & Simulasi Kecurangan
Uji Normal
•	Input data melalui Postman (POST /add_data)
•	Periksa chain (GET /get_chain)
Simulasi Manipulasi
1.	Ubah data langsung di Google Sheets (simulasi kecurangan admin cloud)
2.	Jalankan endpoint:
3.	GET /verify_chain
4.	GET /detect_cloud_tampering
5.	Sistem harus dapat mendeteksi perbedaan data
11. Struktur Folder 
├── app.py
├── blockchain.py
├── data.json
├── google_script.js
├── requirements.txt
└── README.md
