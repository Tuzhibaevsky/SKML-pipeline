#!/bin/sh -f
n=0
n2=0
ul=99

cachedir=$PWD/.cache/conv-root/
mkdir -p $cachedir
mkdir -p $cachedir/submit
mkdir -p $cachedir/flag

while [ $n -le $ul ]
do
  n=`expr $n + 1`
  dir=`pwd`
  ./_03B_conv_template.sh $n $dir > $cachedir/submit/conv-root_job_$n.sh
  chmod a+x $cachedir/submit/conv-root_job_$n.sh
done

cd $cachedir/submit

while [ $n2 -le $ul ]
do
  n2=`expr $n2 + 1`
  pjsub -L rscgrp=atmpd conv-root_job_$n2.sh
done
