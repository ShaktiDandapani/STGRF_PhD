use strict;
use warnings;


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
        print "$word1 = $word2 \n";
    }

    return %hash_data;

}

##
my $file = 'parameters_myocardium.dat';
my %hash;
#
# while (my $line=<$info>) {
#     chomp $line;
#     # print $line,"\n";
#     (my $word1,my $word2) = split /=/, $line;
#
#     $hash{$word1} = $word2;
#     print "$word1 = $word2 \n";
# }

%hash = read_parameters_file({
    filename => $file
});

print $hash{'alpha'}, "\n";
print $hash{'number_of_iterations'};
