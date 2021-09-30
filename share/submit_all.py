#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import argparse
import os.path
from os import path
import glob
from random import randrange, random
import random
from datetime import datetime

def getArgs():

    parser = argparse.ArgumentParser(description='Submit condor jobs')

    parser.add_argument("--job", dest="job", action="store", default="", help="Input for the job name")

    parser.add_argument("--maxEvents", dest="maxEvents", action="store", default="", help="maxEvents")
    parser.add_argument("--runNumber", dest="runNumber", action="store", default="", help="runNumber")
    parser.add_argument("--joboption", dest="joboption", action="store", default="", help="Job option to run")
    parser.add_argument("--gridpack",   dest="gridpack", action="store", default="", help="gridpack")

    parser.add_argument("--no_sub", dest="no_sub", action="store_true", default=False, help="No submission")
    parser.add_argument("--no_delete", dest="no_delete", action="store_true", default=False, help="No delete")

    parser.add_argument("--mH2",   dest="mH2", action="store", default="", help="mass of Scalar Higgs")
    parser.add_argument("--wH2",   dest="wH2", action="store", default="", help="width of Scalar Higgs")

    parser.add_argument("--mH3",   dest="mH3", action="store", default="", help="mass of PsuedoScalar Higgs")
    parser.add_argument("--wH3",   dest="wH3", action="store", default="", help="width of PsuedoScalar Higgs")

    dict_args = vars(parser.parse_args()) # create list from args parser

    return parser.parse_args(), dict_args


def WriteCommand(dict_args):

    seed_num = randrange(5000000)

    Command = 'Gen_tf.py --ecmEnergy=13000. --maxEvents='+args.maxEvents+' --runNumber='+args.runNumber+' --firstEvent=1 --randomSeed='+str(seed_num)+' --outputEVNTFile=EVNT.root --jobConfig='+args.analysis

    return Command


def Run(dict_args,JobFolderName="default"):

    WorkingPath=os.path.abspath(os.getcwd())

    Condor_path = "condor_mich"
    Condor_working_path = "condor_mich_working"

    output = WorkingPath+"/"+Condor_path+"/"+JobFolderName+"/"
    outputworking = WorkingPath+"/"+Condor_working_path+"/"+JobFolderName+"/"

    if path.isdir(output):
        os.system("rm -rf "+output)
    if path.isdir(outputworking):
        os.system("rm -rf "+outputworking)

    os.system("mkdir -p "+output)
    os.system("mkdir -p "+outputworking)

    os.chdir(outputworking)

    with open(JobFolderName+'.sh', "w") as ftw:
        ftw.write("#!/bin/bash\n")
        ftw.write("path="+WorkingPath+"\n")
        ftw.write("export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase\n")
        ftw.write("source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh\n")
        ftw.write("cd $path\n")
        ftw.write("source setup.sh\n")

        os.system("mkdir -p "+outputworking+args.analysis)

        joboption = args.joboption
        if args.analysis=="ttH" and args.mH2!="" and args.wH2!="":
            modified_joboption = joboption.replace('mh2','mh2'+args.mH2)
            modified_joboption = joboption.replace('wh2','wh2'+args.wH2)
        elif args.analysis=="ttA" and args.mH3!="" and args.wH3!="":
            modified_joboption = joboption.replace('mh3','mh3'+args.mH3)
            modified_joboption = joboption.replace('wh3','wh3'+args.wH3)
        else:
            print("Please provide the mass and width of the higgs, and check your job options")
            break
        
        ftw.write("cp config/"+args.analysis+"/"+args.joboption+" "+outputworking+args.analysis+" \n")
        if args.gridpack!="":
            ftw.write("cp -r gridpack/"+args.gridpack+" "+outputworking+"Process\n")

        ftw.write("cd "+outputworking+"\n")

        Command = WriteCommand(dict_args)
        ftw.write(Command+"\n")

        ftw.write("cp log.generate "+output+"\n")
        ftw.write("cp EVNT.root "+output+"\n")
        ftw.write("rm EVNT.root \n")


    with open("job.sub", "w") as jobsub:

        jobsub.write("universe = vanilla\n")
        jobsub.write("executable = "+JobFolderName+'.sh'+"\n")
        jobsub.write("output = "+output+"job.out\n")
        jobsub.write("error = "+output+"job.err\n")
        jobsub.write("log = "+output+"job.log\n")
        jobsub.write("queue\n")

def Submission(JobFolderName):

    os.system("pwd; ls")
    os.system('chmod +x '+JobFolderName+'.sh')

    batch_cmd = "condor_submit job.sub"
    print ("\t > Submission of %s on the HTCaondor" % JobFolderName)
    if args.no_sub:
        pass
    else:
        os.system (batch_cmd)

def main():

    command = WriteCommand(dict_args)
    print(" >> Run command:\n%s" % command)

    JobFolderName = args.job
    Run(dict_args,JobFolderName)
    Submission(JobFolderName)

if __name__ == '__main__':
    args, dict_args = getArgs()
    main()
