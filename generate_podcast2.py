
import re
import asyncio
import sys

try:
    import edge_tts
except ImportError:
    print("edge-tts not installed. Please run: python -m pip install edge-tts")
    sys.exit(1)

HOST_VOICE = "en-US-GuyNeural"
EXPERT_VOICE = "en-US-JennyNeural"

# Naturalness tuning per voice
VOICE_SETTINGS = {
    HOST_VOICE: {"rate": "-4%", "pitch": "-1Hz"},  # slightly slower & deeper
    EXPERT_VOICE: {"rate": "-3%", "pitch": "+2Hz"},  # conversational & brighter
}

# Read script from text file
with open(r'C:\Users\User\OneDrive\Desktop\Podcast\podcast_script.txt', 'r', encoding='utf-8') as f:
    script = f.read()

segments = []
current_voice = None
current_text = ""

for line in script.strip().split('\n'):
    line = line.strip()
    if not line or line.startswith("SEGMENT"):
        continue

    match = re.match(r"^(HOST|EXPERT)(?:\s*\(.*?\))?:\s*(.*)", line)
    if match:
        if current_text:
            segments.append((current_voice, current_text.strip()))
            current_text = ""

        role, text = match.groups()
        current_voice = HOST_VOICE if role == "HOST" else EXPERT_VOICE
        current_text = text + " "
    else:
        current_text += line + " "

if current_text:
    segments.append((current_voice, current_text.strip()))

async def generate_podcast(segments, output_file="podcast_output.mp3"):
    """Generate a podcast TTS file from segments."""
    with open(output_file, "wb") as f:
        for voice, text in segments:
            if not voice:  # Skip if voice is None
                print(f"Skipping segment with no voice: {text}")
                continue
            print(f"[{voice}]: {text}")
            settings = VOICE_SETTINGS.get(voice, {"rate": "+0%", "pitch": "+0Hz"})
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=settings["rate"],
                pitch=settings["pitch"],
            )
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])

if __name__ == "__main__":
    print("Segments to process:")
    print(segments)  # Debugging: Print segments to verify correctness
    asyncio.run(generate_podcast(segments))
    print("\nPodcast saved as 'podcast_output.mp3'")

