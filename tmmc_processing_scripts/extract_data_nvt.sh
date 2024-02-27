#!/bin/bash

config_file="config.dat"

# Check if config.dat exists and read values
if [ -f "$config_file" ]; then
    echo "Using values from $config_file."
    while IFS=": " read -r key value; do
        case $key in
            interval_step) interval_step=$value ;;
            MaxMolecules) MaxMolecules=$value ;;
            number_steps) number_steps=$value ;;
        esac
    done < "$config_file"
else
    echo "Config file not found. Exiting."
    exit 1
fi

# Remove the old results.dat file if it exists
rm -f results.dat

# Assuming there might be a header or non-data lines to skip
# Adjust skip_lines to skip header lines if your TMMC_Statistics.data file includes them
skip_lines=5

for (( i=0; i<=$MaxMolecules+$interval_step; i+=interval_step )); do
    new_dir="interval_${i}"
    echo "Processing directory: $new_dir"
    full_file_path="${new_dir}/TMMC/System_0/TMMC_Statistics.data"
    if [ -f "$full_file_path" ]; then
        # Skip header lines and extract columns 4, 5, 6 from the TMMC file, prepend the interval number
        # Adjusting AWK command to correctly process and output the data
        awk -v interval="$i" 'NR > skip_lines {print interval, $4, $5, $6}' skip_lines="$skip_lines" "$full_file_path" >> results.dat
    else
        echo "TMMC file not found in $new_dir."
    fi
done

echo "All results compiled into results.dat."

