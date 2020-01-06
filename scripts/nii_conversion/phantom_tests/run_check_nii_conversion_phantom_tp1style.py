"""
"""

import os, argparse
from pathlib import Path

from lhab_pipelines.utils import read_tsv
from os.path import join as oj
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LHAB raw to nifti conversion. \nBIDS-Apps compatiple arguments.'
                                                 "\nexample:\n python run_nii_conversion.py /data/raw /data/ participant "
                                                 "--no-public_output --participant_label lhab_1c")
    parser.add_argument('output_base_dir', help='The directory where the output files should be stored.')
    parser.add_argument('--participant_label', help='The label of the participant that should be analyzed.'
                                                    'For the conversion wf this should be given as lhab_1234',
                        nargs="+")
    parser.add_argument('--subject_list_file', help='File with subject_ids')
    parser.add_argument('--info_out_dir', help='The directory where the misc info files are written to', required=True)
    parser.add_argument('--no-public_output',
                        help="Don't create public output.\nIf public_output: strips all info about original "
                             "subject_id, file, date \nDefault: use public_output",
                        default=True, dest="public_output", action='store_false')
    parser.add_argument('--no-use_new_ids', help="Don't use new subject ids. "
                                                 "\nDefault: Use new ids from mapping file",
                        default=True, dest="use_new_ids", action='store_false')
    parser.add_argument('--ds_version', help="Data set version (is added to output path)", default="dev")

    args = parser.parse_args()

    ###
    if args.participant_label:
        old_sub_id_list = [s.strip() for s in args.participant_label]
    else:
        old_sub_id_list = read_tsv(args.subject_list_file, no_header=True)[0].tolist()

    ## checks
    private_str = "_PRIVATE" if not (args.public_output and args.use_new_ids) else ""
    output_dir = Path(args.output_base_dir) / f"LHAB_{args.ds_version}{private_str}" / "sourcedata"

    #
    print("X" * 20 + "\nTesting if correct files are there and others are correctly deleted...")

    shouldbe_there = [
        oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp3/anat/sub-lhabX9999_ses-tp3_run-1_T1w.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.json"),
        oj(output_dir, "sub-lhabX9999/ses-tp3/anat/sub-lhabX9999_ses-tp3_run-1_T1w.json"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_acq-2D_run-1_FLAIR.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_acq-3D_run-1_FLAIR.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp3/func/sub-lhabX9999_ses-tp3_task-rest_run-1_bold.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp3/fmap/sub-lhabX9999_ses-tp3_acq-pa_run-1_bold.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.json"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.bval"),
        oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.bvec"),
        oj(output_dir, "sub-lhabX9999/ses-tp3/fmap/sub-lhabX9999_ses-tp3_acq-ap_run-1_dwi.nii.gz"),
        oj(output_dir, "sub-lhabX9999/ses-tp3/fmap/sub-lhabX9999_ses-tp3_acq-pa_run-1_dwi.nii.gz"),

        oj(args.info_out_dir, "PRIVATE/acq_time_PRIVATE/sub-lhabX9999_ses-tp1_acq_times.tsv"),
        oj(args.info_out_dir, "PRIVATE/parrec_mapping_PRIVATE/sub-lhabX9999_ses-tp1_par2nii_mapping.tsv"),
        oj(args.info_out_dir, "PRIVATE/unconverted_files/sub-lhabX9999_ses-tp1_unconverted.tsv"),
    ]

    for f in shouldbe_there:
        if not os.path.exists(f):
            raise FileNotFoundError("A file that the test should produce was missing: %s" % f)

    # check defacing is on
    f = oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.json")
    with open(f) as fi:
        j = json.load(fi)
    if not j["Defaced"]:
        raise Exception("Defacing seems to be turned off. Exit. %s" % f)

    if args.public_output:
        shouldnotbe_there = [
            oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.txt"),
            oj(output_dir, "sub-lhabX9999/par2nii_mapping.txt"),
        ]
        for f in shouldnotbe_there:
            if os.path.exists(f):
                raise FileExistsError("A file that the test should NOT produce was found: %s" % f)
    print("Everything seems to be fine!")
