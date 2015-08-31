#!/usr/bin/perl

use strict;

my @days=(0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);

sub isleap {
  if(  $_[0] % 400 ==0) { return 1; }
  elsif($_[0] % 100 ==1) { return 0; }
  elsif($_[0] %   4 ==1) { return 1; }
  else { return 0; }
}

for(my $year=2013; $year<=2014; $year++){
  for(my $month=1; $month<=12; $month++){
    my $endday=$days[$month];
    if($month==2 && isleap($year)) { $endday=29; }
#    print "$endday ".$days[$month]."\n";
    for(my $day=1; $day<=$endday; $day++){
      print "wget http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php?prec_no=86&block_no=47821&year=$year&month=$month&day=$day&view=p1";
      print "\n";
      system 'wget http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php\?prec_no=86\&block_no=47821\&year='.$year.
             '\&month='.$month.
             '\&day='.$day.'\&view=p1 -O '.sprintf("%04d%02d%02d", $year,$month, $day).'-log';
    }
  }
}

