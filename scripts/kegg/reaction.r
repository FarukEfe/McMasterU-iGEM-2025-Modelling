# Write the below script in the R terminal from the root repository. Takes a few seconds to install/activate packages.

if (!require("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}

if (!require("KEGGREST")) {
    BiocManager::install("KEGGREST")
}

library('KEGGREST')
library(png)

organism <- "cre"  # Chlamydomonas reinhardtii
pathway_id <- "cre00100"  # KEGG pathway ID for sterol biosynthesis in Chlamydomonas reinhardtii

query <- keggGet(pathway_id)
cids <- names(query[[1]]$COMPOUND)

# For each compound get all the reactions
    # for each reaction, find the pathway and formula
        # If a reaction pathway is a match, add the formula to a new spreadsheet
        # For each compound not currently in the list, add to the new compound list of downloads

rxns <- list()
full_cids <- cids
batch_size <- 10
for (i in seq(1, length(cids), by = batch_size)) {
    batch <- cids[i:min(i + batch_size - 1, length(cids))]
    
    for (compound_id in batch) {
        cat("Processing compound:", compound_id, "\n")
        
        # Get all reactions for this compound
        reactions <- keggLink("reaction", compound_id)
        # Print reactions for debugging
        # cat(reactions, "\n")

        # If there are no reactions, skip to the next compound
        if (length(reactions) == 0) {
            cat("No reactions found for compound:", compound_id, "\n")
            next
        }

        if (length(reactions) > 0) {
            for (rxn_id in reactions) {

                # ignore if rxn is already in the list
                if (rxn_id %in% names(rxns)) {
                    next
                }

                reaction_data <- keggGet(rxn_id)[[1]]
                eqn <- gsub(" ", "", reaction_data$EQUATION)  # Remove spaces from the equation
                # Split eqn into reactants and products
                reactants <- strsplit(eqn, "<=>")[[1]][1]
                products <- strsplit(eqn, "<=>")[[1]][2]
                # split reactants and products into individual compounds
                reactants_list <- strsplit(reactants, "\\+")[[1]]
                products_list <- strsplit(products, "\\+")[[1]]
                full_cids <- c(full_cids, reactants_list, products_list)
                # Get formula list for reactants and products
                rxns[[rxn_id]] <- list(
                    KEGG_ID = rxn_id,
                    NAME = reaction_data$NAME,
                    REACTANTS = reactants_list,
                    PRODUCTS = products_list,
                    PATHWAYS = reaction_data$PATHWAY
                )

            }
        }
    }
}

# Get the additional list of compounds from the list of reactions (rxns) that are not in the original list of compounds (cids)
full_cids <- unique(full_cids)

# Write the reactions in dataframe and export .csv
rids_vec <- unlist(names(rxns))
names_vec <- unlist(lapply(rxns, function(rxn) { if (is.null(rxn$NAME)) { NA } else { rxn$NAME[[1]] } }))
reactants_vec <- sapply(rxns, function(rxn) { paste(rxn$REACTANTS, collapse = "+") })
products_vec <- sapply(rxns, function(rxn) { paste(rxn$PRODUCTS, collapse = "+") })
pathways_vec <- sapply(rxns, function(rxn) { paste(rxn$PATHWAYS, collapse = "|") })
df <- data.frame(
        KEGG_ID = rids_vec,
        NAME = names_vec,
        REACTANTS = reactants_vec,
        PRODUCTS = products_vec,
        PATHWAYS = pathways_vec
)
write.csv(df, file="./data/kegg/cre00100_reactions.csv", quote=TRUE, row.names = FALSE)

# Get full list rxns
batch_size <- 10
all_results <- list()
for (i in seq(1, length(full_cids), by = batch_size)) {
  batch <- full_cids[i:min(i + batch_size - 1, length(full_cids))]
  cat("Processing batch of compounds:", paste(batch, collapse = ", "), "\n")
  res <- keggGet(batch)
  # Remove items where FORMULA is NULL
  res <- res[!sapply(res, function(item) is.null(item$FORMULA))]
  # Add to results
  all_results <- c(all_results, res)
}
# Extract the id and names
all_entries <- lapply(all_results, function(item) { item$ENTRY[[1]] })
all_ids <- lapply(all_entries, function(item) { item[[1]] })
all_names <- lapply(all_results, function(item) { item$NAME })
all_names_short <- lapply(all_names, function(item) { if (length(item) >= 1) { gsub(";", "", item[[1]]) } else {NA} })
all_names_long <- lapply(all_names, function(item) { if (length(item) > 1) { gsub(";", "", item[[2]]) } else {NA} })
# Extract the formula for each compound
all_formulas <- lapply(all_results, function(item) { item$FORMULA })
# Other important specs
all_exact_mass <- lapply(all_results, function(item) { if (!is.null(item$EXACT_MASS)) { item$EXACT_MASS } else {NA} })
all_mol_weight <- lapply(all_results, function(item) { if (!is.null(item$MOL_WEIGHT)) { item$MOL_WEIGHT } else {NA} })
# Unlist
cids_vec <- unlist(all_ids)
names_short_vec <- unlist(all_names_short)
names_long_vec <- unlist(all_names_long)
formulas_vec <- unlist(all_formulas)
exact_mass_vec <- unlist(all_exact_mass)
mol_weight_vec <- unlist(all_mol_weight)
# Write in .csv file via dataframe
df <- data.frame(
    KEGG_ID = cids_vec,
    NAME_SHORT = names_short_vec,
    NAME_LONG = names_long_vec,
    FORMULA = formulas_vec,
    EXACT_MASS = exact_mass_vec,
    MOL_WEIGHT = mol_weight_vec
)
write.csv(df, file="./data/kegg/cre00100_compounds_ext.csv", quote=TRUE)