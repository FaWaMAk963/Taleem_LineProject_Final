import 'dart:async';
import 'package:flutter/material.dart';

import '../services/audio_service.dart';
import '../services/api_service.dart';
import '../models/call_state.dart';

class CallController {
  final AudioService audio = AudioService();
  final ApiService api = ApiService();

  final StreamController<String> _statusController =
      StreamController.broadcast();

  Stream<String> get status => _statusController.stream;

  CallState state = CallState.idle;

  void _update(CallState newState, String message) {
    state = newState;
    _statusController.add(message);
  }

  Future<void> startCall(BuildContext context) async {

    // 🔔 1. RINGING
    _update(CallState.ringing, "Ringing...");
    await audio.playRingtone();

    await Future.delayed(const Duration(seconds: 2));

    // 🌍 2. LANGUAGE SELECTION
    _update(CallState.languageSelect, "Select Language");

    await audio.speak(
      "Welcome to TaleemLine. Press 1 for English, 2 for Urdu, 3 for Pashto"
    );

    String lang = await audio.getFakeInput();

    String language = switch (lang) {
      "1" => "english",
      "2" => "urdu",
      "3" => "pashto",
      _ => "urdu"
    };

    // 🎮 3. MODE SELECTION
    _update(CallState.modeSelect, "Select Mode");

    await audio.speak(
      "Press 4 for Learning, 5 for Test, 6 for Game"
    );

    String modeInput = await audio.getFakeInput();

    String mode = switch (modeInput) {
      "4" => "learning",
      "5" => "test",
      "6" => "game",
      _ => "learning"
    };

    // 🟢 4. ACTIVE CONVERSATION
    _update(CallState.activeConversation, "Starting Conversation");

    String prompt = switch (mode) {
      "learning" => "What do you want to learn today?",
      "test" => "What topic should I test you on?",
      "game" => "Let's play a learning game! Choose a topic.",
      _ => "What do you want to learn today?"
    };

    await audio.speak(prompt);

    // 🎤 5. START VOICE LOOP
    audio.startVoiceLoop(language, mode, api);
  }

  void endCall() {
    _update(CallState.ended, "Call Ended");
  }

  void dispose() {
    _statusController.close();
  }
}