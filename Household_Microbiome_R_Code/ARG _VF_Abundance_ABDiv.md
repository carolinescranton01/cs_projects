## Antibiotic resistance gene and virulence factor abundance and alpha/beta diversity analysis

### Part 1 - setup

**Step 1 - load required packages**

```
library(ggplot2)
library(ggpubr)
library(tidyverse)
library(broom)
library(AICcmodavg)
library(readxl)
library(rstatix)
library(microbiome)
library(dplyr)
library(writexl)
```

**Step 2 - re-format abricate outputs (.txt files, one per sample per database) into excel sheets**
One sheet was made for the virulence factors (detected using the Virulence Factor Database VFDB), and another for the antibiotic resistance genes detected with the ResFinder database. Columns included the Sample_ID and other metadata (location, house number, household location, scaled number of reads) and then gene name and gene function as two columns, followed by the number of occurrences of that gene in the specific sample, and the scaled occurrences (occurrences / scaled reads) in the sample. All of this reformatting was done in excel, using the python scripts writeexcel.py and sortexcel.py, found in this github repository


CONTINUE FROM HERE - cs
Data was imported using the read_excel function

Pulling out top 20 most abundant VF (or ARGs) from the dataframe (example dataframe is called VF, with Gene_function and Scaled_Occurances columns)
>virulence_20 <- VF %>%
group_by(Gene_function) %>%
summarise(Scaled_Occurances = sum(Scaled_Occurances, na.rm = TRUE)) %>%
arrange(desc(Scaled_Occurances))
>top_20_factors_VF <- virulence_20 %>%
  top_n(20, Scaled_Occurances)
>filtered_VFtop20 <- VF %>%
filter(Gene_function %in% top_20_factors_VF$Gene_function)
>print(top_20_factors_VF)
>print(filtered_VFtop20)

Generating relative abundance data for top 20 VFs/ARGs
>top_relative_abundance_VFDB_comp <- filtered_VFDBtop20 %>%
group_by(Geographic_Location, Household_Number, Household_Location) %>%
mutate(Total_Occurrences = sum(Occurances)) %>%
mutate(Relative_Abundance = Occurances / Total_Occurrences) %>%
ungroup() %>%
select(Geographic_Location, Household_Number, Household_Location, Gene_Name,
Gene_function, Scaled_Occurances, Relative_Abundance)

Summarizing and filtering data, only keep data which exists in processed set
>summarized_data <- top_relative_abundance_VFDB_comp %>%
group_by(Geographic_Location, Household_Location, Gene_function) %>%
summarise(Total_Relative_Abundance = sum(Relative_Abundance, na.rm = TRUE)) %>%
ungroup()
>complete_data <- summarized_data %>%
complete(Geographic_Location, Household_Location)
>complete_data[is.na(complete_data$Total_Relative_Abundance),
"Total_Relative_Abundance"] <- 0
>filtered_data <- complete_data %>% filter(Total_Relative_Abundance > 0)

Make VF/ARG abundance bar graph
>VFDB_RA_barplot_comp <- ggplot(filtered_data, aes(x = Household_Location, y =
Total_Relative_Abundance, fill = Gene_function)) + 
geom_bar(stat = "identity", position = "stack", na.rm = TRUE, alpha = 1, color = "black",
linewidth = 0.3, show.legend = TRUE) +
  	font("ylab", size = 15, face = "bold") +
 	font("xlab", size = 15, face = "bold") + 
theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1)) +
 	labs(title = "Relative Abundance of VF Genes Found in Different Locations", 
size = 30) +
  	ylim(0, 1) + 
  	theme_bw() + 
  	facet_wrap(~Geographic_Location) + 
    	scale_x_discrete(limits = unique(filtered_data$Household_Location)) +
  	theme(
    	axis.text.x = element_text(angle = 60, vjust = 1, hjust = 1, size = 12), 
    	axis.text.y = element_text(size = 12), 
    	axis.title.x = element_text(size = 15, face = "bold"), 
    	axis.title.y = element_text(size = 15, face = "bold"), 
   	 plot.title = element_text(size = 20, face = "bold", hjust = 0.5),
   	 legend.position = "bottom", 
   	 legend.title = element_text(size = 12), 
   	 legend.text = element_text(size = 10), 
    	plot.margin = margin(1, 1, 2, 1, "cm"), 
    	strip.text = element_text(size = 12, face = "bold")
  	)
>print(VFDB_RA_barplot_comp)









VF/ARG alpha and beta diversity

Requires certain data to be pulled out and then restructured (using code – see below). Example data is called biom_res (for resfinder) and is a data frame with 3 columns – FullName (which is the sample_ID), Gene_Name, and Scaled_Occurances. If one sample had ten different ARGs/VFs detected, it will have ten rows in this data frame with the same FullName value and different Gene_Name and Scaled_Occurances values for each row. Data was structured in Microsoft Excel and imported using read_xlsx(). Also requires a metadata file with info on the samples to use when graphing diversity (ie. sample ID, location) – in this example called metadata_res.

Restructure data so that there are now many columns (each is a Gene_Name), and all samples (FullName) have one row. Should be a large matrix, where if a specific gene is detected in a sample, it’s scaled occurrence will be in that column, but if a gene was not detected in that sample, it will have a 0. 

Example data structure before pivot_wider command:
Sample ID	Gene_Name	Scaled_Occurrences
A	Gene1	0.2
A	Gene2	0.3
B	Gene1	0.1
C	Gene2	0.01
C	Gene3	0.5

>wide_data_res <- biom_res %>%
pivot_wider(names_from = Gene_Name, values_from = Scaled_Occurances,
values_fill=0)

Example data structure after pivot_wider command:
Sample ID	Gene1	Gene2	Gene3
A	0.2	0.3	0.0
B	0.1	0.0	0.0
C	0.0	0.01	0.5

Run alpha diversity on data, convert to data frame, and merge with metadata
>diversity_results_res <- wide_data_res %>%
select(-FullName) %>%
apply(1, function(x) diversity(x, index = "shannon"))

>results_res <- data.frame(FullName = wide_data_res$FullName,
shannon_diversity=diversity_results)
>merged_results_res <- results_res %>%
left_join(metadata_res, by = "FullName")



Example ggplot code to make box and whisker plots with ANOVA statistical analysis
>res_geolocs_alpha <- ggboxplot(merged_results_res, x = "Geographic_Location", y =
"shannon_diversity") + rotate_x_text() + ylim(0, 2)+
theme(legend.position="none")+labs(title="Shannon Diversity in ARGs in Different
Cities") + stat_compare_means(aes(group=Geographic_Location), label = 'p.format',
method='anova', label.y=1.99, label.x=0.6)
>print(res_geolocs_alpha)

Beta diversity on ARGs/VFs – uses the same re-formatted data as above. In this example data is called wide_data_res_beta – similar to wide_data_res, but in this example used composite data rather than the entire non-composite set. Metadata is structured the same, again only for composites in this example, as only composite data was used for this particular analysis. 

Generating bray-curtis distances, formatting as a data frame, and linking to metadata: 
>bray_curtis_dist_resbeta <- vegdist(wide_data_res_beta[,-1], method = "bray")
>pcoa_results_resbeta <- cmdscale(bray_curtis_dist_resbeta, eig = TRUE, k = 2)
>pcoa_df_resbeta <- data.frame(PC1 = pcoa_results_resbeta$points[,1], PC2 = >pcoa_results_resbeta$points[,2], FullName = wide_data_res_beta$FullName)
>pcoa_df_resbeta <- pcoa_df_resbeta %>%
left_join(metadata_res_beta, by = "FullName")

Example code for PCoA plot:
>res_beta <- ggplot(pcoa_df_resbeta, aes(x = PC1, y = PC2, color = Household_Location,
shape=Geographic_Location)) +
geom_point(size = 3) +
labs(title = "PCoA of Bray-Curtis Dissimilarity", x = "PC1", y = "PC2") +
theme_minimal() +
stat_ellipse(aes(color = Geographic_Location), level = 0.95, size = 0.5)
>print(res_beta)

















