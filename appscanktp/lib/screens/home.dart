import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api.dart';
import 'nextpage.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  File? _image;
  String _ocrResult = "Hasil OCR akan muncul di sini";

  final ImagePicker _picker = ImagePicker();

  // Fungsi untuk memilih gambar dari galeri
  Future<void> _pickImage() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
      });
      await _sendToApi(File(pickedFile.path)); // Kirim gambar ke API
    }
  }

  // Fungsi untuk mengambil gambar dari kamera
// Fungsi untuk mengambil gambar dengan timer
Future<void> _takePhotoWithTimer(BuildContext context) async {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text("Foto akan diambil dalam 3 detik..."),
      duration: Duration(seconds: 3),
    ),
  );

  await Future.delayed(Duration(seconds: 3)); // Timer 3 detik

  final pickedFile = await _picker.pickImage(source: ImageSource.camera);
  if (pickedFile != null) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Nextpage(imageFile: File(pickedFile.path)),
      ),
    );
  }
}


  // Fungsi untuk mengirim gambar ke API
  Future<void> _sendToApi(File image) async {
    final result = await sendImageToApi(image); // Fungsi API dari api.dart
    setState(() {
      _ocrResult = result ?? 'Terjadi kesalahan saat memproses gambar.';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('OCR KTP'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            if (_image != null)
              Image.file(
                _image!,
                height: 200,
                fit: BoxFit.cover,
              ),
            SizedBox(height: 16),
            Text(
              _ocrResult,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.black87),
            ),
            Spacer(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // ElevatedButton.icon(
                //   onPressed: _pickImage,
                //   icon: Icon(Icons.photo),
                //   label: Text("Galeri"),
                // ),
                // ElevatedButton.icon(
                //   onPressed: _takePhoto,
                //   icon: Icon(Icons.camera),
                //   label: Text("Kamera"),
                // ),
                ElevatedButton.icon(
                  onPressed: () =>
                      _takePhotoWithTimer(context), // Pakai fungsi dengan timer
                  icon: Icon(Icons.camera),
                  label: Text("Kamera (3s Timer)"),
                ),

                ElevatedButton.icon(
                  onPressed: () async {
                    final pickedFile = await ImagePicker()
                        .pickImage(source: ImageSource.gallery);
                    if (pickedFile != null) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              Nextpage(imageFile: File(pickedFile.path)),
                        ),
                      );
                    }
                  },
                  icon: Icon(Icons.photo),
                  label: Text("Galeri"),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
