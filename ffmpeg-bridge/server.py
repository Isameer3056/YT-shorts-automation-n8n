"""
Tiny HTTP bridge that runs shell commands (ffmpeg, ffprobe) on request.

n8n's Execute Command node is disabled by default since n8n 2.0 for
security reasons, and re-enabling it via environment variables has known
issues. This sidesteps that entirely: a one-endpoint HTTP server, reachable
only from other containers on the same internal Docker network (never
exposed to the public internet), that runs a given command and returns
its result.

POST /assemble
  { "command": "ffmpeg -y -i ... /data/output.mp4" }
  -> { "returncode": 0, "stdout": "...", "stderr": "..." }
"""
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)


@app.route("/assemble", methods=["POST"])
def assemble():
    data = request.get_json(force=True)
    command = data.get("command")
    if not command:
        return jsonify({"status": "error", "message": "no command provided"}), 400

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return jsonify({
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
