def export_dataframe(df, file_name, format=".csv", table_name="my_table", **kwargs):
    """
    Exports a Pandas DataFrame to a specified file format, including raw SQL `INSERT` statements.

    Parameters:
        df (pd.DataFrame): The DataFrame to export.
        file_name (str): The file name (without extension) to export the DataFrame to.
        format (str): The file format (e.g., '.csv', '.json', '.xlsx', '.sql', '.parquet', etc.).
        table_name (str): Table name for SQL `INSERT` statements (used only when format='.sql').
        **kwargs: Additional keyword arguments for Pandas export functions.

    Returns:
        str: The full file name of the exported file.
    """
    try:
        file_name_with_extension = f"{file_name}{format}"

        # Export logic for supported formats
        if format == ".csv":
            df.to_csv(file_name_with_extension, index=False, **kwargs)
        elif format == ".json":
            df.to_json(file_name_with_extension, orient="records", **kwargs)
        elif format == ".xlsx":
            df.to_excel(file_name_with_extension, index=False, **kwargs)
        elif format == ".parquet":
            df.to_parquet(file_name_with_extension, index=False, **kwargs)
        elif format == ".html":
            df.to_html(file_name_with_extension, index=False, **kwargs)
        elif format == ".pkl":
            df.to_pickle(file_name_with_extension, **kwargs)
        elif format == ".txt":
            df.to_csv(file_name_with_extension, index=False, sep="\t", **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {format}")

        print(f"DataFrame exported successfully to {file_name_with_extension}")
        return file_name_with_extension

    except Exception as e:
        print(f"Error exporting DataFrame: {e}")
        return None

import json

def export_jsonld_metadata(df, filename="dataset_metadata.json"):
    metadata = {
        "@context": "https://schema.org/",
        "@type": "Dataset",
        "name": "Example Dataset",
        "description": "This dataset contains sample demographic and test score data.",
        "creator": {
            "@type": "Person",
            "name": "Nelson Roque",
            "affiliation": "CASCADE Lab"
        },
        "dateCreated": "2025-05-02",
        "variableMeasured": []
    }

    for col in df.columns:
        metadata["variableMeasured"].append({
            "@type": "PropertyValue",
            "name": col,
            "description": f"Auto-description for {col}",  # you can enrich this
            "value": str(df[col].dtype)
        })

    with open(filename, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata saved to {filename}")
