def group_results_by_organism(results, selected_organisms):
    """Group previously fetched results by organism and extract assay type for GSEs."""
    selected_organisms = [o.strip().lower() for o in selected_organisms]
    grouped = {organism: {"GDS": [], "GPL": [], "GSE": []} for organism in selected_organisms}

    # Process GDS and GPL normally
    for category in ["GDS", "GPL"]:
        for entry in results[category]:
            organism = results["MAPPING"].get(entry, "unknown organism").lower()
            for selected_organism in selected_organisms:
                if selected_organism in organism:
                    pubmed_links = results["PUBMED"].get(entry, [])
                    dataset_link = results["LINKS"].get(entry, "")
                    assay_type = "N/A"
                    grouped[selected_organism][category].append(
                        (entry, dataset_link, pubmed_links, assay_type)
                    )
                    break

    # Process GSE in batches of 50
    gse_entries = results["GSE"]
    matching_gse = []

    for entry in gse_entries:
        organism = results["MAPPING"].get(entry, "unknown organism").lower()
        for selected_organism in selected_organisms:
            if selected_organism in organism:
                pubmed_links = results["PUBMED"].get(entry, [])
                dataset_link = results["LINKS"].get(entry, "")
                matching_gse.append((entry, selected_organism, dataset_link, pubmed_links))
                break

    batch_size = 50
    for i in range(0, len(matching_gse), batch_size):
        batch = matching_gse[i:i + batch_size]
        for entry, selected_organism, dataset_link, pubmed_links in batch:
            try:
                gse = GEOparse.get_GEO(geo=entry, silent=True)
                assay_type_list = gse.metadata.get("type", ["Unknown"])
                assay_type = ", ".join(assay_type_list)
            except Exception as e:
                assay_type = f"Error: {str(e)}"

            grouped[selected_organism]["GSE"].append(
                (entry, dataset_link, pubmed_links, assay_type)
            )

        if i + batch_size < len(matching_gse):
            cont = input(f"\nProcessed {i + batch_size}/{len(matching_gse)} GSEs. Continue with next 50? (y/n): ").strip().lower()
            if cont != 'y':
                break

    return grouped



def filter_by_assay_type_across_all(grouped_results):
    assay_dict = {}
    for org, categories in grouped_results.items():
        for entry, link, pubmed_links, assay_type in categories.get("GSE", []):
            if assay_type not in assay_dict:
                assay_dict[assay_type] = []
            assay_dict[assay_type].append((entry, link, pubmed_links, org))

    if not assay_dict:
        print("\nNo assay type data found.")
        return

    print("\n🔹 **Available Assay Types:**")
    for assay_type, entries in assay_dict.items():
        print(f"{assay_type}: {len(entries)} datasets")

    selected_type = input("\nEnter assay type to filter: ").strip()
    selected_entries = assay_dict.get(selected_type, [])

    if not selected_entries:
        print("\nNo datasets found for that assay type.")
        return

    print(f"\n🔹 **Datasets with Assay Type '{selected_type}':**")
    for entry, link, pubmed_links, organism in selected_entries:
        pubmed_str = ", ".join(pubmed_links)
        print(f"{entry} ({organism}) - Dataset: {link} - PubMed: {pubmed_str}")
        