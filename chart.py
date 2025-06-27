import streamlit as st
import streamlit.components.v1 as components


# HTML and JavaScript code for Google Chart
html_code = """
<div id="myChart" style="max-width:700px; height:400px"></div>
<script src="https://www.gstatic.com/charts/loader.js"></script>
<script>
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawChart);
    
    function drawChart() {
        // Set Data
        const data = google.visualization.arrayToDataTable([
            ['Price', 'Size'],
            [50, 7], [60, 8], [70, 8], [80, 9], [90, 9],
            [100, 9], [110, 10], [120, 11], [130, 14], [140, 14], [150, 15]
        ]);
        // Set Options
        const options = {
            title: 'House Prices vs Size',
            hAxis: {title: 'Square Meters'},
            vAxis: {title: 'Price in Millions'},
            legend: 'none'
        };
        // Draw Chart
        const chart = new google.visualization.LineChart(document.getElementById('myChart'));
        chart.draw(data, options);
    }
</script>
"""

# Embed the HTML and JavaScript in Streamlit
st.components.v1.html(html_code, height=400)
