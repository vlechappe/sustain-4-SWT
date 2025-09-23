## Step by step

1. Install [Anaconda]([https://www.anaconda.com/products/individual](https://www.anaconda.com/products/individual))
2. Install Brightway
In a terminal run the following commands
```
conda config --prepend channels conda-forge

conda config --append channels cmutel

conda config --append channels bsteubing

conda create -n ab activity-browser
```

3. Setup project on brightway 
* import ecoinvent 3.8 cutoff database, take care to name it precisely *ecoinvent-3.8-cutoff*
* import biosphere 3

4. Install Jupyter notebook in the ab environment

```
conda activate ab
conda install notebook
```

4. Run Jupyter
```
jupyter-notebook
```

5. Install lca_algebraic 
```
pip install lca_algebraic
```
6. Run *lca_param_syst_noload.ipynb* file with jupyter


