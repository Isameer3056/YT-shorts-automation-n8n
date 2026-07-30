"""
Tiny HTTP bridge in front of Piper's Wyoming-protocol TTS server.

n8n's HTTP Request node can only speak plain HTTP, but Piper (via
rhasspy/wyoming-piper) speaks the Wyoming protocol over a raw TCP socket.
This wraps the *official* `wyoming` Python client library behind a simple
Flask endpoint, so the workflow tool never has to deal with the protocol
directly.

POST /synthesize
  { "text": "...", "out_path": "/data/voice.wav" }
  -> { "status": "ok", "path": "/data/voice.wav" }
"""
from flask import Flask, request, jsonify
from wyoming.client import AsyncClient
from wyoming.tts import Synthesize
from wyoming.audio import AudioChunk
import asyncio
import wave

app = Flask(__name__)

PIPER_HOST = "piper"
PIPER_PORT = 10200


async def synth(text: str, out_path: str) -> None:
    wav = None
    async with AsyncClient.from_uri(f"tcp://{PIPER_HOST}:{PIPER_PORT}") as client:
        await client.write_event(Synthesize(text=text).event())
        while True:
            event = await client.read_event()
            if event is None or event.type == "audio-stop":
                break
            if event.type == "audio-chunk":
                chunk = AudioChunk.from_event(event)
                if wav is None:
                    wav = wave.open(out_path, "wb")
                    wav.setnchannels(chunk.channels)
                    wav.setsampwidth(chunk.width)
                    wav.setframerate(chunk.rate)
                wav.writeframes(chunk.audio)
    if wav:
        wav.close()


@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.get_json(force=True)
    text = data.get("text", "")
    out_path = data.get("out_path", "/data/voice.wav")
    if not text.strip():
        return jsonify({"status": "error", "message": "text is empty"}), 400
    asyncio.run(synth(text, out_path))
    return jsonify({"status": "ok", "path": out_path})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
