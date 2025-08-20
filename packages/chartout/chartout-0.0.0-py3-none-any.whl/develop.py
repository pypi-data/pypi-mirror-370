def altair_heatmap():
    import altair as alt
    import numpy as np
    import pandas as pd

    # Compute x^2 + y^2 across a 2D grid
    x, y = np.meshgrid(range(-5, 5), range(-5, 5))
    z = x**2 + y**2

    # Convert this grid to columnar data expected by Altair
    source = pd.DataFrame({"x": x.ravel(), "y": y.ravel(), "z": z.ravel()})

    chart = alt.Chart(source).mark_rect().encode(x="x:O", y="y:O", color="z:Q")
    return chart

def altair_comet():
    import altair as alt
    import vega_datasets

    chart = alt.Chart(
        vega_datasets.data.barley.url,
        title='Barley Yield comparison between 1932 and 1931'
    ).mark_trail().encode(
        alt.X('year:O').title(None),
        alt.Y('variety:N').title('Variety'),
        alt.Size('yield:Q')
            .scale(range=[0, 12])
            .legend(values=[20, 60])
            .title('Barley Yield (bushels/acre)'),
        alt.Color('delta:Q')
            .scale(domainMid=0)
            .title('Yield Delta (%)'),
        alt.Tooltip(['year:O', 'yield:Q']),
        alt.Column('site:N').title('Site')
    ).transform_pivot(
        "year",
        value="yield",
        groupby=["variety", "site"]
    ).transform_fold(
        ["1931", "1932"],
        as_=["year", "yield"]
    ).transform_calculate(
        calculate="datum['1932'] - datum['1931']",
        as_="delta"
    ).configure_legend(
        orient='bottom',
        direction='horizontal'
    ).configure_view(
        stroke=None
    )  
    return chart  

def altair_map_selection():
    import altair as alt
    from vega_datasets import data
    import geopandas as gpd

    # load data
    gdf_quakies = gpd.read_file(data.earthquakes.url, driver="GeoJSON")
    gdf_world = gpd.read_file(data.world_110m.url, driver="TopoJSON")

    # defintion for interactive brush
    brush = alt.selection_interval(
        encodings=["longitude"], empty=False, value={"longitude": [-50, -110]}
    )

    # world disk
    sphere = alt.Chart(alt.sphere()).mark_geoshape(
        fill="transparent", stroke="lightgray", strokeWidth=1
    )

    # countries as shapes
    world = alt.Chart(gdf_world).mark_geoshape(
        fill="lightgray", stroke="white", strokeWidth=0.1
    )

    # earthquakes as dots on map
    quakes = (
        alt.Chart(gdf_quakies)
        .transform_calculate(
            lon="datum.geometry.coordinates[0]",
            lat="datum.geometry.coordinates[1]",
        )
        .mark_circle(opacity=0.35, tooltip=True)
        .encode(
            longitude="lon:Q",
            latitude="lat:Q",
            color=alt.when(brush)
            .then(alt.value("goldenrod"))
            .otherwise(alt.value("steelblue")),
            size=alt.Size("mag:Q").scale(
                type="pow", range=[1, 1000], domain=[0, 7], exponent=4
            ),
        )
        .add_params(brush)
    )

    # combine layers for the map
    left_map = alt.layer(sphere, world, quakes).project(type="mercator")

    # histogram of binned earthquakes
    bars = (
        alt.Chart(gdf_quakies)
        .mark_bar()
        .encode(
            x=alt.X("mag:Q").bin(extent=[0, 7]),
            y="count(mag):Q",
            color=alt.value("steelblue"),
        )
    )

    # filtered earthquakes
    bars_overlay = bars.encode(color=alt.value("goldenrod")).transform_filter(brush)

    # combine layers for histogram
    right_bars = alt.layer(bars, bars_overlay)

    # vertical concatenate map and bars
    chart = left_map | right_bars
    return chart
