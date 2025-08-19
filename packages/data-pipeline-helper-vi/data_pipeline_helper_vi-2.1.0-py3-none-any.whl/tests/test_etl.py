import pandas as pd
import os
import tempfile
from data_pipeline_helper_vi.data_pipeline_helper.etl import save_dataframe_to_csv,load_csv_to_dataframe

def test_load_and_save_csv():
    data = {'col1': [1, 2, 3], 'col2': [4, 5, 6]}
    df = pd.DataFrame(data)
    temp_file = "temp_test.csv"

    save_dataframe_to_csv(df, temp_file)
    loaded_df = load_csv_to_dataframe(temp_file)

    assert df.equals(loaded_df)

    os.remove(temp_file)
