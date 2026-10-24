
import whisper
import os
from sarvamai import SarvamAI
from dotenv import load_dotenv

load_dotenv()

_model = None
_sarvam_client = None

#now the thing is whisper works better for wnglish rtanscription but what if the data we have is in the hindi or th fuile contains hindii audio 
#so for hindi transcription we will be suing SARVAM

#this will load the model if the model isnot loaded before means fro the first time
def load_model():
    global _model

    if _model is None:
        _model = whisper.load_model("small")
        print("model loaded succesfully")

    return _model


def load_sarvam():
    global _sarvam_client

    if _sarvam_client is None:
        _sarvam_client = SarvamAI(
            api_subscription_key=os.environ["SARVAM_API_KEY"]
        )

    return _sarvam_client


# this will specifically transcribe a chunk not all chunks thats why we create transcribe_all() which will transcribe all the chunkss...the transcribe_All will get use the transcribe_chunk to transcribe each chunks
import time  # top pe import add karo

def transcribe_chunk(chunk, language="en", translate: bool = False):

    if language == "hi":
        client = load_sarvam()

        for attempt in range(3):
            try:
                with open(chunk, "rb") as audio:
                    result = client.speech_to_text.transcribe(
                        file=audio,
                        model="saaras:v4",
                        language_code="hi-IN",
                        mode="translate" if translate else "transcribe"
                    )
                return result.transcript
            except Exception as e:
                print(f"sarvam failed (try {attempt + 1}/3): {e}")
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))  # 2s, then 4s wait

    model = load_model()

    task_to_do = "translate" if translate else "transcribe"

    result = model.transcribe(chunk, task=task_to_do)

    return result["text"]

def transcribe_all(chunks: list, language="en", translate: bool = False):

    transcribed_full = ""

    for i, chunk in enumerate(chunks):
        transcribed = transcribe_chunk(
            chunk,
            language=language,
            translate=translate
        )
        transcribed_full += transcribed + " "
        time.sleep(0.5)

    return transcribed_full.strip()
