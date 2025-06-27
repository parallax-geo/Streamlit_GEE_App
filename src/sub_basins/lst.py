import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

try:
    def get_lst_image(selected_sub_basin, from_date, to_date):
        if selected_sub_basin == 'None':
            return None
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        sub_basin_feature = dataset.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)

        def scale_index(img):
            return img.multiply(0.02).subtract(273).copyProperties(img,['system:time_start','date','system:time_end'])
        # Filter the ERA temperature collection by date
        lst_collection = ee.ImageCollection("MODIS/061/MOD11A2").filterBounds(sub_basin_feature).filterDate(start_date, end_date).select('LST_Day_1km').map(scale_index)

        # Calculate the mean temperature image
        mean_lst_image = lst_collection.mean().clip(sub_basin_feature)

        minMax = mean_lst_image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=sub_basin_feature,
            scale=30,
            bestEffort=True
        )

        area = sub_basin_feature.geometry(0.01).area().divide(1e6)

        try:
            # Access min and max values from the minMax dictionary
            min_image = minMax.get('LST_Day_1km_min')
            max_image = minMax.get('LST_Day_1km_max')
            st.session_state['min'] = min_image.getInfo()
            st.session_state['max'] = max_image.getInfo()
            st.session_state['area'] = area.getInfo()
        except:
            st.session_state['min'] = -10
            st.session_state['max'] = 75
            st.session_state['area'] = area.getInfo()

        return mean_lst_image
    def create_lst_timeseries(selected_sub_basin, from_date, to_date):
        if selected_sub_basin == 'None':
            return None
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        sub_basin_feature = dataset.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)
        def scale_index(img):
            return img.multiply(0.02).subtract(273).copyProperties(img,['system:time_start','date','system:time_end'])
        # Filter the ERA temperature collection by date
        lst_collection = ee.ImageCollection("MODIS/061/MOD11A2").filterBounds(sub_basin_feature).filterDate(start_date, end_date).select('LST_Day_1km').map(scale_index)

        # Create a list of dates and mean temperature values
        timeseries = lst_collection.map(lambda image: ee.Feature(None, {
            'date': image.date().format(),
            'LST_Day_1km': image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=sub_basin_feature,
                scale=1000  # Adjust scale according to your data resolution
            ).get('LST_Day_1km')
        }))
        timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'LST_Day_1km']).values().get(0).getInfo()
        df = pd.DataFrame(timeseries_list, columns=['date', 'LST_Day_1km'])
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        st.session_state['lst_chart_data'] = df

        # Create a time-series plot
        fig, ax = plt.subplots(figsize=(10, 6))  # Adjust the figure size as needed
        df.plot(x='date', y='LST_Day_1km', ax=ax, legend=True, title='LST (C) Time Series')
        plt.xlabel('Date', fontsize=6)
        plt.ylabel('Mean LST (C)')
        plt.grid(True)
        plt.tight_layout()

        return fig
except Exception as e:
    st.write('Something Went Wrong!')
