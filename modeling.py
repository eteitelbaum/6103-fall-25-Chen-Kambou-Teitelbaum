import pandas as pd
data = pd.read_parquet("data/flfp_dataset.parquet")  
print(data.head())
