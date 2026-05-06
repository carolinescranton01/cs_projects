import pandas as pd

# load feature table
table = pd.read_csv(
    "feature-table.tsv",
    sep="\t",
    skiprows=1,
    index_col=0
)

table.index.name = "feature_id"
table = table.reset_index()

# load taxonomy
tax = pd.read_csv("exported-taxonomy/taxonomy.tsv", sep="\t")
tax_map = dict(zip(tax["Feature ID"], tax["Taxon"]))

# convert wide to long
long = table.melt(
    id_vars="feature_id",
    var_name="sample",
    value_name="abundance"
)

# fix errors
long["abundance"] = pd.to_numeric(long["abundance"], errors="coerce")

# remove zeros
long = long[long["abundance"] > 0]

# attach taxonomy
long["taxonomy"] = long["feature_id"].map(tax_map)

# finalize
long = long[[
    "sample",
    "feature_id",
    "taxonomy",
    "abundance"
]]

# print output
long.to_csv("long_feature_table.tsv", sep="\t", index=False)

print("Done - long_feature_table.tsv created")