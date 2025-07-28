# Write the below script in the R terminal from the root repository. Takes a few seconds to install/activate packages.

if (!require("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}

if (!require("KEGGREST")) {
    BiocManager::install("KEGGREST")
}

# ANYTHING ABOVE THIS LINE IS A ONE-TIME INSTALLATION, NO NEED TO RUN AGAIN

library('KEGGREST')
library(png)

pathway_id <- "cre00100"  # KEGG pathway ID for sterol biosynthesis in Chlamydomonas reinhardtii

# Get rxn info for the pathway

query <- keggGet("cre00100")
compounds <- query[[1]]$COMPOUND
# Print individual: compounds[1]
cids <- names(compounds) # Get compounds ids
# Kegg API caps the responses to 10 items so batch them and send multiple requests
batch_size <- 10
all_results <- list()
for (i in seq(1, length(cids), by = batch_size)) {
  batch <- cids[i:min(i + batch_size - 1, length(cids))]
  res <- keggGet(batch)
  all_results <- c(all_results, res)
}
# Extract the 
all_names <- lapply(all_results, function(item) { item$NAME })
all_names_short <- lapply(all_names, function(item) { gsub(";", "", item[[1]]) })
all_names_long <- lapply(all_names, function(item) { if (length(item) > 1) { gsub(";", "", item[[2]]) } else {NA} })
# Extract the formula for each compound
all_formulas <- lapply(all_results, function(item) { item$FORMULA })
# Unlist
cids_vec <- unlist(cids)
names_short_vec <- unlist(all_names_short)
names_long_vec <- unlist(all_names_long)
formulas_vec <- unlist(all_formulas)
# Write in .csv file via dataframe
df <- data.frame(
    KEGG_ID = cids_vec,
    NAME_SHORT = names_short_vec,
    NAME_LONG = names_long_vec,
    FORMULA = formulas_vec
)
write.csv(df, file="./data/kegg/cre00100_compounds.csv", quote=FALSE)