# Shotgun Metagenomics (Illumina) Processing Workflow

This tutorial follows a similar format to the Initial Illumina Shotgun Metagenomics Processing tutorial, but uses loops, or code which is able to ‘loop’ through multiple input files at the same time to run that particular analysis on multiple files at once. Using loops, you can write in one command and analyze all of the data in a folder, rather than going sample-by-sample. Loops take longer to run, but once you press enter it will continue to run until the process finishes or the HPC times out, so you do not need to watch the computer and can go do other things while it runs. 

Example samples in this project will be called Sample1, Sample2, etc. Samples are paired reads, so each will have two files (Sample1_R1 and Sample1_R2)
At the bottom there is a visualization of the file structure and key files in each folder. 

### Non-loop commands - listed at each step. 
Non-loop examples use sampleIDs 'sample_R1.fastq' and 'sample_R2.fastq'. When running an individual sample, these names need to be changed for both the inputs and outputs in the command.

## Setup for this tutorial:
 1.	Open the HPC for 6-12 hours with 24-94 cores (time and cores will depend on what steps you plan to run and how much data you are analyzing, they will be specified in each step) 
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

Initialize conda in your terminal and go to the xdisk where your data is stored (make sure to change 'netid' in the last command to YOUR net ID!) 
``` 
module load anaconda
source .bashrc
cd /xdisk/kcooper/netid
```
Activate the cleaning environment - name may vary based on what you named it, should be Cleaning or cleaning, but if you need to check the list of envs you have, type 'conda env list' and it will list them all.

Firstly, filter the reads with fastp - Move into the raw_reads folder where samples are housed and COPY AND PASTE the following command (right-click to paste on HPC). Do not type this by hand, or the formatting will be messed up and it won’t work. The loop assumes samples are in .fastq format and names end in R1.fastq, so either change this or change sample names to fit these requirements. Command runs the input samples through the fastp software and generates outputs Sample_trimmed_R1.fastq and Sample_trimmed_R2.fastq for each sample. This may give some short errors 'cannot stat "sample__trimmed*" ' – ignore this error message

```
cd raw_reads

# single-sample command:

fastp --in1 sample_R1.fastq --in2 sample_R2.fastq --out1 sample_trimmed_R1.fastq --out2 sample_trimmed_R2.fastq -l 50 -g -h wgs.html > wgs.log

# loop command:
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
# single-sample command:
trim_galore --paired sample_trimmed_R1.fastq sample_trimmed_R2.fastq -o trim-galore

# loop command:
for f in *.fastq; do
  if [[ $f == *R1.fastq ]]; then
    n=${f%%R1.fastq}
    trim_galore --paired ${f} ${n}R2.fastq -o trim-galore
  fi
done
```
After running trim-galore we want to rename our outputs (names are getting too long). Follow the two loops to rename the R1 and then the R2 files with _clean at the end to denote that these are the clean reads. Move into the trim-galore file, then copy and paste the loop.
```
cd trim-galore
for f in *; do n=${f%%}; mv "${n}" "${f//trimmed_R1_val_1.fq/R1_clean.fastq}"; mv "${n}" "${f//trimmed_R2_val_2.fq/R2_clean.fastq}"; done
```
Copy the double-trimmed and renamed reads to a new folder called clean_reads. 
```
cd ../..
mkdir clean_reads
cd trimmed/trim-galore
cp *clean* ../../clean_reads
cd ../..
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
cd kraken2
# single-sample command:
cat sample_R1_clean.fastq sample_R2_clean.fastq > sample_merged.fastq

# loop command:
for f in *.fastq; do if [[ $f == *R1*.fastq ]]; then n=${f%%R1*.fastq}; cat ${f} ${n}R2*.fastq > ${n}merged.fastq; fi; done
```
Remove the non-merged reads from this folder
```
rm -r *clean.fastq
```
Run kraken2 on the reads. Most analysis will use the MY_KRAKEN2_DATABASE database, which is significantly smaller than the Kraken_Special_DB (contains all known genomes and non-redundant sequences, whereas MY_KRAKEN2_DATABASE does not have non-redundant sequences). Only use Kraken_Special_DB if you are on the high-memory node of the HPC and have a lot of time, and were specifically instructed to do so, as it will not succeed. This generates two text files - a report.txt and an output.txt. There are not any instructions on what to do with those in this tutorial, but they are used for analysis, so contact carolinescranton@arizona.edu if you need information on that!
```
# single-sample command:
kraken2 --db /groups/kcooper/MY_KRAKEN2_DB/ --report sample_report.txt --output sample_output.txt sample_merged.fastq -t 94

# loop command:
for f in *.fastq; do n=${f%%.fastq}; kraken2 --db /groups/kcooper/MY_KRAKEN2_DB/ --report "${n}_report.txt" --output "${n}_output.txt" ${n}.fastq -t 94; done
```
If you are using the special database, the only change is after the --db flag, where you would write /groups/kcooper/Kraken_Special_DB (as of 5-1-25, that database is not in there - will update it when it is!)

**EXTRA STEP FOR ANALYSIS IN R**
To analyze kraken2 outputs in R, we convert them into a special format called a .biom file. To generate a .biom file you need metadata, which is data about the sequence data (ie. where it came from, what day it was collected, if the source was sick or healthy, etc). This metadata needs to be in a tab-separated-value file (.tsv). I usually make these on microsoft excel, save them as .txt files, and then replace the .txt to .tsv in the filename as you cannot save a microsoft excel table to a .tsv file directly. This file must be uploaded into the same folder where your kraken2 reports are. **The first column in the metadata table should be named sampleID and the values in that column need to correspond to the sample names - ie. if your sample was called positive1.fastq, and your kraken2 report is called positive1_report.txt, the value in sampleID should be positive1**. To run kraken biom, make sure the command is installed in the same environment as kraken2 (conda install kraken-biom -c bioconda) and then use the following command:
```
kraken-biom sample1_report.txt sample2_report.txt sample3_report.txt -m metadata.tsv -o output.biom
```
where samples are called 'sample1', 'sample2', and 'sample3', metadata is called 'metadata.tsv', and your output biom file is called 'output.biom'

NOTE: Report files must all be listed in the command. If you have a lot of files, the most efficient way to get this list of file names is to type:
```
ls -1 | tr '\n' ' ' > filenames.txt
```
Which lists the file names, removes the new lines and replaces them with a space, and outputs a new file called filenames.txt. Then, open the filenames.txt file (which should say sample1_report.txt sample2_report.txt sample3_report.txt), make sure there are no unnecissary filenames (like the metadata.tsv file, which can be deleted from the list of file names), and then copy and paste that into the kraken-biom command when writing it in the terminal.


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
# single-sample command:
~/.conda/envs/Assemblers/bin/spades.py --meta -1 sample_R1_clean.fastq -2 sample_R2_clean.fastq -o sample_spades -t 94

# loop command:
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
MetaSPADES takes the sequence data and makes it into contigs, which are longer stretches of DNA which are supposed to be in one sequence (ie. putting together 20 chunks of E. coli DNA into one singular long chunk of E. coli DNA, in order). The output of SPADES is a folder called the sample name, and within the folder there are lots of other folders and files but the contigs.fasta file is the most important. However, for all samples, it will be called contigs.fasta, so we need to rename these to include the sample name. We also need to move back to the metagenomics conda environment.

This is a lot more complicated of a process to automate, so rather than you typing it or doing it by hand, you will make and execute a python script (basically a simple program) which does it for you. Enter the following commands to create a new folder for the contigs files to move to, and then within the spades folder, create the script:
```
conda deactivate
conda activate metagenomics
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
            if file == "contigs.fasta":
                subdirectory_name = os.path.basename(root)
                new_filename = f'{subdirectory_name}_contigs.fasta'
                original_file_path = os.path.join(root, file)
                new_file_path = os.path.join(binning_directory, new_filename)
                shutil.copy(original_file_path, new_file_path)
# ----------
if __name__ == "__main__":
    base_directory = input("Enter path to spades directory: ")
    binning_directory = input("Enter path to binning directory: ")
    move_contigs(base_directory, binning_directory)
```
After that is copied in, press control X, Y, and then enter to save the script. When you run it, it will prompt you to put in the path to the spades and binning directories. These should be:

/xdisk/kcooper/**netid/project-name**/spades

/xdisk/kcooper/**netid/project-name**/binning

Make sure you change your netid and project-name to match what you are doing!

To run the script, type the following **while in the spades folder where the script is located**:
```
module load python
python3 move_contigs.py
```
This should rename the contigs from each folder as foldername_spades_contigs.fasta, and copy them into binning folder. There will be a lot of output in the terminal but this is ok. The last thing we need to do is copy the merged reads over as a template for maxbin2. These should be in the kraken folder. Copy them over and move back to the binning folder with the following code:
```
cd ../kraken2
cp *.fastq ../binning
cd ../binning
```
Now we should have specifically-named contig .fasta files for each sample as well as the clean _merged.fastq files for each sample (with matching names), and can continue with metabat and maxbin2 binning


Metabat2 - in the binning folder, copy and paste this to run. It will make directories titled with the sample names (samplename_contigs)_metabat with the metabat outputs in them
```
# single-sample command:
metabat2 -i sample_contigs.fasta -o sample_contigs_metabat

# loop command:
for f in *.fasta; do n=${f%%.fasta}; mkdir ${n}_metabat2; metabat2 -i ${n}.fasta -o ${n}_metabat; mv ${n}.fa ${n}_metabat2; done
```

**NOTE: as of Oct 1 2025, this code for Maxbin2 is not working. I am trying to fix it and will update when I can!! - caroline**

Maxbin2 – copy and paste the following script to run Maxbin2 on the samples, using the original clean reads as a template to predict abundance. You need to update FragGeneScan the first time you use this program by re-installing a higher version, this is the first line in the code. 
```
# update fraggenescan:
conda install -c bioconda fraggenescan

# single-sample command:
run_MaxBin.pl -contig sample_contigs.fasta -reads sample_merged.fastq -max_iteration 5 -out sample_maxbin2

# loop command:
for file in *.fasta; do n="${file%%_contigs.fasta}"; 
mkdir "${n}_maxbin2";
run_MaxBin.pl -contig "$file" -reads "${n}_merged.fastq" -max_iteration 5 -out "${n}_maxbin2"; 
mv ${n}_maxbin2* ${n}_maxbin2; done
```
Run CheckM2 on the bins within the folder using the following loop. **Make sure you assigned a variable to the CheckM2 database, which was one of the very first steps in this tutorial!** First, activate the checkm2 environment (use your own, or alternatively, use the Checkm2_env in the groups folder /groups/kcooper/Checkm2_env)
```
conda deactivate
conda activate /groups/kcooper/Checkm2_env
```
Then, use the following loop to run checkm2 on the samples:
```
# single sample command (metabat)
checkm2 predict --threads 94 --input sample_contigs_metabat --output-directory sample_contigs_metabat_checkm2 -x .fa

# single-sample command (maxbin)
checkm2 predict --threads 94 --input sample_contigs_maxbin2 --output-directory sample_contigs_maxbin2_checkm2 -x .fa

# loop command (for both metabat and maxbin2)
for dir in ./*; do n="${dir}"; checkm2 predict --threads 94 --input "${n}" --output-directory "${n}_checkm2" -x .fa; done
```
Finally, move all checkm2 output folders into their own folder separate from the bins
```
cd ..
mkdir checkm2
mv binning/*_checkm2 checkm2
```

After CheckM2 is done, you have completed the tutorial. Email carolinescranton@arizona.edu with any questions or for information on how to continue analysis :)

**edit 10-2-25**
CONTINUING STEPS - Functional analysis with prokka

Functional analysis looks at the DNA which was sequenced and maps the sequences to specific proteins, by identifying the 3-base-long codons to form amino acid sequences, which then it matches to protein databases to determine the different proteins that the genome codes for. It tells you what proteins the bacteria can *possibly* make, but one thing to remember is that just because the gene is present, it doesn't mean that the organism is ACTUALLY producing it. 

The program prokka can be installed and used to assign taxonomy to assembled contigs or binned contigs (.fasta, .fa files). To install prokka use the following command (I activated my metagenomics environment first so I have prokka grouped with my binning software):
```
conda activate metagenomics
conda install -c conda-forge -c bioconda -c defaults prokka
```

Prokka can be run VERY simply, just by inputting a .fasta/.fa file. To do this, navigate to your spades directory (if using just assembled contigs) or your binning directory, specifically a folder containing binned .fa files (if using binned samples). If you need more specific parameters for your analysis, you can add different arguments. Check out their page for more info: https://github.com/tseemann/prokka

```
# simplest case (file name is binned-contigs.fa, could be just a contigs.fasta file too)
prokka binned-contigs.fa

# intermediate case (names output folder and files specifically, rather than just with today's date. change foldername and sampleID to what you want/specifics for your project) 
prokka --outdir foldername --prefix sampleID binned-contigs.fasta
```
There are more specific options that you can specify as well, like if you only want to identify genes from archea instea of bacteria, or if you have a reference genome, or how to subset the results for only proteins of interest. The output used for firther analysis is the .tsv file within the sample folder, but the other folders contain useful information as well (especially for looking at mutations). I am not an expert at this (and have never done it for any real samples), so please let me know if you are planning on using this and we can work together to figure out what the best steps are!


