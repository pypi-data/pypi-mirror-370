import ouroboros as obo
import pytest
import numpy as np
import pandas as pd
import anndata as ad
import os 
import tempfile
import tensorflow as tf

test_file = "test/test_data/test_dataset.h5ad"

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


### Test for invalid inputs
def test_run_ouroboros_invalid_data_type():
    data_type = "tsv"

    with pytest.raises(TypeError):
        obo.run_ouroboros(test_file, data_type)

def test_run_ouroboros_invalid_species():
    species = "arabidopsis"

    with pytest.raises(TypeError):
        obo.run_ouroboros(test_file, "h5ad", species)

def test_run_oroboros_file_not_found_csv():
    with pytest.raises(FileNotFoundError):
        obo.run_ouroboros("fake/path/data.csv", "csv")

def test_run_oroboros_file_not_found_h5ad():
    with pytest.raises(OSError):
        obo.run_ouroboros("fake/path/data.h5ad", "h5ad")


def test_run_ouroboros_missing_all_gene_h5ad():
    num_cells = 100
    genes = ['Test_gene_1','Test_gene_2','Test_gene_3','Test_gene_4','Test_gene_5']
    adata = make_adata(genes, num_cells)

    with tempfile.TemporaryDirectory() as tmp_output_dir:
        adata_path = os.path.join(tmp_output_dir, "empty.h5ad")
        adata.write_h5ad(adata_path)
        with pytest.raises(ValueError):  
            obo.run_ouroboros(adata_path, "h5ad")

def test_run_ouroboros_missing_all_gene_pandas():
    num_cells = 100
    genes = ['Test_gene_1','Test_gene_2','Test_gene_3','Test_gene_4','Test_gene_5']
    df = make_pandas(genes, num_cells)

    with tempfile.TemporaryDirectory() as tmp_output_dir:
        df_path = os.path.join(tmp_output_dir, "empty.csv")
        df.to_csv(df_path)
        with pytest.raises(ValueError):  
            obo.run_ouroboros(df_path, "csv")


### Test for expected output
EXPECTED_COL = ['dim1', 'dim2', 'dim3', 'KNN_phase', 'cell_cycle_pseudotime', 'south', 'dormancy_pseudotime', 'G0_classification']


def test_run_ouroboros_full_h5ad():
    adata = ad.read_h5ad("test/test_data/test_dataset.h5ad")
    with tempfile.TemporaryDirectory() as tmp_output_dir:
        tf.compat.v1.reset_default_graph()
        z_df = obo.run_ouroboros("test/test_data/test_dataset.h5ad", "h5ad", "human", tmp_output_dir)

        expected_output_files = ['ouroboros_embeddings_pseudotimes.csv', 'ouroboros_KNN_sphere.html', 'ouroboros_cell_cycle_pseudotime.html', 'ouroboros_dormancy_pseudotime.html']
        for file in expected_output_files:
            file = os.path.join(tmp_output_dir, file)
            assert os.path.exists(file), f"Expected output not found: {file}"

        assert z_df.columns.to_list() == EXPECTED_COL, f"Column names unexpected: {z_df.columns.to_list()}"
        assert set(z_df.index) == set(adata.obs_names)

def test_run_ouroboros_partial_h5ad():
    adata = ad.read_h5ad("test/test_data/test_partial_dataset.h5ad")
    with tempfile.TemporaryDirectory() as tmp_output_dir:
        tf.compat.v1.reset_default_graph()
        z_df = obo.run_ouroboros("test/test_data/test_partial_dataset.h5ad", "h5ad", "human", tmp_output_dir, repeat=2)

        expected_output_files = ['ouroboros_embeddings_pseudotimes.csv', 'retrained_reference_embeddings.csv', 'ouroboros_cell_cycle_pseudotime.html', 'ouroboros_dormancy_pseudotime.html']
        for file in expected_output_files:
            file = os.path.join(tmp_output_dir, file)
            assert os.path.exists(file), f"Expected output not found: {file}"

        assert z_df.columns.to_list() == EXPECTED_COL, f"Column names unexpected: {z_df.columns.to_list()}"
        assert set(z_df.index) == set(adata.obs_names)

def test_run_ouroboros_full_pandas():
    adata = ad.read_h5ad("test/test_data/test_dataset.h5ad")
    df = pd.DataFrame(adata.X, columns=adata.var_names)
    df['cell_id'] = adata.obs_names
    
    with tempfile.TemporaryDirectory() as tmp_output_dir:
        pandas_file = os.path.join(tmp_output_dir, "test_dataset.csv")
        df.to_csv(pandas_file)

        tf.compat.v1.reset_default_graph()
        z_df = obo.run_ouroboros(pandas_file, "csv", "human", tmp_output_dir)

        expected_output_files = ['ouroboros_embeddings_pseudotimes.csv', 'ouroboros_KNN_sphere.html', 'ouroboros_cell_cycle_pseudotime.html', 'ouroboros_dormancy_pseudotime.html']
        for file in expected_output_files:
            file = os.path.join(tmp_output_dir, file)
            assert os.path.exists(file), f"Expected output not found: {file}"

        assert z_df.columns.to_list() == EXPECTED_COL
        assert set(z_df.index) == set(df['cell_id'])

def test_run_ouroboros_partial_pandas():
    adata = ad.read_h5ad("test/test_data/test_partial_dataset.h5ad")
    df = pd.DataFrame(adata.X, columns=adata.var_names, index=adata.obs_names)

    with tempfile.TemporaryDirectory() as tmp_output_dir:
        tf.compat.v1.reset_default_graph()
        pandas_file = os.path.join(tmp_output_dir, "test_partial_dataset.csv")
        df.to_csv(pandas_file)
        z_df = obo.run_ouroboros(pandas_file, "csv", "human", tmp_output_dir, repeat=2)

        expected_output_files = ['ouroboros_embeddings_pseudotimes.csv', 'retrained_reference_embeddings.csv', 'ouroboros_cell_cycle_pseudotime.html', 'ouroboros_dormancy_pseudotime.html']
        for file in expected_output_files:
            file = os.path.join(tmp_output_dir, file)
            assert os.path.exists(file), f"Expected output not found: {file}"

        assert z_df.columns.to_list() == EXPECTED_COL
        assert set(z_df.index) == set(df.index)