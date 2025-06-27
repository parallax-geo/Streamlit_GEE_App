import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

try:
    def get_soil_moisture_image_roi(geojson_data, from_date, to_date):
        roi = ee.FeatureCollection(geojson_data)

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)

        def scale_index(img):
            return img.multiply(1).copyProperties(img,['system:time_start','date','system:time_end'])
        # Filter the ERA temperature collection by date
        soil_moisture_collection = ee.ImageCollection("NASA_USDA/HSL/SMAP10KM_soil_moisture").filterBounds(roi).filterDate(start_date, end_date).select('ssm').map(scale_index)

        # Calculate the mean temperature image
        mean_soil_moisture_image = soil_moisture_collection.mean().clip(roi)

        minMax = mean_soil_moisture_image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=roi,
            scale=100,
            bestEffort=True
        )

        area = roi.geometry(0.01).area().divide(1e6)

        try:
            # Access min and max values from the minMax dictionary
            min_image = minMax.get('ssm_min')
            max_image = minMax.get('ssm_max')

            st.session_state['min'] = min_image.getInfo()
            st.session_state['max'] = max_image.getInfo()
            st.session_state['area'] = area.getInfo()
        except:
            st.session_state['min'] = 0
            st.session_state['max'] = 20
            st.session_state['area'] = area.getInfo()

        return mean_soil_moisture_image

    def create_soil_moisture_timeseries_roi(geojson_data, from_date, to_date):
        try:
            roi = ee.FeatureCollection(geojson_data)

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

            # Convert to a Pandas DataFrame
            timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'ssm']).values().get(0).getInfo()
            df = pd.DataFrame(timeseries_list, columns=['date', 'ssm'])
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            st.session_state['soil_moisture_chart_data'] = df

            # Create a time-series plot
            fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
            df.plot(x='date', y='ssm', ax=ax, legend=True, title='Soil Moisture Time Series')
            plt.xlabel('Date', fontsize=6)
            plt.ylabel('Soil Moisture mm')
            plt.grid(True)
            plt.tight_layout()

            return fig
        except Exception as e:
            st.write('No Data Available')
except Exception as e:
        st.write('No Data Available')