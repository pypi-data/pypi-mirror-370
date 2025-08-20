import datetime
import ntpath
import os
import wave
import tempfile
import shutil
from AnyQt.QtCore import QThread, pyqtSignal
from AnyQt.QtWidgets import QApplication, QTextEdit, QPushButton, QSpinBox
from pyannote.audio import Audio
from pyannote.core import Segment

import numpy as np
import torch
import whisper
from Orange.data import Table, Domain, StringVariable
from Orange.widgets import widget
from Orange.widgets.utils.signals import Output
from sklearn.cluster import KMeans
from speechbrain.inference.speaker import EncoderClassifier

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils import SimpleDialogQt
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path, GetFromRemote
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils import SimpleDialogQt
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path, GetFromRemote

import subprocess

def convert_audio_to_pcm(file_path, ffmpeg_path):
    try:

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in [".mp3", ".wav", ".m4a"]:
            print(f"[ERREUR] Type de fichier non supporté : {ext}")
            return None

        pcm_wav_path = file_path.replace(ext, "_pcm.wav")  # pas de nom compliqué ici

        ffmpeg_cmd = [
            ffmpeg_path, "-y",
            "-i", file_path,
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            pcm_wav_path
        ]

        print(f"[INFO] Lancement de ffmpeg : {' '.join(ffmpeg_cmd)}")
        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"[ERREUR] ffmpeg a échoué avec le code {result.returncode}")
            print("[STDERR]", result.stderr)
            return None

        if os.path.exists(pcm_wav_path):
            print(f"[INFO] Fichier converti : {pcm_wav_path}")
            return pcm_wav_path
        else:
            print("[ERREUR] Le fichier converti n’a pas été trouvé.")
            return None

    except Exception as e:
        print("❌ Exception pendant la conversion audio :", e)
        return None


def get_wav_duration(wav_path):
    try:
        with wave.open(wav_path, "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return frames / float(rate)
    except Exception as e:
        # and print the error message
        print("An error occurred when getting the  wav duration : ", e)
        return


class TranscriptionThread(QThread):
    result_signal = pyqtSignal(str, list, float)

    def __init__(self, file_path, model, embedding_model, audio_helper, num_speakers=2):
        super().__init__()
        self.file_path = file_path
        self.model = model
        self.embedding_model = embedding_model
        self.audio_helper = audio_helper
        self.num_speakers = num_speakers

    def run(self):
        try:
            print("[THREAD] Démarrage du thread de transcription")
            print(f"[THREAD] Fichier à traiter : {self.file_path}")

            if not os.path.exists(self.file_path):
                print(f"[ERREUR] Le fichier n'existe pas : {self.file_path}")
                self.result_signal.emit("Erreur : fichier introuvable.", [], 0.0)
                return

            file_duration = get_wav_duration(self.file_path)
            print(f"[INFO] Durée du fichier : {file_duration:.2f} sec" if file_duration else "[ERREUR] Durée inconnue")

            if file_duration is None:
                self.result_signal.emit("Error: File duration unknown.", [], 0.0)
                return

            print("[INFO] Début de la transcription avec Whisper")
            start_time = datetime.datetime.now()

            result = self.model.transcribe(
                self.file_path,
                language="fr",
                without_timestamps=False,
                temperature=0
            )

            transcription_time = (datetime.datetime.now() - start_time).total_seconds() / 60
            print(f"[INFO] Transcription terminée en {transcription_time:.2f} min")

            if not result or "segments" not in result or not result["segments"]:
                print("[ERREUR] Aucun segment détecté")
                self.result_signal.emit("Error: No speech detected.", [], transcription_time)
                return

            segments = result["segments"]
            print(f"[INFO] Nombre de segments détectés : {len(segments)}")

            embeddings = None

            for i, segment in enumerate(segments):
                start, end = segment["start"], segment["end"]

                if end > file_duration:
                    print(f"[AVERTISSEMENT] Segment {i} ignoré (fin hors durée)")
                    continue

                try:
                    waveform, _ = self.audio_helper.crop(self.file_path, Segment(start, end))
                    if waveform.ndim == 1:
                        waveform = waveform.unsqueeze(0)
                    with torch.no_grad():
                        embedding = self.embedding_model.encode_batch(waveform).squeeze().cpu().numpy()
                    if embeddings is None:
                        embeddings = np.zeros((len(segments), embedding.shape[0]))
                    embeddings[i] = embedding
                except Exception as crop_err:
                    print(f"[ERREUR] Erreur lors du crop ou de l'embedding pour le segment {i} : {crop_err}")
                    continue

            print("[INFO] Clustering des embeddings avec KMeans")
            clustering = KMeans(n_clusters=min(self.num_speakers, len(segments)), random_state=42).fit(embeddings)
            labels = clustering.labels_

            speaker_map = {}
            merged_segments = []
            current_speaker = None
            current_text = ""
            current_start = None
            table_output = []

            print("[INFO] Regroupement par locuteur")
            for i, segment in enumerate(segments):
                speaker_id = labels[i]
                if speaker_id not in speaker_map:
                    speaker_map[speaker_id] = f"SPEAKER {len(speaker_map) + 1}"
                speaker = speaker_map[speaker_id]

                if current_speaker == speaker:
                    current_text += f" {segment['text']}"
                else:
                    if current_speaker is not None:
                        timestamp = str(datetime.timedelta(seconds=round(current_start)))
                        merged_segments.append(f"{current_speaker} {timestamp}: {current_text}")
                        table_output.append([current_speaker, timestamp, current_text])
                    current_speaker = speaker
                    current_text = segment["text"]
                    current_start = segment["start"]

            print("[INFO] Finalisation des résultats")
            speaker_text_output = "\n".join(merged_segments)
            self.result_signal.emit(speaker_text_output, table_output, transcription_time)
            print("[THREAD] Transcription terminée et signal émis")

        except Exception as e:
            print("❌ An error occurred during transcription:", e)
            import traceback
            traceback.print_exc()
            return


class OWSpeech_To_Text(widget.OWWidget):
    name = "Speech To Text"
    description = "Convert audio to text with speaker recognition"
    priority = 1111
    category = "Advanced Artificial Intelligence Tools"
    icon = "icons/speech_to_text.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/speech_to_text.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owspeechtotext.ui")
    category = "AAIT - TOOLBOX"

    class Outputs:
        data = Output("Data", Table)
        global_transcription = Output("Global Transcription", Table)

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.num_speakers = 4 # spin box a defaut 4

        self.local_store_path = get_local_store_path()
        model_name = "small.pt"
        self.embedding_model_name = "spkrec-ecapa-voxceleb"
        self.model_path = os.path.join(self.local_store_path, "Models", "S2T", model_name)
        self.embedding_model_path = os.path.join(self.local_store_path, "Models", "S2T", self.embedding_model_name)

        self.ffmpeg_path = os.path.join(self.local_store_path, "Models", "S2T", "ffmpeg", "bin", "ffmpeg.exe")
        # Extraire le dossier de ffmpeg.exe
        ffmpeg_bin_dir = os.path.dirname(self.ffmpeg_path)

        # Ajouter ffmpeg au PATH pour whisper/ffmpeg-python
        if ffmpeg_bin_dir not in os.environ["PATH"]:
            os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ["PATH"]
            print(f"[INFO] Dossier ffmpeg ajouté au PATH Python : {ffmpeg_bin_dir}")


        if not os.path.exists(self.model_path):
            if not SimpleDialogQt.BoxYesNo("Whisper turbo Transcription Model isn't in your computer. Do you want to download it from AAIT store?"):
                return
            try:
                if 0 != GetFromRemote("Whisper turbo"):
                    return
            except Exception as e:
                print(e)
                SimpleDialogQt.BoxError("Unable to get the Whisper turbo.")
                return

        if not os.path.exists(self.embedding_model_path):
            if not SimpleDialogQt.BoxYesNo("Voxceleb Embedding Model isn't in your computer. Do you want to download it from AAIT store?"):
                return
            try:
                if 0 != GetFromRemote("Voxceleb"):
                    return
            except Exception as e:
                print(e)
                SimpleDialogQt.BoxError("Unable to get the Voxceleb.")
                return
        if not os.path.exists(self.ffmpeg_path):
            if not SimpleDialogQt.BoxYesNo("FFMPEG isn't in your computer. Do you want to download it from AAIT store?"):
                return
            try:
                if 0 != GetFromRemote("FFMPEG"):
                    return
            except Exception as e:
                print(e)
                SimpleDialogQt.BoxError("Unable to get the ffmpeg.")
                return

        self.model = whisper.load_model(self.model_path)
        print("Version of PyTorch :", torch.__version__)
        print("Used cuda version :", torch.version.cuda)
        print("CUDA available ? :", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("Number of GPU :", torch.cuda.device_count())
            print("GPU's name :", torch.cuda.get_device_name(0))
        # Définition d'un model d'embedding (hard codé pour l'instant)

        self.embedding_model = EncoderClassifier.from_hparams(source=self.embedding_model_path)
        self.audio_helper = Audio()
        uic.loadUi(self.gui, self)

        self.file_button = self.findChild(QPushButton,
                                          'fileButton')
        self.file_button.clicked.connect(self.select_file)
        self.process_button = self.findChild(QPushButton,
                                             'processButton')
        self.process_button.clicked.connect(self.process_recording)
        self.text_area = self.findChild(QTextEdit, 'textArea')

        self.spinBox_nb_people=self.findChild(QSpinBox,'spinBox_nb_people')
        self.spinBox_nb_people.setValue(int(self.num_speakers))
        self.spinBox_nb_people.valueChanged.connect(self.spinbox_value_changed)
        self.process_button.setEnabled(False)

    def spinbox_value_changed(self, value):
        self.num_speakers = value

    def select_file(self):
        file_path = SimpleDialogQt.BoxSelectExistingFile(self, extention="Audio files (*.wav *.mp3 *.m4a)")

        if file_path:
            # 🔃 Copie dans un chemin sans accents ni caractères spéciaux
            temp_dir = tempfile.gettempdir()
            base_ext = os.path.splitext(file_path)[1]
            clean_copy = os.path.join(temp_dir, "input_audio" + base_ext)
            shutil.copy(file_path, clean_copy)
            print(f"[INFO] Copie vers fichier temporaire sans accents : {clean_copy}")

            # 🔁 Conversion dans ce dossier temporaire
            pcm_path = convert_audio_to_pcm(clean_copy, self.ffmpeg_path)
            print(f"[DEBUG] pcm_path: {pcm_path}")

            if pcm_path:
                self.file_path = pcm_path
                self.temp_pcm_path = pcm_path
                self.process_button.setEnabled(True)
            else:
                SimpleDialogQt.BoxError("Erreur : La conversion audio a échoué.")
        else:
            print("[ERREUR] Aucun fichier sélectionné.")


    def process_recording(self):
        self.process_button.setEnabled(False)
        if not self.file_path:
            SimpleDialogQt.BoxError(
                "Aucun fichier sélectionné. Veuillez choisir un fichier audio avant de lancer la transcription.")
            return
        self.num_speakers = self.spinBox_nb_people.value()
        self.text_area.setText("Transcription in progress...")
        self.thread = TranscriptionThread(
            self.file_path, self.model, self.embedding_model, self.audio_helper, self.num_speakers
        )
        self.thread.result_signal.connect(self.display_text)
        self.thread.start()
        self.progressBarInit()  # Ajout de la barre de progression

    def display_text(self, text, table_output, transcription_time):
        self.text_area.setText(f"{text}\n\n⏳ Temps de transcription: {transcription_time:.2f} minutes")

        # Sortie 1 : tableau par speaker
        domain = Domain([],
                        metas=[StringVariable("Speaker"), StringVariable("Timestamp"), StringVariable("Transcription")])
        metas = [[row[0], row[1], row[2]] for row in table_output] if table_output else [["", "", ""]]
        out_data = Table(domain, [[] for _ in metas])
        for i, meta in enumerate(metas):
            out_data.metas[i] = meta
        self.Outputs.data.send(out_data)

        # Sortie 2 : une seule ligne avec toutes les infos
        global_domain = Domain([],
                               metas=[StringVariable("Nom du fichier"),
                                      StringVariable("Transcription"),
                                      StringVariable("Temps de transcription (min)")])
        filename = ntpath.basename(self.file_path)  # Pour ne garder que le nom du fichier
        global_metas = [[filename, text, f"{transcription_time:.2f}"]]
        global_table = Table(global_domain, [[]])
        global_table.metas[0] = global_metas[0]
        self.Outputs.global_transcription.send(global_table)
        self.progressBarFinished()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = OWSpeech_To_Text()
    window.show()
    if hasattr(app, "exec"):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())
