import os
import subprocess
from flask import Flask, Response

PASTA = "TENOR"  # Pasta com as músicas

app = Flask(__name__)

def gerar_playlist_infinita():
    """Percorre a pasta em ordem alfabética e repete infinitamente."""
    arquivos = sorted(
        [os.path.join(PASTA, f) for f in os.listdir(PASTA) if f.endswith(".mp3")]
    )
    
    while True:
        for musica in arquivos:
            yield musica

playlist = gerar_playlist_infinita()

@app.route("/radio")
def radio():
    def gerar_stream():
        for musica in playlist:
            comando = [
                "ffmpeg",
                "-i", musica,
                "-f", "mp3",
                "-codec:a", "libmp3lame",
                "-"
            ]

            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            for chunk in iter(lambda: processo.stdout.read(4096), b""):
                yield chunk

    return Response(gerar_stream(), mimetype="audio/mpeg")

if __name__ == "__main__":
    print("Rádio rodando em http://localhost:2000/radio")
    app.run(host="0.0.0.0", port=2000, threaded=True)
