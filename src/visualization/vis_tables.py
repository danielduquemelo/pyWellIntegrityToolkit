import numpy as np
from IPython.display import display
import ipywidgets as widgets
import pandas as pd


def display_table_widget(dataframe,):
    try:
        numeric_cols = dataframe.select_dtypes(include=[np.number]).columns
        dataframe[numeric_cols] = dataframe[numeric_cols].round(3)
        table_widget = widgets.HTML(
            value=f"""
            <div style="max-height: 420px; overflow-y: auto; overflow-x: auto; border: 1px solid #ccc; padding: 4px;">
                <style>
                    table.dataframe {{
                        border-collapse: collapse;
                        width: 100%;
                        font-size: 12px;
                    }}
                    table.dataframe thead th {{
                        position: sticky;
                        top: 0;
                        background: white;
                        z-index: 1;
                    }}
                </style>
                {dataframe.to_html(index=False)}
            </div>
            """
        )
        display(table_widget)

    except ImportError:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            display(dataframe)

