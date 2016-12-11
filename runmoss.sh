#!/bin/sh

# $1 /home/richard/mosslocal/
# $2 /home/richard/linux/
# $3 9099daed
# $4 1d8bf926
# $5 mm/bootmem.c
# $6 /home/richard/analysis1234/

cd $1
mkdir $6
git --git-dir=$2.git --work-tree=$2 show $3:$5 > $6/rev1.c
git --git-dir=$2.git --work-tree=$2 show $4:$5 > $6/rev2.c
./moss.pl -l c -o $6out $6/rev1.c $6/rev2.c
