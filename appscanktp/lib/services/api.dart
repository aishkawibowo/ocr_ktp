import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

// URL Flask API
const String flaskApiUrl =
    'https://555e-36-66-204-110.ngrok-free.app/ocr'; // Ganti dengan URL ngrok jika perlu

// Fungsi untuk mengirim gambar ke API dan mendapatkan hasil OCR
Future<String?> sendImageToApi(File image) async {
  final url = Uri.parse(flaskApiUrl);
  final request = http.MultipartRequest('POST', url);

  // Tambahkan file gambar ke permintaan
  request.files.add(await http.MultipartFile.fromPath('image', image.path));

  try {
    final response = await request.send();

    if (response.statusCode == 200) {
      final responseBody = await response.stream.bytesToString();
      final jsonResponse = jsonDecode(responseBody);

      // Ambil hanya data yang diekstrak
      final extractedData = jsonResponse['extracted_data'];

      // Format hasil agar lebih rapi
      return '''
NIK: ${extractedData['nik'] ?? 'Tidak ditemukan'}
Nama: ${extractedData['nama'] ?? 'Tidak ditemukan'}
Alamat: ${extractedData['alamat'] ?? 'Tidak ditemukan'}
Kelurahan: ${extractedData['kelurahan'] ?? 'Tidak ditemukan'}
Kecamatan: ${extractedData['kecamatan'] ?? 'Tidak ditemukan'}
''';
    } else {
      return 'Error: ${response.statusCode}';
    }
  } catch (e) {
    return 'Error: $e';
  }
}
