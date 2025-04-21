from agents.utility.rule_composer_agent import compose_rules_from_document

sample_doc = """
Use 3MA for electronics on a monthly basis.  
New SKUs should be manually forecasted until 3 months of sales history is available.  
For Class A items, run replenishment daily using min-max logic.
"""

rules = compose_rules_from_document(sample_doc, source_doc="test_doc.txt")

print("\n🎯 Extracted Rules:")
for i, rule in enumerate(rules, 1):
    print(f"{i}. {rule}")
