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
### Part 2 - Assign Taxonomy (Kraken - normal and special database)
Deactivate the cleaning environment, activate the metagenomics environment for Kraken2 analysis, make a folder for kraken2, and copy clean_reads to the kraken2 folder to merge them
```
conda deactivate
conda activate metagenomics
mkdir kraken2
cp clean_reads/*.fastq kraken2
```
Merge samples for Kraken2 analysis – kraken2 only takes 1 input so R1 and R2 must be merged into a singular file using the cat command (concatenate). If you have only a few samples this can be done by hand, but you can also use this loop:
```
for f in *.fastq; do if [[ $f == *R1*.fastq ]]; then n=${f%%R1*.fastq}; cat ${f} ${n}R2*.fastq > ${n}merged.fastq; fi; done
```
Remove the non-merged reads from this folder
```
rm -r clean.fastq
```
Run kraken2 on the reads. Most analysis will use the MY_KRAKEN2_DATABASE database, which is significantly smaller than the Kraken_Special_DB (contains all known genomes and non-redundant sequences, whereas MY_KRAKEN2_DATABASE does not have non-redundant sequences). Only use Kraken_Special_DB if you are on the high-memory node of the HPC and have a lot of time, and were specifically instructed to do so, as it will not succeed. This generates two text files - a report.txt and an output.txt. There are not any instructions on what to do with those in this tutorial, but they are used for analysis, so contact carolinescranton@arizona.edu if you need information on that!
```
for f in *.fastq; do n=${f%%.fastq}; kraken2 --db /groups/kcooper/MY_KRAKEN2_DB/ --report "${n}_report.txt" --output "${n}_output.txt" ${n}.fastq -t 94; done
```
If you are using the special database, the only change is after the --db flag, where you would write /groups/kcooper/Kraken_Special_DB (as of 5-1-25, that database is not in there - will update it when it is!)

### Part 3 - assembly
We will now go back to the non-merged reads for the rest of the analysis, which starts with assembly via metaSPADES. We need to make and move to a different folder and change conda environments
```
conda deactivate
conda activate Assemblers
cd ..
mkdir spades
cp clean_reads/*.fastq spades
cd spades
```
Run metaSPADES – **this is very time intensive! If you are doing this on multiple samples, it will likely not finish all of them unless the samples are small or the HPC is open for a very long time (+100 hours)**. For context, a 2 GB paired sample took ~17 hours to run – loop can be used on small samples, if there are few samples, or if HPC is open for a while. In the loop, 'Assemblers' should be changed to match your conda environment name (which is probably assemblers or Assemblers). Copy and paste the following
```
for f in *.fastq; do
    if [[ $f == *R1_clean.fastq ]]; then
        n=${f%%R1_clean.fastq}
        ~/.conda/envs/Assemblers/bin/spades.py --meta -1 ${f} -2 ${n}R2_clean.fastq -o ${n}spades -t 94
    elif [[ $f == *R2_clean.fastq ]]; then
        n=${f%%R2_clean.fastq}
        ~/.conda/envs/Assemblers/bin/ --meta -1 ${n}R1_clean.fastq -2 ${f} -o ${n}spades 
    fi
done
```
### Part 4 - Binning
MetaSPADES takes the sequence data and makes it into contigs, which are longer stretches of DNA which are supposed to be in one sequence (ie. putting together 20 chunks of E. coli DNA into one singular long chunk of E. coli DNA, in order). The output of SPADES is a folder called the sample name, and within the folder there are lots of other folders and files but the contigs.fasta file is the most important. However, for all samples, it will be called contigs.fasta, so we need to rename these to include the sample name.

This is a lot more complicated of a process to automate, so rather than you typing it or doing it by hand, you will make and execute a python script (basically a simple program) which does it for you. Enter the following commands to create a new folder for the contigs files to move to, and then within the spades folder, create the script:
```
cd ..
mkdir binning
cd spades
nano move_contigs.py
```
This will create a python script called move_contigs.py in your current folder (spades) and open the GNU nano editor. Now, copy and paste the entire segment of code (using a right click + paste to paste into the HPC) into the nano editor. 
```
#!/usr/bin/env python3

import os
import shutil
# ----------
def move_contigs(base_directory, binning_directory):
    for root, dirs, files in os.walk(base_directory):
        print(root, dirs, files)  
        for file in files:
            if file == “contigs.fasta”:
                subdirectory_name = os.path.basename(root)
                new_filename = f'{subdirectory_name}_contigs.fasta'
                original_file_path = os.path.join(root, file)
                new_file_path = os.path.join(binning_directory, new_filename)
                shutil.copy(original_file_path, new_file_path)
# ----------
if __name__ == “__main__”:
    base_directory = input(“Enter path to spades directory: “)
    binning_directory = input(“Enter path to binning directory: “)
    move_contigs(base_directory, binning_directory)
```
After that is copied in, press control X, Y, and then enter to save the script. When you run it, it will prompt you to put in the path to the spades and binning directories. These should be:
_/xdisk/kcooper/**netid/project-name**/spades_
_/xdisk/kcooper/**netid/project-name**/binning_
Make sure you change your netid and project-name to match what you are doing!!!


