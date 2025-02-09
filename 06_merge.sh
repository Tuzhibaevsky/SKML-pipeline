#!/bin/bash

SLEEPTIME=5

INDIR=$PWD/out/subh5
PREFIX=f_
OUTDIR=$PWD/out/final
OUTFILE=$OUTDIR/merged.h5
mkdir -p $OUTDIR

    COPYSH=.cache/merge.$PREFIX.sh
    echo '#!/bin/bash' > $COPYSH
    echo '#PJM -L "rscgrp=all"' >> $COPYSH
    echo '#PJM -e ./.errs/merge.'$PREFIX >> $COPYSH
    echo '#PJM -o ./.logs/merge.'$PREFIX >> $COPYSH
    echo 'INDIR='$INDIR >> $COPYSH
    echo 'PREFIX='$PREFIX >> $COPYSH
    echo 'OUTFILE='$OUTFILE >> $COPYSH
    cat ./_06_merge_job.sh >> $COPYSH
    pjsub $COPYSH

#clean up
UNFINISHED=`pjstat | grep "merge" | wc -l` 
while [ $UNFINISHED -gt 0 ]
do
    echo "Waiting for $UNFINISHED jobs to finish..."
    sleep 5
    UNFINISHED=`pjstat | grep "merge" | wc -l`
done
echo "All jobs finished, cleaning up..."
rm .cache/merge.*.sh