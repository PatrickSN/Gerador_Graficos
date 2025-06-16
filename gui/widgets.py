import customtkinter as ctk
from tkinter import ttk



def create_left_panel(main_window, parent, upload_command):
    frame = ctk.CTkFrame(parent)

    # Grupo de seleção de planilha
    sheet_var = ctk.StringVar(value="")
    sheet_menu = ctk.CTkOptionMenu(frame, variable=sheet_var, values=[""])
    sheet_menu.grid(row=0, column=0, pady=(10, 5), padx=(0, 20), sticky="ew")

    ctk.CTkButton(frame, text="Upload de planilha excel", command=upload_command).grid(row=0, column=1, pady=(10, 5))

    # Grupo p.value
    ctk.CTkLabel(frame, text="value:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    value_var = ctk.DoubleVar(value=0.05)
    rb1 = ctk.CTkRadioButton(frame, text="0.10", variable=value_var, value=0.10)
    rb2 = ctk.CTkRadioButton(frame, text="0.05", variable=value_var, value=0.05)
    rb3 = ctk.CTkRadioButton(frame, text="0.01", variable=value_var, value=0.01)
    rb1.grid(row=1, column=1, padx=5)
    rb2.grid(row=1, column=2, padx=5)
    rb3.grid(row=1, column=3, padx=5)

    # Grupo testes
    ctk.CTkLabel(frame, text="testes:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    testes_var = ctk.StringVar(value=None)
    rb4 = ctk.CTkRadioButton(frame, text="Dunnet", variable=testes_var, value="dunnet"
    )
    rb5 = ctk.CTkRadioButton(frame, text="Teste t", variable=testes_var, value="teste_t"
    )
    rb4.grid(row=2, column=1)
    rb5.grid(row=2, column=2)

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
    entries_vals = {}
    lbl = ctk.CTkLabel(frame, text="Selecione o controle:", justify="right")
    lbl.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    radio_widgets = [lbl]

    val_var = ctk.StringVar(value=None)
    for i, nome in enumerate(variaveis):
        rb = ctk.CTkRadioButton(frame, text=f"{nome}", variable=val_var, value=f"{nome}")
        rb.grid(row=3, column=i+1, padx=10, pady=5, sticky="e")
        entries_vals[nome] = rb
        radio_widgets.append(rb)
    
    main_window.val_var = val_var
    main_window.radiobuttons = entries_vals 
    main_window.variaveis_widgets = radio_widgets 

def create_table_frame(parent):
    frame = ctk.CTkFrame(parent)
    scrollable = ctk.CTkScrollableFrame(frame)
    scrollable.pack(padx=10, pady=10, fill="both", expand=True)
    return frame, scrollable

def display_table(scrollable_frame, df):
    # Remove Treeview antigo, se existir
    if hasattr(scrollable_frame, "tree") and scrollable_frame.tree:
        scrollable_frame.tree.destroy()

    # Cria novo Treeview
    tree = ttk.Treeview(scrollable_frame, columns=list(df.columns), show="headings")
    tree.pack(fill="both", expand=True)

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