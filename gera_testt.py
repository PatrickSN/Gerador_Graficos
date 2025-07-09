import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from gui.estatistica import run_t_test

def fator_sort_key(x):
        # Tenta extrair o primeiro número da string
        match = re.search(r'[-+]?\d*\.\d+|\d+', str(x))
        if match:
            return float(match.group())
        else:
            # Se não houver número, retorna a string em minúsculo para ordenação alfabética
            return str(x).lower()

# Carrega os dados
data = pd.read_excel("test-t.xlsx")

# Executa o t-test agrupado por tempo
result = run_t_test(data, group_col="name", fator_col="time", response_col="value")

# Calcula média e erro padrão (SE) para cada grupo por tempo
estatisticas = data.groupby(["time", "name"], observed=False)["value"].agg(['mean', 'std', 'count']).reset_index()
estatisticas['SE'] = estatisticas['std'] / np.sqrt(estatisticas['count'])

# Junta com os resultados do t-test para obter a significância
sig_map = result.set_index("time")["significance"].to_dict()
print("Significância por tempo:", sig_map)

# Estilo
fig, ax = plt.subplots(figsize=(8, 6))

# Gráfico de barras
ordem_tempos = sorted(estatisticas['time'].unique(), key=fator_sort_key)
sns.barplot(data=estatisticas, x="time", y="mean", hue="name", ax=ax, capsize=.1, palette="Set2", order=ordem_tempos)
"""
# Adiciona pontos individuais dos dados originais
sns.stripplot(
    data=data,
    x="time",
    y="value",
    hue="name",
    dodge=True,
    order=ordem_tempos,
    palette="Set2",
    ax=ax,
    size=5,
    linewidth=0.5,
    edgecolor="gray"
)

# Para evitar legenda duplicada
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[:len(names)], labels[:len(names)], loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=2, frameon=False)"""

# busca a maior media para ajustar o limite do eixo y
y_max = estatisticas['mean'].max()
ax.set_ylim(0, y_max * 1.2)

# Adiciona barras de erro e asteriscos
names = estatisticas['name'].unique()

for i, row in estatisticas.iterrows():
    tempo = row['time']
    grupo = row['name']
    media = row['mean']
    erro = row['SE']
    idx_tempo = ordem_tempos.index(tempo)
    deslocamento = -0.2 if grupo == names[0] else 0.2
    x_pos = idx_tempo + deslocamento
    ax.errorbar(x=x_pos, y=media, yerr=erro, fmt='none', c='black', capsize=5)

    # Apenas um asterisco por tempo (acima da barra mais alta)
    """if grupo == names[1] and tempo in sig_map:
        sig = sig_map[tempo]
        if sig != 'ns':
            altura = estatisticas[(estatisticas['time'] == tempo)]["mean"].max()
            ax.text(idx_tempo, altura + 1, sig, ha='center', va='bottom', fontsize=12, fontweight='bold')"""

for tempo in ordem_tempos:
    # Verifica se há significância para esse tempo
    sig = sig_map.get(tempo, "")
    if sig and sig != 'ns':
        # Pega as posições das barras no eixo x
        idx_tempo = ordem_tempos.index(tempo)
        x0 = idx_tempo - 0.2
        x1 = idx_tempo + 0.2
        y_linha = y_max * 1.075  # ajuste a altura do traço conforme necessário

        # Desenha o traço
        ax.plot([x0, x1], [y_linha, y_linha], c='black', linewidth=1.5)
        # Adiciona o asterisco no meio do traço
        ax.text(idx_tempo, y_linha * 1.025, sig, ha='center', va='bottom', fontsize=14, fontweight='bold')

# Ajustes visuais
ax.set_ylabel("Valor médio")
ax.set_xlabel("Tempo")
ax.set_title("Teste t entre grupos por tempo")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=2,frameon=False)
plt.tight_layout()

# Salva a figura
plt.savefig("figS7a_gerada.png", dpi=300)
plt.show()
