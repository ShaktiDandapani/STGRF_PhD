#!/usr/bin/perl
# check_file.pm

use warnings;
use strict;


# Calling example
# ===============
#
# check_file_existence{
#     filename -> 'filename.inp'
# }


sub check_file_existence {
    my ($args) = @_;

    while(!-e $args->{filename}){
        ;
    }

    if (-e $args->{filename}){
      #print "\n The file: $args->{filename} present.";
      return 1;
    }else{
      die "File not found";
    }

}

1;
