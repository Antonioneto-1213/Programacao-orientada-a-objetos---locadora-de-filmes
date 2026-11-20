import sys
import os
import time
import requests

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QToolBar,
    QStatusBar,
    QFrame,
    QScrollArea,
    QInputDialog
)

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QAction, QPixmap

# Endereço base da sua API
API_URL = "http://127.0.0.1:8000"


class JanelaCliente(QDialog):
    cliente_cadastrado = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Cliente")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        titulo = QLabel("CADASTRO DE CLIENTE")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
        """)
        layout.addWidget(titulo)
        formulario = QFormLayout()
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome completo")
        self.telefone = QLineEdit()
        self.telefone.setPlaceholderText("(00) 00000-0000")
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@email.com")
        formulario.addRow("Nome:", self.nome)
        formulario.addRow("Telefone:", self.telefone)
        formulario.addRow("E-mail:", self.email)
        layout.addLayout(formulario)
        botoes = QHBoxLayout()
        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")
        btn_salvar.clicked.connect(self.salvar)
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_salvar)
        botoes.addWidget(btn_cancelar)
        layout.addLayout(botoes)
        self.setLayout(layout)

    def salvar(self):
        nome = self.nome.text().strip()
        telefone = self.telefone.text().strip()
        email = self.email.text().strip()
        if not nome:
            QMessageBox.warning(self, "Atenção", "Digite o nome do cliente.")
            return
        self.cliente_cadastrado.emit(nome, telefone, email)
        self.accept()


class JanelaFilme(QDialog):
    filme_cadastrado = Signal(str, str, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastro de Filme")
        self.setFixedSize(450, 350)
        layout = QVBoxLayout()
        titulo = QLabel("CADASTRO DE FILME")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
        """)
        layout.addWidget(titulo)
        formulario = QFormLayout()
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome do filme")
        self.genero = QComboBox()
        self.genero.addItems([
            "Ação", "Aventura", "Comédia", "Drama", 
            "Ficção Científica", "Terror", "Romance", 
            "Animação", "Suspense"
        ])
        self.ano = QSpinBox()
        self.ano.setRange(1900, 2100)
        self.ano.setValue(2026)
        self.capa = QLineEdit()
        self.capa.setPlaceholderText("Exemplo: interestelar.jpg")
        formulario.addRow("Nome:", self.nome)
        formulario.addRow("Gênero:", self.genero)
        formulario.addRow("Ano:", self.ano)
        formulario.addRow("Capa:", self.capa)
        layout.addLayout(formulario)
        aviso = QLabel("A imagem deve estar dentro da pasta 'capas'.")
        aviso.setStyleSheet("color: #aaaaaa; padding: 5px;")
        layout.addWidget(aviso)
        botoes = QHBoxLayout()
        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")
        btn_salvar.clicked.connect(self.salvar)
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_salvar)
        botoes.addWidget(btn_cancelar)
        layout.addLayout(botoes)
        self.setLayout(layout)

    def salvar(self):
        nome = self.nome.text().strip()
        genero = self.genero.currentText()
        ano = self.ano.value()
        capa = self.capa.text().strip()
        if not nome:
            QMessageBox.warning(self, "Atenção", "Digite o nome do filme.")
            return
        self.filme_cadastrado.emit(nome, genero, ano, capa)
        self.accept()


class Locadora(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes")
        self.showMaximized()

        self.filmes = []
        self.clientes = []

        self.setStyleSheet("""
            QMainWindow { background-color: #0b1120; }
            QWidget { background-color: #0b1120; color: white; font-family: Arial; }
            QLabel { color: white; }
            QLineEdit, QComboBox, QSpinBox { background-color: #131a2c; color: white; border: 1px solid #2b3a5c; border-radius: 6px; padding: 8px; }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #3b82f6; }
            QPushButton { background-color: #1e3a8a; color: white; border: 1px solid #2563eb; border-radius: 6px; padding: 8px 12px; }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton:pressed { background-color: #0d1526; }
            QTableWidget { background-color: #101827; color: white; }
            QMenuBar { background-color: #0d1526; color: white; }
            QMenuBar::item:selected { background-color: #2563eb; }
            QMenu { background-color: #0f172a; color: white; border: 1px solid #2b3a5c; }
            QMenu::item:selected { background-color: #2563eb; }
            QToolBar { background-color: #0d1526; border-bottom: 1px solid #2b3a5c; spacing: 5px; padding: 5px; }
            QStatusBar { background-color: #0d1526; color: #93b4e0; }
            QScrollArea { border: none; background-color: #0b1120; }
            QScrollBar:vertical { background: #0d1526; width: 12px; }
            QScrollBar::handle:vertical { background: #2b3a5c; border-radius: 6px; }
        """)

        self.criar_menu()
        self.criar_toolbar()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Conectando ao banco de dados...")

        widget_principal = QWidget()
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(25, 20, 25, 20)

        cabecalho = QHBoxLayout()
        titulo = QLabel("LOCADORA DE FILMES")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold;")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        self.btn_cadastro_filme = QPushButton("+ Cadastrar filme")
        self.btn_cadastro_filme.clicked.connect(self.abrir_filme)
        cabecalho.addWidget(self.btn_cadastro_filme)

        self.btn_cadastro_cliente = QPushButton("+ Cadastrar cliente")
        self.btn_cadastro_cliente.clicked.connect(self.abrir_cliente)
        cabecalho.addWidget(self.btn_cadastro_cliente)

        layout_principal.addLayout(cabecalho)

        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar por nome ou gênero...")
        self.pesquisa.textChanged.connect(self.atualizar_interface)
        layout_principal.addWidget(self.pesquisa)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.area_filmes = QWidget()
        self.grid_filmes = QGridLayout()
        self.grid_filmes.setSpacing(20)
        self.area_filmes.setLayout(self.grid_filmes)
        self.scroll.setWidget(self.area_filmes)
        layout_principal.addWidget(self.scroll)

        widget_principal.setLayout(layout_principal)
        self.setCentralWidget(widget_principal)
        
        # Carrega os dados da API ao iniciar
        self.carregar_dados_api()

    def carregar_dados_api(self):
        try:
            res_filmes = requests.get(f"{API_URL}/filmes")
            res_clientes = requests.get(f"{API_URL}/clientes")
            
            if res_filmes.status_code == 200:
                self.filmes = res_filmes.json()
            if res_clientes.status_code == 200:
                self.clientes = res_clientes.json()
                
            self.statusBar.showMessage("Conectado à API com sucesso!", 5000)
            self.atualizar_interface()
            
        except requests.exceptions.ConnectionError:
            self.statusBar.showMessage("Erro: Não foi possível conectar à API. Verifique se o servidor está rodando.")
            QMessageBox.critical(self, "Erro de Conexão", "O servidor da API não está rodando.\n\nPor favor, inicie o Uvicorn no terminal.")

    def criar_menu(self):
        menu = self.menuBar()
        menu_filmes = menu.addMenu("Filmes")
        novo_filme = QAction("Cadastrar filme", self)
        novo_filme.triggered.connect(self.abrir_filme)
        menu_filmes.addAction(novo_filme)
        remover_filme = QAction("Remover filme", self)
        remover_filme.triggered.connect(self.selecionar_filme_remover)
        menu_filmes.addAction(remover_filme)
        menu_filmes.addSeparator()
        devolver = QAction("Devolver filme", self)
        devolver.triggered.connect(self.devolver_filme)
        menu_filmes.addAction(devolver)
        
        menu_clientes = menu.addMenu("Clientes")
        novo_cliente = QAction("Cadastrar cliente", self)
        novo_cliente.triggered.connect(self.abrir_cliente)
        menu_clientes.addAction(novo_cliente)
        
        menu_sistema = menu.addMenu("Sistema")
        sair = QAction("Sair", self)
        sair.triggered.connect(self.close)
        menu_sistema.addAction(sair)
        
        menu_ajuda = menu.addMenu("Ajuda")
        sobre = QAction("Sobre", self)
        sobre.triggered.connect(self.sobre)
        menu_ajuda.addAction(sobre)

    def criar_toolbar(self):
        toolbar = QToolBar("Barra de ferramentas")
        self.addToolBar(toolbar)
        novo_aluguel = QAction("Novo aluguel", self)
        novo_aluguel.triggered.connect(self.novo_aluguel)
        toolbar.addAction(novo_aluguel)
        novo_filme = QAction("Novo filme", self)
        novo_filme.triggered.connect(self.abrir_filme)
        toolbar.addAction(novo_filme)
        novo_cliente = QAction("Novo cliente", self)
        novo_cliente.triggered.connect(self.abrir_cliente)
        toolbar.addAction(novo_cliente)
        remover = QAction("Remover filme", self)
        remover.triggered.connect(self.selecionar_filme_remover)
        toolbar.addAction(remover)
        devolver = QAction("Devolver", self)
        devolver.triggered.connect(self.devolver_filme)
        toolbar.addAction(devolver)

    def atualizar_interface(self):
        while self.grid_filmes.count():
            item = self.grid_filmes.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        texto = self.pesquisa.text().strip().casefold()
        filmes_filtrados = []
        for filme in self.filmes:
            nome = filme["nome"].casefold()
            genero = filme["genero"].casefold()
            if texto in nome or texto in genero:
                filmes_filtrados.append(filme)
        colunas = 5
        for indice, filme in enumerate(filmes_filtrados):
            linha = indice // colunas
            coluna = indice % colunas
            card = self.criar_card(filme)
            self.grid_filmes.addWidget(card, linha, coluna)
        self.grid_filmes.setRowStretch(len(filmes_filtrados) // colunas + 1, 1)

    def criar_card(self, filme):
        card = QFrame()
        card.setFixedWidth(220)
        card.setStyleSheet("QFrame { background-color: #101827; border: 1px solid #2563eb; border-radius: 10px; }")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        capa = QLabel()
        capa.setFixedSize(198, 260)
        capa.setAlignment(Qt.AlignCenter)
        caminho = os.path.join("capas", filme["capa"])
        if os.path.exists(caminho):
            pixmap = QPixmap(caminho)
            pixmap = pixmap.scaled(198, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            capa.setPixmap(pixmap)
        else:
            capa.setText("CAPA\n\n" + filme["nome"])
            capa.setStyleSheet("background-color: #1e3a8a; color: #bfdbfe; border-radius: 5px; font-size: 16px; font-weight: bold;")
        layout.addWidget(capa)
        nome = QLabel(filme["nome"])
        nome.setAlignment(Qt.AlignCenter)
        nome.setWordWrap(True)
        nome.setStyleSheet("font-size: 17px; font-weight: bold; padding-top: 8px;")
        layout.addWidget(nome)
        informacoes = QLabel(f"{filme['genero']} • {filme['ano']}")
        informacoes.setAlignment(Qt.AlignCenter)
        informacoes.setStyleSheet("color: #7ea3d1; padding: 3px;")
        layout.addWidget(informacoes)
        status = QLabel(filme["status"])
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #93c5fd; font-weight: bold; padding: 4px;")
        layout.addWidget(status)
        botoes = QHBoxLayout()
        btn_alugar = QPushButton("Alugar")
        btn_alugar.clicked.connect(lambda checked=False, codigo=filme["codigo"]: self.alugar_filme(codigo))
        botoes.addWidget(btn_alugar)
        btn_remover = QPushButton("Remover")
        btn_remover.clicked.connect(lambda checked=False, codigo=filme["codigo"]: self.remover_filme(codigo))
        botoes.addWidget(btn_remover)
        layout.addLayout(botoes)
        card.setLayout(layout)
        return card

    def alugar_filme(self, codigo):
        filme = next((f for f in self.filmes if f["codigo"] == codigo), None)
        if filme is None: return
        if filme["status"] == "Alugado":
            QMessageBox.warning(self, "Filme indisponível", "Esse filme já está alugado.")
            return
        if not self.clientes:
            QMessageBox.warning(self, "Nenhum cliente", "Cadastre um cliente antes de realizar um aluguel.")
            return
        nomes = [cliente["nome"] for cliente in self.clientes]
        cliente, ok = QInputDialog.getItem(self, "Alugar filme", "Selecione o cliente:", nomes, 0, False)
        if not ok: return
        dias, ok = QInputDialog.getInt(self, "Período do aluguel", "Quantidade de dias:", 3, 1, 30)
        if not ok: return
        
        # Envia a atualização para a API
        try:
            res = requests.put(f"{API_URL}/filmes/{codigo}?status=Alugado")
            if res.status_code == 200:
                filme["status"] = "Alugado"
                self.atualizar_interface()
                self.statusBar.showMessage(f"{filme['nome']} alugado para {cliente} por {dias} dias.")
                QMessageBox.information(self, "Aluguel realizado", f"Filme: {filme['nome']}\nCliente: {cliente}\nPrazo: {dias} dias")
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível alugar o filme no servidor.")
        except Exception as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Falha ao comunicar com a API: {e}")

    def remover_filme(self, codigo):
        filme = next((f for f in self.filmes if f["codigo"] == codigo), None)
        if filme is None: return
        resposta = QMessageBox.question(self, "Remover filme", f"Tem certeza que deseja remover o filme:\n\n{filme['nome']}?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resposta == QMessageBox.Yes:
            try:
                res = requests.delete(f"{API_URL}/filmes/{codigo}")
                if res.status_code == 200:
                    nome_filme = filme["nome"]
                    self.filmes.remove(filme)
                    self.atualizar_interface()
                    self.statusBar.showMessage(f"Filme '{nome_filme}' removido.")
                    QMessageBox.information(self, "Filme removido", f"O filme '{nome_filme}' foi removido com sucesso.")
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível remover o filme no servidor.")
            except Exception as e:
                QMessageBox.critical(self, "Erro de Conexão", f"Falha ao comunicar com a API: {e}")

    def selecionar_filme_remover(self):
        if not self.filmes:
            QMessageBox.information(self, "Remover filme", "Não existem filmes cadastrados.")
            return
        nomes = [filme["nome"] for filme in self.filmes]
        nome, ok = QInputDialog.getItem(self, "Remover filme", "Selecione o filme:", nomes, 0, False)
        if not ok: return
        filme = next((f for f in self.filmes if f["nome"] == nome), None)
        if filme:
            self.remover_filme(filme["codigo"])

    def devolver_filme(self):
        alugados = [filme for filme in self.filmes if filme["status"] == "Alugado"]
        if not alugados:
            QMessageBox.information(self, "Devolução", "Não existem filmes alugados.")
            return
        nomes = [filme["nome"] for filme in alugados]
        nome, ok = QInputDialog.getItem(self, "Devolver filme", "Selecione o filme:", nomes, 0, False)
        if not ok: return
        
        filme_alvo = next((f for f in alugados if f["nome"] == nome), None)
        if filme_alvo:
            try:
                res = requests.put(f"{API_URL}/filmes/{filme_alvo['codigo']}?status=Disponível")
                if res.status_code == 200:
                    filme_alvo["status"] = "Disponível"
                    self.atualizar_interface()
                    self.statusBar.showMessage(f"{nome} devolvido com sucesso.")
                    QMessageBox.information(self, "Devolução realizada", f"O filme '{nome}' está disponível novamente.")
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível devolver o filme no servidor.")
            except Exception as e:
                QMessageBox.critical(self, "Erro de Conexão", f"Falha ao comunicar com a API: {e}")

    def abrir_cliente(self):
        janela = JanelaCliente(self)
        janela.cliente_cadastrado.connect(self.adicionar_cliente)
        janela.exec()

    def adicionar_cliente(self, nome, telefone, email):
        novo_cliente = {"nome": nome, "telefone": telefone, "email": email}
        try:
            res = requests.post(f"{API_URL}/clientes", json=novo_cliente)
            if res.status_code == 200:
                self.clientes.append(novo_cliente)
                QMessageBox.information(self, "Cliente cadastrado", f"Cliente '{nome}' cadastrado com sucesso.")
                self.statusBar.showMessage(f"Cliente '{nome}' cadastrado.")
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível cadastrar o cliente no servidor.")
        except Exception as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Falha ao comunicar com a API: {e}")

    def abrir_filme(self):
        janela = JanelaFilme(self)
        janela.filme_cadastrado.connect(self.adicionar_filme)
        janela.exec()

    def adicionar_filme(self, nome, genero, ano, capa):
        novo_filme = {
            "nome": nome,
            "genero": genero,
            "ano": ano,
            "capa": capa,
            "status": "Disponível"
        }
        try:
            res = requests.post(f"{API_URL}/filmes", json=novo_filme)
            if res.status_code == 200:
                filme_salvo = res.json()
                self.filmes.append(filme_salvo)
                self.atualizar_interface()
                self.statusBar.showMessage(f"Filme '{nome}' cadastrado.")
                QMessageBox.information(self, "Filme cadastrado", f"O filme '{nome}' foi cadastrado com sucesso.")
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível cadastrar o filme no servidor.")
        except Exception as e:
             QMessageBox.critical(self, "Erro de Conexão", f"Falha ao comunicar com a API: {e}")

    def novo_aluguel(self):
        disponiveis = [filme for filme in self.filmes if filme["status"] == "Disponível"]
        if not disponiveis:
            QMessageBox.information(self, "Novo aluguel", "Não existem filmes disponíveis.")
            return
        nomes = [filme["nome"] for filme in disponiveis]
        nome, ok = QInputDialog.getItem(self, "Novo aluguel", "Selecione o filme:", nomes, 0, False)
        if not ok: return
        filme = next((f for f in disponiveis if f["nome"] == nome), None)
        if filme:
            self.alugar_filme(filme["codigo"])

    def sobre(self):
        QMessageBox.information(self, "Sobre", "LOCADORA DE FILMES (Versão API)\n\nSistema desenvolvido em Python com PySide6 e FastAPI.\n\nAgora conectado a um banco de dados SQLite real via API!")

    def closeEvent(self, event):
        resposta = QMessageBox.question(self, "Sair", "Deseja realmente sair da locadora?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resposta == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = Locadora()
    janela.show()
    sys.exit(app.exec())