# import wave
# import contextlib
# from dotenv import load_dotenv
# from google_speech_loader import GoogleSpeechV2Loader
# from transcribe_long_audio import TranscribeLongAudio

# load_dotenv()

# def get_audio_duration(audio_path: str) -> float:
#     with contextlib.closing(wave.open(audio_path, 'r')) as f:
#         frames = f.getnframes()
#         rate = f.getframerate()
#         duration = frames / float(rate)
#     return duration

# audio_file = "./long_audio.wav"
# duration = get_audio_duration(audio_file)
# print(f"🎧 Audio duration: {duration:.2f} seconds")
# audio_uri = "gs://kumalbucket/long_audio.wav"
# if duration <= 60:
#     print("🟢 Using GoogleSpeechV2Loader for short audio.")
#     loader = GoogleSpeechV2Loader(audio_file=audio_file)
# else:
#     print("🟡 Using TranscribeLongAudio for long audio.")
#     loader = TranscribeLongAudio(audio_uri=audio_uri)
# docs = loader.load()
# print("✅ Transcript:", docs[0].page_content)
# print(docs)


import wave
import contextlib
import os
from dotenv import load_dotenv
from google.cloud import storage  # <-- Add this import
from google_speech_loader import GoogleSpeechV2Loader
from transcribe_long_audio import TranscribeLongAudio

# --- Configuration ---
GCS_BUCKET_NAME = "kumalbucket"  # Your GCS bucket
# ---------------------

load_dotenv()

def get_audio_duration(audio_path: str) -> float:
    """Gets the duration of a local WAV file."""
    with contextlib.closing(wave.open(audio_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration

def upload_to_gcs(local_file_path: str, bucket_name: str) -> str:
    """
    Uploads a local file to GCS and returns its 'gs://' URI.
    
    The destination file in GCS will have the same name as the local file.
    """
    # Get the file name from the local path
    # e.g., "./sample2.wav" -> "sample2.wav"
    gcs_blob_name = os.path.basename(local_file_path)

    print(f"🔼 Uploading {local_file_path} to gs://{bucket_name}/{gcs_blob_name}...")
    
    # Initialize the GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_name)

    # Upload the file
    blob.upload_from_filename(local_file_path)
    
    print("✅ Upload complete.")
    
    # Return the GCS URI
    return f"gs://{bucket_name}/{gcs_blob_name}"


# --- Main Script ---

# 1. Start with your local file
local_audio_file = "./sample2.wav"

# 2. Get its duration
duration = get_audio_duration(local_audio_file)
print(f"🎧 Audio duration: {duration:.2f} seconds")

# 3. Decide which loader to use
if duration <= 60:
    print("🟢 Using GoogleSpeechV2Loader for short audio.")
    loader = GoogleSpeechV2Loader(audio_file=local_audio_file)
else:
    print("🟡 Using TranscribeLongAudio for long audio.")
    
    # 4. Upload the local file to GCS to get the required URI
    try:
        audio_uri = upload_to_gcs(local_audio_file, GCS_BUCKET_NAME)
        loader = TranscribeLongAudio(audio_uri=audio_uri)
        
    except Exception as e:
        print(f"❌ Error uploading to GCS: {e}")
        print("   Please ensure 'pip install google-cloud-storage' is run")
        print("   And your account has 'Storage Object Creator' permissions on the bucket.")
        loader = None

# 5. Run the loader (if it was created)
if loader:
    docs = loader.load()
    print("✅ Transcript:", docs[0].page_content)
    print(docs)