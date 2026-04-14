import 'package:flutter/material.dart';
import '../controllers/call_controller.dart';

class CallScreen extends StatefulWidget {
  @override
  State<CallScreen> createState() => _CallScreenState();
}

class _CallScreenState extends State<CallScreen> {
  final controller = CallController();

  @override
  void initState() {
    super.initState();
    controller.startCall(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: StreamBuilder<String>(
          stream: controller.status,
          builder: (context, snapshot) {
            return Text(
              snapshot.data ?? "Calling...",
              style: const TextStyle(color: Colors.white, fontSize: 22),
            );
          },
        ),
      ),
    );
  }
}