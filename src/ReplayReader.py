import sc2reader
from sc2reader.engine.plugins import SelectionTracker, APMTracker
sc2reader.engine.register_plugin(SelectionTracker())
sc2reader.engine.register_plugin(APMTracker())
import json
import os
import datetime as dt
from multiprocessing import Pool, cpu_count

class ReplayReader:
    
    def __init__(self, days=None, names=None, path=None):
        """
        Gathers replay directory paths, converts replays to usable objects quickly with multiprocessing. 
        Contains attributes: Days, Names, Path, ReplayPaths, and Replays.
        :param days: Gather replays in this duration
        :param names: Replays that contain the names of the this main user
        :param path: Relative Path to Starcraft II Directory
        """
        self.Config = self.ConfigData() if days == None or path == None else None
        if self.Config != None:
            self.Days = self.Config["days"] if days == None else days
            self.Names = self.Config["names"] if names == None else names
            self.Path = self.Config["path"] if path == None else path
        else:
            self.Days = 1
            self.Names = []
            self.Path = os.path.expanduser('~/Documents/StarCraft II/')
        if len(self.Names) < 1 or self.Names == [""] or self.Names == None: 
            print("Warning: No names are currently configured. This may affect the interpretation of data.")
        self.ReplayPaths = self.GetReplayPaths()
        self.Replays = self.CreateReplayList()

    def ConfigData(self):
        """
        :returns: Data from Config JSON file
        """
        try:
            dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
            with open(dir_path + '\Config.json') as data_file:
                data = json.load(data_file)
                return data
        except Exception as ex:
            print(ex)

    def GetReplayPaths(self):
        """
        :returns: List of replay paths
        """
        try:
            filelist = [f for f in os.listdir(self.Path) if f.endswith(".SC2Replay")]
            filelistlength = len(filelist)
            for f in filelist:
                os.remove(os.path.join(self.Path, f))
            now = dt.datetime.now()
            ago = now - dt.timedelta(days=self.Days)
            replaypaths = []
            for r, d, f in os.walk(self.Path):
                for file in f:
                    if '.SC2Replay' in file:
                        fullname = os.path.join(r, file)
                        st = os.stat(fullname)
                        mtime = dt.datetime.fromtimestamp(st.st_mtime)
                        if os.path.isfile(fullname) and mtime > ago:
                            replaypaths.append(fullname)
            return replaypaths
        except Exception as ex:
            print(ex)
    
    def LoadReplay(self, replaypath):
        """
        :param replaypath: The path of the replay file
        :returns: Replay object
        """
        return sc2reader.load_replay(replaypath)

    def CreateReplayList(self):
        """
        :returns: List of replay objects
        """
        try:
            p = Pool(cpu_count())
            replays = p.map(self.LoadReplay, self.ReplayPaths)
            return replays
        except Exception as err:
            print(err)
