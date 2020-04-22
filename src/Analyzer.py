import sc2reader
from sc2reader.engine.plugins import SelectionTracker, APMTracker
sc2reader.engine.register_plugin(SelectionTracker())
sc2reader.engine.register_plugin(APMTracker())
import os
import sys
import shutil
import datetime as dt
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import itertools
import threading
import time
import sys
from multiprocessing import Queue

class Analyzer(object):

    def __init__(self):
        self.days = 2
        self.replaylist = []
        self.racelist = []
        self.Config = self.ConfigData()
        self.sc2replaypath = self.Config ["App"]["Game"]["path"]
        self.replayfiles = []
        self.ratings = []
        self.currentReplay = 0
        self.players = []
        self.races = []
        self.gamedates = []
        self.names = []
        self.results = []
        self.myratings = []
        self.myplayers = []
        self.mynames = []
        self.myresults = []
        self.myraces = []
        self.filecount = 1
        self.gg = []
        self.myapm = []
        self.opponentapm = []
        self.done = False
        self.ggtypes = ['gg', 'ghg', 'Gg', 'gG', 'g', 'GG']

    def Animate(self):
        percent = 0
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self.done:
                break
            sys.stdout.write('\rprocessing ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rComplete     ')
    
    def ConfigData(self):
        dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
        with open(dir_path + '\Config.json') as data_file:
            data = json.load(data_file)
            return data
    
    def AppendReplayList(self):
        filelist = [f for f in os.listdir(self.sc2replaypath) if f.endswith(".SC2Replay")]
        self.filelistlength = len(filelist)
        for f in filelist:
            os.remove(os.path.join(self.sc2replaypath, f))
        now = dt.datetime.now()
        ago = now - dt.timedelta(days=self.days)
        replayfiles = []
        for r, d, f in os.walk(self.sc2replaypath):
            for file in f:
                if '.SC2Replay' in file:
                    replayfiles.append(os.path.join(r, file))
        for file in replayfiles:
            fullname = os.path.join(self.sc2replaypath, file)
            st = os.stat(fullname)
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            if os.path.isfile(fullname) and mtime > ago:
                self.replayfiles.append(fullname)
    
    def IsLadder(self, replay):
        if replay.category == 'Ladder':
            return True
        return False
    
    # Process all replays
    def ProcessReplays(self):
        self.AppendReplayList()
        for index in range(len(self.replayfiles)):
            try:
                self.currentReplay = self.replayfiles[index]
                replay = sc2reader.load_replay(self.currentReplay)
                if(self.IsLadder(replay)):
                    self.GetData(replay)
                    self.filecount = self.filecount + 1
            except Exception as err:
                print(str(err))

    # Player Name and Race gathered
    def GetData(self, replay):
        self.region = replay.region
        for team in replay.teams:
            if team.players[0].name not in self.Config["App"]["Game"]["names"]:
                self.opponentapm.append(team.players[0].avg_apm)
                for player in team:
                    if player.init_data['scaled_rating']:
                        self.ratings.append(player.init_data['scaled_rating'])
                    self.players.append(player)
                    self.names.append(player.name)
                    self.results.append(player.result)
                    self.races.append(player.pick_race[0])
            if team.players[0].name in self.Config["App"]["Game"]["names"]:
                if team.players[0].result == 'Loss': 
                    for message in replay.messages:
                        if message.text in self.ggtypes:
                            if message.player.name == team.players[0].name:
                                self.gg.append('yes')
                            else:
                                self.gg.append('no')
                self.myapm.append(team.players[0].avg_apm)
                for player in team:
                    if player.init_data['scaled_rating']:
                        self.myratings.append(player.init_data['scaled_rating'])
                    self.myplayers.append(player)
                    self.mynames.append(player.name)
                    self.myresults.append(player.result)
                    self.myraces.append(player.pick_race[0])
        self.gamedates.append(replay.date.timestamp())
    
    def main(self):
        if len(os.listdir(self.sc2replaypath)) != 0:
            self.ProcessReplays()

if __name__ == "__main__":

    Analyzer = Analyzer()
    t = threading.Thread(target=Analyzer.Animate)
    t.start()
    Analyzer.main()
    Analyzer.done = True
    # Use directly Columns as argument. You can use tab completion for this!
    
    ratingPlot = pd.DataFrame(dict(Me=Analyzer.mynames, Opponent=Analyzer.names, Time=Analyzer.gamedates, APM=Analyzer.myapm, OpponentAPM=Analyzer.opponentapm, Race=Analyzer.myraces, MyResult=Analyzer.myresults))
    fig = px.scatter(ratingPlot, x=ratingPlot.Time, y=ratingPlot.APM, color=ratingPlot.Race,  marginal_y="violin", trendline="ols", hover_data=[ratingPlot.Me, ratingPlot.Opponent, ratingPlot.OpponentAPM, ratingPlot.MyResult])
    fig.update_layout(
        showlegend=True,
        title_text="APM over " + str(Analyzer.days) + " days",
        height=1000,
        width=1900,
    )
    fig.show()

    ratingPlot = pd.DataFrame(dict(Me=Analyzer.mynames, Opponent=Analyzer.names, Time=Analyzer.gamedates, Ratings=Analyzer.ratings, Race=Analyzer.races, MyResult=Analyzer.myresults))
    fig2 = px.scatter(ratingPlot, x=ratingPlot.Time, y=ratingPlot.Ratings, color=ratingPlot.Race,  marginal_y="violin", trendline="ols", hover_data=[ratingPlot.Me, ratingPlot.Opponent, ratingPlot.MyResult])
    fig2.update_layout(
        showlegend=True,
        title_text="Opponent Ratings over " + str(Analyzer.days) + " days",
        height=1000,
        width=1900,
    )
    fig2.show()

    ratingOverTime = pd.DataFrame(dict(Me=Analyzer.mynames, Opponent=Analyzer.names, Time=Analyzer.gamedates, MyRating=Analyzer.myratings, Race=Analyzer.races, MyResult=Analyzer.myresults))
    fig3 = px.scatter(ratingOverTime, x=ratingOverTime.Time, y=ratingOverTime.MyRating, color=ratingOverTime.MyResult, marginal_y="violin", trendline="ols", hover_data=[ratingOverTime.Me, ratingOverTime.Opponent, ratingOverTime.MyResult])
    fig3.update_layout(
        showlegend=True,
        title_text="My Ratings over " + str(Analyzer.days) + " days",
        height=1000,
        width=1900,
    )
    fig3.show()

    labels = ['GG','No GG']
    yes = [Analyzer.gg[i] for i in range(len(Analyzer.gg)) if Analyzer.gg[i] == 'yes']
    no = len(Analyzer.gg) - len(yes)
    values = [len(yes), no]
    
    fig4 = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig4.show()