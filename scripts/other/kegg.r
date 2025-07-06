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

# # Get KEGG Gene IDs and EC, then fuse together index-wise
# pathway_data <- keggGet(pathway_id)
# reaction_ids <- pathway_data[[1]]$GENE
# reaction_kegg <- reaction_ids[!(substr(reaction_ids, 1, 5) == "CHLRE")]
# reaction_ids <- reaction_ids [substr(reaction_ids, 1, 5) == "CHLRE"]
# gene_entries <- paste(reaction_ids, reaction_kegg)
# # Get KEGG EC numbers for lookup
# ec_list <- regmatches(gene_entries, gregexpr("EC:[0-9.]+", gene_entries))
# ec_number <- tolower(unique(unlist(ec_list)))

# reaction_data <- lapply(ec_number, function(ec) {
#   ec_record <- tryCatch(keggGet(ec)[[1]], error = function(e) NULL)

#   if (is.null(ec_record)) { return(NULL) }
#   if (!"REACTION" %in% names(ec_record)) { return(NULL) }

# #   equation <- if (!is.null(record$EQUATION)) {
# #     record$EQUATION
# #   } else if (!is.null(record$DEFINITION)) {
# #     record$DEFINITION
# #   } else if (!is.null(record$REACTION)) {
# #     # Some entries store the equation directly in REACTION
# #     gsub("^.*\\]", "", record$REACTION)  # Remove EC number prefix if present
# #   } else {
# #     NA
# #   }
  
#   data.frame(
#     Gene_EC = ec,
#     Reaction_ID = ec_record$REACTION,
#     # Equation = equation,
#     stringsAsFactors = FALSE
#   )
# })

# Get rxns and save in .xml format

kgml <- keggGet(pathway_id, "kgml")
export_path <- paste("./results/other/", pathway_id, ".kgml", sep="")
writeLines(kgml, export_path)