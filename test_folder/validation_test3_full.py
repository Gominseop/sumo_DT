import pandas as pd
import numpy as np
import math
import xml.etree.ElementTree as ET


def validation_volume(test_file, answer_df, d, t):
    targets = list(answer_df["road"])

    tree = ET.parse(test_file)
    root = tree.getroot()
    interval = root.findall("interval")[0]
    edges = interval.findall("edge")

    result = pd.DataFrame(columns=["date", "time", "road", "result_volume", "answer_volume",
                                   "GEH", "GEH_group", "SQV", "SQV_group"])
    j = 0

    for edge in edges:
        i = edge.attrib["id"]
        if '_' in i:
            continue
        volume = int(edge.attrib["arrived"]) if edge.attrib["left"] == "0" else int(edge.attrib["left"])

        if i in targets:
            an = target_answer[target_answer["road"] == i]["volume"].values[0]
            geh = round(math.sqrt(2*((volume-an)**2)/(volume+an)), 2)
            if geh <= 5:
               gg = 0
            elif geh <= 10:
                gg = 1
            else:
                gg = 2
            sqv = round(1/(1+math.sqrt(((volume-an)**2)/(1000*an))), 2)
            if sqv >= 0.9:
                sg = 0
            elif sqv >= 0.85:
                sg = 1
            elif sqv >= 0.8:
                sg = 2
            else:
                sg = 3
            result.loc[j] = [d, t, i, volume, an, geh, gg, sqv, sg]
            j += 1

    return result


def validation_speed(test_file, answer_df):
    targets = list(answer_df["road"])

    tree = ET.parse(test_file)
    root = tree.getroot()
    interval = root.findall("interval")[0]
    edges = interval.findall("edge")

    result = pd.DataFrame(columns=["road", "result_speed", "answer_speed", "max_speed", "result_ratio", "answer_ratio"])
    j = 0

    for edge in edges:
        i = edge.attrib["id"]
        if '_' in i:
            continue
        speed = 0.0
        speed_rel = 0.00
        if "speed" in edge.attrib:
            speed = float(edge.attrib["speed"])
            speed_rel = float(edge.attrib["speedRelative"])

        if i in targets:
            tmp = target_answer[target_answer["road"] == i]
            speed_anw = tmp["speed"].values[0]
            max_speed = tmp["max_speed"].values[0]
            ratio_anw = tmp["speed_ratio"].values[0]
        else:
            speed_anw = -1
            max_speed = -1
            ratio_anw = -1

        result.loc[j] = [i, speed, speed_anw, max_speed, speed_rel, ratio_anw]
        j += 1

    return result


if __name__=="__main__":
    answer_file = "volume_answer.csv"
    answer = pd.read_csv(answer_file, encoding='cp949')

    # vv = pd.DataFrame(columns=["date", "time", "road", "result_volume", "answer_volume",
    #                            "GEH", "GEH_group", "SQV", "SQV_group"])
    vv = None

    for tt in range(10, 12, 1):
        for td in range(1, 31, 1):
            if td in [1, 2, 3, 10, 24]:
                continue

            target_answer = answer[answer["date"] == td]
            target_answer = target_answer[target_answer["time"] == tt]

            for s in range(1, 101, 1):
                test_file = f"result_3_full_folder/{s}.test3_full_{td}_{tt}_edge.xml"
                com_vol = validation_volume(test_file, target_answer, td, tt)
                if vv is None:
                    vv = com_vol
                else:
                    vv = pd.concat([vv, com_vol])

    vv.to_csv(f"volume_validation_test3_full.csv", encoding='cp949', index=False)
