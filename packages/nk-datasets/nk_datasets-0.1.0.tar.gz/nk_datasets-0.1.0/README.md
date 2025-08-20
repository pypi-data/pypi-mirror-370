# NK_datasets

NK_datasets ships standardized datasets for **NPB** (Nippon Professional Baseball) and **KBO** (Korea Baseball Organization), packaged with pandas loaders.  
It also includes MLB players who have played in either NPB, KBO, or both.

- NPB data was scraped from the official [NPB website](https://npb.jp/eng/) and [npbstats.com](http://npbstats.com/eng/).
- KBO data was scraped from the official [KBO website](https://www.koreabaseball.com/).
- MLB alignment is partial; meaning only players who appeared in KBO/NPB are included. It was sourced from [Lahman Database](https://sabr.org/lahman-database/).

## Requirements

- Python 3.9+
- pandas 1.5+

## Install

```bash
pip install nk_datasets
```

## Import

```bash
import nk
```

All Datasets are grouped into the following collections:

- **kbo_npb** – KBO/NPB league tables:
  `load_kbo_batting()`, `load_kbo_pitching()`, `load_kbo_fielding()`, ` load_kbo_people()``load_npb_batting() `, `load_npb_pitching()`, `load_npb_fielding()`, `load_npb_people()`

- **kbo_npb_mlb** – KBO/NPB/MLB league tables with aligned columns for direct comparison across all 3 leagues:
  `load_kbo_batting_aligned()`, `load_kbo_pitching_aligned()`, `load_kbo_fielding_aligned()`, `load_kbo_people_aligned()`, `load_npb_batting_aligned()`, `load_npb_pitching_aligned()`, `load_npb_fielding_aligned()`, `load_npb_people_aligned()`, `load_mlb_batting_aligned()`, `load_mlb_pitching_aligned()`, `load_mlb_fielding_aligned()`, `load_mlb_people_aligned()`

- **nk_merged** – "wide" merged tables (combined schema across KBO and NPB):
  `load_nk_batting()`, `load_nk_pitching()`, `load_nk_fielding()`, `load_nk_people()`, `load_nk_league()`, `load_nk_team()`, `load_nk_merged_people()`

- **nk_merged_tall** – "tall" player stats, split by league/data slice:
  `load_nk_playerstats_KBO()`, `load_nk_playerstats_PL()`, `load_nk_playerstats_CL()`, `load_nk_playerstats_JBL()`, `load_nk_league()`, `load_nk_team()`, `load_nk_stats()`

## Short Snippet

```bash
import nk_datasets as nk

# load nk_merged batting table
df = nk.load_nk_batting()

# show first rows
print(df.head())
```

## License

MIT License © Myungkeun Park
