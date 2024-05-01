# Description: Script to run PixelAV on multiple cores whilest taking care of splitting the track_list accordingly

import subprocess
from multiprocessing import Pool

# Constants
TOTAL_EVENTS = 2000000
CHUNK_SIZE = 50000
NUM_CORES = 6  # Or use multiprocessing.cpu_count() to use all available cores

def run_task(chunk_index):
    command = f"./ppixelav2_list_trkpy_n_2f {chunk_index+1} {CHUNK_SIZE}"
    print(f"Running: {command}")
    subprocess.run(command, shell=True)
    print(f"Finished: {command}")

def main():
    num_chunks = TOTAL_EVENTS // CHUNK_SIZE
    chunk_indices = list(range(num_chunks))
    with Pool(NUM_CORES) as pool:
        pool.map(run_task, chunk_indices)

if __name__ == "__main__":
    main()