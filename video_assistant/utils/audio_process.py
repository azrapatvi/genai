import yt_dlp
import os
from pydub import AudioSegment

DOWNLOAD_DIR=r'E:\chatbot\video_assistant\downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok=True)

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a",'.wav')

    return filename

# this converts teh audio and viddeo file into WAV audio file ex lecture.wav ->Audio file in WAV format.(why wav? because it provides high quality audio file which is useally large in size)
def convert_to_wav(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path) # this reads the audio file or video fril and loads its audio into python
    audio = audio.set_channels(1).set_frame_rate(16000) # to make sound or audio mono and of 16khz
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(audio_path:str,chunk_mins:float=4):  # CHANGED: int -> float so 25 sec (0.4166 min) works
    audio=AudioSegment.from_file(audio_path)
    chunk_ms=int(chunk_mins*60*1000) #becuase this funciton works with the miliseconds only so making it in ms lets considerif i give 10 min in chunk_mins then 10*60*1000  # CHANGED: wrapped in int()
    
    chunks=[]
    for i,start in enumerate(range(0,len(audio),chunk_ms)):
        chunk=audio[start:start+chunk_ms]
        chunk_path = f"{audio_path}_chunk_{i}.mp3"
        chunk.export(chunk_path, format="mp3")  # CHANGED: added format="wav"

        chunks.append(chunk_path)
    return chunks

# this all was for testing
# data=download_youtube_audio("https://www.youtube.com/watch?v=qNbQdQVt0Q4")
# converted=convert_to_wav(data)
# print(chunk_audio(converted,4))

def process_input(source:str, language:str="en"):  # CHANGED: added language param
    if source.startswith('http://')or source.startswith('https://'):
        print("youtube url detected!")
        wav_path=download_youtube_audio(source)
    else:
        print("local file detected!")
        wav_path=convert_to_wav(source)

    print("DONE with loading the file")
    chunk_mins = 25/60 if language == "hi" else 4  # CHANGED: Sarvam allows max 30 sec, so 25 sec chunks for Hindi
    chunks=chunk_audio(wav_path, chunk_mins=chunk_mins)#by default 4 mins
    print(f'we got {len(chunks)} chunks for the give source {source}')

    return chunks