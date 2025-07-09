import customtkinter as ctk
from tkinter import ttk



def create_left_panel(main_window, parent, upload_command):
    """ Cria o painel esquerdo da janela principal com opções de upload, seleção de planilha e configurações de testes estatísticos.
    Parâmetros:
    - main_window: Instância da janela principal.
    - parent: Frame pai onde os widgets serão adicionados.
    - upload_command: Função a ser chamada ao clicar no botão de upload.
    Retorna:
    - frame: Frame contendo os widgets de seleção e configuração.
    """
    frame = ctk.CTkFrame(parent)

    # Grupo de seleção de planilha
    ctk.CTkButton(frame, text="Upload sheet", command=upload_command).grid(row=0, column=0, pady=(10, 5))

    ctk.CTkLabel(frame, text="Select table:").grid(row=0, column=1, padx=10, pady=(10, 5), sticky="e")

    sheet_var = ctk.StringVar(value="")
    sheet_menu = ctk.CTkOptionMenu(frame, variable=sheet_var, values=[""])
    sheet_menu.grid(row=0, column=2, pady=(10, 5), padx=(0, 20), sticky="ew")


    # Grupo p.value
    ctk.CTkLabel(frame, text="p_value:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    value_var = ctk.DoubleVar(value=0.05)
    rb1 = ctk.CTkRadioButton(frame, text="0.10", variable=value_var, value=0.10)
    rb2 = ctk.CTkRadioButton(frame, text="0.05", variable=value_var, value=0.05)
    rb3 = ctk.CTkRadioButton(frame, text="0.01", variable=value_var, value=0.01)
    rb1.grid(row=1, column=1, padx=5)
    rb2.grid(row=1, column=2, padx=5)
    rb3.grid(row=1, column=3, padx=5)

    # Grupo testes
    ctk.CTkLabel(frame, text="Statistical Test:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    testes_var = ctk.StringVar(value=None)
    rb4 = ctk.CTkRadioButton(frame, text="Tukey", variable=testes_var, value="tukey"
    )
    rb5 = ctk.CTkRadioButton(frame, text="Dunnett", variable=testes_var, value="dunnett"
    )
    rb6 = ctk.CTkRadioButton(frame, text="T-test", variable=testes_var, value="t-test"
    )
    rb4.grid(row=2, column=1)
    rb5.grid(row=2, column=2)
    rb6.grid(row=2, column=3)

    def up_ao_mudar(*args):
        if hasattr(main_window, "df"):
            build_frame_variaveis(main_window, main_window.frame_variaveis, main_window.df.columns.tolist())
            main_window.load_selected_sheet(main_window.excel_file)

    testes_var.trace_add("write", up_ao_mudar)
    value_var.trace_add("write", up_ao_mudar)

    # Cria o frame de variáveis e salva na main_window
    frame_variaveis = ctk.CTkFrame(frame)
    frame_variaveis.grid(row=5, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
    main_window.frame_variaveis = frame_variaveis

    # Salva referências se necessário
    main_window.value_var = value_var
    main_window.testes_var = testes_var
    main_window.radiobuttons = [rb1, rb2, rb3, rb4, rb5, rb6]
    main_window.sheet_menu = sheet_menu
    main_window.sheet_var = sheet_var

    return frame

def create_right_panel(main_window, parent, clear_command, grafico_command):
    """ Cria o painel direito da janela principal com campos de entrada para título, subtítulo, eixos X e Y, além de botões para gerar gráfico e limpar entradas.
    Parâmetros:
    - main_window: Instância da janela principal.
    - parent: Frame pai onde os widgets serão adicionados.
    - clear_command: Função a ser chamada ao clicar no botão de limpar entradas.
    - grafico_command: Função a ser chamada ao clicar no botão de gerar gráfico.
    Retorna:
    - frame: Frame contendo os widgets de entrada e botões.
    """
    frame = ctk.CTkFrame(parent)
    
    title_entry = ctk.CTkEntry(frame, placeholder_text="Enter Title")
    title_entry.pack(pady=5, expand=True)

    subtitle_entry = ctk.CTkEntry(frame, placeholder_text="Enter Subtitle")
    subtitle_entry.pack(pady=5, expand=True)

    eixoX_entry = ctk.CTkEntry(frame, placeholder_text="Enter x-axis")
    eixoX_entry.pack(pady=5, expand=True)

    eixoY_entry = ctk.CTkEntry(frame, placeholder_text="Enter y-axis")
    eixoY_entry.pack(pady=5, expand=True)

    ctk.CTkButton(frame, text="Chart generate", command=grafico_command).pack(pady=(20, 5))
    ctk.CTkButton(frame, text="Clear entries", command=clear_command).pack(pady=5)

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
    # Adiciona menu de tratamentos disponíveis
    def atualizar_controles(*args):
        try:
            # Destroi apenas se o widget ainda existir e não for None
            if hasattr(main_window, "control_menu") and main_window.control_menu is not None:
                try:
                    main_window.control_menu.destroy()
                except Exception:
                    pass
                main_window.control_menu = None
            if hasattr(main_window, "control_label") and main_window.control_label is not None:
                try:
                    main_window.control_label.destroy()
                except Exception:
                    pass
                main_window.control_label = None

            col = group_col.get()
            if hasattr(main_window, "df") and col in main_window.df.columns:
                controls = main_window.df[col].dropna().unique().tolist()
                controls = [str(c) for c in controls]  # Converte todos para string
                main_window.control_label = ctk.CTkLabel(frame, text="Select control:")
                main_window.control_label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="e")
                main_window.control_var = ctk.StringVar(value=controls[0] if controls else "")
                main_window.control_menu = ctk.CTkOptionMenu(frame, variable=main_window.control_var, values=controls)
                main_window.control_menu.grid(row=4, column=1, padx=(0, 20))
            else:
                main_window.control_label = None
                main_window.control_menu = None
        except Exception as e:
            # Evita erro duplo de destruição
            pass

    # Limpa o frame antes de adicionar novos widgets
    for widget in frame.winfo_children():
        widget.destroy()

    if not variaveis:
        ctk.CTkLabel(frame, text="Nenhuma variável disponível.").grid(row=3, column=0, columnspan=4, padx=10, pady=(10, 5))
        return
    
    if main_window.testes_var.get() not in ["dunnett", "tukey", "t-test"]:
        ctk.CTkLabel(frame, text="Selecione um teste estatístico.").grid(row=3, column=0, columnspan=4, padx=10, pady=(10, 5))
        return

    if main_window.testes_var.get() == "t-test" or main_window.testes_var.get() == "tukey" and len(variaveis) >= 3:
        ctk.CTkLabel(frame, text="Group column:").grid(row=3, column=0, padx=10, pady=(10, 5), sticky="e")
        group_col = ctk.StringVar(value=variaveis[0] if variaveis else "")
        group_menu = ctk.CTkOptionMenu(frame, variable=group_col, values=variaveis)
        group_menu.grid(row=3, column=1, padx=(0, 20))

        ctk.CTkLabel(frame, text="Condition column:").grid(row=3, column=2, padx=10, pady=(10, 5), sticky="e")
        fator_col = ctk.StringVar(value=variaveis[len(variaveis)-2])
        fator_menu = ctk.CTkOptionMenu(frame, variable=fator_col, values=variaveis)
        fator_menu.grid(row=3, column=3, padx=(0, 20))

        ctk.CTkLabel(frame, text="Values column:").grid(row=3, column=4, padx=10, pady=(10, 5), sticky="e")
        response_col = ctk.StringVar(value=variaveis[len(variaveis)-1])
        response_menu = ctk.CTkOptionMenu(frame, variable=response_col, values=variaveis)
        response_menu.grid(row=3, column=5, padx=(0, 20))

    elif main_window.testes_var.get() == "t-test" or main_window.testes_var.get() == "tukey": 
        ctk.CTkLabel(frame, text="Group column:").grid(row=3, column=0, padx=10, pady=(10, 5), sticky="e")
        group_col = ctk.StringVar(value=variaveis[0] if variaveis else "")
        group_menu = ctk.CTkOptionMenu(frame, variable=group_col, values=variaveis)
        group_menu.grid(row=3, column=1, padx=(0, 20))

        ctk.CTkLabel(frame, text="Values column:").grid(row=3, column=2, padx=10, pady=(10, 5), sticky="e")
        response_col = ctk.StringVar(value=variaveis[len(variaveis)-1])
        response_menu = ctk.CTkOptionMenu(frame, variable=response_col, values=variaveis)
        response_menu.grid(row=3, column=3, padx=(0, 20))

        fator_col = ctk.StringVar(value=None)  # Não é necessário fator_col para t-test com apenas dois grupos sem fator


    else:
        ctk.CTkLabel(frame, text="Group column:").grid(row=3, column=0, padx=10, pady=(10, 5), sticky="e")
        group_col = ctk.StringVar(value=variaveis[0] if variaveis else "")
        group_menu = ctk.CTkOptionMenu(frame, variable=group_col, values=variaveis)
        group_menu.grid(row=3, column=1, padx=(0, 20))

        ctk.CTkLabel(frame, text="Values column:").grid(row=3, column=2, padx=10, pady=(10, 5), sticky="e")
        response_col = ctk.StringVar(value=variaveis[len(variaveis)-1])
        response_menu = ctk.CTkOptionMenu(frame, variable=response_col, values=variaveis)
        response_menu.grid(row=3, column=3, padx=(0, 20))

        fator_col = ctk.StringVar(value=None)  # Não é necessário fator_col 
        
        group_col.trace_add("write", atualizar_controles)
        atualizar_controles()  # Inicializa ao criar

    main_window.group_col = group_col
    main_window.fator_col = fator_col
    main_window.response_col = response_col


def create_table_frame(parent):
    """ Cria um frame para exibir uma tabela com rolagem.
    Parâmetros:
    - parent: Frame pai onde o frame da tabela será adicionado.
    Retorna:
    - frame: Frame contendo o scrollable frame para a tabela.
    - scrollable: Frame rolável onde a tabela será exibida.
    """
    frame = ctk.CTkFrame(parent)
    scrollable = ctk.CTkScrollableFrame(frame)
    scrollable.pack(padx=10, pady=10, fill="both", expand=True)
    return frame, scrollable

def display_table(scrollable_frame, df):
    """ Exibe um DataFrame em um Treeview dentro de um frame rolável.
    Parâmetros:
    - scrollable_frame: Frame rolável onde a tabela será exibida.
    - df: DataFrame a ser exibido.
    Se o scrollable_frame já tiver um Treeview, ele será destruído e substituído
    por um novo Treeview com os dados do DataFrame.
    """
    # Remove Treeview antigo, se existir
    if hasattr(scrollable_frame, "tree") and scrollable_frame.tree:
        scrollable_frame.tree.destroy()

    # Cria novo Treeview
    tree = ttk.Treeview(scrollable_frame, columns=list(df.columns), show="headings")
    tree.pack(fill="both", expand=True, side="top")

    # Scrollbar horizontal
    if not hasattr(scrollable_frame, "h_scroll") or not scrollable_frame.h_scroll:
        h_scroll = ttk.Scrollbar(scrollable_frame, orient="horizontal", command=tree.xview)
        h_scroll.pack(fill="x", side="bottom", expand=True)
        scrollable_frame.h_scroll = h_scroll
    else:
        h_scroll = scrollable_frame.h_scroll
        h_scroll.config(command=tree.xview)
        h_scroll.pack(fill="x", side="bottom", expand=True)
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
    """ Insere as linhas de um DataFrame em um Treeview.
    Parâmetros:
    - tree: Treeview onde as linhas serão inseridas.
    - df: DataFrame cujas linhas serão inseridas.
    Limpa o Treeview antes de inserir novas linhas.
    """
    for row in tree.get_children():
        tree.delete(row)
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

def sort_by_column(scrollable_frame, df, tree, col):
    """ Ordena o DataFrame por uma coluna específica e atualiza o Treeview.
    Parâmetros:
    - scrollable_frame: Frame rolável onde o Treeview está localizado.
    - df: DataFrame a ser ordenado.
    - tree: Treeview a ser atualizado.
    - col: Nome da coluna pela qual ordenar.
    Inverte a ordem de ordenação a cada clique na coluna.
    """
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