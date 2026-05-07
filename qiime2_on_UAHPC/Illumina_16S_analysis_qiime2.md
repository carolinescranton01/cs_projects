# qiime2 processing of Illumina 16S reads for Taxonomy

This tutorial describes how to analyze Illumina 16S data on the HPC. It only details commands though taxonomic assignment and then continues with instrutctions on how to export the data as a long-format table where column corresponds to a feature. Qiime2 can be used for more than just taxonomic assignment - see the links at the bottom of each section for further analysis (creating figures, looking at alpha and beta diversity, and performing statistics)

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


## PATH A. DEMULTIPLEXED PAIRED .FASTQ.GZ FILES
### Qiime2 format - PairedEndFastqManifestPhred33V2

**Step 1a. Create sample manifest (.tsv)**

Use the following directory structure: /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/[upload_manifest_here]
The manifest links the sampleIDs to their absolute file path. It should be in a tab-deliminated text file (tsv). It has the following header columns
sampleID    forward-absolute-filepath    reverse-absolute-filepath

A snippet of a example sample manifest is below. Note that there should only be a SINGLE tab between each line
<img width="1229" height="116" alt="Screenshot 2026-05-06 at 1 25 03 PM" src="https://github.com/user-attachments/assets/1097eb92-8b5e-41b3-af72-0128ec7ef688" />

Note - the file paths can start at the data folder

**Step 2a. Upload fastq.gz files to HPC**

Use the following directory structure:
/xdisk/PI-netID/your-netID/ILLUMINA_16S/data/fastq/[upload gzipped fastq here]

**Step 3a. Run the qiime2 import command**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools import \
 --type SampleData[PairedEndSequencesWithQuality] \
 --input-path /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/manifest.tsv \
 --output-path /xdisk/PI-netID/your-netID/ILLUMINA_16S/data/demux.qza \
 --input-format PairedEndFastqManifestPhred33V2
```

**Step 4a. Visualize to determine trim lengths**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime demux summarize \
 --i-data demux.qza \
 --o-visualization demux.qzv
```

Open the demux.qzv file in qiime2view (https://view.qiime2.org/) to determine where in the forward/reverse read the quality drops (where does it average below 30 on both plots). These values will be used in the trim command

**Step 5a. Trim the reads**

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

**Step 6a. Classify with custom 515F-926R classifier**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime feature-classifier classify-sklearn \
 --i-classifier silva-138-515-926-classifier.qza \
 --i-reads rep-seqs.qza \
 --o-classification taxonomy.qza
```

**Step 7a. Export feature table**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools export \
  --input-path table.qza \
  --output-path exported-table
```

**Step 8a. Convert to biom format**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif biom convert \
  -i exported-table/feature-table.biom \
  -o feature-table.tsv \
  --to-tsv
```

**Step 9a. export taxonomy**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools export \
  --input-path taxonomy.qza \
  --output-path exported-taxonomy
```

**Step 10a. Convert taxonomy to long format for analysis in excel**
This will create a TSV file containing the whole taxonomic string for each feature identified in each sample, with the abundance. So for example, if ten species were found in sample 1, rows 2-11 of the tsv would be sample1 and each row would contain the entire string for each unique species with the abundance as the last column.

Use the python script linked here to do this:
longformat.py 
https://github.com/carolinescranton01/cs_projects/blob/main/qiime2_on_UAHPC/longformat.py

**Step 11a. split taxonomic ranks into individual columns**

```
python -c "import pandas as pd; df=pd.read_csv('long_feature_table.tsv', sep='\t'); t=df['taxonomy'].str.split(';', expand=True).apply(lambda x: x.str.strip() if x is not None else x); t=t.reindex(columns=range(7)); t.columns=['kingdom','phylum','class','order','family','genus','species']; df=df.join(t); df.to_csv('long_feature_table_ranks.tsv', sep='\t', index=False)"
```

Now you can download the long_feature_table_ranks.tsv and use that for further IgG/IgA seq analysis, detailed elsewhere

**Tutorials for further analysis can be found on the qiime webpage. There is not a full tutorial for PairedEndFastqManifestPhred33V2 data, but you can find each of the steps on the tutorials page**
https://docs.qiime2.org/2024.10/tutorials/

## PATH B: multiplexed fastq files (Illumina)
### Qiime2 format - EMPPairedEndSequences

Make sure the set up commands (Download the qiime2 apptainer and build SILVA 515F-926R classifier) from the beginning of this page are run!

**Step 1b. Upload data**

Upload your forward.fastq.gz, reverse.fastq.gz, and barcodes.fastq.gz files into a folder called 'fastq' with this directory structure:
/xdisk/PI-netID/your-netID/ILLUMINA_16S/data/fastq/[upload here]

This folder, containing the multiplexed data, should be within the folder containing the amplicon.sif file

**Step 2b. create and upload metadata**

Create a .tsv file with the sampleIDs and Golay barcodes from library prep (https://earthmicrobiome.org/wp-content/uploads/2022/06/EMP_16S_V4V5_515F_926R_Parada_Quince.xlsx)

The first column should be the sampleIDs, which is what the samples will be called after demultiplexing. The second column will be the corresponding barcode. Upload this .tsv file into the data directory.

**Step 3b. Import the data into qiime**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime tools import \
   --type EMPPairedEndSequences \
   --input-path fastq \
   --output-path emp-paired-end-sequences.qza
```

**Step 4b. Demultiplex the sequences**

```
apptainer exec -B /xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime demux emp-paired \
  --m-barcodes-file meta.tsv \
  --m-barcodes-column barcodes \
  --p-rev-comp-mapping-barcodes \
  --i-seqs emp-paired-end-sequences.qza \
  --o-per-sample-sequences demux-full.qza \
  --o-error-correction-details demux-details.qza
```

**Step 5b. Visualize the sequences using qiime2view**

This step helps you decide where to trim the sequences in the following step. Upload the demuz.qzv to view.qiime2.org. Go to the interactive quality plot tab. Determine the highest base possible where the average quality (middle of black bars) is 30 (*Note - there is some variance, meaning some samples may be less than 30 quality or greater than 30 after that base. Choose a base that shows the overall trend in the data is now at 30 and dropping at higher bases*). Use these two numbers in the following step in the --p-trunc-len-f and --p-trun-len-r arguments.

**Step 6b. Trim the sequences**

```
apptainer exec -B xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime dada2 denoise-paired \
  --i-demultiplexed-seqs demux-full.qza \
  --p-trim-left-f 0 \
  --p-trim-left-r 0 \
  --p-trunc-len-f #YOUR NUMBER HERE (forward) \
  --p-trunc-len-r #YOUR NUMBER HERE (reverese) \
  --o-table table.qza \
  --o-representative-sequences rep-seqs.qza \
  --o-denoising-stats denoising-stats.qza
```
**Step 7b. Classify the sequences**

First, ensure the silva-138-515-926-classifier.qza is in the data folder.

```
apptainer exec -B xdisk/PI-netID/your-netID/ILLUMINA_16S/data:/data amplicon_2024.10.sif qiime feature-classifier classify-sklearn \
 --i-classifier silva-138-515-926-classifier.qza \
 --i-reads rep-seqs.qza \
 --o-classification taxonomy.qza
```

**Steps 8b-12b are the same as steps 7-10a --> export feature table, convert biom to tsv, export the taxonomy, reformat**

Follow those steps and be sure to make sure file paths/names match


**Further analysis instructions for EMPPairedEndSequences can be found in the Atacama soils tutorial**
https://docs.qiime2.org/2024.10/tutorials/atacama-soils/

