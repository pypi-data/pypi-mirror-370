import ouroboros as obo
import importlib_resources as resources
import numpy as np
import pandas as pd
#import anndata as ad
import pytest
import plotly.graph_objs as go
import random
import tempfile
import os

z_df = pd.read_csv("test/test_data/test_pseudotimes.csv")
with resources.path("ouroboros.data", "reference_embeddings.csv") as path:
    ref_embed = pd.read_csv(path)
reference_CC_pole_point = obo.ouroboros_functions.reference_CC_pole_point



def check_plot(fig):
    assert isinstance(fig, go.Figure)

    marker_name = ['Cell cycle pole', 'Reference G1', 'Reference S', 'Reference G2M', 'Reference G0', 'Reference G1-G0 transition']

    assert fig.data[0].type == 'surface', "Expect first layer to be surface"
    for i in range(6):
        assert fig.data[i+1].type == 'scatter3d', "Expect scatter3d type but got {fig.data[i+1].type}"
        assert fig.data[i+1].name == marker_name[i], "Expect {marker_name[i]} type but got {fig.data[i+1].name}"

### Test plotting
def test_plot_sphere_numeric():
    column = 'numeric_feature'
    z_df[column] = np.random.randn(len(z_df))
    assert pd.api.types.is_numeric_dtype(z_df[column])
    marker_size = random.randint(1,25)

    with tempfile.TemporaryDirectory() as outdir:
        fig = obo.plot_sphere(z_df, colour_by = column, ref = ref_embed, marker_size = marker_size, cycle_pole = reference_CC_pole_point, savefig = f'{outdir}/test_continous.html', show = False, snap_png=f'{outdir}/test_continous.jpg')

        check_plot(fig)
        
        output_file = os.path.join(outdir, "test_continous.html") 
        assert os.path.exists(output_file)
        output_file = os.path.join(outdir, "test_continous.jpg") 
        assert os.path.exists(output_file)

        assert fig.data[7].type == 'scatter3d'
        assert fig.data[7].name == column
        assert len(fig.data[7].x) == z_df.shape[0]
        
        

def test_plot_sphere_string():
    column = 'category_feature'
    categories = ['A1', 'B1', 'B2', 'C', 'D']
    z_df[column] = np.random.choice(categories, size=len(z_df))
    assert pd.api.types.is_string_dtype(z_df[column])

    palette = {}
    for cat in categories:
        palette[cat] = "#%06x" % random.randint(0, 0xFFFFFF)
    marker_size = random.randint(1,25)

    with tempfile.TemporaryDirectory() as outdir:
        fig = obo.plot_sphere(z_df, colour_by = column, ref = ref_embed, marker_size = marker_size, cycle_pole = reference_CC_pole_point, palette = palette, savefig = f'{outdir}/test_string.html', snap_png=f'{outdir}/test_string.jpg')

        check_plot(fig)
        
        output_file = os.path.join(outdir, "test_string.html") 
        assert os.path.exists(output_file)
        output_file = os.path.join(outdir, "test_string.jpg") 
        assert os.path.exists(output_file)

        for i in range(len(categories)):
            assert fig.data[i+7].name == categories[i]
            assert fig.data[i+7].type == 'scatter3d'
            filted_df = z_df[z_df[column] == categories[i]]
            assert len(fig.data[i+7].x) == filted_df.shape[0], f"Expect {filted_df.shape[0]} points but got {len(fig.data[i+7].x)}"
            assert fig.data[i+7]['marker']['color'] == palette[categories[i]]
            assert fig.data[i+7]['marker']['size'] == marker_size

def test_plot_sphere_missing_cols():
    missing_col_df = z_df.drop(columns=['dim1', 'dim2', 'dim3'])
    with pytest.raises(ValueError):
        obo.plot_sphere(missing_col_df, colour_by = 'KNN_phase')
        
def test_plot_sphere_missing_colour_by_col():
    with pytest.raises(ValueError):
        obo.plot_sphere(z_df, colour_by = 'test_col')

def test_plot_sphere_invalid_pole():
    cycle_pole = [random.random() for _ in range(4)] # Not 3 item
    with pytest.raises(ValueError):
        obo.plot_sphere(z_df, colour_by = 'KNN_phase', cycle_pole = cycle_pole)


def test_plot_sphere_invalid_palette_categorical():
    column = 'category_feature'
    categories = ['A1', 'B1', 'B2', 'C', 'D']
    z_df[column] = np.random.choice(categories, size=len(z_df))
    assert pd.api.types.is_string_dtype(z_df[column])

    palette = "test_palette"
    with pytest.raises(ValueError):
        obo.plot_sphere(z_df, colour_by = column, palette = palette)

    with pytest.raises(ValueError):
        obo.plot_sphere(z_df, colour_by = "KNN_phase", palette = palette)

def test_plot_sphere_missing_palette_categorical():
    column = 'category_feature'
    categories = ['A1', 'B1', 'B2', 'C', 'D']
    z_df[column] = np.random.choice(categories, size=len(z_df))
    
    palette = {"A1": 'red'}
    with pytest.raises(ValueError):
        obo.plot_sphere(z_df, colour_by = column, palette = palette)


def test_plot_sphere_invalid_palette_numerical():
    column = 'numeric_feature'
    z_df[column] = np.random.randn(len(z_df))
    assert pd.api.types.is_numeric_dtype(z_df[column])

    palette = "test_palette"
    with pytest.raises(ValueError):
        obo.plot_sphere(z_df, colour_by = column, palette = palette)

### TODO Test velocity