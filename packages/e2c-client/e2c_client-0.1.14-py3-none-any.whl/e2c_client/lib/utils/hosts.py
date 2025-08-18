# Antennas list for iteration
CMs = ["CM%02d" % (x + 1) for x in range(12)]
DAs = ["DA%02d" % (x + 41) for x in range(25)]
DVs = ["DV%02d" % (x + 1) for x in range(25)]
PMs = ["PM%02d" % (x + 1) for x in range(4)]
all_ants = CMs + DAs + DVs + PMs
other_vmes = [
    "lo-lmc-1",
    "lo-lmc-2",
    "lo-lmc-3",
    "lo-lmc-4",
    "cob-dmc-01",
    "cob-dmc-02",
    "cob-dmc-03",
    "cob-dmc-04",
    "lo-art-1",
]

ALL_E2C_APE = [ant.lower() + "-e2c" for ant in all_ants]
ALL_E2C_APE.extend([vme.lower() + "-e2c" for vme in other_vmes])
