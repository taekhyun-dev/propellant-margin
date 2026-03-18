#!/usr/bin/env python3
"""
=============================================================================
ΔV Budget & Propellant Margin Analysis
100kg-class VLEO Satellite at ~300 km Altitude
Based on GSFC-STD-1000H Technical Resource Margin Guidelines
=============================================================================

Satellite Reference:
  - Bus dimensions: 35 x 25 x 110 cm
  - Total (wet) mass constraint: 100 kg (including propellant)
  - Propulsion: Hall Effect Thruster (BHT-100 class)
  - Orbit: ~300 km circular LEO (VLEO)
"""

import numpy as np

# =============================================================================
# 1. CONSTANTS & MISSION PARAMETERS
# =============================================================================
RE = 6371.0        # Earth radius [km]
mu = 398600.4418   # Earth gravitational parameter [km^3/s^2]
g0 = 9.80665       # Standard gravity [m/s^2]

# Orbit parameters
h_orbit = 300.0                      # Altitude [km]
r_orbit = RE + h_orbit               # Orbital radius [km]
V_orbit = np.sqrt(mu / r_orbit)      # Orbital velocity [km/s]
T_orbit = 2 * np.pi * r_orbit / V_orbit  # Orbital period [s]

# Satellite parameters
m_wet_total = 100.0     # Total wet mass constraint [kg] (including propellant)
Cd = 2.2                # Drag coefficient (typical for LEO)

# Bus dimensions: 35 x 25 x 110 cm
# Worst-case cross-section (largest face): 110 x 35 cm
A_max = 1.10 * 0.35     # Max cross-section [m^2] = 0.385 m^2
# Nominal (flight attitude): 35 x 25 cm face forward
A_nom = 0.35 * 0.25     # Nominal cross-section [m^2] = 0.0875 m^2

# HET parameters (BHT-100 class)
# Isp_nominal = 1390.0     # Nominal specific impulse [s]
Isp_nominal = 1000.0     # Nominal specific impulse [s]
thrust_nominal = 7.0e-3  # Nominal thrust [N] = 7 mN
power_nominal = 100.0    # Nominal input power [W]

# Mission parameters
mission_life_years = 3.0
mission_life_sec = mission_life_years * 365.25 * 24 * 3600

print("=" * 72)
print("  ΔV BUDGET & PROPELLANT MARGIN ANALYSIS")
print("  100 kg VLEO Satellite @ 300 km | GSFC-STD-1000H Methodology")
print("=" * 72)

print("\n[1] MISSION & ORBIT PARAMETERS")
print("-" * 50)
print(f"  Orbital altitude        : {h_orbit:.0f} km")
print(f"  Orbital radius          : {r_orbit:.1f} km")
print(f"  Orbital velocity        : {V_orbit:.3f} km/s ({V_orbit*1000:.1f} m/s)")
print(f"  Orbital period          : {T_orbit:.1f} s ({T_orbit/60:.1f} min)")
print(f"  Total wet mass          : {m_wet_total:.1f} kg (constraint, incl. propellant)")
print(f"  Nominal cross-section   : {A_nom:.4f} m² (flight attitude)")
print(f"  Max cross-section       : {A_max:.4f} m² (worst-case)")
print(f"  HET Isp (nominal)       : {Isp_nominal:.0f} s")
print(f"  HET Thrust (nominal)    : {thrust_nominal*1e3:.1f} mN")
print(f"  Mission lifetime        : {mission_life_years:.1f} years")

# =============================================================================
# 2. ATMOSPHERIC DRAG ΔV (Dominant factor at VLEO)
# =============================================================================
print(f"\n{'='*72}")
print("[2] ATMOSPHERIC DRAG ΔV ESTIMATION")
print("-" * 50)

# Atmospheric density at 300 km varies significantly with solar activity
# Using NRLMSISE-00 representative values
rho_low  = 1.0e-11   # Solar minimum, quiet [kg/m^3]
rho_nom  = 2.5e-11   # Moderate solar activity [kg/m^3]
rho_high = 1.5e-10   # Solar maximum, active [kg/m^3]

print(f"  Atmospheric density (solar min)  : {rho_low:.2e} kg/m³")
print(f"  Atmospheric density (nominal)    : {rho_nom:.2e} kg/m³")
print(f"  Atmospheric density (solar max)  : {rho_high:.2e} kg/m³")

def drag_dv_per_year(rho, Cd, A, m, V_orb_ms):
    """
    Compute annual ΔV needed to compensate atmospheric drag.
    ΔV/orbit = (Cd * A * rho * V^2) / (2 * m) * (orbital circumference)
    Simplified: drag acceleration * time
    """
    a_drag = 0.5 * rho * Cd * (A / m) * (V_orb_ms ** 2)  # m/s^2
    dv_per_year = a_drag * 365.25 * 24 * 3600              # m/s per year
    return a_drag, dv_per_year

V_orb_ms = V_orbit * 1000  # m/s

# Nominal case
a_drag_nom, dv_drag_nom = drag_dv_per_year(rho_nom, Cd, A_nom, m_wet_total, V_orb_ms)
# Solar max case
a_drag_high, dv_drag_high = drag_dv_per_year(rho_high, Cd, A_nom, m_wet_total, V_orb_ms)
# Worst case: solar max + max cross-section
a_drag_worst, dv_drag_worst = drag_dv_per_year(rho_high, Cd, A_max, m_wet_total, V_orb_ms)

print(f"\n  --- Drag Acceleration ---")
print(f"  Nominal (moderate solar)         : {a_drag_nom:.4e} m/s²")
print(f"  Solar max (nominal attitude)     : {a_drag_high:.4e} m/s²")
print(f"  Worst case (solar max + max A)   : {a_drag_worst:.4e} m/s²")

print(f"\n  --- Annual ΔV for Drag Compensation ---")
print(f"  Nominal                          : {dv_drag_nom:.2f} m/s/year")
print(f"  Solar max                        : {dv_drag_high:.2f} m/s/year")
print(f"  Worst case                       : {dv_drag_worst:.2f} m/s/year")

dv_drag_mission_nom = dv_drag_nom * mission_life_years
dv_drag_mission_high = dv_drag_high * mission_life_years
dv_drag_mission_worst = dv_drag_worst * mission_life_years

print(f"\n  --- {mission_life_years:.0f}-Year Mission Drag ΔV ---")
print(f"  Nominal                          : {dv_drag_mission_nom:.2f} m/s")
print(f"  Solar max                        : {dv_drag_mission_high:.2f} m/s")
print(f"  Worst case                       : {dv_drag_mission_worst:.2f} m/s")

# =============================================================================
# 3. OTHER ΔV COMPONENTS
# =============================================================================
print(f"\n{'='*72}")
print("[3] OTHER ΔV COMPONENTS")
print("-" * 50)

# Orbit correction: launcher dispersion expected mean correction
# Launch vehicle altitude dispersion ~ 1σ = 5 km (normal distribution)
# Expected absolute deviation = σ × √(2/π) ≈ 4 km, rounded to 5 km conservatively
dh_expected = 5.0  # km, expected (mean) altitude correction needed
a_transfer = r_orbit + dh_expected / 2
dv_orbit_correction = abs(np.sqrt(2*mu/r_orbit - mu/a_transfer) - np.sqrt(mu/r_orbit)) * 1000  # m/s
dv_orbit_correction *= 2  # Two burns for Hohmann
print(f"  Orbit correction (expected {dh_expected:.0f} km)  : {dv_orbit_correction:.2f} m/s")

# Collision avoidance maneuvers
# Typical: 2-4 maneuvers per year at VLEO, ~0.5-2 m/s each
n_cam_per_year = 4
dv_per_cam = 1.0  # m/s per maneuver (conservative)
dv_cam_mission = n_cam_per_year * dv_per_cam * mission_life_years
print(f"  Collision avoidance ({n_cam_per_year}/yr × {dv_per_cam:.1f} m/s) : {dv_cam_mission:.2f} m/s")

# Attitude control assist (if propulsion-assisted)
dv_attitude = 2.0 * mission_life_years  # m/s (small allocation)
print(f"  Attitude control assist          : {dv_attitude:.2f} m/s")

# De-orbit ΔV (at 300 km, natural decay is fast, but controlled de-orbit)
# Lower perigee to ~150 km for faster re-entry
r_perigee_deorbit = RE + 150.0
a_deorbit = (r_orbit + r_perigee_deorbit) / 2
dv_deorbit = abs(np.sqrt(mu/r_orbit) - np.sqrt(2*mu/r_orbit - mu/a_deorbit)) * 1000  # m/s
print(f"  Controlled de-orbit (to 150 km)  : {dv_deorbit:.2f} m/s")

# Safe mode / contingency
dv_contingency = 5.0
print(f"  Safe mode / contingency          : {dv_contingency:.2f} m/s")

# =============================================================================
# 4. NOMINAL ΔV BUDGET SUMMARY
# =============================================================================
print(f"\n{'='*72}")
print("[4] NOMINAL ΔV BUDGET SUMMARY")
print("-" * 50)

budget_items = {
    "Drag compensation (3yr, nominal)": dv_drag_mission_nom,
    "Orbit correction (expected mean)": dv_orbit_correction,
    "Collision avoidance": dv_cam_mission,
    "Attitude control assist": dv_attitude,
    "Controlled de-orbit": dv_deorbit,
    "Safe mode / contingency": dv_contingency,
}

dv_total_nominal = 0
for item, dv in budget_items.items():
    print(f"  {item:<42s} : {dv:8.2f} m/s")
    dv_total_nominal += dv

print(f"  {'─'*42}   {'─'*10}")
print(f"  {'TOTAL NOMINAL ΔV':<42s} : {dv_total_nominal:8.2f} m/s")

# --- Preliminary mass breakdown (needed for 3σ analysis) ---
def mass_breakdown_from_wet(dv_ms, m_wet, isp, g0=9.80665):
    """Given wet mass and ΔV, compute dry mass and propellant mass."""
    mass_ratio = np.exp(dv_ms / (g0 * isp))
    m_dry = m_wet / mass_ratio
    m_prop = m_wet - m_dry
    return m_dry, m_prop, mass_ratio

m_dry_nominal, m_prop_nominal_prelim, _ = mass_breakdown_from_wet(
    dv_total_nominal, m_wet_total, Isp_nominal)

print(f"\n  Preliminary mass breakdown (m_wet = {m_wet_total:.0f} kg):")
print(f"  Propellant (nominal ΔV)  : {m_prop_nominal_prelim:.3f} kg")
print(f"  Dry mass available       : {m_dry_nominal:.3f} kg")

# =============================================================================
# 5. 3-SIGMA MARGIN ANALYSIS (GSFC-STD-1000H)
# =============================================================================
print(f"\n{'='*72}")
print("[5] 3σ MARGIN ANALYSIS (GSFC-STD-1000H)")
print("-" * 50)
print("  Five uncertainty contributors per Table 1.06-1:")

# Factor 1: Worst-case spacecraft mass properties
# With m_wet = 100 kg constraint, mass growth has a different interpretation:
#   - Propellant mass from Tsiolkovsky: m_prop = m_wet × (1 - 1/exp(ΔV/(g₀·Isp)))
#   - Propellant depends on m_wet and ΔV, so if actual m_wet exceeds 100 kg
#     due to dry mass growth, more propellant is needed for the same ΔV.
#   - Additionally, dry mass growth reduces the mass available for propellant
#     within the 100 kg envelope.
# We model this as: if actual wet mass is 1σ=5% higher than planned (105 kg),
# the additional propellant needed for the same ΔV is proportional.
sigma_mwet_1s = 0.05  # 5% 1-sigma wet mass uncertainty (mass growth)
m_wet_3sigma = m_wet_total * (1 + 3 * sigma_mwet_1s)
# ΔV impact: more mass → same drag ΔV (nearly), but Tsiolkovsky demands
# proportionally more propellant. Model as equivalent ΔV uncertainty.
dv_sigma1 = dv_total_nominal * sigma_mwet_1s
print(f"\n  [1] Spacecraft mass uncertainty")
print(f"      1σ wet mass growth       : {sigma_mwet_1s*100:.0f}% ({m_wet_total*sigma_mwet_1s:.1f} kg)")
print(f"      3σ wet mass              : {m_wet_3sigma:.1f} kg")
print(f"      (Nominal dry mass        : {m_dry_nominal:.1f} kg within 100 kg wet)")
print(f"      1σ ΔV impact             : {dv_sigma1:.2f} m/s")

# Factor 2: Launch vehicle performance (3σ low)
# Total altitude dispersion: 1σ = 5 km
# Nominal budget already covers expected correction of 5 km
# Factor 2: uncertainty that actual dispersion EXCEEDS the expected value
# Additional 1σ uncertainty beyond expected: ~3 km
sigma_alt_additional_1s = 3.0  # km, 1σ additional beyond expected 5 km
dv_per_km = dv_orbit_correction / dh_expected  # ΔV per km correction
dv_sigma2 = dv_per_km * sigma_alt_additional_1s  # 1σ
print(f"\n  [2] Launch vehicle performance (3σ low)")
print(f"      Nominal budget covers    : {dh_expected:.0f} km expected correction")
print(f"      1σ additional dispersion : ±{sigma_alt_additional_1s:.0f} km beyond expected")
print(f"      3σ total correction      : {dh_expected + 3*sigma_alt_additional_1s:.0f} km")
print(f"      1σ ΔV impact             : {dv_sigma2:.2f} m/s")

# Factor 3: Propulsion subsystem performance
# Isp uncertainty: ±3% (1σ), thrust vector misalignment: ±2°, residuals: 2%
sigma_isp_1s = 0.03  # 3% Isp 1σ uncertainty
thrust_misalign_deg = 2.0  # degrees
cos_loss = 1 - np.cos(np.radians(thrust_misalign_deg))
residual_fraction = 0.02  # 2% unusable propellant

# ΔV impact from Isp degradation
dv_sigma3_isp = dv_total_nominal * sigma_isp_1s
# ΔV impact from thrust misalignment (cosine loss)
dv_sigma3_align = dv_total_nominal * cos_loss
# Combined propulsion 1σ
dv_sigma3 = np.sqrt(dv_sigma3_isp**2 + dv_sigma3_align**2)
print(f"\n  [3] Propulsion subsystem performance")
print(f"      1σ Isp uncertainty       : ±{sigma_isp_1s*100:.0f}%")
print(f"      Thrust misalignment      : ±{thrust_misalign_deg:.0f}°")
print(f"      Cosine loss              : {cos_loss*100:.3f}%")
print(f"      Propellant residuals     : {residual_fraction*100:.0f}%")
print(f"      1σ ΔV impact (combined)  : {dv_sigma3:.2f} m/s")

# Factor 4: Flight dynamics errors
# Navigation uncertainty, maneuver execution error
# Typical: 2-5% of each maneuver ΔV (1σ)
sigma_nav_1s = 0.03  # 3% execution error
dv_sigma4 = dv_total_nominal * sigma_nav_1s
print(f"\n  [4] Flight dynamics errors")
print(f"      1σ maneuver exec error   : ±{sigma_nav_1s*100:.0f}%")
print(f"      1σ ΔV impact             : {dv_sigma4:.2f} m/s")

# Factor 5: Thruster failure (single-fault-tolerant)
# If 1 of 2 thrusters fails, remaining thruster may have off-axis penalty
# Assume ~10% efficiency loss with single thruster
sigma_thruster_fail = 0.05  # Weighted by failure probability
dv_sigma5 = dv_total_nominal * sigma_thruster_fail
print(f"\n  [5] Thruster failure (single-fault-tolerant)")
print(f"      Efficiency loss factor   : {sigma_thruster_fail*100:.0f}%")
print(f"      1σ ΔV impact             : {dv_sigma5:.2f} m/s")

# RSS combination
sigma_total_1s = np.sqrt(dv_sigma1**2 + dv_sigma2**2 + dv_sigma3**2 + 
                          dv_sigma4**2 + dv_sigma5**2)
sigma_total_3s = 3 * sigma_total_1s

print(f"\n  --- RSS Combination ---")
print(f"  {'σ₁ (mass)':<30s} : {dv_sigma1:8.2f} m/s")
print(f"  {'σ₂ (launch vehicle)':<30s} : {dv_sigma2:8.2f} m/s")
print(f"  {'σ₃ (propulsion)':<30s} : {dv_sigma3:8.2f} m/s")
print(f"  {'σ₄ (flight dynamics)':<30s} : {dv_sigma4:8.2f} m/s")
print(f"  {'σ₅ (thruster failure)':<30s} : {dv_sigma5:8.2f} m/s")
print(f"  {'─'*30}   {'─'*10}")
print(f"  {'1σ_total (RSS)':<30s} : {sigma_total_1s:8.2f} m/s")
print(f"  {'3σ_total':<30s} : {sigma_total_3s:8.2f} m/s")

# =============================================================================
# 6. DESIGN ΔV AND PROPELLANT MASS
# =============================================================================
print(f"\n{'='*72}")
print("[6] DESIGN ΔV & PROPELLANT MASS (Tsiolkovsky)")
print("-" * 50)

dv_design = dv_total_nominal + sigma_total_3s

print(f"  Nominal ΔV                       : {dv_total_nominal:.2f} m/s")
print(f"  3σ margin                        : {sigma_total_3s:.2f} m/s")
print(f"  Design ΔV (nominal + 3σ)         : {dv_design:.2f} m/s")
print(f"  Margin percentage                : {sigma_total_3s/dv_total_nominal*100:.1f}%")

# Propellant mass calculation using Tsiolkovsky equation
# With wet mass constraint: m_wet = m_dry + m_prop = 100 kg (fixed)
# m_dry = m_wet / exp(ΔV / (g0 * Isp))
# m_prop = m_wet - m_dry
# (function mass_breakdown_from_wet defined earlier in Section 4)

# Nominal case (nominal ΔV, nominal Isp) — recompute with final values
m_dry_nominal, m_prop_nominal, mr_nominal = mass_breakdown_from_wet(
    dv_total_nominal, m_wet_total, Isp_nominal)

# Design case (design ΔV with 3σ margin, nominal Isp)
m_dry_design, m_prop_design, mr_design = mass_breakdown_from_wet(
    dv_design, m_wet_total, Isp_nominal)

# Add residuals to design propellant
m_prop_design_total = m_prop_design * (1 + residual_fraction)
m_dry_design_actual = m_wet_total - m_prop_design_total

# Worst case (design ΔV, degraded Isp)
Isp_degraded = Isp_nominal * (1 - 3 * sigma_isp_1s)
m_dry_worst, m_prop_worst, mr_worst = mass_breakdown_from_wet(
    dv_design, m_wet_total, Isp_degraded)
m_prop_worst_total = m_prop_worst * (1 + residual_fraction)
m_dry_worst_actual = m_wet_total - m_prop_worst_total

print(f"\n  --- Nominal Case ---")
print(f"  Wet mass       : {m_wet_total:.1f} kg (fixed constraint)")
print(f"  Isp            : {Isp_nominal:.0f} s")
print(f"  ΔV             : {dv_total_nominal:.2f} m/s")
print(f"  Propellant     : {m_prop_nominal:.3f} kg")
print(f"  Dry mass       : {m_dry_nominal:.3f} kg (available for bus + payload)")
print(f"  Mass ratio     : {mr_nominal:.6f}")

print(f"\n  --- Design Case (Nominal + 3σ ΔV) ---")
print(f"  Wet mass       : {m_wet_total:.1f} kg (fixed constraint)")
print(f"  Isp            : {Isp_nominal:.0f} s")
print(f"  ΔV             : {dv_design:.2f} m/s")
print(f"  Propellant     : {m_prop_design:.3f} kg")
print(f"  + Residuals    : {m_prop_design_total:.3f} kg")
print(f"  Dry mass       : {m_dry_design_actual:.3f} kg (available for bus + payload)")

print(f"\n  --- Worst Case (degraded Isp + residuals) ---")
print(f"  Wet mass       : {m_wet_total:.1f} kg (fixed constraint)")
print(f"  Isp (degraded) : {Isp_degraded:.0f} s")
print(f"  ΔV             : {dv_design:.2f} m/s")
print(f"  Propellant     : {m_prop_worst:.3f} kg")
print(f"  + Residuals    : {m_prop_worst_total:.3f} kg")
print(f"  Dry mass       : {m_dry_worst_actual:.3f} kg (available for bus + payload)")

# =============================================================================
# 7. SOLAR ACTIVITY SENSITIVITY ANALYSIS
# =============================================================================
print(f"\n{'='*72}")
print("[7] SOLAR ACTIVITY SENSITIVITY (Drag dominates at VLEO)")
print("-" * 50)

scenarios = [
    ("Solar Minimum", rho_low),
    ("Moderate Activity", rho_nom),
    ("Solar Maximum", rho_high),
]

print(f"  {'Scenario':<22s} {'ρ [kg/m³]':>12s} {'ΔV_drag/yr':>12s} {'ΔV_drag 3yr':>12s} {'m_prop':>9s} {'m_dry_avail':>11s}")
print(f"  {'─'*22} {'─'*12} {'─'*12} {'─'*12} {'─'*9} {'─'*11}")

for name, rho in scenarios:
    _, dv_yr = drag_dv_per_year(rho, Cd, A_nom, m_wet_total, V_orb_ms)
    dv_3yr = dv_yr * mission_life_years
    # Replace drag component in total budget
    dv_total_scenario = dv_3yr + (dv_total_nominal - dv_drag_mission_nom)
    dv_scenario_design = dv_total_scenario + sigma_total_3s
    _, m_p, _ = mass_breakdown_from_wet(dv_scenario_design, m_wet_total, Isp_nominal)
    m_p_total = m_p * (1 + residual_fraction)
    m_d_avail = m_wet_total - m_p_total
    print(f"  {name:<22s} {rho:>12.2e} {dv_yr:>10.2f}   {dv_3yr:>10.2f}   {m_p_total:>7.3f} kg  {m_d_avail:>7.3f} kg")

# =============================================================================
# 8. THRUSTER OPERATION SUMMARY
# =============================================================================
print(f"\n{'='*72}")
print("[8] THRUSTER OPERATION SUMMARY")
print("-" * 50)

# Total impulse
total_impulse_nominal = m_prop_nominal * g0 * Isp_nominal  # N·s
total_impulse_design = m_prop_design_total * g0 * Isp_nominal

# Thruster-on time
t_on_nominal = total_impulse_nominal / thrust_nominal  # seconds
t_on_design = total_impulse_design / thrust_nominal

print(f"  Total impulse (nominal)          : {total_impulse_nominal:.1f} N·s")
print(f"  Total impulse (design)           : {total_impulse_design:.1f} N·s")
print(f"  Thruster-on time (nominal)       : {t_on_nominal:.0f} s ({t_on_nominal/3600:.1f} hrs)")
print(f"  Thruster-on time (design)        : {t_on_design:.0f} s ({t_on_design/3600:.1f} hrs)")
print(f"  BHT-100 typical lifetime         : ~10,000 hrs")
print(f"  Lifetime margin                  : {10000/(t_on_design/3600)*100 - 100:.0f}%")

# Xenon tank sizing (rough)
rho_xe = 1.6  # kg/L (supercritical xenon density at typical storage)
vol_xe_design = m_prop_design_total / rho_xe
print(f"\n  Xenon tank volume (design)       : {vol_xe_design:.2f} L ({vol_xe_design*1000:.0f} mL)")

# =============================================================================
# 9. PHASE-BY-PHASE MARGIN STATUS (GSFC-STD-1000H)
# =============================================================================
print(f"\n{'='*72}")
print("[9] PHASE-BY-PHASE MARGIN STATUS (GSFC-STD-1000H Table 1.06-1)")
print("-" * 50)

# Propellant: 3σ margin required from Phase B through Phase D
# Mass margins at each phase for reference
print(f"\n  Mass budget breakdown (m_wet = {m_wet_total:.0f} kg constraint):")
print(f"  ┌──────────────────────────────────────────────────────────────┐")
print(f"  │ Nominal propellant required      : {m_prop_nominal:8.3f} kg               │")
print(f"  │ Design propellant (w/ 3σ + res)  : {m_prop_design_total:8.3f} kg               │")
print(f"  │ 3σ margin in propellant mass      : {m_prop_design_total - m_prop_nominal:8.3f} kg               │")
print(f"  │ 3σ margin percentage              : {(m_prop_design_total/m_prop_nominal - 1)*100:8.1f}%                │")
print(f"  │                                                              │")
print(f"  │ Dry mass available (nominal)      : {m_dry_nominal:8.3f} kg               │")
print(f"  │ Dry mass available (design prop)  : {m_dry_design_actual:8.3f} kg               │")
print(f"  │ → This is the mass for bus + payload within 100 kg          │")
print(f"  └──────────────────────────────────────────────────────────────┘")

print(f"\n  Phase-by-phase dry mass margin check:")
print(f"  (Allowable dry mass = {m_wet_total:.0f} kg - {m_prop_design_total:.3f} kg propellant"
      f" = {m_dry_design_actual:.3f} kg)")
print(f"  ┌────────────┬───────────┬────────────────────────────────┐")
print(f"  │   Phase    │  Required │  Max predicted dry mass        │")
print(f"  ├────────────┼───────────┼────────────────────────────────┤")

phases = [
    ("Pre-Phase A", "≥15%", 0.15),
    ("Phase A/SRR", "≥15%", 0.15),
    ("Phase B/PDR", "≥10%", 0.10),
    ("Phase C/CDR", "≥5%",  0.05),
    ("Phase C/SIR", "≥2%",  0.02),
    ("Phase D",     "0%",   0.00),
]

m_dry_allowable = m_dry_design_actual  # Dry mass budget after propellant allocation

for phase_name, req_str, req_frac in phases:
    margin_needed = m_dry_allowable * req_frac
    m_max_predicted = m_dry_allowable - margin_needed
    print(f"  │ {phase_name:<10s} │  {req_str:<7s}  │  {m_max_predicted:>6.1f} kg"
          f" (margin {margin_needed:.1f} kg)      │")

print(f"  └────────────┴───────────┴────────────────────────────────┘")

# =============================================================================
# 10. SUMMARY & RECOMMENDATIONS
# =============================================================================
print(f"\n{'='*72}")
print("[10] SUMMARY & RECOMMENDATIONS")
print("=" * 72)
print(f"""
  ┌─────────────────────────────────────────────────────────────────┐
  │  TOTAL WET MASS CONSTRAINT     : {m_wet_total:>6.1f} kg                      │
  │                                                                 │
  │  DESIGN ΔV BUDGET                                              │
  │  ─────────────────────────────────────────────────────────────  │
  │  Nominal ΔV total          : {dv_total_nominal:>8.2f} m/s                    │
  │  3σ uncertainty (RSS)      : {sigma_total_3s:>8.2f} m/s                    │
  │  Design ΔV                 : {dv_design:>8.2f} m/s                    │
  │                                                                 │
  │  MASS BUDGET BREAKDOWN                                          │
  │  ─────────────────────────────────────────────────────────────  │
  │  Design propellant (Xe)    : {m_prop_design_total:>8.3f} kg (incl. 3σ + residuals) │
  │  Dry mass available        : {m_dry_design_actual:>8.3f} kg (for bus + payload)    │
  │  Propellant fraction       : {m_prop_design_total/m_wet_total*100:>8.1f}%                       │
  │                                                                 │
  │  KEY NOTES                                                      │
  │  ─────────────────────────────────────────────────────────────  │
  │  • Drag is the dominant ΔV driver at 300 km VLEO                │
  │  • Solar activity has a ~10x impact on drag ΔV                  │
  │  • 3σ propellant margin per GSFC-STD-1000H Table 1.06-1        │
  │  • ~{m_dry_design_actual:.0f} kg available for bus + payload design             │
  │  • Consider solar cycle phase during mission planning           │
  └─────────────────────────────────────────────────────────────────┘
""")