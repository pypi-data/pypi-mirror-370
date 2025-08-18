import os
import sys
import logging
import urllib.parse
import datetime
import time
from pathlib import Path
import fitz
import numpy as np
import pandas as pd
import easyocr
from concurrent.futures import ProcessPoolExecutor, as_completed

from AnyQt.QtCore import QThread, pyqtSignal
from AnyQt.QtWidgets import QApplication, QLabel, QSpinBox, QTextEdit, QPushButton
from AnyQt import uic

from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Domain, StringVariable, Table

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode
from docling.exceptions import ConversionError

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.fix_torch import fix_torch_dll_error
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.fix_torch import fix_torch_dll_error
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file


fix_torch_dll_error.fix_error_torch()

logging.getLogger("fitz").setLevel(logging.ERROR)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0

from pathlib import Path
from doc2docx import convert
import hashlib

def convert_doc_to_docx(fpath):
    fpath = Path(fpath)
    if fpath.suffix.lower() != ".doc":
        return fpath

    new_path = fpath.with_suffix(".docx")
    if new_path.exists():
        return new_path

    try:
        convert(str(fpath))
        if new_path.exists() and new_path.stat().st_size > 0:
            return new_path
        else:
            raise RuntimeError("Fichier .docx non créé ou vide après conversion")
    except Exception as e:
        raise RuntimeError(f"Erreur conversion .doc → .docx : {e}")

def convert_ppt_to_pdf(fpath):
    import win32com.client
    fpath = Path(fpath)
    if fpath.suffix.lower() != ".ppt":
        return fpath  # Rien à faire

    pdf_path = fpath.with_suffix(".pdf")
    if pdf_path.exists():
        return pdf_path

    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        powerpoint.Visible = 1
        presentation = powerpoint.Presentations.Open(str(fpath), WithWindow=False)
        presentation.SaveAs(str(pdf_path), 32)  # 32 = ppSaveAsPDF
        presentation.Close()
        powerpoint.Quit()
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            raise RuntimeError("PDF non généré")
        return pdf_path
    except Exception as e:
        raise RuntimeError(f"Erreur conversion .ppt → .pdf : {e}")


def truncate_path(path, max_length=240):
    path = Path(path)
    if len(str(path)) <= max_length:
        return path
    hashed = hashlib.md5(str(path).encode()).hexdigest()
    new_name = path.stem[:50] + "_" + hashed + path.suffix
    return path.parent / new_name

def safe_filename(name):
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)





def convert_doc_to_docx(fpath):
    fpath = Path(fpath)
    if fpath.suffix.lower() != ".doc":
        return fpath  # Pas besoin de convertir

    new_path = fpath.with_suffix(".docx")

    if new_path.exists():
        return new_path

    try:
        convert(str(fpath))  # Appel à doc2docx
        if new_path.exists() and new_path.stat().st_size > 0:
            return new_path
        else:
            raise RuntimeError("Fichier .docx non créé ou vide après conversion")
    except Exception as e:
        raise RuntimeError(f"Erreur conversion .doc → .docx : {e}")


def process_file_worker(file_path_str, output_dir_str):
    logs = []
    start_time = time.time()
    start_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(msg):
        logs.append(msg)

    # Convertir les fichiers .doc et .ppt
    try:
        if Path(file_path_str).suffix.lower() == ".doc":
            file_path = convert_doc_to_docx(file_path_str)
            log(f"[CONVERT] ✅ Conversion .doc vers .docx réussie : {Path(file_path).name}")
        if Path(file_path).suffix.lower() == ".ppt":
            file_path = convert_ppt_to_pdf(file_path)
            log(f"[CONVERT] ✅ Conversion .ppt vers .pdf réussie : {file_path.name}")

    except Exception as e:
        log(f"[ERROR] ❌ Échec conversion : {e}")
        return [
            str(Path(file_path_str).parent), str(output_dir_str), Path(file_path_str).name, "",
            [f"[{start_str}] {msg}" for msg in logs],
            {
                "name": Path(file_path_str).name,
                "content": "",
                "input_dir": str(Path(file_path_str).parent),
                "status": "non converti",
                "duration_sec": round(time.time() - start_time, 2),
                "timestamp": start_str,
                "type conversion": "échec conversion"
            }
        ]

    file_path = truncate_path(file_path)  # nom de fichier markdown sécurisé
    output_file_path = truncate_path(output_file_path)
    file_path = Path(file_path)  # Assure qu'on a bien un Path
    output_dir = Path(output_dir_str)
    output_file_path = output_dir / (file_path.stem + "_md-with-image-refs.md")
    file_path = truncate_path(file_path)  # nom de fichier markdown sécurisé
    output_file_path = truncate_path(output_file_path)  # chemin de sortie markdown sécurisé

    if output_file_path.exists():
        return None
    logs = []

    output_file_started = output_dir / (file_path.stem + ".mds")
    if os.path.exists(output_file_started):
        return [
            str(file_path.parent), str(output_dir), file_path.name, "",
            [f"[_] {msg}" for msg in logs],
            {
                "name": file_path.name,
                "content": "blablbabla",
                "input_dir": str(file_path.parent),
                "status": "error start but not finished",
                "duration_sec": round(0, 2),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # z mofifirt
                "type conversion": "error"
            }
        ]
    with open(output_file_started, 'w') as file:
        pass

    def log(msg):
        logs.append(msg)

    def is_pdf_text_based(fpath):
        try:
            with fitz.open(fpath) as doc:
                return any(page.get_text().strip() for page in doc)
        except:
            return False

    def ocr_fallback():
        log(f"[OCR] Lancement OCR sur {file_path.name}")
        reader = easyocr.Reader(['fr', 'en'])
        _ = reader.readtext(np.zeros((100, 100, 3), dtype=np.uint8), detail=0)
        with fitz.open(file_path) as doc:
            content = ""
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                result = reader.readtext(img)
                content += "\n".join([r[1] for r in result]) + "\n\n"
        return content

    start_time = time.time()
    start_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        if output_file_path.exists():
            duration = time.time() - start_time
            content = output_file_path.read_text(encoding='utf-8')
            log(f"[SKIP] ✅ Déjà converti : {file_path.name} ({duration:.2f} sec)")
            return [
                str(file_path.parent), str(output_dir), file_path.name, content,
                [f"[{start_str}] {msg}" for msg in logs],
                {
                    "name": file_path.name,
                    "content": content,
                    "input_dir": str(file_path.parent),
                    "status": "ok",
                    "duration_sec": round(duration, 2),
                    "timestamp": start_str,
                    "type conversion": "deja converti"
                }
            ]

        log(f"[DOC] 📄 Traitement : {file_path.name}")

        if file_path.suffix.lower() == ".pdf" and is_pdf_text_based(file_path):
            try:
                pipeline_options = PdfPipelineOptions()
                pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
                pipeline_options.generate_page_images = True
                pipeline_options.generate_picture_images = True
                conv_res = DocumentConverter(
                    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
                ).convert(file_path)
                conv_res.document.save_as_markdown(output_file_path, image_mode=ImageRefMode.REFERENCED)
                for image_file in output_file_path.parent.glob(f"{file_path.stem}*_*.png"):
                    if len(str(image_file)) > 240:
                        new_image_file = truncate_path(image_file)
                        image_file.rename(new_image_file)
                        try:
                            with open(output_file_path, "r", encoding="utf-8") as md_file:
                                content_md = md_file.read()
                            content_md = content_md.replace(image_file.name, new_image_file.name)
                            with open(output_file_path, "w", encoding="utf-8") as md_file:
                                md_file.write(content_md)
                        except Exception as e:
                            log(f"[WARNING] ⚠️ Erreur mise à jour des noms d'images dans le markdown : {e}")

                try:
                    content = urllib.parse.unquote(output_file_path.read_text(encoding="utf-8"))
                    log("[ENCODING] ✅ Lecture markdown avec encodage utf-8")
                except UnicodeDecodeError:
                    log("[ENCODING] ⚠️ utf-8 échoué, tentative avec utf-8-sig")
                    try:
                        content = urllib.parse.unquote(output_file_path.read_text(encoding="utf-8-sig"))
                        log("[ENCODING] ✅ Lecture markdown avec utf-8-sig")
                    except UnicodeDecodeError:
                        log("[ENCODING] ⚠️ utf-8-sig échoué, fallback latin-1")
                        content = urllib.parse.unquote(output_file_path.read_text(encoding="latin-1"))
                        log("[ENCODING] ✅ Lecture markdown avec latin-1")

                #content = urllib.parse.unquote(output_file_path.read_text(encoding='utf-8'))
                log(f"[DOC] ✅ Conversion OK : {file_path.name}")
                type_conv = "md"
                statut = "ok"
            except Exception as e:
                log(f"[ERROR] ⚠️ Erreur Docling : {file_path.name} — {e}")
                content = ocr_fallback()
                type_conv = "ocr"
                statut = "ok"
        elif file_path.suffix.lower() == ".pdf":
            log(f"[OCR] 🧾 PDF image détecté : {file_path.name}")
            content = ocr_fallback()
            type_conv = "ocr"
            statut = "ok"
        elif file_path.suffix.loxer() == "docx": #else:
            try:
                conv_res = DocumentConverter().convert(file_path)
                conv_res.document.save_as_markdown(output_file_path, image_mode=ImageRefMode.REFERENCED)
                for image_file in output_file_path.parent.glob(f"{file_path.stem}*_*.png"):
                    if len(str(image_file)) > 240:
                        new_image_file = truncate_path(image_file)
                        image_file.rename(new_image_file)
                        try:
                            with open(output_file_path, "r", encoding="utf-8") as md_file:
                                content_md = md_file.read()
                            content_md = content_md.replace(image_file.name, new_image_file.name)
                            with open(output_file_path, "w", encoding="utf-8") as md_file:
                                md_file.write(content_md)
                        except Exception as e:
                            log(f"[WARNING] ⚠️ Erreur mise à jour des noms d'images dans le markdown : {e}")

                try:
                    content = urllib.parse.unquote(output_file_path.read_text(encoding="utf-8"))
                    log("[ENCODING] ✅ Lecture markdown avec encodage utf-8")
                except UnicodeDecodeError:
                    log("[ENCODING] ⚠️ utf-8 échoué, tentative avec utf-8-sig")
                    try:
                        content = urllib.parse.unquote(output_file_path.read_text(encoding="utf-8-sig"))
                        log("[ENCODING] ✅ Lecture markdown avec utf-8-sig")
                    except UnicodeDecodeError:
                        log("[ENCODING] ⚠️ utf-8-sig échoué, fallback latin-1")
                        content = urllib.parse.unquote(output_file_path.read_text(encoding="latin-1"))
                        log("[ENCODING] ✅ Lecture markdown avec latin-1")

                type_conv = "md"
                statut = "ok"
            except Exception as e:
                log(f"[ERROR] ⚠️ Erreur conversion fichier {file_path.name} : {e}")
                content = f"[Erreur conversion] Aucun contenu exploitable : {e}"
                type_conv = "error"
                statut = "nok"

        duration = time.time() - start_time
        log(f"[END] ✅ Fin traitement {file_path.name} en {duration:.2f} secondes")

        if not output_file_path.exists():
            output_file_path.write_text(content, encoding='utf-8')

        return [
            str(file_path.parent), str(output_dir), file_path.name, content,
            [f"[{start_str}] {msg}" for msg in logs],
            {
                "name": file_path.name,
                "content": content,
                "input_dir": str(file_path.parent),
                "status": statut,
                "duration_sec": round(duration, 2),
                "timestamp": start_str,
                "type conversion": type_conv
            }
        ]

    except Exception as e:
        duration = time.time() - start_time
        content = f"[Erreur inattendue] {e}"
        log(f"[ERROR] ❌ Exception inattendue : {file_path.name} — {e} (⏱️ {duration:.2f}s)")
        return [
            str(file_path.parent), str(output_dir), file_path.name, content,
            [f"[{start_str}] {msg}" for msg in logs],
            {
                "name": file_path.name,
                "content": content,
                "input_dir": str(file_path.parent),
                "status": "error",
                "duration_sec": round(duration, 2),
                "timestamp": start_str,
                "type conversion": "error"
            }
        ]


class MarkdownConversionThread(QThread):
    result = pyqtSignal(list)
    progress = pyqtSignal(float)
    finish = pyqtSignal()
    log = pyqtSignal(str)

    def __init__(self, input_dir, max_workers, parent=None):
        super().__init__(parent)
        self.input_dir = Path(input_dir)
        self.output_dir = self.input_dir / "a_md"
        self.max_workers = max_workers

    def run(self):
        os.makedirs(self.output_dir,exist_ok=True)
        global_start = time.time()
        self.log.emit(f"[THREAD] 📁 Traitement du dossier : {self.input_dir}")
        results = []
        files = list(self.input_dir.glob("*.pdf")) + list(self.input_dir.glob("*.docx")) + list(
            self.input_dir.glob("*.doc")) + list(self.input_dir.glob("*.pptx")) + list(self.input_dir.glob("*.ppt"))
        if not files:
            self.log.emit("⚠️ Aucun fichier détecté dans le dossier.")
            self.result.emit([[str(self.input_dir), str(self.output_dir), "", "Aucun fichier détecté"]])
            self.finish.emit()
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = self.output_dir / "log.txt"
        excel_file_path = self.output_dir / "conversion.xlsx"

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_file_worker, str(f), str(self.output_dir)): f for f in files}
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                if result is not None:
                    output_file_ok = Path(result[2])
                    output_file_ok_mde_stem = output_file_ok.stem + ".mde"
                    output_path_ok_mde = Path(result[1]) / output_file_ok_mde_stem
                    if result:
                        logs = result[4]
                        for line in logs:
                            self.log.emit(line)
                        results.append(result)

                        # Dans l'écriture des fichiers logs/mde, forcer encoding utf-8
                        try:
                            with open(log_file_path, "a", encoding="utf-8") as f:
                                for line in logs:
                                    f.write(line + "\n")
                        except Exception as e:
                            self.log.emit(f"[ERROR] ❌ Erreur écriture log : {e}")

                        try:
                            data = result[5]
                            with open(output_path_ok_mde, 'w', encoding='utf-8') as file:
                                file.write(str(data))
                        except Exception as e:
                            self.log.emit(f"[ERROR] ❌ Échec écriture MDE : {e}")

                self.progress.emit(i / len(futures) * 100)

        total_duration = time.time() - global_start
        self.log.emit(f"⏱️ Temps total de traitement : {total_duration:.2f} secondes")
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"\n[GLOBAL] ⏱️ Temps total de traitement : {total_duration:.2f} secondes\n")
        self.result.emit(results)
        self.finish.emit()


class FileProcessorApp(widget.OWWidget):
    name = "Markdownizer"
    description = "Convert PDFs, DOCX, PPTX to Markdown"
    icon = "icons/md.png"
    want_control_area = False
    priority = 1001
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owmarkdownizer.ui")
    category = "AAIT - TOOLBOX"

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        data = Output("Markdown Data Table", Table)
        data2 = Output("Markdow Directory Treated", Table)

    def __init__(self):
        super().__init__()
        self.data = None
        self.thread = None
        self.input_dir = None

        uic.loadUi(self.gui, self)

        self.cpu_label = self.findChild(QLabel, "labelCpuInfo")
        self.spin_box = self.findChild(QSpinBox, "spinBoxThreads")
        self.ok_button = self.findChild(QPushButton, "pushButtonOk")
        self.log_box = self.findChild(QTextEdit, "textEditLog")

        self.cpu_label.setText(f"🖥️ CPU disponibles : {os.cpu_count() or 'inconnu'}")
        self.ok_button.clicked.connect(self.restart_processing)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        self.error("")
        if not in_data:
            return

        try:
            input_dir_var = in_data.domain["input_dir"]
            if not isinstance(input_dir_var, StringVariable):
                raise ValueError
            self.input_dir = in_data.get_column("input_dir")[0]
        except (KeyError, ValueError):
            self.error('"input_dir" column is required and must be Text')
            return

        self.start_thread()

    def start_thread(self):
        self.progressBarInit()
        if self.thread:
            self.thread.quit()

        self.log_box.clear()
        self.thread = MarkdownConversionThread(self.input_dir, self.spin_box.value())
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.log.connect(self.append_log)
        self.thread.start()

    def restart_processing(self):
        if not self.data or not self.input_dir:
            self.append_log("[UI] ❌ Données manquantes.")
            return
        self.append_log("[UI] 🔁 Reprise du traitement avec nouveau nombre de threads...")
        self.start_thread()

    def append_log(self, message):
        self.log_box.append(message)

    def handle_progress(self, value):
        self.progressBarSet(value)

    def handle_result(self, result):
        try:
            domain = Domain([], metas=[
                StringVariable('input_dir'),
                StringVariable('output_dir'),
                StringVariable('name'),
                StringVariable('content'),
                StringVariable('status'),
                StringVariable('duration_sec'),
                StringVariable('timestamp'),
                StringVariable('type conversion')
            ])
            table = Table(domain, [[] for _ in result])
            output_dir = Path(self.input_dir) / "a_md"
            for i, meta in enumerate(result):
                if result is None:
                    continue
                info = meta[5] if isinstance(meta[5], dict) else {}
                table.metas[i] = [
                    meta[0], meta[1], meta[2], meta[3],
                    info.get("status", ""),
                    str(info.get("duration_sec", "")),
                    info.get("timestamp", ""),
                    info.get("type conversion", "")
                ]
            self.Outputs.data.send(table)
            markdown_list = []
            for file in Path(output_dir).glob("*.md"):
                markdown_text = file.read_text()
                markdown_list.append([file, markdown_text])

            domain = Domain([], metas=[
                StringVariable('file_name'),
                StringVariable('content_markdown')
            ])
            table2 = Table(domain, [[] for _ in markdown_list])
            for i, meta in enumerate(markdown_list):
                table2.metas[i] = [meta[0], meta[1]]

            self.Outputs.data2.send(table2)
        except Exception as e:
            _log.error("[ERROR] Erreur lors de la génération de la table de sortie :", exc_info=True)
            self.append_log(f"[ERROR] ❌ Sortie non générée : {e}")
            self.Outputs.data.send(None)

    def handle_finish(self):
        self.append_log("✅ Conversion terminée")
        self.progressBarFinished()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget_instance = FileProcessorApp()
    widget_instance.show()
    sys.exit(app.exec() if hasattr(app, "exec") else app.exec_())
