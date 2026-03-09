import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() {
  runApp(const LanguageLearningApp());
}

class LanguageLearningApp extends StatelessWidget {
  const LanguageLearningApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Language Learning Game',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<dynamic> _languages = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadLanguages();
  }

  Future<void> _loadLanguages() async {
    try {
      final response = await http.get(Uri.parse('http://localhost:5000/api/languages'));
      if (response.statusCode == 200) {
        setState(() {
          _languages = json.decode(response.body);
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load languages';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Language Learning Game'),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _languages.length,
                  itemBuilder: (context, index) {
                    final language = _languages[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 16),
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(16),
                        title: Text(
                          language['name'],
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 8),
                            Text(
                              'Native: ${language['native_name']}',
                              style: const TextStyle(fontSize: 16),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Words: ${language['words_count']}',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                        trailing: ElevatedButton(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => QuizPage(
                                  languageId: language['id'],
                                  languageName: language['name'],
                                ),
                              ),
                            );
                          },
                          child: const Text('Learn'),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}

class QuizPage extends StatefulWidget {
  final String languageId;
  final String languageName;

  const QuizPage({
    super.key,
    required this.languageId,
    required this.languageName,
  });

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  List<dynamic> _words = [];
  int _currentIndex = 0;
  bool _isLoading = true;
  String? _error;
  final TextEditingController _answerController = TextEditingController();
  bool _showResult = false;
  bool? _isCorrect;
  String? _correctAnswer;

  @override
  void initState() {
    super.initState();
    _loadWords();
  }

  @override
  void dispose() {
    _answerController.dispose();
    super.dispose();
  }

  Future<void> _loadWords() async {
    try {
      final response = await http.get(
        Uri.parse('http://localhost:5000/api/words/${widget.languageId}'),
      );
      if (response.statusCode == 200) {
        setState(() {
          _words = json.decode(response.body);
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load words';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _checkAnswer() async {
    if (_answerController.text.isEmpty) return;

    try {
      final response = await http.post(
        Uri.parse('http://localhost:5000/api/check-answer'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'language': widget.languageId,
          'word_id': _words[_currentIndex]['id'],
          'answer': _answerController.text,
        }),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        setState(() {
          _showResult = true;
          _isCorrect = result['correct'];
          _correctAnswer = result['correct_answer'];
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error checking answer: $e';
      });
    }
  }

  void _nextWord() {
    setState(() {
      if (_currentIndex < _words.length - 1) {
        _currentIndex++;
      } else {
        _currentIndex = 0;
      }
      _answerController.clear();
      _showResult = false;
      _isCorrect = null;
      _correctAnswer = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Learning ${widget.languageName}'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : _words.isEmpty
                  ? const Center(child: Text('No words available'))
                  : Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Card(
                            child: Padding(
                              padding: const EdgeInsets.all(24),
                              child: Column(
                                children: [
                                  Text(
                                    'Word ${_currentIndex + 1} of ${_words.length}',
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    _words[_currentIndex]['word'],
                                    style: const TextStyle(
                                      fontSize: 32,
                                      fontWeight: FontWeight.bold,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    _words[_currentIndex]['phonetic'],
                                    style: TextStyle(
                                      fontSize: 16,
                                      color: Colors.grey[600],
                                      fontStyle: FontStyle.italic,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),
                          if (!_showResult) ...[
                            TextField(
                              controller: _answerController,
                              decoration: const InputDecoration(
                                labelText: 'Type the English translation',
                                border: OutlineInputBorder(),
                              ),
                              onSubmitted: (_) => _checkAnswer(),
                            ),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _checkAnswer,
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 16),
                              ),
                              child: const Text(
                                'Check Answer',
                                style: TextStyle(fontSize: 18),
                              ),
                            ),
                          ] else ...[
                            Card(
                              color: _isCorrect! ? Colors.green[100] : Colors.red[100],
                              child: Padding(
                                padding: const EdgeInsets.all(16),
                                child: Column(
                                  children: [
                                    Icon(
                                      _isCorrect! ? Icons.check_circle : Icons.cancel,
                                      color: _isCorrect! ? Colors.green : Colors.red,
                                      size: 48,
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      _isCorrect! ? 'Correct!' : 'Incorrect',
                                      style: TextStyle(
                                        fontSize: 24,
                                        fontWeight: FontWeight.bold,
                                        color: _isCorrect! ? Colors.green : Colors.red,
                                      ),
                                    ),
                                    if (!_isCorrect!) ...[
                                      const SizedBox(height: 8),
                                      Text(
                                        'Correct answer: $_correctAnswer',
                                        style: const TextStyle(fontSize: 16),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _nextWord,
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(vertical: 16),
                              ),
                              child: Text(
                                _currentIndex < _words.length - 1
                                    ? 'Next Word'
                                    : 'Start Over',
                                style: const TextStyle(fontSize: 18),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
    );
  }
}
