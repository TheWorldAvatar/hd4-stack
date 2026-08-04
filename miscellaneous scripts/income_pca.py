import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

fontsize = 14

income_cols = [
    "Below_1_000",
    "1_000_1_999",
    "2_000_2_999",
    "3_000_3_999",
    "4_000_4_999",
    "5_000_5_999",
    "6_000_6_999",
    "7_000_7_999",
    "8_000_8_999",
    "9_000_9_999",
    "10_000_10_999",
    "11_000_11_999",
    "12_000_12_999",
    "13_000_13_999",
    "14_000_14_999",
    "15_000_17_499",
    "17_500_19_999",
    "20_000andOver"
]

income_list = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
               10000, 11000, 12000, 13000, 14000, 15000, 17500, 20000, 22500]

df = pd.read_csv(
    'income data/ResidentHouseholdsbyPlanningAreaofResidenceandMonthlyHouseholdIncomefromWorkCensusOfPopulation2020.csv')
df = df.set_index("Area")
df.index.name = "area"
X = df[income_cols].copy()

X = X.div(X.sum(axis=1), axis=0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)

pcs = pca.fit_transform(X_scaled)

df["pc1"] = pcs[:, 0]
df["pc2"] = pcs[:, 1]

pc_df = pd.DataFrame(
    pcs,
    index=df.index,   # <-- area labels
    columns=["pc1", "pc2"]
)
pc_df.to_csv("income data/pca_output.csv", index=True)
