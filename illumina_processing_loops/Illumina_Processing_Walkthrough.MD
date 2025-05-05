# Loops for Illumina metagenomic processing

This tutorial follows a similar format to the Initial Illumina Shotgun Metagenomics Processing tutorial, but uses loops, or code which is able to ‘loop’ through multiple input files at the same time to run that particular analysis on multiple files at once. Using loops, you can write in one command and analyze all of the data in a folder, rather than going sample-by-sample. Loops take longer to run, but once you press enter it will continue to run until the process finishes or the HPC times out, so you do not need to watch the computer and can go do other things while it runs. 

Example samples in this project will be called Sample1, Sample2, etc. Samples are paired reads, so each will have two files (Sample1_R1 and Sample1_R2)


## Setup for this tutorial:
 1.	Open the HPC for 6-12 hours with 24-94 cores (time and cores will depend on what steps you plan to run, they will be specified in each step) 
 2.	Create conda environments and install all required software for this tutorial

Cleaning
 - Fastp
 - Trim-galore

Metagenomics
 -	Kraken2
 - Metabat2
 - Maxbin2 – this has weird documentation, email caroline (carolinescranton@arizona.edu) if you need help

Assemblers
 - Spades

CheckM2 (alternatively, use the /groups/kcooper/Checkm2_env environment)
 - checkm2

See links to github pages or other repositories for more information on installation. Most are installed using bioconda (so use this if possible) but others require different processes.

 3. Setting CheckM2 environmental variable - only needs to be done once (ever), it tells checkm2 where to find the database it needs to run

```
nano ~/.bashrc
```
This will open the bashrc script for you to edit. Use the down arrow key to scroll all the way to the bottom. Add the following line to the bottom of the bashrc file:
```
export CHECKM2DB=/groups/kcooper/CheckM2_database/uniref100.KO.1.dmnd
```
Then, press control X, then y, and then enter and the window will close

 4.	Make a directory for your project in your xdisk folder on the HPC. Inside this folder, make a folder called raw_reads, and import the data into this folder using globus or another means of importing data as .fastq or .fastq.gz files

At this point you are ready to begin the tutorial!

## Tutorial
### Part 1 - cleaning the raw data

Initialize conda in your terminal
``` 
module load anaconda
source .bashrc
```
Activate the cleaning environment - name may vary based on what you named it, should be Cleaning or cleaning, but if you need to check the list of envs you have, type 'conda env list' and it will list them all.

Firstly, filter the reads with fastp - Move into the raw_reads folder where samples are housed and COPY AND PASTE the following command (right-click to paste on HPC). Do not type this by hand, or the formatting will be messed up and it won’t work. The loop assumes samples are in .fastq format and names end in R1.fastq, so either change this or change sample names to fit these requirements. Command runs the input samples through the fastp software and generates outputs Sample_trimmed_R1.fastq and Sample_trimmed_R2.fastq for each sample. This may give some short errors 'cannot stat "sample__trimmed*" ' – ignore this error message

```
cd raw_reads
for f in *.fastq; do
    if [[ $f == *R1.fastq ]]; then
        n=${f%%R1.fastq}
        fastp --in1 ${f} --in2 ${n}R2.fastq --out1 ${n}trimmed_R1.fastq --out2 ${n}trimmed_R2.fastq -l 50 -g -h wgs.html > wgs.log
    elif [[ $f == *R2.fastq ]]; then
        n=${f%%R2.fastq}
        fastp --in1 ${n}R1.fastq --in2 ${f} --out1 ${n}trimmed_R1.fastq --out2 ${n}trimmed_R2.fastq -l 50 -g -h wgs.html > wgs.log
    fi;
done
```
Go back a folder and make a new folder called ‘trimmed’ for the trimmed reads. Move the fastp-trimmed reads to trimmed. This will give a short error that says 'cannot stat *trimmed*' – ignore this, it still works.
```
cd ..
mkdir trimmed
cd raw_reads
mv *trimmed* ../trimmed
```
Move into trimmed folder to run trim-galore on the fastp-trimmed reads. Trim-galore removes adaptors (short sequences of DNA used to organize samples when sequencing multiple samples at the same time, which next-generation sequencing like Illumina almost always does). Copy and paste the following loop (again, don’t try to type it, the formatting will be messed up). This will run trim-galore on the samples and put outputs into a folder called trim-galore. The outputs from the two trimming steps are now going to be called ‘clean reads’ and will be moved into a folder to keep them separate for the rest of the analysis
```
cd ../trimmed
for f in *.fastq; do
  if [[ $f == *R1.fastq ]]; then
    n=${f%%R1.fastq}
    trim_galore --paired ${f} ${n}R2.fastq -o trim-galore
  fi
done
```
After running trim-galore we want to rename out outputs (names are getting too long). Follow the two loops to rename the R1 and then the R2 files with _clean at the end to denote that these are the clean reads. Move into the trim-galore file, then copy and paste the loop.
```
cd trim-galore
for f in *; do n=${f%%}; mv "${n}" "${f//trimmed_R1_val_1.fq/R1_clean.fastq}"; mv "${n}" "${f//trimmed_R2_val_2.fq/R2_clean.fastq}"; done
```
Copy the double-trimmed and renamed reads to a new folder called clean_reads. 
```
cd ../..
mkdir clean_reads
cp trimmed/trim_galore/*clean* clean_reads
```
### Part 2 - Assign Taxonomy (Kraken)
Deactivate cleaning environment, activate metagenomics environment for Kraken2 analysis, make a folder for kraken2, and copy clean_reads to merged
