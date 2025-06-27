import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_era_temp_image_roi(json_data, from_date, to_date):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)

    def scale_index(img):
        return img.subtract(273).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    temp_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start_date, end_date).select('temperature_2m').map(scale_index)

    # Calculate the mean temperature image
    mean_temp_image = temp_collection.mean().clip(roi)

    minMax = mean_temp_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('temperature_2m_min')
        max_image = minMax.get('temperature_2m_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = -10
        st.session_state['max'] = 55

    return mean_temp_image
def create_temp_timeseries_roi(json_data, from_date, to_date):
    dataset = ee.FeatureCollection(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)
    def scale_index(img):
        return img.subtract(273).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    temp_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start_date, end_date).select('temperature_2m').map(scale_index)

    # Create a list of dates and mean temperature values
    timeseries = temp_collection.map(lambda image: ee.Feature(None, {
        'date': image.date().format(),
        'temperature': image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=dataset,
            scale=1000  # Adjust scale according to your data resolution
        ).get('temperature_2m')
    }))

    # Convert to a Pandas DataFrame
    timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'temperature']).values().get(0).getInfo()
    df = pd.DataFrame(timeseries_list, columns=['date', 'temperature'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %Y')
    st.session_state['temp_chart_data'] = df

    # Create a time-series plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
    df.plot(x='date', y='temperature', ax=ax, legend=True, title='Temperature Time Series')
    plt.xlabel('Date', fontsize=6)
    plt.ylabel('Mean Temperature')
    plt.grid(True)
    plt.tight_layout()

    return fig
