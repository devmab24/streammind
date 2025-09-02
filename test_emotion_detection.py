import unittest
from EmotionDetection.emotion_detection import emotion_detector

class TestEmotionDetection(unittest.TestCase):
    # Required assignment test cases
    def test_joy(self):
        result = emotion_detector("I am glad this happened")
        self.assertEqual(result['dominant_emotion'], 'joy')

    def test_anger(self):
        result = emotion_detector("I am really mad about this")
        self.assertEqual(result['dominant_emotion'], 'anger')

    def test_disgust(self):
        result = emotion_detector("I feel disgusted just hearing about this")
        self.assertEqual(result['dominant_emotion'], 'disgust')

    def test_sadness(self):
        result = emotion_detector("I am so sad about this")
        self.assertEqual(result['dominant_emotion'], 'sadness')

    def test_fear(self):
        result = emotion_detector("I am really afraid that this will happen")
        self.assertEqual(result['dominant_emotion'], 'fear')

    # Extra edge cases
    def test_empty_string(self):
        result = emotion_detector("")
        self.assertIsInstance(result, dict)
        self.assertIn('dominant_emotion', result)
        self.assertNotEqual(result['dominant_emotion'], None)

    def test_neutral_sentence(self):
        result = emotion_detector("This is a chair")
        self.assertIsInstance(result, dict)
        self.assertIn('dominant_emotion', result)

    def test_random_text(self):
        result = emotion_detector("asdfgh qwerty zxcvb")
        self.assertIsInstance(result, dict)
        self.assertIn('dominant_emotion', result)


if __name__ == "__main__":
    unittest.main()
