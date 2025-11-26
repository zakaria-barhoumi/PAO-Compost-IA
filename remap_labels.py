import os
import glob
from tqdm import tqdm # Optional: for progress bar, install with 'pip install tqdm'

# --- CONFIGURATION ---
# Path to your downloaded dataset's labels (original)
# Usually formatted as: dataset/train/labels or dataset/labels/train
INPUT_DIR = "dataset/labels" 

# Where to save the new converted labels
OUTPUT_DIR = "dataset/labels_converted"

# MAPPING LOGIC
# Source IDs (Garbage Detection Dataset):
# 0: BIODEGRADABLE
# 1: CARDBOARD
# 2: GLASS
# 3: METAL
# 4: PAPER
# 5: PLASTIC

# Target IDs (Your New Schema):
# 0: Dgrx
# 1: Mrisq
# 2: NonCompsot
# 3: Compsot

# The Mapping Dictionary {Source_ID: Target_ID}
ID_MAPPING = {
    0: 3,  # BIODEGRADABLE -> Compsot
    1: 2,  # CARDBOARD     -> NonCompost
    2: 2,  # GLASS         -> NonCompost
    3: 1,  # METAL         -> Mrisq
    4: 2,  # PAPER         -> NonCompost
    5: 2   # PLASTIC       -> NonCompost
}

def process_label_file(file_path, output_root):
    """Reads a YOLO label file, remaps classes, and writes to output."""
    
    # Create corresponding output path
    # Example: dataset/labels/train/file.txt -> dataset/labels_converted/train/file.txt
    rel_path = os.path.relpath(file_path, INPUT_DIR)
    out_path = os.path.join(output_root, rel_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    new_lines = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
            
        try:
            current_id = int(parts[0])
            
            # Apply mapping
            if current_id in ID_MAPPING:
                new_id = ID_MAPPING[current_id]
                
                # Reconstruct the line with the new ID
                # parts[1:] contains x_center, y_center, width, height
                new_line = f"{new_id} " + " ".join(parts[1:]) + "\n"
                new_lines.append(new_line)
            else:
                print(f"Warning: Unknown class ID {current_id} in {file_path}")
                # Optional: keep original line or skip? currently skipping unknown classes.
                
        except ValueError:
            print(f"Error parsing line in {file_path}: {line}")

    # Write the new file
    with open(out_path, 'w') as f_out:
        f_out.writelines(new_lines)

def main():
    print(f"Starting conversion...")
    print(f"Input: {INPUT_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Mapping: {ID_MAPPING}")
    
    # Recursively find all .txt files in INPUT_DIR
    # This covers structure like labels/train/*.txt and labels/val/*.txt
    txt_files = glob.glob(os.path.join(INPUT_DIR, '**', '*.txt'), recursive=True)
    
    if not txt_files:
        print("No .txt files found! Check your INPUT_DIR path.")
        return

    print(f"Found {len(txt_files)} label files. Processing...")

    # Process files
    for file_path in tqdm(txt_files, desc="Converting Labels"): # remove tqdm( ... ) and use txt_files if not installed
        process_label_file(file_path, OUTPUT_DIR)
        
    print("\nDone!")
    print(f"New labels are located in: {OUTPUT_DIR}")
    print("Remember to update your data.yaml to point to this new labels folder!")

if __name__ == "__main__":
    main()