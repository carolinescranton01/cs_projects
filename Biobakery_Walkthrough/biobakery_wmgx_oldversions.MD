# Biobakery walkthrough (whole-genome sequence data, humann v3.9 and metaphlan v 3.0)

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
Link to github: https://github.com/biobakery/MetaPhlAn/wiki/MetaPhlAn-4

MetaPHlAn assigns taxonomy to the samples by identifying specific genes within the samples which match to known taxa. To run metaphlan, use the following commands:
```
cd ..
mkdir metaphlan

# for single-end reads
for f in clean_reads/*.fastq; do base=$(basename "$f" .fastq); metaphlan "$f" --db_dir $METAPHLAN_DB --mapout "${base}.bowtie2.bz2" --nproc 5 --input_type fastq -o "${base}_profiled.tsv"; done

# for paired-end reads
for f1 in clean_reads/*_1.fastq; do
  base=$(basename "$f1" _1.fastq)
  f2="clean_reads/${base}_2.fastq"
  if [ -f "$f2" ]; then
    metaphlan "${f1},${f2}" --db_dir $METAPHLAN_DB --mapout "${base}.bowtie2.bz2" --nproc 8 --input_type fastq -o "${base}_profiled.tsv" -t rel_ab_w_read_stats
  else
    echo "Warning: Paired file for $f1 not found. Skipping."
  fi
done
```
This command should output 2 files per sample into the main directory (whether they were paired-end or not) - one ending in .bz2, which contains information on how the reads were aligned, and one ending in .tsv, which contains the alignment information in a readable format (tab deliminated).

Finally, for future analysis, we want to merge our outputs into one large table using a pre-installed script.
NOTE - 6/17/25 - some issue w the .tsv files and merge script. it does not work due to formatting or metaphlan version (working on it!)
```
mkdir metaphlan
mv *.tsv metaphlan
mv *.bz2 metaphlan
cd metaphlan
merge_metaphlan_tables.py *.tsv > merged_abundance_table.tsv
```

### Step 3 - assigning functions to genes usin HUMAnN
Link to github: https://github.com/biobakery/humann

HUMAnN looks at the nucleotide sequences and translates them into potential proteins to identfy the functional capabilities of the bacteria within the sample. It uses 2 databases (chocophlan for a nucleotide search and uniref90 for a translated search). Either of the searches can be bypassed to save time, but running both generates a bettter picture of the capabilities of the microbes in the sample. Humann does not work as well on paired-end reads, so for paired-end reads we will concatonate (join) the forward R1 and reverse R2 fastq files.

NOTE - as of 6/17/25, only the chocophlan DB is installed (not enough space on drive for uniref90, will download when necessary). Humann must be run with --bypass-translated-search flag in order to work. 

First we will copy and concatenate the reads in a new folder:

```
cd ..
mkdir humann
cp clean_reads/*.fastq humann
cd humann
for f in *.fastq; do if [[ $f == *_1.fastq ]]; then n=${f%%_1.fastq}; cat ${f} ${n}_2.fastq > ${n}_merged.fastq; fi; done
rm *_1.fastq
rm *_2.fastq
```

Now we should only have the merged read samples (samplename_merged.fastq). To run Humann on them use the following:

```
for f in *.fastq; do
  base=${f%.fastq}       
  base=${base%_merged}  
  tsv="../metaphlan/${base}_profiled.tsv"
  humann --input "$f" --output humann_out --taxonomic-profile "$tsv" --bypass-translated-search
done
```


NOTE 6-17-25 humann not running - trying to run metaphlan with --bowtie2out flag which is depreciated (need to fix versions)
NOTE 6-18-25 - got humann to run metaphlan simultaneously, BUT uses old versions (humann 3.9 and metaphlan 3.0 with mpa_v31_CHOCOPhlAn_201901.tar database) --> dont need to run metaphlan step at this point if just redoing it w humann. 


