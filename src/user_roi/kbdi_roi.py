import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_kbdi_image_roi(json_data, from_date, to_date):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)

    def scale_index(img):
        return img.multiply(1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    kbdi_collection = ee.ImageCollection("UTOKYO/WTLAB/KBDI/v1").filterDate(start_date, end_date).select('KBDI').map(scale_index)

    # Calculate the mean temperature image
    mean_kbdi_image = kbdi_collection.mean().clip(roi)

    minMax = mean_kbdi_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('KBDI_min')
        max_image = minMax.get('KBDI_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = 0
        st.session_state['max'] = 800

    return mean_kbdi_image
def create_kbdi_timeseries_roi(json_data, from_date, to_date):
    roi = ee.FeatureCollection(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)
    def scale_index(img):
        return img.multiply(1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    kbdi_collection = ee.ImageCollection("UTOKYO/WTLAB/KBDI/v1").filterBounds(roi).filterDate(start_date, end_date).select('KBDI').map(scale_index)

    # Create a list of dates and mean temperature values
    timeseries = kbdi_collection.map(lambda image: ee.Feature(None, {
        'date': image.date().format(),
        'KBDI': image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=4000  # Adjust scale according to your data resolution
        ).get('KBDI')
    }))

    # Convert to a Pandas DataFrame
    timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'KBDI']).values().get(0).getInfo()
    df = pd.DataFrame(timeseries_list, columns=['date', 'KBDI'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %Y')
    st.session_state['kbdi_chart_data'] = df

    # Create a time-series plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
    df.plot(x='date', y='KBDI', ax=ax, legend=True, title='KBDI Time Series')
    plt.xlabel('Date', fontsize=6)
    plt.ylabel('Mean KBDI')
    plt.grid(True)
    plt.tight_layout()

    return fig
