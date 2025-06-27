import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_landcover_image_roi(json_data):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    # Convert dates to ee.Date objects
    start_date = '2020-01-01'
    end_date = '2020-01-02'

    # Filter the ERA temperature collection by date
    landCover_collection = ee.ImageCollection('ESA/WorldCover/v100').filterDate(start_date, end_date)

    # Calculate the mean temperature image
    mean_landcover_image = landCover_collection.first().clip(roi)

    minMax = mean_landcover_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('Map_min')
        max_image = minMax.get('Map_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = 0
        st.session_state['max'] = 100

    return mean_landcover_image