from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class DatasetBundle:
    fifa: pd.DataFrame
    movies: pd.DataFrame
    social: pd.DataFrame


def load_csv(path: Path, **kwargs: object) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def load_datasets(fifa_path: Path, movie_path: Path, social_path: Path) -> DatasetBundle:
    fifa = load_csv(fifa_path)
    movies = load_csv(movie_path, engine="python", on_bad_lines="skip")
    social = load_csv(social_path)
    return DatasetBundle(fifa=fifa, movies=movies, social=social)
