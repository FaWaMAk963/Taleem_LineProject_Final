import 'dart:io';
import 'package:just_audio/just_audio.dart';
import 'package:record/record.dart';
import 'api_service.dart';

class AudioService {
  final player = AudioPlayer();
  final recorder = AudioRecorder();

  String filePath = "audio.wav";

  Future<void> playRingtone() async {
    await player.setAsset("assets/ring.mp3");
    player.play();
  }

  Future<void> speak(String text) async {
    print("AI VOICE: $text");
  }

  Future<String> getFakeInput() async {
    await Future.delayed(const Duration(seconds: 2));
    return "2"; // simulate button press
  }

  Future<void> startVoiceLoop(
    String language,
    String mode,
    ApiService api,
  ) async {

    while (true) {

      // 🎤 start recording
      await recorder.start(
        const RecordConfig(encoder: AudioEncoder.wav),
        path: filePath,
      );

      await Future.delayed(const Duration(seconds: 4));

      await recorder.stop();

      File audioFile = File(filePath);

      // 🌐 send to backend
      String response = await api.sendAudio(
        audioFile,
        language,
        mode,
      );

      // 🔊 speak response
      await speak(response);
    }
  }
}