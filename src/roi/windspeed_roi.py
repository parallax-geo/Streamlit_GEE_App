import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

try:
    def get_windspeed_image_roi(json_data, from_date, to_date):
        roi = ee.FeatureCollection(json_data)

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)

        def scale_index(img):
            ws = img.expression("sqrt((u**2)+(v**2))",{
                    "u": img.select('u_component_of_wind_10m'),
                    "v": img.select('v_component_of_wind_10m'),
                }).rename('windspeed')
            return ws.copyProperties(img,['system:time_start','date','system:time_end'])
        # Filter the ERA temperature collection by date
        windspeed_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterBounds(roi).filterDate(start_date, end_date).select(['u_component_of_wind_10m','v_component_of_wind_10m']).map(scale_index)

        # Calculate the mean temperature image
        mean_windspeed_image = windspeed_collection.mean().clip(roi)

        minMax = mean_windspeed_image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=roi,
            scale=30,
            bestEffort=True
        )

        area = roi.geometry(0.01).area().divide(1e6)

        try:
            # Access min and max values from the minMax dictionary
            min_image = minMax.get('v_component_of_wind_10m_min')
            max_image = minMax.get('v_component_of_wind_10m_max')

            st.session_state['min'] = min_image.getInfo()
            st.session_state['max'] = max_image.getInfo()
            st.session_state['area'] = area.getInfo()
        except:
            st.session_state['min'] = 0
            st.session_state['max'] = 6
            st.session_state['area'] = area.getInfo()

        return mean_windspeed_image

    def create_windspeed_timeseries_roi(json_data, from_date, to_date):
        roi = ee.FeatureCollection(json_data)

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)
        def scale_index(img):
            ws = img.expression("sqrt((u**2)+(v**2))",{
                    "u": img.select('u_component_of_wind_10m'),
                    "v": img.select('v_component_of_wind_10m'),
                }).rename('windspeed')
            return ws.copyProperties(img,['system:time_start','date','system:time_end'])
        # Filter the ERA temperature collection by date
        windspeed_collection = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterBounds(roi).filterDate(start_date, end_date).select(['u_component_of_wind_10m','v_component_of_wind_10m']).map(scale_index)

        # Create a list of dates and mean temperature values
        timeseries = windspeed_collection.map(lambda image: ee.Feature(None, {
            'date': image.date().format(),
            'windspeed': image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=11132  # Adjust scale according to your data resolution
            ).get('windspeed')
        }))

        # Convert to a Pandas DataFrame
        timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'windspeed']).values().get(0).getInfo()
        df = pd.DataFrame(timeseries_list, columns=['date', 'windspeed'])
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        st.session_state['windspeed_chart_data'] = df

        # Create a time-series plot
        fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
        df.plot(x='date', y='windspeed', ax=ax, legend=True, title='windspeed Time Series')
        plt.xlabel('Date', fontsize=6)
        plt.ylabel('windspeed (m/s)')
        plt.grid(True)
        plt.tight_layout()

        return fig
except Exception as e:
        st.write('No Data Available')