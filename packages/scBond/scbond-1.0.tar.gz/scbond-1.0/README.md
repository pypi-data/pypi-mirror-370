# scBOND: Biologically faithful bidirectional translation between single-cell transcriptomes and DNA methylomes with adaptability to paired data scarcity 

A sophisticated framework for bidirectional cross-modality translation between scRNA-seq and scDNAm profiles with broad biological applicability. We show that **scBOND**(a) accurately translates data while preserving biologically significant differences between closely related cell types. It also recovers functional and tissue-specific signals in the human brain and reveals stage-specific and cell type-specific transcriptional-epigenetic mechanisms in the oligodendrocyte lineage. We further introduce **scBOND-Aug**, a powerful enhancement of scBOND that leverages biologically guided data augmentation, achieving remarkable performance and surpassing traditional methods in paired data-limited scenarios.


## Installation

It's prefered to create a new environment for scBOND

```
conda create -n scBond python==3.9
conda activate scBond
```

scBOND is available on PyPI, and could be installed using

```
pip install scBond
```

Installation via Github is also provided

```
git clone https://github.com/Biox-NKU/scBOND
cd scBOND
pip install -r requirements.txt
```

This process will take approximately 5 to 10 minutes, depending on the user's computer device and internet connectivition.

## Quick Start

Illustrating with the translation between  scRNA-seq and scDNAm data as an example, scBOND could be easily used following 3 steps: data preprocessing, model training, predicting and evaluating. 

Generate a scBOND model first with following process:

```python
from scBond.bond import Bond
bond = Bond()
```

### 1. Data preprocessing

* Before data preprocessing, you should load the **raw count matrix** of scRNA-seq and scDNAm data via `bond.load_data`:
  
  ```python
  bond.load_data(RNA_data, MET_data, train_id, test_id, validation_id)
  ```
  
  | Parameters    | Description                                                  |
  | ------------- | ------------------------------------------------------------ |
  | RNA_data      | AnnData object of shape `n_obs` × `n_vars`. Rows correspond to cells and columns to genes. |
  | MET_data      | AnnData object of shape `n_obs` × `n_vars`. Rows correspond to cells and columns to peaks. |
  | train_id      | A list of cell IDs for training.                             |
  | test_id       | A list of cell IDs for testing.                              |
  | validation_id | An optional list of cell IDs for validation, if setted None, bond will use a default setting of 20% cells in train_id. |
  
  Anndata object is a Python object/container designed to store single-cell data in Python packege [**anndata**](https://anndata.readthedocs.io/en/latest/) which is seamlessly integrated with [**scanpy**](https://scanpy.readthedocs.io/en/stable/), a widely-used Python library for single-cell data analysis.

* For data preprocessing, you could use `bond.data_preprocessing`:
  
  ```python
  bond.data_preprocessing()
  ```
  
  You could save processed data or output process logging to a file using following parameters.
  
  | Parameters   | Description                                                                                  |
  | ------------ | -------------------------------------------------------------------------------------------- |
  | save_data    | optional, choose save the processed data or not, default False.                              |
  | file_path    | optional, the path for saving processed data, only used if `save_data` is True, default None.  |
  | logging_path | optional, the path for output process logging, if not save, set it None, default None.       |

  scBOND also support to refine this process using other parameter, however, we strongly recommend the default settings to keep the best result for model.

### 2. Model training

* Before model training, you could choose to use data augmentation strategy or not. If using data augmentation, scBOND will generate synthetic samples with the use of cell-type labels(if `cell_type` in `adata.obs`) .

  scButterfly provide data augmentation API:
  
  ```python
  bond.augmentation(enable_augmentation)
  ```

  You could choose parameter `enable_augmentation` by whether you want to augment data (`True`) or not (`False`), this will cause more training time used, but promise better result for predicting. 
  
  * If you choose `enable_augmentation = True`, scBOND-Aug will try to find `cell_type` in `adata.obs`. If failed, it will automaticly transfer to `False`.
  * If you just want to using original data for scBOND training, set `enable_augmentation = False`.
  
* You could construct a scBOND model as following:
  
  ```python
  bond.construct_model(chrom_list)
  ```
  
  scBOND need a list of peaks count for each chromosome, remember to sort peaks with chromosomes.
  
  | Parameters   | Description                                                                                    |
  | ------------ | ---------------------------------------------------------------------------------------------- |
  | chrom_list   | a list of peaks count for each chromosome, remember to sort peaks with chromosomes.            |
  | logging_path | optional, the path for output model structure logging, if not save, set it None, default None. |
  
* scBOND model could be easily trained as following:
  
  ```python
  bond.train_model()
  ```

  | Parameters   | Description                                                                             |
  | ------------ | --------------------------------------------------------------------------------------- |
  | output_path  | optional, path for model check point, if None, using './model' as path, default None.   |
  | load_model   | optional, the path for load pretrained model, if not load, set it None, default None.   |
  | logging_path | optional, the path for output training logging, if not save, set it None, default None. |
  
  scBOND also support to refine the model structure and training process using other parameters for `bond.construct_model()` and `bond.train_model()` .

### 3. Predicting and evaluating

* scBOND provide a predicting API, you could get predicted profiles as follow:

  ```python
  M2R_predict, R2M_predict = bond.test_model()
  ```

  A series of evaluating method also be integrated in this function, you could get these evaluation using parameters:

  | Parameters    | Description                                                                                 |
  | ------------- | ------------------------------------------------------------------------------------------- |
  | output_path   | optional, path for model evaluating output, if None, using './model' as path, default None. |
  | load_model    | optional, the path for load pretrained model, if not load, set it None, default False.      |
  | model_path    | optional, the path for pretrained model, only used if `load_model` is True, default None.   |
  | test_cluster  | optional, test the correlation evaluation or not, including **AMI**, **ARI**, **HOM**, **NMI**, default False.|
  | test_figure   | optional, draw the **tSNE** visualization for prediction or not, default False.             |
  | output_data   | optional, output the prediction to file or not, if True, output the prediction to `output_path/A2R_predict.h5ad` and `output_path/R2A_predict.h5ad`, default False.                                          |

- Also, scBOND provide **a separate predicting API** for single modal predicting. You can predict DNAm profile with RNA profile as follow:

  ```python
  R2M_predict = bond.predict_single_modal(data_type='rna')
  ```

  And you can predict RNA profile with DNAm profile as follow:

  ```python
  M2R_predict = bond.predict_single_modal(data_type='met')
  ```

## We provide detail tutorials for users with GSE140493 dataset in  [scBOND usage](https://github.com/BioX-NKU/scBOND/blob/main/examples/scBOND_usage.ipynb), [scBOND-aug usage](https://github.com/BioX-NKU/scBOND/blob/main/examples/scBOND_aug_usage.ipynb) and  [scBOND for single modality prediction](https://github.com/BioX-NKU/scBOND/blob/main/examples/scBOND_for_single_modality.ipynb) 

