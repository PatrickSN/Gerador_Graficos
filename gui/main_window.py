import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

from tkinter import filedialog, ttk, colorchooser
from typing import List, Optional

from gui.widgets import *
from gui.estatistica import *


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.df: Optional[pd.DataFrame] = None
        self.filename: Optional[str] = None
        self.sheetnames: List[str] = []
        self.current_sheet: Optional[str] = None

        # Plot params
        self.color_mode_var = ctk.StringVar(value="única")
        self.title_text = ctk.StringVar(value="")
        self.xlabel_text = ctk.StringVar(value="Tratamento")
        self.ylabel_text = ctk.StringVar(value="Média ± EP")
        self.bar_color = ctk.StringVar(value="#8ec6b9")
        self.font_size = ctk.DoubleVar(value=10.0)
        self.fig_w = ctk.DoubleVar(value=8.0)
        self.fig_h = ctk.DoubleVar(value=8.0)
        self.save_format = ctk.StringVar(value="svg")

        self.title("Grafitics: estatística personalizada em gráficos")
        self.geometry(None)
        self.minsize(1000, 800)

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

    def pick_color(self):
        color = colorchooser.askcolor(color=self.bar_color.get())
        if color and color[1]:
            self.bar_color.set(color[1])

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
        frm = ctk.CTkFrame(parent); frm.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(frm, text="Cor das barras:").grid(row=1, column=0, sticky='w', pady=6, padx=6)
        ecolor = ctk.CTkEntry(frm, textvariable=self.bar_color, width=100)
        ecolor.grid(row=1, column=1, sticky='w')
        ctk.CTkButton(frm, text='Paleta…', command=self.pick_color).grid(row=1, column=2, sticky='w')
        ctk.CTkLabel(frm, text="Tamanho da fonte:").grid(row=1, column=4, sticky='w')
        ttk.Spinbox(frm, from_=10, to=24, textvariable=self.font_size, width=6).grid(row=1, column=5, sticky='w')

        ctk.CTkLabel(frm, text="Tamanho (cm):").grid(row=2, column=0, sticky='w')
        ttk.Spinbox(frm, from_=3.0, to=16.0, increment=1, textvariable=self.fig_w, width=6).grid(row=2, column=1, sticky='w')
        ttk.Spinbox(frm, from_=3.0, to=16.0, increment=1, textvariable=self.fig_h, width=6).grid(row=2, column=2, sticky='w')

        ctk.CTkLabel(frm, text="Modo de cor:").grid(row=2, column=3, sticky='e')
        self.color_mode_menu = ctk.CTkOptionMenu(frm,values=["alternadas", "única"],variable=self.color_mode_var)
        self.color_mode_menu.grid(row=2, column=4, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(frm, text="Salvar como:").grid(row=2, column=5, sticky='e')
        ttk.Combobox(frm, values=["svg","tiff"], textvariable=self.save_format, width=8).grid(row=2, column=6, sticky='w')
        ctk.CTkButton(frm, text="Salvar imagem", command=self.build_grafico).grid(row=2, column=7, padx=6)

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
            results, media, erro, letras = (run_test_tukey_anova(self.df, self.group_col.get(), self.response_col.get(), self.value_var.get()))
            display_table(self.table_scrollable, results)
            return media, erro, letras
            

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
        ext = self.save_format.get()
        dpi = 600 if ext.lower() in ('tiff','tif') else 300
        fig_w_pol = self.fig_w.get()/2.54
        fig_h_pol = self.fig_h.get()/2.54
        # Verifica se o DataFrame foi carregado
        if not hasattr(self, "df") or self.df.empty:
            display_table(self.table_scrollable, pd.DataFrame({"": ["Nenhum DataFrame carregado."]}))
            return
        # Verifica se as entradas necessárias estão preenchidas
        """if (self.testes_var.get()=="" or self.group_col.get()=="" or self.response_col.get()=="" or self.control_var.get()==""):
            display_table(self.table_scrollable, pd.DataFrame({"": ["Preencha todos os campos obrigatórios."]}))
            return"""
        
        # Configurações iniciais
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = float(self.font_size.get())

        if self.testes_var.get() == "dunnett":
            summary_stats, order = self.gerar_estatisticas()
            #lembrar de remover partes redundantes do código
            # Configurar o plot
            plt.figure(figsize=(fig_w_pol, fig_h_pol), dpi=dpi)  # Converter cm para polegadas
            ax = plt.gca()
            # Barras
            palette = sns.color_palette("Set1", n_colors=len(order))
            sns.barplot(x=self.group_col.get(), y='mean', data=summary_stats, 
                        errorbar='se', capsize=0.1, 
                        width=0.3, alpha=0.8, ax=ax, order=order, linewidth=0.4, palette=palette,
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
            if order:
                ax.set_xticks(range(len(order)))
                ax.set_xticklabels(order, rotation=45, ha='right')
            else:
                ax.set_xticks([])  # evita warnings se ordens estiver vazio
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
                    linewidth=0.4
                )
                # Adiciona o texto de significância
                ax.text(i, y_pos, row['significance'], ha='center', va='bottom', size=10)

            # Remover bordas
            sns.despine()

            # Salvar figura
            plt.savefig(f"grafico_dunnet.{ext}", format=ext, bbox_inches="tight")
            plt.tight_layout()
            plt.show()

        elif self.testes_var.get() == "t-test":
            summary_stats, order = self.gerar_estatisticas()
            
            sig_map = summary_stats.set_index(self.fator_col.get())['significance'].to_dict()
            # Configurar o plot
            fig, ax = plt.subplots(figsize=(fig_w_pol, fig_h_pol), dpi=dpi)  # Converter cm para polegadas
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
                capsize=0.1,
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
                ax.errorbar(x=x_pos, y=media, yerr=erro, fmt='none', c='black', capsize=5, linewidth=0.4)

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
                    ax.plot([x0, x1], [y_linha, y_linha], c='black', linewidth=1)
                    # Adiciona o asterisco no meio do traço
                    ax.text(idx_fator, y_linha * 1.0025, sig, ha='center', va='bottom', fontsize=float(self.font_size.get()))

            # Ajustes visuais
            y_legenda = y_max * 1.1 * 1.02
            y_legenda_rel = y_legenda / (y_max)

            ax.set_ylabel(self.eixoY_entry.get(),fontsize=float(self.font_size.get()))
            ax.set_xlabel(self.eixoX_entry.get(),fontsize=float(self.font_size.get()))
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[:len(names)], labels[:len(names)], loc="upper center", bbox_to_anchor=(0.5, y_legenda_rel), ncol=2, frameon=False)
            if ordens:
                ax.set_xticks(range(len(ordens)))
                ax.set_xticklabels(ordens, rotation=45, ha='right')
            else:
                ax.set_xticks([])  # evita warnings se ordens estiver vazio
            plt.tight_layout()

            # Remover bordas
            sns.despine()

            # Salva a figura
            plt.savefig(f"grafico_ttest.{ext}", format=ext, bbox_inches="tight")
            plt.show()
        
        elif self.testes_var.get() == "tukey":
            media, erro, letras = self.gerar_estatisticas()
            
            ordens = media.index

            plt.figure(figsize=(fig_w_pol, fig_h_pol),dpi=dpi)
            ax = plt.gca()
            x = np.arange(len(media))
            plt.bar(x, media.values, yerr=erro.values, capsize=5, color='lightblue')
            plt.xticks(x, media.index)
            plt.ylabel(self.eixoY_entry.get(), fontsize=float(self.font_size.get()))
            plt.xlabel(self.eixoX_entry.get(), fontsize=float(self.font_size.get()))
            plt.title(self.title_entry.get(), fontsize=float(self.font_size.get()))

            # Adiciona letras acima das barras
            for i in range(len(x)):
                plt.text(x[i], media.values[i] + max(erro.values)*1.1, letras[i],
                        ha='center', va='bottom', fontsize=float(self.font_size.get()))
            sns.despine()
                
             
            # Pontos individuais
            sns.stripplot(x=self.group_col.get(), y=self.response_col.get(), data=self.df, hue=self.group_col.get(), jitter=0.1, size=1, ax=ax, legend=False, palette='dark:black')
            if ordens:
                ax.set_xticks(range(len(ordens)))
                ax.set_xticklabels(ordens, rotation=45, ha='right')
            else:
                ax.set_xticks([])  # evita warnings se ordens estiver vazio

            plt.tight_layout()
            plt.savefig(f"grafico_tukey.{ext}",format=ext, dpi = dpi)
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