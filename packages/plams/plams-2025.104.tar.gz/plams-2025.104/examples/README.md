# PLAMS Examples

A selection of example workflows using PLAMS. 
These are for demonstration and for use in documentation.
They require an AMS installation to run.

## Adding New Examples

Examples should be added into their own directory in `plams/examples`.
All scripts and any associated data should be added to this directory.
Ideally, new examples should be in notebook format, with descriptive text around each cell.

## Python and reStructuredText Generation

Once a new example notebook has been created, a python script and .rst file can be generated from it using the script `generate_example.sh`.
This script should be run from the examples directory, and takes a single argument which is the directory name of the example e.g.
```bash
cd plams/examples
./generate_example.sh WaterOptimization
```

The script will generate from the notebook a raw python script and reStructuredText text files and associated images.
These latter files are moved to a directory with a corresponding name in `plams/doc/source/examples`, for use in documentation.

As an example, the generated file structure should be like the following, from the initial `water_optimization.ipynb` file:

```
plams
├── examples
│ └── WaterOptimization
│   ├── water_optimization.ipynb
│   └── water_optimization.py
├── doc
│ └── source
│   └── examples
│     └── WaterOptimization
│       ├── WaterOptimization.rst
│       ├── WaterOptimization.common_footer.rst
│       ├── WaterOptimization.common_header.rst
│       ├── water_optimization.ipynb.rst
│       └── water_optimization_files
│         ├── water_optimization_5_0.png
│         └── water_optimization_18_0.png
```

Note that for this script to work, you will need `pandoc` installed on the system and `nbconvert`, `black` and `black[jupyter]` in your python env. 
In addition, the script uses, `amspython` so you will need a valid AMS installation with the `$AMSBIN` environment variable set.

Note all examples can be regenerated using the following command:
```bash
find . -maxdepth 1 -type d -not -name '.' | xargs -I {} ./generate_example.sh {} 
```

## Adding Examples to Documentation

To include the example in the documentation examples, use the following steps:

1. Run the `generate_example.sh` script as outlined above for the required example
2. If this is a new example, the main .rst template file will be created (e.g. `WaterOptimization.rst`) which can be modified as required
3. Other files (header, footer, notebook and image files) are recreated
4. Make sure the example is included in the relevant section in `plams/doc/source/examples/examples.rst`