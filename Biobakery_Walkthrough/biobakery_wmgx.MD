# Biobakery walkthrough (whole-genome sequence data)

This walk-through explains how to use the biobakery suite of tools to process whole genome short-read seuqence data (ie Illumina paired-read data). Data will be cleaned and trimmed to increase quality and remove human contamination (option for other host contamination, ie cats, lettuce, etc available) using kneaddata, mapped to different taxa using metaphlan, and a functional analysis will be done using humann. All databases and software packages are previously installed by CS in the groups folder, but you will need to set environmental variables to access the databases the first time you use this tutorial.

## Part 1 - setup

The biobakery tools are installed in the conda environment /groups/kcooper/biobakery_env. To actuvate the environment, open the HPC and type the following:
```
module load anaconda
source .bashrc
conda activate /groups/kcooper/biobakery_env
```
You should now see (/groups/kcooper/biobakery_env) before your name at the left-hand side of the terminal.
