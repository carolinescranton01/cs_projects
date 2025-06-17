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
export PATH=$PATH:/groups/kcooper/biobakery_env/jre1.8.0_451
export KNEADDATA_DB=/groups/kcooper/biobakery_databases/kneaddata
export HUMANN_NUC=/groups/kcooper/biobakery_databases/humann/chocophlan
export HUMANN_PROT

```
To close the editor, press *control X* and then *y* to save. Then, in the terminal, type:
```
source ~/.bashrc
```
again to activate the changes
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

Kneaddata takes raw sequencing data (can be zipped, fastq.gz) and removes adaptors, host contamination, and tandem repeats. This leaves you with a cleaner sequence to do other analysis on, reducing the chances of misinterpreting the data and making the analysis more accurate. 

Right now only the human genome is downloaded for filtering contamination, but other databases can be downloaded at the provided link AND custom databases can be built if you are processing data from a non-human organism.

To begin the analysis we will move to the raw_reads folder on the xdisk with the samples in it:
```
cd /xdisk/kcooper/[your_netID]/project_name/raw_reads
```
Now, we can run an individual command **or** a loop command on all of the files in the raw_reads folder so they are processed with kneaddata. Choose the command based on sample type (paired vs unpaired) and the amount of samples you want to process at once. If you choose to use loop command (multiple samples at once) on paired reads, you will need to use bash scripts created by CS, which is why the command looks weird - you are going to execute a script rather than type in the full command:
**paired, one sample at a time**
```
kneaddata --input1 sample1_R1.fastq.gz --input2 sample1_R2.fastq.gz -db $KNEADDATA_DB --output kneaddata_out --run-trim-repetitive --threads 4
```
**unpaired, one sample at a time**
```
kneaddata --unpaired sample1.fastq.gz --reference-db $KNEADDATA_DB --output kneaddata_out --run-trim-repetitive --threads 4
```
**paired, loop through multiple samples**
```
/groups/kcooper/biobakery_env/kneaddata_loop_paired.sh
```
**unpaired, loop through multiple samples**
```
for f in *.fastq.gz
do
n=${f%%.fastq.gz}
kneaddata --unpaired ${n}.fastq.gz --reference-db $KNEADDATA_DB --output kneaddata_out/${n} --run-trim-repetitive --threads 4
done
```
Outputs will be created in the kneaddata_out folder within the raw_reads folder. For each sample, we want to continue the analysis on the cleaned and trimmed reads. First, we will move the kneaddata_out folder out of raw_reads into the main project directory for the next steps. Then, we will move the cleaned and trimmed reads (should end in trimmed.fastq) to a new folder:
```
mv kneaddata_out ../
cd ..
mdkir clean_reads
cd kneaddata_out
mv *trimmed.fastq ../clean_reads
```
In the clean_reads folder we now should have all of our kneaddata-processed reads, with specific names (sample1_R1.trimmed.fastq, sample1_R2.trimmed.fastq, etc), which will be used in the next steps in the analysis.

### Step 2 - assign taxonomy with MetaPHlAn

