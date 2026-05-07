# qiime2 processing of ONT 16S reads for Taxonomy

This tutorial details how to analyze 16s rRNA long reads using qiime, in the SingleEndFastqManifestPhred33V2 format. This tutorial begins with the reads after sequencing and basecalling has finished.

**NOTE: qiime2 only works on the OCELOTE cluster of the UA HPC so make sure to open that rather than Puma!**

## Part 1. Setup

### Data upload

ONT data is formatted as many .fastq.gz files within a folder corresponding to the barcode (so 24 folders (+1 unclassified folder) per sequencing run with SQK16S114.24). The first step is to upload all 24 barcode folders to the HPC. If you have multiple sequence runs to work with, I would reccomend renaming the folders before uploading them to the sampleIDs (for example, if barcode01 = gut_sample1_1-1-2026_run1, rename the folder from barcode-1 to gut_sample1_1-1-2026_run1. You will need all of the folders to have unique names for this to work! 
Format your directory structure as follows, and upload the (renamed) barcode folders to the 16S_ONT folder:

/xdisk/PI-netID/yournetID/16S_ONT/[upload your barcode folders here]

Navigate to the 16S_ONT folder. Run the following loop to concatenate the fastq.gz files within the individual folders and copy them out into the main directory

```
for dir in */; do
    dirname=$(basename "$dir")
    
    if ls "$dir"/*.fastq.gz 1> /dev/null 2>&1; then
        echo "Processing $dirname"
        
        cat "$dir"/*.fastq.gz > "${dirname}.fastq.gz"
    fi
done
```

Now you should have your concantenated and renamed .fastq.gz files for each folder, and the folders in the 16S_ONT folder. Create a new folder called data, navigate to it, and make another folder called fastq within the data folder

```
mkdir data
cd data
mkdir fastq
cd ../..
```

Now, move all of the concatenated files into the fastq folder, and go to the data folder

```
mv *.fastq.gz data/fastq
cd data
```

### Download qiime2 apptainer

Within the data folder, download the qiime2 apptainer

```
apptainer pull docker://quay.io/qiime2/amplicon:2024.10
```

### Make manifest file 

qiime2 needs a manifest file to 'find' the samples. This file is a tab-deliminated file (tsv) with two columns: sampleid, absolute-filepath

To get an easy-to-copy list of all the file names, run the following command:

```
ls > filenames.txt
```

This will make a text file with all of the filenames. Open it in the HPC file system and copy the list into an excel file. In column A1 type *sampleid*, and paste the list of filenames in A2. Make sure that each name fills a new cell (so you have the same number of columns as you do samples + 1 for sampleid header). In cell C1 write *absolute-filepath*. In cell B2, write */data/fastq/* and drag that down to the end of sample names. In cell C2, use the excel formula *=A2&B2* and drag down to the end of the list. Column C should now be filled with */data/fastq/samplename1, /data/fastq/samplename2, /data/fastq/samplename3*, etc (with your sample names). Copy the contents of column C and right click on B1, click Paste Special > Values. This should paste the contents of column C into B. Then you can delete column C and save the excel file as a tab-deliminated text file (.txt) with the name *manifest.txt*. 

Upload the manifest.txt file to the HPC, in the /xdisk/PI-netID/yournetID/16S_ONT/data folder

## Part 2. Analysis

Now that you have your fastq.gz files renamed, concatenated, and uploaded in the fastq folder, and your sample manifest in the data folder, AND the qiime2 apptainer downloaded, you can begin analysis. Make sure you are in the data folder (/xdisk/PI-netID/yournetID/16S_ONT/data)

**Step 1. Import data into qiime2**

```
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif qiime tools import \
  --type 'SampleData[SequencesWithQuality]' \
  --input-path manifest.tsv \
  --output-path demux.qza \
  --input-format SingleEndFastqManifestPhred33V2
```

**Step 2. Filter the data**

```
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif qiime quality-filter q-score \
  --i-demux demux.qza \
  --o-filtered-sequences demux-filtered.qza \
  --o-filter-stats filter-stats.qza
```

**Step 3. Generate the table and dereplicated sequence items**

```
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif qiime vsearch dereplicate-sequences \
  --i-sequences demux-filtered.qza \
  --o-dereplicated-table table.qza \
  --o-dereplicated-sequences rep-seqs.qza
```

**Step 4. Cluster the table using vsearch**

```
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif qiime vsearch cluster-features-de-novo \
  --i-sequences rep-seqs.qza \
  --i-table table.qza \
  --p-perc-identity 0.97 \
  --o-clustered-table vsearch-table.qza \
  --o-clustered-sequences vsearch-rep-seqs.qza
  ```

**Step 5. Classify the data with the full SILVA database**

```
# dowload database
wget https://data.qiime2.org/classifiers/sklearn-1.4.2/silva/silva-138-99-nb-classifier.qza

# classify
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif qiime feature-classifier classify-sklearn \
  --i-classifier silva-138-99-nb-classifier.qza \
  --i-reads vsearch-rep-seqs.qza \
  --o-classification taxonomy.qza
```

**Steps 6 through 10 are for exporting the taxonomic table in long format, where each row is a feature and every feature is listed with the sampleID it came from (ie if you had 3 samples, each with ten unique species, there would be thirty rows in the taxonomy.tsv**

**Step 6. Export to feature table**

```
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif qiime tools export \
  --input-path table.qza \
  --output-path exported-table
```

**Step 7. Convert biom to TSV**

```
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif  biom convert \
  -i exported-table/feature-table.biom \
  -o feature-table.tsv \
  --to-tsv
```

**Step 8. Export taxonomy table into long format**

```
apptainer exec -B /xdisk/PI-netID/yournetID/16S_ONT/data:/data amplicon_2024.10.sif qiime tools export \
  --input-path taxonomy.qza \
  --output-path exported-taxonomy
```

**Step 9. Convert to long format**

See the longformat.py script on this github page!

**Step 10. split taxonomic ranks**

```
python -c "import pandas as pd; df=pd.read_csv('long_feature_table.tsv', sep='\t'); t=df['taxonomy'].str.split(';', expand=True).apply(lambda x: x.str.strip() if x is not None else x); t=t.reindex(columns=range(7)); t.columns=['kingdom','phylum','class','order','family','genus','species']; df=df.join(t); df.to_csv('long_feature_table_ranks.tsv', sep='\t', index=False)"
```

Tutorials for further analysis can be found on the qiime webpage. There is no full tutorial for PairedEndFastqManifestPhred33V2 data, but you can find each of the steps on the tutorials page https://docs.qiime2.org/2024.10/tutorials/




