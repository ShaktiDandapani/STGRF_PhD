#!/usr/bin/perl
use warnings;
use strict;
use Cwd;
use libraries::RemodellingRoutines::check_file;
use libraries::RemodellingRoutines::execute_ansys;
use libraries::RemodellingRoutines::read_file_to_hash;
use File::Copy;

# Read in the parameters file and calculate the time etc automatically here ! 
# using python dictionary approach
my %param_data; 
my $param_fname = "./parameters/parameters_myocardium.dat";

# Include a command to print out the time stamp and calculate the time taken for the simulation
# to finish
my $datestring = localtime();
print "Start Time: ", $datestring;
# ---------------------------------------------------------------------------- #
# 1. Declare the name of the file and store into a variable

my $file_name_python = "gr_hgo_model.py";
# my $dir = getcwd;

# Read n system argument for stress_evo
my $evo_flag = $ARGV[0];
print($evo_flag);
# 2. Run a command using the file name and run the file

if (!-e $file_name_python) {
print "no python script generator file found.";
# die "\nNeed a python file to run\n";
} else {
# my $shear_modulus = 2e06;
system("python", $file_name_python, "myocardium");
}

# 3. Only monitor the creation/ modification of .inp file
print "\n         (ctrl+c to halt)             \n";

my $input_file = 'ansys_job.inp';  

check_file_existence({filename => $input_file});

# 4. Once the .inp file is created execute ansys
# Place a check on job name and create new jobname for each iteration
my $step_counter = 0;
my $job_name_clean = 'gr_step_';
my $job_name =  $job_name_clean. $step_counter;  # Here think a a command line argument

execute({
    input_file => $input_file,
    job_name => $job_name
});

print "\n end ansys job";

# ---------------------------------------------------------------------------- #
# 5.b. if nlist and elist are found, use them to run through the
#     script for building fibres..... and proceed to initiate the .inp file
#     to the next step.
my $file_stress = 'stress_list.txt';
my $file_strain = 'strain_list.txt';

my $exists_file_stress = check_file_existence({filename => $file_stress});

my $file_homeo_stress = 'stress_list_0.txt';
my $file_homeo_strain = 'strain_list_0.txt';

if ($exists_file_stress){
    rename $file_stress, $file_homeo_stress;
    rename $file_strain, $file_homeo_strain;
    print "\n Homeostatic state Saved";
}

# Run fibroblast script to create recruitment field
system("python", "./workflows/write_fibroblast_file.py");
system("python", "./workflows/create_homeo_inital.py");
my $fibroblast_homeo_fname =  "fibroblast_info_0.csv";

# Growth And Remodelling Loop

my $homeostatic_material_values = "material_values_0.csv";
rename "material_values.csv", $homeostatic_material_values; # dont need this line 

# print "$no_of_steps, $step, $time_period";
%param_data = read_parameters_file({
    filename => $param_fname,
});
# print $param_data{'time_period'};
my $time_period_param = $param_data{'time_period'};
my $no_of_steps_param = $param_data{'number_of_iterations'};
my $step_param = $param_data{'iteration'};

my $file_time = "./parameters/parameters_myocardium.dat";
my $material_ansys = "materials.inp";
my $rem_script = "./workflows/remodelling_mod_hgo.py";
my $gr_steps_limit = int($no_of_steps_param) - 1;    # Needs to be read in from the parameters_myocardium.dat file
my $old_material_values = " ";  # initialise variable
my $remodelled_material_values = " ";
my $prev_strain_list      = "strain_list_0.txt";
my $prev_stress_list      = "stress_list_0.txt";
my $prev_material_list    = "material_values_0.csv";
my $new_job_name          = "";
my $old_fibro_file        = "";
my $remodelled_fibro_file = "";
my $new_rem_strain_list = "";
my $homeo_counter = 0;

for (my $i = $step_counter; $i <= $gr_steps_limit; $i++){
    %param_data = read_parameters_file({
        filename => $param_fname,
    });
    # print $param_data{'time_period'};
    my $time_period_param = $param_data{'time_period'};
    my $no_of_steps_param = $param_data{'number_of_iterations'};
    my $step_param = $param_data{'iteration'};
    print "\n Curr Step: ", $step_param;
    print "\n Curr Time: ", $step_param * ($time_period_param/$no_of_steps_param);
    
    # # Evolve the homeostatic state if evo_flag is active
    # if ($evo_flag == 1){
    #     $homeo_counter = int(($i - 1)/2);
    #         if ($i < 2){
    #             $file_homeo_strain   = "strain_list_0.txt";
    #         }
    #         else{
    #             $file_homeo_strain   = "strain_list_rem_".$homeo_counter.".txt";
    #             $homeostatic_material_values = "material_values_rem_".$homeo_counter.".csv";
    #         }
    # }

    if ($i == 0){
        $prev_material_list  = $homeostatic_material_values;
        $old_fibro_file      = $fibroblast_homeo_fname;
    }
    else{
           $old_fibro_file      = $remodelled_fibro_file;
    }

    $remodelled_fibro_file          = "fibroblast_info_rem_".$i.".csv";

    $remodelled_material_values     = "material_values_rem_".$i.".csv";


    $new_job_name                   = $job_name_clean."rem_".$i;

    # Execute Growth & Remodelling Script
    print "\n Remodelling Script Running...";
    system("python",
            $rem_script,
            $prev_strain_list,
            $file_homeo_strain,
            $prev_material_list,
			$homeostatic_material_values,
            $remodelled_material_values,
            $material_ansys,
            $fibroblast_homeo_fname,
            $old_fibro_file,
            $remodelled_fibro_file,
            $file_time,
            $evo_flag);

    # Execute ansys simulation for remodelled materials list
    execute({
        input_file => $input_file,
        job_name => $new_job_name
    });

    # save a copy of the stresses for the degraded simulation
    my $exists_file_stress      = check_file_existence({filename => $file_stress});
    my $exists_file_strain      = check_file_existence({filename => $file_strain});

	# This will come when deg stops and remodelling kicks in
	my $new_rem_stress_list     = "stress_list_rem_".$i.".txt";
    $new_rem_strain_list     = "strain_list_rem_".$i.".txt";
    
    # Save the output files in the names of the current step and phase.
    if ($exists_file_stress){
        copy($file_stress, $new_rem_stress_list);
    }

    if ($exists_file_strain){
        copy($file_strain, $new_rem_strain_list);
    }

    $prev_material_list = $remodelled_material_values;
    $prev_strain_list   = $new_rem_strain_list;
    $prev_stress_list   = $new_rem_strain_list;
    my $datestring_2 = localtime();
    print "\n System Time: ", $datestring_2;
}

my $datestring_3 = localtime();
print "\nEnd Time: ", $datestring_3;

