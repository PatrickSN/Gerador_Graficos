import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

class Estatisticas:
    def __init__(self, data,
        col_treatment =  "treatment",
        col_value = "value",
        col_factors = "factors",
        order_of_treatments = [],
        pvalue = 0.05,
        control = "Col-0"
    ):
        self.data = data
        self.col_treatment = col_treatment
        self.col_value = col_value
        self.col_factors = col_factors
        self.order_of_treatments = order_of_treatments
        self.pvalue = pvalue
        self.control = control
        self.dados = {
            "col_treatment":  self.col_treatment,
            "col_value": self.col_value,
            "col_factors": self.col_factors,
            "order_of_treatments": self.order_of_treatments,
            "pvalue": self.pvalue,
            "control": self.control 
        }


    def test_t(self):
        """
        Realiza o teste t de Welch entre dois grupos.
        """
        # Converter a coluna 'name' para categórica com ordem definida
        self.data[self.col_treatment] = pd.Categorical(self.data[self.col_treatment],
                                                        categories=self.order_of_treatments,
                                                        ordered=True)
        
        summary_stats = self.data.groupby(self.col_treatment)[self.col_value].agg(["mean", "std", "count"]).reset_index()
        summary_stats["se"] = summary_stats["std"] / np.sqrt(summary_stats["count"])

        # Realizar ANOVA
        model = smf.ols(f"{self.col_value} ~ C({self.col_treatment})", data=self.data).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        print("\nANOVA:")
        print(anova_table)

        significance_dict = self.add_significance()
        print(significance_dict)
    
    def add_significance(self):
        groups = self.data[self.col_treatment].unique()
        significance = {}
        control_data = self.data.loc[self.data[self.col_treatment] == self.control, self.col_value]
        for grp in groups:
            if grp == self.control:
                significance[grp] = ""
            else:
                grp_data = self.data.loc[self.data[self.col_treatment] == grp, self.col_value]
                # Teste t de Welch (não assume variâncias iguais)
                t_stat, p_val = stats.ttest_ind(grp_data, control_data, equal_var=False)
                significance[grp] = "*" if p_val < self.pvalue else ""
        return significance




if __name__ == "__main__":
    file_path = "L:/Projetos/Lab/Programas/R/Dados/supplementary_review.xlsx"
    data = pd.read_excel(file_path, sheet_name="fig1a")

    
    
    estatisticas = Estatisticas(data, col_treatment="name",
        col_value="value", 
        order_of_treatments=["Col-0", "limyb-32", "L1", "L3", "L4"],
        pvalue=0.05, 
        control="Col-0"
    )
    
    estatisticas.test_t()