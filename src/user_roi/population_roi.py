import ee
import streamlit as st

def get_population_image_roi(json_data):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    population_data = ee.ImageCollection("WorldPop/GP/100m/pop_age_sex_cons_unadj").select('population').filterBounds(roi).filterDate('2020-01-01','2023-12-31').mean().clip(roi)

    minMax = population_data.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('population_min')
        max_image = minMax.get('population_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = 0
        st.session_state['max'] = 100
    return population_data