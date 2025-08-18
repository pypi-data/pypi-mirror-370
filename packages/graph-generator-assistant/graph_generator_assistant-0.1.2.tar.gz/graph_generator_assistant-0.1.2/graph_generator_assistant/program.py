#!/usr/bin/python3

import signal
import sys
import os
import json
import shutil
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QTreeWidget, QTreeWidgetItem, QTabWidget, QMessageBox, 
    QWidget, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QScrollArea, QProgressBar, QStatusBar, QSizePolicy, QPlainTextEdit, 
    QSplitter, QTextBrowser, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread
from PyQt5.QtGui import QPixmap, QIcon, QDesktopServices, QTextOption, QFont

from graph_generator_assistant.modules.lib_data    import data, SYSTEM_DATA, SYSTEM_QUESTION
from graph_generator_assistant.modules.lib_execute import generate_data, save_data
from graph_generator_assistant.modules.lib_files   import open_from_filepath
from graph_generator_assistant.modules.lib_funcs   import consultation_in_depth, extrair_codigo_puro
from graph_generator_assistant.modules.lib_about   import show_about_window
from graph_generator_assistant.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu
import graph_generator_assistant.about as about

program_dir_path = os.path.dirname(os.path.abspath(__file__))

WORKING={"img_path":"", "mod_path":"", "data":""}

CONFIG_FILE = "~/.config/graph_generator_assistant/config_data.json"
config_data = SYSTEM_DATA
config_file_path = os.path.expanduser(CONFIG_FILE)


class WorkerThread(QThread):
    def __init__(self, module_name, config_data, sys_msg, user_msg):
        super().__init__()  # Chama o construtor da classe pai (QThread)
        self.module_name = module_name
        self.config_data = config_data 
        self.sys_msg = sys_msg
        self.user_msg = user_msg
        self.out = ""
        
    def run(self):
        self.out = consultation_in_depth(self.config_data, 
                                    self.sys_msg, 
                                    self.user_msg)


class MainWindow(QMainWindow):
    #############################
    def __init__(self):
        
        super().__init__()
        self.setWindowTitle(about.__program_name__)
        self.setGeometry(100, 100, 800, 600)
        
        self.rodando = False
        self.contador = 0
        
        ## Icon
        # Get base directory for icons
        self.base_dir_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(self.base_dir_path, 'icons', 'logo.png')
        self.setWindowIcon(QIcon(icon_path)) 
        
        ## toolbar
        self.toolbar = QToolBar("Toolbar")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)
        
        webpal_action = QAction("Web palletes", self)
        webpal_action.setIcon(QIcon.fromTheme("emblem-web"))
        webpal_action.triggered.connect(self.open_url_webpal)
        self.toolbar.addAction(webpal_action)
        
        colpick_action = QAction("Color picker", self)
        colpick_path = os.path.join(self.base_dir_path, 'icons', 'color_picker.png')
        colpick_action.setIcon(QIcon(colpick_path))
        colpick_action.triggered.connect(self.open_color_picker)
        self.toolbar.addAction(colpick_action)
        
        # Adicionar o espaçador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        

        configure_action = QAction("Configure AI", self)
        configure_action.setIcon(QIcon.fromTheme("applications-accessories"))
        configure_action.triggered.connect(lambda: open_from_filepath(config_file_path))
        self.toolbar.addAction(configure_action)
        
        coffee_action = QAction("Coffee", self)
        coffee_action.setIcon(QIcon.fromTheme("emblem-favorite"))
        coffee_action.triggered.connect(self.buy_me_a_coffee)
        self.toolbar.addAction(coffee_action)
        
        about_action = QAction("About", self)
        about_action.setIcon(QIcon.fromTheme("help-about"))
        about_action.triggered.connect(self.show_about)
        self.toolbar.addAction(about_action)
        


        ## treeview
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.populate_tree(self.tree, data)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        
        ## Tabwidget
        self.tabs = QTabWidget()
        self.create_grid_tabs()
        self.create_details_tabs()
        
        self.splitter = QSplitter()
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.tabs)
        self.splitter.setSizes([200, 600])
        
        ## progress
        self.progress_bar = QProgressBar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(self.progress_bar)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.load_config_data_from_json()

    #############################
    def show_about(self):     
        data = {
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        
        logo_path = os.path.join(self.base_dir_path, 'icons', 'logo.png')
        
        show_about_window(data,logo_path)
           
    #############################
    def open_url_webpal(self):
        self.status_bar.showMessage("Opening Pinterest")
        QDesktopServices.openUrl(QUrl("https://pinterest.com/search/pins/?q=color palette design colour schemes"))

    #############################
    def open_color_picker(self):    
        subprocess.Popen([sys.executable, os.path.join(self.base_dir_path,"color_picker.py")])
    #############################
    def load_config_data_from_json(self):
        global config_data
        try:
            if not os.path.exists(config_file_path):
                os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
                
                with open(config_file_path, "w", encoding="utf-8") as arquivo:
                    json.dump(config_data, arquivo, indent=4)
                    self.status_bar.showMessage(f"File created in: {config_file_path}")
            else:
                with open(config_file_path, "r") as arquivo:
                    config_data = json.load(arquivo)
            
        except FileNotFoundError:
            self.status_bar.showMessage(f"Error: File '{config_file_path}' was not found.")
            
        except json.JSONDecodeError:
            self.status_bar.showMessage(f"Error: File '{config_file_path}' dont have a valid json.")
    #############################
    def buy_me_a_coffee(self):
        self.status_bar.showMessage("Buy me a coffee in https://ko-fi.com/trucomanx")
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))
    #############################
    def populate_tree(self, parent, data):
        for key, value in data.items():
            item = QTreeWidgetItem([key])
            parent.addTopLevelItem(item) if isinstance(parent, QTreeWidget) else parent.addChild(item)
            if isinstance(value, dict):
                self.populate_tree(item, value)
            elif isinstance(value, list):
                for leaf in value:
                    item.addChild(QTreeWidgetItem([leaf]))
    
    #############################
    def on_tree_item_clicked(self, item):
        self.tabs.setCurrentIndex(0)
        leaves = []
        self.collect_leaves(item, leaves)
        
        images = []
        for val in leaves:
            png_path = os.path.join(program_dir_path,"templates",val+".png")
            if os.path.exists(png_path):
                images.append(png_path)
                #print(png_path)
        self.add_images_to_grid(images)

    #############################
    def collect_leaves(self, item, leaves):
        if item.childCount() == 0:
            leaves.append(item.text(0))
        else:
            for i in range(item.childCount()):
                self.collect_leaves(item.child(i), leaves)

    #############################
    def create_grid_tabs(self):
        self.image_tab = QWidget()
        self.grid_layout = QGridLayout(self.image_tab)  # Layout definido diretamente no widget
        self.tabs.addTab(self.image_tab, "Images")

    #############################
    def set_image_in_detais_tab(self, img_path):      
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            L = self.details_splitter.sizes()
            
            height = L[0]-8
            width = self.details_splitter.width()-8

            self.large_image.setPixmap(pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    #############################
    def add_images_to_grid(self, images):
        
        L = self.grid_layout.count()
        self.progress_bar.setRange(0,L)
        # Limpa widgets antigos
        for i in reversed(range(L)):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
            self.progress_bar.setValue(i)
        
        self.status_bar.showMessage("Deleted old images widgets", msecs=3000) 
        
        # Adiciona novas imagens
        self.progress_bar.setRange(0,len(images))
        for idx, img in enumerate(images):
            pixmap = QPixmap(img)
            label = QLabel()
            label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.mouseDoubleClickEvent = lambda event, img=img: self.image_grid_clicked(img)
            
            json_path = os.path.splitext(img)[0]+".json"
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    label.setToolTip(data.get("title","")) 
            
            self.grid_layout.addWidget(label, idx // 3, idx % 3)
            self.progress_bar.setValue(idx)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage(f"Load {len(images)} image widgets", msecs=5000) 
    
    #############################
    def image_grid_clicked(self,img_path):
        global WORKING
        
        WORKING["img_path"] = img_path
        WORKING["mod_path"] = os.path.splitext(img_path)[0]+".py"
        WORKING["data"] = {}
        
        json_path = os.path.splitext(img_path)[0]+".json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                WORKING["data"] = json.load(f)
                self.markdown_widget.setMarkdown(WORKING["data"]["description"])

        
        self.set_image_in_detais_tab( WORKING["img_path"])
        self.tabs.setCurrentIndex(1)
        
            
    #############################
    def start_timer(self, pos, index):
        """Reinicia o temporizador para evitar chamadas múltiplas enquanto o usuário arrasta."""
        self.timer.start(200) 
        
    def resizeEvent(self, event):
        """Detecta qualquer mudança no tamanho da janela, incluindo o splitter."""
        self.timer.start(200)  # Aguarda 200ms após o último evento de resize
        super().resizeEvent(event) 

    def on_splitter_stopped(self):
        """Executa a ação quando o usuário para de mover o splitter."""
        #print(f"Novos tamanhos: {self.splitter.sizes()}")
        self.set_image_in_detais_tab( WORKING["img_path"])

    ############################# 
    def on_download_img_click(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Arquivo Gráfico",
            None,  # Começa no diretório 
            "PNG Image (*.png);;"
            "JPEG Image (*.jpg *.jpeg);;"
            "EPS Vector (*.eps);;"
            "PDF Document (*.pdf);;"
            "SVG Vector (*.svg);;"
            "PostScript (*.ps);;"
            "Todos os Arquivos (*)",
            options=QFileDialog.Options()
        )
        
        if file_path:
            extension = os.path.splitext(file_path)[1]
            print(extension)
            if extension.lower() in [   ".png", ".jpg", ".jpeg", 
                                        ".eps", ".pdf", ".svg", ".ps"]:
                self.text_output.clear()  # Limpa todo o conteúdo
                generate_data(self,WORKING["mod_path"], file_path)

    #############################    
    def on_download_code_click(self):
        if os.path.exists(WORKING["mod_path"]):
            
            directory = QFileDialog.getExistingDirectory(   self, 
                                                            "Select a diretory")
            
            if directory:
                basename = os.path.basename(WORKING["mod_path"])
                out_path = os.path.join(directory,basename)
                
                shutil.copy(WORKING["mod_path"], out_path)
                
    def on_consult_btn_click(self):
        global WORKING
        
        self.consult_btn.setEnabled(False)
        
        if config_data["api_key"]=="":
            open_from_filepath(config_file_path)
        else:
            module_src_dir  = os.path.dirname(WORKING["mod_path"])    
            module_name     = os.path.splitext(os.path.basename(WORKING["mod_path"]))[0]
            sys_msg = SYSTEM_QUESTION["principal_task"].replace("CUSTOMFUNC",module_name)
            
            with open(WORKING["mod_path"], "r", encoding="utf-8") as f:
                conteudo = f.read()
            
            sys_msg  = sys_msg.replace("BASECODE",conteudo)
            user_msg = self.text_edit.toPlainText()
            
            #print("please wait...")
            #if self.rodando:
            #    return
            
            self.thread = WorkerThread(module_name,config_data, sys_msg, user_msg)
            self.thread.finished.connect(self.funcao_finalizou)
            self.thread.start()
            
            self.rodando = True
            self.startTimer(500)  # Atualiza a cada 500ms

    #############################
    def funcao_finalizou(self):
        res = save_data(self,self.thread.module_name, self.thread.out)
        
        #open_from_filepath(res[0])
        #open_from_filepath(res[1])
        
        WORKING["mod_path"] = res[0]
        WORKING["img_path"] = res[1]
        self.set_image_in_detais_tab( res[1])
        
        self.consult_btn.setEnabled(True)
        self.rodando = False
        self.contador = 0
        self.progress_bar.setValue(0)
        QMessageBox.information(self, "Information","Finished work")
    
    #############################
    def timerEvent(self, event):
        if self.rodando:
            pontos = '.' * (self.contador % 32)
            self.status_bar.showMessage(f"Working{pontos}",1000)

            if self.contador%2 == 0:
                self.progress_bar.setValue(self.progress_bar.maximum())
            else:
                self.progress_bar.setValue(0)
            
            self.contador += 1    
    #############################
    def create_details_tabs(self):
        """
        Cria a aba de detalhes com:
        - Área de visualização de imagem grande
        - Seção de consulta com texto editável
        - Visualizador de Markdown
        - Botões de ação
        """
        
        ##############################################
        # 1. Configuração do Widget principal e layout
        ##############################################
        self.detail_tab = QWidget()
        detail_layout = QVBoxLayout()
        #detail_layout.setContentsMargins(5, 5, 5, 5)  # Margens uniformes
        #detail_layout.setSpacing(10)  # Espaço entre widgets
        
        
        ##############################################
        # 2. Área de visualização da imagem (com scroll)
        ##############################################
        scroll_area = QScrollArea()
        self.large_image = QLabel("Large Image Here")
        self.large_image.setAlignment(Qt.AlignCenter)
        
        # Configuração do scroll area
        scroll_area.setWidget(self.large_image)
        scroll_area.setWidgetResizable(True)
        #scroll_area.setMinimumHeight(200)  # Altura mínima garantida
        
        ##############################################
        # 3. Seção de consulta (container_layout_widget)
        ##############################################
        container_layout_widget = QWidget()
        consult_layout = QHBoxLayout()
        consult_layout.setContentsMargins(0, 0, 0, 0)
        consult_layout.setSpacing(0)
        #

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Write your order for the AI assistant...")
        
        self.consult_btn = QPushButton("Consult")
        self.consult_btn.setIcon(QIcon.fromTheme("applications-internet"))
        self.consult_btn.setFixedWidth(100)
        self.consult_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.consult_btn.clicked.connect(self.on_consult_btn_click)

        consult_layout.addWidget(self.text_edit)
        consult_layout.addWidget(self.consult_btn)
        container_layout_widget.setLayout(consult_layout) 
        
        ##############################################
        # 4. Visualizador Markdown (markdown_widget)
        ##############################################
        self.markdown_widget = QTextBrowser()
        self.markdown_widget.setMarkdown("")
        self.markdown_widget.setMinimumHeight(50)

        ##############################################
        # 5. Configuração do Splitter (details_splitter)
        ##############################################
        self.details_splitter = QSplitter(Qt.Vertical)
        self.details_splitter.addWidget(scroll_area)
        self.details_splitter.addWidget(container_layout_widget)
        self.details_splitter.addWidget(self.markdown_widget)
        self.details_splitter.setSizes([400, 150, 150])

        # Temporizador (timer)
        self.timer = QTimer()
        self.timer.setSingleShot(True)  # Garante que o timer dispare apenas uma vez
        self.timer.timeout.connect(self.on_splitter_stopped)
        self.details_splitter.splitterMoved.connect(self.start_timer)

        detail_layout.addWidget(self.details_splitter)

        ##############################################
        # 6. Área de botões (button_layout)
        ##############################################
        output_layout = QHBoxLayout()
        self.text_output = QPlainTextEdit()
        self.text_output.setReadOnly(True)  # Somente leitura
        self.text_output.setWordWrapMode(QTextOption.NoWrap)  # Sem quebra de linha
        self.text_output.setUndoRedoEnabled(False)  # Desabilitar undo/redo
        self.text_output.setStyleSheet("""
            QPlainTextEdit {
                background-color: black;
                color: white;
            }
        """)
        self.text_output.setSizePolicy(
            QSizePolicy.Expanding,  # Horizontal - pode crescer se necessário
            QSizePolicy.Fixed   # Vertical - pode crescer se necessário
        )
        self.text_output.setMinimumSize(0, 0)
        font = QFont()
        font.setFamily("Courier New")  # Ou "Monospace", "Consolas", etc.
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.text_output.setFont(font)
        output_layout.addWidget(self.text_output)
        
        button_layout = QVBoxLayout()
        #button_layout.setSpacing(8)
        output_label = QLabel("<b>: Output</b>")

        self.refresh_img_btn = QPushButton("Refresh Image")
        self.refresh_img_btn.clicked.connect(self.on_refresh_img_click)
        self.refresh_img_btn.setIcon(QIcon.fromTheme("view-refresh"))

        self.download_img_btn = QPushButton("Download Image")
        self.download_img_btn.clicked.connect(self.on_download_img_click)
        self.download_img_btn.setIcon(QIcon.fromTheme("document-save"))
        
        self.download_code_btn = QPushButton("Download Code")
        self.download_code_btn.clicked.connect(self.on_download_code_click)
        self.download_code_btn.setIcon(QIcon.fromTheme("document-save"))
        

        button_layout.addWidget(output_label)
        button_layout.addWidget(self.refresh_img_btn)
        button_layout.addWidget(self.download_img_btn)
        button_layout.addWidget(self.download_code_btn)
        
        button_height = sum([
            output_label.sizeHint().height(),
            self.refresh_img_btn.sizeHint().height(),
            self.download_img_btn.sizeHint().height(),
            self.download_code_btn.sizeHint().height(),
            5 * 2  # Margem para spacing (5px entre cada elemento)
        ])
        self.text_output.setFixedHeight(button_height)  # Altura FIXA em pixels
        
        output_layout.addLayout(button_layout)
        detail_layout.addLayout(output_layout)

        ##############################################
        # 7. Finalização
        ##############################################
        self.detail_tab.setLayout(detail_layout)
        self.tabs.addTab(self.detail_tab, "Task")
    
    def on_refresh_img_click(self):
        if WORKING["mod_path"]!="" and WORKING["img_path"]!="":
            self.text_output.clear()  # Limpa todo o conteúdo
            generate_data(self,WORKING["mod_path"], WORKING["img_path"])
            self.set_image_in_detais_tab(WORKING["img_path"])
    
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
    app.setApplicationName(about.__package__) # xprop WM_CLASS # *.desktop -> StartupWMClass
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
