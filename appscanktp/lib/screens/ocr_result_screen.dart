import 'package:flutter/material.dart';

class OcrResultScreen extends StatefulWidget {
  final String nik;
  final String nama;
  final String alamat;
  final String kelurahan;
  final String kecamatan;

  const OcrResultScreen({
    super.key,
    required this.nik,
    required this.nama,
    required this.alamat,
    required this.kelurahan,
    required this.kecamatan,
  });

  @override
  _OcrResultScreenState createState() => _OcrResultScreenState();
}

class _OcrResultScreenState extends State<OcrResultScreen> {
  late TextEditingController nikController;
  late TextEditingController namaController;
  late TextEditingController alamatController;
  late TextEditingController kelurahanController;
  late TextEditingController kecamatanController;

  @override
  void initState() {
    super.initState();
    nikController = TextEditingController(text: widget.nik);
    namaController = TextEditingController(text: widget.nama);
    alamatController = TextEditingController(text: widget.alamat);
    kelurahanController = TextEditingController(text: widget.kelurahan);
    kecamatanController = TextEditingController(text: widget.kecamatan);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Hasil OCR KTP')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: nikController,
              decoration: const InputDecoration(labelText: 'NIK'),
            ),
            TextField(
              controller: namaController,
              decoration: const InputDecoration(labelText: 'Nama'),
            ),
            TextField(
              controller: alamatController,
              decoration: const InputDecoration(labelText: 'Alamat'),
            ),
            TextField(
              controller: kelurahanController,
              decoration: const InputDecoration(labelText: 'Kelurahan'),
            ),
            TextField(
              controller: kecamatanController,
              decoration: const InputDecoration(labelText: 'Kecamatan'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                saveData();
              },
              child: const Text('Simpan'),
            ),
          ],
        ),
      ),
    );
  }

  void saveData() {
    String nik = nikController.text;
    String nama = namaController.text;
    String alamat = alamatController.text;
    String kelurahan = kelurahanController.text;
    String kecamatan = kecamatanController.text;

    print('NIK: $nik');
    print('Nama: $nama');
    print('Alamat: $alamat');
    print('Kelurahan: $kelurahan');
    print('Kecamatan: $kecamatan');

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Data berhasil disimpan!')),
    );
  }
}
