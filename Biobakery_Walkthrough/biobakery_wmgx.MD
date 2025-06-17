# Biobakery walkthrough (whole-genome sequence data)

This walk-through explains how to use the biobakery suite of tools to process whole genome short-read seuqence data (ie Illumina paired-read data). Data will be cleaned and trimmed to increase quality and remove human contamination (option for other host contamination, ie cats, lettuce, etc available) using kneaddata, mapped to different taxa using metaphlan, and a functional analysis will be done using humann. All databases and software packages are previously installed by CS in the groups folder, but you will need to set environmental variables to access the databases the first time you use this tutorial.

## Part 1 - setup

The biobakery tools are installed in the conda environment /groups/kcooper/biobakery_env. To actuvate the environment, open the HPC and type the following:
```
module load anaconda
source .bashrc
conda activate /groups/kcooper/biobakery_env
```
You should now see (/groups/kcooper/biobakery_env) before your netID at the left-hand side of the terminal. Now that you have acvtivated the environment you can run commands from the programs which are installed within it. 
Next, we need to set environmental variables to allow your computer to find the databases which it needs to run each of the commands we use later on. We need to create variables for kneaddata, humann, and metaphlan. The databases are installed in /groups/kcooper/biobakery_databases. We want to put the variables in our .bashrc file, which is a file that gives the computer 'directions' allowing it to understand the commands we type in. To access this, type the following:
```
nano ~/.bashrc
```
This should pull up an editor which displays the contents in the .bashrc file. Scroll to the end of the file using the down arrow key and type in the following lines to set the variables:
```
KNEADDATA_DB=/groups/kcooper/biobakery_databases/kneaddata
HUMANN_NUC=/groups/kcooper/biobakery_databases/humann/chocophlan
HUMANN_PROT

```
Now, everything should be set up to allow you to run the biobakery tools detailed in this page from your own HPC. The final step is to upload your data to the HPC's xdisk. This can be done using globus file transfer (or in other ways - the data may already be somewhere else and just needs to be moved/copied over. This step will be different for everyone/for every dataset!)

For consistency, the file structure in this tutorial will be outlined. On your folder on the xdisk, create a folder titled with the project name (example: project_name) and use mv, cp, or globus to move your raw sequence data (fastq.gz files, often will be paired - sample1_R1.fastq.gz and sample1_R2.fastq.gz are zipped files containing the forward and reverse reads for sample 1) into the raw_reads folder. 
```
cd /xdisk/kcooper/[your_netID]/
mkdir project_name
cd project_name
mkdir raw_reads
```

Now everything should be set up and you can run your analysis.

## Part 2 - Data processing
### Step 1 - data cleanup with kneaddata
Link to github page: https://github.com/biobakery/kneaddata



