#!/usr/bin/perl
mkdir "./out/sim" unless -d "./out/sim";
for($i=0;$i<1000;$i++){
    $nstr = sprintf("%03d", $i);
    # Get directory of the file
    mkdir "./out/sim/$nstr" unless -d "./out/sim/$nstr";
    # remove old files
    if (-e "./out/sim/$nstr/skdetsim_high.sh") {
        system "rm ./out/sim/$nstr/*";
    }
    $wd = $ENV{'PWD'};
    system "ln -s /home/upmu/tools/skdetsim-v15p3/skdetsim_high.sh ./out/sim/$nstr/skdetsim_high.sh";
    system "ln -s $wd/config/sk5_official.card ./out/sim/$nstr/sk5_official.card";
    system "ln -s /home/upmu/tools/skdetsim-v15p3/skdetsim_high ./out/sim/$nstr/skdetsim_high";
}
