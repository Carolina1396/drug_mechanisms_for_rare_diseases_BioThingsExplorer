## Evaluate drug mechanisms in BioThings Explorer for rare disease indications.

### Rare disease indications data set
Data set can be download [here](https://www.accessdata.fda.gov/scripts/opdlisting/oopd/)

### Configuration BioThings Explorer server
Run a local copy of BTE TRAPI interface using documentation provided [here](https://github.com/biothings/BioThings_Explorer_TRAPI)

If you use local copy, set SERVER_URL to be "http://localhost:3000". 
If you want to use the production server, set SERVER_URL to be "https://api.bte.ncats.io" or development server, set SERVER_URL to be "https://dev.api.bte.ncats.io".

### Run queries
`python3 src/full_results_dict.py`.

Add or delete query templates: `src/query_templates`
