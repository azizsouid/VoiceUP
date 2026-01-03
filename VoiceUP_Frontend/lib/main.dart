import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:onnxruntime_flutter/onnxruntime_flutter.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:path/path.dart' as p;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(
        body: Center(child: TranscriptionTest()),
      ),
    );
  }
}

class TranscriptionTest extends StatefulWidget {
  const TranscriptionTest({super.key});

  @override
  State<TranscriptionTest> createState() => _TranscriptionTestState();
}

class _TranscriptionTestState extends State<TranscriptionTest> {
  String _result = "Waiting for transcription...";

  @override
  void initState() {
    super.initState();
    _runTest();
  }

  Future<void> _runTest() async {
    try {
      // 1️⃣ Load ONNX model
      final session = await OrtSession.fromAsset('assets/models/tiny_whisper.onnx');

      // 2️⃣ Load audio file
      final filePath = p.join(Directory.current.path, 'audio_files', 'file.wav');
      final audioBytes = await File(filePath).readAsBytes();

      // 3️⃣ Convert audio to float32 tensor
      final inputTensor = await _preprocessAudio(audioBytes);

      // 4️⃣ Run ONNX model
      final output = await session.run({'input': inputTensor});

      // 5️⃣ Decode output (example stub)
      final transcription = _decodeOutput(output['output']);
      final confidence = _calculateConfidence(output['output']);

      setState(() {
        _result = "Transcription: $transcription\nConfidence: $confidence";
      });
    } catch (e) {
      setState(() {
        _result = "Error: $e";
      });
    }
  }

  /// Stub: preprocess audio to model input (Mel spectrogram)
  Future<List<List<List<double>>>> _preprocessAudio(Uint8List audioBytes) async {
    // TODO: implement proper WAV -> float32 -> mel spectrogram
    // For testing, return a dummy tensor
    return List.generate(1, (_) => List.generate(80, (_) => List.generate(3000, (_) => 0.0)));
  }

  /// Stub: decode output tensor to string
  String _decodeOutput(dynamic output) {
    // TODO: implement real decoding from Whisper output
    return "hello world (dummy output)";
  }

  /// Stub: simple confidence calculation
  double _calculateConfidence(dynamic output) {
    // TODO: implement real confidence from output logits
    return 0.9;
  }

  @override
  Widget build(BuildContext context) {
    return Text(
      _result,
      textAlign: TextAlign.center,
    );
  }
}
