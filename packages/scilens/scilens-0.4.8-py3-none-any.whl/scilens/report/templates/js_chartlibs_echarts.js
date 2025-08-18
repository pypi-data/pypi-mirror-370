((w_1, undef) => {
  //
  const obj = {
    add: function(elt, data) {
      const echarts_options = {
        //color:    null, // Custom color palette
        legend:  { left: 'right' },
        tooltip: { trigger: 'item', formatter: '{a}<br/>{b}<br/>{c}' },
        title:   { text: data.title },
        xAxis:   { name: data.xaxis },
        yAxis:   { name: data.yaxis },
        series:  [],
      }
      // series
      data.series.forEach(item => {
        echarts_options.series.push({
          type: 'line',
          name: item.name,
          data: item.data,
        })
      });
      // colors
      if (data.series[0].color) {
        echarts_options.color = data.series.map((e) => e.color)
      }
      // create
      echarts.init(elt).setOption(echarts_options);
    },
  };
  // global
  if(w_1.chartlibs === undef) w_1.chartlibs = {};
  w_1.chartlibs.echarts = obj;
  //
})(window);