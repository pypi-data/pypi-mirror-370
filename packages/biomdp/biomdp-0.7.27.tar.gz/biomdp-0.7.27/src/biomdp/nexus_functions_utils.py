# -*- coding: utf-8 -*-


"""
Created on Tue Jun 07 13:44:46 2022

Common functions for handling Nexus files.
They can be used from Nexus and from outside.
Uses the csv exported from the MVCs. Calculates the maximum of each EMG channel in all files with 'MVC' in their name.
in all files with 'MVC' in their name. Save the maxima in a file
file so you don't have to reload them.
The maximum is used to normalize the EMG channels in the current file.
"""

# =============================================================================
# %% LOAD MODULES
# =============================================================================

__author__ = "Jose L. L. Elvira"
__version__ = "0.4.2"
__date__ = "30/05/2025"


"""
Updates:
    30/05/2025, v0.4.2
        - Some minor adjustments.

    05/03/2025, v0.4.1
        - Adapted to biomdp with translations.
    
    26/07/2024, v0.4.0
        - Corrección importante en el cálculo de AngSegRETROPIE con modelo
          antiguo (a partir de metas).
    
    21/05/2024, v0.3.0
        - Ahora importa funciones útiles desde el package instalable biomdp.
    
    11/05/2024, v0.2.2
        - Incluido escribir variables en Nexus de fuerzas y EMG.
    
    16/03/2024, v0.2.1
        - TODO: PROBAR CÁLCULO ÁNGULOS CON ViconUtils.EulerFromMatrix()
        - Adaptado para que funcione con modelo pie con Meta (central) o con Meta1 y Meta5.
    
    12/01/2024, v0.2.0
        - Trasladadas funciones propias del bikefitting al archivo bikefitting_funciones_apoyo.py.
    
    11/01/2024, v0.1.1
        - Mejorada función cálculo ángulos a partir de matrices rotación.
        - Cambiada nomenclatura de dimensiones:
          daTodos = daTodos.rename({'Archivo':'ID', 'nom_var':'n_var', 'lado':'side', 'eje':'axis'})

    23/04/2023, v0.1.0
        - Incluidas funciones de carga de datos directamente desde Nexus
          (Trajectories, Forces, EMG).
          
    09/06/2022, v0.0.1
                - 
"""
import os
import sys
import time
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import xarray as xr
from matplotlib.backends.backend_pdf import PdfPages  # to save plots in pdf format
from matplotlib.lines import (
    Line2D,
)  # to control legend lines fotmat

# from biomdp.io.read_vicon_csv import read_vicon_csv, read_vicon_csv
# from biomdp.io.read_vicon_c3d import read_vicon_c3d
import biomdp.slice_time_series_phases as stsp

# =============================================================================
# %% CONSTANTS
# =============================================================================

N_VARS_BILATERAL = [
    "AngSegPELVIS",
    "AngBiela",
    "vAngBiela",
    "discr_FrecPedal",
    "Ant_Cabeza",
    "Post_Cabeza",
    "C7",
    "T6",
    "L1",
]

nomVarsContinuas250 = [
    "LASI",
    "RASI",
    "LPSI",
    "RPSI",
    "LHJC",
    "RHJC",
    "LKJC",
    "RKJC",
    "LAJC",
    "RAJC",
    "Left_KneeInt",
    "Left_KneeExt",
    "Right_KneeInt",
    "Right_KneeExt",
    "Left_AnkleInt",
    "Left_AnkleExt",
    "Right_AnkleInt",
    "Right_AnkleExt",
    "Left_TalonSup",
    "Left_TalonInf",
    "Right_TalonSup",
    "Right_TalonInf",
    "Left_Pedal_A",
    "Left_Pedal_P",
    "Right_Pedal_A",
    "Right_Pedal_P",
    "Left_Meta",
    "Right_Meta",
]

nomVarsContinuas250_completo = nomVarsContinuas250 + [
    "Left_Hombro",
    "Left_Codo",
    "Left_Muneca",
    "Right_Hombro",
    "Right_Codo",
    "Right_Muneca",
    "Post_Cabeza",
    "Ant_Cabeza",
    "Right_Cabeza",
    "Left_Cabeza",
]
# Las variables _LR del modelo completo las carga aparte
nomVarsCentrales = [
    "L1",
    "T6",
    "C7",
]

rename_vars = {
    "LASI": "ASI_L",
    "RASI": "ASI_R",
    "LPSI": "PSI_L",
    "RPSI": "PSI_R",
    "LHJC": "HJC_L",
    "RHJC": "HJC_R",
    "LKJC": "KJC_L",
    "RKJC": "KJC_R",
    "LAJC": "AJC_L",
    "RAJC": "AJC_R",
    "Left_KneeInt": "KneeleInt_L",
    "Right_KneeInt": "KneeInt_R",
    "Left_KneeExt": "KneeleExt_L",
    "Right_KneeExt": "KneeExt_R",
    "Left_AnkleInt": "AnkleInt_L",
    "Right_AnkleInt": "AnkleInt_R",
    "Left_AnkleExt": "AnkleExt_L",
    "Right_AnkleExt": "AnkleExt_R",
    "Left_TalonSup": "TalonSup_L",
    "Right_TalonSup": "TalonSup_R",
    "Left_Pedal_A": "Pedal_A_L",
    "Right_Pedal_P": "Pedal_P_R",
    "Left_TalonInf": "TalonInf_L",
    "Right_TalonInf": "TalonInf_R",
    "Left_Meta": "Meta_L",
    "Right_Meta": "Meta_R",
    "Left_Hombro": "Hombro_L",
    "Right_Hombro": "Hombro_R",
    "Left_Codo": "Codo_L",
    "Right_Codo": "Codo_R",
    "Left_Muneca": "Muneca_L",
    "Right_Muneca": "Muneca_R",
}


# =============================================================================
# %% Funciones varias
# =============================================================================
def create_marker(
    vicon,
    num_fot: int,
    n_marker: str,
    n_marker2: str | None = None,
    offset: List[str] | None = None,
    fot_ref: int | None = None,
) -> None:
    """
    Examples:
    create_marker(vicon, num_fot=0, n_marker='Right_MusloAS', offset=[914,29,755])
    create_marker(vicon, num_fot=0, n_marker='Right_MusloAS', n_marker2='Right_MusloAI', offset=[0,0,80])

    """
    n_subject = vicon.GetSubjectNames()[0]
    num_frames = vicon.GetTrialRange()[1]

    region_of_interest = (
        np.array(vicon.GetTrialRegionOfInterest()) - 1
    )  # corrección para que ajuste a la escala empezando en cero
    exists = np.full(
        (num_frames), False, dtype=bool
    )  # pone a cero toda la variable de si existe
    # activa solo en la región de interés del trial
    exists[region_of_interest[0] : region_of_interest[1] + 1] = False

    try:
        marker = np.array([vicon.GetTrajectory(n_subject, n_marker)][0][:3]).T
        exists = np.array([vicon.GetTrajectory(n_subject, n_marker)][0][3])
    except:
        marker = np.zeros((num_frames, 3))

    if n_marker == n_marker2:
        marker = np.array([vicon.GetTrajectory(n_subject, n_marker2)][0][:3]).T
        exists = np.array([vicon.GetTrajectory(n_subject, n_marker)][0][3])

    if offset is not None:
        if n_marker2 is None:
            marker[num_fot, :] = marker[num_fot, :] + np.array(offset)
        else:
            if fot_ref is None:  # carga todo el registro
                marker2 = np.array([vicon.GetTrajectory(n_subject, n_marker2)][0][:3]).T
                marker[num_fot, :] = marker2[num_fot, :] + np.array(offset)
            else:  # carga sólo el fotograma especificado
                marker2 = np.array(
                    [vicon.GetTrajectory(n_subject, n_marker2)][0][:3]
                ).T[fot_ref]
                marker[num_fot, :] = marker2 + np.array(offset)

    exists[num_fot] = True

    # Escribe el marcador modificado
    vicon.SetTrajectory(
        n_subject,
        n_marker,
        marker[:, 0].tolist(),
        marker[:, 1].tolist(),
        marker[:, 2].tolist(),
        exists.tolist(),
    )


def show_base(vicon, origen, matrizRot, nombre, exists, escala) -> None:
    n_subject = vicon.GetSubjectNames()[0]
    # Show base markers
    modeledName = "BaseOrig" + nombre
    if modeledName not in vicon.GetModelOutputNames(n_subject):
        vicon.CreateModeledMarker(n_subject, modeledName)
    vicon.SetModelOutput(n_subject, modeledName, (origen).T, exists)

    modeledName = "Base" + nombre + "X"
    if modeledName not in vicon.GetModelOutputNames(n_subject):
        vicon.CreateModeledMarker(n_subject, modeledName)
    vicon.SetModelOutput(
        n_subject, modeledName, ((matrizRot[0] * escala) + origen).T, exists
    )

    modeledName = "Base" + nombre + "Y"
    if modeledName not in vicon.GetModelOutputNames(n_subject):
        vicon.CreateModeledMarker(n_subject, modeledName)
    vicon.SetModelOutput(
        n_subject, modeledName, ((matrizRot[1] * escala) + origen).T, exists
    )

    modeledName = "Base" + nombre + "Z"
    if modeledName not in vicon.GetModelOutputNames(n_subject):
        vicon.CreateModeledMarker(n_subject, modeledName)
    vicon.SetModelOutput(
        n_subject, modeledName, ((matrizRot[2] * escala) + origen).T, exists
    )


def define_circle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).
    """
    temp = p2[0] * p2[0] + p2[1] * p2[1]
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])

    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Center of circle
    cx = (bc * (p2[1] - p3[1]) - cd * (p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det

    radius = np.sqrt((cx - p1[0]) ** 2 + (cy - p1[1]) ** 2)
    return (cx, cy)  # ((cx, cy), radius)


def normalize_vector(a, order=2, axis=-1):
    """Function to normalize unit vectors"""
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2 == 0] = 1
    return a / np.expand_dims(l2, axis)


def normalize_vectors(x, y, z):
    def normaliza_vector_aux(a):
        """Intermediate function to use normalize_vector with xarray with more dimensions"""
        return normalize_vector(a.T)

    x = xr.apply_ufunc(
        normaliza_vector_aux,
        x,
        input_core_dims=[["axis", "time"]],
        output_core_dims=[["time", "axis"]],
        dask="parallelized",
        vectorize=True,
    )
    y = xr.apply_ufunc(
        normaliza_vector_aux,
        y,
        input_core_dims=[["axis", "time"]],
        output_core_dims=[["time", "axis"]],
        dask="parallelized",
        vectorize=True,
    )
    z = xr.apply_ufunc(
        normaliza_vector_aux,
        z,
        input_core_dims=[["axis", "time"]],
        output_core_dims=[["time", "axis"]],
        dask="parallelized",
        vectorize=True,
    )
    return x, y, z


def calculate_euler_angles_aux(rot_matrix):
    # TODO: PROBAR viconUtils.EulerFromMatrix()

    # rot_matrix = RlGPelvisxr
    # print(rot_matrix)
    # print(rot_matrix.shape)
    # plt.plot(rot_matrix.T)
    R = np.array(rot_matrix, dtype=np.float64, copy=False)[:3, :3]
    angles = np.zeros(3)

    angles[0] = np.arctan2(-R[2, 1], R[2, 2])
    angles[1] = np.arctan2(R[2, 0], np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2))
    angles[2] = np.arctan2(-R[1, 0], R[0, 0])

    # Devuelve el ángulo en radianes
    return np.rad2deg(angles)


def calculate_bases(daData: xr.DataArray, complete_model: bool = False) -> xr.Dataset:
    """
    Calcula las matrices de rotación de cada segmento a partir de sus marcadores.
    Recibe trayectorias marcadores ya separadas en lados o sin separar.
    TODO: SIMPLIFICAR TODO SIN SEPARAR EN LADOS.
    """

    timer_process = time.perf_counter()

    dsRlG = xr.Dataset()  # stores each segment's rotation matrix

    # Separate sides version
    if "side" in daData.coords:
        # PELVIS
        # datos_model=np.zeros((len(daDatos.time), 3))
        try:
            origen = daData.sel(n_var="ASI").sum(dim="side", skipna=False) * 0.5

            x = daData.sel(n_var="ASI", side="R") - origen
            vprovis = (
                origen
                - (
                    daData.sel(n_var="PSI", side="L")
                    + daData.sel(n_var="ASI", side="R")
                )
                * 0.5
            )
            z = xr.cross(x, vprovis, dim="axis")
            y = xr.cross(z, x, dim="axis")

            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat(
                [x, y, z], dim="axis_base"
            )  # .transpose('ID', 'axis_base', 'time', 'axis')
            # RlG = xr.apply_ufunc(normalize_vector, RlG)
            # RlG = RlG.T.groupby('axis_base').map(normalize_vector)

            dsRlG["Pelvis_LR"] = RlG

        except Exception as e:
            print(f"Unable to calculate segment PELVIS. {e}")

        # modelado['nombre'].append('AngSegPELVIS_LR')
        # modelado['datos'].append(datos_model)
        # modeled_name.append('AngSegPELVIS_LR')
        # modeled_data.append(modelado)

        # ----MUSLO_L
        try:
            origen = daData.sel(n_var="KJC", side="L")
            z = daData.sel(n_var="HJC", side="L") - daData.sel(n_var="KJC", side="L")
            vprovis = daData.sel(n_var="KneeInt", side="L") - daData.sel(
                n_var="KneeExt", side="L"
            )
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Muslo_L"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment MUSLO_L. {e}")

        # ----MUSLO_R
        try:
            origen = daData.sel(n_var="KJC", side="R")
            z = daData.sel(n_var="HJC", side="R") - daData.sel(n_var="KJC", side="R")
            vprovis = daData.sel(n_var="KneeExt", side="R") - daData.sel(
                n_var="KneeInt", side="R"
            )
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Muslo_R"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment MUSLO_R. {e}")

        # ----PIERNA_L
        try:
            origen = daData.sel(n_var="AJC", side="L")
            z = daData.sel(n_var="KJC", side="L") - daData.sel(n_var="AJC", side="L")
            vprovis = daData.sel(n_var="AnkleInt", side="L") - daData.sel(
                n_var="AnkleExt", side="L"
            )
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Pierna_L"] = RlG

            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment PIERNA_L. {e}")

        # ----PIERNA_R
        try:
            origen = daData.sel(n_var="AJC", side="R")
            z = daData.sel(n_var="KJC", side="R") - daData.sel(n_var="AJC", side="R")
            vprovis = daData.sel(n_var="AnkleExt", side="R") - daData.sel(
                n_var="AnkleInt", side="R"
            )
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Pierna_R"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment PIERNA_R. {e}")

        # ----RETROPIE_L
        if "Meta" in daData.n_var:
            daMeta = daData.sel(n_var="Meta")
        else:
            daMeta = (
                daData.sel(n_var=["Meta1", "Meta5"]).sum(dim="n_var", skipna=False)
                * 0.5
            )

        try:
            origen = daData.sel(n_var="TalonInf", side="L")
            y = daMeta.sel(side="L") - daData.sel(n_var="TalonSup", side="L")
            vprovis = daData.sel(n_var="TalonSup", side="L") - daData.sel(
                n_var="TalonInf", side="L"
            )
            x = xr.cross(y, vprovis, dim="axis")
            z = xr.cross(x, y, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Retropie_L"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment RETROPIE_L. {e}")

        # ----RETROPIE_R
        try:
            origen = daData.sel(n_var="TalonInf", side="R")
            y = daMeta.sel(side="R") - daData.sel(n_var="TalonSup", side="R")
            vprovis = daData.sel(n_var="TalonSup", side="R") - daData.sel(
                n_var="TalonInf", side="R"
            )
            x = xr.cross(y, vprovis, dim="axis")
            z = xr.cross(x, y, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Retropie_R"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment RETROPIE_R. {e}")

        # =============================================================================
        # Modelo parte superior
        # =============================================================================
        if complete_model:
            # ----LUMBAR_LR
            try:
                origen = (
                    daData.sel(n_var="PSI", side="L")
                    + daData.sel(n_var="PSI", side="R")
                ) * 0.5
                x = daData.sel(n_var="PSI", side="R") - origen
                vprovis = daData.sel(n_var="L1", side="R") - origen
                y = xr.cross(vprovis, x, dim="axis")
                z = xr.cross(x, y, dim="axis")
                x, y, z = normalize_vectors(x, y, z)

                RlG = xr.concat([x, y, z], dim="axis_base")
                dsRlG["Lumbar_LR"] = RlG
                # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

            except Exception as e:
                print(f"Unable to calculate segment LUMBAR. {e}")

            # ----TORAX_LR
            try:
                origen = daData.sel(n_var="C7", side="R")
                z = daData.sel(n_var="C7", side="R") - daData.sel(
                    n_var="T6", side="R"
                )  # .expand_dims({"n_var": ["C7_T6"]})
                vprovis = daData.sel(n_var="Hombro", side="R") - daData.sel(
                    n_var="Hombro", side="L"
                )
                y = xr.cross(z, vprovis, dim="axis").drop_vars("n_var")
                x = xr.cross(y, z, dim="axis")
                x, y, z = normalize_vectors(x, y, z)

                RlG = xr.concat([x, y, z], dim="axis_base")
                dsRlG["Torax_LR"] = RlG
                # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

            except Exception as e:
                print(f"Unable to calculate segment TORAX. {e}")

            # ----CABEZA_LR
            try:
                origen = daData.sel(n_var="Post_Cabeza")
                y = daData.sel(n_var="Ant_Cabeza") - daData.sel(n_var="Post_Cabeza")
                # DÓNDE SE CARGA LADOS DE CABEZA????
                vprovis = daData.sel(n_var="Cabeza", side="R") - daData.sel(
                    n_var="Cabeza", side="L"
                )
                z = xr.cross(vprovis, y, dim="axis").drop_vars("n_var")
                x = xr.cross(y, z, dim="axis")
                x, y, z = normalize_vectors(x, y, z)

                RlG = xr.concat([x, y, z], dim="axis_base")
                dsRlG["Cabeza_LR"] = RlG
                # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

            except Exception as e:
                print(f"Unable to calculate segment CABEZA. {e}")

        dsRlG = dsRlG.drop_vars(["n_var", "side"])

    else:  # unseparated sisdes version
        # PELVIS
        # datos_model=np.zeros((len(daDatos.time), 3))
        try:
            origen = (daData.sel(n_var="ASI_L") + daData.sel(n_var="ASI_R")) * 0.5
            x = daData.sel(n_var="ASI_R") - origen
            vprovis = (
                origen - (daData.sel(n_var="PSI_L") + daData.sel(n_var="ASI_R")) * 0.5
            )
            z = xr.cross(x, vprovis, dim="axis")
            y = xr.cross(z, x, dim="axis")

            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat(
                [x, y, z], dim="axis_base"
            )  # .transpose('ID', 'axis_base', 'time', 'axis')
            # RlG = xr.apply_ufunc(normalize_vector, RlG)
            # RlG = RlG.T.groupby('axis_base').map(normalize_vector)

            dsRlG["Pelvis_LR"] = RlG

        except Exception as e:
            print(f"Unable to calculate segment PELVIS. {e}")

        # modelado['nombre'].append('AngSegPELVIS_LR')
        # modelado['datos'].append(datos_model)
        # modeled_name.append('AngSegPELVIS_LR')
        # modeled_data.append(modelado)

        # ----MUSLO_L
        try:
            origen = daData.sel(n_var="KJC_L")
            z = daData.sel(n_var="HJC_L") - daData.sel(n_var="KJC_L")
            vprovis = daData.sel(n_var="KneeInt_L") - daData.sel(n_var="KneeExt_L")
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Muslo_L"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment MUSLO_L. {e}")

        # ----MUSLO_R
        try:
            origen = daData.sel(n_var="KJC_R")
            z = daData.sel(n_var="HJC_R") - daData.sel(n_var="KJC_R")
            vprovis = daData.sel(n_var="KneeExt_R") - daData.sel(n_var="KneeInt_R")
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Muslo_R"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment MUSLO_R. {e}")

        # ----PIERNA_L
        try:
            origen = daData.sel(n_var="AJC_L")
            z = daData.sel(n_var="KJC_L") - daData.sel(n_var="AJC_L")
            vprovis = daData.sel(n_var="AnkleInt_L") - daData.sel(n_var="AnkleExt_L")
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Pierna_L"] = RlG

            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment PIERNA_L. {e}")

        # ----PIERNA_R
        try:
            origen = daData.sel(n_var="AJC_R")
            z = daData.sel(n_var="KJC_R") - daData.sel(n_var="AJC_R")
            vprovis = daData.sel(n_var="AnkleExt_R") - daData.sel(n_var="AnkleInt_R")
            y = xr.cross(z, vprovis, dim="axis")
            x = xr.cross(y, z, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Pierna_R"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment PIERNA_R. {e}")

        # ----RETROPIE_L
        try:
            origen = daData.sel(n_var="TalonInf_L")
            y = daData.sel(n_var="Meta_L") - daData.sel(n_var="TalonSup_L")
            vprovis = daData.sel(n_var="TalonSup_L") - daData.sel(n_var="TalonInf_L")
            x = xr.cross(y, vprovis, dim="axis")
            z = xr.cross(x, y, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Retropie_L"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment RETROPIE_L.{e}")

        # ----RETROPIE_R
        try:
            origen = daData.sel(n_var="TalonInf_R")
            y = daData.sel(n_var="Meta_R") - daData.sel(n_var="TalonSup_R")
            vprovis = daData.sel(n_var="TalonSup_R") - daData.sel(n_var="TalonInf_R")
            x = xr.cross(y, vprovis, dim="axis")
            z = xr.cross(x, y, dim="axis")
            x, y, z = normalize_vectors(x, y, z)

            RlG = xr.concat([x, y, z], dim="axis_base")
            dsRlG["Retropie_R"] = RlG
            # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

        except Exception as e:
            print(f"Unable to calculate segment RETROPIE_R. {e}")

        # =============================================================================
        # Modelo parte superior
        # =============================================================================
        if complete_model:
            # ----LUMBAR_LR
            try:
                origen = (daData.sel(n_var="PSI_L") + daData.sel(n_var="PSI_R")) * 0.5
                x = daData.sel(n_var="PSI_R") - origen
                vprovis = daData.sel(n_var="L1") - origen
                y = xr.cross(vprovis, x, dim="axis")
                z = xr.cross(x, y, dim="axis")
                x, y, z = normalize_vectors(x, y, z)

                RlG = xr.concat([x, y, z], dim="axis_base")
                dsRlG["Lumbar_LR"] = RlG
                # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

            except Exception as e:
                print(f"Unable to calculate segment LUMBAR. {e}")

            # ----TORAX_LR
            try:
                origen = daData.sel(n_var="C7")
                z = daData.sel(n_var="C7") - daData.sel(n_var="T6")
                vprovis = daData.sel(n_var="Hombro", side="R") - daData.sel(
                    n_var="Hombro", side="L"
                )
                y = xr.cross(z, vprovis, dim="axis")
                x = xr.cross(y, z, dim="axis")
                x, y, z = normalize_vectors(x, y, z)

                RlG = xr.concat([x, y, z], dim="axis_base")
                dsRlG["Torax_LR"] = RlG
                # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

            except Exception as e:
                print(f"Unable to calculate segment TORAX. {e}")

            # ----CABEZA_LR
            try:
                origen = daData.sel(n_var="Post_Cabeza")
                y = daData.sel(n_var="Ant_Cabeza") - daData.sel(n_var="Post_Cabeza")
                # DÓNDE SE CARGA LADOS DE CABEZA????
                vprovis = daData.sel(n_var="Cabeza", side="R") - daData.sel(
                    n_var="Cabeza", side="L"
                )
                z = xr.cross(vprovis, y, dim="axis")
                x = xr.cross(y, z, dim="axis")
                x, y, z = normalize_vectors(x, y, z)

                RlG = xr.concat([x, y, z], dim="axis_base")
                dsRlG["Cabeza_LR"] = RlG
                # datos_model.plot.line(x='time', col='ID', col_wrap=4, hue='axis')

            except Exception as e:
                print(f"Unable to calculate segment CABEZA. {e}")

        dsRlG = dsRlG.drop_vars(["n_var"])

    print(
        f"Bases from {len(daData.ID)} files calculated in {time.perf_counter() - timer_process:.3f} s."
    )

    return dsRlG


def calculate_angles_segments(dsRlG, verbose=False) -> xr.Dataset:
    timer_process = time.perf_counter()

    dsAngSeg = xr.Dataset()

    for RlG in dsRlG:
        if verbose:
            print(f"Calculando {RlG}...")
        if dsRlG[RlG].isnull().all():  # si viene vacío se lo salta
            if verbose:
                print("vacío")
            dsAngSeg[f"AngSeg{RlG.upper()}"] = xr.full_like(
                dsRlG[RlG].isel(axis_base=0), np.nan
            )
            continue
        dsAngSeg[f"AngSeg{RlG.upper()}"] = calculate_angle_xr(RlGChild=dsRlG[RlG])
        if verbose:
            print("Ok")
    # RlGChild=dsRlG[RlG]

    print(
        f"Processed {len(dsRlG.ID)} files in {time.perf_counter() - timer_process:.3f} s."
    )

    return dsAngSeg


def calculate_angles_joints(
    dsRlG: xr.Dataset,
    daTrajec: xr.DataArray,
    complete_model: bool = False,
    verbose: bool = False,
) -> xr.Dataset:
    """
    Calcula ángulos de articulaciones a partir de las matrices de rotación
    daTrajec necesario sólo para el modelo completo
    """
    if complete_model and daTrajec is None:
        raise ValueError("Datos de trayectoria necesarios para el modelo completo")
        return

    timer_process = time.perf_counter()

    dsAngles = xr.Dataset()

    """
    child = dsRlG['Muslo_L'][:,0,0,:]
    parent = dsRlG['Pelvis_LR'][:,0,0,:]
    """
    modeled_names = [
        "AngArtHip_L",
        "AngArtHip_R",
        "AngArtKnee_L",
        "AngArtKnee_R",
        "AngArtAnkle_L",
        "AngArtAnkle_R",
    ]
    child_parents = [
        ["Muslo_L", "Pelvis_LR"],
        ["Muslo_R", "Pelvis_LR"],
        ["Pierna_L", "Muslo_L"],
        ["Pierna_R", "Muslo_R"],
        ["Retropie_L", "Pierna_L"],
        ["Retropie_R", "Pierna_R"],
    ]

    if complete_model:
        modeled_names += [
            "AngArtLumbar_LR",
            "AngArtToracoLumbar_LR",
            #'AngArtL1_LR', 'AngArtT6_LR',
            "AngArtCuello_LR",
            #'AngArtElbow_L', 'AngArtElbow_R',
        ]
        child_parents += [
            ["Pelvis_LR", "Lumbar_LR"],
            ["Lumbar_LR", "Torax_LR"],
            ["Torax_LR", "Cabeza_LR"],
        ]

    for modeled_name, child_parent in zip(modeled_names, child_parents):
        if verbose:
            print(f"Calculando {modeled_name}...")

        try:
            child = dsRlG[child_parent[0]]
            parent = dsRlG[child_parent[1]]
            if (
                child.isnull().all() or parent.isnull().all()
            ):  # si viene vacío se lo salta
                if verbose:
                    print("empty")
                dsAngles[modeled_name] = xr.full_like(child.isel(axis_base=0), np.nan)
                continue

            dsAngles[modeled_name] = calculate_angle_xr(
                RlGChild=child, RlGParent=parent
            )
            if verbose:
                print("Ok")
            """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                            input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                            output_core_dims=[['axis']],
                            vectorize=True
                            )
            """
        except Exception as e:
            print(f"No se ha podido calcular el ángulo {modeled_name}. {e}")

    # ----Correcciones signos específicas
    # HIP (# flex +, abd +, rot ext +)
    if "AngArtHip_R" in dsAngles.variables:
        dsAngles["AngArtHip_R"].loc[dict(axis="y")] = -dsAngles["AngArtHip_R"].loc[
            dict(axis="y")
        ]  # invierte el signo de la abd-add
    if "AngArtHip_R" in dsAngles.variables:
        dsAngles["AngArtHip_R"].loc[dict(axis="z")] = -dsAngles["AngArtHip_R"].loc[
            dict(axis="z")
        ]  # invierte el signo de la rot
    # KNEE
    if "AngArtKnee_L" in dsAngles.variables:
        dsAngles["AngArtKnee_L"].loc[dict(axis="x")] = -dsAngles["AngArtKnee_L"].loc[
            dict(axis="x")
        ]  # solo se invierte el signo de la flexoext
    if "AngArtKnee_R" in dsAngles.variables:
        dsAngles[
            "AngArtKnee_R"
        ] *= -1  # dsAngles[modeled_name].loc[dict(axis=['x', 'y', 'z'])
    # ANKLE
    if "AngArtAnkle_L" in dsAngles.variables:
        dsAngles["AngArtAnkle_L"].loc[dict(axis="y")] = -dsAngles["AngArtAnkle_L"].loc[
            dict(axis="y")
        ]  # solo se invierte el signo de la pronosup tobillo izq
    if "AngArtAnkle_R" in dsAngles.variables:
        dsAngles["AngArtAnkle_R"].loc[dict(axis="z")] = -dsAngles["AngArtAnkle_R"].loc[
            dict(axis="z")
        ]  # solo se invierte el signo de la rotación tobillo der

    # ----ÁNGULOS LINEALES
    if complete_model:
        # TODO: FALTA DIFERENCIAR SI VIENE CON SIDE O NO
        # ----L1
        modeled_name = "AngArtL1_LR"
        try:
            # Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var="T6")
            p2 = daTrajec.sel(n_var="L1")
            p3 = (
                daTrajec.sel(n_var="PSI", side="L")
                + daTrajec.sel(n_var="PSI", side="R")
            ) * 0.5
            dsAngles[modeled_name] = 180 - (
                np.arctan2(
                    np.linalg.norm(xr.cross(p1 - p2, p3 - p2, dim="axis")),
                    xr.dot(p1 - p2, p3 - p2, dim="axis"),
                )
                * 180
                / np.pi
            )

            # dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except Exception as e:
            print(f"No se ha podido calcular el ángulo {modeled_name}. {e}")

        # ----T6
        modeled_name = "AngArtT6_LR"
        try:
            # Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var="C7")
            p2 = daTrajec.sel(n_var="T6")
            p3 = daTrajec.sel(n_var="L1")
            dsAngles[modeled_name] = 180 - (
                np.arctan2(
                    np.linalg.norm(xr.cross(p1 - p2, p3 - p2, dim="axis")),
                    xr.dot(p1 - p2, p3 - p2, dim="axis"),
                )
                * 180
                / np.pi
            )

            # dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except Exception as e:
            print(f"No se ha podido calcular el ángulo {modeled_name}. {e}")

        # ----ELBOW_L
        modeled_name = "AngArtElbow_L"
        try:
            # Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var="Muneca", side="L")
            p2 = daTrajec.sel(n_var="Codo", side="L")
            p3 = daTrajec.sel(n_var="Hombro", side="L")
            dsAngles[modeled_name] = 180 - (
                np.arctan2(
                    np.linalg.norm(xr.cross(p1 - p2, p3 - p2, dim="axis")),
                    xr.dot(p1 - p2, p3 - p2, dim="axis"),
                )
                * 180
                / np.pi
            )

            # dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except Exception as e:
            print(f"No se ha podido calcular el ángulo {modeled_name}. {e}")

        # ----ELBOW_R
        modeled_name = "AngArtElbow_R"
        try:
            # Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var="Muneca", side="R")
            p2 = daTrajec.sel(n_var="Codo", side="R")
            p3 = daTrajec.sel(n_var="Hombro", side="R")
            dsAngles[modeled_name] = 180 - (
                np.arctan2(
                    np.linalg.norm(xr.cross(p1 - p2, p3 - p2, dim="axis")),
                    xr.dot(p1 - p2, p3 - p2, dim="axis"),
                )
                * 180
                / np.pi
            )

            # dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except Exception as e:
            print(f"No se ha podido calcular el ángulo {modeled_name}. {e}")

    '''
    #----HIP_L
    modeled_name = 'AngArtHip_L'
    try:
        child = dsRlG['Muslo_L']
        parent = dsRlG['Pelvis_LR']
                
        dsAngles[modeled_name] = calculate_angle_xr(child, parent)
        """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                        input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                        output_core_dims=[['axis']],
                        vectorize=True
                        )
        """
        # flex +, abd +, rot ext +
        #dsAngles[modeled_name].plot.line(x='time', col='ID', col_wrap=4, hue='axis')
    except:
        print('No se ha podido calcular el ángulo', modeled_name)

    #----HIP_R
    modeled_name = 'AngArtHip_R'
    try:
        child = dsRlG['Muslo_R']
        parent = dsRlG['Pelvis_LR']
        dsAngles[modeled_name] = calculate_angle_xr(child, parent)
        """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                        input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                        output_core_dims=[['axis']],
                        vectorize=True
                        )
        """
        #Ajusta signos
        dsAngles[modeled_name].loc[dict(axis='y')] = -dsAngles[modeled_name].loc[dict(axis='y')] #invierte el signo de la abd-add
        dsAngles[modeled_name].loc[dict(axis='z')] = -dsAngles[modeled_name].loc[dict(axis='z')] #invierte el signo de la rot
        #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
    except:
        print('No se ha podido calcular el ángulo', modeled_name)

    #----KNEE_L
    modeled_name = 'AngArtKnee_L'
    try:
        child = dsRlG['Pierna_L']
        parent = dsRlG['Muslo_L']        
        dsAngles[modeled_name] = calculate_angle_xr(child, parent)
        """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                        input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                        output_core_dims=[['axis']],
                        vectorize=True
                        )
        """
        #Ajusta signos
        dsAngles[modeled_name].loc[dict(axis='x')] = -dsAngles[modeled_name].loc[dict(axis='x')] #solo se invierte el signo de la flexoext        
        #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
    except:
        print('No se ha podido calcular el ángulo', modeled_name)
    
    #----KNEE_R
    modeled_name = 'AngArtKnee_R'
    try:
        child = dsRlG['Pierna_R']
        parent = dsRlG['Muslo_R']        
        dsAngles[modeled_name] = calculate_angle_xr(child, parent)
        """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                        input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                        output_core_dims=[['axis']],
                        vectorize=True
                        )
        """
        #Ajusta signos
        dsAngles[modeled_name] *= -1 #dsAngles[modeled_name].loc[dict(axis=['x', 'y', 'z'])
        #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
    except:
        print('No se ha podido calcular el ángulo', modeled_name)

    #----ANKLE_L
    modeled_name = 'AngArtAnkle_L'
    try:
        child = dsRlG['Retropie_L']
        parent = dsRlG['Pierna_L']        
        dsAngles[modeled_name] = calculate_angle_xr(child, parent)
        """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                        input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                        output_core_dims=[['axis']],
                        vectorize=True
                        )
        """
        #Ajusta signos
        dsAngles[modeled_name].loc[dict(axis='y')] = -dsAngles[modeled_name].loc[dict(axis='y')] #solo se invierte el signo de la pronosup tobillo izq
        #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
    except:
        print('No se ha podido calcular el ángulo', modeled_name)

    #----ANKLE_R
    modeled_name = 'AngArtAnkle_R'
    try:
        child = dsRlG['Retropie_R']
        parent = dsRlG['Pierna_R']        
        dsAngles[modeled_name] = calculate_angle_xr(child, parent)
        """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                        input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                        output_core_dims=[['axis']],
                        vectorize=True
                        )
        """
        #Ajusta signos
        dsAngles[modeled_name].loc[dict(axis='z')] = -dsAngles[modeled_name].loc[dict(axis='z')] #solo se invierte el signo de la rotación tobillo der
        #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
    except:
        print('No se ha podido calcular el ángulo', modeled_name)
    
    if complete_model:
        #----LUMBAR
        modeled_name = 'AngArtLumbar_LR'
        try:
            child = dsRlG['Pelvis_LR']
            parent = dsRlG['Lumbar_LR']        
            dsAngles[modeled_name] = calculate_angle_xr(child, parent)
            """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                            input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                            output_core_dims=[['axis']],
                            vectorize=True
                            )
            """
            #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except:
            print('No se ha podido calcular el ángulo', modeled_name)

        #----TORACOLUMBAR
        modeled_name = 'AngArtToracoLumbar_LR'
        try:
            child = dsRlG['Lumbar_LR']
            parent = dsRlG['Torax_LR']        
            dsAngles[modeled_name] = calculate_angle_xr(child, parent)
            """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                            input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                            output_core_dims=[['axis']],
                            vectorize=True
                            )
            """
            #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except:
            print('No se ha podido calcular el ángulo', modeled_name)
        
        #----L1
        modeled_name = 'AngArtL1_LR'
        try:
            #Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var='T6')
            p2 = daTrajec.sel(n_var='L1')
            p3 = (daTrajec.sel(n_var='PSI', side='L') + daTrajec.sel(n_var='PSI', side='R')) * 0.5
            dsAngles[modeled_name] = 180 - (np.arctan2(np.linalg.norm(xr.cross(p1-p2, p3-p2, dim='axis')), xr.dot(p1-p2, p3-p2, dim='axis'))*180/np.pi)
          
            #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except:
            print('No se ha podido calcular el ángulo', modeled_name)

        #----T6
        modeled_name = 'AngArtT6_LR'
        try:
            #Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var='C7')
            p2 = daTrajec.sel(n_var='T6')
            p3 = daTrajec.sel(n_var='L1')
            dsAngles[modeled_name] = 180 - (np.arctan2(np.linalg.norm(xr.cross(p1-p2, p3-p2, dim='axis')), xr.dot(p1-p2, p3-p2, dim='axis'))*180/np.pi)
          
            #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except:
            print('No se ha podido calcular el ángulo', modeled_name)

        #----CUELLO
        modeled_name = 'AngArtCuello_LR'
        try:
            child = dsRlG['Torax_LR']
            parent = dsRlG['Cabeza_LR']        
            dsAngles[modeled_name] = calculate_angle_xr(child, parent)
            """dsAngles[modeled_name] = xr.apply_ufunc(calcula_ang_artic_aux, child, parent,
                            input_core_dims=[['axis_base', 'axis'], ['axis_base', 'axis']],
                            output_core_dims=[['axis']],
                            vectorize=True
                            )
            """
            #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except:
            print('No se ha podido calcular el ángulo', modeled_name)
        
        #----ELBOW_L
        modeled_name = 'AngArtElbow_L'
        try:
            #Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var='Muneca', side='L')
            p2 = daTrajec.sel(n_var='Codo', side='L')
            p3 = daTrajec.sel(n_var='Hombro', side='L')
            dsAngles[modeled_name] = 180 - (np.arctan2(np.linalg.norm(xr.cross(p1-p2, p3-p2, dim='axis')), xr.dot(p1-p2, p3-p2, dim='axis'))*180/np.pi)
          
            #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except:
            print('No se ha podido calcular el ángulo', modeled_name)

        #----ELBOW_R
        modeled_name = 'AngArtElbow_R'
        try:
            #Probar con esto en xr, si no, hacer función aux y usar ufunc
            p1 = daTrajec.sel(n_var='Muneca', side='R')
            p2 = daTrajec.sel(n_var='Codo', side='R')
            p3 = daTrajec.sel(n_var='Hombro', side='R')
            dsAngles[modeled_name] = 180 - (np.arctan2(np.linalg.norm(xr.cross(p1-p2, p3-p2, dim='axis')), xr.dot(p1-p2, p3-p2, dim='axis'))*180/np.pi)
          
            #dsAngles[modeled_name].plot.line(x='time', row='ID', hue='axis')
        except:
            print('No se ha podido calcular el ángulo', modeled_name)
    '''
    print(
        f"Calculated angles from {len(dsRlG.ID)} files in {time.perf_counter() - timer_process:.3f} s."
    )

    return dsAngles


def calculate_angles_from_trajec(
    daData, complete_model=False, tipo="all", verbose=False
) -> xr.DataArray:
    """
    Calcula ángulos de articulaciones a partir de las trayectorias.
    Paso intermedio de calcular matrices de rotación
    tipo: 'artic', 'segment' o 'all'
    """
    timer_process = time.perf_counter()

    print("\nCalculando matrices de rotación...")
    dsRlG = calculate_bases(daData, complete_model)  # daData=daDatos.isel(ID=0))

    if tipo in ["segment", "all"]:
        print("\nCalculando ángulos de segmentos...")
        dsAngSegments = calculate_angles_segments(dsRlG, verbose=verbose)

    if tipo in ["artic", "all"]:
        print("\nCalculando ángulos articulares...")
        dsAngArtics = calculate_angles_joints(
            dsRlG, complete_model=complete_model, verbose=verbose
        )
    # dsAngArtics['AngArtHip_L'].plot.line(x='time', row='ID', hue='axis')

    if tipo == "all":
        daAngles = xr.merge([dsAngSegments, dsAngArtics])
    elif tipo == "artic":
        daAngles = dsAngArtics
    elif tipo == "segment":
        daAngles = dsAngSegments

    daAngles = daAngles.to_array().rename({"variable": "n_var"})  # .to_dataarray()

    if "side" in daData.coords:
        daAngles = split_trajectories_sides(daAngles)

    daAngles.name = "Angles"
    daAngles.attrs["units"] = "deg"
    daAngles.attrs["freq"] = daData.freq

    # daAngles.sel(n_var='AngArtHip').plot.line(x='time', row='ID', col='axis', hue='side')

    print(
        f"Processed {len(daAngles.ID)} files in {time.perf_counter() - timer_process:.3f} s."
    )

    return daAngles


def adjust_labels_side_end(daData) -> xr.DataArray:
    labels = daData["n_var"].values

    # Busca variablel bilaterales
    n_var_new = [f"{i}_LR" if i in N_VARS_BILATERAL else i for i in labels]

    # Ajusta las etiquetas a formato lados L, R
    n_var_new = [f"{i.split('Left_')[-1]}_L" if "Left" in i else i for i in n_var_new]
    n_var_new = [f"{i.split('Right_')[-1]}_R" if "Right" in i else i for i in n_var_new]
    n_var_new = [
        i[1:] + "_L" if i[0] == "L" and i[0:6] != "Length" and i != "L1_LR" else i
        for i in n_var_new
    ]
    n_var_new = [i[1:] + "_R" if i[0] == "R" else i for i in n_var_new]

    daData = daData.assign_coords(n_var=n_var_new)
    return daData


def rename_variables(nomvar) -> str:
    if nomvar == "GLU":
        nom = "Glúteo"
    elif nomvar == "BIC":
        nom = "Bíceps femoral"
    elif nomvar == "REC":
        nom = "Recto femoral"
    elif nomvar == "VME":
        nom = "Vasto interno"
    elif nomvar == "GAS":
        nom = "Gemelo"
    elif nomvar == "TIB":
        nom = "Tibial"

    elif nomvar == "AngArtHip":
        nom = "Ang Cadera"
    elif nomvar == "AngArtKnee":
        nom = "Ang Rodilla"
    elif nomvar == "AngArtAnkle":
        nom = "Ang Tobillo"
    elif nomvar == "AngSegPELVIS":
        nom = "Pelvis"
    elif nomvar == "x" or nomvar == ["y", "z"]:
        nom = "sagital"
    elif nomvar == "y" or nomvar == ["x", "z"]:
        nom = "frontal"
    elif nomvar == ["x", "y"]:
        nom = "cenital"
    elif nomvar == "z":
        nom = "rotación"

    elif nomvar == "Eje x":
        nom = "mediolateral"
    elif nomvar == "Eje y":
        nom = "anteroposterior"
    elif nomvar == "Eje z":
        nom = "vertical"

    elif nomvar == "HJC":
        nom = "Eje Cadera"
    elif nomvar == "KJC":
        nom = "Eje Rodilla"
    elif nomvar == "AJC":
        nom = "Eje Tobillo"
    elif nomvar == "vAngBiela":
        nom = "Velocidad Ang biela"
    else:
        nom = "desconocido"
    return nom


def calculate_angle_xr(RlGChild, RlGParent=None) -> xr.DataArray:
    """
    Recibe matrices de rotación. Si llega una sola calcula el ángulo del segmento,
    si llegan dos calcula el ángulo entre los dos segmentos (articulación).
    """
    # Comprueba si hay que calcular para segmento o articulación
    if RlGParent is None:
        RlGParent = RlGChild
        bSegment = True
    else:
        bSegment = False

    # TODO: PROBAR FUNCIÓN NEXUS ViconUtils.EulerFromMatrix()
    #  from viconnexusapi import ViconUtils
    def calc_ang_aux(child, parent):
        if bSegment:
            R = child
        else:
            R = np.dot(child, parent.T)
        x = np.arctan2(-R[2, 1], R[2, 2])
        y = np.arctan2(R[2, 0], np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2))
        z = np.arctan2(-R[1, 0], R[0, 0])

        return np.rad2deg(np.array([x, y, z]))

    """
    RlGChild = dsRlG[child_parent[0]]
    RlGParent = dsRlG[child_parent[1]]

    child = RlGChild[:,0].isel(time=0).data
    parent = RlGParent[:,0].isel(time=0).data
    
    ViconUtils.EulerFromMatrix
    """

    """
    #PROBAR CON XR.DOT Y calculate_euler_angles_aux
    xr.dot(RlGChild, RlGParent.T, dim=['axis_base', 'axis'])
    Rxr = xr.dot(RlGChild, RlGParent.T, dim='axis') #['axis_base', 'axis'])
    Rxr[0,0]
    """
    angulo = xr.apply_ufunc(
        calc_ang_aux,
        RlGChild,
        RlGParent,
        input_core_dims=[["axis_base", "axis"], ["axis_base", "axis"]],
        output_core_dims=[["axis"]],
        # exclude_dims=set(('axis',)),
        dask="parallelized",
        vectorize=True,
    )
    # angulo.sel(axis='z').plot.line(x='time')

    """
    datos_model = xr.apply_ufunc(calculate_euler_angles_aux, RlG,
                                 input_core_dims=[['axis_base', 'axis']],
                                 output_core_dims=[['axis']],
                                 vectorize=True,
                                 )
    """
    return angulo


# =============================================================================


# =============================================================================
# %% Extrae variables del Nexus directamente
# =============================================================================
def load_variables_nexus_trajectories(vicon=None, n_vars=None) -> xr.DataArray:
    if vicon is None:
        raise ValueError("Must pass an object ViconNexus.ViconNexus")

    print("Loading Trajectories...")
    timer = time.time()

    if n_vars is None:
        n_vars = vicon.GetMarkerNames(vicon.GetSubjectNames()[0])
        n_vars = n_vars + [
            "LASI",
            "RASI",
            "LHJC",
            "RHJC",
            "LKJC",
            "RKJC",
            "LAJC",
            "RAJC",
            "Left_KneeExt",
            "Left_KneeInt",
            "Right_KneeExt",
            "Right_KneeInt",
            "Left_AnkleExt",
            "Left_AnkleInt",
            "Right_AnkleExt",
            "Right_AnkleInt",
        ]  # vicon.GetModelOutputNames(vicon.GetSubjectNames()[0])

    # Borra si hay nombres repetidos
    n_vars = np.unique(n_vars).tolist()

    markers = []
    for nom in n_vars:
        # print(f'Trying to load variable {nom}')

        dat = vicon.GetTrajectory(vicon.GetSubjectNames()[0], nom)
        dat = np.where(np.array(dat[3]), dat[:3], np.nan)
        # dat = np.array([vicon.GetTrajectory(vicon.GetSubjectNames()[0], nom)][0])
        # np.where(dat[3,:]==1., dat[:3], np.nan)
        # dat = np.array([vicon.GetTrajectory(vicon.GetSubjectNames()[0], nom)][0][:3])
        if dat.size == 0:
            dat = vicon.GetModelOutput(vicon.GetSubjectNames()[0], nom)
            dat = np.where(np.array(dat[1]), np.array(dat[0]), np.nan)

            # dat = np.array(
            #     [vicon.GetModelOutput(vicon.GetSubjectNames()[0], nom)[0][:3]]
            # )[
            #     0
            # ]  # .reshape(3, vicon.GetTrialRange()[1]).T
            print(f"{nom} loaded from Modeled Markers")
        if dat.size == 0:
            dat = np.full((3, vicon.GetTrialRange()[1]), np.nan, dtype=float)
            print(f"Unable to load variable {nom}")

        markers.append(dat)

    # print(f'Cargada la variable {nom}')
    # Añade una dimensión para el ID
    data = np.expand_dims(np.array(markers), axis=0)
    coords = {
        "ID": [vicon.GetSubjectNames()[0]],
        "n_var": n_vars,
        "axis": ["x", "y", "z"],
        "time": np.arange(0, data.shape[-1]) / vicon.GetFrameRate(),
    }

    da = xr.DataArray(
        data=data,
        dims=coords.keys(),
        coords=coords,
    )

    da.name = "Trajectories"
    da.attrs["freq"] = float(vicon.GetFrameRate())
    da.attrs["units"] = "mm"
    da.time.attrs["units"] = "s"

    print("Loaded in {0:.3f} s \n".format(time.time() - timer))

    return da


def load_variables_nexus_force(vicon=None, n_plate=None) -> xr.DataArray:
    if vicon is None:
        raise ValueError("Must pass an object ViconNexus.ViconNexus")

    print("Loading Forces...")
    timer = time.time()

    deviceForce = [x for x in vicon.GetDeviceNames() if n_plate in x][0]
    deviceID = vicon.GetDeviceIDFromName(deviceForce)
    _, _, freqForce, outputIDs, _, _ = vicon.GetDeviceDetails(deviceID)

    # Read channels names
    # cols = [
    #     vicon.GetDeviceOutputDetails(deviceID, outputIDs[i])
    #     for i in range(len(outputIDs))
    # ]

    # Load platform forces
    ejes = []
    for n, eje in enumerate(["x", "y", "z"], start=1):
        ejes.append(vicon.GetDeviceChannel(deviceID, outputIDs[0], n)[0])

    data = np.expand_dims(np.array(ejes), axis=0)  # add dimension for ID
    coords = {
        "ID": [vicon.GetSubjectNames()[0]],
        "axis": ["x", "y", "z"],
        "time": np.arange(0, data.shape[-1]) / freqForce,
    }
    da = xr.DataArray(
        data=data,
        dims=coords.keys(),
        coords=coords,
    )
    da.loc[dict(axis="z")] *= -1
    # da.plot.line(x='time')

    da.name = "Force"
    da.attrs["freq"] = float(freqForce)
    da.attrs["freq_ref"] = vicon.GetFrameRate()  # frequency of markers
    da.attrs["units"] = "N"
    da.time.attrs["units"] = "s"

    print("Loaded in {0:.3f} s \n".format(time.time() - timer))
    return da


def load_variables_nexus_EMG(vicon=None, n_vars=None) -> xr.DataArray:
    if vicon is None:
        raise ValueError("Must pass an object ViconNexus.ViconNexus")

    print("Loading EMG...")
    timer = time.time()

    deviceEMG = [x for x in vicon.GetDeviceNames() if "EMG" in x][0]
    deviceID = vicon.GetDeviceIDFromName(deviceEMG)

    _, _, freqEMG, outputIDs, _, _ = vicon.GetDeviceDetails(deviceID)

    # dir(ViconNexus.ViconNexus)
    # help(ViconNexus.ViconNexus.GetDeviceChannelIDFromName)
    # help(ViconNexus.ViconNexus.GetDeviceChannel)

    # nom_canal,_,_,_,_,channelIDs = vicon.GetDeviceOutputDetails(deviceID,outputIDs[1])

    # Coge los nombres de los canales
    cols = [
        vicon.GetDeviceOutputDetails(deviceID, outputIDs[i])[0]
        for i in range(len(outputIDs))
    ]

    # data, ready, rate = vicon.GetDeviceChannel(deviceID,cols.index('EMG2')+1,1)
    # plt.plot(data)

    channel = []
    for n, nom in enumerate(cols):
        channel.append(vicon.GetDeviceChannel(deviceID, outputIDs[n], 1)[0])

    data = np.expand_dims(np.array(channel), axis=0)  # añade una dimensión para el ID
    coords = {
        "ID": [vicon.GetSubjectNames()[0]],
        "channel": cols,
        "time": np.arange(0, data.shape[-1]) / freqEMG,
    }
    da = xr.DataArray(
        data=data,
        dims=coords.keys(),
        coords=coords,
    )

    # Ajusta a mano los sensores de cada lado
    """rename_vars={'EMG9':'GLU', 'EMG10':'REC', 'EMG11':'BIV',
                    'EMG12':'VAE', 'EMG13':'VAI',
                    'EMG14':'GAS', 'EMG15':'TIB',
                    }
    
    # rename_vars={'EMG1':'GLU_R', 'EMG2':'BIC_R', 'EMG3':'REC_R', 'EMG4':'VME_R', 'EMG5':'GAS_R', 'EMG6':'TIB_R', 
    #                 'EMG7':'GLU_L', 'EMG8':'BIC_L', 'EMG9':'REC_L', 'EMG10':'VME_L', 'EMG11':'GAS_L', 'EMG12':'TIB_L',
    #                 }
    """
    if n_vars is not None:
        # daEMG = daEMG.sel(channel=daEMG.channel.str.contains('EMG'))
        da = da.sel(channel=n_vars)

    da = da * 1000  # convert to millivolts
    da.name = "EMG"
    da.attrs["freq"] = float(freqEMG)
    da.attrs["freq_ref"] = vicon.GetFrameRate()  # frequency of markers
    da.attrs["units"] = "mV"
    da.time.attrs["units"] = "s"

    print("Loaded in {0:.3f} s \n".format(time.time() - timer))
    return da


def write_variables_in_nexus_kinem(da: xr.DataArray, vicon=None) -> None:
    """Write processed Kinematics back to Nexus"""
    if vicon is None:
        raise ValueError("Must pass an object ViconNexus.ViconNexus")

    from itertools import product

    n_subject = vicon.GetSubjectNames()[0]
    num_frames = vicon.GetTrialRange()[1]
    region_of_interest = (
        np.array(vicon.GetTrialRegionOfInterest()) - 1
    )  # corrección para que ajuste a la escala empezando en cero
    exists = np.full(
        (num_frames), False, dtype=bool
    )  # pone a cero toda la variable de si existe
    # activa solo en la región de interés del trial
    exists[region_of_interest[0] : region_of_interest[1] + 1] = True

    for var, lado in product(da.n_var.values, da.side.values):
        if var in N_VARS_BILATERAL:
            lado = "LR"
        n_modeled = f"{var}_{lado}"

        # print(n_modeled)

        if lado == "LR":  # if bilateral, change back to left to be able to select
            lado = "L"

        if "ID" in da.dims:
            insert_values = da.isel(ID=0).sel(n_var=var, side=lado)
        else:
            insert_values = da.sel(n_var=var, side=lado)

        if np.isnan(insert_values).all():
            continue

        insert_values = insert_values.transpose(..., "axis", "time")

        if n_modeled not in vicon.GetModelOutputNames(n_subject):
            vicon.CreateModelOutput(
                n_subject,
                n_modeled,
                "Modeled Angles",
                ["x", "y", "z"],
                ["Angle", "Angle", "Angle"],
            )
        vicon.SetModelOutput(n_subject, n_modeled, insert_values.values, exists)


def write_variables_in_nexus_forces(da: xr.DataArray, vicon=None) -> None:
    """Write processed Forces back to Nexus"""
    if vicon is None:
        raise ValueError("Must pass an object ViconNexus.ViconNexus")

    # Get ModelOutput List
    n_subject = vicon.GetSubjectNames()[0]
    num_frames = vicon.GetTrialRange()[1]
    region_of_interest = (
        np.array(vicon.GetTrialRegionOfInterest()) - 1
    )  # corrección para que ajuste a la escala empezando en cero
    exists = np.full(
        (num_frames), False, dtype=bool
    )  # pone a cero toda la variable de si existe
    # activa solo en la región de interés del trial
    exists[region_of_interest[0] : region_of_interest[1] + 1] = True

    # full_model_output_list = vicon.GetModelOutputNames(n_subject)

    x2 = da.time.data[
        :: int(da.freq / da.freq_ref)
    ]  # list(np.array(np.linspace(region_of_interest[0], len(x1), num_frames)))
    da_subsamp = da.interp(time=x2, method="cubic")

    # musc=['GLU', 'BIC', 'VME', 'REC', 'TIB', 'GAS']

    modeled_name = "Forces"
    var_model = da_subsamp.isel(ID=0).data

    if modeled_name not in vicon.GetModelOutputNames(n_subject):
        vicon.CreateModelOutput(
            n_subject,
            modeled_name,
            "Modeled Forces",
            ["x", "y", "z"],
            ["Force", "Force", "Force"],
        )
    vicon.SetModelOutput(n_subject, modeled_name, var_model, exists)


def write_variables_in_nexus_emg(da: xr.DataArray, vicon=None) -> None:
    """Write processed EMG back to Nexus"""
    if vicon is None:
        raise ValueError("Must pass an object ViconNexus.ViconNexus")

    # Get ModelOutput List

    n_subject = vicon.GetSubjectNames()[0]
    num_frames = vicon.GetTrialRange()[1]

    # Correction to fit the scale starting from zero
    region_of_interest = np.array(vicon.GetTrialRegionOfInterest()) - 1
    exists = np.full((num_frames), False, dtype=bool)
    # active only in the trial's region of interest
    exists[region_of_interest[0] : region_of_interest[1] + 1] = True

    # full_model_output_list = vicon.GetModelOutputNames(n_subject)

    x2 = da.time.data[
        :: int(da.freq / da.freq_ref)
    ]  # list(np.array(np.linspace(region_of_interest[0], len(x1), num_frames)))
    da_subsamp = da.interp(time=x2, method="cubic")

    # musc=['GLU', 'BIC', 'VME', 'REC', 'TIB', 'GAS']

    for modeled_name in da.channel.data:
        # Converto to volts
        var_model = da_subsamp.isel(ID=0).sel(channel=modeled_name).data / 1000

        if modeled_name not in vicon.GetModelOutputNames(n_subject):
            vicon.CreateModelOutput(
                n_subject,
                modeled_name,
                "Modeled EMG (raw)",
                ["EMG"],
                ["Electric Potential"],
            )
        vicon.SetModelOutput(n_subject, modeled_name, [var_model], exists)


# =============================================================================
# %% Extract Nexus variables from csv or c3d
# =============================================================================
def df_to_da_EMG(data: pd.DataFrame | xr.DataArray) -> xr.DataArray:
    if isinstance(data, pd.DataFrame):
        da = (
            data.set_index(["ID", "time"])
            .stack()
            .to_xarray()
            .rename({"level_2": "n_var"})
        )  # .transpose('ID', 'n_var', 'axis', 'time')
    elif isinstance(data, xr.DataArray):
        da = data
    else:
        raise TypeError("Input data must be a pandas DataFrame or an xarray DataArray")

    L = da.sel(
        n_var=da.n_var.str.endswith("_L")
    )  # [i for i in da.n_var.data if '_L' in i and '_LR' not in i])#nomVarsContinuas_L) #el L es distinto porque incluye _L y _LR
    R = da.sel(n_var=da["n_var"].str.endswith("_R"))

    # Remove the endings after _
    L["n_var"] = ("n_var", L["n_var"].str.rstrip(to_strip="_L").data)
    R["n_var"] = ("n_var", R["n_var"].str.rstrip(to_strip="_R").data)

    da = xr.concat([L, R], pd.Index(["L", "R"], name="side")).transpose(
        "ID", "n_var", "side", "time"
    )
    return da


# =============================================================================


# =============================================================================
# %% Load trajectories from c3d
# =============================================================================
def load_trayectories_c3d(file_list, n_vars_load=None):
    raise Exception(
        "Deprecation warning. Use load_c3d_generic_xr(data, section='Trajectories') instead"
    )
    # return

    try:
        import c3d
    except:
        raise ImportError("c3d module not found. Install with: pip install c3d")

    print("Loading files...")
    timer = time.time()

    daAllFiles = []
    error_files = []
    num_processed_files = 0
    for file in file_list:
        # se asegura de que la extensión es c3d
        file = file.with_suffix(".c3d")
        print(file.name)
        try:
            timerSub = time.time()
            print("Loading file: {0:s}".format(file.name))

            with open(file, "rb") as handle:
                reader = c3d.Reader(handle)

                freq = reader.point_rate

                points = []
                for i, (_, p, _) in enumerate(reader.read_frames()):
                    points.append(p)
                    # analog.append(a)
                    if not i % 10000 and i:
                        print("Extracted %d point frames", len(points))

                labels = [s.replace(" ", "") for s in reader.point_labels]
            data = np.asarray(points)[:, :, :3]

            # Ajusta las etiquetas a formato lados L, R
            n_var_new = [
                i.split("Left_")[-1] + "_L" if "Left" in i else i for i in labels
            ]
            n_var_new = [
                i.split("Right_")[-1] + "_R" if "Right" in i else i for i in n_var_new
            ]
            n_var_new = [i[1:] + "_L" if i[0] == "L" else i for i in n_var_new]
            n_var_new = [i[1:] + "_R" if i[0] == "R" else i for i in n_var_new]

            da = xr.DataArray(
                data=np.expand_dims(data, axis=0) / 10,  # pasado a centímetros
                dims=("ID", "time", "n_var", "axis"),
                coords={
                    "ID": [file.parent.parts[-2] + "_" + file.stem],
                    "time": (np.arange(0, data.shape[0]) / freq),
                    "n_var": (n_var_new),
                    "axis": (["x", "y", "z"]),
                },
                name="Trayectorias",
                attrs={
                    "freq": freq,
                    "units": "cm",
                },
            ).transpose("ID", "n_var", "axis", "time")
            da.time.attrs["units"] = "s"
            # Se queda solo con las trayectorias
            da = da.sel(n_var=~da.n_var.str.contains("USERMO"))
            # da.isel(ID=0, axis=0).plot.line(x='time', hue='n_var')

            daAllFiles.append(da)
            print("Tiempo {0:.3f} s \n".format(time.time() - timerSub))
            num_processed_files += 1

        except Exception as err:
            print("\nATTENTION. Unable to process " + file.name, err, "\n")
            error_files.append(os.path.basename(file.name) + " " + str(err))
            continue

    daAllFiles = xr.concat(
        daAllFiles, dim="ID"
    )  # .transpose('ID', 'n_var', 'side', 'axis', 'time')

    print(
        "Cargados {0:d} archivos en {1:.3f} s \n".format(
            num_processed_files, time.time() - timer
        )
    )
    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to process:")
        for x in range(len(error_files)):
            print(error_files[x])
    # *******************************************************

    if n_vars_load:
        daAllFiles = daAllFiles.sel(n_var=n_vars_load)

    # daAllFiles.isel(ID=0).sel(n_var=['HJC', 'KJC', 'AJC']).plot.line(x='time', col='side', hue='n_var')

    """
    #Añade coordenada con nombre del tipo de test. Diferencia entre MVC y dinámicos, por el criterio de nombrado
    if daAllFiles.ID[0].str.contains('MVC'):
        lista_coords = daAllFiles.ID.to_series().str.split('_').str[-1].str.split('-').str[-2]
    else:
        lista_coords = daAllFiles.ID.to_series().str.split('_').str[-1].str.split('-').str[0]
    daAllFiles = daAllFiles.assign_coords(test=('ID', lista_coords))
    """

    return daAllFiles


def split_trajectories_sides(daData) -> xr.DataArray:
    L = daData.sel(n_var=daData.n_var.str.endswith("_L"))
    R = daData.sel(n_var=daData["n_var"].str.endswith("_R"))
    LR = daData.sel(n_var=daData["n_var"].str.endswith("_LR"))
    # [i for i in da.n_var.data if '_L' in i and '_LR' not in i])#nomVarsContinuas_L) #el L es distinto porque incluye _L y _LR
    # daAllFiles.sel(n_var=list(daAllFiles.n_var[daAllFiles['n_var'].str.endswith('_LR').data].data))

    # Quita las terminaciones después de _
    L["n_var"] = ("n_var", L["n_var"].str.rstrip(to_strip="_L").data)
    R["n_var"] = ("n_var", R["n_var"].str.rstrip(to_strip="_R").data)
    LR["n_var"] = ("n_var", LR["n_var"].str.rstrip(to_strip="_LR").data)

    # Integra LR en L y R (para no gastar memoria en dimensión side coordenada LR)
    L = xr.concat([L, LR], dim="n_var")
    R = xr.concat([R, LR], dim="n_var")
    # R.isel(ID=0, axis=0).sel(n_var='AngBiela').plot.line(x='time')

    """daTodos = (xr.concat([L, R, LR], dim='side')
               .assign_coords(side=['L', 'R', 'LR'])
               .transpose('ID', 'n_var', 'side', 'axis', 'time')
               )"""
    daData = xr.concat(
        [L, R],
        pd.Index(["L", "R"], name="side"),  # compat='no_conflicts'
    )  # .transpose('ID', 'n_var', 'side', 'axis', 'time')
    # daData.isel(ID=0, axis=0).sel(n_var='AngBiela').plot.line(x='time')

    return daData


# =============================================================================
# %%Load all csv files in the same dataframe. Kinem and EMG version
# =============================================================================
def load_csv_generic_pl_xr(
    file_list: List[str | Path],
    n_vars_load: List[str] | None = None,
    section: str | None = None,
) -> xr.DataArray:
    """Load all csv files into the same dataframe. Cinem and EMG version."""
    from biomdp.io.read_vicon_csv import read_vicon_csv

    # Polars version
    print("\nLoading files...")
    timerCarga = time.perf_counter()
    num_processed_files = 0
    # dfTodos = []
    daTodos = []
    error_files = []
    for nf, file in enumerate(file_list[:]):
        print(f"Loading file num. {nf + 1} / {len(file_list)}: {file.name}")
        try:
            timerSub = time.perf_counter()

            daProvis = read_vicon_csv(
                file,
                section=section,
                n_vars_load=n_vars_load,
                engine="polars",
            ).expand_dims(
                {
                    "ID": [
                        f"{file.parent.parts[-2].replace('_', '')}_{'_'.join(file.stem.split('-'))}"
                    ]
                },
                axis=0,
            )  # Añade columna ID
            daTodos.append(daProvis)

            print(f"{len(daProvis.time)} rows and {len(daProvis.n_var)} columns")
            print("Time {0:.3f} s \n".format(time.perf_counter() - timerSub))
            num_processed_files += 1

        except Exception as err:  # Si falla anota un error y continúa
            print(
                "\nATTENTION. Unable to process {0}, {1}, {2}".format(
                    file.parent.name, file.name, err
                ),
                "\n",
            )
            error_files.append(file.parent.name + " " + file.name + " " + str(err))
            continue

    daTodos = xr.concat(daTodos, dim="ID")
    # dfTodos = pl.concat(dfTodos)

    print(
        f"Loaded {num_processed_files} files in {time.perf_counter() - timerCarga:.3f} s \n"
    )

    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to process:")
        for x in range(len(error_files)):
            print(error_files[x])

    return daTodos


def load_c3d_generic_xr(file_list, n_vars_load=None, section=None) -> xr.DataArray:
    from biomdp.io.read_vicon_c3d import read_vicon_c3d

    print("\nLoading files...")
    timerCarga = time.perf_counter()

    num_processed_files = 0
    # dfTodos = []
    daTodos = []
    error_files = []
    for nf, file in enumerate(file_list[:]):
        print(f"Loading file nº {nf + 1} / {len(file_list)}: {file.name}")
        try:
            timerSub = time.perf_counter()

            daProvis = read_vicon_c3d(
                file, section=section, n_vars_load=n_vars_load
            ).expand_dims(
                {
                    "ID": [
                        f"{file.parent.parts[-2].replace('_', '')}_{'_'.join(file.stem.split('-'))}"
                    ]
                },
                axis=0,
            )  # add ID columns
            # daProvis.isel(ID=0).sel(n_var='AngArtHip_R', axis='y').plot.line(x='time')
            daTodos.append(daProvis)

            print(f"{len(daProvis.time)} filas y {len(daProvis.n_var)} columnas")
            print("Time {0:.3f} s \n".format(time.perf_counter() - timerSub))
            num_processed_files += 1

        except Exception as err:
            print(
                "\nATTENTION. Unable to process {0}, {1}, {2}".format(
                    file.parent.name, file.name, err
                ),
                "\n",
            )
            error_files.append(file.parent.name + " " + file.name + " " + str(err))
            continue

    print(
        f"Cargados {num_processed_files} archivos en {time.perf_counter() - timerCarga:.3f} s \n"
    )

    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to load:")
        for x in range(len(error_files)):
            print(error_files[x])

    daTodos = xr.concat(daTodos, dim="ID", coords="minimal").astype("float")

    return daTodos


def load_preprocess_csv_cinem(
    file_list, n_vars_load=None, n_preprocessed_file=None
) -> xr.DataArray:
    from biomdp.io.read_vicon_csv import read_vicon_csv_pd

    # if n_preprocessed_file==None:
    #     raise Exception('Debes indicar el nombre de los archivos preprocesados')

    # nomVarsDiscretas240 = ['FrecuenciaPedaleo_y',
    #                     'AngArtLHipPedalAnt_x', 'AngArtRHipPedalAnt_x',
    #                     'AngArtLKneePedalAnt_x', 'AngArtRKneePedalAnt_x',
    #                     'AngArtLKneeMaxExt_x', 'AngArtRKneeMaxExt_x']

    # En versiones del modelo anteriores a la 2.5.0 se ajustan los nombres de las variables para hacer facil distinción de lateralidad
    rename_vars_coords = {
        "AngArtLHip_x": "AngArtHip_L_x",
        "AngArtRHip_x": "AngArtHip_R_x",
        "AngArtLHip_y": "AngArtHip_L_y",
        "AngArtRHip_y": "AngArtHip_R_y",
        "AngArtLHip_z": "AngArtHip_L_z",
        "AngArtRHip_z": "AngArtHip_R_z",
        "AngArtLKnee_x": "AngArtKnee_L_x",
        "AngArtRKnee_x": "AngArtKnee_R_x",
        "AngArtLKnee_y": "AngArtKnee_L_y",
        "AngArtRKnee_y": "AngArtKnee_R_y",
        "AngArtLKnee_z": "AngArtKnee_L_z",
        "AngArtRKnee_z": "AngArtKnee_R_z",
        "AngArtLAnkle_x": "AngArtAnkle_L_x",
        "AngArtLAnkle_y": "AngArtAnkle_L_y",
        "AngArtLAnkle_z": "AngArtAnkle_L_z",
        "AngArtRAnkle_x": "AngArtAnkle_R_x",
        "AngArtRAnkle_y": "AngArtAnkle_R_y",
        "AngArtRAnkle_z": "AngArtAnkle_R_z",
        "AngArtLumbar_x": "AngArtLumbar_LR_x",
        "AngArtLumbar_y": "AngArtLumbar_LR_y",
        "AngArtLumbar_z": "AngArtLumbar_LR_z",
        "AngSegPELVIS_x": "AngSegPELVIS_LR_x",
        "AngSegPELVIS_y": "AngSegPELVIS_LR_y",
        "AngSegPELVIS_z": "AngSegPELVIS_LR_z",
        "AngSegTORAX_x": "AngSegTORAX_LR_x",
        "AngSegTORAX_y": "AngSegTORAX_LR_y",
        "AngSegTORAX_z": "AngSegTORAX_LR_z",
        "AngArtCuello_x": "AngArtCuello_LR_x",
        "AngArtCuello_y": "AngArtCuello_LR_y",
        "AngArtCuello_z": "AngArtCuello_LR_z",
        "AngArtL1_x": "AngArtL1_LR_x",
        "AngArtL1_y": "AngArtL1_LR_y",
        "AngBiela_y": "AngBiela_LR_y",
        "vAngBiela": "vAngBiela_LR_x",
    }
    rename_vars = {
        "AngArtLHip": "AngArtHip_L",
        "AngArtRHip": "AngArtHip_R",
        "AngArtLKnee": "AngArtKnee_L",
        "AngArtRKnee": "AngArtKnee_R",
        "AngArtLAnkle": "AngArtAnkle_L",
        "AngArtRAnkle": "AngArtAnkle_R",
        "AngArtLumbar": "AngArtLumbar_LR",
        "AngSegPELVIS": "AngSegPELVIS_LR",
        "AngSegTORAX": "AngSegTORAX_LR",
        "AngArtCuello": "AngArtCuello_LR",
        "AngArtL1": "AngArtL1_LR",
        "AngBiela": "AngBiela_LR",
        "vAngBiela": "vAngBiela_LR",
        "LHJC": "HJC_L",
        "RHJC": "HJC_R",
        "LKJC": "KJC_L",
        "RKJC": "KJC_R",
        "LAJC": "AJC_L",
        "RAJC": "AJC_R",
        "LPosPedal": "PosPedal_L",
        "RPosPedal": "PosPedal_R",
        "X": "x",
        "Y": "y",
        "Z": "z",
    }

    print("Loading files...")
    timer = time.time()
    # nomVarsACargar = nomVarsContinuas#+nomVarsDiscretas

    dfAllFiles = []
    error_files = []
    num_processed_files = 0
    for file in file_list:
        # print(file.name)
        try:
            timerSub = time.time()
            print("Loading file: {0:s}".format(file.name))
            dfprovis, freq = read_vicon_csv_pd(
                file,
                n_block="Model Outputs",
                returnFreq=True,
                header_format="noflat",
            )
            # dfprovis, daprovis, freq = read_vicon_csv(file, n_block='Model Outputs', returnFreq=True, formatoxArray=True)

            dfprovis = (
                dfprovis.loc[
                    :, ~dfprovis.columns.duplicated()
                ]  # quita duplicados (aparecen en centros articulares)
                .rename(columns=rename_vars)  # , inplace=True)
                .sort_index()
            )

            if n_vars_load:
                dfprovis = dfprovis[n_vars_load]

            # Duplica AngBiela para _L, _R y _LR
            dfprovis = pd.concat(
                [
                    dfprovis,
                    dfprovis[["AngBiela_LR"]].rename(
                        columns={"AngBiela_LR": "AngBiela_L"}
                    ),
                    dfprovis[["AngBiela_LR"]].rename(
                        columns={"AngBiela_LR": "AngBiela_R"}
                    ),
                ],
                axis=1,
            )

            # Ajusta el AngBiela R para ser como el L pero con diferencia de 180º
            dfprovis.loc[:, ("AngBiela_R", "x")] = (
                dfprovis.loc[:, ("AngBiela_R", "x")].where(
                    dfprovis.loc[:, ("AngBiela_R", "x")] < np.pi,
                    dfprovis.loc[:, ("AngBiela_R", "x")] - 2 * np.pi,
                )
                + np.pi
            )
            dfprovis.loc[:, ("AngBiela_R", "y")] = (
                dfprovis.loc[:, ("AngBiela_R", "x")] - np.pi
            )  # dfprovis.loc[:, ('AngBiela_R', 'y')].where(dfprovis.loc[:, ('AngBiela_R', 'y')]<0.0, dfprovis.loc[:, ('AngBiela_R', 'y')]-2*np.pi)+np.pi
            dfprovis.loc[:, ("AngBiela_R", "z")] = (
                dfprovis.loc[:, ("AngBiela_R", "z")].where(
                    dfprovis.loc[:, ("AngBiela_R", "z")] < 0.0,
                    dfprovis.loc[:, ("AngBiela_R", "z")] - 2 * np.pi,
                )
                + np.pi
            )

            ######
            """
            #calcula velocidad angular biela y la añade
            #primero calcula el ángulo unwrapeado        
            if dfprovis['AngBiela']['y'].isnull()[0]: #comprueba si el primer valor es nulo, y le asigna un valor siguiendo la tendencia
                dfprovis.loc[0,('AngBiela','y')] = dfprovis.loc[1,('AngBiela','y')] - (dfprovis.loc[2,('AngBiela','y')]-dfprovis.loc[1,('AngBiela','y')])
            AngBielaUnwrap = np.unwrap(dfprovis[('AngBiela','y')])
            vAngBiela = np.gradient(AngBielaUnwrap)/(1/freq)
            """

            # Añade columna ID y time
            dfprovis.insert(
                0, "ID", [file.parent.parts[-2] + "_" + file.stem] * len(dfprovis)
            )
            dfprovis.insert(
                1, "time", np.arange(len(dfprovis))[0 : len(dfprovis)] / freq
            )  # la parte final es para asegurarse de que se queda con el tamaño adecuado

            dfAllFiles.append(dfprovis)

            # dfAllFiles.append(dfprovis.assign(**{'ID' : file.parent.parts[-2]+'_'+file.stem, #adaptar esto según la estructura de carpetas
            #                                           #'vAngBiela' : vAngBiela,
            #                                           'time' : np.arange(0, len(dfprovis)/freq, 1/freq)[0:len(dfprovis)] #la parte final es para asegurarse de que se queda con el tamaño adecuado
            #                                          }))#.reset_index(drop=True))

            print("Tiempo {0:.3f} s \n".format(time.time() - timerSub))
            num_processed_files += 1

        except Exception as err:
            print("\nATTENTION. Unable to process " + file.name, err, "\n")
            error_files.append(os.path.basename(file.name) + " " + str(err))
            continue

    dfAllFiles = pd.concat(dfAllFiles)

    # dfAllFiles.loc[:,(slice(None), '')]

    # dfAllFiles.rename(columns={'':'x'}, inplace=True)

    """
    dfAllFiles.loc[:, ('vAngBiela','')].rename({'':'x'})#, inplace=True)
    dfAllFiles.loc[:, ('vAngBiela','')].columns=pd.MultiIndex.from_frame(('vAngBiela','x'))
    dfAllFiles['vAngBiela'].name=('vAngBiela','x')
    dfAllFiles.loc[:, ('vAngBiela','')].rename(('vAngBiela','x'), inplace=True)
    """
    # dfAllFiles['SujID'] = dfAllFiles['ID'].str.split('_', expand=True)[0]
    # dfAllFiles['Grupo'] = dfAllFiles['ID'].str.split('_', expand=True)[2]

    print(
        "Cargados {0:d} archivos en {1:.3f} s \n".format(
            num_processed_files, time.time() - timer
        )
    )
    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to process:")
        for x in range(len(error_files)):
            print(error_files[x])
    # *******************************************************

    # Reordena columnas
    # if n_vars_load==None: #Se queda con todas las variables
    #     n_vars_load = dfAllFiles.columns.to_list()

    # dfAllFiles = dfAllFiles.reindex(columns=['ID', 'time'] + n_vars_load, level=0)
    # -------------------------------
    # Ahora traspasa todos los datos a dadaArray separando en L, R y LR. Se podría hacer que vaya haciendo los cortes antes de juntar L, R y LR
    # df = dfAllFiles.set_index([('ID','x'), ('time','x')]).stack()
    # df = dfAllFiles.set_index(['ID', 'time']).stack().to_xarray().to_array().rename({'variable':'n_var'})
    # df.index.rename(['ID', 'time' , 'axis'], inplace=True)
    # df = df.reorder_levels([0,2,1], axis='index')

    # ----------------
    """
    #Duplica la variable usada para hacer los cortes para que funcione el segmenta_xr
    import itertools
    dfprovis = dfAllFiles.copy()
    for bloque in itertools.product(['AngBiela_L', 'AngBiela_R', 'AngBiela_LR'], ['x', 'y', 'z']):
        dfprovis.loc[:, bloque] = dfAllFiles.loc[:, ('AngBiela_LR', 'y')]
    """
    # ----------------

    daTodos = (
        dfAllFiles.set_index(["ID", "time"])
        .stack()
        .to_xarray()
        .to_array()
        .rename({"variable": "n_var"})
    )  # .transpose('ID', 'n_var', 'axis', 'time')
    # daTodos.isel(ID=0).sel(n_var='AngBiela_LR')

    # da = df.to_xarray().to_array().rename({'variable':'n_var'})#.transpose('ID', 'variable', 'axis', 'time').rename({'variable':'n_var'})
    L = daTodos.sel(
        n_var=daTodos.n_var.str.endswith("_L")
    )  # [i for i in da.n_var.data if '_L' in i and '_LR' not in i])#nomVarsContinuas_L) #el L es distinto porque incluye _L y _LR
    R = daTodos.sel(n_var=daTodos["n_var"].str.endswith("_R"))
    LR = daTodos.sel(
        n_var=list(daTodos.n_var[daTodos["n_var"].str.endswith("_LR").data].data)
    )

    # Quita las terminaciones después de _
    L["n_var"] = ("n_var", L["n_var"].str.rstrip(to_strip="_L").data)
    R["n_var"] = ("n_var", R["n_var"].str.rstrip(to_strip="_R").data)
    LR["n_var"] = ("n_var", LR["n_var"].str.rstrip(to_strip="_LR").data)

    """daTodos = (xr.concat([L, R, LR], dim='side')
               .assign_coords(side=['L', 'R', 'LR'])
               .transpose('ID', 'n_var', 'side', 'axis', 'time')
               )"""
    daTodos = xr.concat([L, R, LR], pd.Index(["L", "R", "LR"], name="side")).transpose(
        "ID", "n_var", "side", "axis", "time"
    )
    try:
        daTodos.loc[dict(n_var=["HJC", "KJC", "AJC"])] /= (
            10  # pasa las posiciones de los ejes a cm
        )
    except:
        pass
    # daTodos.isel(ID=0).sel(n_var='AngBiela')

    # Calcula vAngBiela
    vAngBiela = (
        xr.apply_ufunc(np.unwrap, daTodos.sel(n_var="AngBiela"))
        .differentiate(coord="time")
        .expand_dims(dim=["n_var"])
        .assign_coords(dict(n_var=["vAngBiela"]))
    )
    vAngBiela = np.rad2deg(vAngBiela)  # pasa de radianes a grados
    daTodos = xr.concat(
        [daTodos, vAngBiela], dim="n_var", join="left"
    )  # join left para que guarde el orden de coords lado
    # Añade coordenada con nombre del tipo de test
    daTodos = daTodos.assign_coords(
        test=("ID", daTodos.ID.to_series().str.split("_").str[-1].str.split("-").str[0])
    )

    daTodos.name = "Cinem"
    daTodos.attrs["freq"] = float(freq)
    daTodos.attrs["units"] = "deg"
    daTodos.time.attrs["units"] = "s"

    if False:
        vAngBiela.sel(n_var="vAngBiela").plot.line(
            x="time", row="ID", col="side", hue="axis", sharey=False
        )
        daTodos.sel(n_var="vAngBiela").plot.line(
            x="time", row="ID", col="side", hue="axis", sharey=False
        )

        daTodos.isel(ID=slice(0, -1)).sel(
            n_var="AngArtKnee", axis="x", side=["L", "R"]
        ).plot.line(x="time", col="side")

        daTodos.isel(ID=slice(0, -1)).sel(n_var="AngBiela", side="LR").plot.line(
            x="time", col="axis", hue="ID"
        )
        daTodos.isel(ID=slice(2, 4)).sel(n_var="vAngBiela", side="LR").plot.line(
            x="time", col="axis", hue="ID", sharey=False
        )
    # -------------------------------

    # Pone el df en formato 1 nivel encabezados
    dfAllFiles.columns = dfAllFiles.columns.map("_".join).str.strip()
    dfAllFiles = dfAllFiles.rename(columns={"ID_": "ID", "time_": "time"})
    # EL DATAFRAME VA SIN vAngBiela

    return dfAllFiles, daTodos


def load_preprocess_c3d_cinem(file_list, n_vars_load=None) -> xr.DataArray:
    try:
        import c3d
    except:
        raise ImportError("c3d module not found. Install with: pip install c3d")
    try:
        import ezc3d
    except:
        raise ImportError(
            "ezc3d module not found. Install with: pip install ezc3d or conda install -c conda-forge ezc3d"
        )

    print("Loading files...")
    timer = time.time()

    daAllFiles = []
    error_files = []
    num_processed_files = 0
    for file in file_list:
        # cambia extensión de csv a c3d
        file = file.with_suffix(".c3d")
        print(file.name)
        try:
            timerSub = time.time()
            print("Loading file: {0:s}".format(file.name))

            with open(file, "rb") as handle:
                reader = c3d.Reader(handle)

                freq = reader.point_rate

                points = []
                for i, (_, p, _) in enumerate(reader.read_frames()):
                    points.append(p)
                    # analog.append(a)
                    if not i % 10000 and i:
                        print("Extracted %d point frames", len(points))

                labels = [s.replace(" ", "") for s in reader.point_labels]
            data = np.concatenate(points, axis=1)

            # data=np.asarray(analog)#[:,:,:3]

            da = xr.DataArray(
                data=np.expand_dims(data, axis=0) / 10,
                dims=("ID", "n_var", "time"),
                coords={
                    "ID": [file.parent.parts[-2] + "_" + file.stem],
                    "n_var": (labels),
                    "time": (np.arange(0, data.shape[1]) / freq),
                },
                name="Cinem",
                attrs={
                    "freq": float(freq),
                    "units": "deg",
                },
            )
            da.time.attrs["units"] = "s"
            # da.isel(ID=0).plot.line(x='time', hue='n_var')

            if n_vars_load:
                da = da.sel(n_var=n_vars_load)

            rename_vars = {
                "EMG1": "GLU_R",
                "EMG2": "BIC_R",
                "EMG3": "REC_R",
                "EMG4": "VME_R",
                "EMG5": "GAS_R",
                "EMG6": "TIB_R",
                "EMG7": "GLU_L",
                "EMG8": "BIC_L",
                "EMG9": "REC_L",
                "EMG10": "VME_L",
                "EMG11": "GAS_L",
                "EMG12": "TIB_L",
            }
            # TODO: De momento no deja reemplazar nombre por nombre, hay que confiar en que respete el orden
            da = da.assign_coords(
                n_var=(
                    [
                        "GLU_R",
                        "BIC_R",
                        "REC_R",
                        "VME_R",
                        "GAS_R",
                        "TIB_R",
                        "GLU_L",
                        "BIC_L",
                        "REC_L",
                        "VME_L",
                        "GAS_L",
                        "TIB_L",
                    ]
                )
            )

            daAllFiles.append(da)
            print("Tiempo {0:.3f} s \n".format(time.time() - timerSub))
            num_processed_files += 1

        except Exception as err:
            print("\nATTENTION. Unable to process " + file.name, err, "\n")
            error_files.append(os.path.basename(file.name) + " " + str(err))
            continue

    daAllFiles = xr.concat(
        daAllFiles, dim="ID"
    )  # .transpose('ID', 'n_var', 'side', 'axis', 'time')

    print(
        "Cargados {0:d} archivos en {1:.3f} s \n".format(
            num_processed_files, time.time() - timer
        )
    )
    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to process:")
        for x in range(len(error_files)):
            print(error_files[x])
    # *******************************************************

    daAllFiles = df_to_da_EMG(daAllFiles)
    # Añade coordenada con nombre del tipo de test. Diferencia entre MVC y dinámicos, por el criterio de nombrado
    if daAllFiles.ID[0].str.contains("MVC"):
        lista_coords = (
            daAllFiles.ID.to_series().str.split("_").str[-1].str.split("-").str[-2]
        )
    else:
        lista_coords = (
            daAllFiles.ID.to_series().str.split("_").str[-1].str.split("-").str[0]
        )
    daAllFiles = daAllFiles.assign_coords(test=("ID", lista_coords))

    return daAllFiles


# ------------------------------
def load_preprocess_csv_EMG_pl_xr(
    file_list, n_vars_load=None, n_block="Devices", freqEMG=None
) -> xr.DataArray:
    # TODO: Polars version unfinished
    from biomdp.io.read_vicon_csv import read_vicon_csv

    print("Loading files...")
    timer = time.time()

    dfAllFiles = []
    error_files = []
    num_processed_files = 0
    for file in file_list:
        print(file.name)
        try:
            timerSub = time.time()
            print("Loading file: {0:s}".format(file.name))

            dfprovis = read_vicon_csv(
                file, section=n_block, raw=True, engine="polars"
            )  # to_dataarray=False)

            freq = 1 / dfprovis[2, "time"] - dfprovis[0, "time"]

            if n_vars_load:
                dfprovis = dfprovis[n_vars_load]

            if n_block == "Devices":
                rename_vars = {
                    "EMG1": "GLU_R",
                    "EMG2": "BIC_R",
                    "EMG3": "REC_R",
                    "EMG4": "VME_R",
                    "EMG5": "GAS_R",
                    "EMG6": "TIB_R",
                    "EMG7": "GLU_L",
                    "EMG8": "BIC_L",
                    "EMG9": "REC_L",
                    "EMG10": "VME_L",
                    "EMG11": "GAS_L",
                    "EMG12": "TIB_L",
                }
                dfprovis = (
                    dfprovis.rename(columns=rename_vars)
                    .sort_index()
                    .iloc[:, : len(rename_vars)]
                )

            elif n_block == "Model Outputs":
                # Añade el ángulo de la biela para lado L y R interpolando de marcadores a EMG
                angBiela = dfprovis["AngBiela"]["y"]
                angBiela = np.interp(
                    np.arange(len(dfprovis) * freqEMG / freq) / freqEMG,
                    np.arange(len(angBiela)) / freq,
                    angBiela,
                )

                dPedal_z = dfprovis["PosPedal_R"]["z"] - dfprovis["PosPedal_L"]["z"]
                dPedal_z = np.interp(
                    np.arange(len(dfprovis) * freqEMG / freq) / freqEMG,
                    np.arange(len(dPedal_z)) / freq,
                    dPedal_z,
                )

                dfprovis = pd.DataFrame(
                    np.asarray([angBiela, angBiela, dPedal_z, dPedal_z]).T,
                    columns=["AngBiela_L", "AngBiela_R", "dPedal_z_L", "dPedal_z_R"],
                )
                freq = freqEMG

            # Añade columna ID y time
            dfprovis.insert(
                0, "ID", [file.parent.parts[-2] + "_" + file.stem] * len(dfprovis)
            )
            # dfprovis.insert(0, 'ID', [file.stem]*len(dfprovis))
            if "time" not in dfprovis.columns:
                dfprovis.insert(
                    1, "time", np.arange(len(dfprovis))[0 : len(dfprovis)] / freq
                )  # la parte final es para asegurarse de que se queda con el tamaño adecuado

            dfAllFiles.append(dfprovis)

            # dfAllFiles.append(dfprovis.assign(**{'ID' : file.parent.parts[-2]+'_'+file.stem, #adaptar esto según la estructura de carpetas
            #                                           #'vAngBiela' : vAngBiela,
            #                                           'time' : np.arange(0, len(dfprovis)/freq, 1/freq)[0:len(dfprovis)] #la parte final es para asegurarse de que se queda con el tamaño adecuado
            #                                          }))#.reset_index(drop=True))

            print("Time {0:.3f} s \n".format(time.time() - timerSub))
            num_processed_files += 1

        except Exception as err:
            print("\nATTENTION. Unable to process " + file.name, err, "\n")
            error_files.append(os.path.basename(file.name) + " " + str(err))
            continue

    dfAllFiles = pd.concat(dfAllFiles)

    print(
        "{0:d} files loades in {1:.3f} s \n".format(
            num_processed_files, time.time() - timer
        )
    )
    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to process:")
        for x in range(len(error_files)):
            print(error_files[x])
    # *******************************************************
    # ----------------
    daTodos = df_to_da_EMG(dfAllFiles)
    # Añade coordenada con nombre del tipo de test
    daTodos = daTodos.assign_coords(
        test=("ID", daTodos.ID.to_series().str.split("_").str[-1].str.split("-").str[0])
    )

    daTodos = daTodos * 1000  # pasa a milivoltios
    daTodos.name = "EMG"
    daTodos.attrs["freq"] = float(freq)
    daTodos.attrs["units"] = "mV"
    daTodos.time.attrs["units"] = "s"
    # daTodos.isel(ID=0).sel(n_var='GLU')

    # daTodos.isel(ID=slice(0,-1)).plot.line(x='time', col='side', row='n_var', sharey=False)

    # -------------------------------

    return daTodos  # , dfAllFiles, float(freq)


def load_preprocess_csv_EMG(
    file_list, n_vars_load=None, n_block="Devices", freqEMG=None
) -> xr.DataArray:
    from biomdp.io.read_vicon_csv import read_vicon_csv_pd

    print("Loading files...")
    timer = time.time()

    dfAllFiles = []
    error_files = []
    num_processed_files = 0
    for file in file_list:
        print(file.name)
        try:
            timerSub = time.time()
            print("Loading file: {0:s}".format(file.name))

            dfprovis, freq = read_vicon_csv_pd(
                file, n_block=n_block, returnFreq=True, header_format="noflat"
            )
            # dfprovis, daprovis, freq = read_vicon_csv(file, n_block='Model Outputs', returnFreq=True, formatoxArray=True)
            if n_vars_load:
                dfprovis = dfprovis[n_vars_load]

            if n_block == "Devices":
                rename_vars = {
                    "EMG1": "GLU_R",
                    "EMG2": "BIC_R",
                    "EMG3": "REC_R",
                    "EMG4": "VME_R",
                    "EMG5": "GAS_R",
                    "EMG6": "TIB_R",
                    "EMG7": "GLU_L",
                    "EMG8": "BIC_L",
                    "EMG9": "REC_L",
                    "EMG10": "VME_L",
                    "EMG11": "GAS_L",
                    "EMG12": "TIB_L",
                }
                dfprovis = (
                    dfprovis.rename(columns=rename_vars)
                    .sort_index()
                    .iloc[:, : len(rename_vars)]
                )

            elif n_block == "Model Outputs":
                # Añade el ángulo de la biela para lado L y R interpolando de marcadores a EMG
                angBiela = dfprovis["AngBiela"]["y"]
                angBiela = np.interp(
                    np.arange(len(dfprovis) * freqEMG / freq) / freqEMG,
                    np.arange(len(angBiela)) / freq,
                    angBiela,
                )

                dPedal_z = dfprovis["PosPedal_R"]["z"] - dfprovis["PosPedal_L"]["z"]
                dPedal_z = np.interp(
                    np.arange(len(dfprovis) * freqEMG / freq) / freqEMG,
                    np.arange(len(dPedal_z)) / freq,
                    dPedal_z,
                )

                dfprovis = pd.DataFrame(
                    np.asarray([angBiela, angBiela, dPedal_z, dPedal_z]).T,
                    columns=["AngBiela_L", "AngBiela_R", "dPedal_z_L", "dPedal_z_R"],
                )
                freq = freqEMG

            # Añade columna ID y time
            dfprovis.insert(
                0, "ID", [file.parent.parts[-2] + "_" + file.stem] * len(dfprovis)
            )
            # dfprovis.insert(0, 'ID', [file.stem]*len(dfprovis))
            if "time" not in dfprovis.columns:
                dfprovis.insert(
                    1, "time", np.arange(len(dfprovis))[0 : len(dfprovis)] / freq
                )  # la parte final es para asegurarse de que se queda con el tamaño adecuado

            dfAllFiles.append(dfprovis)

            # dfAllFiles.append(dfprovis.assign(**{'ID' : file.parent.parts[-2]+'_'+file.stem, #adaptar esto según la estructura de carpetas
            #                                           #'vAngBiela' : vAngBiela,
            #                                           'time' : np.arange(0, len(dfprovis)/freq, 1/freq)[0:len(dfprovis)] #la parte final es para asegurarse de que se queda con el tamaño adecuado
            #                                          }))#.reset_index(drop=True))

            print("Time {0:.3f} s \n".format(time.time() - timerSub))
            num_processed_files += 1

        except Exception as err:
            print("\nATTENTION. Unable to process " + file.name, err, "\n")
            error_files.append(os.path.basename(file.name) + " " + str(err))
            continue

    dfAllFiles = pd.concat(dfAllFiles)

    print(
        "{0:d} files loaded in {1:.3f} s \n".format(
            num_processed_files, time.time() - timer
        )
    )
    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to process:")
        for x in range(len(error_files)):
            print(error_files[x])
    # *******************************************************
    # ----------------
    daTodos = df_to_da_EMG(dfAllFiles)
    # Añade coordenada con nombre del tipo de test
    daTodos = daTodos.assign_coords(
        test=("ID", daTodos.ID.to_series().str.split("_").str[-1].str.split("-").str[0])
    )

    daTodos = daTodos * 1000  # pasa a milivoltios
    daTodos.name = "EMG"
    daTodos.attrs["freq"] = float(freq)
    daTodos.attrs["units"] = "mV"
    daTodos.time.attrs["units"] = "s"
    # daTodos.isel(ID=0).sel(n_var='GLU')

    # daTodos.isel(ID=slice(0,-1)).plot.line(x='time', col='side', row='n_var', sharey=False)

    # -------------------------------

    return daTodos  # , dfAllFiles, float(freq)


def load_preprocess_c3d_EMG(
    file_list, n_vars_load=None, n_block="Devices", freqEMG=None
) -> xr.DataArray:
    try:
        import c3d
    except:
        raise ImportError("c3d module not found. Install with: pip install c3d")

    print("Loading files...")
    timer = time.time()

    daAllFiles = []
    error_files = []
    num_processed_files = 0
    for file in file_list:
        # cambia extensión de csv a c3d
        file = file.with_suffix(".c3d")
        print(file.name)
        try:
            timerSub = time.time()
            print("Loading file: {0:s}".format(file.name))

            with open(file, "rb") as handle:
                reader = c3d.Reader(handle)

                freqEMG = reader.analog_rate
                # n_var = reader.analog_labels

                analog = []
                for i, (_, _, a) in enumerate(reader.read_frames()):
                    # points.append(p)
                    analog.append(a)
                    if not i % 10000 and i:
                        print(f"Extracted {len(analog)} point frames")

                labels = [
                    s.split(".")[0].replace(" ", "") for s in reader.analog_labels
                ]
            data = np.concatenate(analog, axis=1) * 1000  # pasa a milivoltios

            # data=np.asarray(analog)#[:,:,:3]

            da = xr.DataArray(
                data=np.expand_dims(data, axis=0),
                dims=("ID", "n_var", "time"),
                coords={
                    "ID": [file.parent.parts[-2] + "_" + file.stem],
                    "n_var": (labels),
                    "time": (np.arange(0, data.shape[1]) / freqEMG),
                },
                name="EMG",
                attrs={
                    "freq": freqEMG,
                    "units": "mV",
                },
            )
            da.time.attrs["units"] = "s"
            # da.isel(ID=0).plot.line(x='time', hue='n_var')

            if n_vars_load:
                da = da.sel(n_var=n_vars_load)

            if n_block == "Devices":
                rename_vars = {
                    "EMG1": "GLU_R",
                    "EMG2": "BIC_R",
                    "EMG3": "REC_R",
                    "EMG4": "VME_R",
                    "EMG5": "GAS_R",
                    "EMG6": "TIB_R",
                    "EMG7": "GLU_L",
                    "EMG8": "BIC_L",
                    "EMG9": "REC_L",
                    "EMG10": "VME_L",
                    "EMG11": "GAS_L",
                    "EMG12": "TIB_L",
                }
                # TODO: De momento no deja reemplazar nombre por nombre, ahy que confiar en que respete el orden
                da = da.assign_coords(
                    n_var=(
                        [
                            "GLU_R",
                            "BIC_R",
                            "REC_R",
                            "VME_R",
                            "GAS_R",
                            "TIB_R",
                            "GLU_L",
                            "BIC_L",
                            "REC_L",
                            "VME_L",
                            "GAS_L",
                            "TIB_L",
                        ]
                    )
                )

            daAllFiles.append(da)
            print("Time {0:.3f} s \n".format(time.time() - timerSub))
            num_processed_files += 1

        except Exception as err:
            print("\nATTENTION. Unable to process " + file.name, err, "\n")
            error_files.append(os.path.basename(file.name) + " " + str(err))
            continue

    daAllFiles = xr.concat(
        daAllFiles, dim="ID"
    )  # .transpose('ID', 'n_var', 'side', 'axis', 'time')

    print(
        "{0:d} files loades in {1:.3f} s \n".format(
            num_processed_files, time.time() - timer
        )
    )
    # Inform errors
    if len(error_files) > 0:
        print("\nATTENTION. Unable to process:")
        for x in range(len(error_files)):
            print(error_files[x])
    # *******************************************************

    daAllFiles = df_to_da_EMG(daAllFiles)
    # Añade coordenada con nombre del tipo de test. Diferencia entre MVC y dinámicos, por el criterio de nombrado
    if daAllFiles.ID[0].str.contains("MVC"):
        lista_coords = (
            daAllFiles.ID.to_series().str.split("_").str[-1].str.split("-").str[-2]
        )
    else:
        lista_coords = (
            daAllFiles.ID.to_series().str.split("_").str[-1].str.split("-").str[0]
        )
    daAllFiles = daAllFiles.assign_coords(test=("ID", lista_coords))

    return daAllFiles


# =============================================================================


# =============================================================================
# %%
# =============================================================================
if __name__ == "__main__":
    if False:
        r"""
        sys.path.append(r'F:\Programacion\Python\Mios\Functions')
        import Nexus_FuncionesApoyo as nfa
        """
        # Cargando directamente desde c3d
        ruta_trabajo = Path(
            r"F:\Investigacion\Proyectos\BikeFitting\Bikefitting\EstudioEMG_MVC\Registros\17_Eduardo"
        )

        file_list = list(
            ruta_trabajo.glob("**/*.c3d")
        )  # incluye los que haya en subcarpetas
        file_list = [
            x for x in file_list if "MVC-" not in x.name and "Estatico" not in x.name
        ]
        file_list.sort()

        daDatos = load_c3d_generic_xr(
            file_list[:10], section="Trajectories"
        )  # , n_vars_load=['HJC', 'KJC', 'AJC'])
        daDatos = adjust_labels_side_end(daDatos)
        daDatos = split_trajectories_sides(daDatos)
        # daAngles = calculate_angles_desde_trajec(daDatos)
        # daPos = calcula_variables_posicion(daDatos)
        # daCinem = xr.concat([daAngles, daPos], dim='n_var')
