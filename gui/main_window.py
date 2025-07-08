import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

from tkinter import filedialog, ttk
from tkinter import messagebox
from tkinter import StringVar
from tkinter import TclError

from gui.widgets import *
from gui.estatistica import *


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Análise de Dados com Testes Estatísticos")
        self.geometry(None)
        self.minsize(width=1000, height=600)

        self.title_entry = None
        self.subtitle_entry = None
        self.checkboxes = []

        # Frame principal com abas (Notebook)
        self.tabview = ttk.Notebook(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Aba 1: Análise de dados
        self.tab_analise = ctk.CTkFrame(self.tabview)
        self.tabview.add(self.tab_analise, text="Gerador")
        self.setup_analysis_tab(self.tab_analise)

        # Aba 2: Configurações (placeholder)
        self.tab_configuracoes = ctk.CTkFrame(self.tabview)
        self.tabview.add(self.tab_configuracoes, text="Configurações")
        ctk.CTkLabel(self.tab_configuracoes, text="Configurações aparecerão aqui").pack(padx=20, pady=20)
        """
        # Aba 3: Sobre (placeholder)
        self.tab_sobre = ctk.CTkFrame(self.tabview)
        self.tabview.add(self.tab_sobre, text="Sobre")
        ctk.CTkLabel(self.tab_sobre, text="Aplicativo de análise estatística desenvolvido com tkinter e customtkinter.\nDesenvolvido por ...").pack(padx=20, pady=20)"""

    def setup_analysis_tab(self, parent):
        """
        Monta os elementos da aba de análise principal.
        """
        self.main_frame = ctk.CTkFrame(parent)
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = create_left_panel(self, self.main_frame, self.upload_excel)
        self.right_frame = create_right_panel(self, self.main_frame, self.clear_entries, self.build_grafico)
        self.table_frame, self.table_scrollable = create_table_frame(parent)

        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        self.table_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

    def upload_excel(self):
        """ Abre um diálogo para selecionar um arquivo Excel e carrega suas abas.
        Atualiza o OptionMenu com as abas disponíveis e carrega os dados da aba selecionada
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls ")],
            title="Selecione a planilha Excel"
        )
        if file_path:
            try:
                excel_file = pd.ExcelFile(file_path)
                sheets = excel_file.sheet_names

                # Atualiza o OptionMenu com as abas
                self.sheet_menu.configure(values=sheets)
                self.sheet_var.set(sheets[0])  # Seleciona a primeira aba por padrão
                
                # Carrega os dados da aba selecionada
                self.load_selected_sheet(excel_file)

                # retorna os valores da 1 coluna com excecao da linha 1


                # Cria variáveis e widgets para as colunas
                build_frame_variaveis(self, self.frame_variaveis, self.df.columns.tolist())

                # Associa mudança de aba ao carregamento dos dados
                def on_sheet_change(choice):
                    self.load_selected_sheet(excel_file)
                    build_frame_variaveis(self, self.frame_variaveis, self.df.columns.tolist())

                self.sheet_var.trace_add("write", lambda *args: on_sheet_change(self.sheet_var.get()))

            except Exception as e:
                display_table(self.table_scrollable, pd.DataFrame({"Erro": [str(e)]}))

    def load_selected_sheet(self, excel_file):
        """ Carrega a aba selecionada do arquivo Excel e exibe os dados na tabela.
        Args:
            excel_file (pd.ExcelFile): Objeto ExcelFile contendo as abas do arquivo.
        """
        self.destroy_tabel()
        aba = self.sheet_var.get()
        if not aba:
            return
        self.df = pd.read_excel(excel_file, sheet_name=aba, engine="openpyxl")

        # Retorma a tabela
        display_table(self.table_scrollable, self.df)
        return
    
    def gerar_estatisticas(self):
        """ Gera estatísticas resumidas e executa testes estatísticos com base nas entradas do usuário.
        Retorna:
            results (DataFrame): DataFrame com os resultados dos testes estatísticos.
            order_colum (list): Lista com a ordem das colunas para o gráfico, se o teste for Dunnett.
        """

        if self.testes_var.get() == "dunnett":
            # Executa o teste de Dunnett
            results, order_colum = run_test_dunnett(
                self.df,
                response_col=self.response_col.get(),
                group_col=self.group_col.get(),
                control=self.control_var.get(),
                alpha=self.value_var.get()
            )
            
            # Adiciona estatísticas resumidas e significância
            results = add_significance(
                self.df,
                results,
                response_col=self.response_col.get(),
                group_col=self.group_col.get(),
                control=self.control_var.get(),
                alpha=self.value_var.get()
            )

        elif self.testes_var.get() == "t-test":
            # Verifica se o fator_col está definido

            if not self.fator_col.get():

                groups = self.df[self.group_col.get()].unique()
                print(groups)
                if len(groups) != 2:
                    display_table(self.table_scrollable, pd.DataFrame({"Erro": ["Para o teste t, deve haver exatamente dois grupos."]}))
                    return
            # Executa o teste t

            results = run_t_test(
                self.df,
                group_col=self.group_col.get(),
                fator_col=self.fator_col.get(),
                response_col=self.response_col.get()
            )
            # Adiciona significância

        elif self.testes_var.get() == "tukey":
            # Executa o teste de Tukey
            results = run_test_tukey(
                self.df,
                response_col=self.response_col.get(),
                group_col=self.group_col.get(),
                alpha=self.value_var.get()
            )
            # Adiciona significância
            results = add_significance_tukey(results, alpha=self.value_var.get())
            

        else:
            # Exibe mensagem de erro se nenhum teste for selecionado
            results = pd.DataFrame({"": ["Selecione um teste estatístico válido."]})
        
        # Exibe os resultados na tabela
        display_table(self.table_scrollable, results)
        return results, order_colum if self.testes_var.get() == "dunnett" else None

    def build_grafico(self):
        """ Gera o gráfico com base nas estatísticas calculadas e exibe na janela.
        Verifica se o DataFrame foi carregado e se as entradas necessárias estão preenchidas.
        Se não estiverem, exibe uma mensagem de erro na tabela.
        """
        # Verifica se o DataFrame foi carregado
        if not hasattr(self, "df") or self.df.empty:
            display_table(self.table_scrollable, pd.DataFrame({"": ["Nenhum DataFrame carregado."]}))
            return
        # Verifica se as entradas necessárias estão preenchidas
        """if (self.testes_var.get()=="" or self.group_col.get()=="" or self.response_col.get()=="" or self.control_var.get()==""):
            display_table(self.table_scrollable, pd.DataFrame({"": ["Preencha todos os campos obrigatórios."]}))
            return"""
        
        summary_stats, order = self.gerar_estatisticas()

        # Configurações iniciais
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = 9

        # Configurar o plot
        plt.figure(figsize=(8/2.54, 8/2.54), dpi=300)  # Converter cm para polegadas
        ax = plt.gca()
        # Barras
        sns.barplot(x=self.group_col.get(), y='mean', data=summary_stats, 
                    errorbar='se', capsize=0.2, 
                    width=0.3, alpha=0.8, ax=ax)
        # Pontos individuais
        sns.stripplot(x=self.group_col.get(), y=self.response_col.get(), data=self.df, 
                    jitter=0.1, size=2, color='black', ax=ax)
        
        # Elementos estéticos
        y_max = (summary_stats['mean'] + summary_stats['SE']).max()
        ax.set_xticklabels(order, rotation=45, ha='right')
        ax.set(xlabel=self.eixoX_entry.get(), ylabel=self.eixoY_entry.get(), title=self.title_entry.get())
        y_espaco = 0.2 * y_max * 1.2
        ax.yaxis.set_major_locator(ticker.MultipleLocator(y_espaco))
        ax.set_ylim(0, y_max * 1.2)

        # Adicionar significância
        for i, row in summary_stats.iterrows():
            y_pos = row['mean'] + row['SE']
            ax.text(i, y_pos, row['significance'], ha='center', va='bottom', size=12)

        # Remover bordas
        sns.despine()

        # Salvar figura
        plt.savefig("grafico2.tiff", format="tiff", bbox_inches="tight")
        plt.tight_layout()
        plt.show()
        

    def clear_entries(self):
        """ Limpa todas as entradas e widgets da janela.
        Remove os textos dos campos de entrada, destrói a tabela e limpa as variáveis.
        """
        if self.title_entry:
            self.title_entry.delete(0, "end")
            
        if self.subtitle_entry:
            self.subtitle_entry.delete(0, "end")

        if self.eixoX_entry:
            self.eixoX_entry.delete(0, "end")
        
        if self.eixoY_entry:
            self.eixoY_entry.delete(0, "end")

        if hasattr(self, "value_var"):
            self.value_var.set(0.05)

        if hasattr(self, "testes_var"):
            self.testes_var.set("")
        
        self.destroy_tabel()

        if hasattr(self.table_scrollable, "tree") and self.table_scrollable.tree:
            self.table_scrollable.tree.destroy()
            self.table_scrollable.tree = None

    def destroy_tabel(self):
        if hasattr(self, "variaveis_widgets"):
            for widget in self.variaveis_widgets:
                widget.destroy()
            self.variaveis_widgets = []


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()