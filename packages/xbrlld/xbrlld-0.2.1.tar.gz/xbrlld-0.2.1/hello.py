# %%

from arelle import Cntlr

controller = Cntlr.Cntlr()
model_xbrl = controller.modelManager.load(
    "https://xbrl.frc.org.uk/FRS-102/2025-01-01/FRS-102-2025-01-01.xsd"
)

# %%

relationship_set = model_xbrl.relationshipSet(
    "http://www.xbrl.org/2003/arcrole/concept-reference",
)

# %%

ref = relationship_set.modelRelationships[1000].toModelObject

ref.viewText().strip()

# %%
from xbrlld.taxonomy import write_taxonomy_to_rdf

write_taxonomy_to_rdf(
    "https://xbrl.frc.org.uk/FRS-102/2025-01-01/FRS-102-2025-01-01.xsd",
    "frs102-2025-01-01.ttl",
)

# %%

from xbrlld.taxonomy import write_taxonomy_to_rdf

write_taxonomy_to_rdf(
    "https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-all-2024.xsd",
    "us-gaap-all-2024.ttl",
)

# %%
from arelle import Cntlr

controller = Cntlr.Cntlr()
model_xbrl = controller.modelManager.load(
    "https://www.sec.gov/Archives/edgar/data/1326801/000162828025036791/meta-20250630.htm"
)

# %%

# modelDocument gives access to references
doc = model_xbrl.modelDocument

# schemaRef elements (imports)
for schema_ref in doc.referencesDocument.keys():
    print("Schema:", schema_ref.uri)

# %%
# Family of Apps [Member]

from xbrlld.instance import write_instance_to_rdf

write_instance_to_rdf(
    "https://www.sec.gov/Archives/edgar/data/1326801/000162828025036791/meta-20250630.htm",
    "meta-20250630-v3.ttl",
)

# %%

from rdflib import Dataset, URIRef

d1 = Dataset()
d1.add(
    (
        URIRef("http://example.org/subject"),
        URIRef("http://example.org/predicate"),
        URIRef("http://example.org/object"),
    )
)

d2 = Dataset()
d2.add(
    (
        URIRef("http://example.org/subject"),
        URIRef("http://example.org/predicate"),
        URIRef("http://example.org/object2"),
    )
)

d1 += d2


# %%

# %%
# Family of Apps [Member]

from xbrlld.instance import write_instance_to_rdf

write_instance_to_rdf(
    "./tests/data/instance/04958719_aa_2025-07-07.xhtml",
    "04958719_aa_2025-07-07.ttl",
)
