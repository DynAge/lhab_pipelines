from pathlib import Path
import pandas as pd

mapping = pd.read_csv("/Volumes/lhab_raw/conversion_info/LHAB_v2.0.0/PRIVATE/parrec_mapping.tsv", sep="\t")
mapping["from"] = mapping["from"].str.split("/").str[-1]
mapping["to"] = mapping["to"].str.split("/").str[-1]
mapping.rename(columns={"from": "file"}, inplace=True)
p = Path("/Volumes/lhab_raw/conversion_info/LHAB_v2.0.0/PRIVATE/acq_time_PRIVATE")

l = list(p.glob("*.tsv"))
dfs = []
for f in l:
    dfs.append(pd.read_csv(f, sep="\t"))
df = pd.concat(dfs)

df = pd.merge(df, mapping, how="left", on="file")
df["subject"] = df.to.str.split("_").str[0].str.replace("sub-", "")
df["session"] = df.to.str.split("_").str[1].str.replace("ses-", "")

df.to_csv("/Volumes/lhab_raw/conversion_info/LHAB_v2.0.0/PRIVATE/acq_time.tsv", sep="\t")
