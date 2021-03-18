import re
import sys
from dataclasses import dataclass

@dataclass 
class MatchInfo: #Information about current match (map, type, map section, team info)
    Map: str = ''
    MapType: str = ''
    Section: int = 0
    Team_1: str = ''
    Team_2: str = ''

@dataclass
class PlayerData: #Player stat on csv
    Map: str = ''
    Section: int = 0
    Timestamp: int = 0
    Team: str = ''
    Player: str = ''
    Hero: str = ''
    HeroDamageDone: float = 0.0
    BarrierDamageDone: float = 0.0
    DamageBlocked: float = 0.0
    DamageTaken: float = 0.0
    Deaths: int = 0
    Eliminations: int = 0
    FinalBlow: int = 0
    EnvironmentalDeaths: int = 0
    EnvironmentalKills: int = 0
    HealingDealt: float = 0.0
    ObjectiveKills: int = 0
    SoloKills: int = 0
    UltimatesEarned: int = 0
    UltimatesUsed: int = 0
    HealingReceived: float = 0.0
    UltimateCharge: int = 0
    PlayerClosest: str = ''
    Cooldown1: float = 0.0
    Cooldown2: float = 0.0
    Position: str = ''


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
        self.team1_players = []
        self.team2_players = []

    def get_file_name(self):
        print('Log File Name : ', self.logFile)
        print('Csv File Name : ', self.csvFile)

    def get_match_info(self):
        print('matchInfo : ', self.matchInfo)

    def get_players(self):
        print(self.matchInfo.Team_1,'Players : ', self.team1_players)
        print(self.matchInfo.Team_2,'Players : ', self.team2_players)

    def log_handler(self):
        with open(self.logFile) as fd:
            basket_list = []
            for line in fd.readlines():
                if self.logpattern.pattern_matchInfo.match(line):
                    basket_list = line[11:].split(',')
                    self.matchInfo.Map = basket_list[0]
                    self.matchInfo.Team_1 = basket_list[1]
                    self.matchInfo.Team_2 = basket_list[2]
                    self.matchInfo.Section = basket_list[3]
                elif self.logpattern.pattern_playerInfo.match(line):
                    basket_list = line[11:].split(',')
                    for i in range(0, len(basket_list)):
                        if i <= 5:
                            self.team1_players.append(basket_list[i])
                        else:
                            self.team2_players.append(basket_list[i])                                    
    
    def map_type_setter(self):
        if self.matchInfo.Map in Maps.control:
            self.matchInfo.MapType = 'Control'
        elif self.matchInfo.Map in Maps.assault:
            self.matchInfo.MapType = 'Assault'
        elif self.matchInfo.Map in Maps.hybrid:
            self.matchInfo.MapType = 'Hybrid'
        elif self.matchInfo.Map in Maps.escort:
            self.matchInfo.MapType = 'Escort'
                
def main():
    args = sys.argv[1:]
    parser = LogParser(args)
    parser.log_handler()   
       
if __name__ == "__main__":
    main()