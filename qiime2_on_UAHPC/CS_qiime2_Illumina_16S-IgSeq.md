# CS qiime2 processing of IgG and IgA-seq reads, sequenced with Illumina Miseq/Nextseq (Demultiplexed paired reads (A) + multiplexed reads (B))

**Set up commands**

**Download qiime2 apptainer**
(note - be sure to use UA HPC ocelote cluster)
Use the following directory structure:
/xdisk/PI-netID/your-netID/ILLUMINA_16S/data/[download_to_this_folder]

```
# download the container
apptainer pull docker://quay.io/qiime2/amplicon:2024.10
```

Any qiime2 command will now have to be prefaced with the apptainer exec -B flag, so all commands will start with this:
**apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif**

**Build the SILVA 515-926R custom classifier** (this matches our primer region better and gets better/more accurate classification. These commands may take a while to run (several hours)

```
# Download databases
wget https://data.qiime2.org/2024.2/common/silva-138-99-seqs.qza
wget https://data.qiime2.org/2024.2/common/silva-138-99-tax.qza

# Extract sequences for 515F-926R
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime feature-classifier extract-reads \
 --i-sequences silva-138-99-seqs.qza \
 --p-f-primer GTGCCAGCMGCCGCGGTAA \
 --p-r-primer CCGYCAATTYMTTTRAGTTT \
 --p-trunc-len 0 \
 --o-reads ref-seqs-515-926.qza

# Build classifier
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime feature-classifier fit-classifier-naive-bayes \
 --i-reference-reads ref-seqs-515-926.qza \
 --i-reference-taxonomy silva-138-99-tax.qza \
 --o-classifier silva-138-515-926-classifier.qza
```

**PATH A. DEMULTIPLEXED PAIRED .FASTQ.GZ FILES**

**Step 2a. Create sample manifest (.tsv)**

Use the following directory structure: /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/[upload_manifest_here]
The manifest links the sampleIDs to their absolute file path. It should be in a tab-deliminated text file (tsv). It has the following header columns
sampleID    forward-absolute-filepath    reverse-absolute-filepath

A snippet of a example sample manifest is below. Note that there should only be a SINGLE tab between each line
<img width="1229" height="116" alt="Screenshot 2026-05-06 at 1 25 03 PM" src="https://github.com/user-attachments/assets/1097eb92-8b5e-41b3-af72-0128ec7ef688" />

Note - the file paths can start at the data folder

**Step 3a. Upload fastq.gz files to HPC**

Use the following directory structure:
/xdisk/PI-netID/your-netID/ILLUMINA_16S/data/fastq/[upload gzipped fastq here]

**Step 4a. Run the qiime2 import command**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools import \
 --type SampleData[PairedEndSequencesWithQuality] \
 --input-path /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/manifest.tsv \
 --output-path /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/demux.qza \
 --input-format PairedEndFastqManifestPhred33V2
```

**Step 5a. Visualize to determine trim lengths**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime demux summarize \
 --i-data demux.qza \
 --o-visualization demux.qzv
```

Open the demux.qzv file in qiime2view (https://view.qiime2.org/) to determine where in the forward/reverse read the quality drops (where does it average below 30 on both plots). These values will be used in the trim command

**Step 6a. Trim the reads**

Replace the values after --p-trunc-len-f and --p-trun-len-r with the values for forward (f) and reverse (r) from step 5

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime dada2 denoise-paired \
 --i-demultiplexed-seqs demux.qza \
 --p-trim-left-f 0 \
 --p-trim-left-r 0 \
 --p-trunc-len-f 270 \
 --p-trunc-len-r 235 \
 --o-table table.qza \
 --o-representative-sequences rep-seqs.qza \
 --o-denoising-stats dada2-stats.qza \
 --p-n-threads 16
```

**Step 7a. Classify with custom 515F-926R classifier**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime feature-classifier classify-sklearn \
 --i-classifier silva-138-515-926-classifier.qza \
 --i-reads rep-seqs.qza \
 --o-classification taxonomy.qza
```

**Step 8a. Export feature table**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools export \
  --input-path table.qza \
  --output-path exported-table
```

**Step 9a. Convert to biom format**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif biom convert \
  -i exported-table/feature-table.biom \
  -o feature-table.tsv \
  --to-tsv
```

**Step 10a. export taxonomy**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools export \
  --input-path taxonomy.qza \
  --output-path exported-taxonomy
```

**Step 11a. Convert taxonomy to long format for analysis in excel**
This will create a TSV file containing the whole taxonomic string for each feature identified in each sample, with the abundance. So for example, if ten species were found in sample 1, rows 2-11 of the tsv would be sample1 and each row would contain the entire string for each unique species with the abundance as the last column.

Use the python script linked here to do this:
longformat.py 
https://github.com/carolinescranton01/cs_projects/blob/main/qiime2_on_UAHPC/longformat.py

**Step 12a. split taxonomic ranks into individual columns**

```
python -c "import pandas as pd; df=pd.read_csv('long_feature_table.tsv', sep='\t'); t=df['taxonomy'].str.split(';', expand=True).apply(lambda x: x.str.strip() if x is not None else x); t=t.reindex(columns=range(7)); t.columns=['kingdom','phylum','class','order','family','genus','species']; df=df.join(t); df.to_csv('long_feature_table_ranks.tsv', sep='\t', index=False)"
```

Now you can download the long_feature_table_ranks.tsv and use that for further IgG/IgA seq analysis, detailed elsewhere


