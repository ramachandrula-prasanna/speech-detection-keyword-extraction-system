import 'package:flutter/material.dart';
import 'dart:async';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: LandingPage(),
    );
  }
}
class LandingPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: Center(
        child: Container(
          width: 750,
          padding: EdgeInsets.all(30),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(25),
            boxShadow: [
              BoxShadow(
                color: Colors.black12,
                blurRadius: 10,
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.record_voice_over,
                size: 70,
                color: Colors.blue,
              ),

              SizedBox(height: 20),

              Text(
                "Speech Detection & Keyword Extraction System",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),

              SizedBox(height: 15),

              Text(
                "Detect speech and extract important keywords from live video or uploaded videos.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 17,
                  color: Colors.grey[700],
                ),
              ),

              SizedBox(height: 35),

              SizedBox(
                width: 250,
                child: ElevatedButton.icon(
                  icon: Icon(Icons.videocam),
                  label: Text("Live Detection"),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => HomeScreen(),
                      ),
                    );
                  },
                ),
              ),

              SizedBox(height: 15),

              SizedBox(
                width: 250,
                child: ElevatedButton.icon(
                  icon: Icon(Icons.upload_file),
                  label: Text("Upload Video"),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => UploadScreen(),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ================= HOME =================

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String keywords = "";

  bool isListening = false;
  bool isSpeechDetected = false;

  int refresh = 0;

  Image? currentFrame;

  @override
  void initState() {
    super.initState();

    // 🔥 SMOOTH CAMERA (FIXED)
    Timer.periodic(Duration(milliseconds: 80), (timer) async {
      if (!mounted) return;

      final image = Image.network(
        "http://127.0.0.1:5000/frame?$refresh",
        fit: BoxFit.cover,
      );

      await precacheImage(image.image, context);

      setState(() {
        currentFrame = image;
        refresh++;
      });
    });
  }

  // 🔥 BACKEND CALL
  Future<void> getLiveKeywords() async {
    setState(() {
      isListening = true;
      keywords = "";
    });

    try {
      var response = await http.get(
        Uri.parse("http://127.0.0.1:5000/live"),
      );

      var data = jsonDecode(response.body);

      String result = (data["keywords"] as List).join(", ");

      setState(() {
        keywords = result;
        isSpeechDetected = result != "No speech detected";
        isListening = false;
      });

    } catch (e) {
      setState(() {
        isListening = false;
      });
    }
  }

  void stopListening() {
    setState(() {
      isListening = false;
      isSpeechDetected = false;
    });
  }

  void goToUpload() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => UploadScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: Center(
        child: Container(
          width: 900,
          padding: EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(25),
            boxShadow: [
              BoxShadow(color: Colors.black12, blurRadius: 10)
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [

              // 🔥 TITLE
              Text(
                "Speech Detection & Keyword Extraction System",
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),

              SizedBox(height: 20),

              // 🔥 CAMERA (UPDATED HERE)
              Container(
                height: 400,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.black,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(15),
                  child: currentFrame ??
                      Center(child: CircularProgressIndicator()),
                ),
              ),

              SizedBox(height: 15),

              // 🔥 STATUS INDICATOR
              Container(
                padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: BoxDecoration(
                  color: isListening
                      ? Colors.orange
                      : isSpeechDetected
                          ? Colors.green
                          : Colors.red,
                  borderRadius: BorderRadius.circular(25),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      isListening
                          ? Icons.mic
                          : isSpeechDetected
                              ? Icons.volume_up
                              : Icons.volume_off,
                      color: Colors.white,
                    ),
                    SizedBox(width: 8),
                    Text(
                      isListening
                          ? "Listening..."
                          : isSpeechDetected
                              ? "Speech Detected"
                              : "No Speech",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 20),

              // 🔥 BUTTONS
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton.icon(
                    onPressed: isListening ? null : getLiveKeywords,
                    icon: Icon(Icons.play_arrow),
                    label: Text("Start Detection"),
                  ),
                  SizedBox(width: 15),
                  ElevatedButton.icon(
                    onPressed: isListening ? stopListening : null,
                    icon: Icon(Icons.stop),
                    label: Text("Stop"),
                  ),
                ],
              ),

              SizedBox(height: 20),

              // 🔥 KEYWORDS BOX
              Container(
                width: double.infinity,
                padding: EdgeInsets.all(25),
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Text(
                  keywords.isEmpty ? "Keywords: ..." : keywords,
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),

              SizedBox(height: 20),

              // 🔥 UPLOAD BUTTON
              ElevatedButton.icon(
  onPressed: () {
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => LandingPage(),
      ),
      (route) => false,
    );
  },
  icon: Icon(Icons.home),
  label: Text("Home"),
),
            
            ],
          ),
        ),
      ),
    );
  }
}
   


// ================= UPLOAD =================

class UploadScreen extends StatefulWidget {
  @override
  _UploadScreenState createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String status = "No file selected";
  String keywords = "";
  String? selectedFileName;

  Future<void> pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.video,
    );

    if (result == null) return;

    String path = result.files.single.path!;
    selectedFileName = result.files.single.name;

    setState(() {
      status = "Uploading...";
      keywords = "";
    });

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse("http://127.0.0.1:5000/upload"),
      );

      request.files.add(await http.MultipartFile.fromPath('file', path));

      var response = await request.send();
      var responseBody = await response.stream.bytesToString();

      var data = jsonDecode(responseBody);

      setState(() {
        status = "Processing...";
      });

      await Future.delayed(Duration(seconds: 1));

      setState(() {
        keywords = (data["keywords"] as List).join(", ");
        status = "Done";
      });

    } catch (e) {
      setState(() {
        status = "Upload failed";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: Center(
        child: Container(
          width: 400,
          padding: EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(25),
            boxShadow: [
              BoxShadow(color: Colors.black12, blurRadius: 10)
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [

              Text(
                "Upload Video",
                style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold),
              ),

              SizedBox(height: 20),

              ElevatedButton(
                onPressed: pickFile,
                child: Text("Select Video"),
              ),

              SizedBox(height: 15),

              if (status == "Uploading..." || status == "Processing...")
                CircularProgressIndicator(),

              SizedBox(height: 10),

              Text(status),

              SizedBox(height: 20),

              if (keywords.isNotEmpty)
                Text(keywords),

              SizedBox(height: 20),

              ElevatedButton.icon(
  onPressed: () {
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => LandingPage(),
      ),
      (route) => false,
    );
  },
  icon: Icon(Icons.home),
  label: Text("Home"),
),
            ],
          ),
        ),
      ),
    );
  }
}