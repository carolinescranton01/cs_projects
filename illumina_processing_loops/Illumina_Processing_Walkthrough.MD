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
