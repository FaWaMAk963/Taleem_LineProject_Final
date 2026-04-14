/// Represents the current stage of the AI phone call system.
///
/// This controls:
/// - UI display
/// - voice prompts
/// - recording behavior
/// - backend interaction flow

enum CallState {
  /// App is idle (no call active)
  idle,

  /// Phone is ringing (after dialing 177)
  ringing,

  /// Asking user to select language
  languageSelect,

  /// Asking user to select mode (learning/test/game)
  modeSelect,

  /// Main AI conversation is active
  activeConversation,

  /// User is speaking (recording audio)
  listening,

  /// AI is responding (TTS playing)
  speaking,

  /// Call has ended
  ended
}