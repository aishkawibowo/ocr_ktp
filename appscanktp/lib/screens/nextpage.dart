import 'dart:io';
import 'package:flutter/material.dart';
import '../services/api.dart'; // Pastikan api.dart sudah benar diimpor

class Nextpage extends StatefulWidget {
  final File? imageFile; // Menerima gambar dari halaman sebelumnya

  Nextpage({this.imageFile});

  @override
  _NextpageState createState() => _NextpageState();
}

class _NextpageState extends State<Nextpage> {
  final formKey = GlobalKey<FormState>();

  // Controllers untuk mengisi otomatis data OCR
  TextEditingController nikController = TextEditingController();
  TextEditingController namaController = TextEditingController();
  TextEditingController alamatController = TextEditingController();
  TextEditingController kelurahanController = TextEditingController();
  TextEditingController kecamatanController = TextEditingController();

  bool _isLoading = false; // Untuk loading indikator

  @override
  void initState() {
    super.initState();
    if (widget.imageFile != null) {
      _fillFieldsWithOcrResult(widget.imageFile!);
    }
  }

  // Fungsi untuk mengambil hasil OCR dari API dan mengisi field
  Future<void> _fillFieldsWithOcrResult(File image) async {
    setState(() {
      _isLoading = true;
    });

    String? ocrResult = await sendImageToApi(image);

    setState(() {
      _isLoading = false;
    });

    if (ocrResult != null) {
      // Parsing hasil OCR untuk mengisi field
      List<String> lines = ocrResult.split('\n');
      if (lines.length >= 5) {
        nikController.text = lines[0].split(':')[1].trim();
        namaController.text = lines[1].split(':')[1].trim();
        alamatController.text = lines[2].split(':')[1].trim();
        kelurahanController.text = lines[3].split(':')[1].trim();
        kecamatanController.text = lines[4].split(':')[1].trim();
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Gagal mendapatkan data OCR")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final double height = MediaQuery.of(context).size.height;

    return Scaffold(
      appBar: AppBar(
        title: Text("Data Diri"),
        backgroundColor: const Color.fromRGBO(219, 15, 15, 1),
      ),
      backgroundColor: Colors.white,
      body: _isLoading
          ? Center(child: CircularProgressIndicator()) // Loading indikator
          : Padding(
              padding: const EdgeInsets.all(20.0),
              child: Form(
                key: formKey,
                child: ListView(
                  children: [
                    SizedBox(height: height * 0.02),
                    Text(
                      "Data Diri",
                      style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: const Color.fromRGBO(219, 15, 15, 1)),
                    ),
                    SizedBox(height: height * 0.02),
                    Text(
                      "Silakan periksa dan perbaiki jika ada kesalahan",
                      style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.normal,
                          color: Colors.black),
                    ),
                    SizedBox(height: height * 0.03),
                    // Field NIK
                    TextFormField(
                      controller: nikController,
                      decoration: InputDecoration(labelText: "NIK"),
                      validator: (value) {
                        if (value!.isEmpty) return "Masukkan NIK";
                        return null;
                      },
                    ),
                    SizedBox(height: height * 0.03),

                    // Field Nama
                    TextFormField(
                      controller: namaController,
                      decoration: InputDecoration(labelText: "Nama"),
                      validator: (value) {
                        if (value!.isEmpty) return "Masukkan Nama";
                        return null;
                      },
                    ),
                    SizedBox(height: height * 0.03),

                    // Field Alamat
                    TextFormField(
                      controller: alamatController,
                      decoration: InputDecoration(labelText: "Alamat"),
                      validator: (value) {
                        if (value!.isEmpty) return "Masukkan Alamat";
                        return null;
                      },
                    ),
                    SizedBox(height: height * 0.03),

                    // Field Kelurahan
                    TextFormField(
                      controller: kelurahanController,
                      decoration: InputDecoration(labelText: "Kelurahan"),
                      validator: (value) {
                        if (value!.isEmpty) return "Masukkan Kelurahan";
                        return null;
                      },
                    ),
                    SizedBox(height: height * 0.03),

                    // Field Kecamatan
                    TextFormField(
                      controller: kecamatanController,
                      decoration: InputDecoration(labelText: "Kecamatan"),
                      validator: (value) {
                        if (value!.isEmpty) return "Masukkan Kecamatan";
                        return null;
                      },
                    ),
                    SizedBox(height: height * 0.03),
                    ElevatedButton(
                      onPressed: () {
                        if (formKey.currentState!.validate()) {
                          // Simpan atau lanjutkan proses
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text("Data berhasil disimpan!")),
                          );
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color.fromRGBO(219, 15, 15, 1),
                        padding: EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child:
                          Text("Simpan Data", style: TextStyle(fontSize: 18, color: Colors.white)),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
