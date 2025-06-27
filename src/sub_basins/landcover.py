import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt
try:
    def get_landcover_image(selected_sub_basin):
        if selected_sub_basin == 'None':
            return None
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        sub_basin_feature = dataset.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))

        # Convert dates to ee.Date objects
        start_date = '2020-01-01'
        end_date = '2020-01-02'

        # Filter the ERA temperature collection by date
        landCover_collection = ee.ImageCollection('ESA/WorldCover/v100').filterDate(start_date, end_date)

        # Calculate the mean temperature image
        mean_landcover_image = landCover_collection.first().clip(sub_basin_feature)

        minMax = mean_landcover_image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=sub_basin_feature,
            scale=30,
            bestEffort=True
        )

        area = sub_basin_feature.geometry(0.01).area().divide(1e6)

        try:
            # Access min and max values from the minMax dictionary
            min_image = minMax.get('Map_min')
            max_image = minMax.get('Map_max')

            st.session_state['area'] = area.getInfo()
            st.session_state['min'] = min_image.getInfo()
            st.session_state['max'] = max_image.getInfo()
        except:
            st.session_state['min'] = 0
            st.session_state['max'] = 100
            st.session_state['area'] = area.getInfo()

        return mean_landcover_image
except Exception as e:
    st.write('Something Went Wrong!')