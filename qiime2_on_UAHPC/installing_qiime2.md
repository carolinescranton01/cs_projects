# Installing qiime2 on the HPC for 16s analysis (v 2024.10)

Qiime2 is a program designed to analyze 16S sequencing data. It has really really good documentation and tutorials, so please follow those to familiarize yourself with the program and how it works before starting your own data! It can be ran on your own computer or on the HPC - running it on your own computer can be slow (especially if you have a lot of data), so using the HPC can speed things up. This tutorial will walk through how to install qiime2 on the UA HPC. Qiime2 cannot be installed on the HPC in the same was conda packages can, but fortunately we can install it using a docker container, which functions like a conda environment with installed packages but is installed and accessed differently. To do this, you need to open the HPC using the **Ocelote** cluster (it will not work on Puma). Open the HPC for ~3 hours with ~8 cores to install qiime2

After opening the terminal on the HPC, download the qiime2 docker container, which is auto-converted to apptainer form (apptainer is better for use on systems like the HPC, whereas docker is better for systems in the cloud). I reccomend doing this in your xdisk folder, as you will have more space to store the files you will analyze with qiime2 (since they can get pretty big). Enter the following commands to move to the xdisk, create a qiime2 folder, and install qiime2 (replace netid with your netid):
```
cd /xdisk/kcooper/netid
mkdir qiime2
cd qiime2
apptainer pull docker://quay.io/qiime2/amplicon:2024.10
```
This might take a long time, but it should finish and build a 'sif' file, or a singular image format file. This file contains everything needed to run qiime2. To run commands using qiime2 on the HPC, you need to use the following format:
```
apptainer exec -B $PWD:/data amplicon_2024.10.sif qiime
```
This should print out a list of available qiime2 commands. Every time you write a command, you need to preface it with 'apptainer exec -B $PWD:/data amplicon_2024.10.sif qiime'. This tells apptainer to look for the amplicon_2024.10.sif file within your current working directory (PWD = print working directory) for the data directory, where it can access qiime2. So, for example, to run this command
```
qiime tools import \
  --type EMPPairedEndSequences \
  --input-path 16s_R01_1and2 \
  --output-path 16s_R01_1and2_sequences.qza
```
You would need to write:
```
apptainer exec -B $PWD:/data amplicon_2024.10.sif qiime tools import \
  --type EMPPairedEndSequences \
  --input-path 16s_R01_1and2 \
  --output-path 16s_R01_1and2_sequences.qza
```
When using qiime2, you should go to the xdisk and into the qiime2 folder, upload your data, and run the analysis within that folder. The data needs to be in the same folder as the amplicon_2024.10.sif file in order for qiime2 to work. When it is all done, copy the outputs into a folder named after the specific project. Alternatively, you can create a new folder within the qiime2 folder, upload your raw data, and enter that folder to run the commands, but rather than running $PWD:/data in the apptainer exec command, you would write out the entire path to the qiime2 folder with the amplicon_2024.10.sif file in it (change netid to your netid)- 
```
apptainer exec -B /xdisk/kcooper/netid/qiime2:/data amplicon_2024.10.sif qiime
```

For a qiime2 tutorial (version 2024.10), follow this link: https://docs.qiime2.org/2024.10/tutorials/index.html

Version 2024.10 is outdated in qiime2 - they released 2025.4. However, on the HPC, we don't have this version. You can download it onto your own computer and run qiime2 there by following the instructions at this link https://amplicon-docs.qiime2.org/en/latest/explanations/getting-started.html


