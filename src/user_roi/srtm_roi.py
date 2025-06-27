import ee
import streamlit as st

def get_srtm_image_roi(json_data):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    srtm_data = ee.Image("CGIAR/SRTM90_V4").clip(roi)

    minMax = srtm_data.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('elevation_min')
        max_image = minMax.get('elevation_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = 0
        st.session_state['max'] = 3000

    return srtm_data
