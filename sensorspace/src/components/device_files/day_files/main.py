import os

def rename_json_files():
    # Get all files in the current directory
    files = os.listdir('.')
    # Filter to keep only .json files
    json_files = [f for f in files if os.path.isfile(f) and f.endswith('.json')]
    # Sort files alphabetically to maintain some kind of order if needed
    json_files.sort()

    # Rename files sequentially
    for index, filename in enumerate(json_files):
        new_filename = f"{index}.json"
        os.rename(filename, new_filename)
        print(f"Renamed '{filename}' to '{new_filename}'")

# Call the function
rename_json_files()