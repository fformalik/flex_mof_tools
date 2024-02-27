
#!/bin/bash

config_file="config.dat"

# Check if config.dat exists and read values
if [ -f "$config_file" ]; then
    echo "Using values from $config_file."
    while IFS=": " read -r key value; do
        case $key in
            interval_step) interval_step=$value ;;
            MaxMolecules) MaxMolecules=$value ;;
            overlap) overlap=$value ;;
        esac
    done < "$config_file"
else
    # If config.dat does not exist, prompt the user for values
    read -p "Please enter the interval step (e.g., 100): " interval_step
    read -p "Please enter the maximum number of molecules: " MaxMolecules
    read -p "Please enter the overlap value: " overlap
    # Optionally, prompt for number_steps if your script uses it
    # read -p "Please enter the number of steps: " number_steps
fi


# Remove the old results.dat file if it exists
rm -f results.dat

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

# Number of lines to skip at the beginning of each file (5 lines of comments)
skip_lines=5

for (( i=0; i<=$MaxMolecules; i+=interval_step )); do
    new_dir="interval_${i}_to_$((i+interval_step))"
    echo $i
    if [ -d "$new_dir" ]; then
        file_path="${new_dir}/TMMC/System_0/*"
        if [ $i -eq 0 ]; then
            # For the first interval, adjust skipping and add the sequence column
            tail -n +$(($skip_lines+1)) $file_path | head -n -$overlap | awk -v interval=$i -v step=$interval_step 'BEGIN{counter=interval} {print counter++, $4, $5, $6}' >> results.dat
        else
            # For other intervals, adjust skipping and add the sequence column
            tail -n +$(($skip_lines+$overlap+1)) $file_path | head -n -$overlap | awk -v interval=$i -v step=$interval_step 'BEGIN{counter=interval} {print counter++, $4, $5, $6}' >> results.dat
        fi
    else
        echo "Directory $new_dir does not exist."
    fi
done

echo "All results ready."


