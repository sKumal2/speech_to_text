import os
from typing import List
from google.cloud import speech_v2
from google.cloud.speech_v2.types import cloud_speech
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document

class TranscribeLongAudio(BaseLoader):
    """
    A LangChain Document Loader for transcribing long audio files (>60s)
    using the Google Cloud Speech-to-Text V2 API's batch recognition
    with an 'on-the-fly' recognizer.
    """

    def __init__(self, audio_uri: str):
        """
        Initializes the loader.
        
        Args:
            audio_uri (str): The Google Cloud Storage URI of the input audio file.
                             Must be in the format 'gs://[BUCKET]/[FILE]'.
        """
        if not audio_uri or not audio_uri.startswith("gs://"):
            raise ValueError("audio_uri must be a valid GCS URI, e.g., 'gs://bucket/file.wav'")
        self.audio_uri = audio_uri

    def load(self) -> List[Document]:
        """
        Transcribes the long audio file from the GCS URI and returns
        the full transcript as a single LangChain Document.
        """
        
        PROJECT_ID = os.getenv("PROJECT_ID")
        if not PROJECT_ID:
            # Fallback to the project ID from your original error message
            PROJECT_ID = "108172735379"
            print(f"Warning: GOOGLE_CLOUD_PROJECT env var not set. Falling back to {PROJECT_ID}.")

        client = speech_v2.SpeechClient()

        # Define the on-the-fly configuration
        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            model="long", 
            language_codes=["en-US"], 
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True
            )
        )

        file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=self.audio_uri)

        # Define the request using the "on-the-fly" wildcard recognizer
        request = cloud_speech.BatchRecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
            config=config,
            files=[file_metadata],
            recognition_output_config=cloud_speech.RecognitionOutputConfig(
                inline_response_config=cloud_speech.InlineOutputConfig(),
            ),
        )

        # Transcribes the audio into text
        print("⏳ Starting batch transcription operation...")
        operation = client.batch_recognize(request=request)

        # Timeout for the operation (in seconds)
        # Your audio is 615s, so 600s (10 min) should be a safe timeout.
        print(f"Waiting for operation to complete (timeout set to 600s)...")
        try:
            response = operation.result(timeout=600)
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            if "DeadlineExceeded" in str(e):
                 print("   Suggestion: The audio file is very long. You may need to increase the 'timeout' value in the load() method.")
            return [] # Return empty list on failure

        # Process the results
        try:
            transcript_results = response.results[self.audio_uri].transcript.results
        except KeyError:
            print(f"❌ No transcription results found for URI: {self.audio_uri}")
            print(f"Full response object: {response}")
            return [] 
        except AttributeError:
            print(f"❌ Error: Could not parse results. 'transcript' or 'results' not found.")
            print(f"Full response object: {response}")
            return []

        # Combine all transcript segments into one string
        full_transcript = " ".join(
            [result.alternatives[0].transcript for result in transcript_results if result.alternatives]
        )

        if not full_transcript:
            print("⚠️ Transcription successful, but no text was recognized.")

        # Create the LangChain Document
        metadata = {"source": self.audio_uri}
        doc = Document(page_content=full_transcript, metadata=metadata)

        return [doc]