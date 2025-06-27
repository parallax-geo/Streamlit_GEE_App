import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_soil_moisture_image_roi(json_data, from_date, to_date):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)

    def scale_index(img):
        return img.multiply(1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    soil_moisture_collection = ee.ImageCollection("NASA_USDA/HSL/SMAP10KM_soil_moisture").filterDate(start_date, end_date).select('ssm').map(scale_index)

    # Calculate the mean temperature image
    mean_soil_moisture_image = soil_moisture_collection.mean().clip(roi)

    minMax = mean_soil_moisture_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('ssm_min')
        max_image = minMax.get('ssm_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = 0
        st.session_state['max'] = 20

    return mean_soil_moisture_image
def create_soil_moisture_timeseries_roi(json_data, from_date, to_date):
    roi = ee.FeatureCollection(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)
    def scale_index(img):
        return img.multiply(1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    soil_moisture_collection = ee.ImageCollection("NASA_USDA/HSL/SMAP10KM_soil_moisture").filterBounds(roi).filterDate(start_date, end_date).select('ssm').map(scale_index)

    # Create a list of dates and mean temperature values
    timeseries = soil_moisture_collection.map(lambda image: ee.Feature(None, {
        'date': image.date().format(),
        'ssm': image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=10000  # Adjust scale according to your data resolution
        ).get('ssm')
    }))
    try:
    # Convert to a Pandas DataFrame
        timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'ssm']).values().get(0).getInfo()
        df = pd.DataFrame(timeseries_list, columns=['date', 'ssm'])
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %Y')
        st.session_state['soil_moisture_chart_data'] = df

        # Create a time-series plot
        fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
        df.plot(x='date', y='ssm', ax=ax, legend=True, title='Soil Moisture Time Series')
        plt.xlabel('Date', fontsize=6)
        plt.ylabel('Soil Moisture mm')
        plt.grid(True)
        plt.tight_layout()

        return fig
    except:
        st.write('No Data Available')
