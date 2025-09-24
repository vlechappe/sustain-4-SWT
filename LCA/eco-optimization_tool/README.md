## Step by step

1. Install [Anaconda]([https://www.anaconda.com/products/individual](https://www.anaconda.com/products/individual))
2. Install Brightway
Open an anaconda prompt (terminal) and run the following commands
```
conda config --prepend channels conda-forge

conda config --append channels cmutel

conda config --append channels bsteubing

conda create -n ab activity-browser 
```

3. Setup project on brightway 
* open activity browser
```
activity-browser
```
* create a new project called swt_parametric_lca
* import biosphere 3.8
* import ecoinvent 3.8 cutoff database, take care to name it precisely *ecoinvent-3.8-cutoff*

4. Install Jupyter notebook in the ab environment

```
conda activate ab
conda install notebook
```

4. Run Jupyter
```
jupyter-notebook
```

5. Install required packages lca_algebraic 
* lca_algebraic
* sklearn
* noload
```
pip install lca_algebraic
pip install scikit-learn
pip install noload
```


5. Run *lca_param_syst_noload.ipynb* file with jupyter

After running the first cell, you should be able to see the three databases of your project

* |biosphere3|
* |ecoinvent-3.8-cutoff|
* |bdd_syst|

If that is the case, you should be able to run all the file. Enjoy !

### Run from VScode (optional)

1. Make sure that anaconda is in your path. (Windows users, check [this](https://stackoverflow.com/questions/44515769/conda-is-not-recognized-as-internal-or-external-command))

2. In the VScode terminal, run the followinf commande

   ```
   conda activate ab
   ```

3. Run the notebook (select the ab environment if VScode asks for it)

