((w_1, undefined) => {
  //
  const plotly = {
    add: function(elt, meta, items) {
      const series = []
      let yaxis2 = null;
      
      // 

      items.forEach(item => {
        const serie = {
          name: item.name,
          x:    item.x_data,
          y:    item.y_data,
          // yaxis : 'y1', // required if there are multiple y axes
          // mode: 'lines+markers',
          mode: 'lines',
          line:   { color: item.color, width: 3 },
          // marker: { color: item.color, size: 6 },
        }
        if (item.special) {
          switch (item.special) {
            case 'diff':
              yaxis2 = {title: 'Difference',overlaying: 'y',side: 'right', color: 'rgba(255, 0, 0, 1)'}
              serie.line.color = 'rgba(255, 0, 0, 0.5)';
              serie.yaxis = 'y2';
              serie.fill = 'tozeroy';
              serie.fillcolor = 'rgba(255, 0, 0, 0.2)';
              break;
          }
        }
        // item.special
        series.push(serie)
      });

      const layout = {
        title: { text: meta.title, font: { weight: 800 } },
        xaxis: { title: meta.xaxis },
        yaxis: { title: meta.yaxis },
        autosize: true,
        // showlegend: false,
        // legend: {
        //   x: 1,
        //   xanchor: 'right',
        //   y: 1
        // }
        // margin: {
        //   l: 10,
        //   r: 10,
        //   b: 10,
        //   t: 10,
        //   pad: 0,
        // },          
      };
      if (yaxis2) {layout.yaxis2 = yaxis2;}

      Plotly.newPlot(elt,series,layout);
      WFull.add(elt)
    },
    add_ys: function(elt, meta, x_data, y_items) {
      this.add(elt, meta, y_items.map((item) => {return {name: item.name, color: item.color, x_data: x_data, y_data: item.data} } ))
    },
    upd_y: function(elt, y_index, y_data) {
      Plotly.restyle(elt, { 'y': [y_data] }, [y_index]);
    },
    upd_y_all: function(elt, y_data_arr) {
      Plotly.restyle(elt, { 'y': y_data_arr });
    },
  };
  // global
  if(w_1.chartlibs === undefined) w_1.chartlibs = {};
  w_1.chartlibs.plotly = plotly;
  //

function resize22(obj, container, dir) { // ASSUMPTIONS : obj.size [int, int], "js-plotly-plot"
  // size
  const w = obj.size[0] + (dir * obj.size[0] * 0.1);
  const h = obj.size[0] + (dir * obj.size[0] * 0.1);
  obj.size = [w, h];
  // update widgets
  const update = { width: w, height: h };
  const nodes = dom.q(container, ".js-plotly-plot");
  nodes.forEach((node) => {
    node.style.width  = w + "px";
    node.style.height = h + "px";
    Plotly.relayout(node, update); // update plotly
  });
}
w_1.resize22 = resize22;
  
})(window);