import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf


def t_statistic(data, treatments, pvalue=0.05):
    data['Treatment'] = pd.Categorical(data['Treatment'], categories=treatments, ordered=True)
    print(data)

    # Calcular média e erro padrão para cada grupo
    summary_stats = data.groupby("Treatment")["Values"].agg(["mean", "std", "count"]).reset_index()
    summary_stats["se"] = summary_stats["std"] / np.sqrt(summary_stats["count"])

    # Realizar ANOVA
    model = smf.ols("Values ~ C(Treatment)", data=data).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print("\nANOVA:")
    print(anova_table)

    significance_dict = add_significance(data, pvalue)
    print("\nSignificância (teste t vs. controle):")
    print(significance_dict)

    # Incorporar os níveis de significância aos dados resumidos
    summary_stats["Letters"] = summary_stats["Treatment"].map(significance_dict)

# Função para calcular "significância" via teste t entre grupo controle e cada grupo
def add_significance(data, alpha, control_label="Col-0"):
    groups = data["Treatment"].unique()
    significance = {}
    control_data = data.loc[data["Treatment"] == control_label, "Values"]
    for grp in groups:
        if grp == control_label:
            significance[grp] = ""
        else:
            grp_data = data.loc[data["Treatment"] == grp, "Values"]
            # Teste t de Welch (não assume variâncias iguais)
            t_stat, p_val = stats.ttest_ind(grp_data, control_data, equal_var=False)
            significance[grp] = "*" if p_val < alpha else ""
    return significance

def build_t_test(data, title="", subtitle="", eixoX="", eixoY=""):
    pass

if __name__ == "__main__":
    # Exemplo de uso
    np.random.seed(42)
    treatments = ["Col-0", "Mutant1", "Mutant2"]
    data = pd.DataFrame({
        "Treatment": np.random.choice(treatments, size=20),
        "Values": np.random.normal(loc=10, scale=2, size=20)
    })

    t_statistic(data, treatments)