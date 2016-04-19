#!/bin/env python
import sys
import subprocess

class Bjobs:
    def __init__(self, submition=None):
        if submition:
            lis = submition.strip().split(' ')
            self.name=lis[-2]
            self.status='submitted'
            self.id = lis[-1][1:-1]

def parse_sjm_log(f):
    jobs = {}
    for l in f:
        if "submitted" in l:
            job = Bjobs(l)
            jobs[job.name] = job
        elif "pending" in l and "job" in l:
            jobname = l.strip().split(' ')[-2]
            jobs[jobname].status = 'pending'
        elif "running" in l and "job" in l:
            jobname = l.strip().split(' ')[-2]
            jobs[jobname].status = 'running'
        elif "done" in l and "job" in l:
            jobname = l.strip().split(' ')[-2]
            jobs[jobname].status = 'done'
        else:
            continue
    return jobs

def main():
    '''
    sys.argv[0] <status.log> [bjobs|sjm]
    '''
    fn = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "sjm":
        bjobs_out_format = False
    else:
        bjobs_out_format = True

    jobs = parse_sjm_log(open(fn))
    header_flag = True
    for jobname in jobs.keys():
        job = jobs[jobname]
        if bjobs_out_format:
            if job.status == 'running':
                o = subprocess.check_output('bjobs -J %s' % job.name, shell=True)
                if header_flag:
                    print o.rstrip()
                    header_flag = False
                else:
                    print o.rstrip().split('\n')[-1]
        else:
            print "%s\t%s\t%s"%(job.id, job.status, job.name)


if __name__ == "__main__":
    main()
