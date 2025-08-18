def map_node(node):
    """
    Node/name asignation
    From: https://bitbucket.alma.cl/projects/ALMA/repos/almasw/browse/ADC/SW/SWTools/CCLTools/src/initCCL.py::__get_device_name
    """
    device_list = {
        0x00: "Antenna Control Unit [ACU]",
        0x01: "Pointing Computer",
        0x10: "FE Compressor [FEC]",
        0x13: "Front End Monitor & Control [FEMC]",
        0x1C: "Holography Receiver [HoloRX]",
        0x1D: "Holography DSP      [HoloDSP]",
        0x1E: "125MHz Reference Distributor",
        0x1F: "Optical Pointing Telescope",
        0x20: "Central Reference Distributor [CRD]",
        0x21: "Nutator",
        0x22: "LO Reference Receiver [LORR]",
        0x23: "Frontend Assembly",
        0x24: "Water Vapour Radiometer [WVR]",
        0x25: "Compressor [CMPR]",
        0x26: "Frontend Power Supply [FEPS]",
        0x27: "Master Laser Distributor [MLD]",
        0x28: "Calibration Widgets [ACD]",
        0x29: "IF Processor [IFProc]",
        0x2A: "IF Processor [IFProc]",
        0x2B: "Master Laser [ML]",
        0x2C: "Master Laser [ML]",
        0x30: "Digitizer Clock [DGCK]",
        0x31: "5MHz Distributor",
        0x32: "First LO Offset Generator [FLOOG]",
        0x33: "Low Frequency Reference Distributor [LFRD]",
        0x40: "2nd LO Synthesizer [LO2]",
        0x41: "2nd LO Synthesizer [LO2]",
        0x42: "2nd LO Synthesizer [LO2]",
        0x43: "2nd LO Synthesizer [LO2]",
        0x44: "IF Processor [IFProc]",
        0x45: "IF Processor [IFProc]",
        0x46: "IF Processor [IFProc]",
        0x47: "IF Processor [IFProc]",
        0x50: "DTS Transmitter Module [DTX]",
        0x51: "DTS Transmitter Module [DTX]",
        0x52: "DTS Transmitter Module [DTX]",
        0x53: "DTS Transmitter Module [DTX]",
        0x60: "Power Supply (analog rack) [PSA]",
        0x61: "Power Supply (digital rack) [PSD]",
        0x62: "Power Supply (CRD) [PSCRD]",
        0x3F: "Local Oscillator Reference Test Module [LORTM]",
    }
    name = "Unknown"
    try:
        name = device_list[node]
    except:
        if node in range(0x100, 0x1FF + 1):
            name = "DTS Receiver Module [DRX]"
        elif node in range(0x200, 0x27F + 1):
            name = "Line Length Corrector [LLC]"
        elif node in range(0x280, 0x29F + 1):
            name = "Fiber Optic Amplifier Demux [FOAD]"
        elif node in range(0x300, 0x34F + 1):
            name = "Sub Array Switch [SAS]"
        elif node in range(0x48, 0x4D + 1):
            name = "Photonic Reference Distributor [PRD]"
        elif node in range(0x58, 0x5D + 1):
            name = "Power Supply LLC [PSLLC]"
        elif node in range(0x5E, 0x63 + 1):
            name = "Power Supply SAS [PSSAS]"
        elif node in range(0x38, 0x3D + 1):
            name = "Laser Synthesizer [LS]"
    return name
