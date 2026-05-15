from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class EdgeProtectorInput:
    side_1_mm: float
    side_2_mm: float
    thickness_mm: float
    length_mm: float
    product_type: str
    outer_cover: str
    quantity_pcs: int
    quantity_per_pallet: int
    transport_cost_pln: float
    margin_percent: float
    currency: str = "PLN"


@dataclass_m: float@dataclass
    net_weight_kg: float
    pallets: int
    pallet_weight_kg: float
    three_point_bending_n: float
    price_per_kg_pln: float
    price_per_rm_pln: float
    price_per_piece_pln: float
    total_value_pln: float
    margin_value_pln: float
    control_price_per_kg_pln: float

    def to_dict(self):
        return asdict(self)


@dataclass
class TubeInput:
    diameter_mm: float
    thickness_mm: float
    length_mm: float
    product_type: str
    inner_cover: str
    outer_cover: str
    quantity_pcs: int
    quantity_per_pallet: int
    transport_cost_pln: float
    margin_percent: float
    currency: str = "PLN"


@dataclass
class TubeResult:
    weight_kg_per_rm: float
    weight_kg_per_piece: float
    total_running_m: float
    net_weight_kg: float
    pallets: int
    pallet_weight_kg: float
    flat_crush_n_per_0_1m: float
    price_per_kg_pln: float
    price_per_rm_pln: float
    price_per_piece_pln: float
    total_value_pln: float
    margin_value_pln: float
    control_price_per_kg_pln: float

    def to_dict(self):
        return asdict(self)
class EdgeProtectorResult:
    weight_kg_per_rm: float
    weight_kg_per_piece: float
