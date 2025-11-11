from dotenv import load_dotenv
from google_speech_loader import GoogleSpeechV2Loader

load_dotenv()

loader = GoogleSpeechV2Loader(audio_file="./sample.wav")
docs = loader.load()

print("✅ Transcript:", docs[0].page_content)
print(docs)