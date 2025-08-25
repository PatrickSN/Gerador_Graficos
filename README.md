#  Grafitics: estatística personalizada em gráficos

![Status do Projeto](https://img.shields.io/badge/status-beta-yellow) ![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

Aplicação desktop em Python para carregar planilhas, gerar gráficos interativos e exportar imagens — GUI moderna com **CustomTkinter** e empacotável para Windows via **PyInstaller**.

---

## 🔍 Destaques

- Interface elegante com **CustomTkinter**  
- Leitura de `.xlsx` com **pandas / openpyxl**  
- Gráficos com **matplotlib** e **seaborn**  
- Módulo de estatísticas com **statsmodels**, **scipy** e **networkx**  
- Empacotamento Windows (`.exe`) usando **PyInstaller**

---

## 📁 Estrutura do projeto

```
├── app.py               # Script principal que inicializa a GUI
├── gui/
│   ├── main_window.py   # Janela principal e construção da interface
│   ├── widgets.py       # Componentes reutilizáveis
│   └── estatistica.py   # Funções de análise/estatística
├── requirements.txt     # Dependências
├── build.bat            # Script Windows para gerar o executável
└── README.md            # Este arquivo
```

---

## ⚙️ Instalação (Desenvolvimento)

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

2. Crie e ative um ambiente virtual (Windows):
```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Instale dependências:
```bash
pip install -r requirements.txt
```

4. Execute em modo desenvolvimento:
```bash
python app.py
```

Se tudo estiver funcionando, gere o executável com:
```bash
build.bat
```
O `.exe` será criado em `dist\Gerador_Graficos.exe`.

---

## 🧩 Gerar o executável (Windows)

No Windows, use o `build.bat` fornecido (ou execute manualmente o PyInstaller):

```powershell
# ativar venv (se ainda não estiver)
.venv\Scripts\activate

# gerar exe (exemplo)
pyinstaller --onefile --windowed --name Gerador_Graficos --add-data "gui;gui" app.py
```

O `.exe` resultante ficará em `dist\Gerador_Graficos.exe`.

---

## 📝 Uso Rápido (Usuário Final)

1. Abra o aplicativo (`app.py` ou `.exe`).  
2. Carregue sua planilha `.xlsx`.  
3. Escolha o tipo de gráfico e clique em **Gerar**.  
4. Salve o resultado como PNG pelo botão de exportação.

---

## 🛠️ Dicas de Debug (se o exe fechar instantaneamente)

- Gere o exe com console removendo `--windowed` para ver tracebacks.  
- Teste `python app.py` e corrija todos os erros antes de empacotar.  
- Use `--hidden-import` no PyInstaller se faltar algum import detectado apenas em runtime.

---

## 📄 Licença

Projeto sob licença **MIT**. Veja `LICENSE` para detalhes.

---

## ✉️ Contato

**Lucas Nicácio** — lucas.nicacio@ufv.br
GitHub: https://github.com/PatrickSN
---
