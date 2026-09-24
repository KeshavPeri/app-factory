"""FPL's own ep_next as a pre-deadline benchmark (MODEL-DIAGNOSIS-2026-09-24.md §4f).

The FPL-Core-Insights GW-g snapshot is taken at the END of gameweek g, so its ep_this/form already
include GW g. The honest pre-deadline forecast for GW g is ep_next from the GW g-1 file.
"""
import os
import urllib.request

import pandas as pd
from scipy.stats import spearmanr

SHA = '392f79ad85fcbe5c47b8f1e33d6c3dc787dcfd53'
BASE = f'https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/{SHA}/data/2025-2026/By%20Gameweek'
CACHE = os.environ.get('DATA_DIR', 'cache')
os.makedirs(CACHE, exist_ok=True)
frames = []
for gw in range(1, 39):
    path = os.path.join(CACHE, f'core_2526_pgs_{gw}.csv')
    if not os.path.exists(path):
        urllib.request.urlretrieve(f'{BASE}/GW{gw}/player_gameweek_stats.csv', path)
    frames.append(pd.read_csv(path, low_memory=False))
c = pd.concat(frames, ignore_index=True).sort_values(['id', 'gw'])
c['prev_ep_next'] = c.groupby('id')['ep_next'].shift(1)
c['prev_points'] = c.groupby('id')['event_points'].shift(1)
f = c[(c.minutes > 0) & (c.gw >= 2)]
for col in ['prev_ep_next', 'ep_this', 'form']:
    ok = f[[col, 'event_points', 'prev_points']].dropna()
    print('%-13s vs this GW %.3f | vs previous GW %.3f  n=%d' % (
        col, spearmanr(ok[col], ok.event_points).statistic, spearmanr(ok[col], ok.prev_points).statistic, len(ok)))
