import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_soil_temperature_image_roi(json_data, from_date, to_date):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)

    def scale_index(img):
        return img.multiply(1).subtract(273).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    soil_temperature_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start_date, end_date).select('soil_temperature_level_1').map(scale_index)

    # Calculate the mean temperature image
    mean_soil_temperature_image = soil_temperature_collection.mean().clip(roi)

    minMax = mean_soil_temperature_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('soil_temperature_level_1_min')
        max_image = minMax.get('soil_temperature_level_1_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = -5
        st.session_state['max'] = 40

    return mean_soil_temperature_image
def create_soil_temperature_timeseries_roi(json_data, from_date, to_date):
    roi = ee.FeatureCollection(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)
    def scale_index(img):
        return img.multiply(1).subtract(273).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    soil_temperature_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterBounds(roi).filterDate(start_date, end_date).select('soil_temperature_level_1').map(scale_index)

    # Create a list of dates and mean temperature values
    timeseries = soil_temperature_collection.map(lambda image: ee.Feature(None, {
        'date': image.date().format(),
        'soil_temperature_level_1': image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=11132  # Adjust scale according to your data resolution
        ).get('soil_temperature_level_1')
    }))

    # Convert to a Pandas DataFrame
    timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'soil_temperature_level_1']).values().get(0).getInfo()
    df = pd.DataFrame(timeseries_list, columns=['date', 'soil_temperature_level_1'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %Y')
    st.session_state['soil_temperature_chart_data'] = df

    # Create a time-series plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
    df.plot(x='date', y='soil_temperature_level_1', ax=ax, legend=True, title='Soil Temperature Time Series')
    plt.xlabel('Date', fontsize=6)
    plt.ylabel('Soil Temperature (C)')
    plt.grid(True)
    plt.tight_layout()

    return fig
