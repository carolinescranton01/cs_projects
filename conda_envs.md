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

## Managing conda environments


Add necessary channels (change CHANNEL_NAME to correct name)
```
conda config --add channels CHANNEL_NAME
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
c) raxml
d) cleaning
e) metagenomics

Access to biobakery env

Access to checkM2 env (if install fails)

Access to metagenomicd env (if install fails)



