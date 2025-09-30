This READ.ME explain how to generate a .csv file with all the masses of the wind turbine. 

## 1. Generate .mat files with OpenAFPM.m

To create the .mat files, we use the tool [OpenAfpm](https://www.openafpm.net/). We put as input the data from the handbook "Construire une éolienne Piggott" of the Tripalium association, the french translation of a "Wind Turbine Recipe Book" of Hugh Piggott. 

You can create your own .mat or use the ones in the repository *eco-optimization_tool/SizingWT/OutputsOpenAFPM/*.



## 2. Generate  .FCStd files with OpenAFPM CAD Core

Then, we have created .FCStd files with the tool [OpenAFPM CAD Core](https://github.com/gbroques/openafpm-cad-core?tab=readme-ov-file) (click to go on their Git Hub). The inputs for MagnAFPM are the .mat files. For the Furling and User data, you can refer to the table InputsAfpmCad.xlsx in the repository *eco-optimization_tool/SizingWT/OutputsOpenAFPM/*. This file links the expected data with that from the manual.

You can create your own .FCStd or use the ones in the repository *eco-optimization_tool/SizingWT/WT_3D_Files/*.

##  3. Generate .csv files with export_volumes.py

Now you have the .FCStd files of your wind turbine, you can use the code *export_volumes.py* in order to extract all the relevant masses from your 3D model. To do so, you need to have the logiciel [FreeCAD](https://www.freecad.org/) on your computer. Then, you can run the python code as an external script with the following command 

> /path/to/FreeCAD_1.0.AppImage --console /path/to/export_volumes.py

(adapt it to your own configuration)

It will automatically generate the good .csv file. 

To navigate through all your .FCStd files, you will need to change the files paths at the beginning of *export_volumes.py*.



You can create your own .csv  files or use the ones in the repository *eco-optimization_tool/SizingWT/Volume_csv/*.