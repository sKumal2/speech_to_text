from langchain_google_community import SpeechToTextLoader

project_id = "<PROJECT_ID>"
file_path = "gs://cloud-samples-data/speech/audio.flac"
# or a local file path: file_path = "./audio.wav"

loader = SpeechToTextLoader(project_id=project_id, file_path=file_path)

docs = loader.load()