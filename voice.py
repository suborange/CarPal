import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from pydub import AudioSegment

sound = AudioSegment.from_file("C:/Users/sidhu//Projects/LAHacks2019/Voice/resources/demo.mp3")
sound = sound.set_frame_rate(16000)
sound.export("C:/Users/sidhu/Projects/LAHacks2019/Voice/resources/wavdemo.wav", format="wav", bitrate="16k")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (r"C:\Users\sidhu\Projects\LAHacks2019\Voice\creds.json")

# Instantiates a client
client = speech.SpeechClient()

# The name of the audio file to transcribe
file_name = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'wavdemo.wav')

print("Just loaded file")

# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code='en-US')

# Detects speech in the audio file
response = client.recognize(config, audio)

print("Response generated")

print(response.results)

# for result in response.results:
#     print('Transcript: {}'.format(result.alternatives[0].transcript))