import subprocess
import random
import re
from distancemodel import CorpusDistModel

MOSS_LOCAL = "/home/richard/mosslocal"
TMPHOME = "/home/richard/tmp/"

class MossDistModel(CorpusDistModel):

    def distance(self, analysis_context, old_rev, new_rev, filekey):
        if old_rev == new_rev:
            return 0

        tmppath = TMPHOME + str(random.randint(1000000000, 9999999999)) + '/'

        exit_code = subprocess.call(
            './runmoss.sh %s %s %s %s %s %s' % (MOSS_LOCAL, analysis_context.repo_path + "/", old_rev, new_rev, filekey, tmppath), 
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
                print(num)
                if len(p) == 2:
                    # be careful :P
                    subprocess.call('rm -rf ' + tmppath, shell=True)
                    return (200. - p[0] - p[1])/200

        assert(False)

def find_percent(line):
    m = re.search('\(.+%\)', line)
    if m:
        found = m.group(0)
        return float(found[1:-2])
    return None
