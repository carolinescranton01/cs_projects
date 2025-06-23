# Biobakery walkthrough (whole genome sequencing, 

6-23-25 - need to rewrite - kneaddata good, updated metaphlan to 4.2.2 with Oct22 CHOCOPhlAn DB (202403) and humann 4. humann4 is only compatable with the old metaphlan DB, compatibility has not been updated for newer DB to use the two softwares together

Metaphlan command
metaphlan Maricopa-R_R1_kneaddata_paired_merged.fastq --index mpa_vJun23_CHOCOPhlAnSGB_202403 --mapout Maricopa-R.bowtie2.bz2 --nproc 8 --input_type fastq -o Maricopa-R_profiled.tsv --verbose -t real_ab_w_read_stats

Humann command
humann --input Maricopa-R_R1_kneaddata_paired_merged.fastq --output humann_out  --bypass-translated-search --taxonomic-profile /xdisk/kcooper/carolinescranton/biobakery_test/metaphlan/Maricopa-R_profiled.tsv --threads 8


This walk-through explains how to use the biobakery suite of tools to process whole genome short-read seuqence data (ie Illumina paired-read data). Data will be cleaned and trimmed to increase quality and remove human contamination (option for other host contamination, ie cats, lettuce, etc available) using kneaddata and a functional analysis (including mapping reads to different taxa via metaphlan) will be done using humann. All databases and software packages are previously installed by CS in the groups folder, but you will need to set environmental variables to access the databases the first time you use this tutorial. NOTE - only the basic functions of each program are used in this walkthrough. For each of the three major programs (kneaddata, metaphlan, and humann), there are many more options available to increase the depth of analysis or change the outputs to be compatible with other forms of analysis/export into R. See the github pages or type [program] --help for more information on what each program can do. Additionally, see https://github.com/biobakery/biobakery/wiki for an overview of all of the connected biobakery tools which can be used in conjunction with kneaddata, humann, and metaphlan.

This tutorial uses an older version of humann and metaphlan (older versions were used due to incompatibility issues with the newest versions, humann v4 and metaphlan v4) which runs the two steps simultaneously. To use the most updated versions, see biobakery_wmgx_newversions.md (6-20-25 note - this doc has not been created yet! and versions/databases have not been installed!)

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
export METAPHLAN_DB=/groups/kcooper/biobakery_env/lib/python3.9/site-packages/metaphlan/metaphlan_databases
export HUMANN_NUC=/groups/kcooper/biobakery_databases/humann/chocophlan

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
Note - running trimmomatic and TRF. FastQC is not run.

To begin the analysis we will move to the raw_reads folder on the xdisk with the samples in it:
```
cd /xdisk/kcooper/[your_netID]/project_name/raw_reads
```
Now, we can run an individual command **or** a loop command on all of the files in the raw_reads folder so they are processed with kneaddata. Choose the command based on sample type (paired vs unpaired) and the amount of samples you want to process at once. If you choose to use loop command (multiple samples at once) on paired reads, you will need to use bash scripts created by CS, which is why the command looks weird - you are going to execute a script rather than type in the full command:

**paired, one sample at a time**
```
kneaddata --input1 sample1_R1.fastq.gz --input2 sample1_R2.fastq.gz -db $KNEADDATA_DB --output kneaddata_out --threads 4
```
**unpaired, one sample at a time**
```
kneaddata --unpaired sample1.fastq.gz --reference-db $KNEADDATA_DB --output kneaddata_out --threads 4
```
**paired, loop through multiple samples** - note: only works on zipped samples. use gzip *.fastq to zip any fastq files
```
/groups/kcooper/biobakery_env/kneaddata_loop_paired.sh
```
**unpaired, loop through multiple samples**
```
for f in *.fastq.gz
do
n=${f%%.fastq.gz}
kneaddata --unpaired ${n}.fastq.gz --reference-db $KNEADDATA_DB --output kneaddata_out/${n} --threads 4
done
```
Outputs will be created in the kneaddata_out folder within the raw_reads folder. For each sample, we want to continue the analysis on the cleaned and trimmed reads. First, we will move the kneaddata_out folder out of raw_reads into the main project directory for the next steps. Then, we will move the cleaned and trimmed reads (should end in paired_1.fastq or paired_2.fastq for paired reads, or kneaddata.fastq for unpaired) to a new folder. Depending on whether your reads are paired on unpaired, run the commands (denoted by the comments, beginning with #)
```
mv kneaddata_out ../
cd ..

# for single-end reads (*kneaddata.fastq)
mkdir -p clean_reads; for f in kneaddata_out/*/*kneaddata.fastq; do mv "$f" clean_reads/; done

# for paired-end reads(*paired_1.fastq and *paired_2.fastq)
mkdir -p clean_reads; for f in kneaddata_out/*/*paired_[12].fastq; do mv "$f" clean_reads/; done
```
In the clean_reads folder we now should have all of our kneaddata-processed reads, with specific names (sample1_R1_kneaddata_paired_1.fastq, sample1_R2_kneaddata_paired_2.fastq, etc), which will be used in the next steps in the analysis.

### Step 2 - assign function and taxonomy with MetaPHlAn and HUMAnN
Link to metaphlan3 github: https://github.com/biobakery/MetaPhlAn/wiki/MetaPhlAn-3
Link to humann github: https://github.com/biobakery/humann

HUMAnN looks at the nucleotide sequences and translates them into potential proteins to identfy the functional capabilities of the bacteria within the sample. It uses 2 databases (chocophlan for a nucleotide search and uniref90 for a translated search). Either of the searches can be bypassed to save time, but running both generates a bettter picture of the capabilities of the microbes in the sample. Humann does not work as well on paired-end reads, so for paired-end reads we will concatonate (join) the forward R1 and reverse R2 fastq files. MetaPHlAn assigns taxonomy to the samples by identifying specific genes within the samples which match to known taxa. Metaphlan is run as a step in the humann command, so we will just run humann on our concatenated samples for this step. 

NOTE - as of 6/17/25, only the chocophlan DB is installed (not enough space on drive for uniref90, will download when necessary). Humann must be run with --bypass-translated-search flag in order to work. 

First, concatenate the reads in a new folder called humann:
```
cd ..
mkdir humann

cp clean_reads/*.fastq humann
cd humann
for f in *.fastq; do if [[ $f == *_1.fastq ]]; then n=${f%%_1.fastq}; cat ${f} ${n}_2.fastq > ${n}_merged.fastq; fi; done
rm *_1.fastq
rm *_2.fastq
```

Next, run humann on the concatenated reads with the bypass-translated-search flag to skip the uniref90 search (DB is not downloaded - contact CS if you need it). If you would like to specify more metaphlan options, use the --metaphlan-options='PUT_FLAGS_AND_INFO_HERE' flag/format (ie. --metaphlan-options='-t rel_ab', or another flag can be used (use **metaphlan --help** to see possible flags):
```
for f in *.fastq; do
  base=${f%.fastq}       
  base=${base%_merged} 
  humann --input "$f" --output humann_out  --bypass-translated-search --metaphlan-options='-t rel_ab' --threads 8
done
```
This command runs humann and metaphlan using 8 threads (cores/a measure of computing power or resources), bypassing the translated (uniref) search, and generates metaphlan outputs with relative abundance along with humann outputs. The last step is merging tables to use in future stats/visualation analysis:

``
cd humann_out


After this, you can proceed to the visualzation and stats workflows, detailed in the biobakery_vis.md and biobakery_stats.md documents. You will need the merged data tables from above as well as a metadata file (this file has sample IDs which match those on the tables, and other non-sequence related information in it, such as where the sample was collected from, what date, the conditions of the host (ie sick or not sick), etc. Your metadata file should have all of the information you would want to compare your samples on, so if you were looking at soil from different fields before and after a rain storm, for each sample you would need the field number, the date, and the weather from when that sample was taken in order to make that comparison). 
