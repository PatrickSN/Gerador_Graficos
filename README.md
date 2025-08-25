#  Grafitics: estatística personalizada em gráficos

Uma aplicação gráfica leve em Python que permite carregar dados, gerar gráficos e exportar resultados — com uma interface clean e intuitiva!

---

##  Destaques

-  Interface gráfica com **CustomTkinter**: moderna e personalizável.  
-  Suporta **.xlsx** como entrada, sem complicações.  
-  Geração de gráficos com **Matplotlib** + **Seaborn** para visualização elegante.  
-  Estatísticas avançadas com **Pandas**, **Scipy**, **Statsmodels** e **NetworkX**.  
-  Empacotável como `.exe` usando **PyInstaller** — ideal para distribuir em Windows.

---

##  Visão Geral

Este aplicativo nasce da necessidade de transformar dados em insights visuais rápidos, sem sair da praticidade de uma GUI. Com poucos cliques você:

1. Carrega uma planilha `.xlsx`.  
2. Visualiza o gráfico desejado.  
3. Salva a imagem em PNG.  
4. Se quiser mais, dispõe de estatísticas descritivas e análises mais sofisticadas.

---

##  Estrutura de Arquivos do Projeto

├── app.py # Script principal — inicia a GUI
├── gui/
│ ├── main_window.py # Janela principal e lógica da interface
│ ├── widgets.py # Componentes reutilizáveis (botões, controles)
│ └── estatistica.py # Módulo de análises e estatísticas
├── requirements.txt # Dependências do projeto
├── build.bat # Script Windows para gerar o executável
└── README.md # Este arquivo

##  Instalação e Execução (Para Desenvolvedores)

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo
   
2. Crie e ative um ambiente virtual:

    python -m venv .venv
    .venv\Scripts\activate

3. Instale as dependências:

    pip install -r requirements.txt

4. Teste localmente:

    python app.py