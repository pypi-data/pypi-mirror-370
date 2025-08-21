from mindustry_campaign_stats.constants import Planet, SectorNames, ItemIds
from datetime import datetime, timezone
from typing import Dict, List, Union
import dataclasses
import re


@dataclasses.dataclass
class StorageStats:
    capacity: int
    items: Dict[str, int]


@dataclasses.dataclass
class StorageAndProductionStatsMixin:
    storage: StorageStats
    rawProduction: Dict[str, float]  # Per minute
    netProduction: Dict[str, float]  # Per minute


@dataclasses.dataclass
class SectorStats(StorageAndProductionStatsMixin):
    name: str
    availability: List[str]
    imports: Dict[str, float]  # Per minute
    exports: Dict[str, float]  # Per minute


@dataclasses.dataclass
class TotalsStats(StorageAndProductionStatsMixin):
    pass


@dataclasses.dataclass
class Stats:
    date: datetime
    planet: Planet
    sectors: Dict[int, SectorStats]
    totals: TotalsStats

    def to_dict(self) -> Dict:
        ret = dataclasses.asdict(self)

        ret['date'] = ret['date'].isoformat()
        ret['planet'] = ret['planet'].value

        return ret


class StatsBuilder:
    settings: Dict[str, Union[bool, float, int, bytes, str]]
    planet: Planet

    sectors_info: Dict[int, Dict]

    def __init__(self, settings: Dict[str, Union[bool, float, int, bytes, str]], planet: Planet):
        self.settings = settings
        self.planet = planet

        self.sectors_info = self.get_sectors_info()

    def build_sectors(self) -> Dict:
        return {
            sector_id: SectorStats(
                name=SectorNames.get(self.planet).get(sector_id, str(sector_id)),
                availability=sector_info.get('resources', []),
                storage=StorageStats(
                    capacity=sector_info.get('storageCapacity', 0),
                    items=sector_info.get('items', {})
                ),
                rawProduction={
                    item_id: item_info.get('mean', 0) * 60 for item_id, item_info in
                    sector_info.get('rawProduction', {}).items()
                },
                netProduction={
                    item_id: item_info.get('mean', 0) * 60 for item_id, item_info in
                    sector_info.get('production', {}).items()
                },
                imports={
                    item_id: item_info.get('mean', 0) * 60 for item_id, item_info in
                    sector_info.get('imports', {}).items()
                },
                exports={
                    item_id: item_info.get('mean', 0) * 60 for item_id, item_info in
                    sector_info.get('export', {}).items()
                }
            ) for sector_id, sector_info in self.sectors_info.items()
        }

    def build_totals(self) -> TotalsStats:
        return TotalsStats(
            storage=StorageStats(
                capacity=sum([
                    sector_info.get('storageCapacity', 0) for sector_info in self.sectors_info.values()
                ]),
                items={
                    item_id: sum([
                        sector_info.get('items', {}).get(item_id, 0) for sector_info in self.sectors_info.values()
                    ]) for item_id in ItemIds.get(self.planet)
                }
            ),
            rawProduction={
                item_id: sum([
                    sector_info.get('rawProduction', {}).get(item_id, {}).get('mean', 0) * 60 for sector_info in
                    self.sectors_info.values() if sector_info.get('rawProduction', {}).get(item_id, {}).get('mean', 0)
                ]) for item_id in ItemIds.get(self.planet)
            },
            netProduction={
                item_id: sum([
                    sector_info.get('production', {}).get(item_id, {}).get('mean', 0) * 60 for sector_info in
                    self.sectors_info.values() if sector_info.get('production', {}).get(item_id, {}).get('mean', 0)
                ]) for item_id in ItemIds.get(self.planet)
            }
        )

    def get_sectors_info(self) -> Dict[int, Dict]:
        sector_name_regex = re.compile(fr'{self.planet.value}-s-(?P<number>\d+)-info')

        sectors_info = {}

        for key, value in self.settings.items():
            sector_name_match = sector_name_regex.match(key)

            if not sector_name_match:
                continue

            sector_number = int(sector_name_match.groupdict()['number'])

            sectors_info[sector_number] = value

        return sectors_info


def compute(settings: Dict[str, Union[bool, float, int, bytes, str]], planet: Planet) -> Stats:
    builder = StatsBuilder(settings, planet)

    return Stats(
        date=datetime.now(timezone.utc),
        planet=planet,
        sectors=builder.build_sectors(),
        totals=builder.build_totals()
    )
