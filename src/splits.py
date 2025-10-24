def time_based_mask(df, test_seasons=(2024,)):
    tr_mask = ~df["season"].isin(test_seasons)
    te_mask = df["season"].isin(test_seasons)
    return tr_mask, te_mask
