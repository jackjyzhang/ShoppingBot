import pandas as pd

csv0 = "items.csv"
csv1 = "items_hm.csv"
out = "items_combined.csv"

if __name__ == "__main__":
    df0 = pd.read_csv(csv0, index_col=0)
    df1 = pd.read_csv(csv1, index_col=0)

    df = pd.concat([df0, df1])
    df.to_csv(out)
