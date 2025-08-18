import os
import pandas as pd

from sdom import load_data
def test_load_data_folder_exist():
    test_data_path = os.path.join(os.path.dirname(__file__), '..', 'Data')
    test_data_path = os.path.abspath(test_data_path)

    assert os.path.exists(test_data_path)
    


def test_load_data_keys_and_types():
    test_data_path = os.path.join(os.path.dirname(__file__), '..', 'Data')
    test_data_path = os.path.abspath(test_data_path)
    
    data = load_data( test_data_path )
    data_keys = data.keys()

    assert "solar_plants" in data_keys
    assert "wind_plants" in data_keys
    assert "load_data" in data_keys
    assert "nuclear_data" in data_keys
    assert "large_hydro_data" in data_keys
    assert "other_renewables_data" in data_keys
    assert "cf_solar" in data_keys
    assert "cf_wind" in data_keys
    assert "cap_solar" in data_keys
    assert "cap_wind" in data_keys
    assert "storage_data" in data_keys
    assert "STORAGE_SET_J_TECHS" in data_keys
    assert "STORAGE_SET_B_TECHS" in data_keys
    assert "scalars" in data_keys

    assert type( data["solar_plants"] ) == list
    assert type( data["wind_plants"] ) == list
    assert type( data["load_data"] ) == pd.DataFrame
    assert type( data["nuclear_data"] ) == pd.DataFrame
    assert type( data["large_hydro_data"] ) == pd.DataFrame
    assert type( data["other_renewables_data"] ) == pd.DataFrame
    assert type( data["cf_solar"] ) == pd.DataFrame
    assert type( data["cf_wind"] ) == pd.DataFrame
    assert type( data["cap_solar"] ) == pd.DataFrame
    assert type( data["cap_wind"] ) == pd.DataFrame
    assert type( data["storage_data"] ) == pd.DataFrame
    assert type( data["STORAGE_SET_J_TECHS"] ) == list
    assert type( data["STORAGE_SET_B_TECHS"] ) == list
    assert type( data["scalars"] ) == pd.DataFrame
    

def test_load_data_param_values():
    test_data_path = os.path.join(os.path.dirname(__file__), '..', 'Data')
    test_data_path = os.path.abspath(test_data_path)
    
    data = load_data( test_data_path )
    
    # Check some specific values in the scalars DataFrame
    assert abs( data["scalars"].loc["LifeTimeVRE"].Value - 30 ) <= 0.05
    assert abs( data["scalars"].loc["LifeTimeGasCC"].Value - 30 ) <= 0.05
    assert abs( data["scalars"].loc["GenMix_Target"].Value - 1 ) <= 0.05
    assert abs( data["scalars"].loc["CapexGasCC"].Value - 940.607 ) <= 0.05
    assert abs( data["scalars"].loc["HR"].Value - 6.4 ) <= 0.05
    assert abs( data["scalars"].loc["GasPrice"].Value - 4.11 ) <= 0.05
    assert abs( data["scalars"].loc["FOM_GasCC"].Value - 13.25 ) <= 0.05
    assert abs( data["scalars"].loc["VOM_GasCC"].Value - 2.22 ) <= 0.05
    assert abs( data["scalars"].loc["MaxCycles"].Value - 3250 ) <= 10
    assert abs( data["scalars"].loc["r"].Value - 0.06 ) <= 0.0005