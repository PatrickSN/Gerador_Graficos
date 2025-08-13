import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

from tkinter import filedialog, ttk, colorchooser

from gui.widgets import *
from gui.estatistica import *


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Análise de Dados com Testes Estatísticos")
        self.geometry(None)
        self.minsize(1000, 600)

        self.title_entry = None
        self.subtitle_entry = None
        self.checkboxes = []

        # Frame principal com abas (Notebook)
        self.tabview = ttk.Notebook(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Aba 1: Análise de dados
        self.tab_analise = ctk.CTkFrame(self.tabview)
        self.tabview.add(self.tab_analise, text="Generate")
        self.setup_analysis_tab(self.tab_analise)

        # Aba 2: Configurações (placeholder)
        self.tab_configuracoes = ctk.CTkFrame(self.tabview)
        self.tabview.add(self.tab_configuracoes, text="Settings")
        self.setup_settings_tab(self.tab_configuracoes)

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

    def setup_settings_tab(self, parent):
        """
        Configura os elementos do grafico.
        """
        def escolher_cor():
            cor = colorchooser.askcolor(title="Escolha uma cor")[1]
            if cor:
                self.selected_color = cor
                self.color_label.configure(text=f"Cor selecionada: {cor}", fg_color=cor)

        def toggle_legend():    
            """ Alterna a visibilidade da legenda no gráfico.
            """
            if hasattr(self, "legend_visible"):
                self.legend_visible = not self.legend_visible
            else:
                self.legend_visible = True

            # Atualiza a legenda no gráfico
            if hasattr(self, "grafico"):
                self.grafico.legend().set_visible(self.legend_visible)
                self.grafico.draw()
        
        self.settings_frame = ctk.CTkFrame(parent)
        self.settings_frame.pack(fill="both", expand=True)

        #configura algumas funcoes do grafico
        self.legenda = ctk.CTkCheckBox(self.settings_frame, text="Subtitle", command=toggle_legend())
        self.legenda.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.fontSize = ctk.CTkEntry(self.settings_frame, placeholder_text="Font Size", width=200)
        self.fontSize.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.figSize = ctk.CTkEntry(self.settings_frame, placeholder_text="Figure Size", width=200)
        self.figSize.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        #configura as cores do grafico
        ctk.CTkLabel(self.settings_frame, text="Cores do gráfico:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.selected_color = "#66c2a5"  # cor padrão
        self.color_label = ctk.CTkLabel(self.settings_frame, text=f"Cor selecionada: {self.selected_color} ", fg_color=self.selected_color)
        self.color_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.color_button = ctk.CTkButton(self.settings_frame, text="Selecionar cor", command=escolher_cor)
        self.color_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.color_mode_var = ctk.StringVar(value="única")
        self.color_mode_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            values=["alternadas", "única"],
            variable=self.color_mode_var
        )
        self.color_mode_menu.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        add_tooltip(self.color_mode_menu, "Escolha entre cores alternadas ou cor única para as barras")
        add_tooltip(self.fontSize, "Tamanho da fonte do gráfico")
        add_tooltip(self.figSize, "Entre com o tamanho da figura em centimetros (ex: 8x6)")
        
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
                self.excel_file = pd.ExcelFile(file_path)
                sheets = self.excel_file.sheet_names

                # Atualiza o OptionMenu com as abas
                self.sheet_menu.configure(values=sheets)
                self.sheet_var.set(sheets[0])  # Seleciona a primeira aba por padrão
                
                # Carrega os dados da aba selecionada
                self.load_selected_sheet(self.excel_file)

                # retorna os valores da 1 coluna com excecao da linha 1


                # Cria variáveis e widgets para as colunas
                build_frame_variaveis(self, self.frame_variaveis, self.df.columns.tolist())

                # Associa mudança de aba ao carregamento dos dados
                def on_sheet_change(choice):
                    self.load_selected_sheet(self.excel_file)
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
            results = add_significance_dunnet(
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

            results, order_colum = add_significance_ttest(
                self.df,
                results,
                response_col=self.response_col.get(),
                group_col=self.group_col.get(),
                fator_col=self.fator_col.get(),
                alpha=self.value_var.get()
            )

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
        return results, order_colum if self.testes_var.get() == "dunnett" or self.testes_var.get() == "t-test" else None

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
        
        # Configurações iniciais
        plt.rcParams['font.family'] = self.font_family_var.get() if hasattr(self, 'font_family_var') else 'Arial'
        plt.rcParams['font.size'] = int(self.fontSize.get()) if self.fontSize else 10

        if self.testes_var.get() == "dunnett":
            summary_stats, order = self.gerar_estatisticas()
            #lembrar de remover partes redundantes do código
            # Configurar o plot
            plt.figure(figsize=(8/2.54, 8/2.54), dpi=300)  # Converter cm para polegadas
            ax = plt.gca()
            # Barras
            if self.color_mode_var.get() == "única":
                # Cor única para todas as barras
                palette = [self.selected_color] * len(order)
            else:
                # Cores alternadas, ajustando à quantidade de variáveis
                palette = sns.color_palette("Set1", n_colors=len(order))
            sns.barplot(x=self.group_col.get(), y='mean', data=summary_stats, 
                        errorbar='se', capsize=0.2, 
                        width=0.3, alpha=0.8, ax=ax, order=order, linewidth=1, palette=palette,
                        hue=self.group_col.get(),
                        legend=False
                        )
            # Pontos individuais
            sns.stripplot(x=self.group_col.get(), y=self.response_col.get(), data=self.df, hue=self.group_col.get(),  
                        jitter=0.1, size=1, palette='dark:black', ax=ax, legend=False)
            
            # Elementos estéticos# busca a maior media para ajustar o limite do eixo y
            y_max = summary_stats['mean'].max()
            ax.set_ylim(0, y_max * 1.2)
            ax.set_xticks(range(len(order)))  # Garante que o número de ticks corresponde ao número de labels
            ax.set_xticklabels(order, rotation=45, ha='right')
            ax.set(xlabel=self.eixoX_entry.get(), ylabel=self.eixoY_entry.get(), title=self.title_entry.get())
            y_espaco = 0.2 * y_max * 1.2
            ax.yaxis.set_major_locator(ticker.MultipleLocator(y_espaco))
            ax.set_ylim(0, y_max * 1.2)

            # Adicionar significância
            for i, row in summary_stats.iterrows():
                y_pos = row['mean'] + row['SE']
                # Adiciona barra de erro
                ax.errorbar(
                    x=i,
                    y=row['mean'],
                    yerr=row['SE'],
                    fmt='none',           # Não desenha marcador, só a barra de erro
                    c='black',
                    capsize=5,
                    linewidth=1
                )
                # Adiciona o texto de significância
                ax.text(i, y_pos, row['significance'], ha='center', va='bottom', size=10)

            # Remover bordas
            sns.despine()

            # Salvar figura
            plt.savefig("grafico1.tiff", format="tiff", bbox_inches="tight")
            plt.tight_layout()
            plt.show()

        elif self.testes_var.get() == "t-test":
            summary_stats, order = self.gerar_estatisticas()
            
            sig_map = summary_stats.set_index(self.fator_col.get())['significance'].to_dict()
            # Configurar o plot
            fig, ax = plt.subplots(figsize=(8/2.54, 8/2.54), dpi=300)  # Converter cm para polegadas
            # Gráfico de barras
            if "control" or "Col-0" in order:
                ordens = order
            else:
                ordens = sorted(summary_stats[self.fator_col.get()].unique(), key=fator_sort_key)
            sns.barplot(
                data=summary_stats,
                x=self.fator_col.get(),
                y="mean",
                hue=self.group_col.get(),
                ax=ax,
                capsize=0.2,
                palette="Set2",
                order=ordens
                )
            # Pontos individuais
            sns.stripplot(
                        x=self.fator_col.get(),
                        y=self.response_col.get(),
                        data=self.df,  
                        hue=self.group_col.get(),      # Adicione o mesmo hue do barplot
                        order=ordens,                  # Use a mesma ordem do barplot
                        dodge=True,     # Para separar os pontos dos grupos
                        jitter=0.1,
                        size=1,
                        palette='dark:black',
                        ax=ax
                        )

            # busca a maior media para ajustar o limite do eixo y
            y_max = summary_stats['mean'].max()
            ax.set_ylim(0, y_max * 1.2)

            # Adiciona barras de erro e asteriscos
            names = summary_stats[self.group_col.get()].unique()

            for i, row in summary_stats.iterrows():
                fator = row[self.fator_col.get()]
                grupo = row[self.group_col.get()]
                media = row['mean']
                erro = row['SE']
                idx_fator = ordens.index(fator)
                deslocamento = -0.2 if grupo == names[0] else 0.2
                x_pos = idx_fator + deslocamento
                ax.errorbar(x=x_pos, y=media, yerr=erro, fmt='none', c='black', capsize=5, linewidth=1)

                # Apenas um asterisco por fator (acima da barra mais alta)
                """if grupo == names[1] and fator in sig_map:
                    sig = sig_map[fator]
                    if sig != 'ns':
                        altura = summary_stats[(summary_stats[self.fator_col.get()] == fator)]["mean"].max()
                        ax.text(idx_fator, altura + 1, sig, ha='center', va='bottom', fontsize=12, fontweight='bold')"""

            for fator in ordens:
                # Verifica se há significância para esse fator
                sig = sig_map.get(fator, "")
                if sig and sig != 'ns':
                    # Pega as posições das barras no eixo x
                    idx_fator = ordens.index(fator)
                    x0 = idx_fator - 0.2
                    x1 = idx_fator + 0.2
                    y_linha = y_max * 1.1  # ajuste a altura do traço conforme necessário

                    # Desenha o traço
                    ax.plot([x0, x1], [y_linha, y_linha], c='black', linewidth=1.5)
                    # Adiciona o asterisco no meio do traço
                    ax.text(idx_fator, y_linha * 1.0025, sig, ha='center', va='bottom', fontsize=14, fontweight='bold')

            # Ajustes visuais
            y_legenda = y_max * 1.1 * 1.02
            y_legenda_rel = y_legenda / (y_max)

            ax.set_ylabel(self.eixoY_entry.get())
            ax.set_xlabel(self.eixoX_entry.get())
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[:len(names)], labels[:len(names)], loc="upper center", bbox_to_anchor=(0.5, y_legenda_rel), ncol=2, frameon=False)
            plt.tight_layout()

            # Remover bordas
            sns.despine()

            # Salva a figura
            plt.savefig("grafico2.tiff", format="tiff", bbox_inches="tight")
            plt.show()
        
        elif self.testes_var.get() == "tukey":
            tukey_result, order = self.gerar_estatisticas()
            # Calcula média e erro padrão por genotype
            estatisticas = self.df.groupby(self.group_col.get(), observed=False)[self.response_col.get()].agg(['mean', 'std', 'count']).reset_index()
            estatisticas['SE'] = estatisticas['std'] / np.sqrt(estatisticas['count'])

            # Determina letras de significância com base nas comparações
            # Inicializa cada genotype com uma letra única
            genotypes = estatisticas[self.group_col.get()].tolist()
            letras = {g: set([chr(97 + i)]) for i, g in enumerate(genotypes)}  # a, b, c, ...

            # Remove letras de genotypes que não diferem entre si
            for _, row in tukey_result.iterrows():
                g1, g2 = row['group1'], row['group2']
                p = row['p-adj']
                if p >= self.value_var.get():
                    # Unifica os conjuntos de letras
                    uniao = letras[g1] | letras[g2]
                    letras[g1] = letras[g2] = uniao

            # Converte sets em strings (ex: {'a', 'b'} -> 'ab')
            estatisticas['letra'] = estatisticas[self.group_col.get()].map(lambda g: ''.join(sorted(letras[g])))

            # Gráfico
            fig, ax = plt.subplots(figsize=(8/2.54, 8/2.54), dpi=300)  # Converter cm para polegadas
            sns.barplot(
                        data=estatisticas,
                        x=self.group_col.get(),
                        y="mean",
                        hue=self.group_col.get(),   # Adicione hue igual ao x
                        ax=ax,
                        palette="Set2",
                        capsize=0.1,
                        legend=False                # Para não duplicar a legenda
                        )

            # Pontos individuais
            sns.stripplot(x=self.group_col.get(), y=self.response_col.get(), data=self.df, hue=self.group_col.get(), 
                        jitter=0.1, size=2, palette='dark:black', ax=ax, legend=False)

            # Adiciona barras de erro e letras de significância
            for i, row in estatisticas.iterrows():
                x = i
                y = row['mean']
                se = row['SE']
                letra = row['letra']
                ax.errorbar(x=x, y=y, yerr=se, fmt='none', c='black', capsize=5, linewidth=1)
                ax.text(x, y + se + 0.1, letra, ha='center', va='bottom', fontsize=9)

            # Remover bordas
            sns.despine()

            # Ajustes visuais
            ax.set_ylabel(self.eixoY_entry.get())
            ax.set_xlabel(self.eixoX_entry.get())
            ax.set_title(self.title_entry.get())
            plt.tight_layout()

            # Salva a figura
            plt.savefig("grafico3.tiff", format="tiff", bbox_inches="tight")
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