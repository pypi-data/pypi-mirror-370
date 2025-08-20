import ouroboros as obo
import anndata as ad
import os
import pandas as pd
import numpy as np
import importlib_resources as resources
import random
import pytest

with resources.path("ouroboros.data", "SHAP_feature_set.csv") as path:
    feature_set = pd.read_csv(path).feature_set.tolist()


def make_adata(genes):
    var = pd.DataFrame(index=genes)
    obs = pd.DataFrame(index=[f"cell{i}" for i in range(3)])
    X = np.random.rand(3, len(genes)) if genes else np.zeros((3, 0))
    return ad.AnnData(X=X, obs=obs, var=var)

def test_check_genes_empty():
    adata = make_adata([])
    missing_genes = obo.check_genes(adata)

    assert set(missing_genes) == set(feature_set) , f"Expected all genes missing, but got {missing_genes}"

def test_check_genes_full():
    adata = make_adata(feature_set)
    missing_genes = obo.check_genes(adata)

    assert len(missing_genes) == 0, f"Expected no missing genes, but got {missing_genes}"

def test_check_genes_partial():
    removed_genes = random.sample(feature_set, 20)  # Randomly select 20 genes
    feature_set_copy = [gene for gene in feature_set if gene not in removed_genes]

    adata = make_adata(feature_set_copy)
    missing_genes = obo.check_genes(adata)

    assert set(missing_genes) == set(removed_genes), f"Expected missing genes: {removed_genes}, but got: {missing_genes}"

def test_check_genes_with_additional_genes():
    extra_genes = ["GENE_A", "GENE_B", "GENE_C"]

    removed_genes = random.sample(feature_set, 20) 
    feature_set_copy = [gene for gene in feature_set if gene not in removed_genes] + extra_genes

    adata = make_adata(feature_set_copy)
    missing_genes = obo.check_genes(adata)

    assert all(g not in missing_genes for g in extra_genes), f"Extra genes {extra_genes} shouldn't be missing" 
    assert set(missing_genes) == set(removed_genes), f"Expected missing genes: {removed_genes}, but got: {missing_genes}"

def test_check_genes_with_only_additional_genes():
    extra_genes = ["GENE_A", "GENE_B", "GENE_C"]

    adata = make_adata(extra_genes)
    missing_genes = obo.check_genes(adata)

    assert set(missing_genes) == set(feature_set) , f"Expected all genes missing, but got {missing_genes}"

def test_check_genes_type_error():
    genes = ['GENE_A', 'GENE_B', 'GENE_C']
    with pytest.raises(TypeError, match="Unsupported data type. Expected AnnData or DataFrame."):
        obo.check_genes(genes)


def test_read_in_features():
    assert feature_set == obo.read_in_features()