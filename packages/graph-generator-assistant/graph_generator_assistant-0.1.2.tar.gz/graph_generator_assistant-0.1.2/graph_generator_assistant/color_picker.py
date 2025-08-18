#!/usr/bin/python3

import signal
import sys
import os
import platform
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QSizePolicy
from PyQt5.QtGui import QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, QTimer
from pynput import mouse

# Checagem de sistema operacional
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

# Se Linux e falhar pyautogui, usaremos Xlib
if IS_LINUX:
    try:
        pyautogui.pixel(0, 0)
        USE_PYAUTOGUI = True
    except Exception:
        USE_PYAUTOGUI = False
        from Xlib import display, X

        def get_pixel_linux(x, y):
            dsp = display.Display()
            root = dsp.screen().root
            raw = root.get_image(x, y, 1, 1, X.ZPixmap, 0xffffffff).data
            b, g, r = raw[0], raw[1], raw[2]
            return r, g, b
else:
    USE_PYAUTOGUI = True


class ColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color")
        self.setGeometry(100, 100, 240, 200)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # on top
        
        ## Icon
        # Get base directory for icons
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir_path, 'icons', 'color_picker.png')
        self.setWindowIcon(QIcon(icon_path)) 

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Click 'Start' button")
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAutoFillBackground(True)
        layout.addWidget(self.label)
        
        
        flo = QFormLayout()
        self.html_text = QLineEdit("")
        self.html_text.setReadOnly(True)
        flo.addRow("Hex:", self.html_text)
        self.rgb_text = QLineEdit("")
        self.rgb_text.setReadOnly(True)
        flo.addRow("RGB:", self.rgb_text)
        layout.addLayout(flo)

        self.button = QPushButton("Start")
        self.button.setToolTip("Start color detection") 
        self.button.clicked.connect(self.start_color_detection)
        layout.addWidget(self.button)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_color)

        self.running = False

    def start_color_detection(self):
        self.html_text.setText("")
        self.rgb_text.setText("")
        
        self.running = True
        self.timer.start(100)
        
        listener = mouse.Listener(on_click=self.stop_on_click)
        listener.start()

    def stop_on_click(self, x, y, button, pressed):
        if pressed:
            self.running = False
            QTimer.singleShot(0, self.stop_timer_and_reset_label)
            
            return False


    def stop_timer_and_reset_label(self):
        self.timer.stop()
        self.label.setText("Clique em 'Iniciar'")

        cor_fundo = self.label.palette().color(QPalette.Window)
        self.html_text.setText(cor_fundo.name())
        self.rgb_text.setText(f"RGB({cor_fundo.red()}, {cor_fundo.green()}, {cor_fundo.blue()})")

    def update_color(self):
        if not self.running:
            return

        try:
            x, y = pyautogui.position()

            if USE_PYAUTOGUI:
                r, g, b = pyautogui.pixel(x, y)
            elif IS_LINUX:
                r, g, b = get_pixel_linux(x, y)
            else:
                r = g = b = 0  # fallback

            self.label.setText(f"RGB({r}, {g}, {b})")

            color = QColor(r, g, b)
            palette = self.label.palette()
            palette.setColor(QPalette.Window, color)
            self.label.setPalette(palette)

        except Exception as e:
            self.label.setText(f"Error: {e}")
            self.timer.stop()
            self.running = False

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = ColorPicker()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

