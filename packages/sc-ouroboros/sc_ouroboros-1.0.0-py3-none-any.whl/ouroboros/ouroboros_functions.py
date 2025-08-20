import numpy as np
from matplotlib import pyplot as plt
from .scphere.model.vae import SCPHERE
from .scphere.util.trainer import Trainer
import pandas as pd
import anndata as ad
import plotly.graph_objects as go
import plotly.express as px
import scipy
from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
from sklearn.decomposition import PCA

from kneed import KneeLocator
from scipy.interpolate import UnivariateSpline
import tensorflow as tf
import random

import anndata as ad
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
from plotly.io import write_image
import seaborn as sns
from scipy.sparse import issparse
from scipy.spatial.transform import Rotation as R
from scipy import stats
import shutil
import matplotlib.patches as patches
import requests


reference_CC_pole_point = [0.86202236, 0.24824865, 0.44191636]

phase_pal_transition = {
    'G1':'#1f77b4',
       'S': '#ff7f0e',
       'G2M': '#2ca02c', 
       'G0': 'black', 
       'G1-G0 transition': '#d62728'}


def convert_to_human_genes(data):
    """Convert mouse gene names in an anndata object to their human orthologs (if existing)"""
    orth = pd.read_csv(DATA_DIR / "all_genes_mouse_orthologs.csv")
    
    if isinstance(data, ad.AnnData):
        adata = data[:, data.var_names.isin(list(orth.mouse_genes.astype(str)))]
        if adata.shape[1] == 0:
            raise ValueError("No genes in the input match known mouse genes with human orthologs.")
        mouse_orth = orth.set_index('mouse_genes')
        # Change mouse genes names to human orthologs
        adata.var = adata.var.merge(mouse_orth, how='left', left_index=True, right_index=True)
        adata.var_names = adata.var['human_genes']
        # Need to sum human genes that are accounted for by more than one mouse gene (i.e., they have duplicates)
        # Check if the matrix is sparse and convert it if necessary
        if scipy.sparse.issparse(adata.X):
            dense_matrix = adata.X.toarray()
        else:
            dense_matrix = adata.X
        counts_df = pd.DataFrame(dense_matrix.T, index=adata.var_names, columns=adata.obs_names)
        # Sum the counts for duplicated var_names
        summed_counts = counts_df.groupby(counts_df.index).sum()
        new_data = ad.AnnData(X=summed_counts.T.values, var=pd.DataFrame(index=summed_counts.index))
        new_data.obs_names = adata.obs_names
        new_data.obs = adata.obs
        
    elif isinstance(data, pd.DataFrame):
        # Subset to mouse genes that have human orthologs
        df = data.loc[:, data.columns.isin(orth['mouse_genes'])]
        if df.shape[1] == 0:
            raise ValueError("No genes in the input match known mouse genes with human orthologs.")
        # Map mouse genes to human orthologs
        mouse_to_human = orth.set_index('mouse_genes')['human_genes'].to_dict()
        df.columns = df.columns.map(mouse_to_human)
        # Collapse duplicated human gene symbols by summing across columns
        new_data = df.groupby(axis=1, level=0).sum()
    else:
        raise TypeError("Data must be pandas or adata")
        
    return new_data




def check_features(data):
    missing = []
    #csv_path = files("ouroboros.data").joinpath("SHAP_feature_set.csv")
    #feature_set = pd.read_csv(csv_path)
    feature_set = pd.read_csv(DATA_DIR / 'SHAP_feature_set.csv')
    feature_set = feature_set.feature_set.tolist()
    for feature in feature_set:
        if isinstance(data, ad.AnnData):
            if feature not in data.var_names.tolist():
                missing.append(feature)
        elif isinstance(data, pd.DataFrame):
            if feature not in list(data.columns):
                missing.append(feature)
        else:
            raise TypeError("Unsupported data type. Expected AnnData or DataFrame.")
    if len(missing) == len(feature_set):
        raise ValueError("None of the training genes found in data. Check that gene names (var_names) are Hugo symbol format")
    return missing


def check_genes(data):
    missing = []
    #csv_path = files("ouroboros.data").joinpath("SHAP_feature_set.csv")
    #feature_set = pd.read_csv(csv_path)
    feature_set = pd.read_csv(DATA_DIR / 'SHAP_feature_set.csv')
    feature_set = feature_set.feature_set.tolist()
    for feature in feature_set:
        if isinstance(data, ad.AnnData):
            if feature not in data.var_names.tolist():
                missing.append(feature)
        elif isinstance(data, pd.DataFrame):
            if feature not in list(data.columns):
                missing.append(feature)
        else:
            raise TypeError("Unsupported data type. Expected AnnData or DataFrame.")
    if len(missing) > 0:
        print('Some feature genes are missing from your anndata')
    else:
        print('No feature genes are missing from your anndata')
    return missing


def read_in_refembed():
    ref_embed = pd.read_csv(DATA_DIR / 'reference_embeddings.csv')
    # set cell id to be index
    ref_embed = ref_embed.set_index('cell_id')
    return ref_embed


def read_in_features():
    feature_set = pd.read_csv(DATA_DIR / 'SHAP_feature_set.csv')
    feature_set = feature_set.feature_set.tolist()
    return feature_set


def ouroboros_preprocess(data, data_type):
        # Load SHAP feature set
    feature_set = pd.read_csv(DATA_DIR / "SHAP_feature_set.csv").feature_set.tolist()
    gene_order = pd.read_csv(DATA_DIR / "gene_order.csv")
    gene_order = gene_order['gene_order'].tolist()
    
    if data_type == 'h5ad':
        bdata = data.copy()
        bdata = bdata[:, bdata.var_names.isin(feature_set)].copy()

        matrix = bdata.X.copy()
    
        if scipy.sparse.issparse(matrix):
            matrix = matrix.toarray()

        # Load gene order and reorder matrix
        new_data_df = pd.DataFrame(matrix, columns=bdata.var_names)
        aligned_new_data = new_data_df.loc[:, gene_order].values
        matrix = aligned_new_data.copy()
        
    elif data_type == 'csv':
        df = data
        # Subset to features and order properly
        df = df.loc[:, df.columns.isin(feature_set)]
        df_ordered = df.loc[:, gene_order]
        matrix = df_ordered.values

    return matrix


def ouroboros_embed(matrix, data, data_type, outdir = '.'):
    # Initialize SCPHERE model with same training parameters
    model = SCPHERE(
        n_gene=matrix.shape[1],
        n_batch=2,
        batch_invariant=False,
        z_dim=2,
        latent_dist='vmf',
        observation_dist='nb'
    )
    tf.compat.v1.reset_default_graph()
    model.load_sess(str(DATA_DIR / "model" / "model"))
    new_batch = np.full(matrix.shape[0], 2)

    # Project new data
    z_mean = model.encode(matrix, new_batch)
    
    if data_type == 'h5ad':
        z_mean_df = pd.DataFrame(z_mean, index=data.obs.index, columns=["dim1", "dim2", "dim3"])
    elif data_type == 'csv':
        z_mean_df = pd.DataFrame(z_mean, index=data.index, columns=["dim1", "dim2", "dim3"])
    
    ref_embed = pd.read_csv(DATA_DIR / 'reference_embeddings.csv')
    # set cell id to be index
    ref_embed = ref_embed.set_index('cell_id')
    
    z_mean_df = KNN_predict(ref_embed, z_mean_df)
    
    z_mean_df = calculate_cell_cycle_pseudotime(z_mean_df, ref_embed,  phase_category = 'KNN_phase')

    pseud = dormancy_depth(z_mean_df, ref_embed, retrained = False)
    z_mean_df = z_mean_df.merge(pseud, how = 'left', left_index = True, right_index = True)
    
    z_mean_df['G0_classification'] = np.where(
            z_mean_df['dormancy_pseudotime'] > -0.6, 'quiescence',
            np.where(
                z_mean_df['dormancy_pseudotime'] < -0.6, 'senescence',
                np.nan
            )
        ) 
    
    plot_sphere(z_mean_df, colour_by = 'KNN_phase', ref = ref_embed, marker_size = 2, cycle_pole = reference_CC_pole_point, savefig = f'{outdir}/ouroboros_KNN_sphere.html')
    return z_mean_df



def KNN_predict(ref_embed, z_df):
    # Step 1: Prepare data
    X_train_knn = ref_embed[["dim1", "dim2", "dim3"]].values
    y_train_knn = ref_embed["phase"].values

    z_df = z_df.copy()
    X_test_knn = z_df[["dim1", "dim2", "dim3"]].values

    # Step 2: Train the KNN classifier
    knn = KNeighborsClassifier(n_neighbors=25) 
    knn.fit(X_train_knn, y_train_knn)

    # Step 3: Predict cell cycle phases for the test set
    y_pred = knn.predict(X_test_knn)

    # Step 4: Add predictions to the test set DataFrame
    z_df["KNN_phase"] = y_pred

    return z_df


def ouroboros_retrain(test_adata, seed):
    """Useful if some training genes are missing in embedding dataset and you want to embed them in the riba-mahd embedding"""
    #Read in training data
    matrix = pd.read_csv(DATA_DIR / 'train_matrix.csv')
    train_meta = pd.read_csv(DATA_DIR / 'train_meta.csv')
    train_meta.set_index('Unnamed: 0', inplace = True)

    #csv_path = files("ouroboros.data").joinpath("SHAP_feature_set.csv")
    #feature_set = pd.read_csv(csv_path)
    feature_set = pd.read_csv(DATA_DIR / 'SHAP_feature_set.csv')
    feature_set = feature_set.feature_set.tolist()

    bdata = test_adata.copy()
    if isinstance(bdata, pd.DataFrame):
        test_genes = bdata.columns
    elif isinstance(bdata, ad.AnnData):
        test_genes = bdata.var_names
    else:
        raise TypeError("Expect test_adata to be a pandas DataFrame or an AnnData object.")

    present_features = []
    for feature in feature_set:
        if feature in test_genes:
            present_features.append(feature)
    new_feature_set = present_features
    matrix = matrix.loc[:, new_feature_set]
    in_order_feature_set = matrix.columns.tolist()
    matrix = matrix.values


    map_dict = {}
    for i, val in enumerate(train_meta['library'].unique()):
        map_dict[val] = i
    batch = train_meta['library'].map(map_dict).values

    set_seed(seed)
    tf.compat.v1.reset_default_graph()
    #Initilize model
    model = SCPHERE(n_gene=matrix.shape[1], n_batch=2, batch_invariant=False,
                z_dim=2, latent_dist='vmf',
                observation_dist='nb', seed=0)
    trainer = Trainer(model=model, x=matrix, batch_id=batch, max_epoch=250,
                  mb_size=128, learning_rate=0.001)
    
    #Train model 
    trainer.train()
    
    #Embed reference points
    z_mean = model.encode(matrix, batch)
    z_mean_df = pd.DataFrame(z_mean, index=train_meta.index, columns=["dim1", "dim2", 'dim3'])
    train_df = z_mean_df.merge(train_meta, how = 'left', left_index = True, right_index = True)
    
    
    return model, train_df, in_order_feature_set, trainer




def embed_in_retrained_sphere(adata, model, in_order_feature_set):
    bdata = adata.copy()

    if isinstance(bdata, pd.DataFrame):
        bdata = bdata[in_order_feature_set]
        matrix = bdata.copy()
        gene_list = list(matrix.columns)
        cell_list = list(matrix.index)
    elif isinstance(bdata, ad.AnnData):
        bdata = bdata[:, bdata.var_names.isin(in_order_feature_set)].copy()
        matrix = bdata.X.copy()
        gene_list = bdata.var_names
        cell_list = bdata.obs_names

    else:
        raise TypeError("Expect test_adata to be a pandas DataFrame or an AnnData object.")

    
    if scipy.sparse.issparse(matrix):
        matrix = matrix.toarray()

    # Need to make sure the new matrix has genes in the right order as the training matrix was 
    new_data_df = pd.DataFrame(matrix, columns=gene_list)
    aligned_new_data = new_data_df.loc[:, in_order_feature_set].values
    matrix = aligned_new_data.copy()

    new_batch = np.full(matrix.shape[0], 2)


    # Project the new data into the latent space
    z_mean = model.encode(matrix, new_batch)    
    z_mean_df = pd.DataFrame(z_mean, index=cell_list, columns=["dim1", "dim2", 'dim3'])
    return z_mean_df
    


def fit_great_circle(points):
    """ Fit a great circle around the sphere capturing variation along a set of points
    points = set of points"""
    # Perform PCA to find the plane
    pca = PCA(n_components=3)
    pca.fit(points)
    normal_vector = pca.components_[2]  # Normal vector to the plane
    plane_vectors = pca.components_[:2]  # Basis vectors for the plane

    # Generate great circle points
    t = np.linspace(0, 2 * np.pi, 100)
    circle_points = (
        np.outer(np.cos(t), plane_vectors[0]) +
        np.outer(np.sin(t), plane_vectors[1])
    )
    return circle_points,normal_vector



def find_cyc_center(z_df, ref_embed, phase_category = 'phase', _method = "ref"):
    """ Find a point on the sphere's surface that represents the centre of the cycling cells
    z_df: embedded points including cycling cells to find the centre of
    ref_embed: reference embedded points 
    phase_category: name of the columns with phase labels to parse (needs to have G1/S/G2M)"""

    if _method not in ['ref', 'z_df', 'both']:
        raise ValueError(f"Invalid method '{_method}'. Expected one of: 'ref', 'z_df', 'both'.")
    
    if _method == "both":
        curr_z_df = z_df.copy()
        curr_z_df['phase'] = curr_z_df[phase_category] 
        curr_z_df = pd.concat([curr_z_df, ref_embed])
    elif _method == 'z_df':
        curr_z_df = z_df.copy()
        curr_z_df['phase'] = curr_z_df[phase_category] 
    else:
        curr_z_df = ref_embed.copy()

    cyc = curr_z_df[curr_z_df['phase'].isin(['G2M', 'S', 'G1'])]
    points = cyc[['dim1', 'dim2', 'dim3']].values
    # Fit the great circle
    great_circle, normal_vector = fit_great_circle(points)
    top_center = normal_vector / np.linalg.norm(normal_vector)


    # Little test to make sure top point is in the middle of cycling cells and not G0 cells
    cyc = ref_embed[ref_embed['phase'].isin(['G2M', 'S', 'G1'])]
    points = cyc[['dim1', 'dim2', 'dim3']].values

    ## Get centroid of G1, S, G2M cells
    cyc_centroid = np.mean(points, axis=0)
    ## Get centroid of G0 cells
    g0 = ref_embed[ref_embed['phase'] == 'G0']
    g0_points = g0[['dim1', 'dim2', 'dim3']].values
    g0_centroid = np.mean(g0_points, axis=0)
    ## Compute dot products
    dot_cyc = np.dot(top_center, cyc_centroid)
    dot_g0 = np.dot(top_center, g0_centroid)
    ## If top_center aligns more with G0, flip it
    if dot_g0 > dot_cyc:
        top_center = -top_center
    return great_circle, top_center


def find_cycle_pole(z_df, ref_embed, phase_category = 'KNN_phase'):
    """ Find a point on the sphere's surface that represents the centre of the cycling cells
    z_df: embedded points including cycling cells to find the centre of
    ref_embed: reference embedded points 
    phase_category: name of the columns with phase labels to parse (needs to have G1/S/G2M)"""
    cyc = z_df[z_df[phase_category].isin(['G2M', 'S', 'G1'])]
    points = cyc[['dim1', 'dim2', 'dim3']].values
    # Fit the great circle
    great_circle, normal_vector = fit_great_circle(points)
    top_center = normal_vector / np.linalg.norm(normal_vector)

    # Little test to make sure top point is in the middle of cycling cells and not G0 cells
    cyc = ref_embed[ref_embed['phase'].isin(['G2M', 'S', 'G1'])]
    points = cyc[['dim1', 'dim2', 'dim3']].values

    ## Get centroid of G1, S, G2M cells
    cyc_centroid = np.mean(points, axis=0)
    ## Get centroid of G0 cells
    g0 = ref_embed[ref_embed['phase'] == 'G0']
    g0_points = g0[['dim1', 'dim2', 'dim3']].values
    g0_centroid = np.mean(g0_points, axis=0)
    ## Compute dot products
    dot_cyc = np.dot(top_center, cyc_centroid)
    dot_g0 = np.dot(top_center, g0_centroid)
    ## If top_center aligns more with G0, flip it
    if dot_g0 > dot_cyc:
        top_center = -top_center
    return top_center



def chop_sphere(df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3']):
    """
    Splits points on a sphere into two hemispheres using the equatorial plane,
    while preserving metadata.

    df: DataFrame containing 3D points and metadata.
    center: Center of the sphere (3D coordinates).
    axis_vector: Normal vector to the equatorial plane (North-South axis).
    dim_cols: Column names for the 3D coordinates in the DataFrame.

    Returns:
    north_df: DataFrame of points in the "north" hemisphere.
    south_df: DataFrame of points in the "south" hemisphere.
    """
    # Extract the points and normalize the axis vector
    points = df[dim_cols].values
    axis_vector = axis_vector / np.linalg.norm(axis_vector)

    # Compute signed distances to the equatorial plane
    signed_distances = np.dot(points - center, axis_vector)

    # Split the DataFrame based on distances
    north_df = df[signed_distances > 0].copy()
    south_df = df[signed_distances <= 0].copy()

    return north_df, south_df



def find_latitude_cutoff(df, center, axis_vector, phase_col='phase',
                         dim_cols=['dim1', 'dim2', 'dim3'], target_phases={'S', 'G2M'}, max_cells=3000):
    """
    LEGACY - not used anymore but kept as a neat piece of code 
    
    Iterates through increasing latitudes until reaching a latitude where below it
    there are no cells in target phases (S, G2M). Only returns the cutoff latitude.

    df: DataFrame containing 3D points and metadata.
    center: Center of the sphere (3D coordinates).
    axis_vector: Normal vector to the equatorial plane (North-South axis).
    phase_col: Column name containing cell phase information.
    dim_cols: Column names for the 3D coordinates in the DataFrame.
    target_phases: Set of phases (S, G2M) to track.
    max_cells: Maximum number of cells to use for determining latitude. If exceeded, a random subsample is taken.

    Returns:
    cutoff_latitude: The latitude threshold where below it there are no target phase cells.

    Raises:
    ValueError: If no valid cutoff latitude is found.
    """
    # Subsample if needed (for latitude determination only)
    if len(df) > max_cells:
        subsample_size = max_cells if max_cells % 2 == 0 else max_cells - 1  # Ensure even number
        sampled_df = df.sample(n=subsample_size, random_state=42)
    else:
        sampled_df = df.copy()

    # Normalize axis vector
    axis_vector = axis_vector / np.linalg.norm(axis_vector)

    # Compute vectors from the center
    points = sampled_df[dim_cols].values
    vectors = points - center

    # Compute cos(theta) = dot product of each point with axis vector, normalized
    cos_theta = np.dot(vectors, axis_vector) / np.linalg.norm(vectors, axis=1)

    # Convert to latitude in degrees
    latitudes = np.degrees(np.arcsin(cos_theta))

    # Add latitudes to the sampled DataFrame
    sampled_df['latitude'] = latitudes

    # Sort by latitude
    sampled_df = sampled_df.sort_values(by='latitude', ascending=False)

    # Iterate through latitudes to find the cutoff
    for lat in sampled_df['latitude'].unique():
        below_lat_df = sampled_df[sampled_df['latitude'] < lat]
        
        # Check if any cell below this latitude belongs to S or G2M
        if not below_lat_df[phase_col].isin(target_phases).any():
            return lat  # Return cutoff latitude only

    # If no cutoff found, raise an error
    raise ValueError("Separating cycling cells from non-cycling cells has failed. "
                     "Are you sure your embeddings are correct and cycling cells are present in this dataset?")





def project_to_equator(df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'], radius=1):
    """
    Projects 3D points onto the equatorial plane and flattens them into 2D coordinates.

    df: DataFrame containing 3D points and metadata.
    center: Center of the sphere (3D coordinates).
    axis_vector: Normal vector to the equatorial plane (North-South axis).
    dim_cols: Column names for the 3D coordinates in the DataFrame.
    radius: Radius of the 2D circle for normalization.

    Returns:
    projected_df: DataFrame with 2D projected coordinates and original metadata.
    """
    # Normalize the axis vector
    axis_vector = axis_vector / np.linalg.norm(axis_vector)

    # Find two orthogonal vectors to the axis vector
    arbitrary = np.array([1, 0, 0]) if abs(axis_vector[0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(axis_vector, arbitrary)  # First orthogonal vector
    u = u / np.linalg.norm(u)  # Normalize
    v = np.cross(axis_vector, u)  # Second orthogonal vector
    v = v / np.linalg.norm(v)  # Normalize

    # Extract points from DataFrame
    points = df[dim_cols].values

    # Project points onto the equatorial plane
    centered_points = points - center  # Shift points relative to the sphere center
    normal_component = np.dot(centered_points, axis_vector)[:, None] * axis_vector  # Projection onto normal
    projected_points = centered_points - normal_component  # Remove the normal component

    # Flatten into 2D coordinates
    x_coords = np.dot(projected_points, u)  # Project onto u (x-axis in 2D)
    y_coords = np.dot(projected_points, v)  # Project onto v (y-axis in 2D)


    # Create a new DataFrame with 2D coordinates
    projected_df = df.copy()
    projected_df['x'] = x_coords
    projected_df['y'] = y_coords

    return projected_df





def detect_phase_switch(data, angle_column='angle', phase_column='phase', bins=200):
    """
    Detects the angle at which the majority of cells switch from G2M to G1.

    Parameters:
    - data (pd.DataFrame): DataFrame containing the angle and phase information.
    - angle_column (str): Name of the column with angle values (in radians).
    - phase_column (str): Name of the column with phase information (e.g., 'G2M', 'G1').
    - bins (int): Number of bins to divide the angle into (default: 200).

    Returns:
    - switch_angle (float): Angle (in radians) where the majority switches from G2M to G1, or None if no switch detected.
    - binned_data (pd.DataFrame): DataFrame with bin statistics for further inspection.
    """
    # Create bins along the angle
    data['bin'] = pd.cut(data['angle'], bins=np.linspace(data['angle'].min(), data['angle'].max(), bins + 1), labels=False, include_lowest=True)

    # Count the number of cells in each phase for each bin
    binned_data = data.groupby('bin')['phase'].value_counts().unstack(fill_value=0)

    # What percentage of total counts in each bin are for each phase?
    row_sums = binned_data.sum(axis=1)
    binned_data_percent = (binned_data.div(row_sums, axis=0)) * 100
    binned_data_percent_filtered = binned_data_percent[['G1', 'S', 'G2M']]

    # We need to make sure that these bins are being calculated in increasing order along the cell cycle trajectory, so that when we find our G2M-G1 break it's in the right spot, and not in wrong direction
    # calculate what phase did we initially land in randomly?
    first_bin = binned_data_percent_filtered.iloc[0]
    first_phase = first_bin.idxmax()

    # Going along the bins 
    for i in range(0, len(binned_data_percent_filtered)):
            next_phase = binned_data_percent_filtered.iloc[i].idxmax()
            if next_phase != first_phase:
                    break

    # A dictionary of which phase should come after the inital phase 
    progresssion_dict = {'G1': 'S', 'G2M': 'G1', 'S': 'G2M'}

    next_phase_should_be = progresssion_dict[first_phase]
    if next_phase != next_phase_should_be:
            # Flip the bin order by reversing the angle
            data['angle'] = -data['angle']  # Reverse angles
            data['bin'] = pd.cut(
                    data['angle'], 
                    bins=np.linspace(data['angle'].min(), data['angle'].max(), bins + 1), 
                    labels=False, 
                    include_lowest=True
            )

            # Recompute binned data
            binned_data = data.groupby('bin')['phase'].value_counts().unstack(fill_value=0)
            row_sums = binned_data.sum(axis=1)
            binned_data_percent = (binned_data.div(row_sums, axis=0)) * 100
            flipped = True
    else:
        flipped = False

    # Determine the dominant phase in each bin
    binned_data_percent['dominant_phase'] = binned_data_percent.idxmax(axis=1)
    # Identify where the switch occurs from G2M to G1
    switch_angle = None
    bin_edges = np.linspace(data['angle'].min(), data['angle'].max(), bins + 1)

    for i in range(1, len(binned_data_percent)):
            if binned_data_percent['dominant_phase'].iloc[i - 1] == 'G2M' and binned_data_percent['dominant_phase'].iloc[i] == 'G1':
                    # Calculate the midpoint of the bin where the switch occurs
                    switch_angle = (bin_edges[i - 1] + bin_edges[i]) / 2
                    break

    if switch_angle == None:
           print('No switch angle found - recheck your reference embedding and make sure it makes sense')
    return switch_angle, binned_data, flipped


def adjust_angles(data, angle_column, switch_angle):
    """
    Adjust angles such that the switch angle becomes 0.

    Parameters:
    - data (pd.DataFrame): DataFrame containing the angle information.
    - angle_column (str): Name of the column with angle values (in radians).
    - switch_angle (float): The angle (in radians) to set as 0.

    Returns:
    - adjusted_data (pd.DataFrame): DataFrame with adjusted angles.
    """
    # Adjust angles by subtracting the switch angle
    data['adjusted_angle'] = (data[angle_column] - switch_angle) % (2 * np.pi)
    return data




def check_direction(projected_df, phases_to_check):
    """
    Check if most cells in the initial bins belong to the specified phase(s).

    Parameters:
    - projected_df (DataFrame): The input DataFrame containing 'adjusted_angle' and 'phase'.
    - phases_to_check (str or list of str): The phase(s) to check in the initial bins.

    Returns:
    - bool: True if most cells in the initial bins are in the specified phase(s), False otherwise.
    """
    # Ensure phases_to_check is a list
    if isinstance(phases_to_check, str):
        phases_to_check = [phases_to_check]

    # Define bin edges based on the range of adjusted_angle
    min_angle = projected_df['adjusted_angle'].min()
    max_angle = projected_df['adjusted_angle'].max()
    bin_edges = np.linspace(min_angle, max_angle, 30 + 1)

    # Perform binning
    data = projected_df.copy()
    data['bin'] = pd.cut(data['adjusted_angle'], bins=bin_edges, labels=False, include_lowest=True)

    # Count phase occurrences in the first few bins
    binned_data = data.groupby('bin')['phase'].value_counts().unstack(fill_value=0)
    initial_bins = binned_data.iloc[:5]

    # Sum counts for each phase across the initial bins
    phase_totals = initial_bins.sum(axis=0)

    # Sum the counts for the specified phases
    total_in_phases = phase_totals[phases_to_check].sum()

    # Compare the total in the specified phases to the total in other phases
    most_in_phases = total_in_phases > phase_totals.drop(phases_to_check).sum()

    return most_in_phases




def recalculate_ref_CC_pseudotime(reference_df, surface_point = reference_CC_pole_point):
    center = np.array([0, 0, 0])
    axis_vector = surface_point / np.linalg.norm(surface_point)

    north_df, south_df = chop_sphere(reference_df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'])
    
    projected_df = project_to_equator(north_df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'], radius=1)

        # Compute the angle (in radians) for each point
    angle_offset = np.pi / 2.25  # Shift the starting angle to the positive y-axis

    # Compute the angle and apply the offset
    projected_df['angle'] = np.arctan2(projected_df['y'], projected_df['x']) + angle_offset

    bin_sizes = [200, 300, 400, 500, 600, 700]  # List of bin sizes to test

    for bins in bin_sizes:
        switch_angle, binned_data, flipped = detect_phase_switch(projected_df, bins=bins)
        if switch_angle is not None:  # Break if a switch angle is detected
            #print(f"Switch angle detected... computing cell cycle pseudotime....")
            break
        else:
            print("No switch angle detected with the tested bin sizes.")
        
        
    
    projected_df['adjusted_angle'] = (projected_df['angle'] - switch_angle) % (2 * np.pi)

    #projected_df = adjust_angles(projected_df, angle_column='angle', switch_angle=switch_angle)

    right_way = check_direction(projected_df, phases_to_check = ['G1'])
    if right_way == False: 
        projected_df['adjusted_angle'] = projected_df['adjusted_angle']*-1
    
    if projected_df['adjusted_angle'][0] < 0:
        direction = 'negative direction'
    else:
        direction = 'positive_direction'


    return switch_angle, direction, projected_df, flipped




def calculate_new_CC_pseudotime(z_df, switch_angle, direction, flipped,  surface_point = reference_CC_pole_point, phase_col = 'KNN_phase'):

    center = np.array([0, 0, 0])
    axis_vector = surface_point / np.linalg.norm(surface_point)

    north_df, south_df = chop_sphere(z_df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'])

    projected_df = project_to_equator(north_df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'], radius=1)

        # Compute the angle (in radians) for each point
    angle_offset = np.pi / 2.25  # Shift the starting angle to the positive y-axis

    # Compute the angle and apply the offset
    projected_df['angle'] = np.arctan2(projected_df['y'], projected_df['x']) + angle_offset

    if flipped == True:
        projected_df['angle'] = -projected_df['angle'] 

    #now we adjust our angles with the switch angle we calculated from the reference embedding 
    projected_df = adjust_angles(projected_df, angle_column='angle', switch_angle=switch_angle)

    # Efficiently access the first value
    first_angle = projected_df['adjusted_angle'].iloc[0]  

    # Determine the direction
    new_df_direction = 'negative direction' if first_angle < 0 else 'positive_direction'

    # Only adjust if the direction differs
    if new_df_direction != direction:
        projected_df['adjusted_angle'] *= -1  # Element-wise multiplication is vectorized and fast

    # Normalize angles to range [0, 1] for pseudotime (this step is likely slow on large data)
    projected_df['cell_cycle_pseudotime'] = projected_df['adjusted_angle'].div(2 * np.pi)  # Faster than `/`
    return projected_df


def calculate_new_CC_pseudotime_lat(z_df, switch_angle, direction, surface_point = reference_CC_pole_point, phase_col = 'KNN_phase'):
    #This is all to the originally trained reference 
    center = np.array([0, 0, 0])
    axis_vector = surface_point / np.linalg.norm(surface_point)
    lat = find_latitude_cutoff(z_df, center, axis_vector, phase_col=phase_col,
                        dim_cols=['dim1', 'dim2', 'dim3'], target_phases={'S', 'G2M'})
    # Normalize axis vector
    axis_vector = axis_vector / np.linalg.norm(axis_vector)
    # Compute vectors from the center
    points = z_df[['dim1', 'dim2', 'dim3']].values
    vectors = points - center
    # Compute cos(theta) = dot product of each point with axis vector, normalized
    cos_theta = np.dot(vectors, axis_vector) / np.linalg.norm(vectors, axis=1)
    # Convert to latitude in degrees
    latitudes = np.degrees(np.arcsin(cos_theta))
    z_df['latitude'] = latitudes
    north_df = z_df[z_df['latitude'] >= lat].copy()
    
    projected_df = project_to_equator(north_df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'], radius=1)
    # Compute the angle (in radians) for each point
    angle_offset = np.pi / 2.25  # Shift the starting angle to the positive y-axis

    # Compute the angle and apply the offset
    projected_df['angle'] = np.arctan2(projected_df['y'], projected_df['x']) + angle_offset

    #now we adjust our angles with the switch angle we calculated from the reference embedding 
    projected_df = adjust_angles(projected_df, angle_column='angle', switch_angle=switch_angle)

    # Efficiently access the first value
    first_angle = projected_df['adjusted_angle'].iloc[0]  

    # Determine the direction
    new_df_direction = 'negative direction' if first_angle < 0 else 'positive_direction'

    # Only adjust if the direction differs
    if new_df_direction != direction:
        projected_df['adjusted_angle'] *= -1  # Element-wise multiplication is vectorized and fast

    # Normalize angles to range [0, 1] for pseudotime (this step is likely slow on large data)
    projected_df['cell_cycle_pseudotime'] = projected_df['adjusted_angle'].div(2 * np.pi)  # Faster than `/`
    return projected_df



def calculate_cell_cycle_pseudotime(z_df, ref_embed,  phase_category = 'KNN_phase'):
    great_circle, top_center = find_cyc_center(z_df, ref_embed, phase_category = 'KNN_phase')
    switch_angle, direction, ref_projected_df, flipped = recalculate_ref_CC_pseudotime(ref_embed, surface_point = top_center)

    df = calculate_new_CC_pseudotime(z_df, switch_angle, direction, flipped, surface_point = top_center)
    if df['cell_cycle_pseudotime'].iloc[0] < 0:
        df['cell_cycle_pseudotime'] = df['cell_cycle_pseudotime'] + 1
    df = df[['cell_cycle_pseudotime', 'x', 'y']]
    df.rename(columns = {'x': 'CC_x', 'y': 'CC_y'}, inplace = True)
    cc_df = df[['cell_cycle_pseudotime']]
    z_df = z_df.merge(cc_df, how = 'left', left_index = True, right_index = True)
    return z_df



def fit_g0_great_circle(points, pcs=(1, 2)):
    """
    Fit a great circle on the sphere using specified principal components.

    points: ndarray
        A set of 3D coordinates.
    pcs: tuple
        The indices of the principal components to use for defining the plane (default: (1, 2)).

    Returns:
    circle_points: ndarray
        Coordinates of the great circle points.
    normal_vector: ndarray
        Normal vector to the fitted plane.
    """
    # Perform PCA to find the plane
    pca = PCA(n_components=3)
    pca.fit(points)
    
    # Extract the principal components
    normal_vector = pca.components_[pcs[0] - 1]  # Adjusting for 0-based indexing
    plane_vectors = [pca.components_[pcs[1] - 1], pca.components_[3 - sum(pcs) - 1]]  # Other two components

    # Generate great circle points
    t = np.linspace(0, 2 * np.pi, 100)
    circle_points = (
        np.outer(np.cos(t), plane_vectors[0]) +
        np.outer(np.sin(t), plane_vectors[1])
    )

    return circle_points, normal_vector


def find_g0_center(z_df, phase_category = 'phase'):
    cyc = z_df[z_df[phase_category].isin(['G0', 'G1-G0 transition'])]
    points = cyc[['dim1', 'dim2', 'dim3']].values
    
    # Use PCs 2 and 3 instead of PCs 3 and 4
    great_circle, normal_vector = fit_g0_great_circle(points, pcs=(2, 3))

    # Normalize the normal vector to get the "top center"
    top_center = normal_vector / np.linalg.norm(normal_vector)

    return great_circle, top_center





def make_ref_bin_df_from_g0_tip(projected_df):
    #Start by assigning angles around the flat circle 
    angle_offset = np.pi / 2.3  
    # Compute the raw angle and apply the offset
    projected_df['angle'] = np.arctan2(projected_df['y'], projected_df['x']) + angle_offset
    # Wrap the angles to the range [0, 2π]
    projected_df['angle'] = np.mod(projected_df['angle'], 2 * np.pi)

    # Drop the NA values just in case (there shouldn't be any NAs - this is a relic just in case)
    bin_df = projected_df.dropna(subset = ['angle'])


    # Bin cells along angles so we can find gap between G0 and cell cycle, which tells us where to start our pseudotime 
    min_angle = bin_df['angle'].min()
    max_angle = bin_df['angle'].max()
    bin_edges = np.linspace(min_angle, max_angle, 15 + 1)
    bin_df['bin'] = pd.cut(bin_df['angle'], bins=bin_edges, labels=False, include_lowest=True)
    # calculate the number of each cell in each bin
    binned_data = bin_df.groupby('bin')['phase'].value_counts().unstack(fill_value=0)
    # Find the bin with the lowest total count
    total_counts_per_bin = binned_data.sum(axis=1)
    lowest_count_bin = int(total_counts_per_bin.idxmin())

    # Have total counts be a part of bin_df
    binned_data['total_counts'] = total_counts_per_bin
    binned_data = binned_data.reset_index()
    bin_df = bin_df.merge(binned_data, how= 'left', on = 'bin')

    #Find the edges of the bin that has the lowest counts (i.e. is between the G0 tip and the cell cycle)
    bin_start = bin_edges[lowest_count_bin]
    bin_end = bin_edges[lowest_count_bin + 1]

    # Find the values of the bins on either side of the bin with lowest counts
    next_lowest_count_bin = lowest_count_bin -1
    next_highest_count_bin = lowest_count_bin + 1

    # Find which bin on either side of bin with lowest counts has more G0 cells (so we can set the start of the angle to find the G0 tip as the start of the G0 tip)
    binned_data_subset = binned_data[binned_data['bin'].isin([next_lowest_count_bin, next_highest_count_bin])]
    high_g0_bin = binned_data_subset['G0'].idxmax()
    high_g0_bin_idx = int(binned_data_subset.loc[high_g0_bin, 'bin'])  
    #Find the edges of the bin with the most G0 counts
    high_g0_bin_start = bin_edges[high_g0_bin_idx]
    high_g0_bin_end = bin_edges[high_g0_bin_idx + 1]

    # Find the border that intersects the bin with lowest total counts and the bin with more G0 
    lowest_count_bin_boundaries = {bin_start, bin_end}
    high_g0_bin_boundaries = {high_g0_bin_start, high_g0_bin_end}
    shared_boundary = lowest_count_bin_boundaries.intersection(high_g0_bin_boundaries)
    shared_boundary_value = next(iter(shared_boundary))

    # Change the start of the angle calculation to be the start of the cycling cells 
    switch_angle = shared_boundary_value

    bin_df['adjusted_angle'] = bin_df['angle'] - switch_angle
    bin_df['adjusted_angle'] = bin_df['adjusted_angle'] % (2 * np.pi)


    # Make sure the angle is progressing numerically up through the cycling cells, and not backwards through the G0 cells 
    right_way = check_direction(bin_df, ['G1', 'S', 'G2M'])
    # Switch the angle direction if necessary 
    if right_way == False: 
        bin_df['adjusted_angle'] = bin_df['adjusted_angle']*-1
        switched = True
    else:
        switched = False
    #Set direction for future use
    if bin_df['adjusted_angle'][0] < 0:
        direction = 'negative direction'
    else:
        direction = 'positive_direction'

        # Normalize the angle to the range [0, 1] for pseudotime
    bin_df['dormancy_pseudotime'] = bin_df['adjusted_angle'] / (2 * np.pi)
    return bin_df, switch_angle, switched 




def make_z_bin_df(z_projected_df, switch_angle, switched):
    #Start by assigning angles around the flat circle 
    angle_offset = np.pi / 2.3  
    # Compute the raw angle and apply the offset
    z_projected_df['angle'] = np.arctan2(z_projected_df['y'], z_projected_df['x']) + angle_offset
    # Wrap the angles to the range [0, 2π]
    z_projected_df['angle'] = np.mod(z_projected_df['angle'], 2 * np.pi)
    # Drop the NA values just in case (there shouldn't be any NAs - this is a relic just in case)
    bin_df = z_projected_df.dropna(subset = ['angle'])
    bin_df['adjusted_angle'] = bin_df['angle'] - switch_angle
    bin_df['adjusted_angle'] = bin_df['adjusted_angle'] % (2 * np.pi)
    if switched == True:
        bin_df['adjusted_angle'] = bin_df['adjusted_angle']*-1
            # Normalize the angle to the range [0, 1] for pseudotime
    bin_df['dormancy_pseudotime'] = bin_df['adjusted_angle'] / (2 * np.pi)
    return bin_df


def find_g0_tip(bin_df):
    "Find the tip of G0 in reference so it can be used as the deepest point of G0"
    outer_df = bin_df.copy()
    # Define the smaller radius for classification
    inner_radius = 0.6  # Example: Classify points within a radius of 0.5
    # Calculate the distance from the center (0, 0)
    outer_df['distance'] = np.sqrt(outer_df['x']**2 + outer_df['y']**2)
    # Classify points within the inner radius as 'NaN' or a label
    outer_df['dormancy_pseudotime'] = np.where(
        outer_df['distance'] <= inner_radius,
        np.nan,  # Assign NaN to inner points
        outer_df['dormancy_pseudotime']  # Keep original classification for outer points
    )
    # Now use the new adjusted angle to find the center of the points around the G0 tip in spherical space
    if outer_df['dormancy_pseudotime'].min() < 0:
        high_g0 = outer_df[outer_df['dormancy_pseudotime'] > -0.1]
    else:
        high_g0 = outer_df[outer_df['dormancy_pseudotime'] > 0.9]
    ## Extract the points
    points = high_g0[['dim1', 'dim2', 'dim3']].values
    ## Compute the Cartesian median
    median_cartesian = np.median(points, axis=0)
    ## Normalize to project onto the sphere
    g0_tip = median_cartesian / np.linalg.norm(median_cartesian)
    return g0_tip



def find_g0_transition_point(bin_df, reference_df, phase_category = 'KNN_phase'):
    #Bin cells along angles so we can find gap between G0 and cell cycle
    min_angle = bin_df['dormancy_pseudotime'].min()
    max_angle = bin_df['dormancy_pseudotime'].max()
    bin_edges = np.linspace(min_angle, max_angle, 40 + 1)
    bin_df['bin'] = pd.cut(bin_df['dormancy_pseudotime'], bins=bin_edges, labels=False, include_lowest=True)

    binned_data = bin_df.groupby('bin')[phase_category].value_counts().unstack(fill_value=0)

    # Calculate the total cells in each bin
    binned_data['total_cells'] = binned_data.sum(axis=1)
    # Calculate proportions of each phase
    proportions = binned_data.div(binned_data['total_cells'], axis=0)
    # Identify the combined proportion of G1, S, and G2M
    proportions['G1_S_G2M'] = proportions[['G1', 'S', 'G2M']].sum(axis=1)
    # Iterate through the bins to find where G1_S_G2M < G1-G0

    for bin_idx, row in proportions.iterrows():
        if row['G1_S_G2M'] < row['G1-G0 transition']:
            transition_bin = bin_idx
            break
    # find cells in transition bin 
    transition_cells = bin_df[bin_df['bin'] == transition_bin]
    points = transition_cells[['dim1', 'dim2', 'dim3']].values

    ## Give them latitudes so we know which is highest on the sphere 
    # Compute cyclic center and reference vector (top_center)
    great_circle, ref_top_center = find_cyc_center(reference_df, reference_df, phase_category='phase')
    # Ensure top_center is a unit vector
    ref_top_center = ref_top_center / np.linalg.norm(ref_top_center)
    # Compute dot products
    dot_products = np.dot(points, ref_top_center)
    # Compute norms
    norms = np.linalg.norm(points, axis=1)
    # Compute ratios (dot product divided by norms)
    ratios = np.clip(dot_products / norms, -1, 1)
    # Compute angles (latitude) using arccos
    latitudes = np.arccos(ratios)
    # Store latitudes in DataFrame
    transition_cells['latitudes'] = latitudes

    min_lat = transition_cells['latitudes'].min()
    transition_cell = transition_cells[transition_cells['latitudes'] == min_lat]
    transition_cell = transition_cell.index[0]

    return transition_cell




def assign_new_retrained_g0_pseudotime(bin_df, g0_tip, transition_cell):
    points = bin_df[['dim1', 'dim2', 'dim3']].values
    # Compute dot product between points and the tip of G0
    dot_products = np.dot(points, g0_tip)
    # Compute latitude of points from G0 tip
    latitude = np.arccos(dot_products / np.linalg.norm(points, axis=1))
    bin_df['g0_latitude'] = latitude

    trans_latitude = bin_df[bin_df.index == transition_cell]['g0_latitude'][0]
    bin_df['dormancy_pseudotime'] = np.where(bin_df['g0_latitude'] > trans_latitude, np.nan, bin_df['g0_latitude'])
    # Find min and max g0_pseudotime values (excluding NaNs)
    min_pseudotime = bin_df['dormancy_pseudotime'].min()
    max_pseudotime = trans_latitude  # Transition latitude (upper bound)

    # Normalize g0_pseudotime to [-1, 0]
    bin_df['dormancy_pseudotime'] = -1 + (bin_df['dormancy_pseudotime'] - min_pseudotime) / (max_pseudotime - min_pseudotime)

    # Ensure NaN values stay NaN
    bin_df['dormancy_pseudotime'] = np.where(bin_df['g0_latitude'] > trans_latitude, np.nan, bin_df['dormancy_pseudotime'])

    return bin_df, trans_latitude


def assign_dormancy_depth_in_reference(z_df, ref_embed, g0_tip):
    embed = ref_embed.copy()
    center = [0, 0, 0]
    great_circle, surface_point = find_cyc_center(z_df=z_df, ref_embed=ref_embed, phase_category='KNN_phase')
    axis_vector = surface_point / np.linalg.norm(surface_point)
    north_df, south_df = chop_sphere(ref_embed, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'])

    points = embed[['dim1', 'dim2', 'dim3']].values
    dot_products = np.dot(points, g0_tip)
    latitude = np.arccos(dot_products / np.linalg.norm(points, axis=1))
    embed['g0_latitude'] = latitude
    embed['south'] = embed.index.isin(south_df.index.tolist())

    embed['dormancy_pseudotime'] = np.where(embed['south'], embed['g0_latitude'], np.nan)

    min_lat = embed['dormancy_pseudotime'].min()
    max_lat = embed['dormancy_pseudotime'].max()

    embed['dormancy_pseudotime'] = -1 + (embed['dormancy_pseudotime'] - min_lat) / (max_lat - min_lat)

    return embed, min_lat, max_lat

""""def assign_dormancy_depth_in_reference(ref_embed, g0_tip):
    embed = ref_embed.copy()
    center = [0, 0, 0]
    great_circle, surface_point = find_cyc_center(z_df=ref_embed, ref_embed=ref_embed, phase_category='phase')
    axis_vector = surface_point / np.linalg.norm(surface_point)
    north_df, south_df = chop_sphere(embed, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'])

    points = embed[['dim1', 'dim2', 'dim3']].values
    dot_products = np.dot(points, g0_tip)
    latitude = np.arccos(dot_products / np.linalg.norm(points, axis=1))
    embed['g0_latitude'] = latitude
    embed['south'] = embed.index.isin(south_df.index.tolist())

    embed['dormancy_depth'] = np.where(embed['south'], embed['g0_latitude'], np.nan)

    min_lat = embed['dormancy_depth'].min()
    max_lat = embed['dormancy_depth'].max()

    embed['dormancy_depth'] = -1 + (embed['dormancy_depth'] - min_lat) / (max_lat - min_lat)

    return embed, min_lat, max_lat"""



def assign_g0_pseud_to_all_cells(z_bin_df, g0_tip):
    points = z_bin_df[['dim1', 'dim2', 'dim3']].values
    # Compute dot product between points and the tip of G0
    dot_products = np.dot(points, g0_tip)
    # Compute latitude of points from G0 tip
    latitude = np.arccos(dot_products / np.linalg.norm(points, axis=1))
    z_bin_df['g0_latitude'] = latitude
    
    trans_latitude = z_bin_df['g0_latitude'].max()
    z_bin_df['dormancy_pseudotime'] = np.where(z_bin_df['g0_latitude'] > trans_latitude, np.nan, z_bin_df['g0_latitude'])
    # Find min and max g0_pseudotime values (excluding NaNs)
    min_pseudotime = z_bin_df['dormancy_pseudotime'].min()
    max_pseudotime = trans_latitude  # Transition latitude (upper bound)

    # Normalize g0_pseudotime to [-1, 0]
    z_bin_df['dormancy_pseudotime'] = -1 + (z_bin_df['dormancy_pseudotime'] - min_pseudotime) / (max_pseudotime - min_pseudotime)
    # Ensure NaN values stay NaN
    z_bin_df['dormancy_pseudotime'] = np.where(z_bin_df['g0_latitude'] > trans_latitude, np.nan, z_bin_df['dormancy_pseudotime'])
    return z_bin_df, trans_latitude






def dormancy_depth(z_df, ref_embed, retrained = False):
    center = np.array([0, 0, 0])
    if retrained == True:
        # Need to find the reference G0 tip to set the deepest point of G0 pseudotime 
        ## Find the point that puts G0 cells around the outside edge of a flattened circle
        great_circle, surface_point = find_g0_center(ref_embed, phase_category = 'phase')
        ## Make a vector through the sphere based on that point we can use for flattening it out 
        axis_vector = surface_point / np.linalg.norm(surface_point)
        center = np.array([0, 0, 0])
        ref_projected_df = project_to_equator(ref_embed, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'], radius=1)
        # This function finds the point around the flattened circle that the tip of G0 begins, and creates bins and an angle along it starting in the cycling part of the circle
        ref_bin_df, switch_angle, switched  = make_ref_bin_df_from_g0_tip(ref_projected_df)
        # This function find the center of the tip of G0 so it can be used as the deepest part of G0 pseudotime 
        g0_tip = find_g0_tip(ref_bin_df)
        
        # Assign dormancy depth in new reference embedding, and find min/max latitude values to normalize G0 pseudotime by 
        embed, min_lat, max_lat = assign_dormancy_depth_in_reference(z_df, ref_embed, g0_tip)
        
        # Southern half of sphere without cell cycle pseudotime needs to be assigned dormancy pseudotime 
        great_circle, surface_point = find_cyc_center(z_df, ref_embed, phase_category = 'KNN_phase')
        center = np.array([0, 0, 0])
        axis_vector = surface_point / np.linalg.norm(surface_point)
        north_df, south_df = chop_sphere(z_df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'])
        #Assign which cells are in that southern hemisphere in my flattened bin df so we know which cells to assign a G0 pseudotime to 
        z_df['south'] = z_df.index.isin(south_df.index)

        bin_df = z_df.copy()
        # To find pseudotime, calculate the latitude distance from the tip of G0 that we have decided will be the deepest point of G0 
        points = bin_df[['dim1', 'dim2', 'dim3']].values
        # Compute dot product between points and the tip of G0
        dot_products = np.dot(points, g0_tip)
        # Compute latitude of points from G0 tip
        latitude = np.arccos(dot_products / np.linalg.norm(points, axis=1))
        #Use that latitude distance as dormancy_depth 
        bin_df['g0_latitude'] = latitude

        # Normalize those cells to fall within -1 - 0 as dormancy depth 
        bin_df['dormancy_pseudotime'] = np.where(
            bin_df['south'],
            -1 + (bin_df['g0_latitude'] - min_lat) / (max_lat - min_lat),
            np.nan
        )
        pseud = bin_df[['dormancy_pseudotime']]
        ref_pseud = embed[['dormancy_pseudotime']]
        #pseud = bin_df[['dormancy_depth']]
        'Yay! We found some pseudotime - dont forget to double check that the reference G0 pseudotime makes sense too as we are still debugging this feature :D'
        return pseud, ref_pseud
    else:
        ref_g0_tip = [-0.35114564, -0.73546242, -0.57947542]
        ref_min_lat = 0.015271065556053379
        ref_max_lat = 2.322424776189219
        
         # Southern half of sphere without cell cycle pseudotime needs to be assigned dormancy pseudotime 
        great_circle, surface_point = find_cyc_center(z_df, ref_embed, phase_category = 'KNN_phase')
        center = np.array([0, 0, 0])
        axis_vector = surface_point / np.linalg.norm(surface_point)
        north_df, south_df = chop_sphere(z_df, center, axis_vector, dim_cols=['dim1', 'dim2', 'dim3'])
        #Assign which cells are in that southern hemisphere in my flattened bin df so we know which cells to assign a G0 pseudotime to 
        z_df['south'] = z_df.index.isin(south_df.index)

        bin_df = z_df.copy()
        # To find pseudotime, calculate the latitude distance from the tip of G0 that we have decided will be the deepest point of G0 
        points = bin_df[['dim1', 'dim2', 'dim3']].values
        # Compute dot product between points and the tip of G0
        dot_products = np.dot(points, ref_g0_tip)
        # Compute latitude of points from G0 tip
        latitude = np.arccos(dot_products / np.linalg.norm(points, axis=1))
        #Use that latitude distance as dormancy_depth 
        bin_df['g0_latitude'] = latitude

        # Normalize those cells to fall within -1 - 0 as dormancy depth 
        bin_df['dormancy_pseudotime'] = np.where(
            bin_df['south'],
            -1 + (bin_df['g0_latitude'] - ref_min_lat) / (ref_max_lat - ref_min_lat),
            np.nan
        )
        pseud = bin_df[['dormancy_pseudotime']]
        return pseud 
    
   



reference_CC_pole_point = [0.86202236, 0.24824865, 0.44191636]

phase_pal_transition = {
    'G1':'#1f77b4',
       'S': '#ff7f0e',
       'G2M': '#2ca02c', 
       'G0': 'black', 
       'G1-G0 transition': '#d62728'}


def is_continuous(series):
    return pd.api.types.is_numeric_dtype(series) and series.nunique() > 10


def make_sphere_surface(radius, points=300):
    phi = np.linspace(0, np.pi, points)
    theta = np.linspace(0, 2 * np.pi, points)
    phi, theta = np.meshgrid(phi, theta)
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return go.Surface(x=x, y=y, z=z, colorscale=[[0, 'lightgray'], [1, 'lightgray']],
                      opacity=1, showscale=False, name='', legendgroup='none',
                      contours=dict(x=dict(show=False), y=dict(show=False), z=dict(show=False)))

def project_above_sphere(x, y, z, radius, offset):
    points = np.stack([x, y, z], axis=1)
    normals = points / np.linalg.norm(points, axis=1, keepdims=True)
    projected_points = normals * (radius + offset)
    return projected_points[:, 0], projected_points[:, 1], projected_points[:, 2]


def make_pole_trace(pole, name, color, width, radius, extension=1.3):
    point = np.array(pole)
    point_norm = point / np.linalg.norm(point) * radius
    opp = -point_norm
    return go.Scatter3d(
        x=[point_norm[0]*extension, opp[0]*extension],
        y=[point_norm[1]*extension, opp[1]*extension],
        z=[point_norm[2]*extension, opp[2]*extension],
        mode='lines',
        line=dict(color=color, width=width),
        name=name
    )


def make_reference_traces(ref, radius, offset, marker_size=5, alpha=0.07):
    traces = []
    ref_pal = phase_pal_transition
    for phase, color in ref_pal.items():
        df = ref[ref['phase'] == phase]
        x, y, z = df['dim1'].values, df['dim2'].values, df['dim3'].values
        x, y, z = project_above_sphere(x, y, z, radius, offset)
        traces.append(go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=marker_size, color=color, opacity=alpha),
                                   name=f"Reference {phase}", showlegend=True))
    return traces





def make_new_traces(z_df, radius, offset, color_by='KNN_phase', palette=None, marker_size=3, is_continuous=False):
    traces = []
    if is_continuous:
        color_vals = z_df[color_by].values
        x, y, z = z_df['dim1'].values, z_df['dim2'].values, z_df['dim3'].values
        x, y, z = project_above_sphere(x, y, z, radius, offset)
        traces.append(go.Scatter3d(x=x, y=y, z=z, mode='markers',
                                   marker=dict(size=marker_size, color=color_vals, coloraxis='coloraxis'),
                                   name=color_by, showlegend=False))
        if z_df[color_by].isna().any():
            na_mask = z_df[color_by].isna()
            x_na, y_na, z_na = project_above_sphere(x[na_mask], y[na_mask], z[na_mask], radius, offset)
            traces.append(go.Scatter3d(x=x_na, y=y_na, z=z_na, mode='markers',
                                       marker=dict(size=marker_size, color='grey'),
                                       name='NA', showlegend=True))
    else:
        if palette is None:
            palette = {}
        if not set(z_df[color_by].unique()).issubset(set(palette.keys())):
            missing = set(z_df[color_by].unique()) - set(palette.keys())
            raise ValueError(f"The palette is missing colors for the following categories: {', '.join(missing)}")
        for phase, color in palette.items():
            phase_df = z_df[z_df[color_by] == phase]
            x, y, z = phase_df['dim1'].values, phase_df['dim2'].values, phase_df['dim3'].values
            x, y, z = project_above_sphere(x, y, z, radius, offset)
            traces.append(go.Scatter3d(x=x, y=y, z=z, mode='markers',
                                       marker=dict(size=marker_size, color=color),
                                       name=phase))
    return traces




def make_velocity_vectors(z_df, velocity):
    vel = velocity[['dim1', 'dim2', 'dim3']].to_numpy()
    umap = z_df[['dim1', 'dim2', 'dim3']].to_numpy()
    arrows = [
        go.Scatter3d(x=[u[0], u[0] + v[0]], y=[u[1], u[1] + v[1]], z=[u[2], u[2] + v[2]],
                     mode='lines', line=dict(color='black', width=1), showlegend=False, legendgroup='velocity')
        for u, v in zip(umap, vel)
    ]
    cone = go.Cone(x=umap[:, 0] + vel[:, 0], y=umap[:, 1] + vel[:, 1], z=umap[:, 2] + vel[:, 2],
                   u=vel[:, 0], v=vel[:, 1], w=vel[:, 2], sizemode="scaled", sizeref=0.5, anchor="tail",
                   colorscale=[[0, "black"], [1, "black"]], showscale=False, name='Velocity Vectors', showlegend=True,
                   legendgroup='velocity')
    return arrows, cone



def seaborn_to_plotly(palette_name, n_colors=256):
    cmap = cm.get_cmap(palette_name)  # use matplotlib for everything
    colors = [cmap(i / (n_colors - 1))[:3] for i in range(n_colors)]
    return [[i / (n_colors - 1), f"rgb({r*255:.0f},{g*255:.0f},{b*255:.0f})"] for i, (r, g, b) in enumerate(colors)]

def normalize_colormap(cmap_name='mako', vmin=-1, vmax=0, n_colors=256):
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(cmap_name)
    colors = [cmap(norm(np.linspace(vmin, vmax, n_colors)[i]))[:3] for i in range(n_colors)]
    return [[i / (n_colors - 1), f"rgb({r*255:.0f},{g*255:.0f},{b*255:.0f})"] for i, (r, g, b) in enumerate(colors)]



def plot_sphere(z_df, colour_by = 'KNN_phase', palette = None, ref = None, velocity = None, marker_size = 2, cycle_pole = reference_CC_pole_point, savefig = None, show = False, camera_position = None, snap_png = None):
    fig_data = []

    if {'dim1', 'dim2', 'dim3'} - set(z_df.columns):
        raise ValueError("Require dim1, dim2 and dim3 columns in z_df")
    if colour_by not in z_df.columns:
        raise ValueError(f"{colour_by} column not found in z_df")

    if z_df[colour_by].isna().all():
        raise ValueError(f"Column '{colour_by}' contains only NaN values.")
    
    if len(cycle_pole) != 3:
        raise ValueError(f"cycle_pole must have exactly 3 elements, got {len(cycle_pole)}")


    # Sphere properties
    mtx = z_df[['dim1', 'dim2', 'dim3']].values
    radius = np.mean(np.linalg.norm(mtx, axis=1)) - 0.01
    offset = 0.01 * radius  # Slight offset above the sphere

    # Make grey surface of sphere
    sphere = make_sphere_surface(radius)
    fig_data.append(sphere)
  
    fig_data.append(make_pole_trace(cycle_pole, 'Cell cycle pole', color='grey', width=25, radius = radius, extension=1.3))

    if ref is not None:
        ref_traces = make_reference_traces(ref, radius, offset, marker_size=5, alpha=0.07)
        fig_data += ref_traces

    is_cont = is_continuous(z_df[colour_by])
    if is_cont:
        if isinstance(palette, str):
            palette = seaborn_to_plotly(palette)
        elif palette is None and colour_by == 'cell_cycle_pseudotime':
            palette = normalize_colormap('rocket_r', vmin=0, vmax=1)
        elif palette is None and colour_by == 'dormancy_pseudotime':
            palette = normalize_colormap('mako', vmin=-1, vmax=0)
        elif palette is None:
            palette = seaborn_to_plotly('viridis')
        
    else: 
        if colour_by == 'KNN_phase' and palette is None:
            palette = phase_pal_transition
        elif colour_by != 'KNN_phase' and palette is None:
            # Generate a palette if none is provided
            unique_labels = z_df[colour_by].unique()
            cmap = get_cmap('tab20')
            palette = {
                label: '#{:02x}{:02x}{:02x}'.format(
                    int(r * 255), int(g * 255), int(b * 255)
                )
                for i, label in enumerate(unique_labels)
                for r, g, b, _ in [cmap(i / max(len(unique_labels) - 1, 1))]
            }
        elif isinstance(palette, dict):
            palette = palette 
        else:
            raise ValueError(f"For categorical variables, 'palette' must be a dictionary mapping items to colors.")


    scatter_traces = make_new_traces(z_df, radius, offset, color_by=colour_by, palette=palette, marker_size=marker_size, is_continuous=is_cont)
    fig_data += scatter_traces

    if velocity is not None:
        arrow_traces, cone_trace = make_velocity_vectors(z_df, velocity)
        fig_data += arrow_traces + [cone_trace]
        
    fig = go.Figure(data=fig_data)
    
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False)
        ),
        legend=dict(
            x=0.9, 
            y=0.3, 
            font=dict(size=14),
            itemsizing='constant',  
        ),
        showlegend=True,
    )
        
    if is_cont:
        fig.update_layout(
            coloraxis=dict(
                colorscale=palette,
                cmin=-1 if colour_by == 'dormancy_pseudotime' else None,
                cmax=0 if colour_by == 'dormancy_pseudotime' else None,
                colorbar=dict(
                    title=dict(
                        text=colour_by.replace('_', ' ').capitalize(),
                        side="top",
                        font=dict(size=22)
                    ),
                    len=0.4,
                    thickness=20,
                    x=0.9,
                    y=0.65,
                    yanchor="middle"
                )
            )
        )

    if camera_position:
        fig.update_layout(scene_camera=camera_position)
    if snap_png:
        write_image(fig, snap_png, format="png", width=800, height=800, scale = 2)
    if savefig is not None: 
        fig.write_html(savefig)
    if show == True:
        fig.show()
    return fig
    


def plot_gene_sphere(
    z_df,
    adata,
    gene_name,
    layer=None,
    ref=None,
    velocity=None,
    show=False,
    outpath=None,
    title="",
    cycle_pole=reference_CC_pole_point
):
    """
    Plot gene expression projected on the Ouroboros VAE sphere. Gene_name can be a list of genes or a single gene.
    """
    if isinstance(gene_name, str):
        gene_name = [gene_name]

    included_genes = [gene for gene in gene_name if gene in adata.var_names]

    if len(included_genes) == 0:
        raise ValueError(f"None of the genes in gene_name is in the AnnData object.")    

    if layer:
        adata.X = adata.layers[layer].copy()

    expr = adata[:, included_genes].X
    gene_expression = np.array(expr.mean(axis=1)).flatten() if issparse(expr) else expr.mean(axis=1)
    z_df["gene_expression"] = gene_expression

    # Geometry
    coords = z_df[['dim1', 'dim2', 'dim3']].values
    radius = np.mean(np.linalg.norm(coords, axis=1)) - 0.01
    offset = 0.01 * radius

    fig_data = []

    # Sphere surface
    fig_data.append(make_sphere_surface(radius))

    # Pole
    fig_data.append(make_pole_trace(cycle_pole, 'Poles', color='grey', width=5, radius=radius, extension=1.3))

    # Reference traces
    if ref is not None and not ref.empty:
        fig_data += make_reference_traces(ref, radius, offset, marker_size=5, alpha=0.05)

    # Gene expression points
    x, y, z = z_df['dim1'].values, z_df['dim2'].values, z_df['dim3'].values
    x, y, z = project_above_sphere(x, y, z, radius, offset)
    gene_scatter = go.Scatter3d(
        x=x, y=y, z=z, mode='markers',
        marker=dict(
            size=2,
            color=z_df["gene_expression"],
            colorscale="Viridis",
            colorbar=dict(
                title=title,
                len=0.5,
                thickness=20,
                x=1.5,
            ),
            opacity=1
        ),
        name=f"{gene_name}",
        showlegend=False
    )
    fig_data.append(gene_scatter)

    # Velocity
    if velocity is not None and not velocity.empty:
        arrows, cone = make_velocity_vectors(z_df, velocity)
        fig_data += arrows + [cone]

    # Assemble figure
    fig = go.Figure(data=fig_data)
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False)
        ),
        showlegend=True,
        legend=dict(
            x=0.9, 
            y=0.3, 
            font=dict(size=14),
            itemsizing='constant',  
        ),
        coloraxis=dict(
                colorbar=dict(
                    title=dict(
                        side="top",
                        font=dict(size=22)
                    ),
                    len=0.4,
                    thickness=20,
                    x=0.9,
                    y=0.65,
                    yanchor="middle"
                ))
            )   

    if outpath:
        fig.write_html(outpath)
    if show:
        fig.show()



def rotate_north(z_df, reference_CC_pole_point = [0.86202236, 0.24824865, 0.44191636]):
    """Rotate the cell cycle pole to be north pole
    Note: will replace dim1, dim2, dim3 in z_df"""
    new_df = z_df.copy()
    # Reference point
    reference_CC_pole_point = np.array(reference_CC_pole_point)
    target_vector = reference_CC_pole_point / np.linalg.norm(reference_CC_pole_point)
    # Default North Pole
    north_pole = np.array([0, 0, 1])

    # Compute rotation axis and angle
    rotation_axis = np.cross(target_vector, north_pole)
    if np.linalg.norm(rotation_axis) > 1e-8:  # Avoid division by zero for near-parallel vectors
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
    rotation_angle = np.arccos(np.clip(np.dot(target_vector, north_pole), -1.0, 1.0))

    # Create the rotation
    rotation = R.from_rotvec(rotation_axis * rotation_angle)

    # Extract coordinates
    coordinates = new_df[['dim1', 'dim2', 'dim3']].values

    # Apply the rotation
    rotated_coordinates = rotation.apply(coordinates)

    # Update z_df with the rotated coordinates
    new_df[['dim1', 'dim2', 'dim3']] = rotated_coordinates
    return new_df



def camera_position_on_sphere(radius, latitude, longitude, center=(0, 0, 0)):
    """
    Calculate the camera position and configuration based on spherical coordinates.

    Parameters:
    - radius: Distance from the sphere center to the camera.
    - latitude: Latitude angle in degrees (-90 to 90).
    - longitude: Longitude angle in degrees (0 to 360).
    - center: Tuple (x, y, z) representing the center of the sphere (default is (0, 0, 0)).

    Returns:
    - camera: Dictionary with eye, center, and up vectors for the camera position.
    """
    # Convert latitude and longitude to radians
    lat_rad = np.radians(latitude)
    lon_rad = np.radians(longitude)

    # Calculate camera position in Cartesian coordinates
    x = radius * np.cos(lat_rad) * np.cos(lon_rad)
    y = radius * np.cos(lat_rad) * np.sin(lon_rad)
    z = radius * np.sin(lat_rad)

    # Camera focus (center of the sphere)
    focus = dict(x=center[0], y=center[1], z=center[2])

    # "Up" vector remains fixed (z-axis)
    up = dict(x=0, y=0, z=1)

    # Camera position (eye)
    eye = dict(x=x + center[0], y=y + center[1], z=z + center[2])

    # Return the camera configuration
    return dict(eye=eye, center=focus, up=up)




def sphere_snapshot(lat, lon,  z_df, colour_by='KNN_phase', palette=None, radius = 1.2, ref_embed = None, vel_df = None, save_as_png=True, cycle_pole = [0, 0, 1]):
    radius = radius  # Camera distance from the sphere
    center = (0, 0, 0)  # Sphere center

    # Example latitude and longitude
    latitude = lat  # Degrees (e.g., 30° north) Must be (-90 to 90)
    longitude = lon  # Degrees (e.g., 60° east) Must be (0 to 360)

    # Get camera configuration
    camera = camera_position_on_sphere(radius, latitude, longitude, center)


    # Use the camera configuration in your Plotly plot
    plot_sphere(
        z_df=z_df,
        colour_by=colour_by,
        palette=palette,
        ref=ref_embed,
        cycle_pole=cycle_pole,
        velocity=vel_df,
        marker_size = 5,
        camera_position=camera,
        snap_png=save_as_png,
    )
    
    


def plot_robinson_projection(
    z_df, 
    colour_by, 
    velocity_df=None, 
    palette=None, 
    ref_df=None,
    central_longitude=80, 
    title="", 
    alpha=0.7,
    scale=10,
    save_fig = None,
    rasterize = True,
    show = True
):
    try:
        import cartopy.crs as ccrs
    except ImportError:
        raise ImportError(
            "The 'cartopy' package is required for this function but is not installed.\n"
            "You can install it with conda (recommended):\n"
            "  conda install -c conda-forge cartopy\n"
            "Or with pip (requires system dependencies to be installed first):\n"
            "  pip install cartopy"
        )
    x, y, z = z_df['dim1'].values, z_df['dim2'].values, z_df['dim3'].values
    r = np.sqrt(x**2 + y**2 + z**2)
    lon = np.degrees(np.arctan2(y, x))
    lat = np.degrees(np.arcsin(z / r))

    is_cont = is_continuous(z_df[colour_by])
    has_na = z_df[colour_by].isna()

    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.Robinson(central_longitude=central_longitude))
    ax.set_global()
    ax.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.7, linestyle='--')

    if is_cont:
        values = z_df[colour_by].values

        # Set colormap
        if palette is None:
            if colour_by == 'cell_cycle_pseudotime':
                cmap = get_cmap('rocket_r')
            elif colour_by == 'dormancy_pseudotime':
                cmap = get_cmap('mako')
            else:
                cmap = get_cmap('viridis')
        elif isinstance(palette, str):
            cmap = get_cmap(palette)
        else:
            cmap = get_cmap('viridis')

        # Plot non-NA points
        not_na = ~has_na
        sc = ax.scatter(
            lon[not_na], lat[not_na], c=values[not_na], s=10, alpha=alpha,
            cmap=cmap,
            transform=ccrs.PlateCarree(), 
            rasterized=rasterize
        )

        # Plot NA points in grey
        if has_na.any():
            ax.scatter(
                lon[has_na], lat[has_na], c='lightgrey', s=10, alpha=alpha,
                transform=ccrs.PlateCarree(), rasterized=rasterize
            )

        cb = plt.colorbar(sc, ax=ax, orientation='vertical', shrink=0.6, pad=0.05)
        cb.set_label(colour_by.replace("_", " ").capitalize(), fontsize=12)

    else:
        unique_labels = z_df[colour_by].dropna().unique()
        if palette is None:
            if colour_by == 'KNN_phase':
                palette = phase_pal_transition
            else:
                cmap = get_cmap('tab20')
                palette = {label: cmap(i / len(unique_labels)) for i, label in enumerate(unique_labels)}

        for label in unique_labels:
            idx = z_df[colour_by] == label
            ax.scatter(lon[idx], lat[idx],
                       s=10, label=label, 
                       c=palette.get(label, 'grey'), alpha=alpha,
                       transform=ccrs.PlateCarree(), rasterized=rasterize)

        # Plot NA values in grey
        if has_na.any():
            ax.scatter(
                lon[has_na], lat[has_na],
                s=10, c='lightgrey', label='NA',
                alpha=alpha, transform=ccrs.PlateCarree(), 
                rasterized=rasterize
            )

        plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))

    if velocity_df is not None:
        ax.quiver(
            lon, lat,
            velocity_df['dim1'].values,
            velocity_df['dim2'].values,
            scale=scale, color='black', alpha=0.6, width=0.002,
            transform=ccrs.PlateCarree(), rasterized=rasterize 
        )

    if ref_df is not None:
        xr, yr, zr = ref_df['dim1'].values, ref_df['dim2'].values, ref_df['dim3'].values
        rr = np.sqrt(xr**2 + yr**2 + zr**2)
        lon_r = np.degrees(np.arctan2(yr, xr))
        lat_r = np.degrees(np.arcsin(zr / rr))
        ref_labels = ref_df['phase'].unique()
        
        for label in ref_labels:
            idx = ref_df['phase'] == label
            color = phase_pal_transition[label] if label in phase_pal_transition else 'grey'
            ax.scatter(
                lon_r[idx], lat_r[idx],
                s=20, label=f"ref: {label}",
                c=color, alpha=0.1,
                transform=ccrs.PlateCarree(), 
                rasterized=rasterize 
            )

    plt.title(title)
    if save_fig is not None:
        plt.savefig(save_fig, dpi=300, bbox_inches='tight')
    if show == True:
        plt.show()


def get_wetchner_adata():
    adata_file = DATA_DIR / "wetchner.h5ad"
    if not adata_file.exists():
        url = "https://zenodo.org/record/16818988/files/wetchner.h5ad?download=1"
        response = requests.get(url, stream=True)
        response.raise_for_status()  # fail if something goes wrong
        with open(adata_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    adata = ad.read_h5ad(adata_file)
    return adata


def qc_and_threshold(model, trainer, z_df, new_feature_set, ref_embed, outdir, seed, debug = True):
    """
    Depreciated function; Attepts to find threshold for quiscence and senescence. 
    """

    ## Process Wetchner dataset
    discrete = get_wetchner_adata()
    discrete.X = discrete.layers['raw_counts'].toarray()
    z_mean_df = embed_in_retrained_sphere(discrete, model, new_feature_set)
    z_mean_df = KNN_predict(ref_embed, z_mean_df)    
    z_mean_df = calculate_cell_cycle_pseudotime(z_mean_df, ref_embed,  phase_category = 'KNN_phase')
    pseud, _ = dormancy_depth(z_mean_df, ref_embed, retrained = True)
    z_mean_df = z_mean_df.merge(pseud, how = 'left', left_index = True, right_index = True)
    z_mean_df = z_mean_df.merge(discrete.obs[['rep', 'treatment']], left_index=True, right_index=True)
    
    if debug:
        plt.hist(z_mean_df['dormancy_pseudotime'])
        plt.savefig(f"{outdir}/wetchner.png")
        plt.close()

    z_mean_df['pseudotime'] = np.where(z_mean_df['dormancy_pseudotime'].isna(), z_mean_df['cell_cycle_pseudotime'], z_mean_df['dormancy_pseudotime'])

    ## Process training dataset
    training_embed = ref_embed.copy()
    cc_df = calculate_cell_cycle_pseudotime(training_embed, ref_embed,  phase_category = 'phase')
    cc_df = cc_df[['cell_cycle_pseudotime']]
    training_embed = training_embed.merge(cc_df, how = 'left', left_index = True, right_index = True)
    pseud, ref_pseud = dormancy_depth(training_embed, ref_embed, retrained = True)
    training_embed = training_embed.merge(pseud, how = 'left', left_index = True, right_index = True)
    
    training_embed['pseudotime'] = np.where(training_embed['dormancy_pseudotime'].isna(), training_embed['cell_cycle_pseudotime'], training_embed['dormancy_pseudotime'])

    ### Find Threshold
    threshold = find_threshold(z_mean_df)
    z_df = z_df.copy()

    z_df['G0_classification'] = np.where(
        z_df['dormancy_pseudotime'] > threshold, 'quiescence',
        np.where(
            z_df['dormancy_pseudotime'] < threshold, 'senescence',
            np.nan
        )
    ) 

    ### QC
    qc = quality_control(trainer, z_mean_df, training_embed, new_feature_set, threshold, seed, outdir)
    qc.to_csv(f"{outdir}/qc.csv", sep=',')

    return z_df

def find_threshold(wetchner_df):
    num_bins = 30
    senescence_df = wetchner_df[wetchner_df['treatment'].isin(['IR-induced senescence (10 Gy)', 'Replicative senescence (PDL 57)', 'Etoposide-induced senescent (50 microM)'])]

    discrete_filtered = senescence_df.dropna(subset=["dormancy_pseudotime"]).copy()
    min_val = discrete_filtered["dormancy_pseudotime"].min()
    max_val = discrete_filtered["dormancy_pseudotime"].max()
    bin_edges = np.linspace(min_val, max_val, num_bins + 1)
    discrete_filtered["pseudotime_bin"] = pd.cut(discrete_filtered["dormancy_pseudotime"], bins=bin_edges, include_lowest=True)

    discrete_filtered = discrete_filtered[discrete_filtered['treatment'].isin(['IR-induced senescence (10 Gy)', 'Replicative senescence (PDL 57)', 'Etoposide-induced senescent (50 microM)'])]
    bin_counts = discrete_filtered.groupby(["pseudotime_bin"]).size()
    bin_proportions = bin_counts.div(bin_counts.sum(axis=0))
    y = bin_proportions.values

    bin_midpoints = [(interval.left + interval.right) / 2 for interval in bin_proportions.index]
    x = np.array(bin_midpoints) 

    # Spline smoothing
    spline = UnivariateSpline(x, y, s=0.01)
    x_dense = np.linspace(x.min(), x.max(), 500)
    y_smooth = spline(x_dense)

    kl = KneeLocator(x_dense, y_smooth, curve="convex", direction="decreasing", online=True)
    knee = kl.knee

    return knee
    


def quality_control(trainer, wetchner_df, training_df, new_feature_set, threshold, seed, outdir):
    # Recall using Wechner dataset
    wetchner_df['pseudotime'] = np.where(wetchner_df['dormancy_pseudotime'].isna(), wetchner_df['cell_cycle_pseudotime'], wetchner_df['dormancy_pseudotime'])
    senescence_df = wetchner_df[wetchner_df['treatment'].isin(['IR-induced senescence (10 Gy)', 'Replicative senescence (PDL 57)', 'Etoposide-induced senescent (50 microM)'])]

    senescene = senescence_df[senescence_df['pseudotime'] < -0.6].shape[0]
    true_senescence = senescence_df.shape[0]
    senescence_recall = senescene / true_senescence

    # Model log likelihood
    log_likihood = trainer.status['log_likelihood'][-1] 
    kl_divergenet = trainer.status['kl_divergence'][-1]

    # Missing genes 
    feature_set = pd.read_csv(DATA_DIR / 'SHAP_feature_set.csv')
    feature_set = feature_set.feature_set.tolist()
    missing_gene = len(set(feature_set) - set(new_feature_set))
    proportion_missing_gene = missing_gene / len(feature_set)

    # SHAP score loss
    shap_score = pd.read_csv("/projects/steiflab/research/hmacdonald/total_RNA/Ouroboros_paper/model/feature_selection/output/mean_shap_values.csv")

    shap_loss = {}
    for cell_cycle in ['G0', 'G1', 'G1-G0 transition', 'G2M', 'S']:
        curr_cell_cycle = shap_score[shap_score['Class'] == cell_cycle]
        curr_cell_cycle = curr_cell_cycle[curr_cell_cycle['Feature'].isin(feature_set)]
        total_shap_score = curr_cell_cycle['AbsoluteSHAPValue'].sum()
        shap_score_loss = curr_cell_cycle[~curr_cell_cycle['Feature'].isin(new_feature_set)]['AbsoluteSHAPValue'].sum()

        prop_shap_loss = shap_score_loss/total_shap_score
        shap_loss[f'{cell_cycle}_shap_loss'] = [prop_shap_loss]


    # Scenscenece threshold Diff
    threshold_diff = abs(-0.6 - threshold)

    # Scenscence gene expression score
    wetchner_training = pd.concat([wetchner_df, training_df], axis=0)
    senescence_score = pd.read_csv('/projects/steiflab/scratch/glchang/Ouroboros_paper/senescence.csv')
    wetchner_training = wetchner_training.merge(senescence_score, right_on="cell_id", left_index = True)

    wetchner_training = wetchner_training[~wetchner_training['dormancy_pseudotime'].isna()]
    
    senmayo_corr = wetchner_training['dormancy_pseudotime'].corr(wetchner_training['senmayo'], method='spearman')
    hernandez_segura_corr = wetchner_training['dormancy_pseudotime'].corr(wetchner_training['core_up_sen_genes'], method='spearman')

   
    qc_df = pd.DataFrame({
        'seed': [seed],
        'wetchner_senescence_recall': [senescence_recall],
        'log_likihood': [log_likihood],
        'kl_divergenet': [kl_divergenet],
        'missing_gene': [missing_gene], 
        'proportion_missing_gene': [proportion_missing_gene],
        'threshold_diff': [threshold_diff],
        'senmayo_corr': [senmayo_corr],
        'hernandez_segura_corr': [hernandez_segura_corr],
        **shap_loss
    })
    return qc_df

def set_seed(seed=0):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def select_seed(repeat, outdir):
    all_z_df = []
    for i in range(repeat):
        z_df = pd.read_csv(outdir + "/retrain/" + str(i) + "/ouroboros_embeddings_pseudotimes.csv")
        z_df.set_index('Unnamed: 0', inplace = True)
        z_df['pseudotime'] = np.where(z_df['dormancy_pseudotime'].isna(), z_df['cell_cycle_pseudotime'], z_df['dormancy_pseudotime'])
        z_df['seed'] = i
        all_z_df.append(z_df)
    all_z_df = pd.concat(all_z_df)
    dormant_df = all_z_df.copy()

    depth_matrix = dormant_df.pivot_table(
        index=dormant_df.index, 
        columns='seed', 
        values='pseudotime'
    )
    consensus_curve = depth_matrix.median(axis=1) 
    
    seed_r = {}
    for col in depth_matrix.columns:
        curr = depth_matrix[col]
        
        valid = curr.notna() & consensus_curve.notna()
        if valid.sum() > 2:  
            r, pval = stats.pearsonr(curr[valid], consensus_curve[valid])
            if pval < 0.05:
                seed_r[col] = r
    
    selected_seed = max(seed_r, key=seed_r.get)
    selected_seed_corr = max(seed_r.values())
    
    plot_consensus(depth_matrix, selected_seed, outdir)

    selected_seed_path = outdir + "/retrain/" + str(selected_seed) 
    z_df = pd.read_csv(selected_seed_path + "/ouroboros_embeddings_pseudotimes.csv", index_col=0)
    ref_embed = pd.read_csv(selected_seed_path + "/retrained_reference_embeddings.csv")


    for file in ['ouroboros_embeddings_pseudotimes.csv', "qc.csv", "retrained_reference_embeddings.csv", "model.meta", "model.index", "model.data-00000-of-00001", "checkpoint"]:
        source_path = selected_seed_path + "/" + file
        destination_path = outdir + "/" + file
        shutil.copy(source_path, destination_path)
    
    return z_df, ref_embed
    

def plot_consensus(depth_matrix, selected_seed, outdir):
    depth_matrix_long = depth_matrix.melt(var_name='seed', value_name='pseudotime')

    fig, ax = plt.subplots(figsize=(10, 4))

    for seed in depth_matrix_long['seed'].unique():
        curr = depth_matrix_long[depth_matrix_long['seed'] == seed]

        if seed != selected_seed:
        # Create histogram plot
            hist = sns.kdeplot(
                data=curr, x='pseudotime',alpha = 0.1, linewidth=1
            )
        else:
            hist = sns.kdeplot(
                data=curr, x='pseudotime', alpha = 1, linewidth=2.5, linestyle='--'
            )

    # Remove the default box (spines)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Draw axes at (0,0)
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    # Labels below the axis
    ax.text(-0.5, -0.8, 'G0 pseudotime (Φ)', ha='center', fontsize=12, clip_on=False)
    ax.text(0.5, -0.8, 'CC pseudotime (θ)', ha='center', fontsize=12, clip_on=False)

    # Define the colored boxes for G1, S, G2M phases
    phase_colors = {'G1': '#1f77b4', 'S': '#ff7f0e', 'G2M': '#2ca02c', 'Quiescent-like': 'lightgrey', 'Senescent-like':'black'}
    phase_regions = {'G1': (0, 0.4), 'S': (0.4, 0.75), 'G2M': (0.75, 1), 'Quiescent-like':(-0.6, 0),'Senescent-like': (-1, -0.6)}

    # Add colored boxes at the top of the plot
    for phase, (start, end) in phase_regions.items():
        ax.add_patch(patches.Rectangle(
            (start, ax.get_ylim()[1] * 1.02),  # Position at top
            end - start,  # Width
            ax.get_ylim()[1] * 0.02,  # Height
            color=phase_colors[phase],
            clip_on=False
        ))
        ax.text((start + end) / 2, ax.get_ylim()[1] * 1.04, phase, 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.savefig(f"{outdir}/consensus_seed.png")
    plt.close()

