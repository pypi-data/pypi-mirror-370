from pympebm import run_mpebm, get_params_path
from pympebm.mp_utils import get_unique_rows
import os
import json 
import re 
import numpy as np 

def extract_components(filename):
    pattern = r'^j(\d+)_r([\d.]+)_E(.*?)_m(\d+)$'
    match = re.match(pattern, filename)
    if match:
        return match.groups()  # returns tuple (J, R, E, M)
    return None

if __name__=='__main__':

    cwd = os.getcwd()
    print("Current Working Directory:", cwd)
    data_dir = f"{cwd}/pympebm/test/my_data"
    data_files = os.listdir(data_dir) 
    data_files = [x for x in data_files if 'PR' not in x]

    OUTPUT_DIR = 'algo_results'

    with open(f"{cwd}/pympebm/test/true_order_and_stages.json", "r") as f:
        true_order_and_stages = json.load(f)

    params_file = get_params_path()

    with open(params_file) as f:
        params = json.load(f)

    biomarkers_str = np.array(sorted(params.keys()))
    biomarkers_int = np.arange(0, len(params))
    str2int = dict(zip(biomarkers_str, biomarkers_int))
    int2str = dict(zip(biomarkers_int, biomarkers_str))

    for data_file in data_files:
        estimated_partial_rankings = []

        fname = data_file.replace('.csv', '')
        J, R, E, M = extract_components(fname)

        true_order_dict = true_order_and_stages[fname]['true_order']
        true_stages = true_order_and_stages[fname]['true_stages']
        partial_rankings = true_order_and_stages[fname]['ordering_array']
        n_partial_rankings = len(partial_rankings)

        for idx in range(n_partial_rankings):
            # partial ranking data file path
            pr_data_file = f"{data_dir}/PR{idx}_m{M}_j{J}_r{R}_E{E}.csv"

            results = run_mpebm(
                data_file=pr_data_file,
                save_results=False,
                save_details=True,
                n_iter=10000,
                burn_in=500,
                seed = 53
            )
            order_with_highest_ll = results['order_with_highest_ll']
            # Sort by value, the sorted result will be a list of tuples
            partial_ordering = [k for k, v in sorted(order_with_highest_ll.items(), key=lambda item: item[1])]
            partial_ordering = [str2int[bm] for bm in partial_ordering]
            estimated_partial_rankings.append(partial_ordering)

        padded_partial_rankings = get_unique_rows(estimated_partial_rankings)
        for mp_method in ['Pairwise', 'Mallows_Tau', 'Mallows_RMJ', 'BT', 'PL']:
            run_mpebm(
                partial_rankings=padded_partial_rankings,
                bm2int=str2int,
                mp_method=mp_method,
                save_results=True,
                data_file= os.path.join(data_dir, data_file),
                output_dir=OUTPUT_DIR,
                output_folder=mp_method,
                n_iter=5000,
                n_shuffle=2,
                burn_in=200,
                thinning=1,
                true_order_dict=true_order_dict,
                true_stages = true_stages,
                skip_heatmap=True,
                skip_traceplot=True,
                save_details=False,
                seed = 53
                )

        run_mpebm(
            save_results=True,
            data_file= os.path.join(data_dir, data_file),
            output_dir=OUTPUT_DIR,
            output_folder='saebm',
            n_iter=5000,
            n_shuffle=2,
            burn_in=200,
            thinning=1,
            true_order_dict=true_order_dict,
            true_stages = true_stages,
            skip_heatmap=True,
            skip_traceplot=True,
            save_details=False,
            seed = 53
        )