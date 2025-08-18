"""
mteam - M-TEAM API 客户端
"""

from .client import MTeamClient
from .exceptions import MTeamException, APIError
from . import torrent
from . import member
from . import subtitle

__version__ = "0.1.0"
__all__ = [
    'MTeamClient',
    'MTeamException',
    'APIError',
    'torrent',
    'member',
    'subtitle',
] 