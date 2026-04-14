import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {

  Future<String> sendAudio(
    File audio,
    String language,
    String mode,
  ) async {

    var request = http.MultipartRequest(
      'POST',
      Uri.parse("http://10.0.2.2:8000/process")
    );

    request.files.add(
      await http.MultipartFile.fromPath('file', audio.path)
    );

    request.fields['language'] = language;
    request.fields['mode'] = mode;

    var response = await request.send();

    return await response.stream.bytesToString();
  }
}