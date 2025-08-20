"""
A library of utilities relating to the Association for Standardization of Automation and Measuring Systems (ASAM) file formats.
Allows decompression, subsampling, filtering, and metadata extraction of any file in a memory-efficient manner.
Provides Console information and warning configuration, as well as a global significant figures parameter.
"""

from asammdf import MDF
from numpy import floor, round, log10, abs
from pandas import DataFrame, to_timedelta, concat, to_numeric
from os import path

ROUND_SIGFIGS = 5
CONSOLE_INFO = True
CONSOLE_WARN = True

class MF4Object():
    def __init__(self, filepath:str):
        """
        Create an MF4 Object from the filepath provided.\n
        `MF4Object.num_channels` returns an integer of the total count of unique channels. 
        Two identically named channels from two different groups count as one channel.\n
        `MF4Object.data` returns the MDF object.\n
        `MF4Object.channel_data` returns a list of `signalOBJ`s containing properties:\n
          "Name": The channel name\n
          "Group": The integer group number\n
          "Unit": The units of the channel\n
          "GroupComment": The optional comment of the channel's group. Frequently contains samplerate data\n
          "GroupSource": The semantic name of the group source; e.g. "ECP", "CPC5", "XCP-Gateway". Groups with multiple sources contain source data separated by "; "
        """
        if path.isfile(filepath) and '.mf4' in filepath.lower():
            self.data = MDF(filepath)
            self.channel_data = []
            for i, group in enumerate(self.data.groups):
                for channel in group.channels:
                    unit = channel.conversion.unit if channel.conversion else ""
                    comment = group.channel_group.comment if group.channel_group else ""
                    gname = group.channel_group.acq_name if group.channel_group else ""
                    gsource = group.channel_group.acq_source.name if group.channel_group else ""
                    self.channel_data.append({'Name': channel.name, 'Group': i, 'GroupData': comment, 'Unit': unit, 'GroupComment': gname, 'GroupSource': gsource})
            self.num_channels = len(self.channel_data)
        else:
            raise ValueError("Filepath '{}' does not point to a valid MF4.".format(filepath))
    
    def get_all_channel_names(self):
        """
        Returns a list of channel names as strings. Does not include any other data; output is a list of `str`s, not `signalObj`s. 
        """
        return [ch['Name'] for ch in self.channel_data]
    
    def channels_by_name(self, names, only_names=False):
        """
        Given a list of `names` (or a string of one `name`), returns the `signalObj`s corresponding to each.
        If a `name` cannot be found in the MF4, it is ignored.
        If the optional `only_names` parameter is provided and `True`, returns only the formatted names of each matching channel.
        """
        if isinstance(names, str):
            names = [names]
        
        result = []
        if only_names:
            for name in names:
                result += [item['Name']+"["+item["Unit"]+"]" for item in self.channel_data if item['Name'].lower().strip() == str(name).lower().strip()]
        else:
            for name in names:
                result += [item for item in self.channel_data if item['Name'].lower().strip() == str(name).lower().strip()]
        return result
    
    def channels_by_unit(self, unit:str, only_names:bool=False):
        """
        Given a `unit` returns the `signalObj`s corresponding to each.
        If the `unit` cannot be found in the MF4, it is ignored. 
        If the optional `only_names` parameter is provided and `True`, returns only the formatted names of each matching channel.
        """
        if only_names:
            return [item['Name']+"["+item["Unit"]+"]" for item in self.channel_data if item['Unit'] == unit]
        else:
            return [item for item in self.channel_data if item['Unit'] == unit]
    
    def dataFrame(self, channels:list=[], resample:float=1.0):
        """
        Returns a pandas dataFrame object containing only the selected channels, with data resampled to the `resample` value (a frequency in units of seconds).
        """
        signals = []
        if channels == []:
            channels = self.channel_data
            if CONSOLE_WARN: print("WARN: No channels specified, defaulting to all channels ({})".format(len(channels)))
        for channel in channels:
            try:
               if CONSOLE_INFO: print(" > "+channel['Name'], end=': ')
               samples = self.data.get(channel['Name'], channel['Group'])
               chname = channel['Name']+"["+channel['Unit']+"]"
               if CONSOLE_INFO: print("Form DF, ", end='')
               df = DataFrame({chname:to_numeric(samples.samples, errors='coerce')}, index=to_timedelta(samples.timestamps, unit='s')).fillna(0)
               if CONSOLE_INFO: print("Append, ", end='')
               signals.append(df)
               if CONSOLE_INFO: print("Done")
            except Exception as e:
                if CONSOLE_WARN: print("WARN: Error appending signal {} from group {} ({})".format(channel['Name'], channel['Group'], str(e)))
        if signals:
            if CONSOLE_INFO: print("Resample at {}s".format(resample))
            result = concat(signals, axis=1).resample(rule=str(resample)+'s').mean().ffill()
            if CONSOLE_INFO: print("Round DF")
            try:
                result = roundDF(result, ROUND_SIGFIGS)
            except Exception as e:
                if CONSOLE_WARN: print("WARN: Error rounding dataframe ({})".format(str(e)))
            result.index.name = 'Time[s]'
            result.index = result.index.total_seconds()
            result.index = (result.index - result.index[0]).round(2)
            # result.index.name = "Time[s]"
            return result
    
    def close(self):
        self.data.close()

def roundDF(df:DataFrame, n_figs):
    """
    Rounds a dataframe to a specified number of significant figures. Returns the rounded dataframe.
    """
    power = 10 ** floor(log10(abs(df).clip(1e-9)))
    rounded = round(df / power, n_figs - 1) * power
    return rounded

def toName(signalObj:dict):
    """
    Provided a `signalObj`, returns a formatted string in the format `Channel_Name`[`Channel_Unit`]
    """
    return signalObj['Name']+'['+signalObj['Unit']+']'