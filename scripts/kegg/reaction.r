# Write the below script in the R terminal from the root repository. Takes a few seconds to install/activate packages.

if (!require("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}

if (!require("KEGGREST")) {
    BiocManager::install("KEGGREST")
}

library('KEGGREST')
library(png)

pathway_id <- "cre00100"  # KEGG pathway ID for sterol biosynthesis in Chlamydomonas reinhardtii

cids <- list() # Assume we have list of compounds

# For each compound get all the reactions
    # for each reaction, find the pathway and formula
        # If a reaction pathway is a match, add the formula to a new spreadsheet
        # For each compound not currently in the list, add to the new compound list of downloads