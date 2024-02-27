#!/bin/bash

# Prompt the user for the interval step, MaxMolecules, overlap, and number steps
read -p "Please enter the interval step (e.g., 100): " interval_step
read -p "Please enter the maximum number of molecules: " MaxMolecules
read -p "Please enter the overlap value: " overlap
read -p "Please enter the number steps value: " number_steps

# Validate inputs
if ! [[ "$interval_step" =~ ^[0-9]+$ ]]; then
    echo "Invalid input for interval step. Please enter a positive integer."
    exit 1
fi
if ! [[ "$MaxMolecules" =~ ^[0-9]+$ ]]; then
    echo "Invalid input for MaxMolecules. Please enter a positive integer."
    exit 1
fi
if ! [[ "$overlap" =~ ^[0-9]+$ ]]; then
    echo "Invalid input for overlap. Please enter a positive integer."
    exit 1
fi
if ! [[ "$number_steps" =~ ^[0-9]+$ ]]; then
    echo "Invalid input for number steps. Please enter a positive integer."
    exit 1
fi

config_file="config.dat"

# Get current timestamp
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Write the configuration and timestamp to the file
echo "Timestamp: $timestamp" > $config_file
echo "interval_step: $interval_step" >> $config_file
echo "MaxMolecules: $MaxMolecules" >> $config_file
echo "overlap: $overlap" >> $config_file
echo "number_steps: $number_steps" >> $config_file


# Loop to create new directories and copy modified input files
for (( i=0; i<=$MaxMolecules; i+=interval_step )); do
    # Adjust the start and end of the interval to include overlap
    start=$((i - overlap))
    end=$((i + interval_step + overlap))
    # Ensure start is not less than 0
    if [ $start -lt 0 ]; then
        start=0
    fi

    # Calculate BBB and AAA
    BBB=$((number_steps * (interval_step + 2 * overlap)))
    AAA=$((BBB / 10))

    # Create new directory for the interval
    new_dir="interval_${i}_to_$((i+interval_step))"
    mkdir -p $new_dir

    # Copy the original input file, .def, .cif, and tmp.sh files to the new directory
    cp simulation.input *.def *.cif tmp.sh $new_dir/

    # Rename the copied tmp.sh to i.sh
    mv $new_dir/tmp.sh $new_dir/${i}.sh

    # Modify the values of XX, YY, ZZ, BBB, and AAA in the copied input file
    sed -i "s/XXX/$start/g" $new_dir/simulation.input
    sed -i "s/YYY/$end/g" $new_dir/simulation.input
    sed -i "s/ZZZ/$i/g" $new_dir/simulation.input
    sed -i "s/BBB/$BBB/g" $new_dir/simulation.input
    sed -i "s/AAA/$AAA/g" $new_dir/simulation.input
done

echo "All jobs prepared in directories."

