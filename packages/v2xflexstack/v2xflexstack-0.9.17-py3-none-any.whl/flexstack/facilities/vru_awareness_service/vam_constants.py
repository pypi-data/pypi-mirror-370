"""
Constants extracted from:ETSI TS 103 300-3 V2.2.1 (2023-02)
Table 17: Parameters for VAM generation triggering (clause 6.4)

Parametrs: minimumSafeLateralDistance and minimumSafeLongitudinalDistance are
    not defined here, as they are not static(they depend on the VRU speed)
"""
T_GENVAMMIN = 100  # ms
T_GENVAMMAX = 5000  # ms
T_CHECKVAMGEN = T_GENVAMMIN  # ms Shall be equal to or less than T_GenvamMin
T_GENVAM_DCC = T_GENVAMMIN  # ms T_GenvamMin ≤ T_Genvam_DCC ≤ T_GenvamMax
MINREFERENCEPOINTPOSITIONCHANGETHRESHOLD = 4
MINGROUNDSPEEDCHANGETHRESHOLD = 0.5
MINGROUNDVELOCITYORIENTATIONCHANGETHRESHOLD = 4
MINTRAJECTORYINTERCEPTIONPROBCHANGETHRESHOLD = 10
NUMSKIPVAMSFORREDUNDANCYMITIGATION = 2  # Value can range from 2-10
MINCLUSTERDISTANCECHANGETHRESHOLD = 2
MINIMUMSAFEVERTICALDISTANCE = 5

"""
From ETSI TS 103 300-2 V2.1.1 (2020-05), page 47;
The VRU Basic Service shall interact with the VRU profile management entity in
    the management layer to learn
whether the ITS-S has the VRU role activated.

TODO: Create VRU Profile Mangement

Since it's not yet created the values will be declared here
"""

VRU_PROFILE = {
    "Type": "Cyclist",
    "Speed": 20,
    "TransmissionRange": 70,
    "Environment": "Urban",
    "WeightClass": "High",
    "TrajectoryAmbiguity": "Medium",
    "ClusterSize": 1,
}

"""
ETSI TS 103 300-3 V2.2.1 (2023-02) - 5.4.1 VRU clustering functional overview
States: The support of the clustering function is optional in the VBS for all
VRU profiles.
however the same document in section C.2.3 Protocol data, states;
The VRU Basic Service (VBS) stores at least the following information for the
VAM originating ITS-S operation:
VAM generation time;
• ITS-S position as included in VAM;
• ITS-S speed as included in VAM;
• ITS-S heading as included in VAM;
• VRU role;
• VRU profile;
• VBS cluster state.
VRU role, VRU profile nad VBS cluster state will be hardcoded (VRU_Profile already is).
"""

VRU_ROLE = "VRU_ROLE_ON"
VRU_CLUSTER_STATE = "VRU-ACTIVE-STANDALONE"
