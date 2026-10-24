from utils.audio_process import process_input
from core.transcriber import transcribe_all
from core.extractor import extract_action_items, key_decisions, extract_questions  # file ka naam jo bhi ho wo likho

path = "https://www.youtube.com/watch?v=-VKwVfWNaUU"

chunks = process_input(path, language='hi')
transcribed_full_text = transcribe_all(chunks, language='hi')

# transcript save kar lo, taaki baar-baar transcribe na karna pade
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(transcribed_full_text)

print("\n=== ACTION ITEMS ===")
print(extract_action_items(transcribed_full_text))

print("\n=== KEY DECISIONS ===")
print(key_decisions(transcribed_full_text))

print("\n=== OPEN QUESTIONS ===")
print(extract_questions(transcribed_full_text))