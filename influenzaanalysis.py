import plotly.graph_objs as go

# Data for testing results
categories = ['Influenza A', 'Influenza B', 'Negative', 'Covid-19 Negative']
values = [10.18, 1.41, 88.4, 98.06]

# Create a bar chart
fig = go.Figure(data=[go.Bar(x=categories, y=values, 
                             marker_color=['#3498db', '#2ecc71', '#95a5a6', '#e74c3c'], 
                             hoverinfo='text', 
                             hovertext=[f'{value:.2f}%' for value in values])])

# Customize the plot
fig.update_layout(title='Influenza and Covid-19 Testing Results', 
                  xaxis_title='Test Categories', 
                  yaxis_title='Percentage of Results', 
                  xaxis_tickangle=45, 
                  yaxis_range=[0, 100], 
                  font_size=14, 
                  font_family='Arial', 
                  margin=dict(l=50, r=50, t=100, b=50))

# Show the plot
fig.show()

# Save the plot as an image
fig.write_image('Influenza_Testing_Results.png', width=800, height=600)