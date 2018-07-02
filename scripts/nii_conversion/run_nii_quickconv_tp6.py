"""
quickly converts t1w images (no defacing...)
in pattern:     {raw_dir}/{subject}/*t1w*.par
out pattern:    {output_base_dir}/{subject}/*t1w*.nii.gz

"""
import os, argparse
from glob import glob
from nipype.interfaces.dcm2nii import Dcm2niix
from nipype.interfaces.fsl import Reorient2Std

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LHAB raw to nifti conversion. \nBIDS-Apps compatiple arguments.'
                                                 "\nexample:\n python run_nii_quickconv_tp6.py /data/raw /data/ "
                                                 "--no-public_output --participant_label lhab_1c")
    parser.add_argument('raw_dir', help='The directory with the RAW input dataset.'
                                        '\n original: bids_dir')
    parser.add_argument('output_base_dir', help='The directory where the output files '
                                                'should be stored.'
                                                '\n original: output_dir')

    parser.add_argument('--participant_label', help='The label of the participant that should be analyzed.'
                                                    'For the conversion wf this should be given as lhab_1234',
                        nargs="+")

    args = parser.parse_args()

    raw_dir = args.raw_dir
    output_dir = args.output_base_dir

    ###
    if args.participant_label:
        sub_id_list = [s.strip() for s in args.participant_label]
    else:
        os.chdir(raw_dir)
        sub_id_list = list(filter(os.path.isdir, glob("*")))
        sub_id_list.sort()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for sub_id in sub_id_list:
        subject_out_dir = os.path.join(output_dir, sub_id)
        os.makedirs(subject_out_dir, exist_ok=True)
        par_list = glob(os.path.join(raw_dir, sub_id, "*t1w*.par"))

        if not par_list:
            raise Exception("No t1w images for {}".format(sub_id))
        for par in par_list:
            out_filename = os.path.basename(par).split(".par")[0]
            full_out_path = os.path.join(subject_out_dir, out_filename + ".nii.gz")
            print(full_out_path)
            if not os.path.isfile(full_out_path):
                converter = Dcm2niix()
                converter.inputs.source_names = [par]
                converter.inputs.bids_format = True
                converter.inputs.compress = 'i'
                converter.inputs.has_private = True
                converter.inputs.output_dir = subject_out_dir
                converter.inputs.out_filename = out_filename

                print("XXXXXXX running dcm2niix command")
                print(converter.cmdline)

                converter_results = converter.run()

                reorient = Reorient2Std()
                reorient.inputs.in_file = converter_results.outputs.converted_files
                reorient.inputs.out_file = converter_results.outputs.converted_files
                reorient_results = reorient.run()

    print("\n\n\n\nDONE.\nConverted %d subjects." % len(sub_id_list))
    print(sub_id_list)
