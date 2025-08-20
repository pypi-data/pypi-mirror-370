import ouroboros as obo
import importlib_resources as resources
import numpy as np
import pandas as pd
import anndata as ad
import tempfile
import os
from pathlib import Path
import tensorflow as tf
from ouroboros.scphere.model.vae import SCPHERE
import random
import pytest
import pickle

### Utility Functions
def make_adata(genes, num_cells = 5):
    var = pd.DataFrame(index=genes)
    obs = pd.DataFrame(index=[f"cell{i}" for i in range(num_cells)])
    X = np.random.rand(num_cells, len(genes)) if genes else np.zeros((num_cells, 0))
    adata = ad.AnnData(X=X, obs=obs, var=var)
    adata.layers['raw_counts'] = adata.X.copy()
    return adata

def make_pandas(genes, num_cells = 5):
    data = pd.DataFrame(
        np.random.rand(num_cells, len(genes)),  # random values
        index=[f"Cell{i}" for i in range(num_cells)],  # row index = cell names
        columns=genes  # column index = gene names
    )
    return data


# Test ouroboros_embed 
def test_ouroboros_embed():
    adata = ad.read_h5ad("test/test_data/test_dataset.h5ad") 
    matrix = np.load('test/test_data/test_matrix.npy')

    with tempfile.TemporaryDirectory() as outdir:
        tf.compat.v1.reset_default_graph()
        z_df = obo.ouroboros_functions.ouroboros_embed(matrix, adata, "h5ad", outdir = outdir)

        output_file = os.path.join(outdir, "ouroboros_KNN_sphere.html")
        assert os.path.exists(output_file)
        assert isinstance(z_df, pd.DataFrame)
        assert z_df.shape[0] == adata.shape[0]
        assert list(z_df.columns) == ['dim1', 'dim2', 'dim3', 'KNN_phase', 'cell_cycle_pseudotime', 'south', 'dormancy_pseudotime', 'G0_classification']

        with open(output_file) as f:
            html = f.read()
        for phase in z_df['KNN_phase'].unique():
            assert "\"mode\":\"markers\",\"name\":\"" + phase + "\"" in html

# Test ouroboros_retrain
with resources.path("ouroboros.data", "SHAP_feature_set.csv") as path:
    feature_set = pd.read_csv(path).feature_set.tolist()

with resources.path("ouroboros.data", "train_meta.csv") as path:
    train_meta = pd.read_csv(path)

def test_ouroboros_retrain_adata():
    seed = random.randint(1, 1000000)
    extra_genes = [f"Gene_{i}" for i in range(100)]
    removed_genes = random.sample(feature_set, 30) 
    feature_gene_subset = [gene for gene in feature_set if gene not in removed_genes]
    genes = feature_gene_subset + extra_genes
    adata = make_adata(genes, 100)
    
    model, ref_embed, in_order_feature_set, trainer = obo.ouroboros_functions.ouroboros_retrain(adata, seed)

    assert ref_embed.columns.tolist() == ['dim1', 'dim2', 'dim3', 'phase', 'library']
    assert set(in_order_feature_set) == set(feature_gene_subset)
    assert ref_embed.shape[0] == train_meta.shape[0]
    assert isinstance(model, SCPHERE)

def test_ouroboros_retrain_pandas():
    seed = random.randint(1, 1000000)
    extra_genes = [f"Gene_{i}" for i in range(100)]
    removed_genes = random.sample(feature_set, 30) 
    feature_gene_subset = [gene for gene in feature_set if gene not in removed_genes]
    genes = feature_gene_subset + extra_genes
    df = make_pandas(genes, 100)
    
    model, ref_embed, in_order_feature_set, trainer = obo.ouroboros_functions.ouroboros_retrain(df, seed)

    assert ref_embed.columns.tolist() == ['dim1', 'dim2', 'dim3', 'phase', 'library']
    assert set(in_order_feature_set) == set(feature_gene_subset)
    assert ref_embed.shape[0] == train_meta.shape[0]
    assert isinstance(model, SCPHERE)
    
### Test embed_in_retrained_sphere
def test_embed_in_retrained_sphere_adata():
    with open("test/test_data/test_partial_in_order_feature_set.pkl", "rb") as f:
        in_order_feature_set = pickle.load(f)

    tf.compat.v1.reset_default_graph()
    model = SCPHERE(n_gene=len(in_order_feature_set), n_batch=2, batch_invariant=False,
                z_dim=2, latent_dist='vmf',
                observation_dist='nb')
    model.load_sess("test/test_data/test_partial_model")
    
    adata = ad.read_h5ad("test/test_data/test_partial_dataset.h5ad")
    z_df = obo.ouroboros_functions.embed_in_retrained_sphere(adata, model, in_order_feature_set)

    assert z_df.columns.tolist() == ["dim1", "dim2", "dim3"]
    assert z_df.shape == (adata.shape[0], 3)
    assert set(z_df.index.tolist()) == set(adata.obs.index.to_list())

def test_embed_in_retrained_sphere_pandas():
    with open("test/test_data/test_partial_in_order_feature_set.pkl", "rb") as f:
        in_order_feature_set = pickle.load(f)

    tf.compat.v1.reset_default_graph()
    model = SCPHERE(n_gene=len(in_order_feature_set), n_batch=2, batch_invariant=False,
                z_dim=2, latent_dist='vmf',
                observation_dist='nb')
    model.load_sess("test/test_data/test_partial_model")
    
    adata = ad.read_h5ad("test/test_data/test_partial_dataset.h5ad")
    df = pd.DataFrame(adata.X, index=adata.obs_names, columns=adata.var_names)
    z_df = obo.ouroboros_functions.embed_in_retrained_sphere(df, model, in_order_feature_set)

    assert z_df.columns.tolist() == ["dim1", "dim2", "dim3"]
    assert z_df.shape == (df.shape[0], 3)
    assert set(z_df.index.tolist()) == set(df.index.to_list())

# Test KNN_predict
def test_KNN_predict():
    phases = ["cell_cycle_phase_1", "cell_cycle_phase_2", "cell_cycle_phase_3"]
    num_cells_training = 1000
    num_cells_test = 100

    ref_embed = pd.DataFrame({
        "dim1": np.random.rand(num_cells_training) * 2 - 1,
        "dim2": np.random.rand(num_cells_training) * 2 - 1,
        "dim3": np.random.rand(num_cells_training) * 2 - 1,
        "phase": np.random.choice(phases, size=num_cells_training)
    })
    z_df = pd.DataFrame({
        "dim1": np.random.rand(num_cells_test) * 2 - 1,
        "dim2": np.random.rand(num_cells_test) * 2 - 1,
        "dim3": np.random.rand(num_cells_test) * 2 - 1,
    }, index=[f"cell_{i+1}" for i in range(num_cells_test)])

    z_df_predict = obo.ouroboros_functions.KNN_predict(ref_embed, z_df)
    
    assert isinstance(z_df_predict, pd.DataFrame)
    assert z_df_predict.shape == (num_cells_test, 4)
    assert (z_df_predict[["dim1", "dim2", "dim3"]] == z_df).all().all()
    assert "KNN_phase" in z_df_predict.columns
    assert z_df_predict["KNN_phase"].isnull().sum() == 0
    assert set(z_df_predict["KNN_phase"]).issubset(set(ref_embed["phase"]))

def calculate_cell_cycle_pseudotime():
    phases = ["cell_cycle_phase_1", "cell_cycle_phase_2", "cell_cycle_phase_3"]
    num_cells_training = 1000
    num_cells_test = 100

    ref_embed = pd.DataFrame({
        "dim1": np.random.rand(num_cells_training) * 2 - 1,
        "dim2": np.random.rand(num_cells_training) * 2 - 1,
        "dim3": np.random.rand(num_cells_training) * 2 - 1,
        "phase": np.random.choice(phases, size=num_cells_training)
    })
    z_df = pd.DataFrame({
        "dim1": np.random.rand(num_cells_test) * 2 - 1,
        "dim2": np.random.rand(num_cells_test) * 2 - 1,
        "dim3": np.random.rand(num_cells_test) * 2 - 1,
        "test_phase_labels":  np.random.choice(phases, size=num_cells_test)
    }, index=[f"cell_{i+1}" for i in range(num_cells_test)])

    z_df_pseudotime = obo.ouroboros_functions.calculate_cell_cycle_pseudotime(z_df, ref_embed, phase_category = 'test_phase_labels')

    assert isinstance(z_df_pseudotime, pd.DataFrame)
    assert z_df_pseudotime.shape == (num_cells_test, 5)
    assert (z_df_pseudotime[["dim1", "dim2", "dim3"]] == z_df).all().all()
    assert "cell_cycle_pseudotime" in z_df_pseudotime.columns
    assert np.min(z_df_pseudotime['cell_cycle_pseudotime']) > 0
    assert np.max(z_df_pseudotime['cell_cycle_pseudotime']) < 1

def test_dormancy_depth_retrain():
    phases = ["G1", "G0", "S", "G2M", "G1-G0 transition"]
    num_cells_training = 1000
    num_cells_test = 100

    ref_embed = pd.DataFrame({
        "dim1": np.random.rand(num_cells_training) * 2 - 1,
        "dim2": np.random.rand(num_cells_training) * 2 - 1,
        "dim3": np.random.rand(num_cells_training) * 2 - 1,
        "phase": np.random.choice(phases, size=num_cells_training),
        "library": "library"
    })
    z_df = pd.DataFrame({
        "dim1": np.random.rand(num_cells_test) * 2 - 1,
        "dim2": np.random.rand(num_cells_test) * 2 - 1,
        "dim3": np.random.rand(num_cells_test) * 2 - 1,
        "KNN_phase":  np.random.choice(phases, size=num_cells_test),
        "cell_cycle_pseudotime": np.random.rand(num_cells_test)
    }, index=[f"cell_{i+1}" for i in range(num_cells_test)])

    z_dd, ref_pseud = obo.ouroboros_functions.dormancy_depth(z_df, ref_embed, retrained = True)

    assert isinstance(z_dd, pd.DataFrame)
    assert z_dd.shape == (num_cells_test, 1)
    assert z_dd.columns.to_list()  == ["dormancy_pseudotime"]
    #assert np.min(z_dd["dormancy_pseudotime"]) >= -1
    assert np.max(z_dd["dormancy_pseudotime"]) <= 0
    assert z_dd.index.to_list() == z_df.index.to_list()


    assert isinstance(ref_pseud, pd.DataFrame)
    assert ref_pseud.shape == (num_cells_training, 1)
    assert ref_pseud.columns.to_list()  == ["dormancy_pseudotime"]
    #assert np.min(ref_pseud["dormancy_pseudotime"]) >= -1
    assert np.max(ref_pseud["dormancy_pseudotime"]) <= 0

