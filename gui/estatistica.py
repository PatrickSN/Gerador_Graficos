import numpy as np
import statsmodels.api as sm
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.multicomp import pairwise_tukeyhsd, MultiComparison
from statsmodels.formula.api import ols
from scipy.stats import ttest_ind


class Estatiscas:
    def __init__(self, data: pd.DataFrame, group_col: str, fator_col: str, response_col: str, control: str, alpha=0.05):
        self.data = data
        self.group_col = group_col
        self.fator_col = fator_col if fator_col else None
        self.response_col = response_col
        self.control = control
        self.alpha = alpha

    def run_t_test(self):
        return run_t_test(self.data, self.group_col, self.fator_col, self.response_col)

    def run_dunnett(self):
        return run_test_dunnett(self.data, self.response_col, self.group_col, self.control, self.alpha)

    def run_tukey(self):
        return run_test_tukey(self.data, self.response_col, self.group_col, self.alpha)

    def add_significance(self, dunnett_result):
        return add_significance_dunnet(self.data, dunnett_result, self.response_col, self.group_col, self.control, self.alpha)
    
def fator_sort_key(x):
    import re
    # Tenta extrair o primeiro número da string
    match = re.search(r'[-+]?\d*\.\d+|\d+', str(x))
    if match:
        return (0, float(match.group()))
    else:
        # Se não houver número, retorna a string em minúsculo para ordenação alfabética
        return (1, str(x).lower())
    
def run_t_test(data: pd.DataFrame, group_col: str, fator_col: str, response_col: str) -> pd.DataFrame:
    """
    Para cada nível único de `fator_col`, faz um t-test entre as duas categorias de `group_col`.
    Parâmetros:
    - data: DataFrame contendo os dados.
    - group_col: Nome da coluna com os grupos (categorias).
    - fator_col: Nome da coluna com o fator (ex: 'time').
    - response_col: Nome da coluna com os dados de resposta (ex: 'value').

    Retorna um DataFrame com as colunas:
      - fator_col
      - group1, group2   (nomes das duas categorias)
      - n1, n2           (tamanhos amostrais)
      - t_stat, p_value
      - significance     ("ns", "*", "**", "***")
    """
    
    results = []

    if fator_col:
        # garante ordem consistente de tempos (se quiser custom, ajuste esta linha)
        fatores = data[fator_col].unique()
        for f in fatores:
            sub = data[data[fator_col] == f]
            groups = sub[group_col].unique()
            if len(groups) != 2:
                continue  # pula se não houver exatamente 2 grupos
            g1, g2 = groups
            v1 = sub[sub[group_col] == g1][response_col]
            v2 = sub[sub[group_col] == g2][response_col]
            t_stat, p = ttest_ind(v1, v2, equal_var=False)
            # monta notação de significância
            if p < 0.001:
                sig = '***'
            elif p < 0.01:
                sig = '**'
            elif p < 0.05:
                sig = '*'
            else:
                sig = 'ns'
            results.append({
                fator_col: f,
                'group1': g1,
                'group2': g2,
                'n1': len(v1),
                'n2': len(v2),
                't_stat': t_stat,
                'p_value': p,
                'significance': sig
            })

    else:
        # caso não tenha fator_col, faz t-test direto entre os grupos
        groups = data[group_col].unique()
        if len(groups) != 2:
            raise ValueError("Para t-test sem fator_col, deve haver exatamente 2 grupos.")
        g1, g2 = groups
        v1 = data[data[group_col] == g1][response_col]
        v2 = data[data[group_col] == g2][response_col]
        t_stat, p = ttest_ind(v1, v2, equal_var=False)
        # monta notação de significância
        if p < 0.001:
            sig = '***'
        elif p < 0.01:
            sig = '**'
        elif p < 0.05:
            sig = '*'
        else:
            sig = 'ns'
        results.append({
            group_col: 'Total',
            'group1': g1,
            'group2': g2,
            'n1': len(v1),
            'n2': len(v2),
            't_stat': t_stat,
            'p_value': p,
            'significance': sig
        })
    return pd.DataFrame(results)

def run_test_dunnett(data: pd.DataFrame, response_col:str, group_col:str, control:str, alpha: float=0.05):
    """
    Teste de Dunnett para comparações múltiplas com um grupo controle.
    Parâmetros:
    - data: DataFrame contendo os dados.
    - response_col: Nome da coluna com os dados de resposta.
    - group_col: Nome da coluna com os grupos.
    - control: Nome do grupo controle (ex: 'Col-0').
    - alpha: Nível de significância (default é 0.05).
    Retorna:
    - DataFrame com os resultados do teste de Dunnett, filtrando apenas as comparações com o grupo controle.
    """
    # Convertendo a coluna de grupos para categórica
    data[group_col] = pd.Categorical(data[group_col], data[group_col].dropna().unique().tolist(), ordered=True)

    # 1) roda o Tukey
    tukey = pairwise_tukeyhsd(data[response_col], data[group_col], alpha=alpha)

    # 2) converte a tabela de resultados em DataFrame
    res = tukey._results_table.data
    cols = res[0]
    df_res = pd.DataFrame(res[1:], columns=cols)
    

    # 3) filtra apenas as comparações com Col-0
    mask = (df_res['group1'] == control) | (df_res['group2'] == control)
    results = df_res[mask].copy()
    
    return results, data[group_col].dropna().unique().tolist()

def run_test_tukey(data: pd.DataFrame, response_col:str, group_col:str, alpha: float=0.05):
    """
    Teste de Tukey para comparações múltiplas entre grupos.
    Parâmetros:
    - data: DataFrame contendo os dados.
    - response_col: Nome da coluna com os dados de resposta.
    - group_col: Nome da coluna com os grupos.
    - alpha: Nível de significância (default é 0.05).
    Retorna:
    - DataFrame com os resultados do teste de Tukey.
    """
    # Convertendo a coluna de grupos para categórica
    data[group_col] = pd.Categorical(data[group_col], ordered=True)

    # 1) roda o Tukey
    tukey = pairwise_tukeyhsd(data[response_col], data[group_col], alpha=alpha)

    # 2) converte a tabela de resultados em DataFrame
    res = tukey._results_table.data
    cols = res[0]
    df_res = pd.DataFrame(res[1:], columns=cols)

    return df_res

def run_test_tukey_anova(df: pd.DataFrame, col_trat: str, col_val: str, alpha=0.05):    
    # ANOVA
    modelo = ols(f'{col_val} ~ C({col_trat})', data=df).fit()
    anova = sm.stats.anova_lm(modelo, typ=2)

    # Teste de Tukey
    mc = MultiComparison(df[col_val], df[col_trat])
    tukey_result = mc.tukeyhsd(alpha=alpha)
    results = pd.DataFrame(data=tukey_result._results_table.data[1:], columns=tukey_result._results_table.data[0])



    # Função robusta para atribuição das letras de significância (CLD)
    def tukey_letters(mc, tukey_result):
        groups = list(mc.groupsunique)
        n = len(groups)

        # Cria grafo onde arestas representam "sem diferença significativa"
        G = nx.Graph()
        G.add_nodes_from(groups)

        idx = 0
        for i in range(n):
            for j in range(i+1, n):
                g1, g2 = groups[i], groups[j]
                if not tukey_result.reject[idx]:  # Sem diferença -> adiciona aresta
                    G.add_edge(g1, g2)
                idx += 1

        # Cada componente conexo do grafo pode compartilhar uma letra
        cliques = list(nx.find_cliques(G))

        # Algoritmo de atribuição de letras
        letters_dict = {g: '' for g in groups}
        letra_ord = iter("abcdefghijklmnopqrstuvwxyz")

        for clique in cliques:
            letra = next(letra_ord)
            for grupo in clique:
                letters_dict[grupo] += letra

        return letters_dict

    # Gera letras para os tratamentos
    letters_dict = tukey_letters(mc, tukey_result)

    # Calcula média e erro padrão
    media = df.groupby(col_trat)[col_val].mean()
    erro = df.groupby(col_trat)[col_val].sem()

    # Ordena pelo tratamento para plotar corretamente
    media = media.sort_index()
    erro = erro.reindex(media.index)

    # Letras para cada tratamento na ordem certa
    letras = [letters_dict[t] for t in media.index]

    return results, media, erro, letras


def add_significance_dunnet(data: pd.DataFrame, dunnett_result, response_col:str, group_col:str, control:str, alpha: float=0.05):
    """    Adiciona estatísticas resumidas e significância aos resultados do teste de Dunnett.
    Parâmetros:
    - data: DataFrame contendo os dados originais.
    - dunnett_result: DataFrame com os resultados do teste de Dunnett.
    - response_col: Nome da coluna com os dados de resposta.
    - group_col: Nome da coluna com os grupos.
    - control: Nome do grupo controle (ex: 'Col-0').
    - alpha: Nível de significância (default é 0.05).
    Retorna:
    - DataFrame com as estatísticas resumidas e significância.
    """
    # Calcular estatísticas resumidas
    summary_stats = data.groupby(group_col, observed=False)[response_col].agg(['mean', 'std', 'count']).reset_index()
    summary_stats['SE'] = summary_stats['std'] / np.sqrt(summary_stats['count'])

    significance = []
    p_val = []
    for group in summary_stats[group_col]:
        if group == control:
            significance.append("")
            p_val.append(np.nan)
        else:
            try:
                pval = dunnett_result.loc[(dunnett_result['group1'] == control) & 
                                        (dunnett_result['group2'] == group), 'p-adj'].values[0]
                
                sig = "*" if pval < alpha else ""
            except:
                pval = np.nan
                sig = ""
            significance.append(sig)
            p_val.append(float(pval))
    
    summary_stats['significance'] = significance
    summary_stats['p_val'] = p_val
    summary_stats['p_val'] = summary_stats['p_val'].round(4) 
    return summary_stats[[group_col, 'mean', 'SE', 'p_val', 'significance']]

def add_significance_tukey(tukey_result, alpha: float=0.05):
    """
    Adiciona uma coluna de significância ao resultado do teste de Tukey.
    Parâmetros:
    - tukey_result: DataFrame com os resultados do teste de Tukey.
    - alpha: Nível de significância.
    Retorna:
    - DataFrame com coluna 'significance' indicando se p-adj < alpha.
    """
    tukey_result = tukey_result.copy()
    tukey_result['significance'] = tukey_result['p-adj'].apply(lambda p: "*" if p < alpha else "")
    return tukey_result

def add_significance_ttest(data: pd.DataFrame, t_test_result: pd.DataFrame, response_col: str, group_col: str, fator_col: str, alpha: float = 0.05):
    """
    Retorna estatísticas resumidas e significância no padrão Dunnett para t-test.
    """
    # Estatísticas resumidas
    summary_stats = data.groupby([fator_col, group_col], observed=False)[response_col].agg(['mean', 'std', 'count']).reset_index()
    summary_stats['SE'] = summary_stats['std'] / np.sqrt(summary_stats['count'])

    p_val = t_test_result.set_index(fator_col)['p_value'].to_dict()
    significance = []
    for f in summary_stats[fator_col]:
        if f in p_val:
            p = p_val[f]
            if p < alpha:
                significance.append("*")
            else:
                significance.append("")
        else:
            significance.append("")

    summary_stats['significance'] = significance

    return summary_stats[[fator_col, group_col, 'mean', 'SE', 'significance']], data[fator_col].dropna().unique().tolist()


if __name__ == "__main__":
    """
    file_path = "L:/Projetos/Lab/Programas/R/Dados/supplementary_review.xlsx"
    data = pd.read_excel(file_path, sheet_name="fig1a")
    
    
    results, order = run_test_dunnett(data, response_col='value', group_col='name', control='Col-0')
    print("\nResultados do teste de Dunnett:")
    print(results)
    summary_stats = add_significance_dunnet(data, results, response_col='value', group_col='name', control='Col-0')
    print("Estatísticas resumidas com significância Dunnett: ")
    print(summary_stats)

    results_tukey = run_test_tukey(data, response_col='value', group_col='name')
    print("\nResultados do teste de Tukey:")
    print(results_tukey)
    summary_stats_tukey = add_significance_tukey(results_tukey, alpha=0.05)
    print("Estatísticas resumidas com significância Tukey:")
    print(summary_stats_tukey)"""
    file_path = "L:/Projetos/Lab/Projetos/Gerador_Graficos/exemplos.xlsx"
    data_tukey = pd.read_excel(file_path, sheet_name="Tukey")
    re, media, erro, letras = run_test_tukey_anova(data_tukey, "genotype", "expression")
    
    ordens = sorted(data_tukey["genotype"].unique(), key=fator_sort_key)
    print(media.index[0])

    plot_df = pd.DataFrame({
                'Tratamento': media.index,
                'Média': media.values,
                'Erro': erro.values,
                'Letra': letras
            })
    dpi = 300
    def pixel_for_point(px: float, DPI: int):
        pt = px * 72 / DPI
        return pt
    
    plt.figure(figsize=(3,3), dpi=300)
    ax = plt.gca()

    # Gráfico de barras com erro padrão usando seaborn
    sns.barplot(
        data=plot_df,
        x='Tratamento',
        y='Média',
        errorbar='se',
        yerr=plot_df['Erro'],
        capsize=0.2,
        color='lightblue',
        ax=ax
    )

    # Adiciona barras de erro manualmente
    for i, row in plot_df.iterrows():
        ax.errorbar(
            x=i,
            y=row['Média'],
            yerr=row['Erro'],
            fmt='none',
            c='black',
            capsize = 5,
            linewidth=0.2
        )

    # Adiciona letras acima das barras
    for i, row in plot_df.iterrows():
        ax.text(i, row['Média'] + max(plot_df['Erro'])*1.1, row['Letra'],
                ha='center', va='bottom', fontsize=10)


    # Pontos individuais
    sns.stripplot(x="genotype", y="expression", data=data_tukey, hue="genotype", jitter=0.1, size=1, ax=ax, legend=False, palette='dark:black')

    plt.tight_layout()
    plt.savefig("_tukey.tiff",format="tiff", dpi=300)
    plt.show()

    """
    data = pd.read_excel(file_path, sheet_name="fig7c")
    print("\nResultados do teste t:")
    results_test_t, order = run_t_test(data, group_col='name', fator_col='time', response_col='value')
    print(results_test_t)
    summary_stats_t = add_significance_ttest(data, results_test_t, response_col='value', group_col='name', fator_col='time')
    print("Estatísticas resumidas com significância T-test:")
    print(summary_stats_t)

    file_path = "dataframe.xlsx"
    df = pd.read_excel(file_path, sheet_name="test_t_puro")
    print("\nResultados do teste t puro:")
    results_test_t_puro = run_t_test(df, group_col='Treatment', fator_col=None, response_col='Values')
    print(results_test_t_puro)
    summary_stats_t_puro = add_significance_ttest(df, results_test_t, response_col='value', group_col='name', fator_col=None)
    print("Estatísticas resumidas com significância T-test-puro:")
    print(summary_stats_t)"""


