import streamlit as st
import ee
import pandas as pd
import matplotlib.pyplot as plt

import streamlit.components.v1 as components


try:
    # Function to get NDVI image clipped by the sub-basin and dates
    def get_ndvi_image(selected_sub_basin, from_date, to_date):
        if selected_sub_basin == 'None':
            return None
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        sub_basin_feature = dataset.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)

        def scale_index(img):
            return img.multiply(0.0001).copyProperties(img,['system:time_start','date','system:time_end'])

        # Filter the MODIS NDVI collection by date
        ndvi_collection = ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(sub_basin_feature).filterDate(start_date, end_date).select('NDVI').map(scale_index)

        # Calculate the mean NDVI image
        mean_ndvi_image = ndvi_collection.mean().clip(sub_basin_feature)

        minMax = mean_ndvi_image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=sub_basin_feature,
            scale=100,
            bestEffort=True
        )

        area = sub_basin_feature.geometry(0.01).area().divide(1e6)

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

        sub_basin_geometry = sub_basin_feature.geometry()
        mean_ndvi_image_region = ndvi_collection.mean().clipToBoundsAndScale(geometry=sub_basin_geometry, maxDimension=1000)

        return mean_ndvi_image, mean_ndvi_image_region

    def create_ndvi_timeseries(selected_sub_basin, from_date, to_date):
        
        if selected_sub_basin == 'None':
            return None
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        sub_basin_feature = dataset.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))

        # Convert dates to ee.Date objects
        start_date = ee.Date(from_date)
        end_date = ee.Date(to_date)

        def scale_index(img):
            return img.multiply(0.0001).copyProperties(img,['system:time_start','date','system:time_end'])

        # Filter the MODIS NDVI collection by date
        ndvi_collection = ee.ImageCollection("MODIS/061/MOD13Q1").filterBounds(sub_basin_feature).filterDate(start_date, end_date).select('NDVI').map(scale_index)

        # Create a list of dates and mean NDVI values
        timeseries = ndvi_collection.map(lambda image: ee.Feature(None, {
            'date': image.date().format(),
            'NDVI': image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=sub_basin_feature,
                scale=250
            ).get('NDVI')
        }))

        # Convert to a Pandas DataFrame
        timeseries_list = timeseries.reduceColumns(ee.Reducer.toList(2), ['date', 'NDVI']).values().get(0).getInfo()
        df = pd.DataFrame(timeseries_list, columns=['date', 'NDVI'])
        # df['date'] = pd.to_datetime(df['date'])
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        st.session_state['ndvi_chart_data'] = df
        # st.write(df)


        # date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        # formatted_date = date_obj.strftime("%Y-%m-%d")


        # Create a time-series plot
        fig, ax = plt.subplots(figsize=(10, 6)) #10 x 6
        df.plot(x='date', y='NDVI', ax=ax, legend=True, title='NDVI Time Series')
        plt.xlabel('Date',fontsize=6)
        plt.ylabel('Mean NDVI')
        plt.grid(True)
        plt.tight_layout()


        # list_of_dates = []
        # list_of_ndvi = []

        # for date in df['date']:
        #     list_of_dates.append(date)
        # for ndvi in df['NDVI']:
        #     list_of_ndvi.append(ndvi)
        
        # output = [list(pair) for pair in zip(list_of_dates, list_of_ndvi)]
        # output.insert(0,['date','NDVI'])
        # print(output,'My Output')

        # html_code = '''
        # <div id="myChart" style="height:600px"></div>
        # <script src="https://www.gstatic.com/charts/loader.js"></script>
        # <script>
        #     google.charts.load('current', {'packages':['corechart']});
        #     google.charts.setOnLoadCallback(drawChart);
            
        #     function drawChart() {
        #         // Set Data
        #         const data = google.visualization.arrayToDataTable([
        #         ["date", "NDVI"], [new Date(2024,04,06), 0.1323356644228998], [new Date(2024,04,022), 0.16599354785273343], [new Date(2024,05,8), 0.1779333698393415]

        #         ]);
        #         // Set Options
        #         const options = {
        #             title: 'NDVI Time-Series',
        #             hAxis: {title: 'Date', format: 'Y-M-d'},
        #             vAxis: {title: 'NDVI'},
        #             legend: 'none'
        #         };
        #         // Draw Chart
        #         const chart = new google.visualization.LineChart(document.getElementById('myChart'));
        #         chart.draw(data, options);
        #     }
        # </script>
        # '''

        return fig
except Exception as e:
    st.write('Something Went Wrong!')



