import numpy as np
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd

class Estatiscas:
    def __init__(self, data: pd.DataFrame, response_col: str, group_col: str, control: str, alpha=0.05):
        self.data = data
        self.response_col = response_col
        self.group_col = group_col
        self.control = control
        self.alpha = alpha

    def run_dunnett(self):
        return run_test_dunnett(self.data, self.response_col, self.group_col, self.control, self.alpha)

    def run_tukey(self):
        return run_test_tukey(self.data, self.response_col, self.group_col, self.alpha)

    def add_significance(self, dunnett_result):
        return add_significance(self.data, dunnett_result, self.response_col, self.group_col, self.control, self.alpha)
    
def run_test_dunnett(data, response_col:str, group_col:str, control:str, alpha=0.05):
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

def run_test_tukey(data, response_col:str, group_col:str, alpha=0.05):
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

def add_significance(data, dunnett_result, response_col:str, group_col:str, control:str, alpha=0.05):
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
    summary_stats = data.groupby(group_col)[response_col].agg(['mean', 'std', 'count']).reset_index()
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

def add_significance_tukey(tukey_result, alpha=0.05):
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


if __name__ == "__main__":
    file_path = "L:/Projetos/Lab/Programas/R/Dados/supplementary_review.xlsx"
    data = pd.read_excel(file_path, sheet_name="fig1a")

    results = run_test_dunnett(data, response_col='value', group_col='name', control='Col-0')
    print("Resultados do teste de Dunnett:")
    print(results)

    results_tukey = run_test_tukey(data, response_col='value', group_col='name')
    print("Resultados do teste de Tukey:")
    print(results_tukey)

    summary_stats = add_significance(data, results, 'value', 'name', 'Col-0')
    print("Estatísticas resumidas com significância:")
    print(summary_stats)



