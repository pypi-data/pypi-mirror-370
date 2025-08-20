"""
A library of PDF utilities to interface with matplotlib's PDF engine.
For help, explore the readme and the docs markdown files in the package source.
"""

# Load general packages, lazy load the rest.
import matplotlib.pyplot as plt
from pandas import DataFrame, Series
import os
from typing import Literal
from pvevti import genutil as gu
from shapely.geometry import Point

#  Parameters
debugInfo = False
plt.rcParams['font.family'] = 'Daimler CS'
default_color_palette = "default"

cols = ["#00677F", "#B65302",
        "#7CBCCA", "#0E5A1A",
        "#651B26", "#44B690",
        "#E1933A", "#B4B4B4",]

def getCol(i):
    """
    For Color parsing; returns the hex color for any provided integer.
    Cycles through available colors as defined in the pvevti.pdfutil.cols list.
    """
    return cols[((i+1) % len(cols)-1)]

def setDefaultColorPalette(palette: Literal["default", "red", "blue", "green", "yellow", "gray", "petrol", "bright", 
                                     "pastel_mintcitrus", "pastel_sandybeach", "pastel_technicolor", "pastel_summerstorm", 
                                     "seahawks", "cardinals", "colts", "buccaneers", "dolphins", "panthers", "vikings", 
                                     "commanders", "lions", "jaguars"]):
    global default_color_palette
    default_color_palette = palette
    setColorPalette(default_color_palette)

def setColorPalette(palette: Literal["default", "red", "blue", "green", "yellow", "gray", "petrol", "bright", 
                                     "pastel_mintcitrus", "pastel_sandybeach", "pastel_technicolor", "pastel_summerstorm", 
                                     "seahawks", "cardinals", "colts", "buccaneers", "dolphins", "panthers", "vikings", 
                                     "commanders", "lions", "jaguars"]):
    global cols
    match palette.lower():

        # Standard Palettes
        case "" | "default":
            cols = ["#00677F", "#B65302",
                    "#7CBCCA", "#0E5A1A",
                    "#651B26", "#44B690",
                    "#E1933A", "#B4B4B4",]
        case "red" | "reds":
            cols = ["#2D0000", "#6D3737",
                    "#A21C1C", "#D56060"]
        case "blue" | "blues":
            cols = ["#000D2D", "#374B6D",
                    "#1C1CA2", "#608FD5"]
        case "green" | "greens":
            cols = ["#002D06", "#376D39",
                    "#37A21C", "#60D57B"]
        case "yellow" | "gold":
            cols = ["#856E1C", "#C29013",
                    "#AC9B5F"]
        case "gray" | "grays" | "grey" | "greys":
            cols = ["#1F1F1F", "#828282",
                    "#4D4D4D", "#AFAFAF"]
        
        # DTNA Colors
        case "petrol":
            cols = ["#00677F", "#053F4B",
                    "#2D9DB7", "#2F3E42"]
        case "petrolhighlight":
            cols = ["#FFFF40", "#00677F", 
                    "#053F4B", "#2D9DB7", 
                    "#2F3E42"]
        case "bright":
            cols = ["#00677F", "#6EA046",
                    "#E69123", "#FF0000"]
            
        # Pastels provided by kdesign.co
        case "pastel_mintcitrus":
            cols = ["#D6F0E2", "#FFEAB8",
                    "#BFDBC8", "#FFE8A4",
                    "#E4EEEB", "#FFF6DB"]
        case "pastel_sandybeach":
            cols = ["#C0E5E8", "#EFECE6",
                    "#DAF4EF", "#DEEBEB",
                    "#9EDCE1", "#EFE4CB"]
        case "pastel_technicolor":
            cols = ["#FFADAD", "#FFD6A5",
                    "#FDFFB6", "#E4F1EE",
                    "#D9EDF8", "#DEDAF4"]
        case "pastel_summerstorm":
            cols = ["#C4D7E0", "#E5F4F4",
                    "#879BA6", "#A3BCCB",
                    "#DAE7AB", "#E8EBCF"]
        
        # A select few NFL teams
        case "seahawks":
            cols = ["#002A5C", "#7AC142",
                    "#B2B7BB", "#2D5980"]
        case "cardinals":
            cols = ["#97233F", "#C0C0C0",
                    "#151515", "#FFB612"]
        case "colts":
            cols = ["#013369", "#A5ACAF",
                    "#10252C"]
        case "buccaneers":
            cols = ["#D50A0A", "#FF7900",
                    "#0A0A08", "#B1BABF"]
        case "dolphins":
            cols = ["#008E98", "#005679",
                    "#C0C0C0", "#F78200"]
        case "panthers":
            cols = ["#0088CE", "#080808",
                    "#A5ACAF"]
        case "vikings":
            cols = ["#4F2683", "#C0C0C0",
                    "#FFC62F"]
        case "commanders":
            cols = ["#5A1414", "#FFB612",
                    "#C0C0C0"]
        case "lions":
            cols = ["#0076B6", "#B0B7BC",
                    "#080808"]
        case "jaguars":
            cols = ["#D8A328", "#136677",
                    "#080808", "#9E7A2C"]

        # Fallback
        case "_":
            cols = ["#101010"]

def linspace(start, finish, samples, include=False):
    vals = []
    if include:
        delta = (finish - start) / (samples - 1)
    else:
        delta = (finish - start) / samples
    for i in range(0, samples):
        vals.append(start + i * delta)
    return vals

default_hvac_pdf_config = {
    "docTitle": "DefaultHVACReport",
    "docSubTitle":  "HVAC Report",
    "pages": [
        # Conditions and Route
        {
            "pageName": "Conditions and Route",
            "plots": [
                {
                    "plotTitle":"Trip Route",
                    "plotType": "map",
                    "xData":    "GPS_speed_mph",
                    "yData":    ["gps_x", "gps_y"]
                },
                {
                    "plotTitle":"Conditions",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["amb_t", "gps_z"]
                },
                {
                    "plotTitle":"Signals Overview",
                    "plotType": "table",
                    "yData":    ["amb_t", "cab_breath_l_air_t", "cab_breath_r_air_t"]
                }
            ]
        },

        # Systems
        {
            "pageName": "Cabin Systems",
            "plots": [
                {
                    "plotTitle":"In-Cabin",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["cab_breath_l_air_t", "cab_breath_r_air_t", "CAB_LOUV_FCE_LL_AIR_T", "CAB_LOUV_FCE_RR_AIR_T"]
                },
                {
                    "plotTitle":"Cab Floor",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["CAB_FLR_FRONT_236_ST[°C]", "CAB_FLR_MIDDLE_236_ST[°C]", "CAB_FLR_PASS_SEAT_ST[°C]", "CAB_FLR_SHIFTPLT_ST[°C]", "CAB_LOUV_FLR_LL_AIR_T", "CAB_LOUV_FLR_RR_AIR_T"]
                },
                {
                    "plotTitle":"AC Functionality",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["ac_on"]
                },
                {
                    "plotTitle":"AC Functionality",
                    "plotType": "hist",
                    "xData":    "ac_on"
                }
            ]
        },
    ]
}

default_electrical_pdf_config = {
    "docTitle": "DefaultElectricalReport",
    "docSubTitle":  "Electical Report",
    "pages": [
        # Conditions and Route
        {
            "pageName": "Conditions and Route",
            "plots": [
                {
                    "plotTitle":"Trip Route",
                    "plotType": "map",
                    "xData":    "GPS_speed_mph",
                    "yData":    ["gps_x", "gps_y"]
                },
                {
                    "plotTitle":"Conditions",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["amb_t", "gps_z"]
                },
                {
                    "plotTitle":"Signals Overview",
                    "plotType": "table",
                    "yData":    ["bat_s_volt", "bat_l_volt", "alt_volt"]
                }
            ]
        },

        # Electrical Data
        {
            "pageName": "Voltages and Currents",
            "plots": [
                {
                    "plotTitle":"Batteries and Alternator",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["bat_s_volt", "bat_l_volt", "alt_volt", "batvolt_cval", "is1_u_battery", "isp_dps_ubat"]
                },
                {
                    "plotTitle":"Current",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["alt_cur", "rpg_i_fmu_act", "rpg_i_pcv_des"]
                },
                {
                    "plotTitle":"Current (Volvo Specific)",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["bat_12v_cur", "bat_24v_cur", "dc_dc_cur_out"]
                }
            ]
        }
    ]
}

default_cooling_pdf_config = {
    "docTitle": "DefaultCoolingReport",
    "docSubTitle": "Cooling Report",
    "pages": [
        # Conditions and Route
        {
            "pageName": "Conditions and Route",
            "plots": [
                {
                    "plotTitle":"Trip Route",
                    "plotType": "map",
                    "xData":    "GPS_speed_mph",
                    "yData":    ["gps_x", "gps_y"]
                },
                {
                    "plotTitle":"Conditions",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["amb_t", "gps_z"]
                },
                {
                    "plotTitle":"Signals Overview",
                    "plotType": "table",
                    "yData":    ["amb_t", "clto", "EngCoolantTemp", "CoolTemp_Cval_PT"]
                }
            ]
        },

        # Engine loading and coolant states
        {
            "pageName": "Coolant Loading",
            "plots": [
                {
                    "plotTitle":"Engine Output",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["EngTrq_Cval_PT", "EngRPM_Cval_CPC3"]
                },
                {
                    "plotTitle":"Engine Load",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["EngPctLoadAtCurrSpeed_Cval", "EngRPM_Cval_CPC3"]
                },
                {
                    "plotTitle":"Associated Fluids",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["EngFuelTemp1", "EngAirIntakeTemp", "EngOilTemp1"]
                },
                {
                    "plotTitle":"Metrics Review",
                    "plotType": "table",
                    "yData":    ["EngRPM_Cval_CPC3", "EngTrq_Cval_PT", "EngPctLoadAtCurrSpeed_Cval"]
                }
            ]
        },

        # Fan states
        {
            "pageName": "Fan Behavior",
            "plots": [
                {
                    "plotTitle":"Fan Engagement",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["fan_engagement_rate", "fan_fan_speed", "fan_drive"]
                },
                {
                    "plotTitle":"Fan Engagement",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["fan_status_mcm", "Fan_Rq_PT"]
                },
                {
                    "plotTitle":"Fan Error",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["fan_temp_error_coolant"]
                },
                {
                    "plotTitle":"Metrics Review",
                    "plotType": "table",
                    "yData":    ["fan_engagement_rate", "fan_fan_speed", "fan_status_mcm", "Fan_Rq_PT"]
                }
            ]
        },

        # Transmission states and temperatures
        {
            "pageName": "Transmission",
            "plots": [
                {
                    "plotTitle":"Engine Load",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["EngPctLoadAtCurrSpeed_Cval"]
                },
                {
                    "plotTitle":"Ambient Temperatures",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["amb_t", "tm_abv_trns_air_t"]
                },
                {
                    "plotTitle":"Transmission Temperatures",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["transoiltemp1", "trn_oc_oil_ti", "trn_oc_oil_to"]
                },
            ]
        }
    ]
}

default_powersteering_pdf_config = {
    "docTitle": "DefaultPowerSteeringReport",
    "docSubTitle": "Power Steering Report",
    "pages": [
        # Conditions and Route
        {
            "pageName": "Conditions and Route",
            "plots": [
                {
                    "plotTitle":"Trip Route",
                    "plotType": "map",
                    "xData":    "GPS_speed_mph",
                    "yData":    ["gps_x", "gps_y"]
                },
                {
                    "plotTitle":"Conditions",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["amb_t", "gps_z"]
                },
                {
                    "plotTitle":"Signals Overview",
                    "plotType": "table",
                    "yData":    ["amb_t", "amb_p", "STEER_RES_PSFLD_T", "SteerWheelAngle"]
                }
            ]
        },

        # Reservoir Data
        {
            "pageName": "Reservoir Data",
            "plots": [
                {
                    "plotTitle":"Ambient Air Temperature",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["amb_t", "air_hood_l_air_ti", "air_hood_r_air_ti"]
                },
                {
                    "plotTitle":"Engine-adjacent Air Temperatures",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["blockfrtfce_air_t", "eng_rps_st", "rad_4_2_air_to", "smv_lh_air_t", "str_relay_air_t"]
                },
                {
                    "plotTitle":"Measured Speed",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["VehSpd_Cval_CPC", "isp_vehicle_speed", "GPS_spee"]
                },
                {
                    "plotTitle":"Reservoir Temperature",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["STEER_RES_PSFLD_T"]
                }
            ]
        },

        # Tire Data
        {
            "pageName": "Tires",
            "plots": [
                {
                    "plotTitle":"Tire Pressures",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["TirePress_00", "TirePress_01", "TirePress_10", "TirePress_11", "TirePress_12", "TirePress_13", "TirePress_20", "TirePress_21", "TirePress_22", "TirePress_23"]
                },
                {
                    "plotTitle":"Tire Temepratures",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["TireTemp_00", "TireTemp_01", "TireTemp_10", "TireTemp_11", "TireTemp_12", "TireTemp_13", "TireTemp_20", "TireTemp_21", "TireTemp_22", "TireTemp_23"]
                }
            ]
        }
    ]
}

default_route_conditions_config = {
    "docTitle": "DefaultRouteConditionsReport",
    "docSubTitle": "Route Conditions Report",
    "pages": [
        # 
        {
            "pageName": "Route Overview",
            "plots": [
                {
                    "plotTitle":"Trip Route",
                    "plotType": "map",
                    "xData":    "GPS_speed_mph",
                    "yData":    ["gps_x", "gps_y"]
                }
            ]
        },
        {
            "pageName": "Powertrain",
            "plots": [
                {
                    "plotTitle":"Engine Load",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["EngPctLoadAtCurrSpd_Cval"]
                },
                {
                    "plotTitle":"Engine Output",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["tbf_trq_full_load_limit", "isp_trq_current"]
                },
                {
                    "plotTitle":"Transmission Mode",
                    "plotType":"line",
                    "xData":    "t",
                    "yData":    "TransCurrentGear"
                }
            ]
        },
        {
            "pageName": "Cruise Control",
            "plots": [
                {
                    "plotTitle":"Cruise Control Mode",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["CC_Actv_Stat"]
                },
                {
                    "plotTitle":"Cruise Control Set Speed",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["CC_SetSpd_Cval","vehspd_cval_cpc"]
                },
                {
                    "plotTitle":"Cruise Control Activity",
                    "plotType": "hist",
                    "xData":    "CC_Actv_Stat"
                },
                {
                    "plotTitle":"Overview",
                    "plotType": "table",
                    "yData":    ["CC_actv_stat", "cc_setspd_cval", "vehspd_cval_cpc"]
                }
            ]
        },
        {
            "pageName": "Miscellaneous",
            "plots": [
                {
                    "plotTitle":"Aftertreatment",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ["tmc_status", "dpf_zone_status"]
                },
                {
                    "plotTitle": "Power-Speed Plot",
                    "plotType" : "scatter",
                    "xData"    : "EngRPM_Cval_CPC3",
                    "yData"    : ["HP_CALCULATED"]
                },
                {
                    "plotTitle": "Torque-Speed Plot",
                    "plotType" : "scatter",
                    "xData"    : "EngRPM_Cval_CPC3",
                    "yData"    : ["isp_trq_current"]
                }
            ]
        }
    ]
}

default_towdyno_config = {
    "docTitle": "DefaultTowDynoReport",
    "docSubTitle": "Tow-Dyno Report",
    "pages": [
        # 
        {
            "pageName": "Route Overview",
            "plots": [
                {
                    "plotTitle":"Trip Route",
                    "plotType": "map",
                    "xData":    "GPS_speed_mph",
                    "yData":    ["gps_x", "gps_y"]
                }
            ]
        },
        {
            "pageName": "Retarder Data",
            "plots": [
                {
                    "plotTitle":"Temperatures",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["TC_R1", "TC_R2", "TC_R3", "TC_R4", "TC_R5", "TC_R6"]
                },
                {
                    "plotTitle":"Currents",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["I_R1", "I_R2", "I_R3", "I_R4", "I_R5", "I_R6"]
                },
                {
                    "plotTitle":"Voltages",
                    "plotType": "line",
                    "xData":    "t",
                    "yData":    ["VI_R1", "VI_R2", "VI_R3", "VI_R4", "VI_R5", "VI_R6"]
                },
            ]
        },
        {
            "pageName": "Overview",
            "plots": [
                {
                    "plotTitle":"Temperatures & Currents",
                    "plotType": "table",
                    "yData":    ["TC_R1", "TC_R2", "TC_R3", "TC_R4", "TC_R5", "TC_R6", "I_R1", "I_R2", "I_R3", "I_R4", "I_R5", "I_R6"]
                },
                {
                    "plotTitle":"Weight",
                    "plotType": "dualline",
                    "xData":    "t",
                    "yData":    ['ctl_weight', 'vehspd_cval']
                },
            ]
        },
    ]
}

default_config = {
    "docTitle": "Default Document Title", "docSubTitle": "Default Document Subtitle",
    "pages": [
        # Map and Signal Overview
        {
            "pageName": "Map",
            "plots": [
                {
                    "plotTitle":  "Trip route",
                    "plotType":   "map",
                    "xData":      "GPS_speed_mph",
                    "yData":      ["gps_x", "gps_y"]
                },
                {
                    "plotTitle":  "Overview Table",
                    "plotType":   "table",
                    "yData":      ["amb_t", "amb_p", "gps_speed", "clti", "clto", "clpi", "clpo", "cti", "cto", "EngPctLoadAtCurrSpd_Cval", "fan_fan_speed", "AXLE_FD_OIL_T", "AXLE_RD_OIL_T"]
                }
            ]
        },

        # Ambient Conditions
        {
            "pageName": "Conditions",
            "plots": [
                {
                    "plotTitle": "Altitude",
                    "plotType" : "dualline",
                    "xData"    : "cumulative distance",
                    "yData"    : ["gps_z", "gps_speed"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "Ambient Conditions",
                    "plotType" : "dualline",
                    "xData"    : "cumulative distance",
                    "yData"    : ["amb_t", "amb_p"],
                    "filterLength": 120
                }
            ]
        },

        # Basic Analytics
        {
            "pageName": "Basic Analytics",
            "plots": [
                {
                    "plotTitle": "Speed and Time",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["GPS_speed_mph"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "CAC and Condensor Package",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["amb_t", "cac_2_2_air_ti", "cond_2_2_air_ti"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "Turbocharger and CAC Pressure Performance (Compressor)",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["AMB_P", "ICPI", "ICPO"],
                    "filterLength": 180
                },
                {
                    "plotTitle": "Turbocharger and CAC Pressure Performance (Turbine)",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["amb_p", "expo", "ats_pi", "ats_po"],
                    "filterLength": 180
                }
            ]
        },
        
        # Engine Performance
        {
            "pageName": "Engine Performance",
            "plots": [
                {
                    "plotTitle": "Engine Speeds",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["EngSpd_Cval_PT", "FanSpd_Cval_PT", "OutShaftSpd_Cval_PT"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Engine Torque",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["ebm_eng_act_trq", "tbf_trq_friction", "can_trq_dem"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Fuel Rail",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["rpg_p_rail_act", "rpg_p_rail_des"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Mass Flow",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["sp_intake_mass", "sp_air_mass", "sp_egr_mass", "spe_des_air_mass"]
                }
            ]
        },
        
        # Thermal Analysis - ACM, ATS, Intake, Radiator
        {
            "pageName": "Primary Thermal Analysis",
            "plots": [
                {
                    "plotTitle": "ACM",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["ACM_FRT_ST", "acm_bck_st", "acm_hrn_brk_zt_st"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Aftertreatment System",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["ATS_DPS_ST", "ATS_HRN_AFT_ZT_ST", "ATS_HRN_COND_ST", "ATS_HRN_ELBOW_ST", "ATS_HRN_ZT_TOP_ST"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "Ambient and Intake",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["amb_T", "cti", "icto"],
                    "filterLength": 360
                },
                {
                    "plotTitle": "Radiator Package",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["rad_2_2_air_ti", "rad_2_2_air_to", "rad_4_2_air_ti", "rad_4_2_air_to"],
                    "filterLength": 360
                },
                {
                    "plotTitle": "Fan Activation States",
                    "plotType" : "hist",
                    "xData"    : "fan_fan_speed"
                }
            ]
        },

        # More Thermal Analysis
        {
            "pageName": "Continued Thermal Analysis",
            "plots": [
                {
                    "plotTitle": "SCU Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["soot_scu_st", "soot_scu_air_t", "soot_scu_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "NOX Raw Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["nox_raw_hex_st", "nox_raw_ecu_st", "nox_raw_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "NOX Mid Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["nox_out_hex_st", "nox_out_ecu_st", "nox_out_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "NOX Out Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["nox_out_hex_st", "nox_out_ecu_st", "nox_out_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "HVAC",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["HVAC_SetTemp_Stat", "cab_breath_l_air_t", "cab_breath_r_air_t"],
                    "filterLength": 40
                }
            ]
        },
        
        # PRE-SCR
        {
            "pageName": "Pre-SCR Overview",
            "plots": [
                {
                    "plotTitle": "Pre-SCR Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["PRE_SCR_ST_1", "PRE_SCR_ST_10", 
                                  "PRE_SCR_ST_2", "PRE_SCR_ST_3", 
                                  "PRE_SCR_ST_4", "PRE_SCR_ST_5", 
                                  "PRE_SCR_ST_6", "PRE_SCR_ST_7", 
                                  "PRE_SCR_ST_8", "PRE_SCR_ST_9"],
                    "filterLength": 160
                },
                {
                    "plotTitle":  "Pre-SCR Values",
                    "plotType":   "table",
                    "yData":      ["PRE_SCR_ST_1", "PRE_SCR_ST_10", 
                                  "PRE_SCR_ST_2", "PRE_SCR_ST_3", 
                                  "PRE_SCR_ST_4", "PRE_SCR_ST_5", 
                                  "PRE_SCR_ST_6", "PRE_SCR_ST_7", 
                                  "PRE_SCR_ST_8", "PRE_SCR_ST_9"]
                }
            ]
        },
        
        # Statuses
        {
            "pageName": "Status",
            "plots": [
                {
                    "plotTitle": "TMC Status",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["tmc_status"]
                },
                {
                    "plotTitle": "AM OPC Status",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["am_opc_status"]
                },
                {
                    "plotTitle": "Fan Status",
                    "plotType" : "dualline",
                    "xData"    : "t",
                    "yData"    : ["fan_status_mcm", "clto"]
                }
            ]
        },
        
        # Extra Plots
        {
            "pageName": "Extras",
            "plots": [
                {
                    "plotTitle": "Air Compressor and Dryer Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["air_comp_ti", "air_comp_to", "air_dryer_ti", "air_dryer_to"],
                    "filterLength": 3
                },
                {
                    "plotTitle": "Air Compressor Status",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["air_on"]
                },
                {
                    "plotTitle": "Power-Speed Plot",
                    "plotType" : "scatter",
                    "xData"    : "EngRPM_Cval_CPC3",
                    "yData"    : ["HP_CALCULATED"]
                },
                {
                    "plotTitle": "Torque-Speed Plot",
                    "plotType" : "scatter",
                    "xData"    : "EngRPM_Cval_CPC3",
                    "yData"    : ["isp_trq_current"]
                }
            ]
        }
    ]
}

slc = {
  "AC_ON[STATE]": [0, 1],
  "ACM_BCK_ST[°C]": [0, 90],
  "ACM_FRT_ST[°C]": [0, 90],
  "ACM_HRN_BRK_ZT_ST[°C]": [0, 90],
  "AIR_COMP_TI[°C]": [0, 90],
  "AIR_COMP_TO[°C]": [20, 150],
  "AIR_DRYER_FILTER_ST[°C]": [20, 120],
  "AIR_DRYER_TI[°C]": [20, 120],
  "AIR_DRYER_TO[°C]": [20, 120],
  "AIR_HOOD_L_AIR_TI[°C]": [-50, 50],
  "AIR_HOOD_R_AIR_TI[°C]": [-50, 50],
  "AIR_ON[STATE]": [0, 1],
  "ALT_CUR[A]": [0, 200],
  "ALT_REAR_AIR_T[°C]": [-50, 150],
  "ALT_ST[°C]": [-50, 120],
  "ALT_VOLT[V]": [-1, 16],
  "AMB_P[BARa]": [0.7, 1.1],
  "AMB_T[°C]": [-50, 65],
  "AMB_T_F[]": [-58, 149],
  "AmbAirPress_Cval_PT[mBar]": [700, 1200],
  "AmbientAirTemp[°C]": [-50, 65],
  "AmbTemp_Cval_MCM_PT[°C]": [-50, 65],
  "AmbTemp_Cval_PT[°C]": [-50, 65],
  "ATI[°C]": [-50, 65],
  "ATS_HCIU_FACE_ST[°C]": [50, 200],
  "ATS_HRN_AFT_ZT_ST[°C]": [50, 200],
  "ATS_HRN_COND_ST[°C]": [50, 200],
  "ATS_HRN_ELBOW_ST[°C]": [50, 200],
  "ATS_HRN_ZT_TOP_ST[°C]": [50, 200],
  "ATS_INBRD_ST[°C]": [50, 200],
  "ATS_PI[BARa]": [0.8, 1.1],
  "ATS_PO[BARa]": [0.8, 1.1],
  "ATS_PRESS_IN_ST[°C]": [0, 140],
  "ATS_TI[°C]": [0, 140],
  "ATS_TO[°C]": [0, 140],
  "AXLE_FD_OIL_T[°C]": [0, 165],
  "AXLE_RD_OIL_T[°C]": [0, 165],
  "BarometricPress[kPa]": [80, 110],
  "BAT_L_VOLT[V]": [11, 15],
  "BAT_S_VOLT[V]": [11, 15],
  "BatVolt_Cval[V]": [11, 15],
  "BatVolt_Cval[V].1": [11, 15],
  "BCA_VOLT_IN[V]": [11, 15],
  "BLOCKFRTFCE_AIR_T[°C]": [0, 100],
  "BoostPress_Cval_PT[bar]": [0, 3.5],
  "BoostTemp_Cval_PT[°C]": [0, 3.5],
  "BoostTemp_Cval_PT[°C].1": [0, 3.5],
  "can_vehicle_speed[km/h]": [-1, 150],
  "CLTI[°C]": [0, 120],
  "CLTO[°C]": [0, 120],
  "CPI[BAR]": [0.7, 1.2],
  "CTI[°C]": [-40, 65],
  "CTO[°C]": [-40, 225],
  "CTP3_BOTTOM_ST[°C]": [-40, 75],
  "CTP3_TOP_ST[°C]": [-40, 75],
  "CTP3_USB_ST[°C]": [-40, 75],
  "ELEVATION_FT[]": [0, 10000],
  "EngAirIntakeTemp[°C]": [-40, 65],
  "EngCoolantTemp[°C]": [-40, 120],
  "EngFuelTemp1[°C]": [-40, 160],
  "EngRPM_Cval_CPC3[rpm]": [0, 2500],
  "EngRPM_Cval_CPC3[rpm].1": [0, 2500],
  "EngRPM_Cval_CPC3[rpm].2": [0, 2500],
  "EngSpd_Cval_PT[rpm]": [0, 2500],
  "EngStrtrMode_Stat_MCM[]": [0, 2500],
  "EngTrq_Cval_PT[Nm]": [-2000, 3000],
  "etc_trq_per_load[%]": [0, 100],
  "etc_trq_per_load_corr[%]": [0, 100],
  "EXPO[BARa]": [0, 3],
  "EXTO[°C]": [-40, 500],
  "fan_drive[min-1]": [0, 3000],
  "fan_fan_speed[min-1]": [0, 3000],
  "FuelLvl_Cval[%]": [0, 100],
  "GPS_speed[kph]": [0, 150],
  "GPS_speed_mph[mph]": [0, 93],
  "GPS_speed_mph[]": [0, 93],
  "HP_CALCULATED[]": [-600, 600],
  "HVAC_R_SetTemp_Stat[°C]": [0, 40],
  "ICPI[BAR]": [-0.1, 2.5],
  "ICPO[BAR]": [-0.1, 2.5],
  "ICTI[°C]": [-40, 250],
  "ICTO[°C]": [-40, 100],
  "isp_trq_actual[%]": [0, 100],
  "MCM_BCK_ST[°C]": [-40, 110],
  "MCM_FRT_ST[°C]": [-40, 110],
  "MCS_LENS_L_ST[°C]": [-40, 70],
  "MCS_LENS_R_ST[°C]": [-40, 70],
  "MCS_MON_DOWN_ST[°C]": [-40, 70],
  "MCS_MON_L_ST[°C]": [-40, 70],
  "MCS_MON_R_ST[°C]": [-40, 70],
  "NOX_MID_CONN_ST[°C]": [-40, 70],
  "NOX_MID_ECU_ST[°C]": [-40, 100],
  "NOX_MID_HEX_ST[°C]": [-40, 350],
  "NOX_MID_PRB_ST[°C]": [-40, 350],
  "NOX_OUT_CONN_ST[°C]": [-40, 110],
  "NOX_OUT_ECU_AIR_T[°C]": [-40, 110],
  "NOX_OUT_ECU_ST[°C]": [-40, 150],
  "OIL_PAN_T[°C]": [-40, 125],
  "OilTemp_Cval_PT[°C]": [-40, 125],
  "OilTemp_RA_Cval[°C]": [-40, 125],
  "OilTemp_RA_Cval[°C].1": [-40, 125],
  "OilTemp_RA2_Cval[°C]": [-40, 125],
  "OilTemp_RA2_Cval[°C].1": [-40, 125],
  "STARTER_AIR_T[°C]": [-40, 120],
  "STARTER_BODY_ST[°C]": [-40, 120],
  "STARTER_SOL_ST[°C]": [-40, 120],
  "STARTER_SOL_VOLT[V]": [0, 15],
  "STARTER_VOLT[V]": [0, 15],
  "STEER_RES_PSFLD_T[°C]": [-40, 140],
}

class PDFdoc:
    def __init__(self, name="Unnamed PDF"):
        """
        Create an empty PDF document object with a name attribute. Name may but does not need to include '.pdf'.
        """
        self.pages = []
        if ".pdf" not in name:
            self.name = name + ".pdf"
        else:
            self.name = name
    
    def __str__(self):
        return("Document item\n  (name: {}, pages: {})".format(self.name, len(self.pages)))

    def add_page(self, page):
        """
        Attach a Page object to the PDF document object.
        """
        self.pages.append(page)

    def save(self, location="."):
        """
        Saves the PDF document object as a PDF file on the system. 
        """
        from matplotlib.backends.backend_pdf import PdfPages
        path = location+self.name
        if debugInfo:
            print("Save {}".format(path))
        with PdfPages(path) as pdf:
            for page in self.pages:
                page.save_to(pdf)

class Page:
    def __init__(self, title="Unnamed Page"):
        """
        Create an empty Page object with a title attribute.
        """
        self.items = []
        self.title = title
    
    def __str__(self):
        return("Page item\n  (title: {}, items: {})".format(self.title, len(self.items)))

    def set_title(self, title):
        """
        Override plot title. No return
        """
        self.title = title

    def add_plot(self, item):
        """
        Add a plot object to the page. No return
        """
        self.items.append(item)

    def save_to(self, pdfObj):
        """
        Save page to PDF object. No return
        """
        from matplotlib.gridspec import GridSpec
        fig, ax_hidden = plt.subplots(figsize=(8.5, 11))
        ax_hidden.axis('tight')
        ax_hidden.axis('off')
        gs = GridSpec(len(self.items), 1, hspace=0.1+max(0.2, len(self.items)*0.2-0.3))
        subax = []
        fig.suptitle(self.title)
        if debugInfo:
            print(" Save Page {}".format(self.title))
        for (i, item) in enumerate(self.items):
            subax.append(fig.add_subplot(gs[i]))
            item.render()
        pdfObj.savefig(fig)
        plt.close(fig)

class Plot:
    def __init__(self, type="line", data=[], legend = [], xlabel = "", 
                 ylabel = "", columns = [], infer_names = False, 
                 title = "Unnamed Plot", filterLength = 0, cols=default_color_palette):
        """
        Create a Plot object with type, data, legend, xlabel, ylabel, columns, and infer_names properties. 
          type: str in ["line", "scatter"]
          data: nested list with column-wise data
          legend: list of str to override the legend display
          xlabel, ylabel: str to override respective axis label
          columns: raw column data from a pd df to infer axis and legend names
          infer_names: bool to permit axis and legend name inference
        
        Changing values post-init should be done with the respective methods.
        """
        self.type = type.lower().strip()
        self.data = data
        self.legend = legend
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.columns = list(columns)
        self.grid = 'x'
        self.title= title
        self.filterLength = filterLength
        self.cols = cols
        if infer_names:
            self.infer_names()
    
    def __str__(self):
        return("Plot item\n  (type: {}, legend: {}, \n   xlabel: {}, ylabel: {},\n   grid: {})".format(self.type, self.legend, self.xlabel, self.ylabel, self.grid))

    def infer_names(self):
        """
        Passive method to infer names for signals and axis based on a provided columnset. 
        The plot should have a defined list of column names, *including* the x-axis (usually "t[s]")
        No return
        """
        if self.columns != []:
            names = []
            units = []
            for column in self.columns:
                if "[" in column:
                    names.append(column.split("[")[0])
                    units.append(column.split("[")[1].split("]")[0])
                else:
                    names.append(column)
                    units.append("")
        if len(names) > 2:
            self.legend = names[1:]
            self.xlabel = names[0] + "  [" + units[0] + "]"
            self.ylabel = units[1]
        elif len(names) == 2:
            self.legend = []
            self.xlabel = names[0] + "  [" + units[0] + "]"
            self.ylabel = names[1] + "  [" + units[1] + "]"
        else:
            self.legend = []
            self.xlabel = ""
            self.ylabel = ""
        if self.filterLength != 0:
            self.title = self.title + " [EMA{}]".format(self.filterLength)

    def no_legend(self):
        """
        Clears the legend from the plot
        """
        self.legend = []

    def set_legend(self, legend: list):
        """
        Sets the legend of the plot. Legend must be a list of strings.
        """
        self.legend = legend
    
    def no_xlabel(self):
        """
        Clears the xlabel from the plot.
        """
        self.xlabel = ""
    
    def set_xlabel(self, label: str):
        """
        Sets the xlabel of the plot. Label must be a string.
        """
        self.xlabel = label

    def no_ylabel(self):
        """
        Clears the ylabel from the plot.
        """
        self.ylabel = ""
    
    def set_ylabel(self, label: str):
        """
        Sets the ylabel of the plot. Label must be a string.
        """
        self.ylabel = label

    def set_grid(self, grid):
        """
        Set the plot's grid style to the provided; may be 'x', 'y', 'both', or 'none'.
        """
        if grid in ['none', 'both', 'x', 'y']:
            self.grid = grid
        else:
            self.grid = 'none'

    def no_grid(self):
        """
        Clears the grid from the plot.
        """
        self.grid = 'none'

    def render(self):
        """
        Renders the plot with the provided settings. 
        Change all plot settings prior to calling Plot.render().
        """

        setColorPalette(self.cols)

        # Render plot based on type
        match self.type:

            # Line plot
            case "line" | "lineplot":
                # Plot all chunks, with reduced opacity for the first (number of colors) items, unless only one item is present
                if len(self.data) > 1:
                    for i in range(1, len(self.data)):
                        if i <= len(cols):
                            plt.plot(self.data[0], self.data[i], color=getCol(i-1)+"D0")
                        else:
                            plt.plot(self.data[0], self.data[i], color=getCol(i-1), linestyle='--')
                else:
                    plt.plot(self.data[0], self.data[1], color=getCol(0))

            # Scatter plot
            case "scatter" | "scatterplot":
                # Plot all chunks, with varying opacity based on count of items
                for i in range(1, len(self.data)):
                    if i <= len(cols):
                        if len(self.data[0]) > 16000:
                            app = "28"
                        elif len(self.data[0]) > 8000:
                            app = "50"
                        elif len(self.data[0]) > 4000:
                            app = "8c"
                        else:
                            app = "af"
                        plt.scatter(self.data[0], self.data[i], color=getCol(i-1)+app, s=3)
                    else:
                        plt.scatter(self.data[0], self.data[i], color=getCol(i-1), s=3)

            # Dual-axis lineplot (two y-axes)
            case "dual" | "dualline":
                # Set up axes, trim to 95% width
                ax1 = plt.gca()
                ax2 = ax1.twinx()
                pos = ax2.get_position()
                ax2.set_position([pos.x0, pos.y0, pos.width * 0.95, pos.height])

                # Plot first chunk of data
                ax1.plot(self.data[0], self.data[1], color=getCol(0))

                # Plot all subsequent chunks of data
                for i in range(2, len(self.data)):
                    ax2.plot(self.data[0], self.data[i], color=getCol(i-1))
                
                # Override tick properties, label properties, and grid properties.
                ax1.set_ylabel(self.columns[1], color=getCol(0))
                ax2.set_ylabel(self.columns[2], color=getCol(1))
                ax1.tick_params(axis="y", colors=getCol(0), labelcolor=getCol(0))
                ax2.tick_params(axis="y", colors=getCol(1), labelcolor=getCol(1))
                ax1.grid(True, 'major', 'y')
                ax1.set_xlabel(self.xlabel)

                # Do some shenanigans to make axes align
                tickCount = 6
                y1_spread = ax1.get_ylim()[1] - ax1.get_ylim()[0]
                y2_spread = ax2.get_ylim()[1] - ax2.get_ylim()[0]
                y1_ticks = linspace(ax1.get_ylim()[0]-0.05*y1_spread, ax1.get_ylim()[1]+0.05*y1_spread, tickCount, True)
                y2_ticks = linspace(ax2.get_ylim()[0]-0.05*y2_spread, ax2.get_ylim()[1]+0.05*y2_spread, tickCount, True)
                ax1.set_yticks(y1_ticks)
                ax2.set_yticks(y2_ticks)
                
            # Map
            case "map":
                import geopandas as gpd
                import contextily as ctx
                # Get axes, transform data into a GDF
                ax = plt.gca()
                geometry = [Point(xy) for xy in zip(Series(self.data[1]), Series(self.data[2]))]
                gdf = gpd.GeoDataFrame(geometry=geometry, crs='EPSG:4326')

                # Plot the data
                try:
                    p = gdf.plot(
                        ax=ax, markersize=4, column=Series(self.data[0]),
                        cmap='coolwarm', marker='o', alpha=0.8, legend=True, label='GPS Track',
                        legend_kwds={'label': self.columns[0], 'location': 'bottom'}
                    )
                    max_x, max_y = max(self.data[1]), max(self.data[2])
                    min_x, min_y = min(self.data[1]), min(self.data[2])

                    span_x = max(max_x - min_x, 0.003)
                    mid_x = (max_x + min_x)/2
                    span_y = max(max_y - min_y, 0.003)
                    mid_y = (max_y + min_y)/2
                    span = max(span_x, span_y)*1.1
                    p.set_xlim([mid_x-span/1.8,  mid_x+span/1.8])
                    p.set_ylim([mid_y-span/2, mid_y+span/2])
                except Exception as e:
                    print("[{}] Failed to plot data.".format(str(e)))
                # Attempt to add a Contextily basemap (internet connection reqd.)
                try: 
                    ctx.add_basemap(ax, crs=gdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
                    if debugInfo:
                        print("   Basemap Added!")
                except Exception as e:
                    if debugInfo:
                        print(f"   Error loading basemap: {e}")
                    ax.text(0.5, 0.5, 'Basemap not available!',
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12, color='#7D0000')
                
                # Override labels, grid, and legend
                self.xlabel = 'Latitude'
                ax.set_xticklabels([])
                self.ylabel = 'Longitude'
                ax.set_yticklabels([])
                self.grid   = 'none'
                self.legend = []

            # Table
            case "table":

                # Default cells + warning indices
                cellText = []
                warning = [[False, False, False, False]]

                # Loop to acquire warning data and fill cell data
                for i in range(1, len(self.data)):
                    if debugInfo:
                        print("{}\n Max: {:6.1f}   Min: {:6.1f}   Mean: {:6.1f}".format(self.columns[i], 
                                                                                    max(self.data[i]), 
                                                                                    min(self.data[i]), 
                                                                                    sum(self.data[i])/len(self.data[i])))
                    avg = round(sum(self.data[i])/len(self.data[i]), 3)
                    cellText.append([self.columns[i], round(max(self.data[i]), 2), 
                                     round(min(self.data[i]), 2), 
                                     avg])
                    warnAppend = [False, False, False, False]

                    # Check integrated SLC file
                    if self.columns[i] in slc:
                        if max(self.data[i]) > slc[self.columns[i]][1] or max(self.data[i]) < slc[self.columns[i]][0]:
                            warnAppend[1] = True
                        if min(self.data[i]) < slc[self.columns[i]][0] or min(self.data[i]) > slc[self.columns[i]][1]:
                            warnAppend[2] = True
                        if avg < slc[self.columns[i]][0] or avg > slc[self.columns[i]][1]:
                            warnAppend[3] = True
                        if any(warnAppend) and debugInfo:
                            print(" -- WARNING -- ")
                    
                    # Add warning array (likely all False)
                    warning.append(warnAppend)
                
                # Remove axis and plot
                plt.axis('off')
                ax = plt.gca()
                table = ax.table(cellText=cellText, colLabels=['Signal', 'Maximum', 'Minimum', 'Mean'], loc='center', colWidths=[0.4, 0.175, 0.175, 0.175], colLoc='right')
                
                # Scale cells
                table.scale(1, 1.6)
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                from matplotlib.font_manager import FontProperties

                # Apply heading formatting, and conditional warnings
                for (row, col), cell in table.get_celld().items():
                    cell.set_linewidth(0)
                    if row == 0:  # Check if it's a header row cell
                        cell.set_text_props(fontproperties=FontProperties(weight='bold'))
                    elif col == 0:
                        cell.set_text_props(color="#1F1F1F")
                    elif warning[row][col]:
                        cell.set_text_props(color="#7D0000", fontproperties=FontProperties(weight='bold'))
                    else:
                        cell.set_text_props(color="#3E3E3E")
                
                # Obliterate spines, labels, and ticks
                plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
                plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
                for pos in ['right','top','bottom','left']:
                    plt.gca().spines[pos].set_visible(False)
            
            # Histogram
            case "histogram" | "hist":
                # plot
                plt.grid(True, 'major', 'y', color='#000000')
                x, bins, p = plt.hist(self.data[0], color=cols[0], histtype='bar', linewidth=0.5, edgecolor="white")
                plt.xticks(bins)

                # Override y-label
                self.ylabel = "Count"
            
            # Histogram (Percentage, normalized)
            case "histogrampct" | "histpct":
                # plot
                plt.grid(True, 'major', 'y', color='#000000')
                x, bins, p = plt.hist(self.data[0], color=cols[0], histtype='bar', linewidth=0.5, edgecolor="white")

                # Override y-label and manipulate title
                self.ylabel = "Percent"
                self.title += " (Normalized)"

                # Acquire desired bin height by normalizing
                heightTotal = 0
                for item in p:
                    heightTotal += item.get_height()
                for item in p:
                    item.set_height(100*item.get_height()/heightTotal)
                
                # Set new y-limits and bin labels
                plt.xticks(bins)
                plt.ylim(0, 100)
        
        # Set plot title
        plt.title(self.title)

        # Set plot properties based on plot type and data available
        if self.type not in ['dual', 'dualline', 'table']:
            if self.legend != [] and len(self.data) > 2:
                plt.legend(self.legend, loc="upper left", fontsize=8)
            if self.xlabel != "":
                plt.xlabel(self.xlabel)
            if self.ylabel != "":
                plt.ylabel(self.ylabel)
            if self.grid != 'none' and 'hist' not in self.type:
                plt.grid(visible=True, axis=self.grid, which='major')
            elif 'hist' not in self.type:
                plt.grid(visible=False)

def fixConfig(config_old: dict):
    """
    Configuration checker and correcter; used internally to ensure uniformity.
    """

    config = config_old.copy()
    if "docTitle" not in config:
        config["docTitle"] = "UNNAMED DOCUMENT TITLE"
    if "dataRange" not in config or not isinstance("dataRange", list):
        config["dataRange"] = [0, -1]
    if "docSubTitle" not in config:
        config["docSubTitle"] = "UNNAMED DOCUMENT SUBTITLE"
    if "pages" not in config:
        config["pages"] = []
    for page in config["pages"]:
        if "pageName" not in page:
            page["pageName"] = "UNNAMED PAGE NAME"
        if "plots" not in page:
            page["plots"] = []
        for plot in page["plots"]:
            if "plotTitle" not in plot:
                plot["plotTitle"] = "UNNAMED PLOT"
            if "plotType" not in plot:
                plot["plotType"] = ""
            if "cols" not in plot:
                plot["cols"] = default_color_palette
            if "xData" not in plot:
                plot["xData"] = ""
            if "yData" not in plot:
                plot["yData"] = [""]
            elif not isinstance(plot["yData"], list):
                plot["yData"] = [plot["yData"]]
            if "filterLength" not in plot or plot["filterLength"] == False:
                plot["filterLength"] = 0
            elif plot["filterLength"] == True:
                plot["filterLength"] = 30
            else:
                plot["filterLength"] = int(plot["filterLength"])
    return config

def createDocument(df: DataFrame, config: dict, save_path: str=os.path.expanduser("~")+"\\"):
    """
    Creates, manages, and saves a document given a dataset and configuration file.
    Check documentation for information on config structure. 
    If no save path is specified, defaults to the user's home directory (C:\\Users\\USERNAME\\)
    """
    
    cfg = fixConfig(config)
    data = gu.dfRows(df.copy(), cfg['dataRange'][0], cfg['dataRange'][-1])

    # print("\n-- Metadata --\n\n Document Title: {}\n Document Subtitle: {}".format(cfg['docTitle'], cfg['docSubTitle']))
    # print("\n\n-- Pages --")
    cd_document = PDFdoc(cfg['docTitle'])

    for (i, page) in enumerate(cfg['pages']):
        # print("\n- Page "+str(i+1))
        # print("  Name: {}\n  Number of plots: {}".format(page['pageName'], len(page['plots'])))
        cd_page = Page("{}\n{}".format(cfg['docSubTitle'],page['pageName']))

        for (x, plot) in enumerate(page['plots']):
            # print("\n--  Plot "+str(x+1))
            # print("    Title: {}\n    Type: {}".format(plot['plotTitle'], plot['plotType']))
            # print("    x data: '{}'\n    y data: {}\n    Filter Length: {}".format(plot['xData'], 
            # plot['yData'], plot['filterLength']))
            toPlot = gu.formatData(data, signal_x=plot['xData'], signals_y=plot['yData'])
            if debugInfo:
                print('{} {} {}'.format(i, plot['plotTitle'], toPlot[0][0:5]))
            if plot['filterLength'] > 0:
                toPlot = gu.applyFilter(toPlot, span=plot['filterLength'])
            cd_plot = Plot(type=plot["plotType"], data=toPlot, 
                           columns=(gu.parseNames(data.columns, plot['xData'])+gu.parseNames(data.columns, plot['yData'])), 
                           title=plot['plotTitle'], filterLength=plot['filterLength'], cols=plot["cols"])
            cd_plot.infer_names()
            cd_plot.set_grid('y')
            cd_page.add_plot(cd_plot)
            del cd_plot
        
        cd_document.add_page(cd_page)
        del cd_page

    cd_document.save(save_path)
