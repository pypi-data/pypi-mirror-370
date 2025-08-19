((w_1, undef) => {
//
// Config
//
const PREFIX = "spectrograms_"; // section prefix
const COLORSCALE = "Viridis"; // plotly
const COLORSCALE_DIFF = "RdBu"; // plotly
const CFG = {
  "WIDTH": 300, // default width
  "HEIGHT": 300, // default height
  "DISPLAY_TESTREF": true, // display test reference
  "DISPLAY_DIFF": true, // display diff
  "IS_3D": false, // use 3D surface plot
}

//
class Spectrograms {
  constructor(index, arr_mat) {
    // data
    this.disp_values = CFG.DISPLAY_TESTREF;
    this.disp_diff = CFG.DISPLAY_DIFF;
    this.is_3D = CFG.IS_3D; // 3D or 2D
    this.size = [CFG.WIDTH, CFG.HEIGHT]; // default size
    //
    this.arr_mat = arr_mat;
    this.elt = dom.get(PREFIX+(1+index));
    // init
    this.init();
  }
  init() {
    // resize
    const that = this;
    const o = {};
    dom.tree(
      this.elt,
      {tag:"div", children: [
        {out: "tools", tag:"div", attrs:{class:"py-2"}},
        {out: "vars", tag:"div", attrs:{class:"py-2"}},  
      ]},
      o
    );
    Buttons.add(o.tools, [
      {label: "Increase", fn: function() { resize22(that, that.elt, 1); }},
      {label: "Decrease", fn: function() { resize22(that, that.elt, -1); }},
      {label: "Values", fn: function() { that.disp_values = !that.disp_values; that.rerender(); return that.disp_values; }, state: this.disp_values },
      {label: "Diffs", fn: function() { that.disp_diff = !that.disp_diff; that.rerender(); return that.disp_diff; }, state: this.disp_diff },
      {label: "3D", fn: function() { that.is_3D = !that.is_3D; that.rerender(); return that.is_3D; }, state: this.is_3D },
    ]);
    // Show all
    this.arr_mat.forEach((mat, i) => { this.var_add(i); });
    // toogle buttons
    Buttons.add(o.vars, this.arr_mat.map((mat, i) =>  ({label: mat.name, state:true, fn: function() { return that.var_toogle(i); }})));
  }
  var_get_id(var_i) {
    return this.elt.id+"_"+var_i;
  }
  var_toogle(var_i) {
    if (dom.get(this.var_get_id(var_i))) { this.var_rmv(var_i); return false; }
    else { this.var_add(var_i); return true; }
  }
  var_add(idx) {
    const mat = this.arr_mat[idx];
    const loading = dom.div_p(this.elt, null, null, "Creating ... "+mat.name);
    this.elt.offsetHeight; // force reflow
    //
    const style = "width:"+this.size[0]+"px;height:"+this.size[1]+"px;";
    const attrs = { class: "m-1 shadow-lg" };
    //
    const templs = [];
    if (this.disp_values) templs.push({out:"var", tag:"div", attrs: attrs, style:style});
    if (mat.ref) {
      if (this.disp_values) templs.push({out:"ref", tag:"div", attrs: attrs, style:style});
      if (this.disp_diff) templs.push({out:"dif", tag:"div", attrs: attrs, style:style});
    }
    const e = {};
    dom.tree(
      this.elt,
      {tag:"div", attrs: {id: this.var_get_id(idx)}, children: [
          {tag:"div", style:"display: flex; flex-wrap: wrap;", children: templs},
      ]},
      e
    );

    if (this.disp_values) this.add_widget(e["var"], mat, mat.data);
    if (mat.ref) {
      if (this.disp_values) this.add_widget(e["ref"], mat, mat.ref, " - Ref.");
      if (this.disp_diff) this.add_widget(e["dif"], mat, mat.ref_diff_abs_data(), " - Diff.", COLORSCALE_DIFF);
      // copy22(e["dif"], e["dif2"]);
    }
    loading.remove();
  }
  var_rmv(idx) {
    dom.get(this.var_get_id(idx)).remove();
  }
  rerender() {
    this.arr_mat.forEach((m, i) => { 
      if (dom.get(this.var_get_id(i))) { 
        this.var_rmv(i);
        this.var_add(i);
      }
    });    
  }
  add_widget(elt, mat, matdata, suffix="", colorscale=COLORSCALE) {
    const data = [{
        z: matdata,
        type: this.is_3D ? 'surface' : 'heatmap',
        colorscale: colorscale,
        // contours: { z: { show:true, usecolormap: true, highlightcolor:"#42f462", project:{z: true} } },
    }];
    const layout = {
        title: mat.name + suffix,
        xaxis: { title: mat.x_name || 'X' },
        yaxis: { title: mat.y_name || 'Y' },
        scene: {
            xaxis: { title: mat.x_name || 'X' },
            yaxis: { title: mat.y_name || 'Y' },
            zaxis: { title: mat.z_name || 'Z' },
        },
    };

    Plotly.newPlot(elt, data, layout);
    WFull.add(elt)
  }

}
Spectrograms.config = function(cfg) {for (k in cfg) {CFG[k] = cfg[k];}};
w_1.Spectrograms = Spectrograms;
})(window);