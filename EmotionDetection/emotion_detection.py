import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def emotion_detector(text_to_analyse):
    """
    Analyzes emotions in the given text using Watson NLP API.
    
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
    
    # Strip whitespace
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

    # Define the URL for the sentiment analysis API
    url = 'https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict'

    # Create the payload with the text to be analyzed
    myobj = { "raw_document": { "text": text_to_analyse } }

    # Set the headers with the required model ID for the API
    header = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}

    try:
        # Make a POST request to the API with the payload and headers
        response = requests.post(url, json=myobj, headers=header, timeout=10)
        
        logger.info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the response JSON
            formatted_response = json.loads(response.text)
            
            # Extract only the required emotions and their scores
            emotions = formatted_response['emotionPredictions'][0]['emotion']

            # Create the dictionary with the required emotions
            extracted_emotions = {
                'anger': emotions.get('anger', 0.0),
                'disgust': emotions.get('disgust', 0.0),
                'fear': emotions.get('fear', 0.0),
                'joy': emotions.get('joy', 0.0),
                'sadness': emotions.get('sadness', 0.0)
            }

            # Find the dominant emotion
            dominant_emotion = max(extracted_emotions, key=extracted_emotions.get)

            # Add dominant_emotion to the dictionary
            extracted_emotions['dominant_emotion'] = dominant_emotion

            logger.info(f"Successfully analyzed emotions. Dominant: {dominant_emotion}")
            return extracted_emotions

        else:
            # Handle error gracefully
            logger.error(f"API returned status code: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            return {
                'anger': None,
                'disgust': None,
                'fear': None,
                'joy': None,
                'sadness': None,
                'dominant_emotion': None
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None
        }
    
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error parsing API response: {str(e)}")
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

# def emotion_detector(text_to_analyse):
#     # Define the URL for the sentiment analysis API
#     url = 'https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict'

#     # Create the payload with the text to be analyzed
#     myobj = { "raw_document": { "text": text_to_analyse } }

#     # Set the headers with the required model ID for the API
#     header = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}

#     # Make a POST request to the API with the payload and headers
#     response = requests.post(url, json=myobj, headers=header)

#     # Parse the response JSON
#     formatted_response = json.loads(response.text)

#     if response.status_code == 200:
#         # Extract only the required emotions and their scores
#         emotions = formatted_response['emotionPredictions'][0]['emotion']

#         # Create the dictionary with the required emotions
#         extracted_emotions = {
#             'anger': emotions['anger'],
#             'disgust': emotions['disgust'],
#             'fear': emotions['fear'],
#             'joy': emotions['joy'],
#             'sadness': emotions['sadness']
#         }

#         # Find the dominant emotion
#         dominant_emotion = max(extracted_emotions, key=extracted_emotions.get)

#         # Add dominant_emotion to the dictionary
#         extracted_emotions['dominant_emotion'] = dominant_emotion

#         return extracted_emotions

#     elif response.status_code == 500:
#         # Handle error gracefully
#         return {
#             'anger': None,
#             'disgust': None,
#             'fear': None,
#             'joy': None,
#             'sadness': None,
#             'dominant_emotion': None
#         }
