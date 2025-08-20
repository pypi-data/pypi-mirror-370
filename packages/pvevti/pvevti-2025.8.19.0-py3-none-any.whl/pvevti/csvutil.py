"""
A library of utilities relating to CSV opening, manipulation, saving, and conversions.
For help, explore the readme and the docs markdown files in the package source.
"""

import os.path
from pandas import DataFrame, read_csv

default_csv_dir   = os.path.expanduser("~")+"\\Downloads\\"

#def open_csv(filepath:str):
#    """
#    Returns a latin-1 encoded CSV from the specified filepath in the form of a PD DF object
#    """
#    return read_csv(filepath, encoding='latin-1')

def most_recent_csv(directory=default_csv_dir, ignore="", cascade = False, contain=""):
    """
    Yields the complete path of the most recently modified CSV in the provided directory.
    Returns -1 if no CSVs exist.
    If left blank, searches the current user's downloads folder. 
    """
    files = os.listdir(directory)
    csv_files = [(directory + "\\" + file) for file in files if ".csv" in file and (ignore == "" or (ignore not in file)) and (contain == "" or (contain in file))]
    if cascade:
        for path in os.listdir(directory):
            fullpath = os.path.join(directory, path)
            if os.path.isdir(fullpath):
                csv_files = csv_files + all_csvs(fullpath, ignore=ignore, cascade=True)
    csv_files.sort(key=os.path.getmtime)
    if len(csv_files) >= 1:
        return csv_files[-1]
    else:
        return -1

def all_csvs(directory=default_csv_dir, ignore="", cascade = False, contain=""):
    """
    Yields a list of complete paths to CSV files located in the provided directory.
    Returns an empty list if no CSVs exist. Set cascade to True to iteratively search through sub-directories.
    """
    files = os.listdir(directory)
    csv_files = [(directory + "\\" + file) for file in files if ".csv" in file and (ignore == "" or (ignore not in file)) and (contain == "" or (contain in file))]
    if cascade:
        for path in os.listdir(directory):
            fullpath = os.path.join(directory, path)
            if os.path.isdir(fullpath):
                csv_files = csv_files + all_csvs(fullpath, ignore=ignore, cascade=True)
    if len(csv_files) >= 1:
        return csv_files
    else:
        return []

def df_from_csv(csv_name, column_names=[], low_memory=False, encoding="latin-1"):
    """
    Yields a dataframe from a provided CSV (path). 
    Only passes specified column names unless none are specified, then passes the full table.
    """
    if type(column_names) == str:
        column_names = [column_names]

    from csv import reader
    with open(csv_name) as csv_file:
        csv_reader = reader(csv_file, delimiter=',')
        cols = next(csv_reader)
    
    from pvevti.genutil import parseName
    column_names = [parseName(cols, column_name) for column_name in column_names if parseName(cols, column_name) != -1]

    try:
        if len(column_names) > 0:
            df = read_csv(csv_name, usecols=column_names, encoding=encoding, low_memory=low_memory, on_bad_lines='skip')
        else:   
            df = read_csv(csv_name, encoding=encoding, low_memory=False, on_bad_lines='skip')
        df.drop(df.columns[df.columns.str.contains('Unnamed', case=False)], axis=1, inplace=True)
    except Exception as e:
        print("[Error: {}] Failed to load DF from {}.".format(str(e), csv_name))
        df = DataFrame(data={})
    
    return df

def df_to_csv(df, csv_name, save_index=False, addition='_Filtered', encoding="latin-1"):
    """
    Saves a provided pandas df to the provided csv path.
    Returns -1 if an error occurs in saving.
        df: dataframe object to save
        csv_name: full path of CSV
        save_index (optional): defaults to false, specifies saving the index columns.
        addition (optional): defaults to "_Filtered", specifies an appendage to add to the end of the literal CSV filename
    """
    csv_name = csv_name.split('.')[0] + addition + '.csv'
    try:
        df.to_csv(csv_name, index=save_index, encoding=encoding)
    except Exception as e:
        if e.errno == 13:
            print("[Error 13] Failed to save CSV. Make sure the file destination is not open in another application.")
        else:
            print("[Error {}] Failed to save CSV.".format(e.errno))
        return -1
    print("Saved DF to "+csv_name)
