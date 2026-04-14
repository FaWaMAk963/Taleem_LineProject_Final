import 'package:flutter/material.dart';
import 'screens/dial_screen.dart';

void main() {
  runApp(const TaleemLineApp());
}

class TaleemLineApp extends StatelessWidget {
  const TaleemLineApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: DialScreen(),
    );
  }
}