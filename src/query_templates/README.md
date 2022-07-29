## Query templates
Templates to send BioThingsExplorer query requests.

Example of query structure (Disease-SmallMolecule):

```
{
  "message": {
    "query_graph": {
      "nodes": {
        "n0": {
          "categories": [
            "biolink:Disease"
          ]
        },
        "n1": {
          "categories": [
            "biolink:SmallMolecule"
          ]
        }
      },
      "edges": {
        "e01": {
          "subject": "n0",
          "object": "n1"
        }
        }
      }
    }
  }
```
