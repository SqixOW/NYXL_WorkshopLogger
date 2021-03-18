import re
import sys
from dataclasses import dataclass

@dataclass 
class MatchInfo: #Information about current match (map, type, map section, team info)
    Map: str = ''
    MapType: str = ''
    Section: str = ''
    Team_1: str = ''
    Team_2: str = ''
    Offense: str = ''
    Defense: str = ''
    Team1_Percent: str =''
    Team2_Percent: str =''    

@dataclass
class PlayerData: #Player stat on csv
    Map: str = ''
    Section: str = ''
    Timestamp: str = ''
    Team: str = ''
    Player: str = ''
    Hero: str = ''
    HeroDamageDone: str = ''
    BarrierDamageDone: str = ''
    DamageBlocked: str = ''
    DamageTaken: str = ''
    Deaths: str = ''
    Eliminations: str = ''
    FinalBlow: str = ''
    EnvironmentalDeaths: str = ''
    EnvironmentalKills: str = ''
    HealingDealt: str = ''
    ObjectiveKills: str = ''
    SoloKills: str = ''
    UltimatesEarned: str = ''
    UltimatesUsed: str = ''
    HealingReceived: str = ''
    UltimateCharge: str = ''
    PlayerClosest: str = ''
    Cooldown1: str = ''
    Cooldown2: str = ''
    Position: str = ''
    MaxHealth: str = ''


class LogPattern: # Regex log patterns
    def __init__(self):
        self.pattern_dupstart = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(DuplicatingStart),(\w*),(\w*)')
        self.pattern_dupend = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(DuplicatingEnd),(\w*),(\w*)')
        self.pattern_resurrect = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(Resurrected),(\w*)')
        self.pattern_finalblow = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(FinalBlow),(\w*),(\w*),(\w*\s*\w*)')
        self.pattern_suicide = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(Suicide),(\w*)')
        self.pattern_matchInfo = re.compile('(\[(.*?)\])\s(\w*\s*\w*\s*\w*|Watchpoint: Gibraltar|King\'s Row),(\w*\s*\w*),(\w*\s*\w*),(\d)')
        self.pattern_playerInfo = re.compile('(\[(.*?)\])\s(\w*),(\w*),(\w*),(\w*),(\w*),(\w*),(\w*),(\w*),(\w*),(\w*),(\w*),(\w*)')
        self.pattern_typeControl = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+)')
        self.pattern_typeOthers = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(True|False),(\d*\.?\d+)')
        self.pattern_playerData = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(\w*),(\w*\s*\w*|Soldier: 76),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\w*),(\W[-]?(\d*\.?\d+), [-]?(\d*\.?\d+), [-]?(\d*\.?\d+)\W),(\w*\s*\w*),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+)')

class Controls: # Control map subtitles
    def __init__(self):
        self.ilios = ['Lighthouse','Well','Ruins']
        self.lijang_tower = ['Night Market','Garden','Control Tower']
        self.nepal = ['Village', 'Shrine', 'Sanctum']
        self.oasis = ['City Center', 'Gardens', 'University']
        self.busan = ['Sanctuary', 'Downtown', 'Meka Base']

class Maps: # Map types and the name of maps
    def __init__(self):
        self.control = ['Ilios', 'Lijiang Tower', 'Nepal', 'Oasis', 'Busan']
        self.assault = ['Horizon Lunar Colony', 'Temple of Anubis', 'Volskaya Industries', 'Paris', 'Hanamura']
        self.hybrid = ['King\'s Row', 'Eichenwalde', 'Numbani', 'Hollywood', 'Blizzard World']
        self.escort = ['Route 66', 'Watchpoint: Gibraltar', 'Dorado', 'Rialto', 'Havana', 'Junkertown']
        
class LogHandler: # Log Parsing & Handling
    def __init__(self, args):
        self.logFile = args[0]
        self.csvFile = args[0].replace('.txt','.csv')
        self.logpattern = LogPattern()
        self.matchInfo = MatchInfo()
        self.playerList = []
        self.Maps = Maps()
        self.team1_players = [PlayerData(),PlayerData(),PlayerData(),PlayerData(),PlayerData(),PlayerData()]
        self.team2_players = [PlayerData(),PlayerData(),PlayerData(),PlayerData(),PlayerData(),PlayerData()]

    def get_file_name(self):
        print('Log File Name : ', self.logFile)
        print('Csv File Name : ', self.csvFile)

    def get_match_info(self):
        print('matchInfo : ', self.matchInfo)

    def get_players(self):
        for i in range(0, 6):
            print(self.matchInfo.Team_1,'Players : ', self.team1_players[i].Player)
        for i in range(0, 6):
            print(self.matchInfo.Team_2,'Players : ', self.team2_players[i].Player)

    def log_handler(self):
        with open(self.logFile) as fd:
            basket_list = []
            for line in fd.readlines():

                if self.logpattern.pattern_matchInfo.match(line):       # pattern 1 : MatchInfo
                    basket_list = line[11:].split(',')
                    self.matchInfo.Map = basket_list[0]
                    self.matchInfo.Team_1 = basket_list[1]
                    self.matchInfo.Team_2 = basket_list[2]
                    self.matchInfo.Section = basket_list[3]
                    self.map_type_setter()

                elif self.logpattern.pattern_playerInfo.match(line):    # pattern 2 : PlayerInfo
                    basket_list = line[11:].split(',')
                    basket_list[11] = basket_list[11].rstrip()
                    self.playerList = basket_list
                    print(self.playerList)
                    for i in range(0, len(basket_list)):
                        if i <= 5:
                            self.team1_players[i%6].Player = basket_list[i]
                            self.team1_players[i%6].Map = self.matchInfo.Map
                            self.team1_players[i%6].Section = self.matchInfo.Section
                            self.team1_players[i%6].Team = self.matchInfo.Team_1
                        else:
                            self.team2_players[i%6].Player = basket_list[i]
                            self.team2_players[i%6].Map = self.matchInfo.Map
                            self.team2_players[i%6].Section = self.matchInfo.Section
                            self.team2_players[i%6].Team = self.matchInfo.Team_2

                elif self.logpattern.pattern_playerData.match(line):    # pattern 3 : Player Match data
                    basket_list = line[11:].split(',')                    
                    print(basket_list[1])
                    idx = self.playerList.index(basket_list[1])
                    if idx > 5 :
                        self.team2_players[idx%6].Timestamp = basket_list[0]
                        self.team2_players[idx%6].Hero = basket_list[2]
                        self.team2_players[idx%6].HeroDamageDone = basket_list[3]
                        self.team2_players[idx%6].BarrierDamageDone = basket_list[4]
                        self.team2_players[idx%6].DamageBlocked = basket_list[5]
                        self.team2_players[idx%6].DamageTaken = basket_list[6]
                        self.team2_players[idx%6].Deaths = basket_list[7]
                        self.team2_players[idx%6].Eliminations = basket_list[8]
                        self.team2_players[idx%6].FinalBlow = basket_list[9]
                        self.team2_players[idx%6].EnvironmentalDeaths = basket_list[10]
                        self.team2_players[idx%6].EnvironmentalKills = basket_list[11]
                        self.team2_players[idx%6].HealingDealt = basket_list[12]
                        self.team2_players[idx%6].ObjectiveKills = basket_list[13]
                        self.team2_players[idx%6].SoloKills = basket_list[14]
                        self.team2_players[idx%6].UltimatesEarned = basket_list[15]
                        self.team2_players[idx%6].UltimatesUsed = basket_list[16]
                        self.team2_players[idx%6].HealingReceived = basket_list[17]
                        self.team2_players[idx%6].UltimateCharge = basket_list[18]
                        self.team2_players[idx%6].PlayerClosest = basket_list[19]
                        self.team2_players[idx%6].Position = basket_list[20] + ',' + basket_list[21] + ',' + basket_list[22]
                        self.team2_players[idx%6].Cooldown1 = basket_list[24]
                        self.team2_players[idx%6].Cooldown2 = basket_list[25]
                        self.team2_players[idx%6].MaxHealth = basket_list[26].rstrip()
                        print(self.team2_players[idx%6])
                    else :
                        self.team1_players[idx].Timestamp = basket_list[0]
                        self.team1_players[idx].Hero = basket_list[2]
                        self.team1_players[idx].HeroDamageDone = basket_list[3]
                        self.team1_players[idx].BarrierDamageDone = basket_list[4]
                        self.team1_players[idx].DamageBlocked = basket_list[5]
                        self.team1_players[idx].DamageTaken = basket_list[6]
                        self.team1_players[idx].Deaths = basket_list[7]
                        self.team1_players[idx].Eliminations = basket_list[8]
                        self.team1_players[idx].FinalBlow = basket_list[9]
                        self.team1_players[idx].EnvironmentalDeaths = basket_list[10]
                        self.team1_players[idx].EnvironmentalKills = basket_list[11]
                        self.team1_players[idx].HealingDealt = basket_list[12]
                        self.team1_players[idx].ObjectiveKills = basket_list[13]
                        self.team1_players[idx].SoloKills = basket_list[14]
                        self.team1_players[idx].UltimatesEarned = basket_list[15]
                        self.team1_players[idx].UltimatesUsed = basket_list[16]
                        self.team1_players[idx].HealingReceived = basket_list[17]
                        self.team1_players[idx].UltimateCharge = basket_list[18]
                        self.team1_players[idx].PlayerClosest = basket_list[19]
                        self.team1_players[idx].Position = basket_list[20] + ',' + basket_list[21] + ',' + basket_list[22]
                        self.team1_players[idx].Cooldown1 = basket_list[24]
                        self.team1_players[idx].Cooldown2 = basket_list[25]
                        self.team1_players[idx].MaxHealth = basket_list[26].rstrip()
                        print(self.team1_players[idx])
                    if basket_list[1] == 'YaHo2':
                        break
                                    
    
    def map_type_setter(self):
        if self.matchInfo.Map in self.Maps.control:
            self.matchInfo.MapType = 'Control'
        elif self.matchInfo.Map in self.Maps.assault:
            self.matchInfo.MapType = 'Assault'
        elif self.matchInfo.Map in self.Maps.hybrid:
            self.matchInfo.MapType = 'Hybrid'
        elif self.matchInfo.Map in self.Maps.escort:
            self.matchInfo.MapType = 'Escort'
                
def main():
    args = sys.argv[1:]
    parser = LogHandler(args)
    parser.log_handler()
       
if __name__ == "__main__":
    main()