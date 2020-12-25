import pandas as pd

df = pd.read_csv('valeurs.csv')
print(df.head())
print(df['vitmot1'].tolist())
vitmot1 = []
vitmot2 = []
for vit in df['vitmot1'].tolist():
    vit = vit.replace(',', '.')
    vitmot1.append(float(vit))
for vit2 in df['votmot2'].tolist():
    vit2 = vit2.replace(',', '.')
    vitmot2.append(float(vit2))
print(vitmot1)
print(vitmot2)