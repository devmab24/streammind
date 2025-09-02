
import requests
import json

def emotion_detector(text_to_analyse):
    # Define the URL for the sentiment analysis API
    url = 'https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict'

    # Create the payload with the text to be analyzed
    myobj = { "raw_document": { "text": text_to_analyse } }

    # Set the headers with the required model ID for the API
    header = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}

    # Make a POST request to the API with the payload and headers
    response = requests.post(url, json=myobj, headers=header)

    # Parse the response JSON
    formatted_response = json.loads(response.text)

    if response.status_code == 200:
        # Extract only the required emotions and their scores
        emotions = formatted_response['emotionPredictions'][0]['emotion']

        # Create the dictionary with the required emotions
        extracted_emotions = {
            'anger': emotions['anger'],
            'disgust': emotions['disgust'],
            'fear': emotions['fear'],
            'joy': emotions['joy'],
            'sadness': emotions['sadness']
        }

        # Find the dominant emotion
        dominant_emotion = max(extracted_emotions, key=extracted_emotions.get)

        # Add dominant_emotion to the dictionary
        extracted_emotions['dominant_emotion'] = dominant_emotion

        return extracted_emotions

    elif response.status_code == 500:
        # Handle error gracefully
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None
        }
