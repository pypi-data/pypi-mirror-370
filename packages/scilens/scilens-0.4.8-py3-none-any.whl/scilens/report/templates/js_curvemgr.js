// dependances: utils_dom.js, chartlibs.js
//
// global_curves = {
//     test: [
//         {
//             curves: [
//                 {
//                     title: "Curve 1",
//                     short_title: "C1",
//                     series: [[1,2],[2,3],[3,4],[4,5],[5,6]],
//                 },
//                 {
//                     title: "Curve 2",
//                     short_title: "C2",
//                     series: [[1,3],[2,4],[3,5],[4,6],[5,7]],
//                 },
//             ],
//             charts: [
//                 {
//                     title: "Chart 1",
//                     xaxis: "X",
//                     yaxis: "Y",
//                     curves: [0,1],
//                 },
//                 {
//                     title: "Chart 2",
//                     xaxis: "X",
//                     yaxis: "Y",
//                     curves: [0],
//                 },
//             ],
//         },
//     ],
//     reference: [
//         {
//             curves: [
//                 ...
//
//

((w_1, undef) => {

// 
const ERROR_LABEL = "*"
// button gen

const BUTTON_CLASSES = "text-xs rounded-lg mx-1 my-1";
const BUTTON_CLASSES_ACTIVE = "text-xs rounded-lg mx-1 my-1 bg-slate-500 text-white";

const BUTTON_CLASSES_ERR = "text-xs rounded-lg mx-1 my-1 bg-red-400";
const BUTTON_CLASSES_ERR_ACTIVE = "text-xs rounded-lg mx-1 my-1 bg-red-600 text-white";

// button selcect

const SEL_BUTTON_CLASSES = "text-xs rounded-lg mx-1 my-1";
const SEL_BUTTON_CLASSES_ACTIVE = "text-xs rounded-lg mx-1 my-1 bg-slate-500 text-white";


const CONFIG = {
  display_on_load: false,
  init_width: 600,
  init_height: 400,
  compare_vs_values: true, 
  compare_vs_difference: true,
}


const curve_add_chart = function(element_parent, data, zoom) {
  zoom = zoom || 1;
  //
  const width  = CONFIG.init_width * zoom;
  const height = CONFIG.init_height * zoom;
  //
  // create div
  const div = document.createElement('div');
  div.style.cssText = "width: "+width+"; height: "+height+"px;";
  div.className = "m-1 shadow-lg";
  element_parent.appendChild(div);
  // chart
  chartlibs.plotly.add(
    div,
    { title: data.title, xaxis: data.xaxis , yaxis: data.yaxis },
    data.series.map((item) => {return {
      name:    item.name,
      color:   item.color,
      x_data:  item.data.map((e) => e[0]),
      y_data:  item.data.map((e) => e[1]),
      special: item.special,
    }}),
  )
};


const standalone = function() {
  const curve = global_curves.test[0].curves[0];
  curve_add_chart(document.body, {
    title: "title",
    xaxis: "xaxis",
    yaxis: "yaxis",
    series : [
      {
        name:  curve.short_title,
        data:  curve.series,
        color: null,
      },
    ]
  });
};

const INIT_DISPLAY = false ;


const CurvesChart = function(blockIndex, chartIndex) {
  this.curve_block = new CurvesBlock(blockIndex);
  this.blockIndex = blockIndex;
  this.chartIndex = chartIndex;
  this.chart = global_curves.test[blockIndex].charts[chartIndex];
  this.curves = {
    test:      global_curves.test[blockIndex],
    reference: global_curves.reference[blockIndex],
  }
}
CurvesChart.prototype = {
  getDomToogleInit: function() {
    const blockIndex = this.blockIndex;
    const chartIndex = this.chartIndex;
    const has_error = this.chart.comparison && this.chart.comparison.curves_nb_with_error;
    const children = [{
      tag:"button", 
      attrs: {id: `chart_toogle_${blockIndex}_${chartIndex}`, type:"button", class: BUTTON_CLASSES },
      html: this.chart.title + (has_error ? " " + ERROR_LABEL : ""),
      click: function() { CurvesChart.toogle(blockIndex,chartIndex); },
    }];
    // if (this.chart.comparison) {
    //   if (this.chart.comparison.curves_nb_with_error) {
    //     // children.push({tag:"span", attrs: { class:"text-xs ERROR"}, html: `${this.chart.comparison.curves_nb_with_error} curves with errors`});
    //     // children.push({tag:"span", attrs: { class:"text-xs ERROR"}, html: "*errors"});
    //   }
    // }
    return {tag:"span",  attrs:{class: has_error ? "error_container" : "" }, children: children};
  },
  // state : true = visible, false = hidden
  toogle: function(force_state) {
    const blockIndex = this.blockIndex;
    const chartIndex = this.chartIndex;
    const b =  dom.get(`chart_toogle_${blockIndex}_${chartIndex}`);
    const current_isHidden = (b.className == BUTTON_CLASSES);
    const target_state = (force_state != undef) ? force_state : current_isHidden;
    // update button
    b.className = (target_state)?BUTTON_CLASSES_ACTIVE:BUTTON_CLASSES;
    // update curves
    const id = `chart_container_${blockIndex}_${chartIndex}`;
    // remove if hidden
    if (!target_state && !current_isHidden) { dom.get(id).remove(); }
    if (target_state && current_isHidden) {
      const chart = this.chart;
      const eContainer = dom.get(`curves_${parseInt(blockIndex)}`);
      let comparison = ""
      if (this.chart.comparison && this.chart.comparison.curves_nb_with_error) {
        comparison = `${this.chart.comparison.curves_nb_with_error} curve(s) with errors`;
        for (let i = 0; i < this.chart.curves.length; i++) {
          const curve = this.curves["test"].curves[this.chart.curves[i]]
          comparison += ` - ${curve.title}: ${curve.comparison_error}`
        }
      }
      const out = dom.tree_o(
        eContainer,
        {tag:"div", attrs: {id:id}, children: [
          {tag:"div", style:"margin:10px 0px;", children: [
            {tag:"strong", html: chart.title},
            {tag:"button", attrs: { type:"button", class:BUTTON_CLASSES}, html: "Remove",
              click: function() { CurvesChart.toogle(blockIndex,chartIndex); },
            },
            {tag:"span", attrs: {class:"ERROR"}, html: comparison},
          ]},
          {out:"row_1", tag:"div", style:"display: flex;flex-wrap: wrap;"},
          {out:"row_2", tag:"div", style:"display: flex;flex-wrap: wrap;"},
        ]},
      );
      // display test and reference
      const labels = { test: "Test", reference: "Reference" }
      for (type in labels) {
        
        const series = []

        chart.curves.forEach(curve_index => {
          const curve = this.curves[type].curves[curve_index]
          series.push({
            name:  curve.short_title,
            data:  curve.series,
            color: null,
          })
        });        
        const data = {
          title: chart.title + " [" + labels[type] + "]",
          xaxis: chart.xaxis,
          yaxis: chart.yaxis,
          series : series,
        }
        curve_add_chart(out.row_1, data, this.curve_block.zoom);

      }
      // display each curve test vs reference
      if (CONFIG.compare_vs_values || CONFIG.compare_vs_difference) {
        for (index_curve in chart.curves) {
          real_index = chart.curves[index_curve]

          const series = [];
          if (CONFIG.compare_vs_values) {
            series.push({
              name:  "Test",
              data:  this.curves["test"].curves[real_index].series,
              color: '#1982c4',
            });
            series.push({
              name:  "Reference",
              data:  this.curves["reference"].curves[real_index].series,
              color: '#6a4c93',
            });
          }
          if (CONFIG.compare_vs_difference) {
            series.push({
              name:  "Difference",
              data:  this.curves["test"].curves[real_index].series.map((e, i) => {
                return [e[0], e[1] - this.curves["reference"].curves[real_index].series[i][1]]
              }),
              color: '#ffcc00',
              special: 'diff',
            });
          }

          // {
          //   name:  "Test",
          //   data:  this.curves["test"].curves[real_index].series,
          //   color: '#1982c4',
          // },
          // {
          //   name:  "Reference",
          //   data:  this.curves["reference"].curves[real_index].series,
          //   color: '#6a4c93',
          // },
          // {
          //   name:  "Difference",
          //   data:  this.curves["test"].curves[real_index].series.map((e, i) => {
          //     return [e[0], e[1] - this.curves["reference"].curves[real_index].series[i][1]]
          //   }),
          //   color: '#ffcc00',
          //   special: 'diff',
          // },          
          // 
          const data = {
            title: this.curves["test"].curves[real_index].title + " [Test vs Reference]",
            xaxis: chart.xaxis,
            yaxis: chart.yaxis,
            series : series,
          }
          curve_add_chart((chart.curves.length > 1) ? out.row_2 : out.row_1, data, this.curve_block.zoom);
        }
      }
      
    }
  },
}
CurvesChart.toogle = function(blockIndex, chartIndex, force_state) {
  (new CurvesChart(blockIndex, chartIndex)).toogle(force_state);
};


const CurvesBlock = function(blockIndex) {
  this.blockIndex = blockIndex;
  this.charts = global_curves.test[blockIndex].charts; // ASSUMPTION test and reference have same charts
  this.eContainer = dom.get(`curves_${parseInt(blockIndex)}`); // ASSUMPTION always exists
  this.zoom = this.eContainer.dataset.zoom || 1;
}
CurvesBlock.prototype = {
  toogleCharts: function(force_state) {
    const blockIndex = this.blockIndex
    this.charts.forEach((chart, chartIndex) => {
      CurvesChart.toogle(blockIndex, chartIndex, force_state);
    });    
  },
  resize: function(direction) {
    const mult = (1 + direction * 0.1);
    this.eContainer.dataset.zoom = this.zoom * mult;
    const curves = dom.q(this.eContainer, ".js-plotly-plot");
    curves.forEach((e) => {
      const w = parseFloat(e.style.width) * mult;
      const h = parseFloat(e.style.height) * mult;
      e.style.width = w + "px";
      e.style.height = h + "px";
      Plotly.relayout(e, { width: w, height: h } );
    });
  },
  init: function() {
    const blockIndex = this.blockIndex
    const charts     = this.charts; 
    // buttons (global and per chart)
    dom.tree(
      this.eContainer,
      {tag:"div", attrs: {id: `curvemgr_block_${blockIndex}`} , children:[
        {tag:"div", children: [
          {tag:"strong", html: "All"},
          {tag:"button", attrs: { type:"button", class:BUTTON_CLASSES}, html: "Show",   click: function() { CurvesBlock.toogle(blockIndex, true); }},
          {tag:"button", attrs: { type:"button", class:BUTTON_CLASSES}, html: "Remove", click: function() { CurvesBlock.toogle(blockIndex, false); }},
          {tag:"strong", html: "Size"},
          {tag:"button", attrs: { type:"button", class:BUTTON_CLASSES}, html: "Increase", click: function() { CurvesBlock.resize(blockIndex, 1); }},
          {tag:"button", attrs: { type:"button", class:BUTTON_CLASSES}, html: "Decrease", click: function() { CurvesBlock.resize(blockIndex, -1); }},
        ]},
        {tag:"div", children: charts.map((chart, chartIndex) => {
          const cc = new CurvesChart(blockIndex, chartIndex);
          return cc.getDomToogleInit();
        })}
      ]}
    );
    // load
    if (CONFIG.display_on_load) {
      charts.forEach((chart, chartIndex) => {
        CurvesChart.toogle(blockIndex, chartIndex);
      });
    }
  },
};
// 
// Static Methods
CurvesBlock.toogle = function(blockIndex, force_state) {
  (new CurvesBlock(blockIndex)).toogleCharts(force_state);
};
CurvesBlock.resize = function(blockIndex, direction) {
  (new CurvesBlock(blockIndex)).resize(direction);
};


// ***************************************************************************
// ***************************************************************************
// CURVE MANAGER
// ***************************************************************************
// ***************************************************************************

w_1.curvemgr = {
  init_group_curves: function() {
    for (const i in global_curves.test) {
      if (global_curves.test[i]) {
        const cb = new CurvesBlock(i);
        cb.init();
      }
    }
  },
  init(config) {
    for (const k in CONFIG) {
      if (config[k] != undef) {CONFIG[k] = config[k];}
    }
    this.init_group_curves();
  }
};

})(window);
