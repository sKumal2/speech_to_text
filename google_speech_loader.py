from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from google.cloud import speech_v2
from google.cloud.speech_v2.types import cloud_speech
import os

class GoogleSpeechV2Loader(BaseLoader):
    def __init__(self, audio_file: str, language: str = "en-US"):
        self.audio_file = audio_file
        self.language = language
        self.project_id = os.getenv("PROJECT_ID")

    def load(self):
        client = speech_v2.SpeechClient()

        with open(self.audio_file, "rb") as f:
            audio_content = f.read()

        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=[self.language],
            model="long",
        )

        request = cloud_speech.RecognizeRequest(
            recognizer=f"projects/{self.project_id}/locations/global/recognizers/_",
            config=config,
            content=audio_content,
        )

        response = client.recognize(request=request)

        # Combine all transcripts into one text
        transcript = " ".join([r.alternatives[0].transcript for r in response.results])

        return [
            Document(
                page_content=transcript,
                metadata={"language": self.language, "file_path": self.audio_file}
            )
        ]
