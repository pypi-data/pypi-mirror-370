"""
A library of general utilities focusing mainly on pandas, numPy, csvutil, and jsonutil integration.
For help, explore the readme and the docs markdown files in the package source.
"""
from pandas import DataFrame, Series, concat, core
from numpy import square, radians, append, cos, sqrt

debugInfo = False

geoFence = [
    {
        "name": "PKMR",
        "desc": "M-Resort Lot",
        "box":  ["""35°57'52.6"N 115°09'56.4"W""",
                 """35°57'58.0"N 115°09'49.1"W"""]
    },
    {
        "name": "PKSI",
        "desc": "Swan Island Lot",
        "box":  ["""45°33'39.8"N 122°42'50.8"W""",
                 """45°33'46.6"N 122°42'44.0"W"""]
    },
    {
        "name": "PKBK",
        "desc": "Baker Lot",
        "box":  ["""35°15'39.3"N 116°04'46.7"W""",
                 """35°16'09.1"N 116°04'13.4"W"""]
    },
    {
        "name": "PKBH",
        "desc": "Bullhead Lot",
        "box":  ["""35°10'00.7"N 114°34'09.9"W""",
                 """35°10'17.8"N 114°33'52.9"W"""]
    },
    {
        "name": "PKCM",
        "desc": "Copper Mountain Lot",
        "box":  ["""39°29'56.2"N 106°08'31.5"W""",
                 """39°30'15.6"N 106°08'15.6"W"""]
    },
    {
        "name": "SITT",
        "desc": "Swan Island Test Track",
        "box":  ["""45°33'50.7"N 122°43'00.3"W""",
                 """45°33'21.5"N 122°42'01.5"W"""]
    },
    {
        "name": "SIRT",
        "desc": "Swan Island Regional Testing",
        "box":  ["""45°33'05.3"N 122°43'06.8"W""",
                 """45°34'20.7"N 122°41'28.0"W"""]
    },
    {
        "name": "HSCD",
        "desc": "Hot-Soak Cooldown Prim Loop",
        "box":  ["""35°58'14.4"N 115°09'35.1"W""",
                 """35°36'32.1"N 115°23'35.5"W"""]
    },
    {
        "name": "TR01",
        "desc": "M-Baker Transit",
        "box":  ["""35°15'31.4"N 116°04'55.6"W""",
                 """35°58'10.9"N 115°09'46.0"W"""]
    },
    {
        "name": "TR02",
        "desc": "Bakersfield-Baker Transit",
        "box":  ["""34°48'35.0"N 119°11'42.9"W""",
                 """35°27'51.8"N 115°58'59.5"W"""]
    },
    {
        "name": "TR03",
        "desc": "M-Bullhead Transit",
        "box":  ["""36°02'18.2"N 115°11'33.6"W""",
                 """35°07'55.2"N 114°32'32.0"W"""]
    },
    {
        "name": "TRGJ-CM",
        "desc": "Grand Junction - Copper Mountain Transit",
        "box":  ["""38°56'44.9"N 108°44'36.6"W""",
                 """39°47'55.7"N 106°05'06.3"W"""]
    },
    {
        "name": "TRCM-BR",
        "desc": "Copper Mountain - Burley Transit",
        "box":  ["""38°57'24.4"N 106°00'32.8"W""",
                 """42°36'36.4"N 113°53'29.6"W"""]
    },
    {
        "name": "TRBR-HQ",
        "desc": "Burley - Portland Transit",
        "box":  ["""42°33'28.6"N 113°46'35.6"W""",
                 """45°53'16.4"N 122°55'05.2"W"""]
    },
    {
        "name": "SL01",
        "desc": "Searchlight Flat Loop",
        "box":  ["""35°27'51.3"N 114°55'19.7"W""",
                 """35°17'13.3"N 114°52'15.4"W"""]
    },
    {
        "name": "BH01",
        "desc": "Bullhead City Parking Lot Loop",
        "box":  ["""35°09'38.4"N 114°34'23.4"W""",
                 """35°14'39.7"N 114°14'10.7"W"""]
    },
    {
        "name": "BG02",
        "desc": "Baker Grade; Max Cooling",
        "box":  ["""35°24'20.3"N 115°46'59.4"W""",
                 """35°11'33.4"N 116°08'39.6"W"""]
    },
    {
        "name": "BG03",
        "desc": "Baker Grade; Max Cooling, continue to M",
        "box":  ["""35°11'00.8"N 116°09'16.7"W""",
                 """35°58'16.0"N 115°09'40.9"W"""]
    },
    {
        "name": "BG04",
        "desc": "Baker Grade; Max Transmission Oil",
        "box":  ["""35°11'16.3"N 116°09'12.4"W""",
                 """35°28'55.9"N 115°26'31.4"W"""]
    },
    {
        "name": "LV01",
        "desc": "Las Vegas City Loop",
        "box":  ["""35°56'09.4"N 115°11'30.0"W""",
                 """36°02'50.3"N 115°04'48.3"W"""]
    },
    {
        "name": "LV02",
        "desc": "Mesquite Highway Loop",
        "box":  ["""35°57'22.4"N 115°11'19.1"W""",
                 """36°49'47.0"N 114°00'56.4"W"""]
    },
    {
        "name": "ALT02",
        "desc": "Eisenhower Loop",
        "box": ["""39°29'55.6"N 106°09'01.6"W""",
                """39°41'26.3"N 105°52'56.8"W"""]
    },
    {
        "name": "ALT03",
        "desc": "Loveland Pass",
        "box": ["""39°29'55.6"N 106°09'01.6"W""",
                """39°41'26.3"N 105°51'00.0"W"""]
    },
    {
        "name": "ALT01",
        "desc": "Winter Park",
        "box":  ["""39°29'55.6"N 106°09'01.6"W""",
                 """39°53'55.5"N 105°36'55.4"W"""]
    }
]

def getGPSBox(listItem:list):
    """
    Given an input of a list of two strings containing GPS data in `dms` N `dms` W format, returns a list of `[west, south, east, north]`.
    """
    if len(listItem[0].split(' ')) != 2 or len(listItem[1].split(' ')) != 2:
        listItem = ["""35°57'52.6"N 115°09'56.4"W""",
                    """35°57'58.0"N 115°09'49.1"W"""]
        
    items = [listItem[0].split(' ')[1],listItem[0].split(' ')[0],listItem[1].split(' ')[1],listItem[1].split(' ')[0]]
    results = []

    for item in items:
        gain = 1
        # print(item)
        if "W" in item or "S" in item:
            gain = -1
        else:
            gain = 1
        item = item.replace('N', '').replace('W', '')
        d = int(item.split('°')[0])
        m = int(item.split('°')[1].split("'")[0]) / 60
        s = float(item.split('°')[1].split("'")[1].split('"')[0]) / 3600
        results.append(round(d+m+s, 6)*gain)
        # print(" Results append {}".format(round(d+m+s, 6)*gain))
    results = [min(results[0], results[2]), 
               min(results[1], results[3]), 
               max(results[0], results[2]), 
               max(results[1], results[3])]

    return results

def inGeofence(df:DataFrame, gf:list):
    """
    Given a dataframe object and a geoFence list object, returns True if the dataframe lies within the specified geofence.
    """
    bounds = getGPSBox(gf)
    gps_x = df['GPS_x[°]']
    gps_y = df['GPS_y[°]']
    #print(" x> {} y> {}\n x< {} y< {}".format((gps_x>bounds[0]).all(), (gps_y>bounds[1]).all(), (gps_x<bounds[2]).all(), (gps_y<bounds[3]).all()))
    #print(" x  {} y  {}\n x  {} y  {}".format(bounds[0], bounds[1], bounds[2], bounds[3]))
    if (gps_x>bounds[0]).all() and (gps_x<bounds[2]).all() and (gps_y>bounds[1]).all() and (gps_y<bounds[3]).all():
        return True
    else:
        return False

class Date():
    def __init__(self, month:int=1, day:int=1, year:int=1970):
        self.month = month
        self.year =  year
        self.day =   day

    def __str__(self):
        return "{}/{}/{}".format(self.month, self.day, self.year)
    
    def getDay(self):
        return self.day
    
    def getMonth(self):
        return self.month
    
    def getYear(self):
        return self.year

    def daysAfterZero(self):
        monthLengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        daysFromMonths = sum(monthLengths[0:(self.month-1)])
        return int(self.year * 365.25) + daysFromMonths + self.day
        
    def daysAfterEpoch(self):
        monthLengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        daysFromMonths = sum(monthLengths[0:(self.month-1)])
        return int((self.year-1970) * 365.25) + daysFromMonths + self.day

    def extractDate(path_or_filename:str):
        strs = path_or_filename.split('/')[-1].split('_')
        lens = [len(item) for item in strs]
        #print(strs)
        #print(lens)
        goal = [4, 2, 2]
        for idx, item in enumerate(lens):
            if lens[idx:idx+3] == goal and str.isnumeric(''.join(strs[idx:idx+3])):
                return Date(int(strs[idx+1]), int(strs[idx+2]), int(strs[idx]))
        return Date(1, 1, 1970)

def extractE9Serial(path_or_filename:str, standardize:bool=False):
    """
    Given a string input for a path or filename, extracts the E9 serial number and returns it as a pure string.
    """
    if "E9" in path_or_filename:
        idx = path_or_filename.index("E9")
        E9str = path_or_filename[idx:(idx+6)]
        if standardize:
            E9str = E9str[0:-1]+str(int(int(E9str[-1])/5)*5)
        return E9str
    elif "704783" in path_or_filename:
        return "VOLVO"
    else:
        return "E9XXXX"

def extractGLRunNumber(path_or_filename:str):
    """
    Given a string input for a path or filename, extracts the E9 serial number and returns it as a pure string.
    """
    if "_GL" in path_or_filename:
        idx = path_or_filename.index("_GL")
        return(path_or_filename[(idx+3):(idx+6)])
    else:
        return "999"

def extractVehicleData(E9Serial:str):
    """
    Provided an input serial number as a string in the E9xxxx format (or volvo), returns a tuple of strings:
        (Truck model, Cab configuration, Tractor Color, Engine, Transmission, Axle Ratio)
    If no matching truck is found, returns a tuple of strings of the same length, populated with "--"s.
    """
    data = {
        # Cummins Fleet
        "E96370": ("M2 106", "Daycab", 'Green', "Cummins B7.2", "Allison 9-Speed", "5.88"),
        "E96275": ("49X SFA", "Daycab", 'Tan', "Cummins X15", "Eaton Endurant XD-Pro", "3.91"),
        "E96305": ("47X", "Daycab", 'Green', "Cummins X10 HHP", "Allison 4500 RDS", "4.30"),
        "E93425": ("M2 106", "Daycab", 'White', "Cummins B6.7 Octane", "Allison 9-Speed", "6.14"),

        # Detroit Fleet
        "E95895": ('Gen5 Cascadia 126"', '72" Raised Roof Sleeper', 'Gray with camo hood', "Detroit DD15 Gen6", "DT12-OHE", "2.64OD"),
        "E95870": ('49X SBA', 'Flat Roof Sleeper', 'Brown', "Detroit DD15 Gen6", "DT12-OHE", "3.73"),
        "E96065": ('Gen5 Cascadia 126"', '72" Raised Roof Sleeper', 'Tan', "Detroit DD13 Gen6", "DT12-DHE", "2.41"),
        "E96085": ('M2 114SD', "Daycab", 'Red', "Detroit DD13 Gen6", "Allison 4500 RDS", "3.91"),
        "E95900": ('Gen5 Cascadia', 'Daycab', 'Blue with camo hood', "Detroit DD15 Gen6", "DT12-OHE", "2.85"),
        "E96070": ('49X SFA', '72" Raised Roof Sleeper', 'Blue', "Detroit DD16 Gen6", "DT12-OVX", "3.73"),

        # International
        "INTERNATIONAL": ("LT625", "Sleeper", 'Red', "International S13", "International T14", "2.15"),

        # Volvo
        "VOLVO":  ("VNL860", "Sleeper", 'Dark gray', "Volvo D13TC", "Volvo I-Shift 12-Speed", "2.15")
    }
    if "E9" in E9Serial and 'xxxx' not in E9Serial:
        E9Serial = E9Serial[0:-1] + str(int(int(E9Serial[-1])/5)*5)
    if E9Serial in data:
        return data[E9Serial]
    else:
        return ("--", "--", "--", "--", "--", "--")

def dfRows(df:DataFrame, first_index:int, last_index:int):
    df_new = df.copy()
    first_index = max(first_index, 0)
    last_index = min(last_index, len(df_new)-1)

    return df_new.iloc[first_index:last_index]

def parseFileSize(sz):
    """
    Converts a bit-format integer filesize into a string of appropriate declension (kb, mb, gb) with the appropriate ending.
    """
    if sz > 1000000000:
        return '{:.2f}gb'.format(sz/1000000000)
    elif sz > 1000000:
        return '{:.1f}mb'.format(sz/1000000)
    elif sz > 1000:
        return '{:.1f}kb'.format(sz/1000)
    else:
        return str(sz)+'b'

def compression(f1, f2):
    """
    Yields a string percentage of filesize reduction for two bit-format integer size inputs.
    """
    f1 = int(f1)
    f2 = int(f2)
    largeFile = max(f1, f2)
    smallFile = min(f1, f2)
    return "{:.1f}%".format((1 - smallFile / largeFile) * 100)

def getColumnData(df, colname=""):
    """
    Yields a tuple of (column name, column units, full column name) for the specified name. Returns -1 if no matching column name
    If no column name is provided, returns a list with all signals in the same format.
    """

    columns = list(df.columns)
    units = []
    name = []
    fullname = []

    for column in columns:
        if "[" in column:
            units.append(column.split("[")[1].split("]")[0])
            name.append(column.split("[")[0])
            fullname.append(column)
        else:
            units.append("")
            name.append(column.split("[")[0])
            fullname.append(column)
    
    columns = name
    
    if colname != "":
        for (idx, col) in enumerate(columns):
            if col == colname:
                return (col, units[idx], fullname[idx])
        for (idx, col) in enumerate(columns):
            if col.lower() in colname.lower():
                return (col, units[idx], fullname[idx])
        return -1
    else:
        return list(zip(columns, units, fullname))

def discard(df_old, prefs, empty = True):
    """
    Discards columns based on a preferences file in .json format. 
    By default, discards columns identified as empty. 
    Returns the resultant df.
    """
    df = df_old.copy()
    to_discard = prefs['discard'].dropna()
    columns = df.columns

    # Wildcard search
    for search_item in to_discard.index:
        if "*" in search_item:
            split_location = search_item.index("*")
            start_str = search_item.split("*")[0]
            end_str = search_item.split("*")[1]
            for column in columns:
                name = column.split('[')[0].strip()
                if name[0:len(start_str)] == start_str and name[split_location:(split_location+len(end_str))] == end_str:
                    df = df.drop(column, axis=1)

    columns = df.columns
    # Traditional search
    for column in columns:
        name = column.split('[')[0].strip()
        if name in to_discard.index:
            df = df.drop(column, axis=1)
        elif (df[column] == 0).all() and empty:
            df = df.drop(column, axis=1)
        elif "Unnamed" in column:
            df = df.drop(column, axis=1)
    
    return df

def squish(df, prefs):
    """
    Preforms data trimming on a dataframe based on passed preferences in a .json format.
    Returns reduced size dataframe
    """
    
    # Reformat time column to save decimals
    df["t[s]"] = df["t[s]"].astype(int)

    # Units and Names
    units = prefs['units'].dropna()
    names = prefs['names'].dropna()

    # Identify column types
    columns = df.columns
    for column in columns:
        try:
            tag = column.split('[')[1].split(']')[0]
        except:
            tag = ""
        name = column.split('[')[0].strip()
        if name in names.index:
            df[column] = df[column].astype(float).round(int((names[name])))
        elif tag.lower() in units.index:
            df[column] = df[column].astype(float).round(int((units[tag.lower()])))
    return df

def id_patch(keep):
    """
    Identifies patches in the form of tuples of indices.
    Rising/falling edge for boolean list in the form of a 1D DF.
    """

    # Cast DF to list and init empty lists for start/finish indices
    keep = keep.values.tolist()
    start = []
    finish = []

    # Loop through each element and find high/low changes
    for i, k in enumerate(keep):
        if i > 0 and keep[i] != keep[i-1]:
            if len(start) <= len(finish):
                start.append(i)
            else:
                finish.append(i)
        elif i == 0 and not keep[i]:
            start.append(i)

    # Zip into tuples, then list and return
    result = list(zip(start, finish))
    return result

def interp(df, indices):
    """
    Interpolates data in a provided df based on index sets to replace. 
    """
    for index in indices:
        if index[0] > 1:
            for i in range(index[0], index[1]):
                df.iloc[i] = (df.iloc[index[0]-1] + (i-index[0]+1)*(df.iloc[index[1]] - df.iloc[index[0]-1])/len(range(index[0], index[1]+1)))
        else:
            for i in range(0, index[1]):
                df.iloc[i] = df.iloc[index[1]]
    return df

def gps_filter_data(df):
    """
    Yields a GPS-refined copy of the input dataframe. Does no other cleaning.
    Previously make use of GCD algorithm. Now makes use of the FCC distance formula.
    https://en.wikipedia.org/wiki/Geographical_distance#FCC's_formula
    """
    new_df = df.copy()

    # Calculate distances traveled
    x = radians(new_df['GPS_x[°]'])
    y = radians(new_df['GPS_y[°]'])
    dx = append(x.diff().iloc[1:-1], 0)
    dy = append(y.diff().iloc[1:-1], 0)
    x_m = (x[0:-2] + x[1:-1]) / 2
    
    # Apply FCC Formula
    K1 = 111.13209 - 0.56605 * cos(2 * radians(x_m)) + 0.0012 * cos(4 * radians(x_m))
    K2 = 111.41513 * cos(radians(x_m)) - 0.09455 * cos(3 * radians(x_m)) + 0.00012 * cos(5 * radians(x_m))
    dist = sqrt(square(K1 * dx) + square(K2 * dy)) * 1000
    keep_dist = dist < 1

    # Keep distance under 1km or geofenced into the US
    lat_left, lon_bottom, lat_right, lon_top = [-170, 25, -65, 70]
    keep_region = (new_df['GPS_x[°]'].iloc[0:-1] < lat_right) & (new_df['GPS_x[°]'].iloc[0:-1] > lat_left) & (new_df['GPS_y[°]'].iloc[0:-1] > lon_bottom) & (new_df['GPS_y[°]'].iloc[0:-1] < lon_top)
    keep = keep_dist & keep_region
    for idx in [0, len(df)-1, len(df)-2]: 
        keep[idx] = True
    
    # Create a replaced column for later
    new_df['GPS Replaced [STATE]'] = ~keep
    patches = id_patch(keep)

    # Interpolate Signals
    for signal in ['GPS_x[°]', 'GPS_y[°]', 'GPS_z[m]', 'GPS_speed[kph]', 'GPS_speed_mph[mph]', 'GPS_speed_mph[]']:
        new_df.loc[:, signal] = interp(df.loc[:, signal], patches)
    
    # Recalculate Distance for total traveled (odometer)
    x = radians(new_df['GPS_x[°]'])
    y = radians(new_df['GPS_y[°]'])
    dx = append(x.diff().iloc[1:-1], 0)
    dy = append(y.diff().iloc[1:-1], 0)
    x_m = (x[0:-2] + x[1:-1]) / 2
    K1 = 111.13209 - 0.56605 * cos(2 * radians(x_m)) + 0.0012 * cos(4 * radians(x_m))
    K2 = 111.41513 * cos(radians(x_m)) - 0.09455 * cos(3 * radians(x_m)) + 0.00012 * cos(5 * radians(x_m))

    # Calculate trip odometer
    dist = list(sqrt(square(K1 * dx) + square(K2 * dy)) * 1000)
    dist_traveled = [0]
    for i in range(1, len(dist)):
        dist_traveled.append(round(2*(dist_traveled[i-1]+dist[i]), 0)/2)
    dist_traveled[-1] = dist_traveled[len(df)-3]
    dist_traveled.append(dist_traveled[len(df)-3])
    
    # Pre-round and save
    dist_traveled = Series(dist_traveled)
    dist_traveled.name = 'GPS_Distance_Traveled[m]'
    new_df["Cumulative Distance [m]"] = dist_traveled

    # Return
    return new_df

def comparativeDF(df, signalA, signalB, asList = True, name = ""):
    """
    Outputs the signalA name -> signalB name difference (A > B, relative is positive)
    """
    signalA_name = getColumnData(df, signalA)[2]
    signalB_name = getColumnData(df, signalB)[2]

    result = df[signalA_name] - df[signalB_name]
    result.name = name

    if not asList and name == "":
        raise ValueError("Name must be defined if result is passed as DF (asList = False).")

    if asList:
        return result.values.tolist()
    else:
        return result

def roundCols(df, rounding_accuracy):
    """
    Given a dataframe and a rounding accuracy dict, returns the dataframe with each column rounded to spec.
    """
    new_df = df.copy()

    for column in new_df.columns:
        try:
            new_df[column] = new_df[column].astype(float).round(rounding_accuracy[column])
        except Exception as e:
            print("[Error] {e.errno}] Failed to round column {column}. Ensure all columns are numeric in nature.")
    
    return new_df

def parseName(columns, name:str):
    """
    Checks if the name string input is a signal in the columns provided.
    Columns may be of type list or columns object (like df.columns).

    If the name is found, returns the corrected name (including units and capitalization).
    Else, returns -1.

    The name string can contain the '[units]' portion of a signal name, but does not need to.
    """
    if isinstance(columns, core.indexes.base.Index):
        columns = columns.to_list()
    columns_new = [str(column).lower().split('[')[0].strip() for column in columns]
    
    name = name.lower().split('[')[0]
    if name.lower().strip() in columns_new:
        return columns[columns_new.index(name.lower().strip())]
    return -1

def parseNames(columns, keys):
    """
    Given columns in the form of df.columns, yields the full column names matching the abbreviated key inputs
    E.g. for columns ['Col1[C]', 'Col2[F]', 'Col3[K]'] and key 'col2', 'Col2[F]' would be returned.
    If no match, returns []
    """
    if not isinstance(keys, list):
        keys = [keys]
    
    keysFound = [False] * len(keys)
    results = []

    for (idx, key) in enumerate(keys):
        for column in columns:
            if key.lower().strip() == column.split('[')[0].lower().strip() and not keysFound[idx]:
                results.append(column)
                keysFound[idx] = True
        if not keysFound[idx]:
            results.append("(Not found) "+str(key))
    
    return results

def signalFromName(df, name):
    """
    Yields all the associated data with a specific abbreviated name input.
    If no match, returns a list of the appropriate size of 0s
    """
    # print(" signalFromName "+name+"\n  "+str(parseNames(df.columns, name)))
    searchName = parseNames(list(df.columns), str(name))
    if searchName != [] and "Not found" not in searchName[-1]:
        return list(df[searchName[-1]])
    else:
        return [0]*len(df)

def formatData(df, signal_x, signals_y=""):
    """
    Given a DF object and a signal name, returns a list of the raw data under that column.
    If provided a second signal, either as a name or a list of names, returns an N dimensional array.
    """
    if signals_y == "":
        return signalFromName(df, signal_x)
    elif type(signals_y) != list:
        signals_y = [signals_y]
    res = [signalFromName(df, signal_x)]
    for signal in signals_y:
        # print("SFN Run: "+signal)
        res.append(signalFromName(df, signal))
    return res

def ema(data, span=3):
    """
    Standard Exponential Moving Average Filter
    Given a list input and an optional span input, outputs a list of the same length with the filter applied.
    Original implementation by Dayanand Shah.
    """
    alpha = 2 / (span + 1)
    ema_values = []
    
    # Initialize the first EMA with the first data point
    if data:
        ema_values.append(data[0])
    
    # Calculate subsequent EMAs
    for i in range(1, len(data)):
        ema_values.append((data[i] * alpha) + (ema_values[-1] * (1 - alpha)))
        
    return ema_values

def sma(data, span=3):
    """
    Standard Simple Moving Average Filter
    Given a list input and an optional span input, outputs a list of the same length with the filter applied.
    """
    if span % 2 != 1:
        span = span + 1

    sma_values = []
    if data and len(data)>=(span):
        for i in range(0, int(span/2)):
            sma_values.append(data[i])
    else:
        return data
    
    for i in range(int(span/2), len(data)-int(span/2)):
        sma_values.append(round(sum(data[(i-1):(i+2)])/span, 8))
    
    for i in range(len(data)-int(span/2), len(data)):
        sma_values.append(data[i])

    return sma_values

def applyFilter(data, toFilter=[], span=3):
    """
    Provided a list of numbers or a list of lists of numbers, applies an EMA filter to relevant data and returns the result.
    """
    if data:
        if isinstance(data[0], list):
            res = []
            
            for (i,col) in enumerate(data):
                if toFilter == [] or i in toFilter:
                    res.append(ema(col, span))
                else:
                    res.append(col)
            return res
        else:
            return ema(data, span)

def getRoute(df, notFoundStr:str=""):
    """
    Provided any DF object with GPS_x[°] and GPS_y[°] signals present, returns a tuple: (Route Name, Route Description).
    If none are found, uses the default notFoundStr parameter for the Route Name and an empty string for the Route Description.
    To add routes to the parsing system, modify the geoFence parameter. Do so externally with: pvevti.genutil.geoFence.append().
    """
    for route in geoFence:
        # print("Name: {}".format(route['name']))
        if inGeofence(df, route['box']):
            return (route['name'], route['desc'])
    return (notFoundStr, '')

def detectMatching(pathList:list, sort:bool=True):
    """
    Yields a sorted list based on run number of only the CSV paths containing the most common serial number in the input list. 
    """
    # Reserve serial numbers and counts of each serial number lists
    serials = []
    serialCounts = []

    # Loop to find unique serials and count occurrences
    for path in pathList:
        serial = extractE9Serial(path, True)
        if serial != 'E9XXXX':
            if serial not in serials:
                serials.append(serial)
                serialCounts.append(1)
            else:
                serialCounts[serials.index(serial)] += 1
    
    # Return empty if no results (spare processing)
    if len(serials) == 0:
        return []
    
    # Data output
    topSerial = serials[serialCounts.index(max(serialCounts))]
    if debugInfo == True:
        print(list(zip(serials, serialCounts)))
        print('Most frequently occurring: ', topSerial)

    # Create list of only files to sort
    listToSort = []
    dates = []
    runNumbers = []

    # Sanity check dates are the same
    for path in pathList:
        if topSerial == extractE9Serial(path, True):
            listToSort.append(path)
            runNumbers.append(int(extractGLRunNumber(path)))
            dates.append(Date.extractDate(path).daysAfterEpoch())

    span = max(dates) - min(dates)
    if span > 0:
        print("WARN Selection encompasses {} days.".format(span+1))
    
    if sort:
        sortedList = [path for run, path in sorted(zip(runNumbers, listToSort))]
        return sortedList
    else:
        return listToSort
    
def combineDFs(dfs:list=[], runs:list=[], filenames:list=[]):
    """
    Combines a list of dataframes `dfs`. 
    Optionally accepts a list of run numbers `runs`. These may be of type `int` or `str`, but should not include the 'GL' pretext.
    Returns a new dataframe with the data merged. 
    """
    for i in range(0,len(dfs)):
        # print(len(dfs[i]))
        if len(runs) == len(dfs):
            if 'RunNumber[GL]' not in list(dfs[i].columns):
                dfs[i].insert(1, 'RunNumber[GL]', [str(runs[i])]*len(dfs[i]), allow_duplicates=True)
            else:
                dfs[i]['RunNumber[GL]'] = [str(runs[i])]*len(dfs[i])
        if len(filenames) == len(dfs):
            if 'FileName[]' not in list(dfs[i].columns):
                dfs[i].insert(1, 'FileName[]', [str(filenames[i])]*len(dfs[i]), allow_duplicates=True)
            else:
                dfs[i]['FileName[]'] = [str(filenames[i])]*len(dfs[i])
        if 't[s]' in list(dfs[i].columns):
            if 'RunTime[s]' not in list(dfs[i].columns):
                dfs[i].insert(0, 'RunTime[s]', dfs[i]['t[s]'].to_list())
            else:
                dfs[i]['RunTime[s]'] = dfs[i]['t[s]'].to_list()
            if i > 0:
                dfs[i]['t[s]'] += max(dfs[i-1]['t[s]'].to_list()) + 1
    
    if len(dfs) > 1:
        return concat(dfs, ignore_index=True).fillna(0)
    elif len(dfs) == 1:
        return dfs[0]
    else:
        return DataFrame()
    
def subsetDF(df:DataFrame, signals:list):
    """
    Returns the dataframe with only the provided signals.
    Signals can be provided with or without units, and do not require correct capitalization.
    If a requested signal does not exist in the DF, it is omitted from the result.
    """
    signals = [parseName(df.columns, signal) for signal in signals if parseName(df.columns, signal) != -1]
    return df[signals]
