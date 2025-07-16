import argparse
import os

def main(png_filenames, input_filename, output_filename):
    # Initialize an empty dictionary to store the matched rows
    matched_rows = {}

    # Extract only the MJD portion from the provided PNG filenames
    png_mjd = [filename.split('_')[1] for filename in png_filenames]

    # Open the input file and read its content
    with open(input_filename, "r") as input_file:
        lines = input_file.readlines()

    # Open a new file to write the matched rows
    with open(output_filename, "w") as output_file:
        # Iterate over each line in the content
        for line in lines:
            # Strip whitespace and split each line into components
            parts = line.strip().split()
            if len(parts) == 11:
                # Extract the filename from the line and strip any surrounding whitespace
                full_path = parts[8].strip()
                filename = os.path.basename(full_path)  # Get only the filename

                # Extract only the MJD part from the filename (the second underscore-separated component)
                file_mjd = filename.split('_')[1]

                # Check if the MJD is in the list of PNG MJD values
                if file_mjd in png_mjd:
                    # Write the line to the output file without adding an extra newline
                    output_file.write(line)
                    # Add the line to the dictionary with the filename as the key
                    if filename not in matched_rows:
                        matched_rows[filename] = []
                    matched_rows[filename].append(line.strip())

    # Print the matched rows dictionary
    print(matched_rows)

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Crossmatch PNG filenames with input file.",
        epilog=(
            "Author: Pranav Limaye\n"
            "Date: May 24, 2024\n"
            "Example usage: python crossmatch_script.py -i input.cands -o output.txt _60439.2009370249_cfbf00000_01_01_replot.png _60439.2020366037_cfbf00000_01_01_replot.png"
        )
    )
    parser.add_argument(
        "png_filenames",
        nargs="+",
        help="List of PNG filenames to crossmatch. Provide one or more filenames separated by spaces."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input filename containing the data to be processed."
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output filename where the matched rows will be written."
    )

    args = parser.parse_args()

    main(args.png_filenames, args.input, args.output)
