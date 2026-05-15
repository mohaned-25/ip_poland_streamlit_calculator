from __future__ import annotations

import math

from .data_loader import get_paper, load_materials
from .models import EdgeProtectorInput, EdgeProtectorResult, TubeInput, TubeResult


def ceil_div(a: float, b: float) -> int:
    return int(math.ceil(a / b)) if b else 0


def apply_margin(value: float, margin_percent: float) -> tuple[float, float]:
    margin_value = value * margin_percent / 100.0
    return value + margin_value, margin_value


def edge_cross_section_area_mm2(
    side_1_mm: float,
    side_2_mm: float,
    thickness_mm: float
) -> float:
    return thickness_mm * (side_1_mm + side_2_mm - thickness_mm)


def edge_weight_kg_per_rm(
    side_1_mm: float,
    side_2_mm: float,
    thickness_mm: float,
    density_kg_m3: float
) -> float:
    cfg = load_materials()["calibration"]

    area_mm2 = edge_cross_section_area_mm2(
        side_1_mm=side_1_mm,
        side_2_mm=side_2_mm,
        thickness_mm=thickness_mm
    )

    raw_weight = area_mm2 * density_kg_m3 / 1_000_000.0

    return raw_weight * cfg["edge_weight_factor"]


def edge_three_point_bending_n(
    side_1_mm: float,
    side_2_mm: float,
    thickness_mm: float,
    tea_index: float
) -> float:
    cfg = load_materials()["calibration"]

    section_value = thickness_mm ** 2 * max(side_1_mm, side_2_mm) * tea_index

    return section_value * cfg["edge_strength_factor"] / 1000.0


def tube_annulus_area_mm2(
    diameter_mm: float,
    thickness_mm: float
) -> float:
    inner_diameter_mm = max(diameter_mm - 2 * thickness_mm, 0)

    return math.pi / 4.0 * (
        diameter_mm ** 2 - inner_diameter_mm ** 2
    )


def tube_weight_kg_per_rm(
    diameter_mm: float,
    thickness_mm: float,
    density_kg_m3: float
) -> float:
    cfg = load_materials()["calibration"]

    raw_weight = (
        tube_annulus_area_mm2(
            diameter_mm=diameter_mm,
            thickness_mm=thickness_mm
        )
        * density_kg_m3
        / 1_000_000.0
    )

    return raw_weight * cfg["tube_weight_factor"]


def tube_flat_crush_n(
    diameter_mm: float,
    thickness_mm: float,
    scott_bond: float,
    tea_index: float
) -> float:
    cfg = load_materials()["calibration"]

    stiffness = (
        thickness_mm ** 2
        / max(diameter_mm, 1)
        * (0.65 * scott_bond + 350 * tea_index)
    )

    return stiffness * cfg["tube_flat_crush_factor"] / 10.0


def calculate_edge_protector(
    inp: EdgeProtectorInput
) -> EdgeProtectorResult:
    paper = get_paper(inp.product_type)
    cfg = load_materials()["calibration"]

    length_m = inp.length_mm / 1000.0
    total_rm = inp.quantity_pcs * length_m

    weight_kg_rm = edge_weight_kg_per_rm(
        side_1_mm=inp.side_1_mm,
        side_2_mm=inp.side_2_mm,
        thickness_mm=inp.thickness_mm,
        density_kg_m3=paper["density"]
    )

    weight_kg_piece = weight_kg_rm * length_m
    net_weight_kg = weight_kg_piece * inp.quantity_pcs

    pallets = ceil_div(inp.quantity_pcs, inp.quantity_per_pallet)

    pallet_weight_kg = (
        weight_kg_piece * inp.quantity_per_pallet
        + 20.0
    )

    base_price_kg = cfg["edge_reference_cost_pln_per_kg"]

    price_kg_with_transport = (
        base_price_kg
        + inp.transport_cost_pln / max(net_weight_kg, 1)
    )

    final_price_kg, margin_value_per_kg = apply_margin(
        value=price_kg_with_transport,
        margin_percent=inp.margin_percent
    )

    price_rm = final_price_kg * weight_kg_rm
    price_piece = price_rm * length_m
    total_value = price_piece * inp.quantity_pcs

    bending_force = edge_three_point_bending_n(
        side_1_mm=inp.side_1_mm,
        side_2_mm=inp.side_2_mm,
        thickness_mm=inp.thickness_mm,
        tea_index=paper["tea_index"]
    )

    return EdgeProtectorResult(
        weight_kg_per_rm=weight_kg_rm,
        weight_kg_per_piece=weight_kg_piece,
        total_running_m=total_rm,
        net_weight_kg=net_weight_kg,
        pallets=pallets,
        pallet_weight_kg=pallet_weight_kg,
        three_point_bending_n=bending_force,
        price_per_kg_pln=final_price_kg,
        price_per_rm_pln=price_rm,
        price_per_piece_pln=price_piece,
        total_value_pln=total_value,
        margin_value_pln=margin_value_per_kg * net_weight_kg,
        control_price_per_kg_pln=final_price_kg
    )


def calculate_tube(
    inp: TubeInput
) -> TubeResult:
    paper = get_paper(inp.product_type)
    cfg = load_materials()["calibration"]

    length_m = inp.length_mm / 1000.0
    total_rm = inp.quantity_pcs * length_m

    weight_kg_rm = tube_weight_kg_per_rm(
        diameter_mm=inp.diameter_mm,
        thickness_mm=inp.thickness_mm,
        density_kg_m3=paper["density"]
    )

    weight_kg_piece = weight_kg_rm * length_m
    net_weight_kg = weight_kg_piece * inp.quantity_pcs

    pallets = ceil_div(inp.quantity_pcs, inp.quantity_per_pallet)

    pallet_weight_kg = (
        weight_kg_piece * inp.quantity_per_pallet
        + 20.0
    )

    base_price_kg = cfg["tube_reference_cost_pln_per_kg"]

    price_kg_with_transport = (
        base_price_kg
        + inp.transport_cost_pln / max(net_weight_kg, 1)
    )

    final_price_kg, margin_value_per_kg = apply_margin(
        value=price_kg_with_transport,
        margin_percent=inp.margin_percent
    )

    price_rm = final_price_kg * weight_kg_rm
    price_piece = price_rm * length_m
    total_value = price_piece * inp.quantity_pcs

    flat_crush = tube_flat_crush_n(
        diameter_mm=inp.diameter_mm,
        thickness_mm=inp.thickness_mm,
        scott_bond=paper["scott_bond"],
        tea_index=paper["tea_index"]
    )

    return TubeResult(
        weight_kg_per_rm=weight_kg_rm,
        weight_kg_per_piece=weight_kg_piece,
        total_running_m=total_rm,
        net_weight_kg=net_weight_kg,
        pallets=pallets,
        pallet_weight_kg=pallet_weight_kg,
        flat_crush_n_per_0_1m=flat_crush,
        price_per_kg_pln=final_price_kg,
        price_per_rm_pln=price_rm,
        price_per_piece_pln=price_piece,
        total_value_pln=total_value,
        margin_value_pln=margin_value_per_kg * net_weight_kg,
        control_price_per_kg_pln=final_price_kg
    )
