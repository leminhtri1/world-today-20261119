# The World Today: 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/leminhtri1/world-today-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/leminhtri1/world-today-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

An entry for make.fun's bounty [*Sum up 19 November's world news in one image*](https://make.fun/bounty/news-image-20261119)
(`news-image-20261119`).

- `build.py` draws `entry.png` (1024×1024) with Pillow: a date masthead, a region bar,
  a drawn illustration of the Shenzhen summit, eight story cells with drawn icons, a
  numbered world map and 14 numbered briefs, 23 stories from 19 November 2026 in all,
  with a date-check footer naming the sources. Fonts are Georgia and Arial from the
  system font folder (not included in this repository).
- `main.py` (Python 3.13, standard library only) copies `entry.png` to
  `/output/entry.png`.

```sh
python build.py   # regenerate entry.png (needs Pillow)
python main.py    # writes /output/entry.png
```

MIT licensed.
