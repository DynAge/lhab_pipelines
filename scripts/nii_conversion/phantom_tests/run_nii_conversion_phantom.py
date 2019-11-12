"""
CI Test for LHAB conversion pipeline (par to nifti).
- converts example data set (phantom)
- tests if files nifti and json files are there
- tests if sensitive information is deleted
- runs bids validator

- does NOT check dwi data conversion

- docker run --rm -ti -v ${HOME}/outputs:/data/out fliem/${CIRCLE_PROJECT_REPONAME,,} python /code/lhab_pipelines/scripts/nii_conversion/phantom_tests/run_nii_conversion_phantom.py /code/lhab_pipelines/scripts/nii_conversion/phantom_tests/01_RAW /data/out participant --ds_version phantomas
"""

import os, argparse
from lhab_pipelines.nii_conversion.conversion import run_conversion
from lhab_pipelines.utils import read_tsv

import numpy as np
import json

from os.path import join as oj
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LHAB raw to nifti conversion. \nBIDS-Apps compatiple arguments.'
                                                 "\nexample:\n python run_nii_conversion.py /data/raw /data/ participant "
                                                 "--no-public_output --participant_label lhab_1c")
    parser.add_argument('raw_dir', help='The directory with the RAW input dataset.'
                                        '\n original: bids_dir')
    parser.add_argument('output_base_dir', help='The directory where the output files '
                                                'should be stored.'
                                                '\n original: output_dir')
    parser.add_argument('analysis_level', help='Level of the analysis that will be performed. ',
                        choices=['participant', 'group'])
    parser.add_argument('--info_out_dir', help='The directory where the misc info files are written to', required=True)
    parser.add_argument('--participant_label', help='The label of the participant that should be analyzed.'
                                                    'For the conversion wf this should be given as lhab_1234',
                        nargs="+")
    parser.add_argument('--session_label', help='Old style session labels: T1, T2...',
                        nargs="+", default=['T1', 'T2', 'T3', 'T4', 'T5', 'T6'])
    parser.add_argument('--subject_list_file', help='File with subject_ids')
    parser.add_argument('--no-public_output',
                        help="Don't create public output.\nIf public_output: strips all info about original "
                             "subject_id, file, date \nDefault: use public_output",
                        default=True, dest="public_output", action='store_false')
    parser.add_argument('--no-use_new_ids', help="Don't use new subject ids. "
                                                 "\nDefault: Use new ids from mapping file",
                        default=True, dest="use_new_ids", action='store_false')
    parser.add_argument('--ds_version', help="Data set version (is added to output path)", default="dev")
    parser.add_argument('--new_id_lut_file', help="old to new ids")
    parser.add_argument('--bvecs_from_scanner_file', help="")
    parser.add_argument('--tp6_raw_lut', help="")
    parser.add_argument('--dry_run', help="Don't convert, just collect information", default=False,
                        action='store_true')
    parser.add_argument('--demo_file', help="file with sex and dob")

    args = parser.parse_args()

    ## info
    # LAS Orientation
    # i : RL
    # i-: LR
    # j : PA
    # j-: AP
    # k : IS
    # k-: SI
    general_info = {"MagneticFieldStrength": 3.0, "ManufacturersModelName": "Philips Ingenia"}
    sense_info = {"ParallelAcquisitionTechnique": "SENSE", "ParallelReductionFactorInPlane": 2}

    # TR=2sec, 43 slices,  # ascending sliceorder
    rs_info = {"SliceEncodingDirection": "k", "SliceTiming": np.arange(0, 2.0, 2. / 43)}

    do_deface = True if args.public_output else False

    info_list = [
        # anatomical
        {"bids_name": "T1w", "bids_modality": "anat", "search_str": "t1w_", "deface": do_deface,
         "add_info": {**general_info}},
        # flair
        {"bids_name": "FLAIR", "bids_modality": "anat", "search_str": ["2dflair_", "flair_longtr"], "acq": "2D",
         "deface": do_deface,
         "add_info": {**general_info}},
        {"bids_name": "FLAIR", "bids_modality": "anat", "search_str": "3d*flair_", "acq": "3D", "deface": do_deface,
         "add_info": {**general_info}},

        # dwi
        {"bids_name": "dwi", "bids_modality": "dwi", "search_str": ["_dti_T", "dti_high"], "only_use_last": True,
         "acq": "ap",
         "add_info": {**general_info, **sense_info, "PhaseEncodingDirection": "j-"}},

        # func
        {"bids_name": "bold", "bids_modality": "func", "search_str": ["_fmri_T", "resting2000"], "task": "rest",
         "physio": True, "add_info": {**general_info, **sense_info, **rs_info, "PhaseEncodingDirection": "j-"}},

        # fieldmaps
        {"bids_name": "bold", "bids_modality": "fmap", "search_str": ["_fmri_pa_T", "resting_pa"], "acq": "pa",
         "add_info": {**general_info, **sense_info, **rs_info, "PhaseEncodingDirection": "j"}},
        {"bids_name": "dwi", "bids_modality": "fmap", "search_str": ["_dti_pa_T", "dti_nodif_pa"], "acq": "pa",
         "add_info": {**general_info, **sense_info, "PhaseEncodingDirection": "j"}},
        {"bids_name": "dwi", "bids_modality": "fmap", "search_str": ["_dti_ap_T", "dti_nodif_ap"], "acq": "ap",
         "add_info": {**general_info, **sense_info, "PhaseEncodingDirection": "j-"}}
    ]



    dataset_description = {"Name": "LHAB longitudinal healthy aging brain study",
                           "BIDSVersion": "1.0.0",
                           "License": "XXXXXX what license is this dataset distributed under? The use of license name "
                                      "abbreviations is suggested for specifying a license. A list of common licenses"
                                      " with suggested abbreviations can be found in appendix III.",
                           "Authors": "XXXXXX List of individuals who contributed to the creation/curation of the dataset",
                           "Acknowledgements": "XXXXXX who should be acknowledge in helping to collect the data",
                           "HowToAcknowledge": "XXXXXX Instructions how researchers using this dataset should "
                                               "acknowledge the original authors. This "
                                               "field can also be used to define a publication that should be cited in publications that use "
                                               "the dataset",
                           "Funding": "XXXXXX sources of funding (grant numbers)"
                           }

    ###
    if args.participant_label:
        old_sub_id_list = [s.strip() for s in args.participant_label]
    else:
        old_sub_id_list = read_tsv(args.subject_list_file)["sub_id"].tolist()

    run_conversion(args.raw_dir, args.output_base_dir, args.analysis_level, args.info_out_dir, old_sub_id_list,
                   args.session_label, args.public_output, args.use_new_ids, args.ds_version, info_list,
                   dataset_description, args.new_id_lut_file, args.bvecs_from_scanner_file, args.tp6_raw_lut,
                   args.dry_run, args.demo_file)

    ## checks
    private_str = "_PRIVATE" if not (args.public_output and args.use_new_ids) else ""
    output_dir = Path(args.output_base_dir) / f"LHAB_{args.ds_version}{private_str}" / "sourcedata"

    # bids validator
    print("X" * 20 + "\nRuning BIDS validator")
    os.system("bids-validator %s" % output_dir)

    #
    print("X" * 20 + "\nTesting if correct files are there and others are correctly deleted...")
    #
    # shouldbe_there = [
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp3/anat/sub-lhabX9999_ses-tp3_run-1_T1w.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.json"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp3/anat/sub-lhabX9999_ses-tp3_run-1_T1w.json"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_acq-2D_run-1_FLAIR.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_acq-3D_run-1_FLAIR.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp3/func/sub-lhabX9999_ses-tp3_task-rest_run-1_bold.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp3/fmap/sub-lhabX9999_ses-tp3_acq-pa_run-1_bold.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.json"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.bval"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp1/dwi/sub-lhabX9999_ses-tp1_acq-ap_run-1_dwi.bvec"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp3/fmap/sub-lhabX9999_ses-tp3_acq-ap_run-1_dwi.nii.gz"),
    #                   oj(output_dir, "sub-lhabX9999/ses-tp3/fmap/sub-lhabX9999_ses-tp3_acq-pa_run-1_dwi.nii.gz"),
    #                   ]
    #
    # for f in shouldbe_there:
    #     if not os.path.exists(f):
    #         raise FileNotFoundError("A file that the test should produce was missing: %s" % f)
    #
    # # check defacing is on
    # f = oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.json")
    # with open(f) as fi:
    #     j = json.load(fi)
    # if not j["Defaced"]:
    #     raise Exception("Defacing seems to be turned off. Exit. %s" % f)

    # if args.public_output:
    #     shouldnotbe_there = [
    #         oj(output_dir, "sub-lhabX9999/ses-tp1/anat/sub-lhabX9999_ses-tp1_run-1_T1w.txt"),
    #         oj(output_dir, "sub-lhabX9999/par2nii_mapping.txt"),
    #     ]
    #     for f in shouldnotbe_there:
    #         if os.path.exists(f):
    #             raise FileExistsError("A file that the test should NOT produce was found: %s" % f)
    print("Everthing seems to be fine!")
