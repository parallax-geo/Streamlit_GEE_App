import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

def get_transpiration_image_roi(json_data, from_date, to_date):
    json_data = Map.user_roi
    roi = ee.Geometry(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)

    def scale_index(img):
        return img.multiply(1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    transpiration_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start_date, end_date).select('evaporation_from_vegetation_transpiration_sum').map(scale_index)

    # Calculate the mean temperature image
    mean_transpiration_image = transpiration_collection.mean().clip(roi)

    minMax = mean_transpiration_image.reduceRegion(
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
        st.session_state['min'] = 0
        st.session_state['max'] = 10

    return mean_transpiration_image
def create_transpiration_timeseries_roi(json_data, from_date, to_date):
    roi = ee.FeatureCollection(json_data)

    # Convert dates to ee.Date objects
    start_date = ee.Date(from_date)
    end_date = ee.Date(to_date)
    def scale_index(img):
        return img.multiply(1).copyProperties(img,['system:time_start','date','system:time_end'])
    # Filter the ERA temperature collection by date
    transpiration_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterBounds(roi).filterDate(start_date, end_date).select('evaporation_from_vegetation_transpiration_sum').map(scale_index)

    # Create a list of dates and mean temperature values
    timeseries = transpiration_collection.map(lambda image: ee.Feature(None, {
        'date': image.date().format(),
        'evaporation_from_vegetation_transpiration_sum': image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=11132  # Adjust scale according to your data resolution
        ).get('evaporation_from_vegetation_transpiration_sum')
    }))

    # Convert to a Pandas DataFrame
    timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'evaporation_from_vegetation_transpiration_sum']).values().get(0).getInfo()
    df = pd.DataFrame(timeseries_list, columns=['date', 'evaporation_from_vegetation_transpiration_sum'])
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%b %Y')
    st.session_state['transpiration_chart_data'] = df

    # Create a time-series plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
    df.plot(x='date', y='evaporation_from_vegetation_transpiration_sum', ax=ax, legend=True, title='Transpiration Time Series')
    plt.xlabel('Date', fontsize=6)
    plt.ylabel('Transipiration (m)')
    plt.grid(True)
    plt.tight_layout()

    return fig
