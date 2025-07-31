# Write the below script in the R terminal from the root repository. Takes a few seconds to install/activate packages.

if (!require("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}

if (!require("KEGGREST")) {
    BiocManager::install("KEGGREST")
}

library('KEGGREST')

ec_list <- c("2.5.1.21", "1.14.14.17", "2.3.3.10", "1.1.1.88", "2.7.4.2", "2.7.1.36", "4.1.1.33", "5.3.3.2")
ec_names <- c("Squalene synthase", "Squalene epoxidase", "mvaS", "mvaE", "pmk", "mvk", "mvaD", "Idli")
names(ec_names) <- ec_list

compounds_list <- list()
rxns_list <- list()
for (ec in ec_list) {
    cat("Processing EC:", ec, "\n")
    
    # Get reactions associated with the EC number
    reactions <- keggGet(ec)[[1]]$REACTION
    reactions <- lapply(reactions, function(item) { gsub(";", "", item) })
    reactions <- lapply(reactions, function(item) { substr(item, nchar(item)-6, nchar(item)-1) })

    cat("Reactions found:", length(reactions), "\n")
    for (rxn in reactions) {
        r_info <- keggGet(rxn)[[1]]
        compounds <- strsplit(r_info$EQUATION, " ")[[1]]
        compounds <- compounds[substr(compounds, 1, 1) == "C"]

        for (cid in compounds) {
            c_info <- keggGet(cid)[[1]]
            if (c_info$ENTRY %in% lapply(compounds_list, function(x) x$ENTRY)) {
                next  # Skip if compound already processed
            }
            compounds_list <- c(compounds_list, list(c_info))
        }

        r_info$EC <- ec
        r_info$ENZYMENAME <- ec_names[ec]

        eqn <- gsub(" ", "", r_info$EQUATION)
        splt <- strsplit(eqn, "<=>")[[1]]
        reactants <- splt[1]
        products <- splt[2]
        r_info$REACTANTS <- reactants
        r_info$PRODUCTS <- products

        rxns_list <- c(rxns_list, list(r_info))
    }
}

# Make dataframes for compounds list and reactions list separately
cpd_name_vec <- unlist(lapply(compounds_list, function(x) x$NAME[1]))
cpd_id_vec <- unlist(lapply(compounds_list, function(x) x$ENTRY))
cpd_formula_vec <- unlist(lapply(compounds_list, function(x) { if (!is.null(x$FORMULA)) x$FORMULA else NA }))
cpd_exact_mass_vec <- unlist(lapply(compounds_list, function(x) { if (!is.null(x$EXACT_MASS)) x$EXACT_MASS else NA }))
cpd_mol_weight_vec <- unlist(lapply(compounds_list, function(x) { if (!is.null(x$MOL_WEIGHT)) x$MOL_WEIGHT else NA }))

compound_df <- data.frame(ID = cpd_id_vec, NAME = cpd_name_vec, FORMULA = cpd_formula_vec, EXACT_MASS = cpd_exact_mass_vec, MOL_WEIGHT = cpd_mol_weight_vec, stringsAsFactors = FALSE)

rxn_name_vec <- unlist(lapply(rxns_list, function(x) x$NAME[1]))
rxn_id_vec <- unlist(lapply(rxns_list, function(x) x$ENTRY))
rxn_ec_vec <- unlist(lapply(rxns_list, function(x) x$EC))
rxn_enzymename_vec <- unlist(lapply(rxns_list, function(x) x$ENZYMENAME))
rxn_reactants_vec <- unlist(lapply(rxns_list, function(x) x$REACTANTS))
rxn_products_vec <- unlist(lapply(rxns_list, function(x) x$PRODUCTS))

rxn_df <- data.frame(ID = rxn_id_vec, NAME = rxn_name_vec, EC = rxn_ec_vec, ENZYMENAME = rxn_enzymename_vec, REACTANTS = rxn_reactants_vec, PRODUCTS = rxn_products_vec, stringsAsFactors = FALSE)
# Save the dataframes to CSV files
write.csv(compound_df, "./data/altered/tables/compounds_list.csv", row.names = FALSE, quote=TRUE)
write.csv(rxn_df, "./data/altered/tables/reactions_list.csv", row.names = FALSE, quote=TRUE)
