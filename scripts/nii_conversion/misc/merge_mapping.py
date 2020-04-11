from pathlib import Path
import pandas as pd

p = Path("/Volumes/lhab_raw/conversion_info/LHAB_v2.0.0/PRIVATE/parrec_mapping_PRIVATE")

l = list(p.glob("*.tsv"))
dfs = []
for f in l:
    dfs.append(pd.read_csv(f, sep="\t"))
df = pd.concat(dfs)

df.to_csv("/Volumes/lhab_raw/conversion_info/LHAB_v2.0.0/PRIVATE/parrec_mapping.tsv", sep="\t", index=False)
