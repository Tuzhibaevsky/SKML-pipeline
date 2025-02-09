#!/usr/bin/perl
mkdir "./out/seeds" unless -d "./out/seeds";
chdir "./out/seeds" ;
for($i=0;$i<3000;$i++) {
    $r1 = 0.;
    $r2 = 0.;
    $r3 = 0.;
    $r4 = 0.;
    while ($r1 == 0 || $r2 == 0 || $r3 == 0 || $r4 == 0) {
	$r1 = int((2*rand()-1)**2*100000.);
	$r2 = int((2*rand()-1)**2*100000.);
	$r3 = int((2*rand()-1)**2*100000.);
	$r4 = int((2*rand()-1)**2*100000.);
    }
    $nstr = sprintf("%03d", $i);
    $out = "random.tbl.$nstr";
    &mkcard();
}
##################
sub mkcard{
    open (OUT, "> $out");
    printf OUT "%.d %.d %.d %.d 0\n",$r1,$r2,$r3,$r4;
    close OUT;
}
