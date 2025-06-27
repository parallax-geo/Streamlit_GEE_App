import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import shape

try:
    def get_ndvi_image_for_roi(geojson_data, from_date, to_date):
        # Convert the GeoJSON object to an Earth Engine Geometry
        roi = ee.FeatureCollection(geojson_data)

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)

        def scale_index(img):
            return img.multiply(0.0001).copyProperties(img,['system:time_start','date','system:time_end'])


        # Filter the MODIS NDVI collection by date
        ndvi_collection = ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(roi).filterDate(start_date, end_date).select('NDVI').map(scale_index)

        # Calculate the mean NDVI image
        mean_ndvi_image = ndvi_collection.mean().clip(roi)

        minMax = mean_ndvi_image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=roi,
            scale=100,
            bestEffort=True
        )

        area = roi.geometry(0.01).area().divide(1e6)

        # Access min and max values from the minMax dictionary
        try:
            min_image = minMax.get('NDVI_min')
            max_image = minMax.get('NDVI_max')
        
            st.session_state['min'] = min_image.getInfo()
            st.session_state['max'] = max_image.getInfo()
            st.session_state['area'] = area.getInfo()
        except:
            st.session_state['min'] = 0
            st.session_state['max'] = 1
            st.session_state['area'] = area.getInfo()

        return mean_ndvi_image

    def create_ndvi_timeseries_roi(geojson_data, from_date, to_date):

        dataset = ee.FeatureCollection(geojson_data)

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)

        def scale_index(img):
            return img.multiply(0.0001).copyProperties(img, ['system:time_start', 'date', 'system:time_end'])

        # Filter the MODIS NDVI collection by date
        ndvi_collection = ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(dataset).filterDate(start_date, end_date).select('NDVI').map(scale_index)

        # Create a list of dates and mean NDVI values
        timeseries = ndvi_collection.map(lambda image: ee.Feature(None, {
            'date': image.date().format(),
            'NDVI': image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=dataset,
                scale=250
            ).get('NDVI')
        }))

        # Convert to a Pandas DataFrame
        timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'NDVI']).values().get(0).getInfo()
        df = pd.DataFrame(timeseries_list, columns=['date', 'NDVI'])
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        st.session_state['ndvi_chart_data'] = df

        # Create a time-series plot
        fig, ax = plt.subplots(figsize=(10, 6))
        df.plot(x='date', y='NDVI', ax=ax, legend=True, title='NDVI Time Series')
        plt.xlabel('Date')
        plt.ylabel('Mean NDVI')
        plt.grid(True)
        plt.tight_layout()

        return fig
except Exception as e:
        st.write('No Data Available')