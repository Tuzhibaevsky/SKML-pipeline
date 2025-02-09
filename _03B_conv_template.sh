#!/bin/sh -f
echo '#!/bin/csh -f'
echo '# batch request conv-root_job_'$1'.sh'
echo '#' 
echo '# @$-x'
echo '# @$-q all'
#echo '# @$-o '$2'/conv-root_job_'$1'.out'
echo '# @$-o /dev/null'
echo '# @$-eo'
echo '#'
echo 'cd '$2
echo $2'/_03B_conv-root_job.sh'
