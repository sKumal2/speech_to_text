import os
from langchain_google_community import SpeechToTextLoader
from dotenv import load_dotenv

load_dotenv()

project_id = os.getenv("PROJECT_ID")
credentials_path = os.getenv("CREDENTIALS_PATH")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id


file_path = "./sample.wav"

loader = SpeechToTextLoader(
    project_id=project_id,
    file_path=file_path
)

docs = loader.load()
print("✅ Transcription successful:")
print(docs)