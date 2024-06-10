import plotly.express as px

def make_chart(type, data, x, y, ylabel, color, rangebreaks):
    labels = {'value': ylabel, 'variable': 'Legenda'}
    match type:
        case 'line':
            fig = px.line(data,
                          x=x,
                          y=y,
                          color_discrete_sequence=color,
                          labels=labels
                          )
        case 'bar':
            fig = px.bar(data,
                         x=x,
                         y=y,
                         color_discrete_sequence=color,
                         barmode="group",
                         labels=labels
                         )
    if rangebreaks:
        fig.update_xaxes(rangebreaks=rangebreaks)
    return fig