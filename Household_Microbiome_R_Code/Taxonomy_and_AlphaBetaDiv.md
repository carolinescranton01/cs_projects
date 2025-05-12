### RMarkdown walkthrough on how to analyze .biom files for taxonomic composition, alpha diversity, and beta diversity

This code was used to analyze all samples for both bacterial and viral taxa, with a few minor edits (such as changing the taxonomic ranks for viruses)

**Step 1. Load required packages**
```{r, echo=T, message=F, warning=F}
library(speedyseq)
library(microbiome) 
library(phyloseq) 
library(microbiomeutilities) 
library(RColorBrewer)
library(ggpubr)
library(DT)
library(data.table)
library(dplyr)
library(writexl)
library(openxlsx)
```

**Step 2: Import biom file:**
```{r}
#biomfile <- import_biom(BIOMfilename = “PATH/TO/YOUR/FILE/biomfile.biom”)
```
Change column names in taxonomy to taxonomic levels (instead of ‘Rank 1’, ‘Rank 2’, etc)
>colnames(tax_table(biomfile)) <- c("Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species")

To replace metadata within biom file using excel file with updated metadata (has to have same Sample_ID as biom file)
>updated_metadata_1 <- read.xlsx("updated_metadata.xlsx")
>rownames(updated_metadata_1) <- updated_metadata_1$Sample_ID
>updated_metadata_2 <- sample_data(updated_metadata_1)
>updated_metadata_2$Sample_ID <- NULL
>biomfile <- merge_phyloseq(biomfile, updated_metadata_2)

Remove unwanted taxa
#remove mitochondira
>biomfile_nomitochondria <- subset_taxa(biomfile, Family != "Mitochondria")
>ntaxa(biomfile)-ntaxa(biomfile_nomitochondria)

#remove chloroplast
>biomfile_nochloroplast<- subset_taxa(biomfile, Family != "Chloroplast")
>ntaxa(biomfile)-ntaxa(biomfile_nochloroplast)

# remove Human DNA
>biomfile_nohuman <- subset_taxa(biomfile, Family != "Hominidae")
>ntaxa(biomfile)-ntaxa(biomfile_nohuman)
>biomfile_nohuman2 <- subset_taxa(biomfile, Genus != "Homo")
>ntaxa(biomfile)-ntaxa(biomfile_nohuman2)


Preliminary figures to look at phyla prevalence, sequencing depth, etc
#Phylum plot
>biom_1 <- plot_taxa_cv(biomfile, plot.type = "scatter")
>biom_1 + scale_x_log10()

#Sequencing depth by geographic location
>biom_seqdepth.ngtax_Geo <- plot_read_distribution(biomfile, "Geographic_Location", "density")
>print(biom_seqdepth.ngtax_Geo)

#Sequencing depth by household location
>biom_seqdepth.ngtax_House <- plot_read_distribution(biomfile, "Household_Location", "density")
>print(biom_seqdepth.ngtax_House)

#Histogram of ASVs – reformat data structure and then graph
>biom_histogram_data<- data.table(
  	tax_table = as.data.frame(tax_table(biomfile)),
  	ASVabundance = taxa_sums(biomfile),
  	ASV = taxa_names(biomfile))
>biom_histogram_plot <- ggplot(biom_histogram_data, aes(ASVabundance)) +  
geom_histogram() + ggtitle("Histogram of ASVs (unique sequence) counts") + theme_bw() + scale_x_log10() + ylab("Frequency of ASVs") + xlab("Abundance (raw counts)")
>print(biom_histogram_plot)

Rarefication of samples + plot for beta diversity analysis 
>set.seed(1234)
>biom_rar <- rarefy_even_depth(biomfile, sample.size = 10000) # can increase number
>print(biom_rar)# Note what number you use
>barplot(sample_sums(biom_rar), las =2)

Alpha diversity calculations
>biom.alphadiv <- alpha(biom_rar, index = "all")

NOTE: Alpha diversity was exported into excel and added into a new dataframe with sample metadata (sample ID, geographic location, household location, etc) which was re-uploaded to R and used for ggplot box+whisker plots which used ANOVA for statistical analysis. Below is an example of the code for a plot

>household_shannon_div <- ggboxplot(diversity_dataframe, x = "Household_Location", 
y = "diversity_shannon") + rotate_x_text() + ylim(0, 10) +  theme(legend.position="none")+labs(title="Shannon Diversity in Households in Different Cities") + stat_compare_means(aes(group=Household_Location), label = 
'p.format', method='anova', label.y=5, label.x=1.5)+facet_wrap(~Geographic_Location)

Beta diversity code
>biom_data <- ordinate(biom_rar, "PCoA", "bray")
>plot_ordination(biom_rar, biom_data, "bray", color = "Geographic_Location", 
shape = "Geographic_Location") + geom_point(size = 1)+ ggtitle("PCoA of Data") + font("ylab", size = 12, face = "bold") + 
stat_ellipse(aes(color = Geographic_Location), level = 0.95, size = 0.5) + 
font("xlab", size = 12, face = "bold") + font("title", size = 10, face = "bold")

Generating taxonomic relative abundance graphs
>biom_phylum <- aggregate_top_taxa2(biomfile, top = 10, "Phylum") 
>biom_phylum.rel <- microbiome::transform(biom_phylum, "compositional")
>biom_phylum.rel <- psmelt(biom_phylum.rel)

# Convert phyloseq object to a data frame
>dfphy <- psmelt(biom_phylum.rel)
>biom_phy.rel.abun <- ggplot(dfphy, aes(x = Household_Location, y = Abundance, 
fill = Phylum)) +
geom_bar(stat = "identity") +
 	facet_wrap(~ Geographic_Location, scales = "free_x") +
theme(legend.position = "bottom", legend.text = element_text(size = 6), 
legend.title = element_text(size = 10), legend.key.size = unit(0.5, "cm"), 
legend.spacing.y = unit(0.1, "cm")) +
 	scale_fill_brewer("Phylum", palette = "Paired") + 
 	theme_bw() + 
  	theme(axis.text.x = element_text(angle = 90, size = 6)) + 
labs(title = "Relative Abundance by Household Location", x = "Household Location",
y = "Relative Abundance") + guides(fill = guide_legend(title = "Phylum", 
title.theme = element_text(size = 10), label.theme = element_text(size = 8), 
keywidth = unit(0.5, "cm"), keyheight = unit(0.5, "cm")))

>print(biom_phy.rel.abun)

NOTE: The same methods were used for other taxonomic levels. x was changed to geographic_location when looking at each city overall. Data can be subsetted to look at specific geographic or household location’s taxonomy
