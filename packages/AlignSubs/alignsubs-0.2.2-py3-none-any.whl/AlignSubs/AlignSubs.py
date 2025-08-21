import csv
from collections import defaultdict
import os
import sys
import time
import importlib.util
import subprocess
from Bio import SeqIO

# --- Dependency check and auto-install ---
missing = []
for pkg in ["Bio"]:
    if importlib.util.find_spec(pkg) is None:
        missing.append(pkg)

if missing:
    print("Missing dependencies detected:", ", ".join(missing))
    choice = input("Do you want to install them now? (yes/no): ").strip().lower()
    if choice in ["yes", "y"]:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "biopython"])
            print("Biopython installed successfully.")
        except Exception as e:
            print("Failed to install biopython:", e)
            sys.exit(1)
    else:
        print("Please install manually with: pip install biopython")
        sys.exit(1)

# Kyte-Doolittle hydropathy scale
KD_SCALE = {
    "A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5,
    "Q": -3.5, "E": -3.5, "G": -0.4, "H": -3.2, "I": 4.5,
    "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8, "P": -1.6,
    "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2
}

DNA_CHARS = set("ACGTU-")
PROTEIN_CHARS = set("ACDEFGHIKLMNPQRSTVWY-")

def get_sequence_type():
    stype = input("Are your sequences Protein or DNA/RNA? (protein/dna/rna): ").strip().lower()
    if stype not in ("protein", "dna", "rna"):
        print("Invalid input, defaulting to protein.")
        stype = "protein"
    return stype

def get_input_file():
    path = input("Enter path to alignment file (FASTA or Clustal): ").strip()
    while not os.path.isfile(path):
        print("File not found. Try again.")
        path = input("Enter path to alignment file (FASTA or Clustal): ").strip()
    return path

def detect_format(filename):
    with open(filename) as f:
        first_line = f.readline().strip()
        if first_line.startswith("CLUSTAL"):
            return "clustal"
        else:
            return "fasta"

def read_alignment(filename):
    fmt = detect_format(filename)
    if fmt == "fasta":
        records = list(SeqIO.parse(filename, "fasta"))
    else:
        records = list(SeqIO.parse(filename, "clustal"))
    names = [r.id for r in records]
    seqs = [str(r.seq).upper() for r in records]
    return names, seqs

def validate_seq_type(seq_type, seqs):
    all_chars = set("".join(seqs).replace("-", ""))
    if seq_type in ("dna", "rna") and not all_chars <= DNA_CHARS:
        print(f"Warning: Sequences contain characters not valid for {seq_type.upper()}: {all_chars - DNA_CHARS}")
        ans = input("Do you still want to continue? (yes/no): ").strip().lower()
        if ans not in ("yes", "y"):
            sys.exit("Exiting due to invalid sequence characters.")
    if seq_type == "protein" and not all_chars <= PROTEIN_CHARS:
        print(f"Warning: Sequences contain characters not valid for PROTEIN: {all_chars - PROTEIN_CHARS}")
        ans = input("Do you still want to continue? (yes/no): ").strip().lower()
        if ans not in ("yes", "y"):
            sys.exit("Exiting due to invalid sequence characters.")
    return True

def calculate_hydro_change(a1, a2):
    if a1 in KD_SCALE and a2 in KD_SCALE:
        return abs(KD_SCALE[a1] - KD_SCALE[a2])
    return 0

def compare_alignment(names, seqs, seq_type):
    all_changes = dict()
    hydro_changes = dict()
    n = len(names)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            key = (names[i], names[j])
            changes = defaultdict(list)
            hydro = dict()
            for idx, (c1, c2) in enumerate(zip(seqs[i], seqs[j]), 1):
                if c1 != c2 and c1 != "-" and c2 != "-":
                    change = f"{c1}>{c2}"
                    changes[change].append(idx)
                    if seq_type == "protein":
                        hydro[change] = calculate_hydro_change(c1, c2)
            all_changes[key] = changes
            if seq_type == "protein":
                hydro_changes[key] = hydro
    return all_changes, hydro_changes

def save_directional_csv(names, all_changes, hydro_changes=None):
    out_file = input("Enter path to save directional list CSV file: ").strip()
    if not out_file.lower().endswith(".csv"):
        out_file += ".csv"
    header = ["From", "To", "Change", "Positions", "Count"]
    if hydro_changes:
        header.append("HydropathyChange")
    with open(out_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for p1 in names:
            for p2 in names:
                if p1 == p2:
                    continue
                changes = all_changes.get((p1, p2), {})
                sorted_changes = sorted(changes.items(), key=lambda x: len(x[1]), reverse=True)
                for change, positions in sorted_changes:
                    row = [p1, p2, change, ",".join(map(str, positions)), len(positions)]
                    if hydro_changes:
                        row.append(round(hydro_changes.get((p1, p2), {}).get(change, 0), 2))
                    writer.writerow(row)
    print(f"Directional CSV saved to {out_file}")
    time.sleep(0.5)

def save_substitution_summary_csv(names, all_changes, hydro_changes=None):
    out_file = input("Enter path to save substitution count summary CSV file: ").strip()
    if not out_file.lower().endswith(".csv"):
        out_file += ".csv"

    subs_summary = defaultdict(lambda: defaultdict(int))
    total_counts = defaultdict(int)

    for (p1, p2), changes in all_changes.items():
        for change, positions in changes.items():
            subs_summary[change][f"{p1}->{p2}"] = len(positions)
            total_counts[change] += len(positions)

    sorted_changes = sorted(total_counts.items(), key=lambda x: x[1], reverse=True)

    header = ["Change"]
    if hydro_changes:
        header.append("HydropathyChange")
    header += [f"{p1}->{p2}" for p1 in names for p2 in names if p1 != p2] + ["Total"]

    rows = []
    for change, total in sorted_changes:
        row = [change]
        if hydro_changes:
            found = False
            for (p1, p2), hydros in hydro_changes.items():
                if change in hydros:
                    row.append(round(hydros[change], 2))
                    found = True
                    break
            if not found:
                row.append(0)
        for p1 in names:
            for p2 in names:
                if p1 == p2:
                    continue
                row.append(subs_summary[change].get(f"{p1}->{p2}", 0))
        row.append(total)
        rows.append(row)

    with open(out_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Substitution summary CSV saved to {out_file}")
    time.sleep(0.5)

if __name__ == "__main__":
    print("Alignment Substitution Analyzer v0.2")
    time.sleep(1)

    seq_type = get_sequence_type()
    time.sleep(0.5)
    infile = get_input_file()
    time.sleep(0.5)
    names, seqs = read_alignment(infile)

    validate_seq_type(seq_type, seqs)

    print(f"Sequence type confirmed: {seq_type.upper()}")
    time.sleep(0.5)

    all_changes, hydro_changes = compare_alignment(names, seqs, seq_type)

    include_hydro = False
    if seq_type == "protein":
        ans = input("Include hydropathy column in CSVs? (yes/no): ").strip().lower()
        if ans in ("yes", "y"):
            include_hydro = True

    save_directional_csv(names, all_changes, hydro_changes if include_hydro else None)
    save_substitution_summary_csv(names, all_changes, hydro_changes if include_hydro else None)

    print("All tasks completed successfully!")

