import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class ReplayAnalyzer:

    def __init__(self, replayReader):
        """
        Use replay data to produce visual information.
        :param replayReader: ReplayReader
        """
        self.__Names = replayReader.Names
        self.__Replays = replayReader.Replays
        if len(self.__Names) < 1 or self.__Names == [""] or self.__Names == None:
            print("Names not found in passsed replayReader")
        if len(self.__Replays) < 1 or self.__Replays == [] or self.__Replays == None:
            print("Replays not found in passed replayReader")

    def __PlayerMatchesName(self, replay):
        """
        A player in the replay matches the name configured in the list of names.
        :returns: boolean
        """
        if(replay.players[0].name in self.__Names or replay.players[1].name in self.__Names):
            return True
        return False

    def __IsLadder(self, replay):
        """
        Checks if replay is a ladder game.
        :returns: boolean
        """
        if(replay.category == 'Ladder'):
            return True
        return False

    def MMROverTime(self):
        """
        Our MMR value over time.
        """
        myname = []
        mymmr = []
        opponentname = []
        opponentmmr = []
        region = []
        for replay in self.__Replays:
            if (self.__PlayerMatchesName(replay) and self.__IsLadder(replay)):
                for player in replay.players:
                    if (player.name in self.__Names):
                        myname.append(player.name)
                        mymmr.append(player.init_data['scaled_rating'])
                    if (player.name not in self.__Names):
                        opponentname.append(player.name)
                        opponentmmr.append(player.init_data['scaled_rating'])
                    region.append(replay.region)
        return 0

    def GGPercentage(self):
        """
        Percentage of games where we message gg before defeat.
        """
        return 0

    def APMOverTime(self):
        """
        Actions Per Minute over time.
        """
        return 0