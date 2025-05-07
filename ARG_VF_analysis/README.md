# Taxonomic, Antibiotic Resistance Gene, and Virulence Factor Identification from single-end reads on the UA HPC
The attached bash script can be used to run through all commands to analyze the ARGs (using DeepARG, Abricate, CARD, Resfinder, and NCBI databases) and VFs (using VFDB) on the HPC, as well as assign taxonomy to the samples via kraken2. 

Upload the script to the HPC (alternatively, create a new bash script using the following command and copy and paste the contents into the script) into a folder tittled with the project name. Within the folder, you should have a directory called raw_reads which contains all of the raw sequence data as .fastq files. This can be organized by sample name - so for example, if you had ten samples, there would be ten folders, labelled sample1 - sample10. Within these folders, there would be several .fastq files from the sequencer (pre-sorted by barcode, so all sample folders contain all of the sequence data for that sample from all sequencing runs). The first step in the script to create folders for all outputs, and the second step is to concatenate all of the sequencing files into one, and then rename it with the folder name. So if the sample1 folder has 200 .fastq files inside, the first loop in the script will concatenate those 200 files into one .fastq file called sample1, and copy that out into a separate directory called fastq_all which will only have the concatenated .fastq files within. 

```
nano analysis.sh
# copy and paste the contents into the GNU editor
# press control X, control Y, enter to save
```
Next, the Antibiotics environment (where deeparg and abricate are installed) is activate. Change the enviroment name if you have them installed elsewhere. Documentation for installation is below:
DeepARG:
Abricate: 

To run the script type the following (replace analysis with the script name, either ARG-VF-Kraken_script_CS.sh or whatever you named or renamed it as):
```
bash analysis.sh
```
