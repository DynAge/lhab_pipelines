from nipype.interfaces.dcm2nii import Dcm2niix
from copy import deepcopy

class Dcm2niix_par(Dcm2niix):
    """allows to convert single par files, not possible with nipype implementation
    based on nipype 1.2.3
    """

    def _format_arg(self, opt, spec, val):
        bools = [
            'bids_format', 'merge_imgs', 'single_file', 'verbose', 'crop',
            'has_private', 'anon_bids', 'ignore_deriv', 'philips_float',
            'to_nrrd',
        ]
        if opt in bools:
            spec = deepcopy(spec)
            if val:
                spec.argstr += ' y'
            else:
                spec.argstr += ' n'
                val = True
        if opt == 'source_names':
            return spec.argstr % (val[0] or '.')
        return super(Dcm2niix, self)._format_arg(opt, spec, val)

