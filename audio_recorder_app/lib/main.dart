import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:http/http.dart' as http;

void main() {
  runApp(AudioRecorderApp());
}

class AudioRecorderApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Voice to Text Sender',
      home: SpeechToTextScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class SpeechToTextScreen extends StatefulWidget {
  @override
  _SpeechToTextScreenState createState() => _SpeechToTextScreenState();
}

class _SpeechToTextScreenState extends State<SpeechToTextScreen> {
  late stt.SpeechToText _speech;
  bool _isListening = false;
  String _text = '';
  bool _isSending = false;
  final List<String> _savedQuestions = [];

  final TextEditingController _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
  }

  void _listen() async {
    if (!_isListening) {
      bool available = await _speech.initialize(
        onStatus: (val) => print('Status: $val'),
        onError: (val) => print('Error: $val'),
      );
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (val) => setState(() {
            _text = val.recognizedWords;
            _textController.text = _text;
            _textController.selection = TextSelection.collapsed(offset: _text.length);
          }),
        );
      }
    } else {
      setState(() => _isListening = false);
      _speech.stop();
    }
  }

  void _saveCurrentText() {
    final trimmed = _textController.text.trim();
    if (trimmed.isNotEmpty) {
      setState(() {
        _savedQuestions.add(trimmed);
        _text = '';
        _textController.clear();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Question saved!')),
      );
    }
  }

  void _sendToStreamlit(String questionText, {int? indexToRemove}) async {
    setState(() => _isSending = true);

    final url = Uri.parse('https://receiver-api-314832503242.europe-west1.run.app/receive');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: '{"question_text": "${questionText.replaceAll('"', '\\"')}"}',
    );

    setState(() => _isSending = false);

    if (response.statusCode == 200) {
      if (indexToRemove != null) {
        setState(() => _savedQuestions.removeAt(indexToRemove));
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Sent to Question Management App!')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to send.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Question Speech2Text')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Editable transcription field
            TextField(
              controller: _textController,
              onChanged: (val) => _text = val,
              maxLines: null,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Transcribed Text (Editable)',
              ),
            ),
            const SizedBox(height: 12),

            // Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  icon: Icon(_isListening ? Icons.mic_off : Icons.mic),
                  label: Text(_isListening ? 'Stop' : 'Start'),
                  onPressed: _listen,
                ),
                ElevatedButton.icon(
                  icon: Icon(Icons.save),
                  label: Text('Save'),
                  onPressed: _saveCurrentText,
                ),
                ElevatedButton.icon(
                  icon: Icon(Icons.send),
                  label: _isSending ? Text('Sending...') : Text('Send'),
                  onPressed: _isSending || _textController.text.trim().isEmpty
                      ? null
                      : () => _sendToStreamlit(_textController.text.trim()),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Saved questions list
            Expanded(
              child: _savedQuestions.isEmpty
                  ? Center(child: Text('No saved questions yet.'))
                  : ListView.builder(
                      itemCount: _savedQuestions.length,
                      itemBuilder: (context, index) {
                        final question = _savedQuestions[index];
                        return Card(
                          margin: EdgeInsets.symmetric(vertical: 4),
                          child: ListTile(
                            title: Text(question),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: Icon(Icons.send),
                                  onPressed: _isSending
                                      ? null
                                      : () => _sendToStreamlit(question, indexToRemove: index),
                                ),
                                IconButton(
                                  icon: Icon(Icons.delete),
                                  onPressed: () {
                                    setState(() => _savedQuestions.removeAt(index));
                                  },
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
