#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
# © 2018 The Board of Trustees of the Leland Stanford Junior University
# Nathaniel Watson
# nathankw@stanford.edu
# 2018-10-23
###

"""
Use this script when there are records on the IGVF Portal for which you know their aliases, but
want to retreive their DACC accessions. This will only work if the record aliases you provided are
registered with the records on the IGVF Portal. Note that if the particular DACC profile at hand
doesn't support the accession property, then the uuid will be returned. 
"""

import argparse
import igvf_utils
from igvf_utils.connection import Connection
from igvf_utils.parent_argparser import igvf_login_parser
# igvf_login_parser contains the arguments needed for logging in to the
# IGVF Portal, including which env.


def get_parser():
    parser = argparse.ArgumentParser(
        parents=[igvf_login_parser],
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--infile", required=True, help="""
        Input file containing record aliases (one per line). Empty lines and lines beginning with 
        a '#' will be ignored.""")

    parser.add_argument("-o", "--outfile", required=True, help="""
        The output file, which is in the same as the input file except for the addition of the
        tab-delimited columns - one for each alias.
  """)
    parser.add_argument("-l", "--submitter-lab", help="""
        The submitting lab alias prefix (i.e. michael-snyder) for these aliases.  No need to set this
        option if your input file's aliases are already prefixed with the submitting lab. Furthermore,
        for any aliases lacking the prefix, the default will be taken from the IGVF_LAB environment
        variable if not set here.""")
    return parser


def main():
    """Program
    """
    parser = get_parser()
    args = parser.parse_args()
    infile = args.infile
    outfile = args.outfile
    igvf_mode = args.igvf_mode
    submitter_lab = args.submitter_lab
    if not submitter_lab:
        submitter_lab = igvf_utils.LAB_PREFIX.rstrip(":")

    conn = Connection(igvf_mode=igvf_mode)

    fh = open(infile, 'r')
    fout = open(outfile, 'w')
    for line in fh:
        alias = line.strip("\n").split("\t")[0]
        if not alias or alias.startswith("#"):
            fout.write(line)
            continue
        alias_lab_prefix = alias.split(":", 1)
        try:
            lab_prefix, alias_name = alias.split(":", 1)
        except ValueError:
            if not submitter_lab:
                raise Exception("Unknown submitting lab name for alias {}. See description for --submitter-lab argument.".format(alias))
            alias = submitter_lab + ":" + alias
        rec = conn.get(rec_ids=alias, ignore404=False)
        try:
            dacc_id = rec["accession"]
        except KeyError:
            dacc_id = rec["uuid"]
        line = [line.strip("\n")]
        outline = line.append(dacc_id)
        fout.write("\t".join(line) + "\n")
    fout.close()
    fh.close()

if __name__ == "__main__":
    main()
