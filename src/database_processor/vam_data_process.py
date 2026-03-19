import pandas as pd

def get_VAM_OCTG_data(xlsx_path, basic=True):
    df_vam_data = pd.read_excel(xlsx_path)
    df_vam_by_grade = split_VAM_OCTG_data_by_grade(df_vam_data)
    df_vam_by_grade['Slenderness Ratio'] = df_vam_by_grade['Size (OD)'] / df_vam_by_grade['Wall Thickness (in)']

    if basic:
        return get_basic_pipe_options(df_vam_by_grade)
    return df_vam_by_grade


def split_VAM_OCTG_data_by_grade(df_vam_data):
    grade_cols = [c for c in df_vam_data.columns if c.startswith("JYS @") and c.endswith("ksi (kips)")]
    df_vam_by_grade = (
        df_vam_data
        .melt(
            id_vars=[c for c in df_vam_data.columns if c not in grade_cols],
            value_vars=grade_cols,
            var_name="Steel Grade Source",
            value_name="JYS (kips)"
        )
        .dropna(subset=["JYS (kips)"])
        .copy()
    )
    # ADD GRADE KEY
    df_vam_by_grade["Steel Grade"] = (
        "VM"
        + df_vam_by_grade["Steel Grade Source"]
            .str.extract(r"@(\d+)\s*ksi", expand=False)
            .astype(int)
            .astype(str)
    )

    # ADD YIELD STRESS
    df_vam_by_grade["Yield stress (ksi)"] = (
        df_vam_by_grade["Steel Grade Source"]
            .str.extract(r"@(\d+)\s*ksi", expand=False)
            .astype(float)
    )

    return df_vam_by_grade


def get_basic_pipe_options(df_vam_by_grade):
    return (
        df_vam_by_grade[["Size (OD)", "Wall Thickness (in)", "Yield stress (ksi)", "Slenderness Ratio"]]
        .drop_duplicates()
        .sort_values(["Size (OD)", "Wall Thickness (in)", "Yield stress (ksi)", "Slenderness Ratio"])
        .reset_index(drop=True)
    )

