#!/usr/bin/perl
# execute_ansys.pm

use warnings;
use strict;
use Cwd;

# Calling example
# ===============
#
# execute{
#       filename -> 'remodelling_1.inp',
#       jobname  -> 'some_job';
#}

sub execute{

      my ($args) = @_;
      system("ansys161 -i $args->{input_file} -j $args->{job_name}");
}


1;
