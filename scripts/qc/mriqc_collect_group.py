import os
from glob import glob
import pandas as pd
import json
import argparse
import shutil


def read_json(filename):
    with open(filename) as fi:
        return json.load(fi)


def collect_subject_files(in_dir, modality):
    df = pd.DataFrame([])

    search_str = "sub-*" + modality + ".json"
    g = glob(os.path.join(in_dir, search_str))
    if g:
        for f in g:
            parts = os.path.basename(f).split("_")
            if modality == "bold":
                sub, ses, task, run, _ = [p.split("-")[-1] for p in parts]
            else:
                sub, ses, run, _ = [p.split("-")[-1] for p in parts]
            in_data = read_json(f)
            _ = in_data.pop("metadata")
            df_ = pd.DataFrame(in_data, index=[sub])
            df_["session_id"] = ses
            df_["run_id"] = run
            df_.index.name = "subject_id"
            df = df.append(df_)
        return df
    else:
        print("No data found for %s in %s" % (modality, in_dir))
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('base_dir', help="Directory containing mriqc output")
    args = parser.parse_args()

    out_dir = os.path.join(args.base_dir, "group_derivates")
    if os.path.isdir(out_dir):
        print("deleting old output group data")
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)

    in_dir = os.path.join(args.base_dir, "derivatives")
    for modality in ["T1w", "bold"]:
        df = collect_subject_files(in_dir, modality)
        out_filename = os.path.join(out_dir, "mriqc_group_%s.tsv" % modality, )
        df.to_csv(out_filename, sep="\t")
        print(modality, out_filename)
