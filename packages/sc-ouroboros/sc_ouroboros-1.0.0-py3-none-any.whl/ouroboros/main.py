import argparse
import anndata as ad
import pandas as pd
import logging
logger = logging.getLogger(__name__)

import os
# Create output directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/ouroboros_run.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger()


from .ouroboros_functions import *

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 = all logs, 1 = info, 2 = warning, 3 = error

import socket

def trace_http_requests():
    import builtins
    import http.client

    original_request = http.client.HTTPConnection.request

    def wrapped_request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        print(f"[TRACE] HTTP request: {method} {self.host}{url}")
        return original_request(self, method, url, body, headers, encode_chunked=encode_chunked)

    http.client.HTTPConnection.request = wrapped_request

trace_http_requests()



import time

progress_frames = [
    """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⡶⢿⣟⡛⣿⢉⣿⠛⢿⣯⡈⠙⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⡾⠻⣧⣬⣿⣿⣿⣿⣿⡟⠉⣠⣾⣿⠿⠿⠿⢿⣿⣦⠀⠀⠀
⠀⠀⠀⠀⣠⣾⡋⣻⣾⣿⣿⣿⠿⠟⠛⠛⠛⠀⢻⣿⡇     ⠈⠛⠀⠀⠀
⠀⠀⠀⣸⣿⣉⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠈⢿⣇⠀⠀⠀
⠀⠀⢰⣿⣉⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⠀⠀⠀
⠀⠀⣾⣏⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣿⠉⣿⣿⣿⡇⠀⠀⠀⠀
        Data loaded""",
    """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⡶⢿⣟⡛⣿⢉⣿⠛⢿⣯⡈⠙⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⡾⠻⣧⣬⣿⣿⣿⣿⣿⡟⠉⣠⣾⣿⠿⠿⠿⢿⣿⣦⠀⠀⠀
⠀⠀⠀⠀⣠⣾⡋⣻⣾⣿⣿⣿⠿⠟⠛⠛⠛⠀⢻⣿⡇     ⠈⠛⠀⠀⠀
⠀⠀⠀⣸⣿⣉⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠈⢿⣇⠀⠀⠀⠀
⠀⠀⢰⣿⣉⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⠀⠀⠀⠀
⠀⠀⣾⣏⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣿⠉⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣿⡛⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠸⡿⢻⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢻⡟⢙⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠻⣿⡋⣻⣿⣿⣿⣦⣤⣀⣀⣀⠀⠀
⠀⠀⠀⠀⠀⠈⠻⣯⣤⣿⠻⣿⣿⣿⣿⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠾⣧⣼⣟⣉⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀
        Model loaded""",
    """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⡶⢿⣟⡛⣿⢉⣿⠛⢿⣯⡈⠙⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⡾⠻⣧⣬⣿⣿⣿⣿⣿⡟⠉⣠⣾⣿⠿⠿⠿⢿⣿⣦⠀⠀⠀
⠀⠀⠀⠀⣠⣾⡋⣻⣾⣿⣿⣿⠿⠟⠛⠛⠛⠀⢻⣿⡇     ⠈⠛⠀⠀⠀
⠀⠀⠀⣸⣿⣉⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠈⢿⣇⠀⠀⠀⠀
⠀⠀⢰⣿⣉⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⠀⠀⠀⠀
⠀⠀⣾⣏⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣿⠉⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣿⡛⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣧⣼⡇⠀⠀
⠀⠀⠸⡿⢻⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣥⣽⠁⠀⠀
⠀⠀⠀⢻⡟⢙⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣧⣸⡏⠀⠀⠀
⠀⠀⠀⠀⠻⣿⡋⣻⣿⣿⣿⣦⣤⣀⣀⣀⣀⣀⣠⣴⣿⣿⢿⣥⣼⠟⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠻⣯⣤⣿⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⣷⣴⡿⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠾⣧⣼⣟⣉⣿⣉⣻⣧⡿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀
    Cells embedded in VAE sphere """,
    """⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⡶⢿⣟⡛⣿⢉⣿⠛⢿⣯⡈⠙⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⡾⠻⣧⣬⣿⣿⣿⣿⣿⡟⠉⣠⣾⣿⠿⠿⠿⢿⣿⣦⠀⠀⠀
⠀⠀⠀⠀⣠⣾⡋⣻⣾⣿⣿⣿⠿⠟⠛⠛⠛⠀⢻⣿⡇⢀⣴⡶⡄⠈⠛⠀⠀⠀
⠀⠀⠀⣸⣿⣉⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠈⢿⣇⠈⢿⣤⡿⣦⠀⠀⠀⠀
⠀⠀⢰⣿⣉⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠦⠀⢻⣦⠾⣆⠀⠀⠀
⠀⠀⣾⣏⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⡶⢾⡀⠀⠀
⠀⠀⣿⠉⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⣼⡇⠀⠀
⠀⠀⣿⡛⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣧⣼⡇⠀⠀
⠀⠀⠸⡿⢻⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣥⣽⠁⠀⠀
⠀⠀⠀⢻⡟⢙⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣧⣸⡏⠀⠀⠀
⠀⠀⠀⠀⠻⣿⡋⣻⣿⣿⣿⣦⣤⣀⣀⣀⣀⣀⣠⣴⣿⣿⢿⣥⣼⠟⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠻⣯⣤⣿⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⣷⣴⡿⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠾⣧⣼⣟⣉⣿⣉⣻⣧⡿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀Sphere visualization complete⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""
]

def show_progress(stage):
    try:
        get_ipython  # Will raise NameError if not in IPython/Jupyter
        import sys
        from IPython.display import clear_output, display
        clear_output(wait=True)
        print(progress_frames[stage])
    except (NameError, ImportError):
        # CLI fallback
        print("\033c", end="")  # Terminal clear
        print(progress_frames[stage])



 
def run_ouroboros(data, data_type, species = 'human', outdir = '.', seed = 0, repeat = 1):
    """
    Run the full Ouroboros pipeline for projecting single-cell expression data
    into VAE spherical embedding space and using KNN to compute cell cycle phase, pseudotime and dormancy pseudotime.

    Parameters
    ----------
    data : str 
        Path to input file (needs to be either a 'h5ad' or a 'csv')
        - For 'h5ad': Anndata object
        - For 'csv' : expects a CSV with cells as rows and genes as columns, with a 'cell_id' index column - must be RAW COUNTS

    data_type : str
        Format of the input data, must be either 'h5ad' or 'csv'

    species : str {'human', 'mouse'}, optional (default='human')
        Species of origin. If 'mouse', gene names will be mapped to human orthologs.

    outdir : str, optional (default='.')
        Output directory where embedding and pseudotime files will be saved.

    Returns
    -------
    z_df : pandas.DataFrame
        A dataframe containing the spherical embedding coordinates (dim1, dim2, dim3),
        predicted states, and dormancy pseudotime for each cell.

    Outputs
    -------
    - ouroboros_embeddings_pseudotimes.csv
    - retrained_reference_embeddings.csv (if retraining is triggered)

    Notes
    -----
    - If key training genes are missing from the input data, the model will be retrained
      on the subset of genes available.
    - The output embeddings and pseudotimes can be used for visualization and downstream analysis.

    Example
    -------
    >>> run_ouroboros("sample.h5ad", "h5ad", species="human", outdir="results/")
    >>> python -m Ouroboros_pypi.Ouroboros.main \
    --data adata.h5ad  \
    --data_type h5ad \
    --species mouse \
    --outdir /path/to/outdir
    """

    if data_type == 'h5ad':
        data = ad.read_h5ad(data)
        if "raw_counts" in data.layers: 
            data.X = data.layers['raw_counts'].copy()
        
    elif data_type == 'csv':
        data = pd.read_csv(data)
        if "cell_id" in data.columns:
            data = data.set_index('cell_id')
        elif "Unnamed: 0" in data.columns:
            data = data.set_index('Unnamed: 0')
    else: 
        raise TypeError("Unsupported data type. Expected --h5ad or --csv for data_type.")

    show_progress(0)
        
    if species == 'mouse':
        logger.info('Converting mouse genes to human orthologs...')
        data = convert_to_human_genes(data)
        logger.info('Genes successfully converted to human orthologs')
    elif species == 'human':
        pass
    else:
        raise TypeError("Unsupported species. Model only optimized for --human or --mouse")

    missing = check_features(data)
    
    os.makedirs(outdir, exist_ok=True) 
    
    if len(missing) > 0:
        logger.warning(f"""Key training genes seem to be missing from your dataset\n
              Missing genes include: {missing}
              For higher accuracy consider including these genes in the matrix and running Ouroboros again.
              Retraining model without them......""")
        for i in range(repeat):
            curr_seed = seed + i
            curr_outdir = outdir + "/retrain/" + str(i)
            os.makedirs(curr_outdir, exist_ok=True)
            model, ref_embed, in_order_feature_set, trainer_model = ouroboros_retrain(data, curr_seed)
            ref_embed.to_csv(f'{curr_outdir}/retrained_reference_embeddings.csv')
            model.save_sess(f'{curr_outdir}/model')

            show_progress(1)
            z_df = embed_in_retrained_sphere(data, model, in_order_feature_set)
            show_progress(2)
            z_df = KNN_predict(ref_embed, z_df)
        
            z_df = calculate_cell_cycle_pseudotime(z_df, ref_embed,  phase_category = 'KNN_phase')
            pseud, ref_pseud = dormancy_depth(z_df, ref_embed, retrained = True)
            z_df = z_df.merge(pseud, how = 'left', left_index = True, right_index = True)
            z_df = qc_and_threshold(model, trainer_model, z_df, in_order_feature_set, ref_embed, curr_outdir, seed)
            z_df.to_csv(f'{curr_outdir}/ouroboros_embeddings_pseudotimes.csv')

        z_df, ref_embed = select_seed(repeat, outdir)
    else:
        logger.info('All training genes present, embedding your cells in VAE latent space...')
        matrix = ouroboros_preprocess(data, data_type)
        show_progress(1)
        z_df = ouroboros_embed(matrix, data, data_type, outdir = outdir)
        show_progress(2)
        # Read in known reference embeddings 
        ref_embed = pd.read_csv(DATA_DIR / 'reference_embeddings.csv')
        # set cell id to be index
        ref_embed = ref_embed.set_index('cell_id')

    z_df.to_csv(f'{outdir}/ouroboros_embeddings_pseudotimes.csv')
    try:
        plot_sphere(z_df, colour_by = 'cell_cycle_pseudotime', palette = None, ref = ref_embed, velocity = None, marker_size = 2, cycle_pole = reference_CC_pole_point, savefig = f'{outdir}/ouroboros_cell_cycle_pseudotime.html', show = False)
    except ValueError as e:
        logger.info(f"Caught error in cell_cycle_pseudotime plot: {e}")
    try:
        plot_sphere(z_df, colour_by = 'dormancy_pseudotime', palette = None, ref = ref_embed, velocity = None, marker_size = 2, cycle_pole = reference_CC_pole_point, savefig = f'{outdir}/ouroboros_dormancy_pseudotime.html', show = False)
    except ValueError as e:
        logger.info(f"Caught error in dormancy_pseudotime plot: {e}")

    show_progress(3)
    return z_df
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--data_type", choices=["csv", "h5ad"], required=True)
    parser.add_argument("--species", default="human")
    parser.add_argument("--outdir", default=".")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()

    run_ouroboros(args.data, args.data_type, species=args.species, outdir=args.outdir, seed=args.seed, repeat=args.repeat)


if __name__ == "__main__":
    main()
