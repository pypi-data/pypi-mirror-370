import requests
import time
from collections import Counter
import GEOparse
import pandas as pd
import warnings
import sys


def search_geo_data(keywords):
    """Fetch all GDS, GPL, and GSE results for given keywords and count organisms."""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

    query = " AND ".join([f'({keyword}[All Fields])' for keyword in keywords])

    def fetch_results(filter_type):
        search_query = query + f' AND "{filter_type}"[Filter]'
        all_ids = []
        retstart = 0
        batch_size = 200

        while True:
            search_params = {
                "db": "gds", "term": search_query,
                "retmode": "json", "retmax": batch_size,
                "retstart": retstart
            }
            response = requests.get(base_url, params=search_params)
            if response.status_code != 200:
                print(f"Error fetching {filter_type} data. Status code: {response.status_code}")
                break
            response_json = response.json()
            ids = response_json.get("esearchresult", {}).get("idlist", [])
            all_ids.extend(ids)
            if len(ids) < batch_size:
                break
            retstart += batch_size
            time.sleep(1)

        valid_numbers = []
        id_to_organism = {}
        id_to_links = {}
        id_to_pubmed = {}

        for i in range(0, len(all_ids), batch_size):
            batch_ids = all_ids[i:i+batch_size]
            summary_params = {"db": "gds", "id": ",".join(batch_ids), "retmode": "json"}
            summary_response = requests.get(summary_url, params=summary_params).json()
            for uid in batch_ids:
                record = summary_response.get("result", {}).get(uid, {})
                accession = record.get("accession", "")
                entry_type = record.get("entrytype", "")
                organism = record.get("taxon", "Unknown Organism").strip()
                dataset_link = f'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}' if accession else ""
                pubmed_ids = record.get("pubmedids", [])
                pubmed_links = [f'https://pubmed.ncbi.nlm.nih.gov/{pmid}' for pmid in pubmed_ids] if pubmed_ids else ["No PubMed Link"]

                if entry_type.lower() == filter_type and accession.startswith(filter_type.upper()):
                    valid_numbers.append(accession)
                    id_to_organism[accession] = organism
                    id_to_links[accession] = dataset_link
                    id_to_pubmed[accession] = pubmed_links
            time.sleep(1)
        return valid_numbers, id_to_organism, id_to_links, id_to_pubmed

    gds_results, gds_mapping, gds_links, gds_pubmed = fetch_results("gds")
    gpl_results, gpl_mapping, gpl_links, gpl_pubmed = fetch_results("gpl")
    gse_results, gse_mapping, gse_links, gse_pubmed = fetch_results("gse")

    combined_mapping = {**gds_mapping, **gpl_mapping, **gse_mapping}
    organism_counts = Counter(combined_mapping.values())

    return {
        "GDS": gds_results,
        "GPL": gpl_results,
        "GSE": gse_results,
        "MAPPING": combined_mapping,
        "LINKS": {**gds_links, **gpl_links, **gse_links},
        "PUBMED": {**gds_pubmed, **gpl_pubmed, **gse_pubmed},
        "ORGANISM_COUNTS": organism_counts
    }

