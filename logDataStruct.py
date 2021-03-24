import re
from dataclasses import dataclass

@dataclass 
class MatchInfo: #Information about current match (map, type, map section, team info)
    Map: str = ''
    MapType: str = ''
    RoundName: str = ''
    Section: str = ''
    Team_1: str = ''
    Team_2: str = ''
    Offense: str = ''
    Defense: str = ''

@dataclass
class PlayerData: #Player stat on csv
    Map: str = ''
    Section: str = ''
    Point: str = '0'
    RoundName: str = ''
    Timestamp: str = ''
    Team: str = ''
    Player: str = ''
    Hero: str = ''
    HeroDamageDealt: str = '0'
    BarrierDamageDealt: str = '0'
    DamageBlocked: str = '0'
    DamageTaken: str = '0'
    Deaths: str = '0'
    Eliminations: str = '0'
    FinalBlows: str = '0'
    EnvironmentalDeaths: str = '0'
    EnvironmentalKills: str = '0'
    HealingDealt: str = '0'
    ObjectiveKills: str = '0'
    SoloKills: str = '0'
    UltimatesEarned: str = '0'
    UltimatesUsed: str = '0'
    HealingReceived: str = '0'
    UltimateCharge: str = '0'
    Cooldown1: str = '0'
    Cooldown2: str = '0'
    CooldownSecondaryFire: str = '0'
    CooldownCrouching: str = '0'
    IsAlive: str = 'True'
    TimeElapsed: str = '0'
    Position: str = ''
    MaxHealth: str = '0'
    DeathByHero: str = ''
    DeathByAbility: str = ''
    DeathByPlayer: str = ''
    Resurrected: str = ''
    DuplicatedHero: str = ''
    DuplicateStatus: str = ''
    Health: str = ''
    DefensiveAssists: str = '0'
    OffensiveAssists: str = '0'
    IsBurning: str = '0'
    IsKnockedDown: str = '0'
    IsAsleep: str = '0'
    IsFrozen: str = '0'
    IsUnkillable: str = '0'
    IsInvincible: str = '0'
    IsRooted: str = '0'
    IsStunned: str = '0'
    IsHacked: str = '0'


class LogPattern: # Regex log patterns
    def __init__(self):
        self.pattern_dupstart = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(DuplicatingStart),(\w*),(\w*)')
        self.pattern_dupend = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(DuplicatingEnd),(\w*)')
        self.pattern_resurrect = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(Resurrected),(\w*)')
        self.pattern_finalblows = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(FinalBlow),(\w*),(\w*),(\w*\s*\w*)')
        self.pattern_suicide = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(Suicide),(\w*)')
        self.pattern_matchInfo = re.compile('(\[(.*?)\])\s(\w*\s*\w*\s*\w*|Watchpoint: Gibraltar|King\'s Row),(\w*\s*\w*),(\w*\s*\w*),(\d)')
        self.pattern_playerInfo = re.compile('(\[(.*?)\])\s(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76),(\w*|Soldier: 76)')
        self.pattern_typeControl = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+)')
        self.pattern_typeOthers = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(True|False),(\d*\.?\d+)')
        self.pattern_playerData = re.compile('(\[(.*?)\])\s(\d*\.?\d+),(\w*),(\w*\s*\w*|Soldier: 76|D.Va),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+),(\W[-]?(\d*\.?\d+), [-]?(\d*\.?\d+), [-]?(\d*\.?\d+)\W),(\w*\s*\w*),(\d*\.?\d+),(\d*\.?\d+),(\d*\.?\d+)')
