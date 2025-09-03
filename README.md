# 🧠 Emotion Detection Web Application

A real-time emotion analysis web application built with Flask that analyzes text input and identifies five core emotions: joy, anger, sadness, fear, and disgust. This project was developed as part of an AI and Data Science course on Coursera.

## 🌟 Features

- **Real-Time Emotion Analysis**: Instantly analyzes user-inputted text for emotional content
- **Five Emotion Categories**: Detects joy, anger, sadness, fear, and disgust with confidence scores
- **Responsive Web Interface**: Modern Bootstrap-powered UI that works across all devices
- **Multiple NLP Engines**: Supports both Watson NLP API and local TextBlob/VADER analysis
- **Comprehensive Error Handling**: Robust error management with user-friendly feedback
- **Production Ready**: Configured for deployment with Gunicorn WSGI server

## 🚀 Live Demo

**[Try the Live App Here](https://emotion-detector-40dbd84f487d.herokuapp.com/)**

## 📸 Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)

### Emotion Analysis Results
![Results Display](screenshots/emotion-results.png)

## 🛠️ Tech Stack

### Backend
- **Python 3.x** - Core programming language
- **Flask 3.1.2** - Web framework
- **Watson NLP API** - Primary emotion analysis service
- **TextBlob** - Local sentiment analysis fallback
- **VADER Sentiment** - Enhanced local emotion detection
- **Requests** - HTTP client for API calls

### Frontend
- **HTML5 & CSS3** - Structure and styling
- **Bootstrap 4.3.1** - Responsive UI framework
- **JavaScript (Vanilla)** - Client-side functionality
- **AJAX** - Asynchronous server communication

### Development & Deployment
- **Gunicorn** - Production WSGI server
- **Virtual Environment** - Dependency isolation
- **Git** - Version control
- **pytest** - Testing framework (optional)

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Internet connection (for Watson API, optional for local mode)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/emotion-detection-app.git
cd emotion-detection-app
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv emotion_env

# Activate virtual environment
# On Windows:
emotion_env\Scripts\activate
# On macOS/Linux:
source emotion_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

# Download TextBlob corpora (for local emotion detection)
python -m textblob.download_corpora
```

### 4. Run the Application
```bash
python server.py
```

### 5. Access the App
Open your browser and navigate to:
```
http://localhost:5000
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
WATSON_API_KEY=your_watson_api_key_here  # Optional
```

### Production Deployment
For production deployment, use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## 📝 API Documentation

### Emotion Detection Endpoint
```
GET /emotionDetector?textToAnalyze=<your_text>
```

**Parameters:**
- `textToAnalyze` (string, required): Text to analyze for emotions

**Response:**
```json
{
  "status": "success",
  "emotions": {
    "anger": 0.1234,
    "disgust": 0.0567,
    "fear": 0.0892,
    "joy": 0.7234,
    "sadness": 0.0073,
    "dominant_emotion": "joy"
  }
}
```

**Error Response:**
```json
{
  "error": "Invalid input! Please provide some text to analyze."
}
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest

# Run specific test file
python test_emotion_detection.py

# Run with coverage
python -m pytest --cov=EmotionDetection
```

### Test Cases Included
- Joy emotion detection
- Anger emotion detection
- Sadness emotion detection
- Fear emotion detection
- Disgust emotion detection
- Empty input handling
- Invalid input handling

## 📁 Project Structure

```
emotion-detection-app/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── server.py                    # Flask application entry point
├── EmotionDetection/
│   ├── __init__.py
│   └── emotion_detection.py     # Core emotion analysis logic
├── templates/
│   └── index.html              # Main web interface template
├── static/
│   └── mywebscript.js          # Frontend JavaScript
├── test_emotion_detection.py   # Unit tests
└── screenshots/                # Application screenshots
    ├── main-interface.png
    └── emotion-results.png
```

## 🔍 How It Works

1. **User Input**: User enters text through the web interface
2. **Text Processing**: JavaScript sends text to Flask backend via AJAX
3. **Emotion Analysis**: 
   - Primary: Watson NLP API analyzes the text
   - Fallback: Local TextBlob/VADER analysis if Watson fails
4. **Results Processing**: Backend formats emotion scores and identifies dominant emotion
5. **Display**: Frontend receives JSON response and displays results with visual feedback

## 🚨 Known Issues & Limitations

- Watson NLP API may have connectivity issues or timeouts
- Local emotion detection is less accurate than trained ML models
- Currently supports only English text input
- No user authentication or rate limiting implemented
- Emotion detection is context-dependent and may not capture sarcasm/irony

## 🛣️ Future Enhancements

- [ ] Add support for multiple languages
- [ ] Implement user accounts and history tracking
- [ ] Add more emotion categories
- [ ] Include confidence intervals and uncertainty measures
- [ ] Add batch text processing capability
- [ ] Implement real-time emotion tracking over time
- [ ] Add data visualization charts for emotion trends
- [ ] Include emotion comparison between different texts

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Add tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@devmab24](https://github.com/devmab24)
- LinkedIn: [Your LinkedIn Profile](https://www.linkedin.com/in/devmab/)
- Email: talk2muhammadbello@gmail.com

## 🙏 Acknowledgments

- **Coursera AI and Data Science Course** - For the initial project assignment
- **IBM Watson NLP** - For providing the emotion analysis API
- **TextBlob & VADER** - For local sentiment analysis capabilities
- **Flask Community** - For the excellent web framework
- **Bootstrap Team** - For the responsive UI components

## 📊 Project Stats

- **Development Time**: 3 weeks
- **Lines of Code**: ~500
- **Technologies Used**: 10+
- **Test Coverage**: 85%

## 🔗 Related Projects

- [Sentiment Analysis with BERT](ongoing)
- [Text Classification API](ongoing)
- [NLP Toolkit Collection](ongoing)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/devmab24/emotion-detection-app/issues) page
2. Create a new issue with detailed description
3. Contact me via email or LinkedIn

---

⭐ **If you found this project helpful, please give it a star!** ⭐
