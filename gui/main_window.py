import customtkinter as ctk
from tkinter import filedialog
from gui.widgets import *
from gui.test_t import *
from gui.test_dunnett import *
import pandas as pd

# acesso ao value e testes
# valor_value = self.value_var.get()
# tipo_teste = self.testes_var.get()

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Análise de Dados com Testes Estatísticos")
        self.geometry(None)
        self.minsize(width=800, height=600)

        self.title_entry = None
        self.subtitle_entry = None
        self.checkboxes = []

        # Variáveis de frames
        self.main_frame = ctk.CTkFrame(self)
        self.left_frame = create_left_panel(
            self, self.main_frame, self.upload_excel
        )
        self.right_frame = create_right_panel(
            self, self.main_frame, self.clear_entries, self.build_grafico
        )
        self.table_frame, self.table_scrollable = create_table_frame(self)

        # Posição dos frames
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        self.table_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

    def upload_excel(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls *.csv")],
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

                # Associa mudança de aba ao carregamento dos dados
                def on_sheet_change(choice):
                    self.load_selected_sheet(excel_file)
                self.sheet_var.trace_add("write", lambda *args: on_sheet_change(self.sheet_var.get()))

            except Exception as e:
                display_table(self.table_scrollable, pd.DataFrame({"Erro": [str(e)]}))
                print(f"Erro ao carregar o arquivo: {e}")

    def build_grafico(self):
        if not hasattr(self, "df") or self.df.empty:
            display_table(self.table_scrollable, pd.DataFrame({"Erro": ["Nenhum dado carregado!"]}))
            return
        
        # Verifica se o título e subtítulo foram preenchidos
        
        # Verifica se o eixo X e Y foram preenchidos

        # Verifica se o teste foi selecionado
        tipo_teste = self.testes_var.get() if hasattr(self, "testes_var") else ""

        dados = {
            "title": self.title_entry.get() if self.title_entry else "",
            "subtitle": self.subtitle_entry.get() if self.subtitle_entry else "",
            "eixoX": self.eixoX_entry.get() if hasattr(self, "eixoX_entry") else "",
            "eixoY": self.eixoY_entry.get() if hasattr(self, "eixoY_entry") else "",
            "control": self.val_var.get() if hasattr(self, "val_var") else "",
            "value": self.value_var.get() if hasattr(self, "value_var") else 0.05,
            "df": self.df
        }

        print(f"Dados para o gráfico: {dados}")
        return
        
        if tipo_teste == "dunnet":
            display_table(self.table_scrollable, pd.DataFrame({"Desenvolvimento": ["Selecione outro teste estatístico!"]}))
            build_dunnett_test(self.df, title, subtitle, eixoX, eixoY)
        elif tipo_teste == "teste_t":
            build_t_test(self.df, title, subtitle, eixoX, eixoY)
        else:
            display_table(self.table_scrollable, pd.DataFrame({"Erro": ["Selecione um teste estatístico válido!"]}))

    def load_selected_sheet(self, excel_file):
        self.destroy_variables()
        aba = self.sheet_var.get()
        if not aba:
            return
        self.df = pd.read_excel(excel_file, sheet_name=aba, engine="openpyxl")
        
        # Verifica a seleção do teste
        if self.testes_var.get() == "dunnet":
            cabecalho_esperado = ["Treatment", "Factors", "Values"]
            treatments = order_of_(self.df, "Treatment")
            factors = order_of_(self.df, "Factors")
            build_frame_variaveis(self, self.left_frame, factors)
        elif self.testes_var.get() == "teste_t":
            cabecalho_esperado = ["Treatment", "Values"]
            treatments = order_of_(self.df, "Treatment")
            build_frame_variaveis(self, self.left_frame, treatments)
        
        # Retorma a tabela
        else:
            display_table(self.table_scrollable, self.df)
            return

        # Verifica se o cabeçalho está correto
        if list(self.df.columns) != cabecalho_esperado:
            display_table(self.table_scrollable, pd.DataFrame({"Erro": ["Cabeçalho inválido! Para o teste é esperado: " + ", ".join(cabecalho_esperado)]}))
            return
        
        display_table(self.table_scrollable, self.df)

    def clear_entries(self):
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
        
        self.destroy_variables()

        if hasattr(self.table_scrollable, "tree") and self.table_scrollable.tree:
            self.table_scrollable.tree.destroy()
            self.table_scrollable.tree = None

    def destroy_variables(self):        
        if hasattr(self, "val_var"):
            self.val_var.set("")

        if hasattr(self, "variaveis_widgets"):
            for widget in self.variaveis_widgets:
                widget.destroy()
            self.variaveis_widgets = []


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()