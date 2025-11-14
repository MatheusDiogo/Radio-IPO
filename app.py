import os
import glob
from flask import Flask, render_template, send_file, abort, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "coralipo12345"

# --- CONFIGURAÇÕES ---
VOICES_DIR = 'Vozes'            # Diretório que contém as vozes
FILE_PATTERN = '*.mp3'          # Tipo de arquivo de música
MIME_TYPE = 'audio/mpeg'        # MIME para MP3
# ----------------------

# Dicionário global:
# MUSIC_PATHS["Tenor"]["arquivo.mp3"] = caminho absoluto
MUSIC_PATHS = {}

PASSWORD = "coralipo"  # senha fixa

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha = request.form.get("senha")
        if senha == PASSWORD:
            session["auth"] = True
            return redirect(url_for('index'))
        return render_template("login.html", error="Senha incorreta!")

    return render_template("login.html")

def load_music_files():
    """
    Carrega todas as vozes (pastas dentro de /Vozes)
    e todos os arquivos mp3 dentro de cada pasta.
    """
    global MUSIC_PATHS
    MUSIC_PATHS.clear()

    if not os.path.isdir(VOICES_DIR):
        print(f"ERRO: Diretório '{VOICES_DIR}' não existe.")
        return

    voices = sorted([
        d for d in os.listdir(VOICES_DIR)
        if os.path.isdir(os.path.join(VOICES_DIR, d))
    ])

    print(f"Vozes encontradas ({len(voices)}): {voices}")

    for voice in voices:
        full_voice_dir = os.path.join(VOICES_DIR, voice)
        files = sorted(glob.glob(os.path.join(full_voice_dir, FILE_PATTERN)))

        MUSIC_PATHS[voice] = {}

        for full_path in files:
            filename = os.path.basename(full_path)
            MUSIC_PATHS[voice][filename] = full_path

        print(f"  - {voice}: {len(files)} arquivos")


# ---------------------------------------
# 1️⃣ PÁGINA PRINCIPAL → Lista de Vozes
# ---------------------------------------
@app.route('/')
def index():
    if not session.get("auth"):
        return redirect(url_for('login'))

    voices = sorted(MUSIC_PATHS.keys())
    return render_template('index.html', voices=voices)


# ----------------------------------------------------
# 2️⃣ LISTA DE MÚSICAS DA VOZ → /voz/<voz_escolhida>
# ----------------------------------------------------
@app.route('/voz/<voice_name>')
def voice_page(voice_name):
    if not session.get("auth"):
        return redirect(url_for('login'))
    
    if voice_name not in MUSIC_PATHS:
        abort(404, description="Voz não encontrada.")

    songs = sorted(MUSIC_PATHS[voice_name].keys())

    return render_template(
        'songs.html',
        voice_name=voice_name,
        songs=songs
    )


# ----------------------------------------
# 3️⃣ PLAYER → /player?voice=X&song=Y
# ----------------------------------------
@app.route('/player')
def player_page():
    if not session.get("auth"):
        return redirect(url_for('login'))
    
    voice = request.args.get('voice')
    song = request.args.get('song')

    if not voice or voice not in MUSIC_PATHS:
        abort(404, description="Voz inválida.")

    if not song or song not in MUSIC_PATHS[voice]:
        abort(404, description="Música não encontrada.")

    return render_template('player.html', voice=voice, song=song)


# -----------------------------------------------------
# ROTA QUE ENTREGA O ARQUIVO MP3 → /play/<voz>/<arquivo>
# -----------------------------------------------------
@app.route('/play/<voice>/<path:filename>')
def play_song(voice, filename):
    if not session.get("auth"):
        return redirect(url_for('login'))
    
    if voice not in MUSIC_PATHS:
        abort(404, description="Voz inválida.")

    full_path = MUSIC_PATHS[voice].get(filename)

    if not full_path or not os.path.exists(full_path):
        abort(404, description="Arquivo não encontrado.")

    print(f"Servindo: {voice}/{filename}")

    return send_file(full_path, mimetype=MIME_TYPE)


# Inicialização
if __name__ == '__main__':
    load_music_files()

    port = int(os.environ.get("PORT", 2000))
    print(f"Rodando na porta {port}...")

    app.run(host='0.0.0.0', port=port)