"""

|-- T1
|   `-- 01_noIF
|       `-- lhab_xxxx_t1_raw
|           |-- lhab_xxxx_2dflair_T1.par
|           |-- lhab_xxxx_2dflair_T1.rec
...
|-- T2
|   `-- 01_noIF
|       `-- lhab_xxxx_t2_raw
|           |-- lhab_xxxx_2dflair_T2.par
|           |-- lhab_xxxx_2dflair_T2.rec
"""

import os, argparse
from pathlib import Path

from lhab_pipelines.nii_conversion.conversion import run_conversion
from lhab_pipelines.utils import read_tsv
from lhab_pipelines.nii_conversion.config import get_info_list_v2, dataset_description_v2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LHAB raw to nifti conversion. \nBIDS-Apps compatiple arguments.'
                                                 "\nexample:\n python run_nii_conversion.py /data/raw /data/ participant "
                                                 "--no-public_output --participant_label lhab_1c")
    parser.add_argument('raw_dir', help='The directory with the RAW input dataset.')
    parser.add_argument('output_base_dir', help='The directory where the output files should be stored.')
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

    do_deface = True if args.public_output else False
    info_list_v2 = get_info_list_v2(do_deface)

    ###
    if args.participant_label:
        old_sub_id_list = [s.strip() for s in args.participant_label]
    else:
        old_sub_id_list = read_tsv(args.subject_list_file, no_header=True)[0].tolist()

    run_conversion(args.raw_dir, args.output_base_dir, args.analysis_level, args.info_out_dir, old_sub_id_list,
                   args.session_label, args.public_output, args.use_new_ids, args.ds_version, info_list_v2,
                   dataset_description_v2, args.new_id_lut_file, args.bvecs_from_scanner_file, args.tp6_raw_lut,
                   args.dry_run, args.demo_file)

    # bids validator
    private_str = "_PRIVATE" if not (args.public_output and args.use_new_ids) else ""
    output_dir = Path(args.output_base_dir) / f"LHAB_{args.ds_version}{private_str}" / "sourcedata"

    print("X" * 20 + "\nRuning BIDS validator")
    os.system("bids-validator %s" % output_dir)

    print("\n\n\n\nDONE.\nConverted %d subjects." % len(old_sub_id_list))
    print(old_sub_id_list)
