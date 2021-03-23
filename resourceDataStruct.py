import re
from dataclasses import dataclass

@dataclass
class ResourceData:
    Timestamp: str='0'
    Player: str='0'
    Team: str='0'
    Cooldown1: str = '0'
    Cooldown2: str = '0'
    CooldownSecondaryFire: str = '0'
    CooldownCrouching: str = '0'
    UltimateCharging: str = '0'
    UltimateEarned: str = '0'
    UltimateUsed: str = '0'
    Point: str = '0'
    MaxHealth: str = '0'
    Position: str = ''