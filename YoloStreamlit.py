from AI.Yolo import get_teeth_presenceAISlop


def streamlit_to_Yolo(image_bytes, list , list2,conf = 0.5):

    present_teeth, missing_teeth = get_teeth_presenceAISlop(image_bytes, conf)
    list.append(missing_teeth)
    list2.append(present_teeth)
    return list,list2