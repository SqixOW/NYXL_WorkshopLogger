import re
import sys
import math
import csv
from logDataStruct import LogPattern, MatchInfo, PlayerData
from resourceDataStruct import ResourceData
from dataclasses import dataclass, asdict
from mapInfo import Controls, Maps
        
class LogHandler: # Log Parsing & Handling
    def __init__(self, args):
        self.logFile = args[0]
        self.csvFile = args[0].replace('.txt','.csv')
        #self.resourceDataFile = args[0].replace('.txt','_resourceData.csv')
        self.logpattern = LogPattern()
        self.matchInfo = MatchInfo()
        self.playerList = []
        self.initialTimestamp = 0
        self.Maps = Maps()
        self.playerDataDict = {}   
        self.team1OffenseFlag = 'False'
        self.sectionNumber = 0

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
        resultCsv = open(self.csvFile, 'w')
        #resourceDataCsv = open(self.resourceDataFile,'w')
        
        resultDictKey = PlayerData()
        resultDict = asdict(resultDictKey)
        resultWriter = csv.DictWriter(resultCsv, fieldnames = resultDict.keys(), lineterminator = '\n')
        resultWriter.writeheader()
        """
        resourceDictKey = ResourceData()
        resourceDict = asdict(resourceDictKey)
        resourceWriter = csv.DictWriter(resourceDataCsv, fieldnames = resourceDict.keys(), lineterminator = '\n')
        resourceWriter.writeheader()
        """
        with open(self.logFile) as fd:
            for line in fd.readlines():
                basket_list = self.define_basket_list(line)
                if self.logpattern.pattern_playerData.match(line):    # pattern 3 : Player Match data
                    self.playerData_stream_handler(basket_list)
                    self.boolean_handler(basket_list)
                    self.write_csv(line[11:].split(',')[1], resultCsv, resultWriter)
                    #resourceDict = self.resourceData_handler(basket_list) # Handling Resource Data Category
                    #resourceWriter.writerow(asdict(resourceDict))
                
                elif self.logpattern.pattern_matchInfo.match(line):       # pattern 1 : MatchInfo
                    self.matchInfo_stream_handler(basket_list)

                elif self.logpattern.pattern_playerInfo.match(line):    # pattern 2 : PlayerInfo
                    self.playerInfo_stream_handler(basket_list)                    
                    
                elif self.logpattern.pattern_finalblows.match(line):    # pattern 4 : Final blow occured(handling DeathBy* variables), need to clear the DeathBy series after write to csv
                    self.finalBlows_stream_handler(basket_list)

                elif self.logpattern.pattern_typeControl.match(line): # pattern 5 : handling 'Point' and 'RoundMap' if the map type is control
                    self.typeControl_stream_handler(basket_list)

                elif self.logpattern.pattern_typeOthers.match(line): # pattern 6 : handling 'Point' and 'RoundMap' if the map type is not control
                    self.typeOthers_stream_handler(basket_list)

                elif self.logpattern.pattern_dupstart.match(line): # pattern 7 : handling echo ult
                    self.dupstart_stream_handler(basket_list)

                elif self.logpattern.pattern_dupend.match(line): # pattern 7 : handling echo ult
                    self.dupend_stream_handler(basket_list)

                elif self.logpattern.pattern_resurrect.match(line): #pattern 8 : resurrect
                    self.resurrect_stream_handler(basket_list)

        resultCsv.close()
        #resourceDataCsv.close()

    def matchInfo_stream_handler(self,basket_list): # set MatchInfo Class
        self.matchInfo.Map = basket_list[0]
        self.matchInfo.Team_1 = basket_list[1]
        self.matchInfo.Team_2 = basket_list[2]
        self.matchInfo.Section = str(int(self.matchInfo.Section) + 1)
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

    def playerInfo_stream_handler(self,basket_list): # define playerDataDict dictionary(type : {str, dataclass PlayerData}), and also set player name on PlayerData dataclass
        self.playerList = basket_list
        for i in range(0, len(self.playerList)):
            self.playerDataDict[self.playerList[i]] = PlayerData()
            self.playerDataDict[self.playerList[i]].Player = self.playerList[i]
    
    def playerData_stream_handler(self,basket_list): # set playerDataDict dictonary(type : {str, dataclass PlayerData})
        if self.initialTimestamp == 0:
            self.initialTimestamp = float(basket_list[0])
            idx = self.playerList.index(basket_list[1])
        userProfile = basket_list[1]
        self.playerDataDict[userProfile].Map = self.matchInfo.Map

        if self.matchInfo.MapType != 'Control':
            self.playerDataDict[userProfile].Section = str(self.sectionNumber)
        else:
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
                if self.team1OffenseFlag == 'False':
                    self.playerDataDict[userProfile].RoundName = 'Defense'
                elif self.team1OffenseFlag == 'True':
                    self.playerDataDict[userProfile].RoundName = 'Offense'
            else:
                self.playerDataDict[userProfile].Team = self.matchInfo.Team_2
                if self.team1OffenseFlag == 'False':
                    self.playerDataDict[userProfile].RoundName = 'Offense'
                elif self.team1OffenseFlag == 'True':
                    self.playerDataDict[userProfile].RoundName = 'Defense'
        self.playerDataDict[userProfile].Hero = basket_list[2]
        self.playerDataDict[userProfile].HeroDamageDealt = basket_list[3]
        self.playerDataDict[userProfile].BarrierDamageDealt = basket_list[4]
        self.playerDataDict[userProfile].DamageBlocked = basket_list[5]
        self.playerDataDict[userProfile].DamageTaken = basket_list[6]
        self.playerDataDict[userProfile].Deaths = basket_list[7]
        self.playerDataDict[userProfile].Eliminations = basket_list[8]
        self.playerDataDict[userProfile].FinalBlows = str(int(basket_list[9]) + int(basket_list[11]))
        self.playerDataDict[userProfile].EnvironmentalDeaths = basket_list[10]
        self.playerDataDict[userProfile].EnvironmentalKills = basket_list[11]
        self.playerDataDict[userProfile].HealingDealt = basket_list[12]
        self.playerDataDict[userProfile].ObjectiveKills = basket_list[13]
        self.playerDataDict[userProfile].SoloKills = basket_list[14]
        self.playerDataDict[userProfile].UltimatesEarned = basket_list[15]
        self.playerDataDict[userProfile].UltimatesUsed = basket_list[16]
        self.playerDataDict[userProfile].HealingReceived = basket_list[17]
        self.playerDataDict[userProfile].UltimateCharge = basket_list[18]
        self.playerDataDict[userProfile].Position = basket_list[19] + ',' + basket_list[20] + ',' + basket_list[21]
        self.playerDataDict[userProfile].Cooldown1 = basket_list[23]
        self.playerDataDict[userProfile].Cooldown2 = basket_list[24]
        self.playerDataDict[userProfile].CooldownSecondaryFire = basket_list[25]
        self.playerDataDict[userProfile].CooldownCrouching = basket_list[26]
        self.playerDataDict[userProfile].IsAlive = basket_list[27]
        self.playerDataDict[userProfile].TimeElapsed = basket_list[28]
        self.playerDataDict[userProfile].MaxHealth = basket_list[29]
        self.playerDataDict[userProfile].Health = basket_list[30]
        self.playerDataDict[userProfile].DefensiveAssists = basket_list[31]
        self.playerDataDict[userProfile].OffensiveAssists = basket_list[32]
        self.playerDataDict[userProfile].IsBurning = basket_list[33]
        self.playerDataDict[userProfile].IsKnockedDown = basket_list[34]
        self.playerDataDict[userProfile].IsAsleep = basket_list[35]
        self.playerDataDict[userProfile].IsFrozen = basket_list[36]
        self.playerDataDict[userProfile].IsUnkillable = basket_list[37]
        self.playerDataDict[userProfile].IsInvincible = basket_list[38]
        self.playerDataDict[userProfile].IsHacked = basket_list[39]
        self.playerDataDict[userProfile].IsRooted = basket_list[40]
        self.playerDataDict[userProfile].IsStunned = basket_list[41].rstrip()

    def finalBlows_stream_handler(self,basket_list): # set DeathBy ... 
        self.playerDataDict[basket_list[3]].DeathByPlayer = basket_list[2]
        self.playerDataDict[basket_list[3]].DeathByHero = self.playerDataDict[basket_list[2]].Hero
        self.playerDataDict[basket_list[3]].DeathByAbility = basket_list[4]
    
    def define_basket_list(self,line): # define basket list (delete [hh:mm:ss])
        basket_list = line[11:].split(',')
        basket_list[len(basket_list)-1] = basket_list[len(basket_list)-1].rstrip()
        return basket_list
    
    def boolean_handler(self, basket_list):
        if self.playerDataDict[basket_list[1]].IsAlive == 'True':
            self.playerDataDict[basket_list[1]].IsAlive = '1'
        elif self.playerDataDict[basket_list[1]].IsAlive == 'False':
            self.playerDataDict[basket_list[1]].IsAlive = '0'
        
        if self.playerDataDict[basket_list[1]].IsBurning == 'True':
            self.playerDataDict[basket_list[1]].IsBurning = '1'
        elif self.playerDataDict[basket_list[1]].IsBurning == 'False':
            self.playerDataDict[basket_list[1]].IsBurning = '0'
        
        if self.playerDataDict[basket_list[1]].IsKnockedDown == 'True':
            self.playerDataDict[basket_list[1]].IsKnockedDown = '1'
        elif self.playerDataDict[basket_list[1]].IsKnockedDown == 'False':
            self.playerDataDict[basket_list[1]].IsKnockedDown = '0'

        if self.playerDataDict[basket_list[1]].IsFrozen == 'True':
            self.playerDataDict[basket_list[1]].IsFrozen = '1'
        elif self.playerDataDict[basket_list[1]].IsFrozen == 'False':
            self.playerDataDict[basket_list[1]].IsFrozen = '0'
        
        if self.playerDataDict[basket_list[1]].IsUnkillable == 'True':
            self.playerDataDict[basket_list[1]].IsUnkillable = '1'
        elif self.playerDataDict[basket_list[1]].IsUnkillable== 'False':
            self.playerDataDict[basket_list[1]].IsUnkillable = '0'
        
        if self.playerDataDict[basket_list[1]].IsInvincible == 'False':
            self.playerDataDict[basket_list[1]].IsInvincible = '0'
        elif self.playerDataDict[basket_list[1]].IsInvincible == 'True':
            self.playerDataDict[basket_list[1]].IsInvincible = '1'

        if self.playerDataDict[basket_list[1]].IsAsleep == 'True':
            self.playerDataDict[basket_list[1]].IsAsleep = '1'
        elif self.playerDataDict[basket_list[1]].IsAsleep== 'False':
            self.playerDataDict[basket_list[1]].IsAsleep = '0'

        if self.playerDataDict[basket_list[1]].IsRooted == 'True':
            self.playerDataDict[basket_list[1]].IsRooted = '1'
        elif self.playerDataDict[basket_list[1]].IsRooted== 'False':
            self.playerDataDict[basket_list[1]].IsRooted = '0'        

        if self.playerDataDict[basket_list[1]].IsStunned == 'True':
            self.playerDataDict[basket_list[1]].IsStunned = '1'
        elif self.playerDataDict[basket_list[1]].IsStunned == 'False':
            self.playerDataDict[basket_list[1]].IsStunned = '0'        

        if self.playerDataDict[basket_list[1]].IsHacked == 'True':
            self.playerDataDict[basket_list[1]].IsHacked = '1'        
        elif self.playerDataDict[basket_list[1]].IsHacked == 'False':
            self.playerDataDict[basket_list[1]].IsHacked = '0'        

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

    def typeControl_stream_handler(self,basket_list): # set point if the map is Control type
        for i in range(0, 6):
            self.playerDataDict[self.playerList[i]].Point = basket_list[1]
            self.playerDataDict[self.playerList[i+6]].Point = basket_list[2]
        
    def typeOthers_stream_handler(self,basket_list): # set point if the map is not Control type
        if basket_list[1] != self.team1OffenseFlag and self.matchInfo.MapType != 'Control':
            self.sectionNumber = self.sectionNumber + 1
        if basket_list[1] == 'False':
            self.team1OffenseFlag = 'False'            
            for i in range(0, 6):
                self.playerDataDict[self.playerList[i+6]].Point = basket_list[2]
        elif basket_list[1] == 'True':
            self.team1OffenseFlag = 'True'
            for i in range(0, 6):
                self.playerDataDict[self.playerList[i]].Point = basket_list[2]
    
    def dupstart_stream_handler(self,basket_list): # handling duplicate - duplicate ON
        self.playerDataDict[basket_list[2]].DuplicateStatus = 'DUPLICATING'
        self.playerDataDict[basket_list[2]].DuplicatedHero = basket_list[3]
    
    def dupend_stream_handler(self,basket_list): # handling duplicate - duplicate OFF
        self.playerDataDict[basket_list[2]].DuplicateStatus = ''
        self.playerDataDict[basket_list[2]].DuplicatedHero = ''

    def resurrect_stream_handler(self, basket_list): # handling resurrect event
        self.playerDataDict[basket_list[2]].Resurrected = 'RESURRECTED'

    def resourceData_handler(self,basket_list):
        resourceData = ResourceData()
        resourceData.Player = basket_list[2]
        resourceData.Timestamp = self.playerDataDict[basket_list[2]].Timestamp
        resourceData.Team = self.playerDataDict[basket_list[2]].Team
        resourceData.Cooldown1 = self.playerDataDict[basket_list[2]].Cooldown1
        resourceData.Cooldown2 = self.playerDataDict[basket_list[2]].Cooldown2
        resourceData.CooldownCrouching = self.playerDataDict[basket_list[2]].CooldownCrouching
        resourceData.CooldownSecondaryFire = self.playerDataDict[basket_list[2]].CooldownSecondaryFire
        resourceData.UltimateCharge = self.playerDataDict[basket_list[2]].UltimateCharge
        resourceData.UltimatesEarned = self.playerDataDict[basket_list[2]].UltimatesEarned
        resourceData.UltimatesUsed = self.playerDataDict[basket_list[2]].UltimatesUsed
        resourceData.Point = self.playerDataDict[basket_list[2]].Point
        resourceData.MaxHealth = self.playerDataDict[basket_list[2]].MaxHealth
        resourceData.Position = self.playerDataDict[basket_list[2]].Position
        return resourceData


def main():
    args = sys.argv[1:]
    parser = LogHandler(args)
    parser.log_handler()
       
if __name__ == "__main__":
    main()