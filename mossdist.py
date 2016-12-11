import subprocess
import random
import re
from distancemodel import CorpusDistModel
import os

# TODO: clean this up?
# MOSS_PATH = "/home/richard/mosslocal"
# MOSS_SCRATCH = "/home/richard/tmp/"
MOSS_PATH = os.environ['MOSS_PATH']
print("Using MOSS_PATH=" + MOSS_PATH)
MOSS_SCRATCH = os.environ['MOSS_SCRATCH']
print("USING MOSS_PATH=" + MOSS_SCRATCH)

class MossDistModel(CorpusDistModel):

    def distance(self, analysis_context, old_rev, new_rev, filekey):
        if old_rev == new_rev:
            return 0

        tmppath = MOSS_SCRATCH + str(random.randint(1000000000, 9999999999)) + '/'

        exit_code = subprocess.call(
            './runmoss.sh %s %s %s %s %s %s' % (
                MOSS_PATH, analysis_context.repo_path + "/", old_rev, new_rev, filekey, tmppath), 
            shell=True)
        if exit_code:
            assert(False)

        p = []
        with open(tmppath + 'out/index.html', 'r') as mossfile:
            for line in mossfile:
                num = find_percent(line)
                if num is None:
                    continue
                p.append(num)
                if len(p) == 2:
                    # be careful :P
                    subprocess.call('rm -rf ' + tmppath, shell=True)
                    return (200. - p[0] - p[1])/200

        # Lines did not match at all
        return 1

def find_percent(line):
    m = re.search('\(.+%\)', line)
    if m:
        found = m.group(0)
        return float(found[1:-2])
    return None
