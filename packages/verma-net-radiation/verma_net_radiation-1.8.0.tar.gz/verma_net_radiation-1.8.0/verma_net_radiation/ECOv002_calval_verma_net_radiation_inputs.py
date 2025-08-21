import os
import pandas as pd

def load_ECOv002_calval_verma_net_radiation_inputs() -> pd.DataFrame:
    """
    Load the input data for the Verma net radiation model from the ECOSTRESS Collection 2 Cal-Val dataset.
    
    Returns:
        pd.DataFrame: A DataFrame containing the input data.
    """

    # Define the path to the input CSV file relative to this module's directory
    module_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(module_dir, "ECOv002-cal-val-verma-net-radiation-inputs.csv")

    # Load the input data into a DataFrame
    inputs_df = pd.read_csv(input_file_path)

    return inputs_df