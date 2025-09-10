# Installing and using conda environments on the UA HPC

When using the HPC, it is important to be organized, so different ways to organize your work and programs have been created. The majority of bioinformatics programs are written in the programming language **python**, which is what we run on the HPC (however, other languages, like R, can be used). Within python, there is a distribuition called **anaconda**. This is a second layer of organization that helps all of the programs which you install and run work together and stay updated. Finally, the level of organization which we will be using most actively is called **conda** - conda is a package and environment manager, meaning when you install packages (different programs used in bioinformatics), it keeps them organized in what are called 'environments'. Many of the programs that we use rely on smaller, more universal programs - for example, an assembly program like metaSPADES requires many additional programs to run, called dependencies, which do things like organize the data, print out messages, and count files. When you install metaSPADES these are all automatically installed, so it isn't something to worry too much about (but is important when troubleshooting errors). When you install multiple complext programs in one conda environment, conda and anaconda work together to make sure that only one version of each dependency is installed so your environment isn't cluttered with many repeated programs and files.

We typically organize conda environments based on the type of analysis - for example, keep all of your assembly programs in an environment called 'assemblers'. Additionally, some programs require large databases which cannot be installed in your personal HPC space. They are installed in the groups folder, which is accessable to everyone in the lab.

Below are instructions on how to create conda environments, manage your conda environments, install programs, and activate conda environments. Additionally, there are resources online that are easy to access just by googling your question - the developers of the entire anaconda/conda system designed it to be easy to use and accessible to everyone, so there is a lot of information you can find online!

To get started, open the HPC for 1+ hours with 4+ cores and enter the following commands in terminal to access python and anaconda:

```
module load anaconda
source .bashrc
```

## Creating a conda environment

To create a conda environment, use the following command (replace ENV_NAME with the name of your environment).

```
conda create -n ENV_NAME
```

A specific version of python can be specified in this by adding python=## (with the number corresponding to the version).


## Installing packages

To install packages, you need to activate the environment and then install them. There are multiple arguments which can be specified in this command.

```
conda activate ENV_NAME
conda install PACKAGE_NAME
```

To specify the version of the package, write PACKAGE_NAME=## (where ## corresponds to the version). To specify the channel to use to install the package, use the '-c' flag.

```
conda install PACKAGE_NAME=3.1 -c biobakery
```

Instructions on what package version or channel to use are often found in the documentation (github page) for the specific package. 


## Managing conda environments

List all conda environments you have created and their paths
```
conda env list
```

Activate and deactivate environments
```
conda activate ENV_NAME
conda deactivate ENV_NAME
```

List all packages installed within an environment (includes dependencies - this will output way more than just the few you did 'conda install' for)
```
conda activate ENV_NAME
conda list
```

Add new channels (change CHANNEL_NAME to correct name)
```
conda config --add channels CHANNEL_NAME
```

Delete a conda environment (deactivate the environment first) - If you want to delete ALL packages associated with that enviroment (other environments will not be affected), add the flag --all
```
conda env remove -n ENV_NAME
```

## Cooper lab conda environments and programs - installation and access

1. Update channels

```
conda config --add channels bioconda biobakery
```

2. Create environments + install packages


a) assemblers
```
conda create -n assemblers
conda activate assemblers
conda install spades -c bioconda
conda install flye -c bioconda
conda install canu -c bioconda
conda install haslr -c bioconda
conda deactivate
```

b) checkM2
```
conda create -n checkM2
conda activate checkM2
conda install checkm2 -c bioconda
conda deactivate
```

c) raxml
```
conda create -n raxml
conda activate raxml
conda install raxml -c bioconda
conda install modeltest-ng -c bioconda
conda deactivate
```

d) cleaning
```
conda create -n cleaning
conda activate cleaning
conda install quast -c bioconda
conda install trimmomatic -c bioconda
conda install fastp -c bioconda
conda deactivate
```

e) metagenomics
```
conda create -n metagenomics
conda activate metagenomics
conda install metabat2 -c bioconda
conda install maxbin2 -c bioconda
conda install concoct -c bioconda
conda install kraken2 -c bioconda
conda install kraken-biom -c bioconda
conda deactivate
```

Access to biobakery env
```
conda activate /groups/kcooper/biobakery_env
```

Access to checkM2 env (if install fails)
```
conda activate /groups/kcooper/checkm2_env
```

Access to metagenomics env (if install fails)
```
conda activate /groups/kcooper/metagenomics_env
```



