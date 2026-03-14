"""Fleet database — verified IMO/MMSI from MarineTraffic/VesselFinder.

Community contributions welcome. Add your carrier's fleet via PR.
"""

FLEET_DB = {
    "CMB.TECH": [
        {"name": "MINERAL QINGDAO", "imo": "9738583", "mmsi": "538008606", "type": "Bulk Carrier (Newcastlemax)", "flag": "MH", "dwt": 206298},
        {"name": "MINERAL HOKKAIDO", "imo": "9384954", "mmsi": "563082300", "type": "Bulk Carrier (Capesize)", "flag": "SG", "dwt": None},
        {"name": "CMB RUBENS", "imo": "9832640", "mmsi": "538008033", "type": "Bulk Carrier (Ultramax)", "flag": "MH", "dwt": 63514},
        {"name": "CMB VAN DIJCK", "imo": "9883106", "mmsi": "370209000", "type": "Bulk Carrier (Ultramax)", "flag": "PA", "dwt": 63667},
        {"name": "CMB MATSYS", "imo": "9916226", "mmsi": "352980770", "type": "Bulk Carrier (Ultramax)", "flag": "PA", "dwt": 63620},
        {"name": "CMB TENIERS", "imo": "9916214", "mmsi": "352978143", "type": "Bulk Carrier (Ultramax)", "flag": "PA", "dwt": 63611},
        {"name": "CMB FLORIS", "imo": "9908499", "mmsi": "563131400", "type": "Bulk Carrier (Ultramax)", "flag": "SG", "dwt": 63628},
        {"name": "CMB CHIKAKO", "imo": "9701190", "mmsi": "357320000", "type": "Bulk Carrier (Panamax)", "flag": "PA", "dwt": 61299},
        {"name": "CMB SAKURA", "imo": "9316854", "mmsi": "371784000", "type": "Bulk Carrier (Panamax)", "flag": "PA", "dwt": 75765},
    ],
    "DEME": [
        {"name": "ORION", "imo": "9825453", "mmsi": "205755000", "type": "Crane Ship (OIV)", "flag": "BE", "dwt": 60575},
        {"name": "SPARTACUS", "imo": "9834404", "mmsi": "253810000", "type": "Cutter Suction Dredger", "flag": "LU", "dwt": None},
        {"name": "LIVING STONE", "imo": "9776925", "mmsi": "244010952", "type": "Cable Layer", "flag": "NL", "dwt": None},
        {"name": "APOLLO", "imo": "9769764", "mmsi": "253586000", "type": "Jack-up OIV", "flag": "LU", "dwt": None},
        {"name": "CONGO RIVER", "imo": "9574523", "mmsi": "205298000", "type": "TSHD", "flag": "BE", "dwt": None},
        {"name": "BONNY RIVER", "imo": "9810939", "mmsi": "253665000", "type": "TSHD", "flag": "LU", "dwt": None},
        {"name": "PEARL RIVER", "imo": "9051014", "mmsi": "210245000", "type": "TSHD", "flag": "CY", "dwt": 17947},
        {"name": "SCHELDT RIVER", "imo": "9778143", "mmsi": "205708000", "type": "TSHD", "flag": "BE", "dwt": None},
        {"name": "NILE RIVER", "imo": "9187007", "mmsi": "246472000", "type": "TSHD", "flag": "NL", "dwt": None},
        {"name": "UILENSPIEGEL", "imo": "9247467", "mmsi": "205146000", "type": "TSHD", "flag": "BE", "dwt": None},
        {"name": "BREYDEL", "imo": "9382384", "mmsi": "205520000", "type": "TSHD", "flag": "BE", "dwt": None},
        {"name": "AMAZONE", "imo": "9158630", "mmsi": "245718000", "type": "TSHD", "flag": "NL", "dwt": 3000},
        {"name": "GROENEWIND", "imo": "9900318", "mmsi": "219032879", "type": "Wind Service Vessel", "flag": "DK", "dwt": 330},
    ],
    "Heerema": [
        {"name": "SLEIPNIR", "imo": "9781425", "mmsi": "374887000", "type": "SSCV (20,000t crane)", "flag": "PA", "dwt": None, "gt": 273700},
        {"name": "THIALF", "imo": "8757740", "mmsi": "353979000", "type": "SSCV", "flag": "PA", "dwt": None},
        {"name": "BALDER", "imo": "7710226", "mmsi": "354721000", "type": "SSCV", "flag": "PA", "dwt": 59404},
        {"name": "AEGIR", "imo": "9605396", "mmsi": "354590000", "type": "DCV / Pipelayer", "flag": "PA", "dwt": None},
        {"name": "KOLGA", "imo": "9646326", "mmsi": "244790079", "type": "AH Tug", "flag": "NL", "dwt": None},
        {"name": "BYLGIA", "imo": "9646314", "mmsi": "244740210", "type": "AH Tug", "flag": "NL", "dwt": None},
    ],
}
