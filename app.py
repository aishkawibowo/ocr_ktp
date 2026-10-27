from flask import Flask, request, jsonify
import os
import cv2
import re
import easyocr
import base64
import time
import logging
from difflib import get_close_matches

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
# Fungsi untuk membersihkan dan menormalisasi teks hasil OCR
def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\b[A-Z0-9]\b', '', text)
    text = re.sub(r'[^\w\s.,]', '', text)
    text = text.strip()
    return text.capitalize()

# Fungsi untuk melakukan OCR pada gambar menggunakan EasyOCR
def ocr_on_ktp(image):
    reader = easyocr.Reader(['id'], gpu=True)  # GPU False untuk menghindari overhead jika tidak ada GPU
    result = reader.readtext(image, detail=0, paragraph=True)  # detail=0 untuk mempercepat output
    if result:
        ocr_text = " ".join(result)
    else:
        ocr_text = "Tidak ada teks yang terdeteksi."
    return normalize_text(ocr_text)


# Data kecamatan dan kelurahan/desa berdasarkan daftar dari file
kecamatan_desa = {
    "Tarik": ["Mergobener", "Kendalsewu", "Kalimati", "Gempolklutuk", "Kedinding", "Mergosari", "Kemuning", "Segodobancang", "Janti", "Singogalih", "Kedungbacok", "Gampingrowo", "Mindugading", "Sebani", "Kramattemenggung", "Tarik", "Klantingsari", "Banjarwungu", "Balongmacekan", "Mliriprowo"],
    "Prambon": ["Prambon", "Kedungwonokerto", "Bendotretek", "Watutulis", "Simogirang", "Wonoplintahan", "Cangkringturi", "Jatialun-alun", "Jatikalang", "Gampang", "Bulang", "Simpang", "Wirobiting", "Kedungkembar", "Kedungsugo", "Gedangrowo", "Kajartengguli", "Temu", "Jedongcangkring", "Pejangkungan", "Jedongcangkring"],
    "Krembung": ["Krembung", "Mojoruntut", "Lemujut", "Cangkring", "Keret", "Balonggarut", "Kandangan", "Tanjekwagir", "Gading", "Rejeni", "Ploso", "Waung", "Kedungsumur", "Keper", "Wangkal", "Tambakrejo", "Wonomlati", "Kedungrawan", "Jenggot"],
    "Porong": ["Kel. Juwetkenongo", "Kel. Gedang", "Kel. Porong", "Glagaharum", "Pamotan", "Plumbon", "Kel. Mindi", "Kel. Siring", "Kebonagung", "Renokenongo", "Kedungsolo", "Kebakalan", "Kesambi", "Candipari", "Lajuk", "Kedungboto", "Kel. Jatirejo", "Wunut", "Pesawahan"],
    "Jabon": ["Jemirahan", "Balongtani", "Tambakkalisongo", "Kupang", "Kedungpandan", "Kedungrejo", "Trompoasri", "Dukuhsari", "Kedungcangkring", "Besuki", "Keboguyang", "Pejarakan", "Semambung", "Panggreh", "Permisan"],
    "Tanggulangin": ["Kedensari", "Kalisampurno", "Ketapang", "Kedungbendo", "Sentul", "Penatarsewu", "Banjarasri", "Banjarpanji", "Kalidawir", "Putat", "Ngaban", "Kalitengah", "Kludan", "Ketegan", "Ganggangpanjang", "Randegan", "Gempolsari", "Kedungbanteng", "Boro"],
    "Candi": ["Kedungkendo", "Karangtanjung", "Sugihwaras", "Gelam", "Sumorame", "Ngampelsari", "Balonggabus", "Balongdowo", "Kendalpecabean", "Kedungpeluk", "Klurak", "Kebonsari", "Candi", "Blingo", "Larangan", "Tenggulunan", "Sepande", "Sumokali", "Wedoroklurak", "Durungbedug", "Sidodadi", "Jambangan", "Durungbanjar"],
    "Sidoarjo": ["Magersari", "Sidoklumpuk", "Lemahputro", "Pekauman", "Sidokare", "Bulusidokare", "Celep", "Sekardangan", "Gebang", "Urangagung", "Lebo", "Suko", "Banjarbendo", "Rangkahkidul", "Kemiri", "Jati", "Cemengbakalan", "Sarirogo", "Pucang", "Sidokumpul", "Pucanganom", "Cemengkalang", "Blurukidul", "Sumput"],
    "Tulangan": ["Kemantren", "Medalem", "Kepatihan", "Gelang", "Kepadangan", "Singopadu", "Kajeksan", "Grinting", "Modong", "Grabagan", "Kepunten", "Janti", "Tlasih", "Pangkemiri", "Jiken", "Grogol", "Kedondong", "Tulangan", "Kenongo", "Kepuhkemiri", "Kebaron", "Sudimoro"],
    "Wonoayu": ["Wonoayu", "Popoh", "Jimbarankulon", "Ketimang", "Ploso", "Lambangan", "Sawocangkring", "Karangpuri", "Plaosan", "Candinegoro", "Mulyodadi", "Wonokalang", "Semambung", "Simoketawang", "Tanggul", "Wonokasian", "Mojorangagung", "Sumberrejo", "Pilang", "Jimbaranwetan", "Becirongengor", "Pagerngumbuk", "Simoangin-angin", "Jimbaran Wetan"],
    "Krian": ["Kel. Krian", "Kel. Tambakkemerakan", "Kel. Kemasan", "Kraton", "Sidomojo", "Watugolong", "Barengkrajan", "Sidorejo", "Keboharan", "Terungwetan", "Terungkulon", "Ponokawan", "Junwangi", "Gamping", "Jerukgamping", "Katerungan", "Tropodo", "Sidomulyo", "Tempel", "Jatikalang", "Terik", "Sedenganmijen"],
    "Balongbendo": ["Singkalan", "Bakungtemenggungan", "Sumokembangsri", "Seduri", "Wonokupang", "Bakalanwringinpitu", "Gagangkepuhsari", "Suwaluh", "Watesari", "Seketi", "Jabaran", "Balongbendo", "Jeruklegi", "Wonokarang", "Bakungpringgodani", "Bogempinggir", "Kedungsukodani", "Waruberon", "Kemangsen", "Penambangan"],
    "Taman": ["Kel. Taman", "Kel. Ketegan", "Kel. Wonocolo", "Kel. Bebekan", "Kel. Ngelom", "Kel. Kalijaten", "Kedungturi", "Kletek", "Jemundo", "Sadang", "Gilang", "Tawangsari", "Krembangan", "Tanjungsari", "Sidodadi", "Kramatjegu", "Trosobo", "Bohar", "Wage", "Kel. Sepanjang", "Kel. Geluran", "Sambibulu", "Bringinbendo", "Pertapanmaduretno"],
    "Sukodono": ["Wilayut", "Anggaswangi", "Jumputrejo", "Suruh", "Pekarungan", "Cangkringsari", "Jogosatru", "Ngaresrejo", "Sambungrejo", "Sukodono", "Kloposepuluh", "Masanganwetan", "Suko", "Panjunan", "Bangsri", "Kebonagung", "Pademonegoro", "Plumbungan", "Masangankulon"],
    "Buduran": ["Entalsewu", "Pagerwojo", "Sidokerto", "Siwalanpanji", "Sidomulyo", "Prasung", "Sawohan", "Dukuhtengah", "Banjarsari", "Wadungasih", "Sukorejo", "Sidokepung", "Buduran", "Damarsri", "Banjarkemantren"],
    "Gedangan": ["Keboansikep", "Keboananom", "Ganting", "Karangbong", "Tebel", "Punggul", "Kragan", "Wedi", "Ketajen", "Semambung", "Sawotratap", "Bangah", "Gedangan", "Sruni", "Gemurung"],
    "Sedati": ["Kwangsan", "Pepe", "Kalanganyar", "Tambakcemandi", "Gisikcemandi", "Cemandi", "Buncitan", "Pulungan", "Betro", "Sedatiagung", "Sedatigede", "Pabean", "Semampir", "Pranti", "Segorotambak", "Banjarkemuning"],
    "Waru": ["Pepelegi", "Medaeng", "Waru", "Kureksari", "Tropodo", "Tambaksawah", "Tambakrejo", "Tambakoso", "Wadungasri", "Berbek", "Kepuhkiriman", "Wedoro", "Kedungrejo", "Bungurasih", "Ngingas", "Tambaksumur", "Janti"],
    "lainnya": ["lainnya : (diluar Kab. Sidoarjo)"]
}

# Jika kecamatan/kelurahan tidak ada dalam daftar, tampilkan "diluar Kab. Sidoarjo"
OUT_OF_SIDOARJO = "lainnya : (diluar Kab. Sidoarjo)"

def extract_data_from_ocr(ocr_text):
    data = {
        "nik": None,
        "nama": None,
        "alamat": None,
        "kelurahan": None,
        "kecamatan": None
    }

    # Cari NIK (16 digit angka)
    nik_match = re.search(r'\b\d{16}\b', ocr_text)
    if nik_match:
        data["nik"] = nik_match.group()

    # Cari Nama (batasi jumlah kata sebelum "lahir" atau angka tanggal)
    nama_match = re.search(r'nama\s+([\w\s]+?)(?=\s*lahir|\s*temp[a-z]*\s*tgl|\s\d{2,4})', ocr_text, re.IGNORECASE)

    # Jika regex gagal, gunakan metode alternatif dengan batas kata
    if not nama_match:
        nama_match = re.search(r'nama\s+([\w\s]+)', ocr_text, re.IGNORECASE)

    # Simpan hasil nama jika ditemukan
    if nama_match:
        nama = nama_match.group(1).strip().title()
        # Hapus kata "Tempaulgilahir" dan sejenisnya jika masih masuk
        nama = re.sub(r'\btemp[a-z]*\s*tgl?\s*lahir\b', '', nama, flags=re.IGNORECASE).strip()
        # Batasi nama maksimal 3 kata agar tidak menangkap tempat lahir
        data["nama"] = " ".join(nama.split()[:3])


    # Cari Alamat (berhenti sebelum kata kunci "kelurahan" atau "kecamatan")
    alamat_match = re.search(r'alamat\s+([\w\s.,-]+?)(?:\s+keldesa|\s+kelurahan|\s+kecamatan)', ocr_text, re.IGNORECASE)
    if alamat_match:
        alamat_cleaned = re.sub(r'\b(rt|rw|rtrw|rt/rw|r\.t|r\.w)\b\s*\d+(\s*\d+)?', '', alamat_match.group(1), flags=re.IGNORECASE)
        data["alamat"] = alamat_cleaned.strip().title()

    # Cari Kecamatan
    kecamatan_match = re.search(r'kecamatan\s+([\w\s]+?)(?:\s+agama|\s+stalus|\s+status|\s+pekerjaan|\s+kewarganegaraan)', ocr_text, re.IGNORECASE)
    if kecamatan_match:
        data["kecamatan"] = kecamatan_match.group(1).strip().title()

    # Cari Kelurahan/Desa
    kelurahan_match = re.search(r'(?:kelurahan|desa)\s+([\w\s]+?)\s+kecamatan', ocr_text, re.IGNORECASE)
    if kelurahan_match:
        data["kelurahan"] = kelurahan_match.group(1).strip().title()

    # Jika kecamatan tidak terdeteksi oleh regex, biarkan null
    if not data["kecamatan"]:
        data["kecamatan"] = None
        data["kelurahan"] = None  # Jika kecamatan tidak ada, kelurahan juga tidak ada
        return data

    # Jika kecamatan ditemukan tetapi tidak ada dalam daftar, ubah jadi "diluar Kab. Sidoarjo"
    if data["kecamatan"] not in kecamatan_desa:
        data["kecamatan"] = OUT_OF_SIDOARJO
        data["kelurahan"] = OUT_OF_SIDOARJO
        return data

    # Jika kecamatan valid tetapi kelurahan tidak ditemukan, ubah jadi "diluar Kab. Sidoarjo"
    if data["kelurahan"] and data["kelurahan"] not in kecamatan_desa[data["kecamatan"]]:
        data["kelurahan"] = OUT_OF_SIDOARJO

    return data

# Fungsi untuk mengubah gambar menjadi base64 untuk ditampilkan di browser
def convert_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        app.logger.error("No image uploaded!")  # Log error jika tidak ada gambar
        return jsonify({'error': 'No image uploaded!', 'message': 'Foto tidak berhasil dimuat'}), 400

    start_time = time.time()  # Mulai hitung waktu

    # Simpan file gambar sementara
    image_file = request.files['image']
    image_path = "temp.jpg"
    image_file.save(image_path)

    # Baca gambar dengan OpenCV
    image = cv2.imread(image_path)
    if image is None:
        app.logger.error("Failed to load image!")  # Log error jika gambar gagal dimuat
        return jsonify({'error': 'Failed to load image!', 'message': 'Foto tidak berhasil dimuat'}), 500
    
    print("Foto berhasil dimuat", flush=True)

    # Resize gambar agar lebih kecil untuk mempercepat OCR
    height, width = image.shape[:2]
    image = cv2.resize(image, (width // 2, height // 2))

    # Lakukan OCR
    print("Foto sedang di proses", flush=True)
    ocr_text = ocr_on_ktp(image)
    print(f"OCR Result: {ocr_text}", flush=True)
    
    extracted_data = extract_data_from_ocr(ocr_text)
    print(f"Extracted Data: {extracted_data}", flush=True)
    
    # Hapus file sementara
    os.remove(image_path)

    end_time = time.time()  # Akhir hitung waktu
    print(f"Time taken: {end_time - start_time} seconds")  # Tampilkan waktu ke log

    # Kembalikan hasil sebagai JSON
    return jsonify({
        'ocr_text': ocr_text,
        'extracted_data': extracted_data
    })

# Fungsi untuk mengubah gambar menjadi base64 untuk ditampilkan di browser
def convert_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/camera', methods=['GET'])
def camera():
#     cap = cv2.VideoCapture(0)  # Ganti dengan 1 jika menggunakan kamera eksternal
#     if not cap.isOpened():
#         return jsonify({'error': 'Cannot access the camera!'}), 500

#     # Ambil gambar hanya dalam waktu singkat
#     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Pastikan buffer kamera kecil
#     cap.set(cv2.CAP_PROP_FPS, 30)       # Atur frame rate tinggi

    # ret, frame = cap.read()
    # if not ret:
    #     cap.release()
    #     return jsonify({'error': 'Failed to read frame!'}), 500

    # # Resize gambar untuk mengurangi ukuran file
    # frame = cv2.resize(frame, (640, 480))
    # frame_base64 = convert_image_to_base64(frame)
    
        # HTML template untuk menampilkan form upload gambar dari file explorer
    html = '''
    <html>
        <body>
            <h1>Upload Image for OCR</h1>
            <form method="post" action="/ocr" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required />
                <button type="submit">Upload and OCR</button>
            </form>
        </body>
    </html>
    '''
    return html

    # HTML template untuk menampilkan gambar dari kamera
    # html = f'''
    # <html>
    #     <body>
    #         <h1>Real-time Camera Feed</h1>
    #         <img src="data:image/jpeg;base64,{frame_base64}" />
    #         <form method="post" action="/ocr" enctype="multipart/form-data">
    #             <input type="file" name="image" />
    #             <button type="submit">Upload and OCR</button>
    #         </form>
    #     </body>
    # </html>
    # '''

    cap.release()
    return html


# if __name__ == '__main__':
#     port = int(os.getenv("PORT", 3000))
#     app.run(host='ujicoba.sidoarjokab.go.id', port=port, debug=True)
if __name__ == '__main__':
    app.run(debug=True)
    