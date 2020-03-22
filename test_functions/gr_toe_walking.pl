#!/usr/bin/perl
use strict;
use warnings;
use Cwd;
use libraries::RemodellingRoutines::check_file;
use libraries::RemodellingRoutines::execute_ansys;
use libraries::RemodellingRoutines::read_file_to_hash;
use File::Copy;

my %param_data; 
my $param_fname = "./parameters/parameters.dat";

# Include a command to print out the time stamp and calculate the time taken for the simulation
# to finish
my $date_string = localtime();
print "Start Time: ", $date_string, "\n";

# 1. Execute the homeostatic step (say a displacement of 2)
# 2. Save the values of strains and materials -> as homeostatic values (0) .
# 3. Execute another simulation with a greater stretch and hold it (update the solutions file)
# 4. Correspondingly execute remodelling routine thereafter as the fibres maintain homeostatis via (g & r)
# ---------------------------
# use command line arguments to control which growth and remodelling case to be executed !
# Improve usage of directory structures !

# 1. Pass the name of the python execution file to the variable below
my $file_name_python = "gr_hgo_model.py";

# ---------------------------------------------------------------------------- #
#                                                                              #
#              Running the python script for .inp file creation                 #
#                                                                              #
# ---------------------------------------------------------------------------- #

# 2. Run a command using the file name and run the file

if (!-e $file_name_python) {
print "no python script generator file found.";
} else {
system("python", $file_name_python, "uni_strip");
}

# 3. Only monitor the creation/ modification of .inp file
print "\n# ---------------------------------- #\n";
print "\n         (ctrl+c to halt)             \n";
print "\n# ---------------------------------- #\n";

# ---------------------------------------------------------------------------- #
#                                                                              #
#                   Execute Mechanical APDL to obtain results                  #
#                                                                              #
# ---------------------------------------------------------------------------- #

my $input_file = 'ansys_job.inp'; 

check_file_existence({filename => $input_file});

# 4. Once the .inp file is created execute ansys
# Place a check on job name and create new jobname for each iteration

# this needs to be implicitly read in from the parameters.dat file.
my $step_counter = 0; # zero here and then update for next one remodelling phase :) 

my $job_name_clean = 'gr_step_';
my $job_name =  $job_name_clean. $step_counter; 

# Execute ansys to the job name
execute({
    input_file => $input_file,
    job_name => $job_name
});

print "....";
# 5.  Rename first stress strain files to be homeostatic stress strain files 
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

# Growth And Remodelling Loop

my $homeostatic_material_values = "material_values_0.csv";
rename "material_values.csv", $homeostatic_material_values; # dont need this line 
%param_data = read_parameters_file({
    filename => $param_fname,
});
# print $param_data{'time_period'};
my $time_period_param = $param_data{'time_period'};
my $no_of_steps_param = $param_data{'number_of_iterations'};
my $step_param = $param_data{'iteration'};

my $file_time      = "./parameters/parameters.dat";
my $material_ansys = "materials.inp";
my $rem_script     = "./workflows/remodelling_tissue_strip_new.py";
my $gr_steps_limit = int($no_of_steps_param);    # Needs to be read in from the parameters_myocardium.dat file 
my $old_material_values = " ";  # initialise variable
my $remodelled_material_values = " ";
my $prev_strain_list      = "strain_list_0.txt";
my $prev_stress_list      = "stress_list_0.txt";
my $prev_material_list    = "material_values_0.csv";
my $new_job_name          = "";

$step_counter = $step_counter + 1;
print "Here";
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

    print "\n step: ", $i;

    if ($i == 1){
        $prev_material_list  = $homeostatic_material_values;
    }
    else{
        # Could do away with this line 
        $prev_material_list  = $remodelled_material_values;
    }

    $new_job_name                   = $job_name_clean."rem_".$i;
    $remodelled_material_values     = "material_values_rem_".$i.".csv";

    # Execute Growth & Remodelling Script
    print "\n Remodelling Script Running...";
    system("python",
            $rem_script,
            $prev_strain_list,                      # strain_curr_file
            $file_homeo_strain,                     # strain_homeo_file
            $prev_stress_list,                      # stress_curr_file
            $file_homeo_stress,                     # stress_homeo_file
            $prev_material_list,                    # material_old_csv
            $material_ansys,                        # material_inp_file
            $remodelled_material_values,            # material_new_csv
			$homeostatic_material_values,           # material_homeo_csv
            $file_time);                            # parameters_file

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
    my $new_rem_strain_list     = "strain_list_rem_".$i.".txt";
    
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

}

# Terminal command to obtain the time step at the end
my $datestring = localtime();
print "Start Time: ", $datestring;