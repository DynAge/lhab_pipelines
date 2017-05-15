#!/usr/bin/env python
# -*- coding: utf-8 -*-#
# @(#) upload data to openbis
#
#
# Copyright (C) 2015, GC3, University of Zurich. All rights reserved.
#
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

__docformat__ = 'reStructuredText'
__author__ = 'Tyanko Aleksiev <tyanko.alexiev@gmail.com>'

import subprocess
import argparse
import re
import sys
import os
import json
import pybis
import logging
import getpass
import csv
from pybis import Openbis
import time

log = logging.getLogger()
log.addHandler(logging.StreamHandler())

def setup():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--add-subjects', dest='subjects', type=str,
                        help='CSV file containing the new subjects')
    parser.add_argument('-m', '--behavioral-memory', dest='bmem', type=str,
                        help='CSV file containing the behavioral memory')
    parser.add_argument('-a', '--behavioral-attention', dest='atte', type=str,
                        help='CSV file containing the behavioral attention')
    parser.add_argument('-r', '--mri-data', dest='mri', type=str,
                        help='Directory containing all mri data')
    args = parser.parse_args()
    return args 

def openbis_instance():
    s = Openbis(url='https://s3itdata.uzh.ch', verify_certificates=True)
    username = input("Enter OpenBis Username:")
    password = getpass.getpass()
    s.login(username,password)
    assert s.token is not None
    assert s.is_token_valid() is True
    return s

def main(opts, session):

    # create a list of all subjects and verify for each insert if subject is not already present
    subjects_list = {}
    for i in session.get_samples(experiment="/FLIEM/LHAB_TEST/E158", type="SUBJECT"):
        subjects_list[i.props.subject_id] = i.identifier

    if opts.subjects:
        with open(opts.subjects, 'r') as subjects_file:
            csv_file = csv.DictReader(subjects_file)
            for row in csv_file:
                if row["participant_id"] not in subjects_list:
                    sample = session.new_sample(space="FLIEM", type="SUBJECT", experiment="/FLIEM/LHAB_TEST/E158",\
                            props={"gender":row["sex"],"subject_id":row["participant_id"]})
                    sample.save()
                else: 
                    print ("Participant %s, already part of the project" % (row["participant_id"]))

    elif opts.bmem:
        with open(opts.bmem, 'r') as memory_file:
            csv_file = csv.DictReader(memory_file)
            for row in csv_file:
                sample = session.new_sample(space="FLIEM", type="SUBJECT_MEMORY", experiment="/FLIEM/LHAB_TEST/E181",\
                        parents=subjects_list.get(row["participant_id"]), props={"participant_id":row["participant_id"],\
                        "session_id":row["session_id"],"score_1":int(row["score_1"]),"score_2":int(row["score_2"])})
                sample.save()

    elif opts.mri:
        for root, subdirs, filenames in os.walk(opts.mri):
            for f in filenames:
                filename = os.path.splitext(f)[0]
                extention = os.path.splitext(f)[1]
                subject = filename.split("_")[0]
                subject_id = subject.split("-")[1]
                sample = session.new_sample(space="FLIEM", type="SUBJECT_MRI", experiment="/FLIEM/LHAB_TEST/E183",\
                        parents=subjects_list.get(subject_id), props={"subject_id":subject_id,"mri_acquisition":filename.split("_")[2],\
                        "mri_modality":filename.split("_")[4],"mri_run":filename.split("_")[1],\
                        "mri_sequence":filename.split("_")[3]})
                sample.save()
                path = os.path.abspath(os.path.join(root, f))
                print (path)
                time.sleep(5)
                print(sample.identifier)
                dataset = session.new_dataset(type="ANALYZED_DATA", experiment="/FLIEM/LHAB_TEST/E183", sample=sample.identifier, files=['./sub-lhabX0015_ses-tp1_acq-ap_run-1_dwi.bval'])
                dataset
                dataset.save()

if __name__ == "__main__":
    opts = setup()
    session = openbis_instance()
    sys.exit(main(opts, session))
