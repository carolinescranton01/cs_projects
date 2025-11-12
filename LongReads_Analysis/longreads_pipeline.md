# Long Reads analysis (oxford nanopore) 
**IN PROGRESS 11/12/15**

This tutorial walks through how to analyze long-read metagenomic data on the HPC. Basecalled data is uploaded into a project/raw_reads folder (project = your project name) as unzipped fastq files. Data is then filtered (trimmed) using filtlong based on read length and quality. Human (host) contamination is removed with minimap2 and a reference genome. Taxonomy is assigned via kraken2. Genomes are assembled with Flye, and binned into draft metagenomic-assembled genomes with metabat2, concoct, and maxbin2. Bins are checked with CheckM2. Functional analysis is conducted with prokka, and figures/stats are created in R using .biom files from kraken2/kraken-biom.

## Step 1: create a new environment and install packages

Create a new conda environment (I called it longreads) and install the following packages. Some (kraken2, kraken-biom, metabat2, maxbin2, concoct, checkm2, prokka) are used in the short reads pipeline (illumina WGS analysis) and may already be installed in other environments. I reccomend to only install the new packages in the longreads env, and you can switch environments (conda deactivate, conda activate XYZ) to use the already installed packages. This helps to avoid errors from packages which are installed multiple times.

```
# create new env
conda create -n longreads -c bioconda

# install new packages
conda install -c bioconda filtlong
conda install -c bioconda minimap2
conda install -c bioconda samtools

```

## Step 2: Filter low-quality reads using filtlong

Filtlong (https://github.com/rrwick/Filtlong) filters short reads and reads with low quality. The code below filters reads which are shorter than 1000 base pairs (long reads should be 10-100 kb in length) and keeps the top 90% of reads with the best quality. The input is input.fastq. The last part of the command ( > output.fastq) outputs into a new file called output.fastq. Below is the single-sample command, and the loop command.

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
When we sequence from an organism (ie. sequence the gut microbiome of a human), we often get a good deal of host contaminant (human DNA, or the DNA of any other host). Sequencing does not discriminate between prokaryotic and eukaryotic DNA so we have to remove that after we have already sequenced our sample. For that we will use minimap2 and a host genome, in this case a human genome.

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

```
Note: minimap2 can be used to map your reads to any genome - while we are using it to pull out host reads, if you had an organism of interest you could use minimap to pull reads from that organism out of your sample. 
