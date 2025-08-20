IC_1 = """
    ASK {
      {
        # Check observation has a data set
        ?obs a qb:Observation .
        FILTER NOT EXISTS { ?obs qb:dataSet ?dataset1 . }
      } UNION {
        # Check has just one data set
        ?obs a qb:Observation ;
           qb:dataSet ?dataset1, ?dataset2 .
        FILTER (?dataset1 != ?dataset2)
      }
    }
"""

IC_3 = """
    ASK {
      ?dsd a qb:DataStructureDefinition .
      FILTER NOT EXISTS { ?dsd qb:component [qb:componentProperty [a qb:MeasureProperty]] }
    }
"""

constraints: list[str] = [IC_1, IC_3]
