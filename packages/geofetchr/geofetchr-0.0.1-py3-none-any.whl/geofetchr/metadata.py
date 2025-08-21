def view_metadata_by_id():
    geo_id = input("\nEnter a GEO ID (e.g., GSE12345, GDS67890, GPL13579): ").strip()
    if not geo_id:
        return
    try:
        geo = GEOparse.get_GEO(geo=geo_id, silent=False)
        print(f"\n🔹 **Metadata for {geo_id}:**")
        for key, value in geo.metadata.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        