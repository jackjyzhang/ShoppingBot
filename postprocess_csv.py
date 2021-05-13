import pandas as pd

csv = "items_combined.csv"
out_csv = "items_postprocessed.csv"

if __name__ == "__main__":
    df = pd.read_csv(csv, index_col=0)
    print(f"Original length {len(df)}")
    df = df[df.duplicated(['descrption', 'brand', 'price', 'url']) == False]
    print(f"Deduplicated length {len(df)}")
    df.reset_index(drop=True, inplace=True)
    df.index.name = 'id'
    df.to_csv(out_csv)