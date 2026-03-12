import streamlit as st
import pandas as pd
import plotly.express as px

# Usa el ancho de la pantalla
st.set_page_config(layout="wide") 
# Título de arriba
st.title("SAR Crop Monitoring Dashboard") 

# Lectura de datos
df_saocom = pd.read_csv("CSVS/rvi.csv")
df_saocom["fecha"] = pd.to_datetime(df_saocom["fecha"])
df_saocom["year"] = df_saocom["fecha"].dt.year


# selector
shape = st.sidebar.selectbox(
    "Seleccionar polígono",
    sorted(df_saocom["shape_id"].unique())
)

poly = df_saocom[df_saocom["shape_id"] == shape]

###########################################################
st.divider()

# grafico RVI (queda igual)
fig_feno = px.line(
    poly,
    x="fecha",
    y="mean_rvi",
    markers=True,
    title=f"Serie temporal RVI para la parcela {shape} "
)

fig_feno.update_yaxes(range=[0,1],
                    title_font=dict(size=28),
                    tickfont=dict(size=18)
                    )
fig_feno.update_xaxes(
    tickangle=45,
    tickformat="%Y-%m-%d",
    title_font=dict(size=28),
    tickfont=dict(size=18)
)



fig_feno.update_layout(template="plotly_dark",
                       title_font=dict(size=30))


fig_display = fig_feno
st.plotly_chart(fig_display, use_container_width=True)

#fig_export = fig_feno
#fig_export.update_layout(width=1600, height=700)

#fig_export.write_image(f"rvi_{shape}.png", scale=2)

#fig_feno.write_image(f"rvi_{shape}.png", width=1400, height=600, scale=2)


###########################################################
st.divider()
st.subheader("Soil moisture profile (sensors)")


# leer csv de sensores dss
df_dss = pd.read_csv("CSVS/consulta_humedad_suelos.csv")
df_dss["fecha"] = pd.to_datetime(df_dss["fecha"])

# Agrego SMAP
df_smap = pd.read_csv("CSVS/smap_humedad.csv")
df_smap["fecha"] = pd.to_datetime(df_smap["fecha"])
df_smap["year"] = df_smap["fecha"].dt.year


show_smap = st.sidebar.checkbox(
    "Mostrar serie SMAP",
    value=False
)

show_saocom = st.sidebar.checkbox(
    "Mostrar serie SAOCOM",
    value=False
)


depths = [
   "0-5cm","5-15cm","15-30cm","30-45cm", 
]

selected_depths = st.sidebar.multiselect(
    "Seleccionar profundidades",
    depths,
    default=["0-5cm","5-15cm","15-30cm","30-45cm"]
)



# convertir a formato largo usando SOLO lo seleccionado
df_long = df_dss.melt(
    id_vars=["fecha"],
    value_vars=selected_depths,
    var_name="profundidad",
    value_name="humedad"
)

# agregar año
df_long["year"] = df_long["fecha"].dt.year




# separar por año
df_2024 = df_long[df_long["year"] == 2024]
df_2025 = df_long[df_long["year"] == 2025]

smap_2024 = df_smap[df_smap["year"] == 2024]
smap_2025 = df_smap[df_smap["year"] == 2025]

saocom_2024 = df_saocom[(df_saocom["year"] == 2024) & (df_saocom["shape_id"] == shape)]
saocom_2025 = df_saocom[(df_saocom["year"] == 2025) & (df_saocom["shape_id"] == shape)]


# función para generar gráfico
def make_profile_plot(df_data, df_smap,df_saocom, title):

    fig = px.line(
        df_data,
        x="fecha",
        y="humedad",
        color="profundidad",
        markers=True,
        title=title
    )

    fig.update_layout(template="plotly_dark",
                      title_font=dict(size=30))

    fig.update_yaxes(
        title="Soil Moisture",
        range=[0,50],
        title_font=dict(size=28),
        tickfont=dict(size=18)

    )
    fig.update_xaxes(
    tickangle=45,
    tickformat="%Y-%m-%d",
    title_font=dict(size=28),
    tickfont=dict(size=18)
    )
   
    if show_smap:
        
        fig.add_scatter(
            x=df_smap["fecha"],
            y=df_smap["humedad_smap"]*100,
            mode="lines+markers",
            name="SMAP Soil Moisture",
            line=dict(color="cyan", width=3)
        )

    if show_saocom:
        fig.add_scatter(
        x=df_saocom["fecha"],
        y=df_saocom["mean_ssmh"],
        mode="markers",
        name="SAOCOM",
        marker=dict(size=10, color="red"),
        error_y=dict(
        type="data",
        array=df_saocom["std_ssmh"],
        visible=True
    )
        
    )


    fig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=18)
        )
    )

    return fig


# crear figuras
fig_profile_2024 = make_profile_plot(df_2024, smap_2024, saocom_2024, "Soil moisture profile 2024")
fig_profile_2025 = make_profile_plot(df_2025, smap_2025, saocom_2025, "Soil moisture profile 2025")


#st.markdown("### Soil moisture profile 2024")
st.plotly_chart(fig_profile_2024, use_container_width=True)

#st.markdown("### Soil moisture profile 2025 -2026")
st.plotly_chart(fig_profile_2025, use_container_width=True)


