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
url = "https://find-and-update.company-information.service.gov.uk/company/04958719/filing-history/MzQ3MjcxNzcwNGFkaXF6a2N4/document?format=xhtml&download=0"
model_xbrl = controller.modelManager.load(url)
