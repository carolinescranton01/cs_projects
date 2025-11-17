# Long Reads analysis (oxford nanopore) 
**IN PROGRESS 11/12/15**

This tutorial walks through how to analyze long-read metagenomic data on the HPC. Basecalled data is uploaded into a project/raw_reads folder (project = your project name) as unzipped fastq files. Data is then filtered (trimmed) using filtlong based on read length and quality. Human (host) contamination is removed with minimap2 and a reference genome. Taxonomy is assigned via kraken2. Genomes are assembled with Flye, and binned into draft metagenomic-assembled genomes with metabat2, concoct, and maxbin2. Bins are checked with CheckM2. Functional analysis is conducted with prokka, and figures/stats are created in R using .biom files from kraken2/kraken-biom.

## Step 1: create a new environment and install packages

Create a new conda environment (I called it longreads) and install the following packages. Some (kraken2, kraken-biom, metabat2, maxbin2, concoct, checkm2, prokka) are used in the short reads pipeline (illumina WGS analysis) and may already be installed in other environments. I reccomend to only install the new packages in the longreads env, and you can switch environments (conda deactivate, conda activate XYZ) to use the already installed packages. This helps to avoid errors from packages which are installed multiple times.

```
# create new env
conda create -n longreads -c bioconda

# activate env
conda activate longreads

# install new packages
conda install -c bioconda filtlong
conda install -c bioconda minimap2
conda install -c bioconda samtools

```

## Step 2: Filter low-quality reads using filtlong

Filtlong (https://github.com/rrwick/Filtlong) filters long reads and reads with low quality. The code below filters reads which are shorter than 1000 base pairs (long reads should be 10-100 kb in length) and keeps the top 90% of reads with the best quality. The input is input.fastq. The last part of the command ( > output.fastq) outputs into a new file called output.fastq. Below is the single-sample command, and the loop command.

```
# if not already activated:
conda activate longreads
cd raw_reads

# single-sample
filtlong --min_length 1kb --keep_percent 90 input.fastq > output.fastq

# loop
for file in *.fastq
do
    base=$(basename "$file" .fastq)
    filtlong --min_length 1000 --keep_percent 90 "$file" > "${base}_filt.fastq"
done

# move the filtered reads into a new folder called filtered
cd ..
mkdir filtered
mv raw_reads/*filt.fastq filtered
cd filtered
```
If your dataset is large you can include the -t flag (target bases) which will set an upper limit - the recommended is 500 mb (500 million bases per read)

## Step 3: remove human (or host) DNA
When we sequence from an organism (ie. sequence the gut microbiome of a human), we often get a good deal of host contaminant (human DNA, or the DNA of any other host). Sequencing does not discriminate between prokaryotic and eukaryotic DNA so we have to remove that after we have already sequenced our sample. For that we will use minimap2 and a host genome, in this case a human genome. This code is for oxford nanopore reads - if you have pacbio reads the -ax flag will need ot be altered. For more info and documentation on minimap2, see their github page: https://github.com/lh3/minimap2 

The first time you use this, you will need to download a host genome and index it (into the filtered folder with our filtered samples). This is an example with the human genome:

```
# wget goes to the link and downloads the data from NCBI
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.28_GRCh38.p13/GCA_000001405.28_GRCh38.p13_genomic.fna.gz

# gunzip unzips it
gunzip GCA_000001405.28_GRCh38.p13_genomic.fna.gz

# mv renames it to a shorter name
mv GCA_000001405.28_GRCh38.p13_genomic.fna GRCh38.fa

# this minimap command indexes it so that when you use this genome later, it runs faster
minimap2 -d GRCh38.mmi GRCh38.fa
```

Now we have our indexed reference genome, so we can filter our reads against it:

```
# single-sample command:
inimap2 -ax map-ont "$HOST_INDEX" "$file" | samtools view -b -f 4 > "${base}_nonhost.bam"

# loop:
# set host genome - change to match your file name if you did not use the human genome
HOST_INDEX="GRCh38.mmi"

# run the command on the filtered samples
for file in *_filt.fastq; do
    base="${file%.fastq}"
    minimap2 -ax map-ont "$HOST_INDEX" "$file" | samtools view -b -f 4 > "${base}_nonhost.bam"
    # convert BAM to FASTQ for non-host reads only
    samtools fastq "${base}_nonhost.bam" > "${base/_filt/_clean}.fastq"
    # remove intermediate BAM file
    rm "${base}_nonhost.bam"
done
```
**Note:** minimap2 can be used to map your reads to any genome - while we are using it to pull out host reads, if you had an organism of interest you could use minimap to pull reads from that organism out of your sample. 

**Note:** the human genome is large (the raw file and indexed file together are 10GB). These can be deleted when you are done and redownloaded/indexed at a later time to save space.

Now we have our reads which are filtered for quality and host reads are removed, we can copy them to a new folder:

```
cd ..
mkdir clean
mv filtered/*clean.fastq clean
cd clean
```

## Step 4: assign taxonomy with kraken2

If kraken2 is already installed in the metagenomics environment, activate it. If not, install kraken2 and kraken-biom with the following commands:
```
# deactivate longreads 
conda deactivate

# create and activate a new environment (metagenomics)
conda create -n metagenomics -c bioconda
conda acivate metagenomics

# install packages
conda install kraken2 -c bioconda
conda install kraken-biom -c bioconda
```

Kraken2 assigns taxonomy to the reads based on 35 bp kmers, or segments of DNA which are 35 bases long, which are mapped to a specified database. We will use the database in the groups folder (/groups/kcooper/MY_KRAKEN2_DB) but you can download and build custom databases if needed. Run this command from inside the clean folder, which contains our cleaned up reads. Make sure to have a metadata file ready if you are wanting to run kraken-biom. Here is the github page for kraken2: https://github.com/DerrickWood/kraken2/wiki/Manual

```
# single sample:
kraken2 --db /groups/kcooper/MY_KRAKEN2_DB/ --report sample_report.txt --output sample_output.txt sample_merged.fastq -t 94

# loop:
for f in *.fastq; do n=${f%%.fastq}; kraken2 --db /groups/kcooper/MY_KRAKEN2_DB/ --report "${n}_report.txt" --output "${n}_output.txt" ${n}.fastq -t 94; done
```

To generate a .biom file for analysis in R, use the following command, where each sample is listed out in the command, metadata.tsv is your metadata file, and output.biom is the biom file output for analysis in R

```
kraken-biom sample1_report.txt sample2_report.txt sample3_report.txt -m metadata.tsv -o output.biom
```

Finally, to clean things up, we will move all kraken outputs and files into an external folder

```
cd ..
mkdir kraken
mv clean/*report.txt kraken
mv clean/*output.txt kraken
mv clean/*.tsv kraken
mv clean/*.biom kraken
```
## Step 5: Assemble the genomes with Flye (better for metagenomic samples - use Canu for single isolates)

We will now assemble metagenome-assembled genomes from our clean reads. First, we will copy the clean reads into a new folder, and then activate the assemblers environment (if you have this created and installed - if not see the last few lines of code in the following chunk). Here is the flye manual: https://github.com/mikolmogorov/Flye/blob/flye/docs/USAGE.md

```
# copy the reads to a new folder
mkdir assembly
cp clean/*clean.fastq assembly
cd assembly

# change conda environments (if you have flye instealled in the assemblers environment)
conda deactivate
conda activate assemblers

# if you do not have assemblers environment created and flye installed, you can install it into the longreads environment
conda deactivate
conda activate longreads
conda install -c bioconda flye
```

Flye will assemble the genomes - **this may take a very long time**. It is recomemeded to open the HPC for 24+ hours when doing assembly, especially in loops.
**11-12-25 IN PROGRESS**
```
# single sample:
flye --nano-raw sample_clean.fastq --out-dir flye_metagenome_out --meta --threads 16

# loop:
```
