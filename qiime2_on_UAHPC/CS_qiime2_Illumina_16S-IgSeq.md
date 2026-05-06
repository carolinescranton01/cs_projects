# CS qiime2 processing of IgG and IgA-seq reads, sequenced with Illumina Miseq/Nextseq (Demultiplexed paired reads (A) + multiplexed reads (B))

**Set up commands**
Download qiime2 apptainer (note - be sure to use UA HPC ocelote cluster)
Use the following directory structure:
/xdisk/PI-netID/your-netID/ILLUMINA_16S/data/[download_to_this_folder]
```
# download the container
apptainer pull docker://quay.io/qiime2/amplicon:2024.10
```

Any qiime2 command will now have to be prefaced with the apptainer exec -B flag, so all commands will start with this:
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif

Build the SILVA 515-926R custom classifier (this matches our primer region better and gets better/more accurate classification. These commands may take a while to run (several hours)
```
# Download databases
wget https://data.qiime2.org/2024.2/common/silva-138-99-seqs.qza
wget https://data.qiime2.org/2024.2/common/silva-138-99-tax.qza

# Extract sequences for 515F-926R
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime feature-classifier extract-reads --i-sequences silva-138-99-seqs.qza --p-f-primer GTGCCAGCMGCCGCGGTAA --p-r-primer CCGYCAATTYMTTTRAGTTT --p-trunc-len 0 --o-reads ref-seqs-515-926.qza

# Build classifier
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime feature-classifier fit-classifier-naive-bayes --i-reference-reads ref-seqs-515-926.qza --i-reference-taxonomy silva-138-99-tax.qza --o-classifier silva-138-515-926-classifier.qza
```

**PATH A. DEMULTIPLEXED PAIRED .FASTQ.GZ FILES**

Step 2a. Create sample manifest (.tsv)
Use the following directory structure: /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/[upload_manifest_here]
The manifest links the sampleIDs to their absolute file path. It should be in a tab-deliminated text file (tsv). It has the following header columns
sampleID    forward-absolute-filepath    reverse-absolute-filepath

A snippet of a properly-formatted sample manifest is below:

sample-id	forward-absolute-filepath	reverse-absolute-filepath
Scranton-9435934_0003_n_IgAseq_S53	/data/fastq/Scranton-9435934_0003_n_IgAseq_S53_R1_001.fastq.gz	/data/fastq/Scranton-9435934_0003_n_IgAseq_S53_R2_001.fastq.gz
Scranton-9435934_0003_p_IgAseq_S5	/data/fastq/Scranton-9435934_0003_p_IgAseq_S5_R1_001.fastq.gz	/data/fastq/Scranton-9435934_0003_p_IgAseq_S5_R2_001.fastq.gz
Scranton-9435934_0004_n_IgAseq_S54	/data/fastq/Scranton-9435934_0004_n_IgAseq_S54_R1_001.fastq.gz	/data/fastq/Scranton-9435934_0004_n_IgAseq_S54_R2_001.fastq.gz
Scranton-9435934_0004_p_IgAseq_S6	/data/fastq/Scranton-9435934_0004_p_IgAseq_S6_R1_001.fastq.gz	/data/fastq/Scranton-9435934_0004_p_IgAseq_S6_R2_001.fastq.gz

Note - the file paths can start at the data folder

Step 3a. Upload fastq.gz files to HPC with the following directory structure:
/xdisk/PI-netID/your-netID/ILLUMINA_16S/data/fastq/[upload gzipped fastq here]

Step 4a. Run the qiime2 import command
```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools import --type SampleData[PairedEndSequencesWithQuality] --input-path /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/manifest_clean.tsv --output-path /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/demux.qza --input-format PairedEndFastqManifestPhred33V2
```

Step 5a. Visualize to determine trim lengths
```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime demux summarize --i-data demux.qza --o-visualization demux.qzv
```
Open the demux.qzv file in qiime2view (https://view.qiime2.org/) to determine where in the forward/reverse read the quality drops (where does it average below 30 on both plots). These values will be used in the trim command

Step 6a. Trim the reads
Replace the values after --p-trunc-len-f and --p-trun-len-r with the values for forward (f) and reverse (r) from step 5
```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime dada2 denoise-paired --i-demultiplexed-seqs demux.qza --p-trim-left-f 0 --p-trim-left-r 0 --p-trunc-len-f 270 --p-trunc-len-r 235 --o-table table.qza --o-representative-sequences rep-seqs.qza --o-denoising-stats dada2-stats.qza --p-n-threads 16
```
