# AHTS & DP2 Operations: Smart Advisor Requirements

This document outlines the high-value features for the Integrated Bridge System (IBS) Smart Advisor, specifically tailored for an OOW on a DP2 offshore tug/AHTS (e.g., Heerema-style operations like Bylgia/Kolga).

These features emphasize predictive risk mitigation, real-time stability oversight, towing/anchor-specific guidance, and hybrid W2W capabilities — all STCW-compliant.

## 1. Anchor Handling & Towing (AHT) Guidance Module
- **Winch & Tow Wire Monitoring:** Real-time tension (multiple drums), payout/length, angle, chain/wire catenary shape (visualized in 3D Cesium overlay), and snatch-load prediction (using Morison-equation drag + heave/current models).
  - *Alerts:* Tension >85% MBL, rapid payout spikes, or predicted snap-load.
- **Anchor Deployment/Recovery Advisor:** Step-by-step checklists fused with DP capability. Integration with live winch data + USBL/ROV for subsea anchor position verification.
- **Towing Mode:** Bollard pull vs. environmental load comparison, tow line tension/angle monitoring, emergency quick-release status, and predicted tow stability (heading/yaw excursion).
- **Deck Safety / Shark Jaw Status:** Deck camera AI detects jaw engagement, roller wear, or personnel proximity (safety interlock alerts).

## 2. Walk-to-Work (W2W) / Gangway Transfer Support
- **Motion-Compensated Gangway Integration:** Real-time gangway status (extension/retraction, motion compensation active, connection force).
  - *Predictive Envelope:* Hs/wind/current forecast vs. gangway operability envelope.
- **Safe Transfer Advisor:** Personnel countdown, weather window monitoring, emergency disconnect prediction, fused with DP station-keeping.
  - *AR Overlay (Cesium):* Show gangway projection + safe corridor.
- **Hybrid Ops:** Dynamic mode switching (DP follow-target for gangway alignment during transfer).

## 3. Vessel Stability & Intact Stability Monitoring
- **Live Stability Calculator:** Real-time GM, GZ curve, righting arm, heel/trim from loading computer (deck cargo, chain lockers, ballast).
- **Environmental Fusion:** Wind/current/wave forces → predicted heel in tow/anchor ops.

## 3. Vessel Stability & Intact Stability Monitoring (Continued)
- **DP-Integrated Stability:** External forces (tow wire tension, anchor chain pull) fed into stability model → alerts if heel exceeds safe limits.
- **Damage Stability Advisor:** What-if scenarios for flooding/compartment breach (post-FMEA) with DP consequence analysis.
- **Ballast & Trim Control:** Automated suggestions for ballast adjustment during heavy anchor handling.

## 4. Other Critical Offshore Support Features
- **Bollard Pull & Capability Forecasting:** Polar plots extended for AHT modes (anchor chain external force, tow configurations).
- **FiFi / Emergency Response:** Fire-fighting monitor status, pump capacity, deluge coverage for platform assist.
- **Deck Load & Cargo Monitoring:** Clear deck area, cargo weight distribution, stability impact alerts.
- **Subsea & ROV Synergy:** Anchor position verification via ROV/USV, chain catenary monitoring from subsea camera.
- **Crew & Fatigue Integration:** Tie rest-hour compliance directly to AHT/W2W phase risk (e.g., "Hold phase + high tension + projected rest breach in 60 min – recommend handover").

## Implementation Priority & Integration
- **High Priority (Next Sprint):** AHT winch/tension + stability monitoring.
- **UI Placement:** Dedicated "AHT/W2W" tab or cards in Mission Control, with 3D Cesium overlays (tether/chain catenary, gangway corridor, stability heel indicator).
- **Voice Advisor Hooks:** "Advisor, bollard pull vs. current load?", "Gangway status for transfer?".
