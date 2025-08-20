import ouroboros as obo
import importlib_resources as resources
import numpy as np
import pandas as pd
import anndata as ad
import pytest

with resources.path("ouroboros.data", "all_genes_mouse_orthologs.csv") as path:
    mouse_genes = pd.read_csv(path)

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

### Test for convert_to_human_genes function
def test_convert_to_human_genes_adata():
    no_orthlog = ["GENE_A", "GENE_B", "GENE_C"]
    num_orthlog = 50
    mouse_genes_orthlog = mouse_genes.sample(n=num_orthlog)
    genes = mouse_genes_orthlog['mouse_genes'].tolist() + no_orthlog

    adata = make_adata(genes)
    orthlog_adata = obo.convert_to_human_genes(adata)
    assert orthlog_adata.shape[0] == adata.shape[0]
    #assert orthlog_adata.shape[1] == num_orthlog
    assert set(orthlog_adata.var.index.tolist()) == set(mouse_genes_orthlog['human_genes'].tolist())

    for gene in no_orthlog:
        assert gene not in orthlog_adata.var.index

def test_convert_to_human_genes_pandas():
    no_orthlog = ["GENE_A", "GENE_B", "GENE_C"]
    num_orthlog = 50
    num_cells = 5
    mouse_genes_orthlog = mouse_genes.sample(n=num_orthlog)
    genes = mouse_genes_orthlog['mouse_genes'].tolist() + no_orthlog

    data = make_pandas(genes, num_cells)
    orthlog_data = obo.convert_to_human_genes(data)
    assert orthlog_data.shape[0] == num_cells
    assert orthlog_data.shape[1] == num_orthlog
    assert set(orthlog_data.columns.tolist()) == set(mouse_genes_orthlog['human_genes'].tolist())

    for gene in no_orthlog:
        assert gene not in orthlog_data.columns

def test_convert_to_human_genes_none_adata():
    no_orthlog = [f"Gene_{i}" for i in range(20)]
    adata = make_adata(no_orthlog)

    with pytest.raises(ValueError):
        obo.convert_to_human_genes(adata)


def test_convert_to_human_genes_none_pandas():
    no_orthlog = [f"Gene_{i}" for i in range(20)]
    data = make_pandas(no_orthlog)

    with pytest.raises(ValueError):
        obo.convert_to_human_genes(data)

def test_convert_to_human_gene_invalid_datatype():
    num_cells = 10
    num_genes = 100
    data = np.random.rand(num_cells, num_genes)

    with pytest.raises(TypeError):
        obo.convert_to_human_genes(data)


### Test for ouroboros_preprocess function

with resources.path("ouroboros.data", "SHAP_feature_set.csv") as path:
    feature_set = pd.read_csv(path).feature_set.tolist()

def test_ouroboros_preprocess_adata():
    genes = feature_set + [f"Gene_{i}" for i in range(20)]
    num_cells = 10
    adata = make_adata(genes, num_cells)
    
    matrix = obo.ouroboros_functions.ouroboros_preprocess(adata, 'h5ad')
    
    assert isinstance(matrix, np.ndarray)
    assert matrix.shape[0] == num_cells
    assert matrix.shape[1] == len(feature_set)
    
def test_ouroboros_preprocess_pandas():
    genes = feature_set + [f"Gene_{i}" for i in range(20)]
    num_cells = 10
    df = make_pandas(genes, num_cells)
    
    matrix = obo.ouroboros_functions.ouroboros_preprocess(df, 'csv')
    
    assert isinstance(matrix, np.ndarray)
    assert matrix.shape[0] == num_cells
    assert matrix.shape[1] == len(feature_set)

