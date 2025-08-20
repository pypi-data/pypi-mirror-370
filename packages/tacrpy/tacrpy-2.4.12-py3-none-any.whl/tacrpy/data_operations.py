"""
Modul pro běžné transformace a zpracování dat.
"""

import pandas as pd


def create_mapping_dict(df: pd.DataFrame) -> dict:
    """ Z dataframe, kde se k jedné hodnotě váže více pozorování v samostatných řádcích (např. projekt má N uchazečů)
    vytvoří mapovací dict

    :param df: dataframe s hodnotami one-to-many
    :return: mapovací dict, kde unikátní ID je klíč a hodnotou je seznam hodnot, které patří k danému unikátnímu ID
    """

    mapping_dict = {}
    for i in range(len(df)):
        key = df.iloc[i, 0]
        value = df.iloc[i, 1]
        mapping_dict.setdefault(key, [])
        mapping_dict[key].append(value)

    return mapping_dict


def list_intersection(list1: list, list2: list, percentages: bool = True) -> dict:
    """ Získá průnik hodnot mezi dvěma seznamy (listy) a vypočítá metriky průniku.

    Metriky průniku:

    - *intersect (list)* - seznam stejných hodnot
    - *intersect_count (int)* - počet stejných hodnot
    - *intersect_ratio (float)* - podíl stejných hodnot vůči všem unikátním hodnotám z obou seznamů
    - *intersect_l1_ratio (float)* - podíl stejných hodnot vůči všem hodnotám v prvnímu seznamu
    - *intersect_l2_ratio (float)* - podíl stejných hodnot vůči všem hodnotám v druhému seznamu


    :param list1: seznam hodnot
    :param list2: seznam hodnot
    :param percentages: poměrové metriky zobrazí vrátí v procentech (0-100) na dvě desetinná místa
    :return: dict metrik průniků
    """

    intersect = set(list1).intersection(set(list2))
    l1_count = len(set(list1))
    l2_count = len(set(list2))
    all_count = len(set(list1 + list2))
    
    intersect_count = len(intersect)
    intersect_ratio = intersect_count / all_count
    intersect_l1_ratio = intersect_count / l1_count
    intersect_l2_ratio = intersect_count / l2_count

    intersect_dict = dict()
    intersect_dict['intersect'] = list(intersect)
    intersect_dict['intersect_count'] = intersect_count
    if percentages:
        intersect_dict['intersect_ratio'] = round(intersect_ratio * 100, 2)
        intersect_dict['intersect_ratio_l1'] = round(intersect_l1_ratio * 100, 2)
        intersect_dict['intersect_ratio_l2'] = round(intersect_l2_ratio * 100, 2)
    else:
        intersect_dict['intersect_ratio'] = intersect_ratio
        intersect_dict['intersect_ratio_l1'] = intersect_l1_ratio
        intersect_dict['intersect_ratio_l2'] = intersect_l2_ratio
    return intersect_dict



