import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

class test_t:
    def __init__(self, data, treatments, pvalue=0.05, control_label="Col-0"):
        self.data = data
        self.treatments = treatments
        self.pvalue = pvalue
        self.control_label = control_label

    def t_statistic(self):
        self.data['Treatment'] = pd.Categorical(self.data['Treatment'], categories=self.treatments, ordered=True)
        print(self.data)

        # Calcular média e erro padrão para cada grupo
        summary_stats = self.data.groupby("Treatment")["Values"].agg(["mean", "std", "count"]).reset_index()
        summary_stats["se"] = summary_stats["std"] / np.sqrt(summary_stats["count"])

        # Realizar ANOVA
        model = smf.ols("Values ~ C(Treatment)", data=self.data).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        print("\nANOVA:")
        print(anova_table)

        significance_dict = self.add_significance(self.data, self.pvalue)
        print("\nSignificância (teste t vs. controle):")
        print(significance_dict)

        # Incorporar os níveis de significância aos dados resumidos
        summary_stats["Letters"] = summary_stats["Treatment"].map(significance_dict)

    # Função para calcular "significância" via teste t entre grupo controle e cada grupo
    def add_significance(self, data, alpha):
        groups = data["Treatment"].unique()
        significance = {}
        control_data = data.loc[data["Treatment"] == self.control_label, "Values"]
        for grp in groups:
            if grp == self.control_label:
                significance[grp] = ""
            else:
                grp_data = data.loc[data["Treatment"] == grp, "Values"]
                # Teste t de Welch (não assume variâncias iguais)
                t_stat, p_val = stats.ttest_ind(grp_data, control_data, equal_var=False)
                significance[grp] = "*" if p_val < alpha else ""
        return significance

    def build_t_test(data, title="", subtitle="", eixoX="", eixoY=""):
        return        
        # Resumo estatístico
        summary = data.groupby("name").agg(
            Mean=("value", "mean"),
            SE=("value", lambda x: x.std() / np.sqrt(len(x)))
        ).reset_index()
        summary["Letters"] = summary["name"].map(sig_dict)
        # Plotar
        plt.figure(figsize=(6, 6))
        sns.barplot(data=data, x="name", y="value", estimator=np.mean, ci=None, order=order_of_treatments, color="blue", alpha=0.8)
        sns.stripplot(data=data, x="name", y="value", order=order_of_treatments, color="black", size=4, jitter=0.15)
        plt.errorbar(summary["name"], summary["Mean"], yerr=summary["SE"], fmt='none', color='black', capsize=5)

        # Adicionar texto de significância
        for i, row in summary.iterrows():
            plt.text(i, row["Mean"] + row["SE"] + 2, row["Letters"], ha='center', va='bottom', fontsize=12)

        plt.xticks(ticks=range(len(new_labels)), labels=new_labels, rotation=45, ha='right')
        plt.ylabel("mRNA/Actin")
        plt.title("LIMYB")
        sns.despine()
        plt.tight_layout()

        # Salvar imagem
        plt.savefig("L:/Programas/R/figuras tiff/imagens/figS1a_tiff_py.tiff", dpi=800)
        plt.show()

if __name__ == "__main__":
    # Exemplo de uso
    
    treatments = ["Col-0", "limyb-32", "L1", "L3", "L4"]
    file_path = "L:/Projetos/Lab/Programas/R/Dados/supplementary_review.xlsx"
    data = pd.read_excel(file_path, sheet_name="fig1a")
    test = test_t(data, treatments, pvalue=0.05)
    test.t_statistic()