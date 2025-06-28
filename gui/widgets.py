import customtkinter as ctk
from tkinter import ttk



def create_left_panel(main_window, parent, upload_command):
    frame = ctk.CTkFrame(parent)

    # Grupo de seleção de planilha
    ctk.CTkButton(frame, text="Upload de planilha excel", command=upload_command).grid(row=0, column=0, pady=(10, 5))

    ctk.CTkLabel(frame, text="*Selecione a Aba:").grid(row=0, column=1, padx=10, pady=(10, 5), sticky="e")

    sheet_var = ctk.StringVar(value="")
    sheet_menu = ctk.CTkOptionMenu(frame, variable=sheet_var, values=[""])
    sheet_menu.grid(row=0, column=2, pady=(10, 5), padx=(0, 20), sticky="ew")


    # Grupo p.value
    ctk.CTkLabel(frame, text="*Alpha:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    value_var = ctk.DoubleVar(value=0.05)
    rb1 = ctk.CTkRadioButton(frame, text="0.10", variable=value_var, value=0.10)
    rb2 = ctk.CTkRadioButton(frame, text="0.05", variable=value_var, value=0.05)
    rb3 = ctk.CTkRadioButton(frame, text="0.01", variable=value_var, value=0.01)
    rb1.grid(row=1, column=1, padx=5)
    rb2.grid(row=1, column=2, padx=5)
    rb3.grid(row=1, column=3, padx=5)

    # Grupo testes
    ctk.CTkLabel(frame, text="*Testes:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    testes_var = ctk.StringVar(value=None)
    rb4 = ctk.CTkRadioButton(frame, text="Tukey", variable=testes_var, value="tukey"
    )
    rb5 = ctk.CTkRadioButton(frame, text="Dunnett", variable=testes_var, value="dunnett"
    )
    rb4.grid(row=2, column=1)
    rb5.grid(row=2, column=2)

    def up_ao_mudar(*args):
        pass

    testes_var.trace_add("write", up_ao_mudar)
    value_var.trace_add("write", up_ao_mudar)

    # Salva referências se necessário
    main_window.value_var = value_var
    main_window.testes_var = testes_var
    main_window.radiobuttons = [rb1, rb2, rb3, rb4, rb5]
    main_window.sheet_menu = sheet_menu
    main_window.sheet_var = sheet_var

    return frame

def create_right_panel(main_window, parent, clear_command, grafico_command):
    frame = ctk.CTkFrame(parent)
    
    title_entry = ctk.CTkEntry(frame, placeholder_text="Entrada do Título")
    title_entry.pack(pady=5, expand=True)

    subtitle_entry = ctk.CTkEntry(frame, placeholder_text="Entrada do SubTítulo")
    subtitle_entry.pack(pady=5, expand=True)

    eixoX_entry = ctk.CTkEntry(frame, placeholder_text="Entrada do Eixo X")
    eixoX_entry.pack(pady=5, expand=True)

    eixoY_entry = ctk.CTkEntry(frame, placeholder_text="Entrada do Eixo Y")
    eixoY_entry.pack(pady=5, expand=True)

    ctk.CTkButton(frame, text="Gerar gráfico", command=grafico_command).pack(pady=(20, 5))
    ctk.CTkButton(frame, text="Limpar entradas", command=clear_command).pack(pady=5)

    main_window.title_entry = title_entry
    main_window.subtitle_entry = subtitle_entry
    main_window.eixoX_entry = eixoX_entry
    main_window.eixoY_entry = eixoY_entry

    return frame

def build_frame_variaveis(main_window, frame, variaveis):
    """ Cria o frame de variáveis para seleção de colunas de tratamento e valores.
    Parâmetros:
    - main_window: Instância da janela principal.
    - frame: Frame onde os widgets serão adicionados.
    - variaveis: Lista de variáveis disponíveis para seleção.
    Se variaveis estiver vazio, não cria os widgets de seleção.
    """
    if not variaveis:
        ctk.CTkLabel(frame, text="Nenhuma variável disponível.").grid(row=3, column=0, columnspan=4, padx=10, pady=(10, 5))
        return

    ctk.CTkLabel(frame, text="*Coluna de tratamento:").grid(row=3, column=0, padx=10, pady=(10, 5), sticky="e")
    group_col = ctk.StringVar(value=variaveis[0] if variaveis else "")
    group_menu = ctk.CTkOptionMenu(frame, variable=group_col, values=variaveis)
    group_menu.grid(row=3, column=1, padx=(0, 20))

    ctk.CTkLabel(frame, text="*Coluna dos valores:").grid(row=3, column=2, padx=10, pady=(10, 5), sticky="e")
    response_col = ctk.StringVar(value=variaveis[len(variaveis)-1])
    response_menu = ctk.CTkOptionMenu(frame, variable=response_col, values=variaveis)
    response_menu.grid(row=3, column=3, padx=(0, 20))

    # Adiciona menu de tratamentos disponíveis
    def atualizar_controles(*args):
        try:
            # Remove menu antigo se existir
            if hasattr(main_window, "control_menu") and main_window.control_menu:
                main_window.control_menu.destroy()
            if hasattr(main_window, "control_label") and main_window.control_label:
                main_window.control_label.destroy()

            col = group_col.get()
            if hasattr(main_window, "df") and col in main_window.df.columns:
                controls = main_window.df[col].dropna().unique().tolist()
                controls = [str(c) for c in controls]  # Converte todos para string
                main_window.control_label = ctk.CTkLabel(frame, text="*Selecione o controle:")
                main_window.control_label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="e")
                main_window.control_var = ctk.StringVar(value=controls[0] if controls else "")
                main_window.control_menu = ctk.CTkOptionMenu(frame, variable=main_window.control_var, values=controls)
                main_window.control_menu.grid(row=4, column=1, padx=(0, 20))
            else:
                main_window.control_label = None
                main_window.control_menu = None
        except Exception as e:
            if hasattr(main_window, "control_menu"):
                main_window.control_menu.destroy()
            if hasattr(main_window, "control_label"):
                main_window.control_label.destroy()

    group_col.trace_add("write", atualizar_controles)
    atualizar_controles()  # Inicializa ao criar

    main_window.group_col = group_col
    main_window.response_col = response_col


def create_table_frame(parent):
    frame = ctk.CTkFrame(parent)
    scrollable = ctk.CTkScrollableFrame(frame)
    scrollable.pack(padx=10, pady=10, fill="both", expand=True)
    return frame, scrollable

def display_table(scrollable_frame, df):
    # Remove Treeview antigo, se existir
    if hasattr(scrollable_frame, "tree") and scrollable_frame.tree:
        scrollable_frame.tree.destroy()
    if hasattr(scrollable_frame, "h_scroll") and scrollable_frame.h_scroll:
        scrollable_frame.h_scroll.destroy()

    # Cria novo Treeview
    tree = ttk.Treeview(scrollable_frame, columns=list(df.columns), show="headings")
    tree.pack(fill="both", expand=True, side="top")

    # Scrollbar horizontal
    h_scroll = ttk.Scrollbar(scrollable_frame, orient="horizontal", command=tree.xview)
    h_scroll.pack(fill="x", side="bottom")
    tree.configure(xscrollcommand=h_scroll.set)

    # Inicializa dicionário de ordenação, se necessário
    if not hasattr(scrollable_frame, "sort_ascending"):
        scrollable_frame.sort_ascending = {}

    # Define cabeçalhos e comandos de ordenação
    for col in df.columns:
        tree.heading(col, text=col, command=lambda c=col: sort_by_column(scrollable_frame, df, tree, c))
        tree.column(col, anchor="center")
        scrollable_frame.sort_ascending[col] = True

    # Salva referências
    scrollable_frame.tree = tree
    scrollable_frame.df = df
    scrollable_frame.h_scroll = h_scroll

    # Insere linhas
    insert_rows(tree, df)

def insert_rows(tree, df):
    for row in tree.get_children():
        tree.delete(row)
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

def sort_by_column(scrollable_frame, df, tree, col):
    ascending = scrollable_frame.sort_ascending[col]
    df.sort_values(by=col, ascending=ascending, inplace=True, ignore_index=True)
    insert_rows(tree, df)
    scrollable_frame.sort_ascending[col] = not ascending

def order_of_(df, coluna= None):
    """
    Retorna uma lista com todos os valores únicos presentes em todas as colunas do DataFrame, sem repetição.
    """
    valores_unicos = set()
    if coluna:
        # Se uma coluna específica for fornecida, retorna os valores únicos dessa coluna
        if coluna in df.columns:
            valores_unicos.update(df[coluna].dropna().unique())
        
    # Caso contrário, percorre todas as colunas do DataFrame
    else:

        for col in df.columns:
            valores_unicos.update(df[col].dropna().unique())

    return list(valores_unicos)