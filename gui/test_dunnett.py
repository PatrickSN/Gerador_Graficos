import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import MultiComparison

def dunnett_test(data, treatments_levels, factors_levels ):
    data["Treatments"] = pd.Categorical(data["Treatments"], categories=treatments_levels, ordered=True)
    data["Factors"] = pd.Categorical(data["Factors"], categories=factors_levels, ordered=True)

    summary_data = (
        data.groupby(["Treatments", "Factors"])
        .agg(mean_value=("value", "mean"),
            sd_value=("value", "std"),
            se_value=("value", lambda x: x.std() / np.sqrt(len(x))))
        .reset_index()
    )

    significance_data = add_significance(data, "Treatments", "Factors", "value")

    summary_data = summary_data.merge(significance_data, on=["Treatments", "Factors"], how="left")


def add_significance(df, group_col, Factors_col, value_col, control_Factors="H2O", alpha=0.05):
    significance_rows = []
    for name in df[group_col].unique():
        sub = df[df[group_col] == name]
        control = sub[sub[Factors_col] == control_Factors][value_col]
        for time in df[Factors_col].cat.categories:
            if time == control_Factors:
                significance_rows.append({"Treatments": name, "Factors": time, "significance": ""})
            else:
                test = sub[sub[Factors_col] == time][value_col]
                if len(control) > 0 and len(test) > 0:
                    t_stat, p_val = stats.ttest_ind(test, control, equal_var=False)
                    significance_rows.append({
                        "Treatments": name,
                        "Factors": time,
                        "significance": "*" if p_val < alpha else ""
                    })
                else:
                    significance_rows.append({"Treatments": name, "Factors": time, "significance": ""})
    return pd.DataFrame(significance_rows)

def build_dunnett_test(data, title="", subtitle="", eixoX="", eixoY=""):
    pass