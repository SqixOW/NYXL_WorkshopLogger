import re
import sys
import math
import csv
from logDataStruct import LogPattern, MatchInfo, PlayerData
from dataclasses import dataclass, asdict
from mapInfo import Controls, Maps
        
class LogHandler: # Log Parsing & Handling
    def __init__(self, args):
        self.logFile = args[0]
        self.csvFile = args[0].replace('.txt','.csv')
        self.logpattern = LogPattern()
        self.matchInfo = MatchInfo()
        self.playerList = []
        self.initialTimestamp = 0
        self.Maps = Maps()
        self.playerDataDict = {}   
        self.team1OffenseFlag = False

    def set_map_type(self):
        if self.matchInfo.Map in self.Maps.control:
            self.matchInfo.MapType = 'Control'
        elif self.matchInfo.Map in self.Maps.assault:
            self.matchInfo.MapType = 'Assault'
        elif self.matchInfo.Map in self.Maps.hybrid:
            self.matchInfo.MapType = 'Hybrid'
        elif self.matchInfo.Map in self.Maps.escort:
            self.matchInfo.MapType = 'Escort'
           
    def log_handler(self):
        result_csv = open(self.csvFile, 'w')
        dict_key = PlayerData()
        p = asdict(dict_key)
        writer = csv.DictWriter(result_csv, fieldnames=p.keys(), lineterminator = '\n')
        writer.writeheader()

        with open(self.logFile) as fd:
            for line in fd.readlines():
                if self.logpattern.pattern_playerData.match(line):    # pattern 3 : Player Match data
                    self.playerData_stream_handler(line)
                    self.write_csv(line[11:].split(',')[1], result_csv, writer)
                
                elif self.logpattern.pattern_matchInfo.match(line):       # pattern 1 : MatchInfo
                    self.matchInfo_stream_handler(line)

                elif self.logpattern.pattern_playerInfo.match(line):    # pattern 2 : PlayerInfo
                    self.playerInfo_stream_handler(line)                    
                    
                elif self.logpattern.pattern_finalblow.match(line):    # pattern 4 : Final blow occured(handling DeathBy* variables), need to clear the DeathBy series after write to csv
                    self.finalBlow_stream_handler(line)

                elif self.logpattern.pattern_typeControl.match(line): # pattern 5 : handling 'Point' and 'RoundMap' if the map type is control
                    self.typeControl_stream_handler(line)

                elif self.logpattern.pattern_typeOthers.match(line): # pattern 6 : handling 'Point' and 'RoundMap' if the map type is not control
                    self.typeOthers_stream_handler(line)

                elif self.logpattern.pattern_dupstart.match(line): # pattern 7 : handling echo ult
                    self.dupstart_stream_handler(line)

                elif self.logpattern.pattern_dupend.match(line): # pattern 7 : handling echo ult
                    self.dupend_stream_handler(line)

                elif self.logpattern.pattern_resurrect.match(line): #pattern 8 : resurrect
                    self.resurrect_stream_handler(line)

        result_csv.close()

    def matchInfo_stream_handler(self,line): # set MatchInfo Class
        basket_list = self.define_basket_list(line)
        self.matchInfo.Map = basket_list[0]
        self.matchInfo.Team_1 = basket_list[1]
        self.matchInfo.Team_2 = basket_list[2]
        self.matchInfo.Section = basket_list[3]
        self.set_map_type()
        if self.matchInfo.MapType == 'Control':
            maplists = Controls()
            if self.matchInfo.Map == 'Ilios':
                self.matchInfo.RoundName = maplists.ilios[int(self.matchInfo.Section)]
            if self.matchInfo.Map == 'Lijiang Tower':
                self.matchInfo.RoundName = maplists.lijiang_tower[int(self.matchInfo.Section)]
            if self.matchInfo.Map == 'Oasis':
                self.matchInfo.RoundName = maplists.oasis[int(self.matchInfo.Section)]
            if self.matchInfo.Map == 'Busan':
                self.matchInfo.RoundName = maplists.busan[int(self.matchInfo.Section)]
            if self.matchInfo.Map == 'Nepal':
                self.matchInfo.RoundName = maplists.nepal[int(self.matchInfo.Section)]
        else:
            self.matchInfo.Offense = self.matchInfo.Team_2
            self.matchInfo.Defense = self.matchInfo.Team_1

    def playerInfo_stream_handler(self,line): # define playerDataDict dictionary(type : {str, dataclass PlayerData}), and also set player name on PlayerData dataclass
        basket_list = self.define_basket_list(line)
        self.playerList = basket_list
        for i in range(0, len(self.playerList)):
            self.playerDataDict[self.playerList[i]] = PlayerData()
            self.playerDataDict[self.playerList[i]].Player = self.playerList[i]
    
    def playerData_stream_handler(self,line): # set playerDataDict dictonary(type : {str, dataclass PlayerData})
        basket_list = self.define_basket_list(line)
        if self.initialTimestamp == 0:
            self.initialTimestamp = float(basket_list[0])
            idx = self.playerList.index(basket_list[1])
        userProfile = basket_list[1]
        self.playerDataDict[userProfile].Map = self.matchInfo.Map
        self.playerDataDict[userProfile].Section = self.matchInfo.Section
        self.playerDataDict[userProfile].Timestamp = str(round(float(basket_list[0]) - self.initialTimestamp,2))

        if userProfile in self.playerList[0:6]: # set team
            self.playerDataDict[userProfile].Team = self.matchInfo.Team_1
        else:
            self.playerDataDict[userProfile].Team = self.matchInfo.Team_2

        if self.matchInfo.MapType == 'Control': # set map info
            self.playerDataDict[userProfile].RoundName = self.matchInfo.RoundName
        else:
            if userProfile in self.playerList[0:6]:
                if self.team1OffenseFlag == False:
                    self.playerDataDict[userProfile].RoundName = 'Defense'
                elif self.team1OffenseFlag == True:
                    self.playerDataDict[userProfile].RoundName = 'Offense'
            else:
                self.playerDataDict[userProfile].Team = self.matchInfo.Team_2
                if self.team1OffenseFlag == False:
                    self.playerDataDict[userProfile].RoundName = 'Offense'
                elif self.team1OffenseFlag == True:
                    self.playerDataDict[userProfile].RoundName = 'Defense'
        self.playerDataDict[userProfile].Hero = basket_list[2]
        self.playerDataDict[userProfile].HeroDamageDealt = basket_list[3]
        self.playerDataDict[userProfile].BarrierDamageDealt = basket_list[4]
        self.playerDataDict[userProfile].DamageBlocked = basket_list[5]
        self.playerDataDict[userProfile].DamageTaken = basket_list[6]
        self.playerDataDict[userProfile].Deaths = basket_list[7]
        self.playerDataDict[userProfile].Eliminations = basket_list[8]
        self.playerDataDict[userProfile].FinalBlow = basket_list[9]
        self.playerDataDict[userProfile].EnvironmentalDeaths = basket_list[10]
        self.playerDataDict[userProfile].EnvironmentalKills = basket_list[11]
        self.playerDataDict[userProfile].HealingDealt = basket_list[12]
        self.playerDataDict[userProfile].ObjectiveKills = basket_list[13]
        self.playerDataDict[userProfile].SoloKills = basket_list[14]
        self.playerDataDict[userProfile].UltimatesEarned = basket_list[15]
        self.playerDataDict[userProfile].UltimatesUsed = basket_list[16]
        self.playerDataDict[userProfile].HealingReceived = basket_list[17]
        self.playerDataDict[userProfile].UltimateCharge = basket_list[18]
        self.playerDataDict[userProfile].PlayerClosest = basket_list[19]
        self.playerDataDict[userProfile].Position = basket_list[20] + ',' + basket_list[21] + ',' + basket_list[22]
        self.playerDataDict[userProfile].Cooldown1 = basket_list[24]
        self.playerDataDict[userProfile].Cooldown2 = basket_list[25]
        self.playerDataDict[userProfile].CooldownSecondaryFire = basket_list[26]
        self.playerDataDict[userProfile].CooldownCrouching = basket_list[27]
        self.playerDataDict[userProfile].IsCrouching = basket_list[28]
        self.playerDataDict[userProfile].IsAlive = basket_list[29]
        self.playerDataDict[userProfile].TimeElapsed = basket_list[30]
        self.playerDataDict[userProfile].MaxHealth = basket_list[31].rstrip()

    def finalBlow_stream_handler(self,line): # set DeathBy ... 
        basket_list = self.define_basket_list(line) 
        self.playerDataDict[basket_list[3]].DeathByPlayer = basket_list[2]
        self.playerDataDict[basket_list[3]].DeathByHero = self.playerDataDict[basket_list[2]].Hero
        self.playerDataDict[basket_list[3]].DeathByAbility = basket_list[4]
    
    def define_basket_list(self,line): # define basket list (delete [hh:mm:ss])
        basket_list = line[11:].split(',')
        basket_list[len(basket_list)-1] = basket_list[len(basket_list)-1].rstrip()
        return basket_list
    
    def write_csv(self, player, result_csv, writer):
        p = asdict(self.playerDataDict[player])
        writer.writerow(p)

        self.cleansing_DeathBy(player)
        self.cleansing_resurrect(player)
        return 0
    
    def cleansing_DeathBy(self,player):
        if self.playerDataDict[player].DeathByPlayer != '':
            self.playerDataDict[player].DeathByPlayer = ''
        if self.playerDataDict[player].DeathByAbility != '':
            self.playerDataDict[player].DeathByAbility = ''
        if self.playerDataDict[player].DeathByHero != '':
            self.playerDataDict[player].DeathByHero = ''
    
    def cleansing_resurrect(self,player):
        if self.playerDataDict[player].Resurrected == 'RESURRECTED':
            self.playerDataDict[player].Resurrected = ''

    def typeControl_stream_handler(self,line): # set point if the map is Control type
        basket_list = self.define_basket_list(line)
        for i in range(0, 6):
            self.playerDataDict[self.playerList[i]].Point = basket_list[1]
            self.playerDataDict[self.playerList[i+6]].Point = basket_list[2]
        
    def typeOthers_stream_handler(self,line): # set point if the map is not Control type
        basket_list = self.define_basket_list(line)
        if basket_list[1] == "False":
            self.team1OffenseFlag = False            
            for i in range(0, 6):
                self.playerDataDict[self.playerList[i+6]].Point = basket_list[2]
        elif basket_list[1] == "True":
            self.team1OffenseFlag = True
            for i in range(0, 6):
                self.playerDataDict[self.playerList[i]].Point = basket_list[2]
    
    def dupstart_stream_handler(self,line): # handling duplicate - duplicate ON
        basket_list = self.define_basket_list(line)
        self.playerDataDict[basket_list[2]].DuplicateStatus = 'DUPLICATING'
        self.playerDataDict[basket_list[2]].DuplicatedHero = basket_list[3]
    
    def dupend_stream_handler(self,line): # handling duplicate - duplicate OFF
        basket_list = self.define_basket_list(line)
        self.playerDataDict[basket_list[2]].DuplicateStatus = ''
        self.playerDataDict[basket_list[2]].DuplicatedHero = ''

    def resurrect_stream_handler(self, line): # handling resurrect event
        basket_list = self.define_basket_list(line)
        self.playerDataDict[basket_list[2]].Resurrected = 'RESURRECTED'

def main():
    args = sys.argv[1:]
    parser = LogHandler(args)
    parser.log_handler()
       
if __name__ == "__main__":
    main()