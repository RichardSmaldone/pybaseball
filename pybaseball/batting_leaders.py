import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

import pybaseball.datasources.fangraphs as fangraphs

_FG_BATTING_LEADERS_TYPES = "c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,-1"
_FG_BATTING_LEADERS_URL = "/leaders.aspx?pos=all&stats=bat&lg={league}&qual={qual}&type={types}&season={end_season}&month=0&season1={start_season}&ind={ind}&team=&rost=&age=&filter=&players=&page=1_100000"
# TODO: update url to include more stats


def batting_stats(start_season: int, end_season: int = None, league: str = 'all', qual: int = 1, ind: int = 1):
    if start_season is None:
        raise ValueError(
            "You need to provide at least one season to collect data for. Try batting_leaders(season) or batting_leaders(start_season, end_season)."
        )
    if end_season is None:
        end_season = start_season

    column_mapper = BattingStatsColumnMapper()

    fg_data = fangraphs.get_fangraphs_tabular_data_from_url(
        _FG_BATTING_LEADERS_URL.format(
            league=league,
            qual=qual,
            types=_FG_BATTING_LEADERS_TYPES,
            end_season=end_season,
            start_season=start_season,
            ind=ind
        ),
        column_name_mapper=column_mapper.map,
        known_percentages = ['GB/FB']
    )

    return fg_data.sort_values(['WAR', 'OPS'], ascending=False)


class BattingStatsColumnMapper:
    def __init__(self):
        self.call_counts = {}

    def map(self, column_name):
        self.call_counts[column_name] = self.call_counts.get(column_name, 0) + 1
        # First time around use the actual column name
        if self.call_counts[column_name] == 1:
            return column_name

        # Rename the second FB% column
        if column_name == 'FB%' and self.call_counts[column_name] == 2:
            return 'FB% (Pitch)'

        # Just tack on a number for other calls
        return column_name + " " + str(self.call_counts[column_name])
