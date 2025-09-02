# Alternative implementation using TextBlob and VADER
# First install: pip install textblob vaderSentiment
# Then run: python -m textblob.download_corpora

import logging
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def emotion_detector(text_to_analyse):
    """
    Analyzes emotions using TextBlob and VADER sentiment analysis.
    Maps sentiment to emotion categories.
    
    Args:
        text_to_analyse (str): Text to analyze for emotions
        
    Returns:
        dict: Dictionary containing emotion scores and dominant emotion
    """
    
    # Input validation
    if not text_to_analyse or not isinstance(text_to_analyse, str):
        logger.warning("Invalid input provided to emotion_detector")
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None
        }
    
    text_to_analyse = text_to_analyse.strip()
    
    if not text_to_analyse:
        logger.warning("Empty text provided to emotion_detector")
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None
        }

    try:
        # Initialize analyzers
        analyzer = SentimentIntensityAnalyzer()
        blob = TextBlob(text_to_analyse)
        
        # Get VADER scores
        vader_scores = analyzer.polarity_scores(text_to_analyse)
        
        # Get TextBlob polarity and subjectivity
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Emotion mapping logic
        emotion_scores = {
            'anger': 0.0,
            'disgust': 0.0,
            'fear': 0.0,
            'joy': 0.0,
            'sadness': 0.0
        }
        
        # Map VADER compound score to emotions
        compound = vader_scores['compound']
        pos = vader_scores['pos']
        neg = vader_scores['neg']
        neu = vader_scores['neu']
        
        # Joy mapping
        if compound > 0.1:
            emotion_scores['joy'] = min(pos * 1.2, 1.0)
        
        # Sadness mapping
        if compound < -0.1 and polarity < 0:
            emotion_scores['sadness'] = min(neg * 1.1, 1.0)
        
        # Anger mapping (negative sentiment + high intensity)
        if compound < -0.3 and subjectivity > 0.5:
            emotion_scores['anger'] = min(neg * 0.9, 1.0)
        
        # Fear mapping (negative sentiment + uncertainty words)
        fear_words = ['afraid', 'scared', 'worry', 'anxious', 'nervous', 'panic', 'fear']
        text_lower = text_to_analyse.lower()
        fear_count = sum(1 for word in fear_words if word in text_lower)
        if fear_count > 0 or (compound < -0.2 and 'not' in text_lower):
            emotion_scores['fear'] = min((neg + fear_count * 0.2), 1.0)
        
        # Disgust mapping (very negative sentiment)
        disgust_words = ['disgusting', 'gross', 'awful', 'terrible', 'horrible', 'hate']
        disgust_count = sum(1 for word in disgust_words if word in text_lower)
        if compound < -0.4 or disgust_count > 0:
            emotion_scores['disgust'] = min((neg * 0.8 + disgust_count * 0.3), 1.0)
        
        # Ensure at least some emotion if neutral
        if all(score == 0.0 for score in emotion_scores.values()):
            if compound >= 0:
                emotion_scores['joy'] = 0.3
            else:
                emotion_scores['sadness'] = 0.3
        
        # Normalize to ensure scores don't exceed 1.0
        for emotion in emotion_scores:
            emotion_scores[emotion] = round(min(emotion_scores[emotion], 1.0), 4)
        
        # Find dominant emotion
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Add dominant_emotion to result
        result = emotion_scores.copy()
        result['dominant_emotion'] = dominant_emotion
        
        logger.info(f"VADER compound: {compound}, TextBlob polarity: {polarity}")
        logger.info(f"Dominant emotion: {dominant_emotion}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in emotion detection: {str(e)}")
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None
        }

# import requests
# import json
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def emotion_detector(text_to_analyse):
#     """
#     Analyzes emotions in the given text using Watson NLP API.
    
#     Args:
#         text_to_analyse (str): Text to analyze for emotions
        
#     Returns:
#         dict: Dictionary containing emotion scores and dominant emotion
#     """
    
#     # Input validation
#     if not text_to_analyse or not isinstance(text_to_analyse, str):
#         logger.warning("Invalid input provided to emotion_detector")
#         return {
#             'anger': None,
#             'disgust': None,
#             'fear': None,
#             'joy': None,
#             'sadness': None,
#             'dominant_emotion': None
#         }
    
#     # Strip whitespace
#     text_to_analyse = text_to_analyse.strip()
    
#     if not text_to_analyse:
#         logger.warning("Empty text provided to emotion_detector")
#         return {
#             'anger': None,
#             'disgust': None,
#             'fear': None,
#             'joy': None,
#             'sadness': None,
#             'dominant_emotion': None
#         }

#     # Define the URL for the sentiment analysis API
#     url = 'https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict'

#     # Create the payload with the text to be analyzed
#     myobj = { "raw_document": { "text": text_to_analyse } }

#     # Set the headers with the required model ID for the API
#     header = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}

#     try:
#         # Make a POST request to the API with the payload and headers
#         response = requests.post(url, json=myobj, headers=header, timeout=10)
        
#         logger.info(f"API Response Status: {response.status_code}")
        
#         if response.status_code == 200:
#             # Parse the response JSON
#             formatted_response = json.loads(response.text)
            
#             # Extract only the required emotions and their scores
#             emotions = formatted_response['emotionPredictions'][0]['emotion']

#             # Create the dictionary with the required emotions
#             extracted_emotions = {
#                 'anger': emotions.get('anger', 0.0),
#                 'disgust': emotions.get('disgust', 0.0),
#                 'fear': emotions.get('fear', 0.0),
#                 'joy': emotions.get('joy', 0.0),
#                 'sadness': emotions.get('sadness', 0.0)
#             }

#             # Find the dominant emotion
#             dominant_emotion = max(extracted_emotions, key=extracted_emotions.get)

#             # Add dominant_emotion to the dictionary
#             extracted_emotions['dominant_emotion'] = dominant_emotion

#             logger.info(f"Successfully analyzed emotions. Dominant: {dominant_emotion}")
#             return extracted_emotions

#         else:
#             # Handle error gracefully
#             logger.error(f"API returned status code: {response.status_code}")
#             logger.error(f"Response text: {response.text}")
#             return {
#                 'anger': None,
#                 'disgust': None,
#                 'fear': None,
#                 'joy': None,
#                 'sadness': None,
#                 'dominant_emotion': None
#             }
            
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Request failed: {str(e)}")
#         return {
#             'anger': None,
#             'disgust': None,
#             'fear': None,
#             'joy': None,
#             'sadness': None,
#             'dominant_emotion': None
#         }
    
#     except (json.JSONDecodeError, KeyError) as e:
#         logger.error(f"Error parsing API response: {str(e)}")
#         return {
#             'anger': None,
#             'disgust': None,
#             'fear': None,
#             'joy': None,
#             'sadness': None,
#             'dominant_emotion': None
#         }

# # import requests
# # import json

# # def emotion_detector(text_to_analyse):
# #     # Define the URL for the sentiment analysis API
# #     url = 'https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict'

# #     # Create the payload with the text to be analyzed
# #     myobj = { "raw_document": { "text": text_to_analyse } }

# #     # Set the headers with the required model ID for the API
# #     header = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}

# #     # Make a POST request to the API with the payload and headers
# #     response = requests.post(url, json=myobj, headers=header)

# #     # Parse the response JSON
# #     formatted_response = json.loads(response.text)

# #     if response.status_code == 200:
# #         # Extract only the required emotions and their scores
# #         emotions = formatted_response['emotionPredictions'][0]['emotion']

# #         # Create the dictionary with the required emotions
# #         extracted_emotions = {
# #             'anger': emotions['anger'],
# #             'disgust': emotions['disgust'],
# #             'fear': emotions['fear'],
# #             'joy': emotions['joy'],
# #             'sadness': emotions['sadness']
# #         }

# #         # Find the dominant emotion
# #         dominant_emotion = max(extracted_emotions, key=extracted_emotions.get)

# #         # Add dominant_emotion to the dictionary
# #         extracted_emotions['dominant_emotion'] = dominant_emotion

# #         return extracted_emotions

# #     elif response.status_code == 500:
# #         # Handle error gracefully
# #         return {
# #             'anger': None,
# #             'disgust': None,
# #             'fear': None,
# #             'joy': None,
# #             'sadness': None,
# #             'dominant_emotion': None
# #         }
