read -p "Please enter the interval step (e.g., 10): " interval_step
read -p "Please enter the maximum number of molecules: " MaxMolecules
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
if ! [[ "$number_steps" =~ ^[0-9]+$ ]]; then
    echo "Invalid input for number steps. Please enter a positive integer."
    exit 1
fi

# Save parameters to config.dat with timestamp
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
echo "Timestamp: $timestamp" > config.dat
echo "interval_step: $interval_step" >> config.dat
echo "MaxMolecules: $MaxMolecules" >> config.dat
echo "number_steps: $number_steps" >> config.dat


# Loop to create new directories and copy modified input files
for (( i=0; i<=$MaxMolecules; i+=interval_step )); do
    # Since XXX and YYY are the same, we only need one variable for both
    start_end=$i

    # ZZZ value adjustment removed as it's not needed in this context

    # Calculate AAA and BBB
    BBB=$number_steps
    AAA=$((BBB / 10))

    # Create new directory for the interval
    new_dir="interval_${i}"
    mkdir -p "$new_dir"

    # Copy the original input file, .def, .cif, and tmp.sh files to the new directory
    cp simulation.input *.def *.cif tmp.sh "$new_dir/"

    # Rename the copied tmp.sh to i.sh
    mv "$new_dir/tmp.sh" "$new_dir/${i}.sh"

    # Modify the values of XX (start and end), ZZZ, BBB, and AAA in the copied input file
    sed -i "s/XXX/$start_end/g" "$new_dir/simulation.input"
    sed -i "s/YYY/$start_end/g" "$new_dir/simulation.input"
    sed -i "s/ZZZ/$i/g" "$new_dir/simulation.input"
    sed -i "s/BBB/$BBB/g" "$new_dir/simulation.input"
    sed -i "s/AAA/$AAA/g" "$new_dir/simulation.input"
done

echo "All jobs prepared in directories."


