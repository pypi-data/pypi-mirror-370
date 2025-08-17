#!/usr/bin/python3

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFormLayout, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton, QFrame,
    QFileDialog, QGroupBox, QLabel, QButtonGroup, QComboBox, QMessageBox,
    QMainWindow, QAction, QToolBar, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QDesktopServices
import signal
import json
import os

from manuscript_cover_letter.modules.lib_cover_basic  import generate_cover_basic1
from manuscript_cover_letter.modules.lib_cover_style1 import generate_cover_style1
from manuscript_cover_letter.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu
from manuscript_cover_letter.wabout  import show_about_window
import manuscript_cover_letter.about  as about


class DocForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(about.__program_name__)
        self.setGeometry(50, 50, 1200, 400)

        ## Icon
        # Get base directory for icons
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        self.setWindowIcon(QIcon(self.icon_path)) 
        

        # Dados de exemplo
        self.fields = {
            "journal": "Name of journal, ex: Journal of Artificial Intelligence and Urban Systems",
            "complete_name": "Full name of corresponding author",
            "university": "University of corresponding author.",
            "country": "Country of corresponding author.",
            "address": "Address of corresponding author, ex: Lavras MG, CEP 37.200-000, Caixa Postal 3037",
            "emails": "john.doe@datainscience.edu\nj.doe.research@gmail.com",
            "telephone": "Tel. +1 416 555 0134 Office",
            "title": "Title of manuscript",
            "summary": "A paragraph explaining why the article is relevant, what is the main contribution, ex: \nThis study..."
        }

        self.input_widgets = {}

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Criação dos campos dinamicamente
        for key, value in self.fields.items():
            if len(value) > 100 or '\n' in value:
                widget = QTextEdit()
            else:
                widget = QLineEdit()
            widget.setPlaceholderText(value)
            widget.setToolTip(value)
            self.input_widgets[key] = widget
            form_layout.addRow(key.capitalize().replace("_", " ") + ":", widget)

            if key in ["journal", "telephone"]:
                tmp = QLabel("")
                tmp.setFixedHeight(widget.fontMetrics().height() * 1)
                form_layout.addRow(tmp,tmp)
                

        self.input_widgets["emails"].setFixedHeight(widget.fontMetrics().height() * 3)

        layout.addLayout(form_layout)

        # Estilo com QComboBox (mais compacto e escalável)
        style_box = QGroupBox("Choose output style")
        style_layout = QVBoxLayout()
        self.style_combo = QComboBox()
        self.style_combo.addItems(["docx basic", "docx style1", "json cover letter"])
        style_layout.addWidget(self.style_combo)
        style_box.setLayout(style_layout)
        layout.addWidget(style_box)

        # Botão Save As
        self.save_button = QPushButton("Save the cover letter")
        self.save_button.clicked.connect(self.save_file)
        layout.addWidget(self.save_button)

        central_widget.setLayout(layout)

        # Adiciona a toolbar
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        

        # 
        open_action = QAction(QIcon.fromTheme("x-office-address-book"),"Open JSON", self)
        open_action.triggered.connect(self.load_from_json)
        open_action.setToolTip("Load information from JSON file.")
        toolbar.addAction(open_action)
        
        # Adicionar o espaçador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Coffee
        self.coffee_action = QAction(QIcon.fromTheme("emblem-favorite"), "Coffee", self)
        self.coffee_action.setToolTip("Buy me a coffee (TrucomanX)")
        self.coffee_action.triggered.connect(self.on_coffee_action_click)
        toolbar.addAction(self.coffee_action)

        # 
        about_action = QAction(QIcon.fromTheme("help-about"),"About", self)
        about_action.triggered.connect(self.open_about)
        about_action.setToolTip("Show the information of program.")
        toolbar.addAction(about_action)

    def on_coffee_action_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))
        
    def open_about(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)

    def load_from_json(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open JSON files", "", "JSON Files (*.CoverLetter.json)")
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Atualiza os widgets com os dados do JSON
                for key, widget in self.input_widgets.items():
                    if key in data:
                        value = data[key]
                        if isinstance(widget, QTextEdit):
                            widget.setPlainText(value)
                        else:
                            widget.setText(value)

                QMessageBox.information(self, "Sucess", "Successful charged data from JSON!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading JSON:\n{str(e)}")

    def save_file(self):
        fields_dict = {}
        for key, widget in self.input_widgets.items():
            if isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()
            else:
                value = widget.text().strip()
            if not value:
                QMessageBox.critical(
                    self,
                    "Void field",
                    f"The field <b>'{key.replace('_', ' ').capitalize()}'</b> is void. Please fill in all the fields before saving."
                )
                return
            fields_dict[key] = value

        filename, _ = QFileDialog.getSaveFileName(self, "Save cover letter", "", "Word Documents (*.docx);;JSON Files (*.CoverLetter.json)")
        if filename:
            style = self.style_combo.currentText()
            if "json" in style:
                if not filename.endswith(".CoverLetter.json"):
                    filename += ".CoverLetter.json"
            else:
                if not filename.endswith(".docx"):
                    filename += ".docx"

            self.generate_manuscript_file(filename, fields_dict, style)

    @staticmethod
    def generate_manuscript_file(filename, fields_dict, style="docx basic"):
        if style == "docx basic":
            generate_cover_basic1(filename, fields_dict)
        elif style == "docx style1":
            generate_cover_style1(filename, fields_dict)
        elif style == "json cover letter":
            with open(filename, 'w', encoding='utf-8') as arquivo:
                json.dump(fields_dict, arquivo, indent=4, ensure_ascii=False)
        else:
            generate_cover_basic1(filename, fields_dict)

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file('~/.local/share/applications')
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.config/autostart', overwrite=True)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.local/share/applications', overwrite=True)
            return

    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 
    window = DocForm()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

