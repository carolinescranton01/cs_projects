# Loops for Illumina metagenomic processing

### This tutorial follows a similar format to the Initial Illumina Shotgun Metagenomics Processing tutorial, but uses loops, or code which is able to ‘loop’ through multiple input files at the same time to run that particular analysis on multiple files at once. Using loops, you can write in one command and analyze all of the data in a folder, rather than going sample-by-sample. Loops take longer to run, but once you press enter it will continue to run until the process finishes or the HPC times out, so you do not need to watch the computer and can go do other things while it runs. 

Example samples in this project will be called Sample1, Sample2, etc. Samples are paired reads, so each will have two files (Sample1_R1 and Sample1_R2)


### Setup for this tutorial:
> 1.	Open the HPC for 6-12 hours with 24-94 cores (time and cores will depend on what steps you plan to run, they will be specified in each step) 
> 2.	Create conda environments and install all required software for this tutorial
>     a. Cleaning
>         i.Fastp
>        ii.Trim-galore
>    b.	Metagenomics
>        i.	Kraken2
>        ii. Metabat2
>        iii. Maxbin2 – this has weird documentation, email caroline (carolinescranton@arizona.edu) if you need help
>    c.	Assemblers
>        i.	Spades
>    d.	CheckM2 (alternatively, use the /groups/kcooper/Checkm2_env environment)
>        i. checkm2

# See links to github pages or other repositories for more information on installation. Most are installed using bioconda (so use this if possible) but others require different processes

3.	Set environmental variables – this only needs to be done once; it tells the commands where to look for specific databases
>nano ~/.bashrc
This will open the bashrc file for you to edit. Use the down arrow key to scroll all the way to the bottom. Add the following line to the bottom of the bashrc file:

export CHECKM2DB=/groups/kcooper/CheckM2_database/uniref100.KO.1.dmnd

Then, press control X, then y, and then enter and the window will close
4.	Move sequences into a folder called raw_reads as .fastq or .fastq.gz files, within a larger folder named according to the project name

Begin tutorial

1.	Initialize conda in your terminal
>module load anaconda
>source ~/.bashrc

2.	Activate Cleaning environment (where fastp and trim-galore are installed)
>conda activate Cleaning

3.	Fastp – filters samples 
a.	Move into the raw_reads folder where samples are housed
b.	COPY AND PASTE the following command (right-click to paste on HPC). Do not type this by hand, or the formatting will be messed up and it won’t work. The loop assumes samples are in .fastq format and names end in R1.fastq, so either change this or change sample names to fit these requirements. Command runs the input samples through the fastp software and generates outputs Sample_trimmed_R1.fastq and Sample_trimmed_R2.fastq for each sample. This may give some short errors 'cannot stat "sample__trimmed*" ' – ignore this error message

for f in *.fastq; do
    if [[ $f == *R1.fastq ]]; then
        n=${f%%R1.fastq}
        fastp --in1 ${f} --in2 ${n}R2.fastq --out1 ${n}trimmed_R1.fastq --out2 ${n}trimmed_R2.fastq -l 50 -g -h wgs.html > wgs.log
    elif [[ $f == *R2.fastq ]]; then
        n=${f%%R2.fastq}
        fastp --in1 ${n}R1.fastq --in2 ${f} --out1 ${n}trimmed_R1.fastq --out2 ${n}trimmed_R2.fastq -l 50 -g -h wgs.html > wgs.log
    fi;
done

4.	Go back a folder and make a new folder called ‘trimmed’ for the trimmed reads. Move the fastp-trimmed reads to trimmed. This will give a short error that says 'cannot stat *trimmed*' – ignore this, it still works.

>cd ..
>mkdir trimmed
>cd raw_reads
>mv *trimmed* ../trimmed

5.	Move into trimmed folder to run trim-galore on the fastp-trimmed reads. Trim-galore removes adaptors (short sequences of DNA used to organize samples when sequencing multiple samples at the same time, which next-generation sequencing like Illumina almost always does) 
a.	Copy and paste the following loop (again, don’t try to type it, the formatting will be messed up). This will run trim-galore on the samples and put outputs into a folder called trim-galore. The outputs from the two trimming steps are now going to be called ‘clean reads’ and will be moved into a folder to keep them separate for the rest of the analysis

for f in *.fastq; do
  if [[ $f == *R1.fastq ]]; then
    n=${f%%R1.fastq}
    trim_galore --paired ${f} ${n}R2.fastq -o trim-galore
  fi
done

6.	After running trim-galore we want to rename out outputs (names are getting too long). Follow the two loops to rename the R1 and then the R2 files with _clean at the end to denote that these are the clean reads. Note that the file extension changed to .fq after trim-galore, this is still a fastq file, so don’t worry about it. Copy and paste the two loops separately

Loop 1:

for f in *trimmed_R1_val_1.fq; do
    mv “$f” “${f//trimmed_R1_val_1/R1_clean}”
done

Loop 2:

for f in *trimmed_R2_val_2.fq; do
    mv “$f” “${f//trimmed_R2_val_2/R2_clean}”
done

7.	Copy (cp, not mv, in case we need to start over from this step) the double-trimmed and renamed reads to a new folder called clean_reads. 

>cd ../..
>mkdir clean_reads
>cp trimmed/trimmed_galore/*clean.fq clean_reads


8.	Deactivate cleaning environment, activate metagenomics environment for Kraken2 analysis, make a folder for kraken2, and copy clean_reads to merged

>conda deactivate
>conda activate metagenomics
>mkdir kraken2
>cp clean_reads/*.fq kraken2


9.	Merge samples for Kraken2 analysis – kraken2 only takes 1 input so R1 and R2 must be merged into a singular file using the cat command (concatenate). If you have only a few samples this can be done by hand, but you can also use this loop (copy and paste it, the > symbol is part of the code in this case!)

for f in *.fq; do if [[ $f == *R1_001.fq ]]; then n=${f%%R1_001.fq}; cat ${f} ${n}R2_001.fastq > ${n}merged.fq; fi; done

10.	Move merged reads to kraken2 folder
>mv *merged.fq ../kraken2

11.	Kraken2 loop – copy and paste the following loop. This will generate kraken2 report and output files which are used in other analysis (contact carolinescranton@arizona.edu if you need help with these other analyses! Instructions for them are not in this document)

for f in *.fq; do n=${f%%*.fq}; kraken2 --db /groups/kcooper/MY_KRAKEN2_DB --report ${n}_k2_report.txt --output ${n}_k2_output.txt ${n}.fq -t 94; done

12.	We will now go back to the non-merged reads for the rest of the analysis, which starts with assembly via metaSPADES. We need to make and move to a different folder and change conda environments:

>conda deactivate
>conda activate Assemblers 			# or whatever environment spades is in
>cd ..
>mkdir spades
>cp clean_reads/*.fq ../spades
>cd spades

13.	Run metaSPADES – this is very time intensive! If you are doing this on multiple samples, it will likely not finish all of them unless the samples are small or the HPC is open for a very long time (+100 hours). For context, a 2 GB paired sample took ~17 hours to run – loop can be used on small samples, if there are few samples, or if HPC is open for a while. Some parts of the loop need to be edited – the u## needs to be changed to the correct one in your path, and the Assemblers should be changed to match your conda environment name (which is probably assemblers or Assemblers). Copy and paste the following AFTER changing the highlighted sections

for f in *.fq; do
    if [[ $f == *R1_clean.fq ]]; then
        n=${f%%R1_clean.fq}
        ~/home/u##/netid/.conda/envs/Assemblers/bin/spades.py --meta -1 ${f} -2 ${n}R2_clean.fq -o ${n}_spades -t 94
    elif [[ $f == *R2_clean.fq ]]; then
        n=${f%%R2_clean.fq}
        ~/.conda/envs/Assemblers/bin/--meta -1 ${n}R1_clean.fq -2 ${f} -o ${n}_spades 
    fi
done

14.	Copy and rename contigs.fasta files for binning analysis. MetaSPADES takes the sequence data and makes it into contigs, which are longer stretches of DNA which are supposed to be in one sequence (ie. putting together 20 chunks of E. coli DNA into one singular long chunk of E. coli DNA in order). The output of SPADES is a folder with the sample name, and within the folder lots of other folders and files but the contigs.fasta file is the most important. However, for all samples, it will be called contigs.fasta, so we need to rename.

This is a lot more complicated of a process to automate, so rather than you typing it or doing it by hand, you will make and execute a python script (basically a simple program) which does it for you. Enter the following command to create the script:

>cd ..
>mkdir binning
>cd spades
>nano move_contigs.py

This will create a python script called move_contigs.py in your current folder (spades) and open the GNU nano editor. Now, look at the next page and copy and paste the entire segment of code (in this font) into the nano editor. 


















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





After that is copied in, press control X, Y, and then enter to save the script. When you run it, it will prompt you to put in the path to the spades and binning directories. These should be:

/xdisk/kcooper/netid/project-name/spades
/xdisk/kcooper/netid/project-name/binning

Where ‘netid’ and ‘project-name’ can be changed to match your information. 
To run the script, type the following:

>module load python
>python3 move_contigs.py

This should rename the contigs from each folder as foldername_contigs.fasta, and copy them into binning folder. The last thing we need to do is copy the merged reads over as a template for maxbin2. These should be in the kraken folder. Copy them over and move back to the binning folder.

>cd ../kraken
>cp *.fq ../binning
>cd ../binning


Now we should have specifically-named contig .fasta files for each sample as well as the clean .fq files for each sample (with matching names), and can continue with metabat and maxbin2 binning

15.	Metabat2 - in the binning folder, copy and paste this to run. It will make directories titled with the sample names (samplename_contigs)_metabat with the metabat outputs in them

for f in *.fasta; do n=${f%%.fasta}; metabat2 -i ${n}.fasta -o ${n}_metabat; mkdir ${n}_metabat2; mv ${n}*.fa ${n}_metabat2; done

16.	Maxbin2 – in the binning, copy and paste the following script after fixing the highlighted variables (u##, netid, and the environment, which is likely metagenomics) to run Maxbin2 on the samples, using the original clean reads as a template to predict abundance. 


for file in *.fasta; 
do n="${file%%_contigs.fasta}"; /home/u##/netid/.conda/envs/Metagenomics/bin/run_MaxBin.pl -contig "$file" -reads "${n}.fastq" -max_iteration 5 -out "${n}_maxbin2"; 
mkdir "${n}_maxbin2"; 
mv "${n}_maxbin2*" ${n}; done


17.	Run CheckM2 on the bins within the folder using the following loop. Make sure you assigned a variable to the CheckM2 database, which was one of the very first steps in this tutorial!

for dir in ./; do 
Checkm2 predict --threads 94 --input $dir --output $dir_checkm;
done




















