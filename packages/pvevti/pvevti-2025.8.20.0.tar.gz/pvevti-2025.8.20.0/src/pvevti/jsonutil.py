"""
A library of json-specific utilities focusing on extracting preferences from json files, and making use of packaged preferences.
For help, explore the readme and the docs markdown files in the package source.
"""

from pandas import read_json
import os

default_prefs_dir = "\\".join(__file__.split("\\")[0:-2])+"\\pvevti\\prefs.json"

class Prefs():
    """
    Preferences class; methods are used to extract various properties from either the default document or a specified document.
    """
    def getPrefs(path=default_prefs_dir):
        """
        Returns a DF object with all preferences. Path can be a path to a prefs.json file, a directory where a prefs.json file exists, or left blank to default to the runpath's prefs.json.
        """
        if path == "":
            pref_path = os.path.dirname(os.path.abspath(__file__))+'\\prefs.json'
        elif "prefs.json" not in path:
            pref_path = path+'\\prefs.json'
        else:
            pref_path = path
        return read_json(pref_path)

    def extractUnits(prefs):
        """
        Returns a list of tuples given a prefs DF object;
         (column units, rounding accuracy)
        """
        return list(zip(prefs['units'].dropna().index.tolist(), prefs['units'].dropna().astype(int).tolist()))
    
    def extractNames(prefs):
        """
        Returns a list of tuples given a prefs DF object;
         (column name, rounding accuracy)
        """
        return list(zip(prefs['names'].dropna().index.tolist(), prefs['names'].dropna().astype(int).tolist()))

    def extractDiscard(prefs):
        """
        Returns a list of columns to drop given a prefs DF object.
        """
        return prefs['discard'].dropna().index.tolist()

    def columnsToDrop(columns, prefs):
        """
        Columns must be input as a columns item (i.e. columns = df.columns)
        Prefs must be a pd prefs object, created with Prefs.getPrefs()
        Returns a list of column names from the original df to drop
        """
        to_discard = Prefs.extractDiscard(prefs)
        result = []

        # Wildcard search
        for search_item in to_discard:
            if "*" in search_item:
                split_location = search_item.index("*")
                start_str = search_item.split("*")[0]
                end_str = search_item.split("*")[1]
                for column in columns:
                    name = column.split('[')[0].strip()
                    if name[0:len(start_str)] == start_str and name[split_location:(split_location+len(end_str))] == end_str:
                        result.append(column)
        
        # Trad search
        for column in columns:
            if column.split("[")[0].strip() in to_discard or "Unnamed" in column:
                result.append(column)

        return result

    def getRoundingAcc(prefs, columns):
        """
        Columns must be input as a columns item (i.e. columns = df.columns)
        Prefs must be a pd prefs object, created with Prefs.getPrefs()
        Returns a dict of keys and values for rounding accuracy.
        """
        
        byUnits = Prefs.extractUnits(prefs)
        byName  = Prefs.extractNames(prefs)
        colResult = {}

        for column in columns:

            if "[" in column and "]" in column:
                colName = column.split("[")[0]
                colUnit = column.split("[")[1].split("]")[0]
            else:
                colName = column
                colUnit = "TEXT"
            
            for (name, acc) in byName:
                if colName == name:
                    colResult[column] = acc

            if column not in colResult:
                for (unit, acc) in byUnits:
                    if colUnit.lower() == unit.lower():
                        colResult[column] = acc
            
            if column not in colResult:
                colResult[column] = 0
        
        return colResult