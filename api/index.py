# from flask import Flask
# import speech_recognition as sr
# import pyttsx3

# app = Flask(__name__)

# recognizer = sr.Recognizer()

# @app.route('/api/nexi-loop', methods=['GET'])
# def nexi_loop():
#     print("🎙️ Nexi started listening... Press Ctrl+C to stop manually.")

#     try:
#         while True:
#             with sr.Microphone() as source:
#                 recognizer.adjust_for_ambient_noise(source)
#                 print("👂 Listening...")

#                 audio = recognizer.listen(source, timeout=5)
#                 print("📝 Transcribing...")

#                 try:
#                     text = recognizer.recognize_google(audio, language='en-US')
#                     print(f"✅ You said: {text}")

#                     # Re-initialize pyttsx3 each time to avoid engine lock
#                     engine = pyttsx3.init()
#                     engine.say(text)
#                     engine.runAndWait()

#                 except sr.UnknownValueError:
#                     print("❌ Could not understand audio.")
#                 except sr.RequestError as e:
#                     print(f"❗ API error: {e}")
#                 except Exception as e:
#                     print(f"🔥 Unexpected error: {e}")

#     except KeyboardInterrupt:
#         print("🛑 Nexi stopped manually.")

#     return "Nexi stopped.", 200

# if __name__ == '__main__':
#     app.run(debug=True)

import os
import io
from flask import Flask
import speech_recognition as sr
from google.cloud import texttospeech
from pydub import AudioSegment
import simpleaudio as sa

# Set relative path to service-account.json
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "service-account.json")

app = Flask(__name__)
recognizer = sr.Recognizer()

# Initialize Google TTS client
tts_client = texttospeech.TextToSpeechClient()

def speak_with_google(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-IN",
        name="en-IN-Standard-F",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Use in-memory audio (no file save)
    audio_stream = io.BytesIO(response.audio_content)
    audio = AudioSegment.from_file(audio_stream, format="mp3")
    playback = sa.play_buffer(audio.raw_data,
                              num_channels=audio.channels,
                              bytes_per_sample=audio.sample_width,
                              sample_rate=audio.frame_rate)
    playback.wait_done()

@app.route('/api/nexi-loop', methods=['GET'])
def nexi_loop():
    print("🎙️ Nexi started listening... Press Ctrl+C to stop manually.")

    try:
        while True:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                print("👂 Listening...")

                audio = recognizer.listen(source, timeout=5)
                print("📝 Transcribing...")

                try:
                    text = recognizer.recognize_google(audio, language='en-US')
                    print(f"✅ You said: {text}")

                    # Speak with Google TTS in real-time
                    speak_with_google(text)

                except sr.UnknownValueError:
                    print("❌ Could not understand audio.")
                except sr.RequestError as e:
                    print(f"❗ API error: {e}")
                except Exception as e:
                    print(f"🔥 Unexpected error: {e}")

    except KeyboardInterrupt:
        print("🛑 Nexi stopped manually.")

    return "Nexi loop stopped.", 200

if __name__ == '__main__':
    app.run(debug=False)
