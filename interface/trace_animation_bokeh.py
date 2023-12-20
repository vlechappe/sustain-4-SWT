#!/usr/bin/env python3

import numpy as np
from bokeh.io import curdoc, show
from bokeh.layouts import column, row, gridplot, grid
from bokeh.models import ColumnDataSource, CustomJS, Slider, CheckboxGroup, Legend, LegendItem, DataTable, TableColumn, Div, HoverTool, Label
from bokeh.plotting import figure, show, output_notebook
from bokeh.models.annotations.labels import Label
import pandas as pd

# mes fichiers import perso
from init_variables import *
import bibliotheque


##############################################################
##########       def power curve data       ##################
##############################################################
# from .csv file
source_PC = bibliotheque.powercurve_from_csv("./data_csv/powercurve.csv")
#print(source_PC.data)

# from array
#source_PC = bibliotheque.powercurve_from_array(windspeed_avg_def)


######################################################
##########       impacts data from csv      ########## 
######################################################
impact_dict = {"Acidification" : "orange", "Climate change" : "blue",  "Energy" : "green", "Eutrophication" : "black", "Material ressource": "red" }
#impact_dict = {"imp1" : "orange", "imp2" : "blue"}

#source_impacts = bibliotheque.impacts_data_from_csv("./data_csv/impacts_data.csv", nb_impacts)
source_impacts, source_impacts_per_kWh = bibliotheque.impacts_data_from_csv("./data_csv/impacts_data.csv", impact_dict, z0_init, vref_init, href_init, source_PC, lifetime_init)


#print(impact_dict.keys())

#for impact, color in impact_dict.items():
#        print(impact, color)  
#print(type(source_impacts.data))
#for impact in source_impacts.data:
#        print(source_impacts.data[impact])

#for names in impact_names:
#    print(type(names))  

######################################################
##########       computation lep data      ########### 
######################################################
source_LEP_plot = bibliotheque.lep_data_computation(windspeed_avg_def, source_PC, lifetime_init)

######################################################
##########       lep data for impacts      ########### 
######################################################
#source_LEP_impacts = bibliotheque.lep_data_impacts(Vw_init, source_PC, lifetime_init)



######################################################
##################       plots     ################### 
######################################################
plot_impacts, impact_renderer, legend = bibliotheque.figure_impacts(size_plot, props, source_impacts_per_kWh, impact_dict)
plot_PC = bibliotheque.figure_PC(size_plot, props, source_PC)
plot_LEP = bibliotheque.figure_LEP(size_plot, props, source_LEP_plot)


######################################################
##########      Definitions des widgets    ########## 
######################################################
z0_widget = bibliotheque.slider_widget_definition(z0_widget_def, "Roughness length"+r"$$z_0$$"+"(m)")
windspeed_avg_widget = bibliotheque.slider_widget_definition(windspeed_avg_def, "Average windspeed "+r"$$V_{avg}$$"+"(m/s)")
lifetime_widget = bibliotheque.slider_widget_definition(lifetime_def,"Lifetime (year)")
h_widget = bibliotheque.slider_widget_definition(h_def,"Mast height " + r"$$h$$"+"(m)")
href_widget = bibliotheque.slider_widget_definition(href_def, r"$$h_{ref}$$"+"(m)")
vref_widget = bibliotheque.slider_widget_definition(vref_def, r"$$V_{ref}$$"+"(m/s)")
table_widget = bibliotheque.dataTable_widget_definition(source_PC)
impacts_widget= bibliotheque.checkboxGroup_widget_definition(impact_dict)

text_LEP_div, text_LEP_formula_div, text_EROI_div, text_PC_div, v_avg_div, map_widget = bibliotheque.div_definition(Vw_init, source_PC, lifetime_init)


######################################################
##########      Definitions des callback     ########## 
######################################################
# Update impacts per kWh computation
# attention pas de inline comment avec   //...
# calcul lep ok
callback = CustomJS(args=dict(source_impacts=source_impacts, source_impacts_per_kWh=source_impacts_per_kWh, z0=z0_widget, href=href_widget, vref=vref_widget, lifetime=lifetime_widget, source_PC = source_PC),
                    code="""
    const Z = z0.value
    const hr = href.value
    const vr = vref.value
    const life = lifetime.value
    const P = source_PC.data["P"]
    const V = source_PC.data["V"]
    const h = source_impacts.data["h"]
    const v_avg = Array.from(h, (h) => vr*Math.log(h/Z)/Math.log(hr/Z))
    const lep = new Array(h.length) 
    var F = new Array(h.length)
    function js_compute_LEP(life, F, P) {
         var sum=0
         for (let i = 1; i < F.length-1; i++) {
             sum=sum+(F[i]-F[i-1])*(P[i-1]+P[i])/2
         } 
         return life*8760*sum ;
    }
    for (const [key, value] of Object.entries(source_impacts_per_kWh.data)) {
        if (key != "h"){
            for (let i = 0; i < v_avg.length; i++) {
                F = Array.from(V, (V) => 1-Math.exp(-Math.PI*Math.pow(V,2)/(4*Math.pow(v_avg[i],2))))
                lep[i]=js_compute_LEP(life, F, P)/1000
                source_impacts_per_kWh.data[key][i] =  source_impacts.data[key][i]/lep[i]
            }
        }
    }
    source_impacts_per_kWh.change.emit()
""")


# Update display of impact according to selected impact
callback2 = CustomJS(args=dict(impact_renderer=impact_renderer, impacts=impacts_widget, legend=legend, impact_dict = impact_dict),
                    code="""
    const nb_impacts=Object.keys(impact_dict).length
    for (let i = 0; i < nb_impacts; i++) {
        //permet d afficher ou de cacher la courbe quand on clique ou pas
        impact_renderer[i].visible = impacts.active.includes(i);
        //permet d afficher ou de cacher la legende associee quand on clique ou pas
        if (impacts.active.includes(i)==0){
        legend.items[i].visible=false;
        }
        else{
        legend.items[i].visible=true;
        }
    }
""")
# update LEP computation
callback3 = CustomJS(args=dict(text_widget=text_LEP_div, windspeed_avg=windspeed_avg_widget, lifetime=lifetime_widget, source_PC=source_PC),
                    code="""
    const v_avg_1 = windspeed_avg.value
    const life = lifetime.value
    const P = source_PC.data["P"]
    const V = source_PC.data["V"]
    var F = Array.from(V, (V) => 1-Math.exp(-Math.PI*Math.pow(V,2)/(4*Math.pow(v_avg_1,2))))
    function js_compute_LEP(life, F, P) {
        var sum=0
        for (let i = 1; i < F.length-1; i++) {
            sum=sum+(F[i]-F[i-1])*(P[i-1]+P[i])/2
        } 
        return life*8760*sum ;
    }
    const lep = Math.round(js_compute_LEP(life, F, P)/1000)
    text_widget.text="Lifetime Energy Production (LEP) : "+lep.toString()+" kWh"
    //source_LEP_impacts.data["lep"]=lep
""")

# update LEP plot
callback4 = CustomJS(args=dict(lifetime=lifetime_widget, source_LEP_plot=source_LEP_plot, source_PC=source_PC),
                    code="""
    const life = lifetime.value
    const P=source_PC.data["P"]
    const V=source_PC.data["V"]
    const v_avg = source_LEP_plot.data["v_avg"] 
    const lep = new Array(v_avg.length)
    var F = new Array(V.length) 
    function js_compute_LEP(life, F, P) {
         var sum=0
         for (let i = 1; i < F.length-1; i++) {
             sum=sum+(F[i]-F[i-1])*(P[i-1]+P[i])/2
         } 
         return life*8760*sum ;
    }
    for (let i = 0; i < v_avg.length; i++) {
             F = Array.from(V, (V) => 1-Math.exp(-Math.PI*Math.pow(V,2)/(4*Math.pow(v_avg[i],2))))
             lep[i]=js_compute_LEP(life, F, P)/1000
    } 
    source_LEP_plot.data = {v_avg, lep}     
""")

#update average windspeed computations
# computation validated in matlab
callback5 = CustomJS(args=dict(z0=z0_widget, h=h_widget, href=href_widget, vref=vref_widget, v_avg=windspeed_avg_widget),
                    code="""
     const Z = z0.value
     const height = h.value
     const hr = href.value
     const vr = vref.value
     const vavg = vr*Math.log(height/Z)/Math.log(hr/Z)
     v_avg.value=vavg
""")

#update average windspeed computations
# computation validated in matlab
callback6 = CustomJS(args=dict(z0=z0_widget, map_widget = map_widget),
                    code="""
     const Z = z0.value
     const size = "1000x1000"

    if (Z<0.5){
        map_widget.text = "<iframe src=/home/vlechappe/Desktop/INSA/divers/python/tracer_map/data/new/map_new_10x10.html style='min-width:calc(50vw - 26px); height: 500px'><iframe>" 
    }
    else{
        map_widget.text = "<iframe src=/home/vlechappe/Desktop/INSA/divers/python/tracer_map/data/new/map_new_"+size+".html style='min-width:calc(50vw - 26px); height: 500px'><iframe>" 
    }
""")
#console.log(text_widget)


##################################################
##########      Lien widgets/callbacks     #######
##################################################
z0_widget.js_on_change('value', callback)
href_widget.js_on_change('value', callback)
vref_widget.js_on_change('value', callback)
lifetime_widget.js_on_change('value', callback)
source_PC.selected.js_on_change('indices', callback)



impacts_widget.js_on_change('active', callback2)

windspeed_avg_widget.js_on_change('value', callback3)
lifetime_widget.js_on_change('value', callback3)
source_PC.selected.js_on_change('indices', callback3)

# when vavg is modified LEP should be modify 
z0_widget.js_on_change('value', callback3)
h_widget.js_on_change('value', callback3)
href_widget.js_on_change('value', callback3)
vref_widget.js_on_change('value', callback3)

lifetime_widget.js_on_change('value', callback4)

z0_widget.js_on_change('value', callback5)
h_widget.js_on_change('value', callback5)
href_widget.js_on_change('value', callback5)
vref_widget.js_on_change('value', callback5)

z0_widget.js_on_change('value', callback6)


#################################################################
##########      definition du layout pour affichage     #########
#################################################################
column_1=column(impacts_widget,  lifetime_widget, text_LEP_div, text_LEP_formula_div, text_EROI_div)
layout_widget=column(h_widget, z0_widget, href_widget, vref_widget)
grid_v_avg=grid([ [v_avg_div],[layout_widget,windspeed_avg_widget]])
grid_main = grid([[plot_impacts, column_1, table_widget, text_PC_div], [grid_v_avg, plot_LEP, plot_PC, None], [map_widget]])
#curdoc().add_root(layout)
show(grid_main)



