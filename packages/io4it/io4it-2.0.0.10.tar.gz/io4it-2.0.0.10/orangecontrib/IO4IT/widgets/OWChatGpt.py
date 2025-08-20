import os
import sys
import base64
import ast
import openai
import Orange
from Orange.data import StringVariable
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.settings import Setting
from AnyQt.QtWidgets import QApplication, QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.IO4IT.utils import offuscation_basique
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.IO4IT.utils import offuscation_basique

class ChatGpt(OWWidget):
    name = "CallChatGptApi"
    description = "Call to chatgpt API. You need to provide a prompt and an api_keys. You call also add an image_paths and a system_prompt if you want."
    icon = "icons/chatgpt.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/chatgpt.png"
    priority = 3000
    max_tokens = Setting(4096)
    temperature = Setting(0)
    model = Setting("gpt-4o")
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owchatgpt.ui")
    want_control_area = False
    category = "AAIT - LLM INTEGRATION"

    class Inputs:
        data = Input("Data", Orange.data.Table)

    @Inputs.data
    def set_data(self, in_data):
        if in_data is None:
            return
        if "prompt" not in in_data.domain:
            self.error("input table need a prompt column")
            return
        self.prompt = in_data.get_column("prompt")[0]
        if "image_paths" in in_data.domain:
            self.image_paths = in_data.get_column("image_paths")[0]
        if "api_keys" not in in_data.domain:
            self.api_keys = offuscation_basique.lire_config_cli_api("CHAT_GPT")
            if offuscation_basique.lire_config_cli_api("CHAT_GPT") is None:
                self.error("input table need a api_keys column or a folder API with you CHAT_GPT keys in aait store")
        if self.api_keys is None:
            self.api_keys = in_data.get_column("api_keys")[0]
        if "system_prompt" in in_data.domain:
            self.system_prompt = in_data.get_column("system_prompt")[0]
        self.data = in_data
        self.run()

    class Outputs:
        data = Output("Data", Orange.data.Table)

    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(400)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)
        self.edit_model = self.findChild(QLineEdit, 'modelName')
        self.edit_model.setPlaceholderText("Model name")
        self.edit_model.setText(self.model)
        self.edit_model.editingFinished.connect(self.update_parameters)

        self.edit_max_tokens = self.bind_spinbox("boxMaxTokens", self.max_tokens)
        self.edit_temperature = self.bind_spinbox("boxTemperature", self.temperature, is_double=True)
        self.pushButton_call_api =self.findChild(QPushButton, 'callApi')
        self.pushButton_call_api.clicked.connect(self.run)

        self.data = None
        self.prompt = None
        self.image_paths = None
        self.api_keys = None
        self.system_prompt = ""
        self.text_response = None
        self.thread = None
        self.run()

    def bind_spinbox(self, name, value, is_double=False):
        widget_type = QDoubleSpinBox if is_double else QSpinBox
        box = self.findChild(widget_type, name)
        box.setValue(value)
        box.editingFinished.connect(self.update_parameters)
        return box

    def update_parameters(self):
        self.max_tokens = self.edit_max_tokens.value()
        self.temperature = self.edit_temperature.value()
        self.model = self.edit_model.text()

    def generate_answers(self):
        try:
            openai.api_key = self.api_keys
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": self.prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            self.text_response = response.choices[0].message.content
        except Exception as e:
            print(e)
            self.error(f"Error: {e}")
            return
        if self.text_response is None:
            self.error("No response from chatgpt.")


    def run(self):
        self.error("")
        self.warning("")
        if self.data is None:
            return

        if self.prompt == "" or self.prompt is None:
            self.error("No prompt provided.")
            return

        if self.api_keys is None:
            self.error("No api keys provided.")
            return

        # si on relance la génération par le bouton le prompt est déjà rempli (déjà une liste)
        # mais on peut changer le model, la temp ou le nombre max de token
        if isinstance(self.prompt, list):
            self.prompt = [{"type": "text", "text": self.prompt}]
            if self.image_paths is not None and self.image_paths != []:
                if type(self.image_paths) == str:
                    self.image_paths = ast.literal_eval(self.image_paths)
                for img_path in self.image_paths:
                    filename = os.path.basename(img_path)

                    # Ajoute une mention de l’image avant
                    self.prompt.append({
                        "type": "text",
                        "text": f"Photo : {filename}"
                    })

                    with open(img_path, "rb") as f:
                        b64_img = base64.b64encode(f.read()).decode("utf-8")
                        self.prompt.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_img}"
                            }
                        })
        self.progressBarInit()
        self.thread = thread_management.Thread(self.generate_answers)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def handle_progress(self, progress) -> None:
        value = progress[0]
        text = progress[1]
        if value is not None:
            self.progressBarSet(value)
        if text is None:
            self.textBrowser.setText("")
        else:
            self.textBrowser.insertPlainText(text)

    def handle_result(self, result):
        new_name_column = StringVariable("answer")
        table = self.data.add_column(new_name_column, [self.text_response])
        self.Outputs.data.send(table)

    def handle_finish(self):
        print("Generation finished")
        self.progressBarFinished()

    def post_initialized(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = ChatGpt()
    my_widget.show()

    if hasattr(app, "exec"):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())
