import os, argparse
from glob import glob
import pandas as pd
import subprocess
import re


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get euler number for freesurfer recon")
    parser.add_argument('fs_dir', help="freesurfer dir")
    parser.add_argument('output_dir', help="where euler numbers will be written to")
    parser.add_argument('analysis_level', help="Level of the analysis that will be performed.",
                        choices=["participant", "group"])
    parser.add_argument('--participant_label', help='The label of the participant that should be analyzed.',
                        nargs="+")
    args = parser.parse_args()

    if args.participant_label:
        fs_subjects = []
        for s in args.participant_label:
            fs_subjects += glob(os.path.join(args.fs_dir, "sub-{}*".format(s)))
    else:
        fs_subjects = glob(os.path.join(args.fs_dir, "sub-*"))

    # only use crossectional subjects (without long sessions, as they don't have a orig.nofix surface)
    fs_subjects = [s for s in fs_subjects if "long" not in s]
    fs_subjects.sort()

    raw_out_dir = os.path.join(args.output_dir, "euler_raw_files")
    if not os.path.isdir(raw_out_dir):
        os.makedirs(raw_out_dir)

    df_group = pd.DataFrame([])
    for subject_path in fs_subjects:
        subject = os.path.basename(subject_path)
        for h in ["lh", "rh"]:
            for surf in ["orig.nofix"]:
                out_filename = "{s}_{h}_{surf}_euler.csv".format(s=subject, h=h, surf=surf)
                outfile = os.path.join(raw_out_dir, out_filename)

                if args.analysis_level == "participant":
                    # participants
                    if not os.path.isfile(outfile):
                        surf_file = os.path.join(subject_path, "surf", h + "." + surf)
                        cmd = "mris_euler_number {}".format(surf_file)
                        print(cmd)
                        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE, shell=True)
                        euler_text = proc.stderr.read().decode()

                        p = re.compile(r"(-?\d+) --> (\d+) holes")
                        euler_number, n_holes = p.findall(euler_text)[0]

                        p = re.compile(r"total defect index = (\d+)")
                        total_defect_index = p.findall(euler_text)[0]

                        df = pd.DataFrame({"subject": [subject],
                                           "hemi": [h],
                                           "surf": [surf],
                                           "euler": [euler_number],
                                           "n_holes": [n_holes],
                                           "total_defect_index":[total_defect_index],
                                           "euler_text": [euler_text]
                        })

                        df = df[["subject", "hemi", "surf", "euler", "n_holes", "total_defect_index", "euler_text"]]
                        df.to_csv(outfile, index=False)

                else:
                    # group
                    df_ = pd.read_csv(outfile)
                    df_group = pd.concat((df_group, df_))

    if args.analysis_level == "group":
        df_group.to_csv(os.path.join(args.output_dir, "00_group_euler.csv"), index=False)
