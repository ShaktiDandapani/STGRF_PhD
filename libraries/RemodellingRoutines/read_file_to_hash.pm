use strict;
use warnings;


# Usage
#
# read_parameters_file


sub read_parameters_file{
    my ($args) = @_;

    my $file = $args->{filename};

    my %hash_data;
    open my $info, $file or die " Could not open $file: %!";

    while (my $line=<$info>) {
        chomp $line;
        # print $line,"\n";
        (my $word1,my $word2) = split /=/, $line;

        $hash_data{$word1} = $word2;
        # print "$word1 = $word2 \n";
    }

    return %hash_data;

}

1;
