import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_et_image_roi(json_data, from_date, to_date):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)
    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)

    def scale_index(img):
        return img.multiply(0.1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    et_collection = ee.ImageCollection("MODIS/061/MOD16A2").filterDate(start_date, end_date).select('ET').map(scale_index)

    # Calculate the mean temperature image
    mean_et_image = et_collection.mean().clip(roi)

    minMax = mean_et_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )

    try:
        # Access min and max values from the minMax dictionary
        min_image = minMax.get('ET_min')
        max_image = minMax.get('ET_max')

        st.session_state['min'] = min_image.getInfo()
        st.session_state['max'] = max_image.getInfo()
    except:
        st.session_state['min'] = 0
        st.session_state['max'] = 20

    return mean_et_image
def create_et_timeseries_roi(json_data, from_date, to_date):
    dataset = ee.FeatureCollection(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)
    def scale_index(img):
        return img.multiply(0.1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    et_collection = ee.ImageCollection("MODIS/061/MOD16A2").filterBounds(dataset).filterDate(start_date, end_date).select('ET').map(scale_index)

    # Create a list of dates and mean temperature values
    timeseries = et_collection.map(lambda image: ee.Feature(None, {
        'date': image.date().format(),
        'ET': image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=json_data,
            scale=1000  # Adjust scale according to your data resolution
        ).get('ET')
    }))

    # Convert to a Pandas DataFrame
    timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'ET']).values().get(0).getInfo()
    df = pd.DataFrame(timeseries_list, columns=['date', 'ET'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %Y')
    st.session_state['et_chart_data'] = df

    # Create a time-series plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
    df.plot(x='date', y='ET', ax=ax, legend=True, title='ET Time Series')
    plt.xlabel('Date', fontsize=6)
    plt.ylabel('Mean Evapotranspiration (ET)')
    plt.grid(True)
    plt.tight_layout()

    return fig
