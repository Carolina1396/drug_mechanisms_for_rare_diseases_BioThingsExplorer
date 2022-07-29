import csv
import glob
import os
import pathlib
import sys
from query_dict import query

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

full_results_fp = os.path.join(__location__, '../results/full_results_test_.csv') 
pathlib.Path(os.path.dirname(full_results_fp)).mkdir(parents=True, exist_ok=True)

output_dir = os.path.join(__location__, '../output/') 
pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)


def get_full_results():
    """
    Iterate over each template
    """
    with open(full_results_fp, 'w', newline='') as full_results_f:
        full_results = dict()

        template_names = set()
        for template_fp in glob.glob(os.path.join(__location__, 'query_templates') + '/*'):
            template_basename = os.path.basename(template_fp)
            template_name, template_ext = os.path.splitext(template_basename)

            template_names.add(template_name)

            output_fp = os.path.join(output_dir, f'{template_name}.csv')
            query(output_fp, template_fp)

            with open(output_fp, newline='', encoding='utf-8') as output_f:
                reader = csv.DictReader(output_f, delimiter=',')
                for row in reader:
                    mondo_id = row["mondo id"]
                    chembl_id = row["chembl id"]
                    has_hit = row["has hit"]

                    full_results_key = (mondo_id, chembl_id)

                    if full_results_key in full_results:
                        full_results_value = full_results[full_results_key]
                    else:
                        full_results_value = {'mondo id': mondo_id, 'chembl id': chembl_id}
                        full_results[full_results_key] = full_results_value

                    full_results_value[template_name] = has_hit

        full_results_fieldnames = ["mondo id", "chembl id"] + list(template_names)
        writer = csv.DictWriter(full_results_f, fieldnames=full_results_fieldnames)

        writer.writeheader()
        for value in full_results.values():
            writer.writerow(value)


if __name__ == "__main__":
        get_full_results()
