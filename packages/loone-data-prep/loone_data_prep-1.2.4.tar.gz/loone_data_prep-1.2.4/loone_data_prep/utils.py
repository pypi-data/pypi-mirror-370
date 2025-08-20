import sys
import os
import datetime
import math
from glob import glob
from calendar import monthrange
import traceback
import numpy as np
import pandas as pd
from retry import retry
from scipy.optimize import fsolve
from scipy import interpolate
from rpy2.robjects import r
from rpy2.robjects.vectors import (
    StrVector as rpy2StrVector,
    DataFrame as rpy2DataFrame,
)
from rpy2.rinterface_lib.embedded import RRuntimeError


DEFAULT_STATION_IDS = ["L001", "L005", "L006", "LZ40"]
INTERP_DICT = {
    "PHOSPHATE, TOTAL AS P": {
        "units": "mg/L",
        "station_ids": [
            "S65E",
            "FECSR78",
            "CULV10A",
            "S71",
            "S72",
            "S84",
            "S127",
            "S133",
            "S135",
            "S154",
            "S191",
            "S308C",
            "S4",
            "L001",
            "L004",
            "L005",
            "L006",
            "L007",
            "L008",
            "LZ40",
        ],
    },
    "PHOSPHATE, ORTHO AS P": {
        "units": "mg/L",
        "station_ids": [
            "L001",
            "L004",
            "L005",
            "L006",
            "L007",
            "L008",
            "LZ40",
        ],
    },
    "NITRATE+NITRITE-N": {
        "units": "mg/L",
        "station_ids": [
            "S65E",
            "FECSR78",
            "CULV10A",
            "S71",
            "S72",
            "S84",
            "S127",
            "S133",
            "S135",
            "S154",
            "S191",
            "S308C",
            "S4",
            "L001",
            "L004",
            "L005",
            "L006",
            "L007",
            "L008",
            "LZ40",
        ],
    },
    "AMMONIA-N": {
        "units": "mg/L",
        "station_ids": [
            "S65E",
            "FECSR78",
            "CULV10A",
            "S71",
            "S72",
            "S84",
            "S127",
            "S133",
            "S135",
            "S154",
            "S191",
            "S308C",
            "S4",
            "L001",
            "L004",
            "L005",
            "L006",
            "L007",
            "L008",
            "LZ40",
        ],
    },
    "CHLOROPHYLL-A(LC)": {
        "units": "ug/L",
        "station_ids": [
            "S65E",
            "FECSR78",
            "CULV10A",
            "S71",
            "S72",
            "S84",
            "S127",
            "S133",
            "S135",
            "S154",
            "S191",
            "S308C",
            "S4",
            "L001",
            "L004",
            "L005",
            "L006",
            "L007",
            "L008",
            "LZ40",
        ],
    },
    "CHLOROPHYLL-A, CORRECTED": {
        "units": "ug/L",
        "station_ids": [
            "S65E",
            "FECSR78",
            "CULV10A",
            "S71",
            "S72",
            "S84",
            "S127",
            "S133",
            "S135",
            "S154",
            "S191",
            "S308C",
            "S4",
            "L001",
            "L004",
            "L005",
            "L006",
            "L007",
            "L008",
            "LZ40",
        ],
    },
    "DISSOLVED OXYGEN": {
        "units": "mg/L",
        "station_ids": [
            "L001",
            "L004",
            "L005",
            "L006",
            "L007",
            "L008",
            "LZ40",
        ],
    },
    "RADP": {
        "units": "MICROMOLE/m^2/s",
        "station_ids": ["L001", "L005", "L006", "LZ40"],
    },
    "RADT": {
        "units": "kW/m^2",
        "station_ids": ["L001", "L005", "L006", "LZ40"],
    },
}
DEFAULT_PREDICTION_STATIONS_IDS = [
    "S65E_S",
    "S71_S",
    "S72_S",
    "S191_S",
    "FISHP",
    "S4_P",
    "S84_S",
    "S127_P",
    "S127_C",
    "S133_P",
    "S154_C",
    "S135_P",
    "S135_C",
]
DEFAULT_EXPFUNC_PHOSPHATE_CONSTANTS = {
    "S65E_S": {"a": 2.00040151533473, "b": 0.837387838314323},
    "S71_S": {"a": 2.55809777403484, "b": 0.765894033054918},
    "S72_S": {"a": 2.85270576092534, "b": 0.724935760736887},
    "S191_S": {"a": 3.0257439276073, "b": 0.721906661127014},
    "FISHP": {"a": 2.59223308404186, "b": 0.756802713030507},
    "S4_P": {"a": 2.86495657296006, "b": 0.72203267810211},
    "S84_S": {"a": 2.53265243618408, "b": 0.750938593484588},
    "S127_P": {"a": 2.34697955615531, "b": 0.794046635942522},
    "S127_C": {"a": 2.73825064156312, "b": 0.715023290260209},
    "S133_P": {"a": 2.64107054734111, "b": 0.756152588482486},
    "S154_C": {"a": 3.10305150879462, "b": 0.7099895764193},
    "S135_P": {"a": 2.50975664040355, "b": 0.760702496334553},
    "S135_C": {"a": 2.43076251736749, "b": 0.759494593788417},
}
DEFAULT_EXPFUNC_NITROGEN_CONSTANTS = {
    "FISHP": {"a": 3.45714698709252, "b": 0.592252136022012},
    "S4_P": {"a": 1.2337557014752, "b": 1.04595934798695},
    "S65E_S": {"a": 4.71575889172016, "b": 0.505549283553318},
    "S71_S": {"a": 3.97701995028333, "b": 0.606281118481932},
    "S72_S": {"a": 2.36651051985955, "b": 0.774589654354149},
    "S84_S": {"a": 2.69855941365441, "b": 0.697201188144741},
    "S127_C": {"a": 2.22368957908813, "b": 0.758610540522343},
    "S127_P": {"a": 2.19477310222979, "b": 0.786485799309641},
    "S133_P": {"a": 1.79092549100026, "b": 0.882497515298829},
    "S154_C": {"a": 2.88850639994145, "b": 0.665252221554856},
    "S191_S": {"a": 3.99798269355392, "b": 0.586177156114969},
    "S135_C": {"a": 6.44418674308781, "b": 0.322821841402605},
    "S135_P": {"a": 3.09890183766129, "b": 0.657896838486496},
}

@retry(RRuntimeError, tries=5, delay=15, max_delay=60, backoff=2)
def get_dbkeys(
    station_ids: list,
    category: str,
    param: str,
    stat: str,
    recorder: str,
    freq: str = "DA",
    detail_level: str = "dbkey",
    *args: str,
) -> rpy2StrVector | rpy2DataFrame:
    """Get dbkeys. See DBHydroR documentation for more information:
    https://cran.r-project.org/web/packages/dbhydroR/dbhydroR.pdf

    Args:
        station_ids (list): List of station IDs.
        category (str): Category of data to retrieve. Options are "WEATHER", "SW", "GW", or "WQ".
        param (str): Parameter of data to retrieve.
        stat (str): Statistic of data to retrieve.
        recorder (str): Recorder of data to retrieve.
        freq (str, optional): Frequency of data to retrieve. Defaults to "DA".
        detail_level (str, optional): Detail level of data to retrieve. Defaults to "dbkey". Options are "dbkey",
            "summary", or "full".

    Returns:
        rpy2StrVector | rpy2DataFrame: dbkeys info at the specified detail level.
    """

    station_ids_str = '"' + '", "'.join(station_ids) + '"'

    dbkeys = r(
        f"""
        library(dbhydroR)

        station_ids <- c({station_ids_str})
        dbkeys <- get_dbkey(stationid = station_ids,  category = "{category}", param = "{param}", stat = "{stat}", recorder="{recorder}", freq = "{freq}", detail.level = "{detail_level}")
        print(dbkeys)
        return(dbkeys)
        """  # noqa: E501
    )

    return dbkeys


def data_interpolations(
    workspace: str,
    parameter: str = "RADP",
    units: str = "MICROMOLE/m^2/s",
    station_ids: list = DEFAULT_STATION_IDS,
    *args: str,
) -> None:
    """
    Args:
        workspace (str): _description_
        station (list, optional): Defaults to '["L001", "L005", "L006", "LZ40"]'.
        parameter (str, optional): NITRATE+NITRITE-N, AMMONIA-N, PHOSPHATE, TOTAL AS P, PHOSPHATE, ORTHO AS P,
            CHLOROPHYLL-A, CORRECTED, CHLOROPHYLL-A(LC), RADP. Defaults to 'RADP'.
        units (str, optional): mg/L, ug/L, MICROMOLE/m^2/s. Defaults to 'MICROMOLE/m^2/s'.
    """

    for station in station_ids:
        name = f"{station}_{parameter}"
        path = f"{workspace}/{name}.csv"

        if not os.path.exists(path):
            name = f"water_quality_{name}"
            path = f"{workspace}/{name}.csv"
            if not os.path.exists(path):
                print(f'Skipping "{name}" File does not exist.')
                continue

        Data_In = pd.read_csv(path)

        # check there is more than one row in the file for interpolation.
        if len(Data_In.iloc[:]) < 10:
            print(f'"{name}" file does not have enough values to interpolate.')
            continue

        Data_In = Data_In.set_index(["date"])
        Data_In.index = pd.to_datetime(Data_In.index, unit="ns")
        Data_df = Data_In.resample("D").mean()
        Data_df = Data_df.dropna(
            subset=["%s_%s_%s" % (station, parameter, units)]
        )
        Data_df = Data_df.reset_index()
        Data_df["Yr_M"] = pd.to_datetime(Data_df["date"]).dt.to_period("M")
        start_date = Data_df["date"].iloc[0]
        end_date = Data_df["date"].iloc[-1]
        date_rng = pd.date_range(start=start_date, end=end_date, freq="ME")
        Monthly_df = pd.DataFrame(date_rng, columns=["date"])
        Monthly_df["Yr_M"] = pd.to_datetime(Monthly_df["date"]).dt.to_period(
            "M"
        )
        New_date = []
        New_data = []
        Days = []
        Days_cum = []
        # Set index for the two dataframes
        Data_df = Data_df.set_index(["Yr_M"])
        Monthly_df = Monthly_df.set_index(["Yr_M"])
        for i in Monthly_df.index:
            if i in Data_df.index:
                if type(Data_df.loc[i]["date"]) == pd.Timestamp:
                    New_date.append(Data_df.loc[i]["date"])
                    New_data.append(
                        Data_df.loc[i][
                            "%s_%s_%s" % (station, parameter, units)
                        ]
                    )
                else:
                    for j in range(len(Data_df.loc[i]["date"])):
                        New_date.append(Data_df.loc[i]["date"][j])
                        New_data.append(
                            Data_df.loc[i][
                                "%s_%s_%s" % (station, parameter, units)
                            ][j]
                        )
            elif i not in Data_df.index:
                New_date.append(
                    datetime.datetime(
                        Monthly_df.loc[i]["date"].year,
                        Monthly_df.loc[i]["date"].month,
                        1,
                    )
                )
                New_data.append(np.NaN)

        New_date = pd.to_datetime(New_date, format="%Y-%m-%d")
        Days = New_date.strftime("%d").astype(float)
        for i in range(len(Days)):
            if i == 0:
                Days_cum.append(Days[i])
            elif New_date[i].month == New_date[i - 1].month:
                Days_cum.append(Days_cum[i - 1] + (Days[i] - Days[i - 1]))
            elif New_date[i].month != New_date[i - 1].month:
                Days_cum.append(
                    Days_cum[i - 1]
                    + Days[i]
                    + monthrange(New_date[i - 1].year, New_date[i - 1].month)[
                        1
                    ]
                    - Days[i - 1]
                )
        Final_df = pd.DataFrame()
        Final_df["date"] = New_date
        Final_df["Data"] = New_data
        Final_df["Days"] = Days
        Final_df["Days_cum"] = Days_cum
        # Final_df.to_csv('C:/Work/Research/LOONE/Nitrogen Module/Interpolated_Data/In-Lake/L008_DO_No_Months_Missing_Trial.csv')  # noqa: E501
        # Remove Negative Data Values
        Final_df = Final_df[Final_df["Data"] >= 0]
        Final_df["date"] = pd.to_datetime(Final_df["date"], format="%Y-%m-%d")
        start_date = Final_df["date"].iloc[0]
        end_date = Final_df["date"].iloc[-1]
        date_rng_TSS_1 = pd.date_range(
            start=start_date, end=end_date, freq="D"
        )
        # Create a data frame with a date column
        Data_df = pd.DataFrame(date_rng_TSS_1, columns=["date"])
        Data_len = len(Data_df.index)
        Cum_days = np.zeros(Data_len)
        Data_daily = np.zeros(Data_len)
        # Set initial values
        Cum_days[0] = Data_df["date"].iloc[0].day
        Data_daily[0] = Final_df["Data"].iloc[0]
        for i in range(1, Data_len):
            Cum_days[i] = Cum_days[i - 1] + 1
            # Data_daily[i] = interpolate.interp1d(Final_df['Days'], Final_df['TSS'] , kind = 'linear')(Cum_days[i])
            Data_daily[i] = np.interp(
                Cum_days[i], Final_df["Days_cum"], Final_df["Data"]
            )
        Data_df["Data"] = Data_daily
        Data_df.to_csv(f"{workspace}/{name}_Interpolated.csv", index=False)


def interpolate_all(workspace: str, d: dict = INTERP_DICT) -> None:
    """Interpolate all needed files for Lake Okeechobee

    Args:
        workspace (str): Path to files location.
        d (dict, optional): Dict with parameter key, units, and station IDs. Defaults to INTERP_DICT.
    """
    for param, values in d.items():
        print(
            f"Interpolating parameter: {param} for station IDs: {values['station_ids']}."
        )
        data_interpolations(
            workspace, param, values["units"], values["station_ids"]
        )


def kinematic_viscosity(
    workspace: str, in_file_name: str, out_file_name: str = "nu.csv"
):
    # Read Mean H2O_T in LO
    LO_Temp = pd.read_csv(os.path.join(workspace, in_file_name))
    LO_T = LO_Temp["Water_T"]

    n = len(LO_T.index)

    class nu_Func:
        def nu(T):
            nu20 = (
                1.0034 / 1e6
            )  # m2/s (kinematic viscosity of water at T = 20 C)

            def func(x):
                # return[log(x[0]/nu20)-((20-T)/(T+96))*(1.2364-1.37E-3*(20-T)+5.7E-6*(20-T)**2)]
                return [
                    (x[0] / nu20)
                    - 10
                    ** (
                        ((20 - T) / (T + 96))
                        * (
                            1.2364
                            - 1.37e-3 * (20 - T)
                            + 5.7e-6 * (20 - T) ** 2
                        )
                    )
                ]

            sol = fsolve(func, [9.70238995692062e-07])
            nu = sol[0]
            return nu

    nu = np.zeros(n, dtype=object)

    for i in range(n):
        nu[i] = nu_Func.nu(LO_T[i])

    nu_df = pd.DataFrame(LO_Temp["date"], columns=["date"])
    nu_df["nu"] = nu
    nu_df.to_csv(os.path.join(workspace, out_file_name), index=False)


def wind_induced_waves(
    input_dir: str,
    output_dir: str,
    wind_speed_in: str = "LOWS.csv",
    lo_stage_in: str = "LO_Stg_Sto_SA_2008-2023.csv",
    wind_shear_stress_out: str = "WindShearStress.csv",
    current_shear_stress_out: str = "Current_ShearStress.csv",
    forecast: bool = False,
):
    # Read Mean Wind Speed in LO
    LO_WS = pd.read_csv(os.path.join(f"{input_dir}/", wind_speed_in))
    LO_WS["WS_mps"] = LO_WS["LO_Avg_WS_MPH"] * 0.44704  # MPH to m/s
    # Read LO Stage to consider water depth changes
    LO_Stage = pd.read_csv(os.path.join(f"{input_dir}/", lo_stage_in))
    if forecast:
        LO_Stage["Stage_ft"] = LO_Stage["Stage"].astype(float)
    LO_Stage["Stage_m"] = LO_Stage["Stage_ft"] * 0.3048
    Bottom_Elev = 0.5  # m (Karl E. Havens • Alan D. Steinman 2013)
    LO_Wd = LO_Stage["Stage_m"] - Bottom_Elev
    g = 9.81  # m/s2 gravitational acc
    # d = 1.5  # m  LO Mean water depth
    F = 57500  # Fetch length of wind (m) !!!!!!
    nu = 1.0034 / 1e6  # m2/s (kinematic viscosity of water at T = 20 C)
    ru = 1000  # kg/m3

    n = len(LO_WS.index)

    class Wind_Func:
        def H(g, d, F, WS):
            H = (
                (
                    0.283
                    * np.tanh(0.53 * (g * d / WS**2) ** 0.75)
                    * np.tanh(
                        0.00565
                        * (g * F / WS**2) ** 0.5
                        / np.tanh(0.53 * (g * d / WS**2) ** (3 / 8))
                    )
                )
                * WS**2
                / g
            )  # noqa: E501
            return H

        def T(g, d, F, WS):
            T = (
                (
                    7.54
                    * np.tanh(0.833 * (g * d / WS**2) ** (3 / 8))
                    * np.tanh(
                        0.0379
                        * (g * F / WS**2) ** 0.5
                        / np.tanh(0.833 * (g * d / WS**2) ** (3 / 8))
                    )
                )
                * WS
                / g
            )  # noqa: E501
            return T

        def L(g, d, T):
            def func(x):
                return [
                    (g * T**2 / 2 * np.pi) * np.tanh(2 * np.pi * d / x[0])
                    - x[0]
                ]

            sol = fsolve(func, [1])
            L = sol[0]
            return L

    W_H = np.zeros(n, dtype=object)
    W_T = np.zeros(n, dtype=object)
    W_L = np.zeros(n, dtype=object)
    W_ShearStress = np.zeros(n, dtype=object)
    for i in range(n):
        W_H[i] = Wind_Func.H(g, LO_Wd[i], F, LO_WS["WS_mps"].iloc[i])
        W_T[i] = Wind_Func.T(g, LO_Wd[i], F, LO_WS["WS_mps"].iloc[i])
        W_L[i] = Wind_Func.L(g, LO_Wd[i], W_T[i])
        W_ShearStress[i] = (
            W_H[i]
            * (ru * (nu * (2 * np.pi / W_T[i]) ** 3) ** 0.5)
            / (2 * np.sinh(2 * np.pi * LO_Wd[i] / W_L[i]))
        )

    Wind_ShearStress = pd.DataFrame(LO_WS["date"], columns=["date"])
    Wind_ShearStress["ShearStress"] = (
        W_ShearStress * 10
    )  # Convert N/m2 to Dyne/cm2
    Wind_ShearStress.to_csv(
        os.path.join(output_dir, wind_shear_stress_out), index=False
    )

    # # Monthly
    # Wind_ShearStress['Date'] = pd.to_datetime(Wind_ShearStress['Date'])
    # Wind_ShearStress_df = pd.DataFrame()
    # Wind_ShearStress_df['Date'] = Wind_ShearStress['Date'].dt.date
    # Wind_ShearStress_df['ShearStress'] = pd.to_numeric(Wind_ShearStress['ShearStress'])
    # Wind_ShearStress_df = Wind_ShearStress_df.set_index(['Date'])
    # Wind_ShearStress_df.index = pd.to_datetime(Wind_ShearStress_df.index, unit = 'ns')
    # Wind_ShearStress_df = Wind_ShearStress_df.resample('M').mean()
    # Wind_ShearStress_df.to_csv('C:/Work/Research/Data Analysis/Lake_O_Weather_Data/WindSpeed_Processed/WindShearStress_M.csv')  # noqa: E501

    # The drag coefficient
    CD = 0.001 * (0.75 + 0.067 * LO_WS["WS_mps"])
    air_ru = 1.293  # kg/m3

    def tau_w(WS, CD, air_ru):
        tau_w = air_ru * CD * (WS**2)
        return tau_w

    def Current_bottom_shear_stress(ru, tau_w):
        # Constants
        kappa = 0.41  # Von Karman constant
        # Calculate the bottom friction velocity
        u_b = math.sqrt(tau_w / ru)
        # Calculate the bottom shear stress
        tau_b = ru * kappa**2 * u_b**2
        return tau_b

    Current_Stress = np.zeros(n, dtype=object)
    Wind_Stress = np.zeros(n, dtype=object)
    for i in range(n):
        Wind_Stress[i] = tau_w(LO_WS["WS_mps"].iloc[i], CD[i], air_ru)
        Current_Stress[i] = Current_bottom_shear_stress(ru, Wind_Stress[i])

    Current_ShearStress_df = pd.DataFrame(LO_WS["date"], columns=["date"])
    Current_ShearStress_df["Current_Stress"] = (
        Current_Stress * 10
    )  # Convert N/m2 to Dyne/cm2
    Current_ShearStress_df["Wind_Stress"] = (
        Wind_Stress * 10
    )  # Convert N/m2 to Dyne/cm2
    Current_ShearStress_df["Wind_Speed_m/s"] = LO_WS["WS_mps"]

    def Current_bottom_shear_stress_2(u, k, nu, ks, z, ru):
        def func1(u_str1):
            return [u_str1[0] - u * k * np.exp(z / (0.11 * nu / u_str1[0]))]

        sol1 = fsolve(func1, [1])

        def func2(u_str2):
            return [u_str2[0] - u * k * np.exp(z / (0.0333 * ks))]

        sol2 = fsolve(func2, [1])

        def func3(u_str3):
            return [
                u_str3[0]
                - u * k * np.exp(z / ((0.11 * nu / u_str3[0]) + 0.0333 * ks))
            ]

        sol3 = fsolve(func3, [1])
        if sol1[0] * ks / nu <= 5:
            u_str = sol1[0]
        elif sol2[0] * ks / nu >= 70:
            u_str = sol2[0]
        elif sol3[0] * ks / nu > 5 and sol3[0] * ks / nu < 70:
            u_str = sol3[0]
        tau_c = ru * u_str**2
        return tau_c

    def Current_bottom_shear_stress_3(u, k, nu, ks, z, ru):
        def func1(u_str1):
            return [
                u_str1[0] - u * k * (1 / np.log(z / (0.11 * nu / u_str1[0])))
            ]

        sol1 = fsolve(func1, [1])

        def func2(u_str2):
            return [u_str2[0] - u * k * (1 / np.log(z / (0.0333 * ks)))]

        sol2 = fsolve(func2, [1])

        def func3(u_str3):
            return [
                u_str3[0]
                - u
                * k
                * (1 / np.log(z / ((0.11 * nu / u_str3[0]) + 0.0333 * ks)))
            ]

        sol3 = fsolve(func3, [1])
        if sol1[0] * ks / nu <= 5:
            u_str = sol1[0]
        elif sol2[0] * ks / nu >= 70:
            u_str = sol2[0]
        elif sol3[0] * ks / nu > 5 and sol3[0] * ks / nu < 70:
            u_str = sol3[0]
        else:
            u_str = 0
        tau_c = ru * u_str**2
        return tau_c

    ks = 5.27e-4  # m
    current_stress_3 = np.zeros(n, dtype=object)
    for i in range(n):
        current_stress_3[i] = Current_bottom_shear_stress_3(
            0.05, 0.41, nu, ks, LO_Wd[i], ru
        )
    Current_ShearStress_df["Current_Stress_3"] = (
        current_stress_3 * 10
    )  # Convert N/m2 to Dyne/cm2
    Current_ShearStress_df.to_csv(
        os.path.join(output_dir, current_shear_stress_out), index=False
    )


def stg2sto(
    stg_sto_data_path: str, v: pd.Series, i: int
) -> interpolate.interp1d:
    stgsto_data = pd.read_csv(stg_sto_data_path)
    # NOTE: We Can use cubic interpolation instead of linear
    x = stgsto_data["Stage"]
    y = stgsto_data["Storage"]
    if i == 0:
        # return storage given stage
        return interpolate.interp1d(
            x, y, fill_value="extrapolate", kind="linear"
        )(v)
    else:
        # return stage given storage
        return interpolate.interp1d(
            y, x, fill_value="extrapolate", kind="linear"
        )(v)


def stg2ar(stgar_data_path: str, v: pd.Series, i: int) -> interpolate.interp1d:
    import pandas as pd
    from scipy import interpolate

    stgar_data = pd.read_csv(stgar_data_path)
    # NOTE: We Can use cubic interpolation instead of linear
    x = stgar_data["Stage"]
    y = stgar_data["Surf_Area"]
    if i == 0:
        # return surface area given stage
        return interpolate.interp1d(
            x, y, fill_value="extrapolate", kind="linear"
        )(v)
    else:
        # return stage given surface area
        return interpolate.interp1d(
            y, x, fill_value="extrapolate", kind="linear"
        )(v)


@retry(Exception, tries=3, delay=15, backoff=2)
def get_pi(workspace: str) -> None:
    # Weekly data is downloaded from:
    # https://www.ncei.noaa.gov/access/monitoring/weekly-palmers/pdi-0804.csv
    # State:Florida Division:4.South Central
    df = pd.read_csv(
        "https://www.ncei.noaa.gov/access/monitoring/weekly-palmers/pdi-0804.csv"
    )
    df.to_csv(os.path.join(workspace, "PI.csv"))


def nutrient_prediction(
    input_dir: str,
    output_dir: str,
    station_ids: dict = DEFAULT_PREDICTION_STATIONS_IDS,
    constants: dict = DEFAULT_EXPFUNC_PHOSPHATE_CONSTANTS,
    nutrient: str = "PHOSPHATE",
) -> None:
    """Predict nutrient loads for the given station IDs.
    
    Args:
        input_dir (str): Path to the directory where the input files are located.
        output_dir (str): Path to the directory where the output files will be saved.
        station_ids (list, optional): List with station IDs to do predictions for. Defaults to DEFAULT_PREDICTION_STATIONS_IDS.
        constants (dict, optional): Dictionary with constants for the exponential function. Defaults to DEFAULT_EXPFUNC_PHOSPHATE_CONSTANTS.
        nutrient (str, optional): Nutrient to predict. Defaults to "PHOSPHATE". Options are "PHOSPHATE" or "NITROGEN".
    """
    for station in station_ids:
        print(f"Predicting nutrient loads for station: {station}.")
        # Construct paths for flow file
        flow_file_path = ""
        flow_file_path_exists = True
        # Manually define matches for forecast case
        station_file_map = {
            'S65E_S': f"{input_dir}/750072741_INFLOW_cmd_geoglows.csv",
            'S71_S': f"{input_dir}/750068601_MATCHED_cmd_geoglows.csv",
            'FISHP': f"{input_dir}/750053213_MATCHED_cmd_geoglows.csv",
            'S84_S': f"{input_dir}/750069782_INFLOW_cmd_geoglows.csv",
            'S133_P': f"{input_dir}/750035446_INFLOW_cmd_geoglows.csv",
            'S154_C': f"{input_dir}/750064453_INFLOW_cmd_geoglows.csv",
            'S135_P': f"{input_dir}/750052624_MATCHED_cmd_geoglows.csv",
            'S135_C': f"{input_dir}/750052624_MATCHED_cmd_geoglows.csv",
        }

        if station in station_file_map:
            flow_file_path = station_file_map[station]
            if os.path.exists(flow_file_path):
                flow = pd.read_csv(flow_file_path)
            else:
                print(
                    f"Skipping nutrient prediction for station: {station}. Forecast file path does not exist."
                )
                continue
        else:
            print(
                f"Skipping nutrient prediction for station: {station}. No forecast match defined."
            )
            continue

        # Create structures to hold resulting data
        out_dataframe = pd.DataFrame(index=flow["date"].copy())
        prediction_columns = [out_dataframe]

        # Run predictions for each ensemble
        for column_name in flow.columns:
            if "ensemble" not in column_name:
                continue
            import warnings

            warnings.filterwarnings("error")

            try:
                # Get the current ensemble as an individual pandas DataFrame
                flow_column = flow.loc[:, column_name]

                # Calculate the logarithm of the flow data

                Q_Log = np.log(
                    flow_column + 1e-8
                )  # Add a small number to prevent log(0) errors

                # Calculate the predicted TP loads using the logarithm of the flow data
                TP_Loads_Predicted_Log = (
                    constants[station]["a"] * Q_Log ** constants[station]["b"]
                )

                # Calculate the predicted TP loads using the exponential of the predicted TP loads logarithm
                predicted_column = np.exp(TP_Loads_Predicted_Log)

                # Store prediction data in a pandas DataFrame (So we can concat all ensemble data into one dataframe)
                predicted_column = pd.DataFrame(
                    predicted_column.tolist(), index=flow["date"].copy()
                )
                predicted_column.columns = [column_name]

                prediction_columns.append(predicted_column)
            except RuntimeWarning as e:
                print(f"Unexpected RuntimeWarning: {str(e)}")
                traceback.print_exc()

        # Concat individual ensemble columns together into one pandas DataFrame
        out_dataframe = pd.concat(objs=prediction_columns, axis="columns")

        column_mean = out_dataframe.mean(axis="columns")
        column_percentile_25 = out_dataframe.quantile(q=0.25, axis="columns")
        column_percentile_75 = out_dataframe.quantile(q=0.75, axis="columns")
        column_median = out_dataframe.median(axis="columns")
        column_std = out_dataframe.std(axis="columns")

        out_dataframe["mean"] = column_mean
        out_dataframe["percentile_25"] = column_percentile_25
        out_dataframe["percentile_75"] = column_percentile_75
        out_dataframe["median"] = column_median
        out_dataframe["standard_deviation"] = column_std

        # Save the predicted TP loads to a CSV file
        out_dataframe.to_csv(
            os.path.join(output_dir, f"{station}_{nutrient}_predicted.csv")
        )

        # Save the predicted TP loads to a CSV file (in input_dir)
        # Output is needed in input_dir by GEOGLOWS_LOONE_DATA_PREP.py and in output_dir for graph visualization in the app
        out_dataframe.to_csv(
            os.path.join(input_dir, f"{station}_{nutrient}_predicted.csv")
        )


def photo_period(
    workspace: str,
    file_name: str = "PhotoPeriod",
    phi: float = 26.982052,
    doy: np.ndarray = np.arange(1, 365),
    verbose: bool = False,
):
    """Generate PhotoPeriod.csv file for the given latitude and days of the year.

    Args:
        workspace (str): A path to the directory where the file will be generated.
        file_name (str): The name of the file to be generated.
        phi (float, optional): Latitude of the location. Defaults to 26.982052.
        doy (np.ndarray, optional): An array holding the days of the year that you want the photo period for. Defaults to np.arange(1,365).
        verbose (bool, optional): Print results of each computation. Defaults to False.
    """
    phi = np.radians(phi)  # Convert to radians
    light_intensity = 2.206 * 10**-3

    C = np.sin(np.radians(23.44))  # sin of the obliquity of 23.44 degrees.
    B = -4.76 - 1.03 * np.log(
        light_intensity
    )  # Eq. [5]. Angle of the sun below the horizon. Civil twilight is -4.76 degrees.

    # Calculations
    alpha = np.radians(90 + B)  # Eq. [6]. Value at sunrise and sunset.
    M = 0.9856 * doy - 3.251  # Eq. [4].
    lmd = (
        M
        + 1.916 * np.sin(np.radians(M))
        + 0.020 * np.sin(np.radians(2 * M))
        + 282.565
    )  # Eq. [3]. Lambda
    delta = np.arcsin(C * np.sin(np.radians(lmd)))  # Eq. [2].

    # Defining sec(x) = 1/cos(x)
    P = (
        2
        / 15
        * np.degrees(
            np.arccos(
                np.cos(alpha) * (1 / np.cos(phi)) * (1 / np.cos(delta))
                - np.tan(phi) * np.tan(delta)
            )
        )
    )  # Eq. [1].

    # Print results in order for each computation to match example in paper
    if verbose:
        print("Input latitude =", np.degrees(phi))
        print("[Eq 5] B =", B)
        print("[Eq 6] alpha =", np.degrees(alpha))
        print("[Eq 4] M =", M[0])
        print("[Eq 3] Lambda =", lmd[0])
        print("[Eq 2] delta=", np.degrees(delta[0]))
        print("[Eq 1] Daylength =", P[0])

    photo_period_df = pd.DataFrame()
    photo_period_df["Day"] = doy
    photo_period_df["Data"] = P

    photo_period_df.to_csv(
        os.path.join(workspace, f"{file_name}.csv"), index=False
    )


def find_last_date_in_csv(workspace: str, file_name: str) -> str:
    """
    Gets the most recent date from the last line of a .csv file.
    Assumes the file is formatted as a .csv file, encoded in UTF-8,
    and the rows in the file are sorted by date in ascending order.

    Args:
        workspace (str): The directory where the file is located.
        file_name (str): The name of the file.

    Returns:
        str: The most recent date as a string in YYYY-MM-DD format, or None if the file does not exist or the date cannot be found.
    """

    # Helper Functions
    def is_valid_date(date_string):
        try:
            datetime.datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # Check that file exists
    file_path = os.path.join(workspace, file_name)
    if not os.path.exists(file_path):
        return None

    # Attempt to extract the date of the last line in the file
    try:
        with open(file_path, "rb") as file:
            # Go to the end of the file
            file.seek(-2, os.SEEK_END)

            # Loop backwards until you find the first newline character
            while file.read(1) != b"\n":
                file.seek(-2, os.SEEK_CUR)

            # Read the last line
            last_line = file.readline().decode()

            # Extract the date from the last line
            date = None

            for value in last_line.split(","):
                if is_valid_date(value):
                    date = value
                    break

            # Return date
            return date
    except OSError as e:
        print(f"Error reading file {file_name}: {e}")
        return None


def dbhydro_data_is_latest(date_latest: str):
    """
    Checks whether the given date is the most recent date possible to get data from dbhydro.
    Can be used to check whether dbhydro data is up-to-date.

    Args:
        date_latest (str): The date of the most recent data of the dbhydro data you have

    Returns:
        bool: True if the date_latest is the most recent date possible to get data from dbhydro, False otherwise
    """
    date_latest_object = datetime.datetime.strptime(
        date_latest, "%Y-%m-%d"
    ).date()
    return date_latest_object == (
        datetime.datetime.now().date() - datetime.timedelta(days=1)
    )


def get_synthetic_data(date_start: str, df: pd.DataFrame):
    """
    Gets 15 days of synthetic NO and Chla data matching forecast start date.
    
    Args:
        date_start (str): The date to start the forecast
        df (pd.DataFrame): The dataset containing NO or Chla data
    
    Returns:
        pd.DataFrame, pd.DataFrame: The updated NO or Chla dataset
    """
    date_end = date_start + datetime.timedelta(days=15)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    # Extract the month and day from the 'date' column
    df['month_day'] = df['date'].dt.strftime('%m-%d')
    
    # Extract the month and day from date_start and date_end
    start_month_day = date_start.strftime('%m-%d')
    end_month_day = date_end.strftime('%m-%d')
    
    # Filter the DataFrame to include only rows between date_start and date_end for all previous years
    mask = (df['month_day'] >= start_month_day) & (df['month_day'] <= end_month_day)
    filtered_data = df.loc[mask]
    
    # Group by the month and day, then calculate the average for each group
    average_values = filtered_data.groupby('month_day')['Data'].mean()
    # Interpolate in case there are missing values:
    start_date = pd.to_datetime('2001-' + start_month_day)
    end_date = pd.to_datetime('2001-' + end_month_day)

    full_dates = pd.date_range(start=start_date, end=end_date)
    full_index = full_dates.strftime('%m-%d')

    average_values = average_values.reindex(full_index)
    average_values = average_values.interpolate(method='linear')
    average_values_df = pd.DataFrame({
        'date': pd.date_range(start=date_start, end=date_end),
        'Data': average_values.values
    })
    
    df = pd.concat([df, average_values_df], ignore_index=True)
    df.drop(columns=['month_day'], inplace=True)
        
    return df


if __name__ == "__main__":
    if sys.argv[1] == "get_dbkeys":
        get_dbkeys(
            sys.argv[2].strip("[]").replace(" ", "").split(","), *sys.argv[3:]
        )
    elif sys.argv[1] == "data_interp":
        interp_args = [x for x in sys.argv[2:]]
        interp_args[0] = interp_args[0].rstrip("/")
        if len(interp_args) == 4:
            interp_args[3].strip("[]").replace(" ", "").split(",")
        data_interpolations(interp_args)
    elif sys.argv[1] == "interp_all":
        interpolate_all(sys.argv[2].rstrip("/"))
    elif sys.argv[1] == "kinematic_viscosity":
        kinematic_viscosity(sys.argv[2].rstrip("/"), *sys.argv[3:])
    elif sys.argv[1] == "wind_induced_waves":
        wind_induced_waves(
            sys.argv[2].rstrip("/"), sys.argv[3].rstrip("/"), *sys.argv[4:]
        )
    elif sys.argv[1] == "get_pi":
        get_pi(sys.argv[2].rstrip("/"))
    elif sys.argv[1] == "nutrient_prediction":
        nutrient_prediction(sys.argv[2].rstrip("/"), sys.argv[3].rstrip("/"))
