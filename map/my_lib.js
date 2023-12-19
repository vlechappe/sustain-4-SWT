////////////////////////////////////////////////////////////////////////
///////////            linspace function                ////////////////
////////////////////////////////////////////////////////////////////////
function makeArr(startValue, stopValue, cardinality) {
    var arr = [];
    var step = (stopValue - startValue) / (cardinality - 1);
    for (var i = 0; i < cardinality; i++) {
    arr.push(startValue + (step * i));
    }
    return arr;
}

////////////////////////////////////////////////////////////////////////
/////////// Legend continuous (windspeed, optimal_height)  ////////////////
////////////////////////////////////////////////////////////////////////
function legend_continuous(interval, colormap, legend_name) {
    values = makeArr(interval[0], interval[1], 100);
    colors = values.map((x)=>colormap.color(x));
    //console.log(windspeed_colors)
    var colormap_discrete = {};
    //discrete color map from continuous function colormap, there is maybe a different a to do that
    colormap_discrete.color = d3.scale.threshold() 
        .domain(values)
        .range(colors)

    colormap_discrete.x = d3.scale.linear()
              .domain(interval)
              .range([0, 400]);

    colormap_discrete.legend = L.control({position: 'topright'});
    colormap_discrete.legend.onAdd = function (map) {var div = L.DomUtil.create('div', 'legend'); return div};
    colormap_discrete.legend.addTo(map);

    colormap_discrete.xAxis = d3.svg.axis()
        .scale(colormap_discrete.x)
        .orient("top")
        .tickSize(1)
        .tickValues(interval);

    colormap_discrete.svg = d3.select(".legend.leaflet-control").append("svg")
        .attr("id", 'legend')
        .attr("width", 450)
        .attr("height", 40);

    colormap_discrete.g = colormap_discrete.svg.append("g")
        .attr("class", "key")
        .attr("transform", "translate(25,16)");

    colormap_discrete.g.selectAll("rect")
        .data(colormap_discrete.color.range().map(function(d, i) {
          //console.log(i)
          return {
            x0: i ? colormap_discrete.x(colormap_discrete.color.domain()[i - 1]) : colormap_discrete.x.range()[0],
            x1: i < colormap_discrete.color.domain().length ? colormap_discrete.x(colormap_discrete.color.domain()[i]) : colormap_discrete.x.range()[1],
            z: d
          };
        }))
        .enter().append("rect")
        .attr("height", 10)
        .attr("x", function(d) { return d.x0; })
        .attr("width", function(d) { return d.x1 - d.x0; })
        .style("fill", function(d) { return d.z; });


    colormap_discrete.g.call(colormap_discrete.xAxis).append("text")
        .attr("class", "caption")
        .attr("y", 21)
        .text(legend_name);
}


////////////////////////////////////////////////////////////////////////
//////////////////   Legend    roughness    ////////////////////////////
////////////////////////////////////////////////////////////////////////
function legend_roughness(roughness_intervals, roughness_colors) {
    var color_map_roughness = {};
    color_map_roughness.color = d3.scale.threshold()
         .domain(roughness_intervals) // 13 values
         .range(roughness_colors); // 14 values
         //.domain([0.5, 1])  // n values : the first is greater than the min scale and the last is smaller than the max scale 
         //.range(["#74add1", "#d73027", "#000000"]); //n+1 values
     
         // orange : '#ff7f0eff'
         // vert : '#2ca02cff'
         // bleu : '#1f77b4ff'
         // rouge fonce : '#d62728ff'
         // marron : '#8c564bff'
         // violet : '#9467bdff'
         // rose : '#e377c2ff'
         // gris : '#7f7f7fff'
         // vert clair: '#bcbd22ff'
         // bleu clair: '#17becfff'
         // bleu fonce : '#1f77b4ff'
         // jaune clair: '#ffffbf'
         // saumon : '#fddbc7' 
         // noir : '#000000' 

     color_map_roughness.x = d3.scale.log()  //d3.scale.log() //d3.scale.linear()
         .domain([0.001, 1.6])     // create the empty legend bar axis 
         .range([0, 600]);     // create the empty legend bar size 

     color_map_roughness.legend = L.control({position: 'topright'});
     color_map_roughness.legend.onAdd = function (map) {var div = L.DomUtil.create('div', 'legend'); return div};
     color_map_roughness.legend.addTo(map);


     color_map_roughness.xAxis = d3.svg.axis()
       .scale(color_map_roughness.x)
       .orient("top")
       .tickSize(1)
       .tickFormat(d3.format(".f"))
       .tickValues(roughness_values);

     color_map_roughness.svg = d3.select(".legend.leaflet-control").append("svg")
       .attr("id", 'legend')
       .attr("width", 700)
       .attr("height", 40);

     color_map_roughness.g = color_map_roughness.svg.append("g")
       .attr("class", "key")
       .attr("transform", "translate(25,16)");

     color_map_roughness.g.selectAll("rect")
       .data(color_map_roughness.color.range().map(function(d, i) {
         return {
           x0: i ? color_map_roughness.x(color_map_roughness.color.domain()[i - 1]) : color_map_roughness.x.range()[0],
           x1: i < color_map_roughness.color.domain().length ? color_map_roughness.x(color_map_roughness.color.domain()[i]) : color_map_roughness.x.range()[1],
           z: d
         };
       }))
       .enter().append("rect")
       .attr("height", 10) // epaisseur du rectangle
       .attr("x", function(d) { return d.x0; })
       .attr("width", function(d) { return d.x1 - d.x0; })
       .style("fill", function(d) { return d.z; });

     color_map_roughness.g.call(color_map_roughness.xAxis).append("text")
       .attr("class", "caption")
       .attr("y", 21) // position du texte sous le rectangle
       .text("Roughness length (m)");
}


////////////////////////////////////////////////////////////////////////
/////////////////////       plot markers    ////////////////////////////
////////////////////////////////////////////////////////////////////////
// function plot_markers() {
//     var marker_1= L.marker(
//         [46.9, 2.0],
//         {}
//     ).addTo(map);


//     var marker_2 = L.marker(
//         [46.8, 2.4],
//         {}
//     ).addTo(map);


//     var marker_3 = L.marker(
//         [46.9, 4.0],
//         {}
//     ).addTo(map);


//     var marker_4 = L.marker(
//         [45.9, 2.0],
//         {}
//     ).addTo(map);


//     var marker_5 = L.marker(
//         [45.9, 4.0],
//         {}
//     ).addTo(map);

//     var marker_6 = L.marker(
//         [46.7, 2.4],
//         {}
//     ).addTo(map);

//     var marker_7 = L.marker(
//         [46.6, 2.4],
//         {}
//     ).addTo(map);
// }

////////////////////////////////////////////////////////////////////////
//////////  Handle fetch/arayBuffer/georaster parsing response   ///////
////////////////////////////////////////////////////////////////////////
async function fetch_response(url) {
    const response = await fetch(url);
        if (!response.ok){throw new Error("Erreur http : ${response.status}");}
    const arrayBuffer = await response.arrayBuffer();
    const geoRaster =  parseGeoraster(arrayBuffer);
    return geoRaster
}

////////////////////////////////////////////////////////////////////////
////////////               Color maps                          /////////
////////////////////////////////////////////////////////////////////////
// for cropped data (2 bands in this case)
function pixel_to_color_roughness(pixelValues) {
    var pixelValue = pixelValues[0].toFixed(3); // one band contains the data
    var pixelValue_transparent_band = pixelValues[1].toFixed(3); // the other band contains the transparency (0/255)
    //console.log(pixelValue_transparent_band)
    if (pixelValue_transparent_band == 0) {
        color = null
    } 
    else {
    var isEqual = (element) => element == pixelValue;
    index = roughness_values.findIndex(isEqual)
    //console.log(index)
    color = roughness_colors[index];
    //console.log(color)
    }
    return color;
}

// // for non cropped data (only one band in this case)
// function pixel_to_color_roughness(pixelValues) {
//     var pixelValue = pixelValues[0].toFixed(3); // one band contains the data
//     //console.log(pixelValue_transparent_band)
//     var isEqual = (element) => element == pixelValue;
//     index = roughness_values.findIndex(isEqual)
//     //console.log(index)
//     color = roughness_colors[index];
//     //console.log(color)

//     return color;
// }


function pixel_to_color_windspeed(pixelValues) {
    var pixelValue = pixelValues[0];
    var pixelValue_transparent_band = pixelValues[1].toFixed(3); 
    //console.log(pixelValue)
    if (pixelValue_transparent_band == 0) {
        color = null
    } 
    else {
    color = windspeed_colormap.color(pixelValues[0])
    }
    return color;
}

function pixel_to_color_optimal_height(pixelValues) {
    var pixelValue = pixelValues[0];
    var pixelValue_transparent_band = pixelValues[1].toFixed(3); 
    //console.log(pixelValue)
    if (pixelValue_transparent_band == 0) {
        color = null
    } 
    else {
    color = optimal_height_colormap.color(pixelValues[0])
    }
    return color;
}

////////////////////////////////////////////////////////////////////////
////////////       From geotiff  to georaster layer        /////////////
////////////////////////////////////////////////////////////////////////
function GRtoGRL(georaster, pixel_to_color) {
    //const georaster = parseGeoraster(arrayBuffer);
    //console.log("georaster:", georaster);
    var layer = new GeoRasterLayer({
        georaster: georaster,
        opacity: 0.7,
        pixelValuesToColorFn: pixel_to_color,
        resolution: 256
    });
    return layer
}


////////////////////////////////////////////////////////////////////////
//////////////////   Display customized pop up   ////////////////////////
////////////////////////////////////////////////////////////////////////
function find_index (lat, long, vec_x, vec_y, xRes, yRes, height) {
    x_index = vec_x.findIndex((element) => Math.abs(element- long) < xRes)
    y_index = vec_y.findIndex((element) => Math.abs(element- lat) < yRes)
    return [height-y_index-1,x_index]  // be careful lat is y/is row, lon is x/is column
}



function display_popup() {
    var lat_lng_popup = L.popup();
    function latLngPop(e) {
        // pop up will appear only inside the raster and only on the uncropped zone (last condition)
        if ((e.latlng.lng>xmax) || (e.latlng.lng<xmin) || (e.latlng.lat>ymax) || (e.latlng.lat<ymin) ){
            console.log("out of scope")
        } else {
            index = find_index(e.latlng.lat,e.latlng.lng, vec_x, vec_y, xRes, yRes, height)
            //console.log(index)
            const windspeed = array_windspeed[index[0]][index[1]].toFixed(1);
            const roughness = array_roughness[index[0]][index[1]].toFixed(3); 
                if (windspeed == 0 & roughness ==0){
                    console.log("out of scope")
                } else {
                    lat_lng_popup
                        .setLatLng(e.latlng)
                        .setContent("Latitude: " + e.latlng.lat.toFixed(4) +
                                    "<br>Longitude: " + e.latlng.lng.toFixed(4)+
                                    "<br>Vr (10 m): " + windspeed + " m/s"+
                                    "<br>Roughness: " + roughness +
                                    "<br>Optimal height: " + array_optimal_height[index[0]][index[1]].toFixed(1)+" m")
                        .openOn(map);
                }
         }
    }
    map.on('click', latLngPop);
}
