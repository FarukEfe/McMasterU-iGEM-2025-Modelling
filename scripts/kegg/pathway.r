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

# Fetch the pathway image and save it as a PNG file
img <- keggGet(pathway_id, "image")
temp <- tempfile(fileext = ".png")
path <- "./results/other/sterol_syn_path.png"
writePNG(img, target = temp)
file.copy(temp, path)