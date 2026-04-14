import 'package:flutter/material.dart';
import 'call_screen.dart';

class DialScreen extends StatefulWidget {
  @override
  State<DialScreen> createState() => _DialScreenState();
}

class _DialScreenState extends State<DialScreen> {
  String input = "";

  void pressKey(String value) {
    setState(() {
      input += value;
    });

    if (input == "17") {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => CallScreen()),
      );
    }
  }

  Widget button(String text) {
    return ElevatedButton(
      onPressed: () => pressKey(text),
      child: Text(text),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(input, style: const TextStyle(color: Colors.white, fontSize: 30)),

          Wrap(
            children: List.generate(10, (i) {
              return button(i.toString());
            }),
          ),
        ],
      ),
    );
  }
}