import polars as pl

def find_cycles_in_sourcing_matrix(df):
    """
    Identify (product, origin, destination) tuples that form cycles in the DataFrame.

    Args:
        df (pl.DataFrame): The sourcing matrix DataFrame.

    Returns:
        set: A set of tuples (product, origin, destination) that need to be removed.
    """
    # Create a set to track seen (product, origin, destination) pairs
    seen_pairs = set()
    cycles_to_remove = set()

    # Iterate over the DataFrame rows
    for row in df.iter_rows(named=True):
        product = row['product']
        origin = row['origin']
        destination = row['destination']

        # Check if the swapped pair has been seen
        if (product, destination, origin) in seen_pairs:
            # Add both the current and the swapped pair to the cycles set
            cycles_to_remove.add((product, origin, destination))
            cycles_to_remove.add((product, destination, origin))
        else:
            # Add the current pair to the seen set
            seen_pairs.add((product, origin, destination))

    return cycles_to_remove

def filter_out_cycles(df, prod_origin_destination):
    """
    Filter the DataFrame to keep only rows that match the prod_origin_destination tuples.

    Args:
        df (pl.DataFrame): The original sourcing matrix DataFrame.
        prod_origin_destination (set): A set of tuples (product, origin, destination) to keep.

    Returns:
        pl.DataFrame: The filtered DataFrame.
    """
    # Convert the set to a DataFrame
    filter_df = pl.DataFrame(
        list(prod_origin_destination),
        schema=["product", "origin", "destination"]
    )

    # Perform an inner join to keep only matching rows
    df_filtered = df.join(filter_df, on=["product", "origin", "destination"], how="anti")

    return df_filtered


def break_direct_cycles(df) -> pl.DataFrame:
    """
    Break direct cycles in the DataFrame.

    Args:
    """
    cycles = find_cycles_in_sourcing_matrix(df)
    print("Tuples to remove due to cycles:", cycles)
    # Filter the DataFrame
    df_filtered = filter_out_cycles(df, cycles)



# Example usage
if __name__ == "__main__":
    # Read the CSV into a DataFrame
    df = pl.read_csv("tests/swan_dataset/sourcing_matrix.csv", comment_prefix="#")
    
    # Find cycles
    cycles = find_cycles_in_sourcing_matrix(df)
    print("Tuples to remove due to cycles:", cycles)
    
    # Filter the DataFrame
    df_filtered = filter_out_cycles(df, cycles)
    df_filtered.write_csv("tests/swan_dataset/sourcing_matrix_filtered.csv")
    print("Filtered DataFrame saved to sourcing_matrix_filtered.csv")