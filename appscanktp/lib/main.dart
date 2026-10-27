import 'package:flutter/material.dart';
import 'screens/home.dart'; // Pastikan import HomeScreen dari folder screens
import 'screens/nextpage.dart'; 

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Aktifkan rendering software untuk kompatibilitas lebih baik
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OCR KTP',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomeScreen(), // Pastikan HomeScreen sudah dipanggil di sini
    );
  }
}
