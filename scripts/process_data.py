from __future__ import annotations

import argparse
import json
import logging
import math
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from geopy.exc import GeocoderServiceError, GeopyError
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DOCS_DATA_DIR = ROOT / "docs" / "data"
GROUP_STAGE_CSV_CANDIDATES = (
    RAW_DIR / "group_stage.csv",
    RAW_DIR / "fifaworldcup2026-groupstage.csv",
)
TEAM_ORIGINS_CSV_CANDIDATES = (
    RAW_DIR / "team_origins.csv",
    RAW_DIR / "fifaworldcup2026-basecamps.csv",
)
OUTPUT_JSON = PROCESSED_DIR / "travel_distances.json"
DOCS_JSON = DOCS_DATA_DIR / "travel_distances.json"

AIRPORT_FILTERS = {
    "type": ["large_airport", "medium_airport"],
    "has_scheduled_service": True,
}

TEAM_ALIASES = {
    "cabo verde": "Cape Verde",
    "cape verde": "Cape Verde",
    "cote d'ivoire": "Ivory Coast",
    "ivory coast": "Ivory Coast",
    "iran": "IR Iran",
    "czechia": "Czech Republic",
    "korea republic": "South Korea",
    "korea, republic of": "South Korea",
    "korea republic of": "South Korea",
    "usa": "United States",
    "united states of america": "United States",
    "usa (us)": "United States",
}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )


def slugify_column(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("/", " ")
        .replace("-", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace(".", " ")
        .replace(",", " ")
        .replace("  ", " ")
        .replace(" ", "_")
    )


def normalize_team_name(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    return TEAM_ALIASES.get(text.lower(), text)


def normalize_location_text(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    return " ".join(text.split())


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input file: {path}")
    frame = pd.read_csv(path)
    frame.columns = [slugify_column(column) for column in frame.columns]
    return frame


def resolve_input_file(candidates: Iterable[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    joined = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Missing required input file. Looked for: {joined}")


def pick_column(frame: pd.DataFrame, candidates: Iterable[str]) -> str:
    available = set(frame.columns)
    for candidate in candidates:
        normalized = slugify_column(candidate)
        if normalized in available:
            return normalized
    raise KeyError(f"Could not find any of these columns: {', '.join(candidates)}")


@dataclass(slots=True)
class AirportLookup:
    iata: str
    name: str | None = None
    city: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    raw: Any = None


@dataclass(slots=True)
class TeamOrigin:
    training_site: str
    airport: AirportLookup


class AirportBackend:
    def __init__(self) -> None:
        self.module = self._import_module()
        self.backend = self.module
        self.airports = getattr(self.module, "airports", [])

    def _import_module(self):
        candidates = ("airports.airport_data", "airports", "airports_py", "airport_data")
        for module_name in candidates:
            try:
                return import_module(module_name)
            except ModuleNotFoundError:
                continue
        raise ModuleNotFoundError(
            "Could not import airports-py. Install the project dependencies with uv."
        )

    def _call_backend(self, method_names: Iterable[str], *args, **kwargs):
        for method_name in method_names:
            method = getattr(self.backend, method_name, None)
            if callable(method):
                try:
                    return method(*args, **kwargs)
                except TypeError:
                    # Some versions may not accept keyword filters.
                    if kwargs:
                        return method(*args)
                    raise
        raise AttributeError(f"Backend does not expose any of: {', '.join(method_names)}")

    def find_nearest_airport(
        self, latitude: float, longitude: float, filters: dict[str, Any] | None = None
    ) -> AirportLookup | None:
        allowed_types = None
        scheduled_required = None
        other_filters: dict[str, Any] = {}
        if filters:
            raw_types = filters.get("type")
            if isinstance(raw_types, (list, tuple, set)):
                allowed_types = {str(item) for item in raw_types}
            elif raw_types:
                allowed_types = {str(raw_types)}
            if "has_scheduled_service" in filters:
                scheduled_required = bool(filters["has_scheduled_service"])
            other_filters = {key: value for key, value in filters.items() if key not in {"type", "has_scheduled_service"}}

        nearest_airport = None
        min_distance = float("inf")
        for airport in self.airports:
            if not str(airport.get("iata", "")).strip():
                continue
            airport_lat = _coerce_float(airport.get("latitude"))
            airport_lon = _coerce_float(airport.get("longitude"))
            if airport_lat is None or airport_lon is None:
                continue
            if allowed_types is not None and str(airport.get("type")) not in allowed_types:
                continue
            if scheduled_required is not None:
                scheduled = airport.get("scheduled_service")
                scheduled_bool = str(scheduled).upper() == "TRUE" if isinstance(scheduled, str) else bool(scheduled)
                if scheduled_bool != scheduled_required:
                    continue
            if other_filters:
                matched = True
                for key, value in other_filters.items():
                    if airport.get(key) != value:
                        matched = False
                        break
                if not matched:
                    continue

            distance = haversine_coords(latitude, longitude, airport_lat, airport_lon)
            if distance < min_distance:
                min_distance = distance
                nearest_airport = {
                    **airport,
                    "distance": round(distance, 2),
                }

        return self._normalize_airport_result(nearest_airport)

    def calculate_distance(self, origin_iata: str, destination_iata: str) -> float:
        try:
            result = self._call_backend(
                ("calculate_distance", "distance", "get_distance"),
                origin_iata,
                destination_iata,
            )
            if result is None:
                raise ValueError("Distance lookup returned no result")
            return float(result)
        except Exception:
            origin = self.lookup_airport(origin_iata)
            destination = self.lookup_airport(destination_iata)
            fallback = haversine_km(origin, destination) if origin and destination else None
            if fallback is None:
                raise
            return float(fallback)

    def lookup_airport(self, iata: str) -> AirportLookup | None:
        method_names = ("get_airport_by_iata", "airport_by_iata", "lookup_airport", "get_airport")
        result = None
        for method_name in method_names:
            method = getattr(self.backend, method_name, None)
            if not callable(method):
                continue
            result = method(iata)
            break
        return self._normalize_airport_result(result)

    @staticmethod
    def _normalize_airport_result(result: Any) -> AirportLookup | None:
        if result is None:
            return None
        if isinstance(result, list):
            if not result:
                return None
            result = result[0]
        if isinstance(result, AirportLookup):
            return result
        if isinstance(result, dict):
            iata = result.get("iata") or result.get("iata_code") or result.get("code")
            if not iata:
                return None
            return AirportLookup(
                iata=str(iata),
                name=result.get("name"),
                city=result.get("city"),
                country=result.get("country"),
                latitude=_coerce_float(result.get("latitude") or result.get("lat")),
                longitude=_coerce_float(result.get("longitude") or result.get("lon") or result.get("lng")),
                raw=result,
            )
        iata = getattr(result, "iata", None) or getattr(result, "iata_code", None) or getattr(result, "code", None)
        if not iata:
            return None
        return AirportLookup(
            iata=str(iata),
            name=getattr(result, "name", None),
            city=getattr(result, "city", None),
            country=getattr(result, "country", None),
            latitude=_coerce_float(getattr(result, "latitude", None) or getattr(result, "lat", None)),
            longitude=_coerce_float(getattr(result, "longitude", None) or getattr(result, "lon", None)),
            raw=result,
        )


def _coerce_float(value: Any) -> float | None:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def haversine_km(origin: AirportLookup, destination: AirportLookup) -> float | None:
    if origin.latitude is None or origin.longitude is None:
        return None
    if destination.latitude is None or destination.longitude is None:
        return None
    radius_km = 6371.0
    lat1 = math.radians(origin.latitude)
    lon1 = math.radians(origin.longitude)
    lat2 = math.radians(destination.latitude)
    lon2 = math.radians(destination.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(a))


def haversine_coords(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(a))


def normalize_text_tokens(value: str) -> list[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in value)
    return [token for token in cleaned.split() if len(token) >= 3]


class GeoResolver:
    def __init__(self) -> None:
        user_agent = os.environ.get("NOMINATIM_USER_AGENT", "worldcup2026-travel-distance")
        self.geocoder = Nominatim(user_agent=user_agent, timeout=10)
        self.geocode = RateLimiter(
            self.geocoder.geocode,
            min_delay_seconds=0,
            max_retries=0,
            swallow_exceptions=True,
            return_value_on_exception=None,
        )
        self.disabled = False
        self._warned_disabled = False

    def geocode_text(self, text: str) -> tuple[float, float] | None:
        if not text:
            return None
        if self.disabled:
            return None
        try:
            location = self.geocode(text)
        except (GeocoderServiceError, GeopyError):
            self.disabled = True
            if not self._warned_disabled:
                logging.warning("Nominatim geocoding is rate-limited; using offline airport fallback.")
                self._warned_disabled = True
            return None
        if location is None:
            self.disabled = True
            if not self._warned_disabled:
                logging.warning("Nominatim geocoding returned no result; using offline airport fallback.")
                self._warned_disabled = True
            return None
        return float(location.latitude), float(location.longitude)


def venue_candidates(row: pd.Series) -> list[str]:
    venue = normalize_location_text(row.get("venue"))
    city = normalize_location_text(row.get("city"))
    raw_candidates = [
        city,
        f"{venue}, {city}" if venue and city else "",
        venue,
        row.get("venue_name"),
        row.get("stadium"),
        row.get("match_venue"),
        row.get("venue_city"),
        row.get("match_city"),
    ]
    seen: set[str] = set()
    values: list[str] = []
    for candidate in raw_candidates:
        text = normalize_location_text(candidate)
        if text and text.lower() not in seen:
            seen.add(text.lower())
            values.append(text)
    return values


def training_site_candidates(row: pd.Series) -> list[str]:
    training_site = normalize_location_text(row.get("training_site"))
    city = normalize_location_text(row.get("city"))
    team = normalize_location_text(row.get("team"))
    raw_candidates = [
        f"{training_site}, {city}" if training_site and city else "",
        f"{team} {training_site}" if team and training_site else "",
        training_site,
        row.get("training_site_name"),
        row.get("camp"),
        row.get("origin"),
        row.get("training_base"),
        city,
    ]
    seen: set[str] = set()
    values: list[str] = []
    for candidate in raw_candidates:
        text = normalize_location_text(candidate)
        if text and text.lower() not in seen:
            seen.add(text.lower())
            values.append(text)
    return values


def geocode_with_cache(
    resolver: GeoResolver,
    key: str,
    candidates: list[str],
    cache: dict[str, tuple[float, float] | None],
    label: str,
) -> tuple[float, float] | None:
    if key in cache:
        return cache[key]
    for candidate in candidates:
        coords = resolver.geocode_text(candidate)
        if coords:
            cache[key] = coords
            return coords
    logging.warning("Could not geocode %s: %s", label, key)
    cache[key] = None
    return None


def lookup_airport_with_cache(
    backend: AirportBackend,
    coords: tuple[float, float] | None,
    cache: dict[str, AirportLookup | None],
    cache_key: str,
    label: str,
    candidates: list[str] | None = None,
) -> AirportLookup | None:
    if cache_key in cache:
        return cache[cache_key]
    if coords is None:
        airport = None
    else:
        airport = backend.find_nearest_airport(coords[0], coords[1], filters=AIRPORT_FILTERS)
    if airport is None and candidates:
        airport = lookup_airport_by_text(backend, candidates)
    if airport is None:
        if coords is None:
            logging.warning("Skipping airport lookup for %s because coordinates are missing", label)
        else:
            logging.warning("Could not map %s to a commercial airport", label)
    cache[cache_key] = airport
    return airport


def lookup_airport_by_text(backend: AirportBackend, candidates: list[str]) -> AirportLookup | None:
    airport_rows = backend.airports
    best_row: dict[str, Any] | None = None
    best_score = -1.0

    for candidate in candidates:
        query = normalize_location_text(candidate).lower()
        if not query:
            continue
        query_tokens = normalize_text_tokens(query)
        for airport in airport_rows:
            iata = str(airport.get("iata", "")).strip()
            if not iata:
                continue
            airport_type = str(airport.get("type", "")).lower()
            if airport_type not in {"large_airport", "medium_airport"}:
                continue
            scheduled = airport.get("scheduled_service")
            scheduled_bool = str(scheduled).upper() == "TRUE" if isinstance(scheduled, str) else bool(scheduled)
            if not scheduled_bool:
                continue
            city = normalize_location_text(airport.get("city") or "").lower()
            name = normalize_location_text(airport.get("airport") or "").lower()
            score = 0.0
            if query == city or query == name:
                score += 100.0
            if query in city or city in query:
                score += 60.0
            if query in name or name in query:
                score += 60.0
            for token in query_tokens:
                if token in city:
                    score += 8.0
                if token in name:
                    score += 6.0
            if airport_type == "large_airport":
                score += 10.0
            if score > best_score:
                best_score = score
                best_row = airport

    return AirportBackend._normalize_airport_result(best_row)


def ensure_directories() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_team_origin_lookup(
    origins: pd.DataFrame,
    geo_resolver: GeoResolver,
    airport_backend: AirportBackend,
) -> dict[str, TeamOrigin]:
    team_col = pick_column(origins, ["team", "team_name", "country"])
    site_col = pick_column(origins, ["training_site", "training site", "origin", "camp"])
    city_col = pick_column(origins, ["city", "training_city", "camp_city"])

    geo_cache: dict[str, tuple[float, float] | None] = {}
    airport_cache: dict[str, AirportLookup | None] = {}
    lookup: dict[str, TeamOrigin] = {}

    for _, row in origins.iterrows():
        team = normalize_team_name(row.get(team_col))
        training_site = normalize_location_text(row.get(site_col))
        city = normalize_location_text(row.get(city_col))
        if not team or not training_site:
            continue
        cache_key = f"{team.lower()}|{training_site.lower()}|{city.lower()}"
        coords = geocode_with_cache(
            geo_resolver,
            cache_key,
            training_site_candidates(pd.Series({"training_site": training_site, "city": city, "team": team})),
            geo_cache,
            f"training site for {team}",
        )
        airport = lookup_airport_with_cache(
            airport_backend,
            coords,
            airport_cache,
            f"training:{cache_key}",
            f"training site for {team}",
            training_site_candidates(pd.Series({"training_site": training_site, "city": city, "team": team})),
        )
        if airport:
            lookup[team] = TeamOrigin(training_site=training_site, airport=airport)

    return lookup


def build_venue_lookup(
    matches: pd.DataFrame,
    geo_resolver: GeoResolver,
    airport_backend: AirportBackend,
) -> dict[str, AirportLookup]:
    geo_cache: dict[str, tuple[float, float] | None] = {}
    airport_cache: dict[str, AirportLookup | None] = {}
    lookup: dict[str, AirportLookup] = {}

    for _, row in matches.iterrows():
        city = normalize_location_text(row.get("city"))
        for candidate in venue_candidates(row):
            key = candidate.lower()
            if key in lookup:
                break
            coords = geocode_with_cache(
                geo_resolver,
                f"{candidate.lower()}|{city.lower()}",
                [candidate, f"{candidate}, {city}" if city else ""],
                geo_cache,
                f"venue {candidate}",
            )
            airport = lookup_airport_with_cache(
                airport_backend,
                coords,
                airport_cache,
                f"venue:{candidate.lower()}|{city.lower()}",
                f"venue {candidate}",
                [candidate, city],
            )
            if airport:
                lookup[key] = airport
                if city:
                    lookup.setdefault(city.lower(), airport)
                break
    return lookup


def select_team_columns(matches: pd.DataFrame) -> tuple[str, str]:
    team_1 = pick_column(matches, ["team_1", "team1", "home_team", "team_a"])
    team_2 = pick_column(matches, ["team_2", "team2", "away_team", "team_b"])
    return team_1, team_2


def select_venue_column(matches: pd.DataFrame) -> str:
    return pick_column(matches, ["venue", "stadium", "match_venue", "location"])


def team_distance_aggregation(
    matches: pd.DataFrame,
    team_origins: dict[str, TeamOrigin],
    venue_lookup: dict[str, AirportLookup],
    airport_backend: AirportBackend,
) -> list[dict[str, Any]]:
    team_1_col, team_2_col = select_team_columns(matches)
    venue_col = select_venue_column(matches)
    team_totals: dict[str, int] = {team: 0 for team in team_origins}
    team_matches: dict[str, int] = {team: 0 for team in team_origins}
    missing_pairs: list[tuple[str, str]] = []
    match_teams = {
        normalize_team_name(row.get(team_1_col))
        for _, row in matches.iterrows()
        if normalize_team_name(row.get(team_1_col))
    } | {
        normalize_team_name(row.get(team_2_col))
        for _, row in matches.iterrows()
        if normalize_team_name(row.get(team_2_col))
    }

    for team in match_teams:
        team_totals.setdefault(team, 0)
        team_matches.setdefault(team, 0)

    for _, row in matches.iterrows():
        venue_text = normalize_location_text(row.get(venue_col))
        if not venue_text:
            continue

        venue_key = venue_text.lower()
        destination = venue_lookup.get(venue_key)
        if destination is None:
            for candidate in venue_candidates(row):
                destination = venue_lookup.get(candidate.lower())
                if destination:
                    break

        if destination is None:
            logging.warning("Could not resolve venue airport for %s", venue_text)
            continue

        teams = [normalize_team_name(row.get(team_1_col)), normalize_team_name(row.get(team_2_col))]
        for team in teams:
            if not team:
                continue
            origin = team_origins.get(team)
            if origin is None:
                missing_pairs.append((team, venue_text))
                logging.warning("Missing training airport for team %s", team)
                continue
            try:
                distance = airport_backend.calculate_distance(origin.airport.iata, destination.iata)
            except Exception as exc:  # pragma: no cover - backend dependent
                logging.warning(
                    "Could not calculate distance for %s -> %s: %s",
                    origin.airport.iata,
                    destination.iata,
                    exc,
                )
                continue
            team_totals[team] = team_totals.get(team, 0) + int(round(distance))
            team_matches[team] = team_matches.get(team, 0) + 1

    rows = []
    for team, total in team_totals.items():
        origin = team_origins.get(team)
        rows.append(
            {
                "team": team,
                "training_site": origin.training_site if origin else "",
                "total_distance_km": int(total),
                "matches_count": int(team_matches.get(team, 0)),
            }
        )
    rows.sort(key=lambda item: item["total_distance_km"], reverse=True)
    if missing_pairs:
        logging.info("Encountered %d team/venue pairs without a complete route", len(missing_pairs))
    return rows


def write_json(payload: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_payload(
    team_rows: list[dict[str, Any]],
    group_stage_rows: int,
    origin_rows: int,
    dataset_type: str = "processed",
) -> dict[str, Any]:
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "dataset_type": dataset_type,
            "methodology": (
                "Travel distance is the sum of great-circle distances between each team's "
                "nearest commercial airport to its training site and the nearest commercial "
                "airport to each match venue."
            ),
            "teams_processed": len(team_rows),
            "matches_processed": int(group_stage_rows),
            "origin_rows_processed": int(origin_rows),
            "units": "km",
        },
        "teams": team_rows,
    }


def generate_demo_payload() -> dict[str, Any]:
    demo = [
        {
            "team": "Argentina",
            "training_site": "Sporting KC Training Centre",
            "total_distance_km": 5340,
            "matches_count": 3,
        },
        {
            "team": "Brazil",
            "training_site": "Columbia Park Training Facility",
            "total_distance_km": 4980,
            "matches_count": 3,
        },
        {
            "team": "France",
            "training_site": "Bentley University",
            "total_distance_km": 4720,
            "matches_count": 3,
        },
        {
            "team": "United States",
            "training_site": "Great Park Sports Complex",
            "total_distance_km": 4550,
            "matches_count": 3,
        },
        {
            "team": "Japan",
            "training_site": "Nashville SC",
            "total_distance_km": 4210,
            "matches_count": 3,
        },
    ]
    return build_payload(demo, group_stage_rows=0, origin_rows=0, dataset_type="demo")


def process_data() -> dict[str, Any]:
    group_stage_path = resolve_input_file(GROUP_STAGE_CSV_CANDIDATES)
    origins_path = resolve_input_file(TEAM_ORIGINS_CSV_CANDIDATES)

    if not group_stage_path.exists() or not origins_path.exists():
        logging.warning("Raw CSV inputs were not found, writing demo payload instead.")
        return generate_demo_payload()

    group_stage = load_csv(group_stage_path)
    origins = load_csv(origins_path)

    geo_resolver = GeoResolver()
    airport_backend = AirportBackend()

    team_origin_lookup = build_team_origin_lookup(origins, geo_resolver, airport_backend)
    venue_lookup = build_venue_lookup(group_stage, geo_resolver, airport_backend)
    team_rows = team_distance_aggregation(group_stage, team_origin_lookup, venue_lookup, airport_backend)

    payload = build_payload(team_rows, len(group_stage), len(origins))
    return payload


def sync_docs_json(source: Path, destination: Path) -> None:
    shutil.copyfile(source, destination)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate travel distance JSON for the dashboard.")
    parser.add_argument("--output", type=Path, default=OUTPUT_JSON, help="Processed JSON output path")
    parser.add_argument(
        "--docs-output",
        type=Path,
        default=DOCS_JSON,
        help="Copy of the JSON used by the GitHub Pages frontend",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = parse_args(sys.argv[1:] if argv is None else argv)
    ensure_directories()
    payload = process_data()
    write_json(payload, args.output)
    sync_docs_json(args.output, args.docs_output)
    logging.info("Wrote %s", args.output)
    logging.info("Copied %s", args.docs_output)
    logging.info("Processed %d teams", payload["metadata"]["teams_processed"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
