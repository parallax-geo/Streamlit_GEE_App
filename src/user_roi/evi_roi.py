import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_evi_image_roi(json_data, from_date, to_date):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)

    def scale_index(img):
        return img.multiply(0.0001).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    evi_collection = ee.ImageCollection("MODIS/061/MOD13Q1").filterDate(start_date, end_date).select('EVI').map(scale_index)

    # Calculate the mean temperature image
    mean_evi_image = evi_collection.mean().clip(roi)

    minMax = mean_evi_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('EVI_min')
        max_image = minMax.get('EVI_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = 0
        st.session_state['max'] = 1

    return mean_evi_image
def create_evi_timeseries_roi(json_data, from_date, to_date):
    roi = ee.FeatureCollection(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)
    def scale_index(img):
        return img.multiply(0.0001).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    evi_collection = ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(roi).filterDate(start_date, end_date).select('EVI').map(scale_index)

    # Create a list of dates and mean temperature values
    timeseries = evi_collection.map(lambda image: ee.Feature(None, {
        'date': image.date().format(),
        'evi': image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=json_data,
            scale=250  # Adjust scale according to your data resolution
        ).get('EVI')
    }))

    # Convert to a Pandas DataFrame
    timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'evi']).values().get(0).getInfo()
    df = pd.DataFrame(timeseries_list, columns=['date', 'evi'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %Y')
    st.session_state['evi_chart_data'] = df

    # Create a time-series plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
    df.plot(x='date', y='evi', ax=ax, legend=True, title='EVI Time Series')
    plt.xlabel('Date', fontsize=6)
    plt.ylabel('Mean EVI')
    plt.grid(True)
    plt.tight_layout()

    return fig
