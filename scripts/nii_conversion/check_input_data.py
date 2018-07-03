"""
This script
        * checks if every rec has a par
        * checks if all recs are larger than 3 MB
        * counts number of scans per subject

in pattern:     {raw_dir}/{subject}/*t1w*.par

"""
import os, argparse
import pandas as pd

from glob import glob


def classify_modality(filename):
    clf = None
    mod_search_str = {"t1w": "t1w",
                      "flair": "flair",
                      "dwi": "dti_high",
                      "dwi_fmap": "dti_nodif_",
                      "bold": "resting2000",
                      "bold_fmap": "resting_pa",
                      }
    for mod, search_str in mod_search_str.items():
        if search_str in filename:
            clf = mod
    return clf


def get_file_size_mb(file):
    return os.path.getsize(file) / 1000000.


def check_input_data(in_dir):
    small_size_thr = 3

    print("\n\n", "*" * 20)
    print("""This script 
        * checks if every rec has a par
        * checks if all recs are larger than {} MB
        * counts number of scans per subject
    """.format(small_size_thr))

    # get subjects
    os.chdir(in_dir)
    sub_id_list = list(filter(os.path.isdir, glob("*")))
    sub_id_list.sort()

    df = pd.DataFrame([])
    for subject in sub_id_list:
        search_str = os.path.join(in_dir, subject, "*.rec")
        rec_list = glob(search_str)
        rec_list.sort()

        if len(rec_list) < 1:
            raise Exception("No recs found for {}".format(subject))

        # check that rec file exists
        for rec in rec_list:
            if not os.path.isfile(rec.split(".rec")[0] + ".par"):
                raise Exception("Rec file missing for {}".format(rec))

        rec_names = [os.path.basename(p) for p in rec_list]
        df_ = pd.DataFrame({"subject": subject, "rec": rec_names, "full_path": rec_list})

        df = pd.concat((df, df_))

    df.reset_index(inplace=True, drop=True)
    df["scan"] = df.rec.apply(classify_modality)
    df["size_mb"] = df.full_path.apply(get_file_size_mb)

    if sum(df.scan.isnull()) > 0:
        print(df[df.scan.isnull()])
        raise Exception("Classification did not work reliably.")

    if df.size_mb.min() < small_size_thr:
        print(df[df.size_mb < small_size_thr])
        raise Exception("Some rec files below {} MB".format(small_size_thr))


    # reports
    tot = df.groupby(["subject"])["rec"].count().reset_index()

    print("\n\n", "*" * 20)
    print("{} subjects found".format(len(tot)))

    print("\n\n", "*" * 20)
    print("Total scan count")
    print(tot.to_string())

    print("\n\n", "*" * 20)
    print("Scan count per modality")
    scan_count = df.groupby(["subject", "scan"])[["rec"]].count().reset_index(). \
        pivot(index='subject', columns='scan', values='rec').reset_index().fillna(0)
    print(scan_count.to_string())


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='checks and counts par/rec raw data')
    parser.add_argument('in_dir', help='The directory with the RAW input dataset.'
                                       '\n original: bids_dir')
    args = parser.parse_args()

    check_input_data(args.in_dir)
