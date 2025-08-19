((w_1, undef) => {
//
// FramesData
//
const FramesData = dataclass(
  ['length', 'data_vector', 'name', 'unit', 'steps_starts'],
  {},
  (self) => {
    if (self.data_vector && self.data_vector.length != self.length) {
      throw new Error("FramesData: data_vector length does not match length");
    }
    if (self.data_vector && self.steps_starts) {
      const steps = [];
      const start = self.data_vector[0];
      const end = self.data_vector[self.length-1];
      self.steps_starts.forEach((vstart,i) => {
        if (vstart >= end) return; // start outside right data_vector
        const sstart = (vstart < start) ? start : vstart; // start outside left data_vector
        const vend = (i+1 < self.steps_starts.length) ? self.steps_starts[i+1] : end;
        if (vend < start) return; // end outside left data_vector
        const send = (vend > end) ? end : vend; // end outside right data_vector
        steps.push({
            index: i,
            value: vstart,
            start: sstart,
            end: send,
            color: palette.get(i),
            disp_per_margin_left: (100*(sstart-start)/(end-start))+"%", // rendering
            disp_per_width: (100*(send-sstart)/(end-start))+"%", // rendering
        })
      });
      self.steps = steps;
      self.steps[self.steps.length-1].last = true
    }
  },
  {
    label(idx) {
      const f = `(Frames: ${1+parseInt(idx)}/${this.length})`;
      const l = (this.data_vector)?`${this.data_vector[idx]} ${this.unit || ""}`:"";
      return `${this.name || ""}  ${l} ${f}`;
    },
    step(idx) {
      const v = this.data_vector[idx];
      return this.steps.find((s) => s.value >= v || (s.last && v<= s.end));
    },
  }
);
//
// Config
//
const PREFIX = "frameseries_"; // section prefix
const CFG = {
  "WIDTH": 300, // default width
  "HEIGHT": 300, // default height
}
//
//
/**
 * @param {FramesData} frames_data
 * @returns {string}
 */
class Frameseries {
  constructor(index, arr_mat, frames_data, invert = false) {
    // size
    this.size = [CFG.WIDTH, CFG.HEIGHT]; // default size
    //
    this.arr_mat = arr_mat;
    this.elt = dom.get(PREFIX+(1+index));
    // frames
    this.frames_data = frames_data;
    //
    this.finvert = true; // invert frames
    // Steps
    this.steps = null;
    // init
    this.init();
  }
  init() {
    // 
    const that = this;
    //
    let dom_steps = null;
    if (this.frames_data.steps) {
      const divs = [];
      this.frames_data.steps.forEach((s,i) => {
        const m = (i==0) ? "margin-left:"+s.disp_per_margin_left+";" : "";
        divs.push({tag:"div", style:"display: inline-block;"+m+"width: "+s.disp_per_width+"; height: 20px; background-color: "+s.color+";"});
      });
      dom_steps = {tag:"div", children: [
          {tag:"div", style:"height:15px;background-color:#eee;", children: divs},
      ]};
    }
    //
    dom.tree(
        this.elt,
        {out:"root", tag:"div", children: [
            {out: "tools", tag:"div"},
            dom_steps,
            {out:"sli", tag:"input", style:"width: 100%;", attrs: {"type":"range","value":0,"min":0,"max":this.frames_data.length-1}},
            {out:"lab", tag:"div", style:"text-align: center;"},
            {out:"tbuttons", tag:"div"},
            {out:"graphs", tag:"div", style:"display: flex; flex-wrap: wrap;"},
        ]},
        this
    );
    this.sli.addEventListener('input', function(){that.frame_change();}, true);
    // tools
    Buttons.add(this.tools, [
      {label: "Increase", fn: function() { resize22(that, that.elt, 1); }},
      {label: "Decrease", fn: function() { resize22(that, that.elt, -1); }},
    ]);
    // frame change initialization (only label)
    this.frame_change();
    // add graphs
    this.arr_mat.forEach((m, i) => { this.var_add(i); });
    // toogle vars buttons
    Buttons.add(that.tbuttons, this.arr_mat.map((mat, i) =>  ({label: mat.name, state:true, fn: function() { return that.var_toogle(i); }})));
  }
  frame_change() {
    const that = this;
    const idx = this.sli.value;
    // steps
    let steps_label = "" ;
    if (this.frames_data.steps) {
      const step = this.frames_data.step(idx);
      steps_label = (step) ? ` <span style="padding:3px 5px;background-color:${step.color};">Step: ${step.index+1}/${this.frames_data.steps.length}</span>` : "";
    }
    // label
    this.lab.innerHTML = this.frames_data.label(idx) + steps_label ;
    // curves
    this.arr_mat.forEach((m, i) => {
      if (that["var_"+i]) {
        if (this.finvert) {
          chartlibs.plotly.upd_y_all(that["var_"+i], [m.data.map((x) => x[idx]), m.ref.map((x) => x[idx])]);
        } else {
          chartlibs.plotly.upd_y_all(that["var_"+i], [m.data[idx], m.ref[idx]]);
        }
      }
    });
  }
  var_toogle(var_i) {
    if (this["var_"+var_i]) { this.var_rmv(var_i); return false; } else { this.var_add(var_i); return true; }
  }
  var_add(var_i) {
    dom.tree(
        this.graphs,
        {out:"var_"+var_i, tag:"div", style:"width:"+this.size[0]+"px;height:"+this.size[1]+"px;", attrs: { class: "m-1 shadow-lg" }},
        this
    );
    this.add_widget(var_i);
  }
  var_rmv(var_i) {
    this["var_"+var_i].remove();
    delete this["var_"+var_i];
  }
  add_widget(var_i) {
    const idx = this.sli.value;
    const mat = this.arr_mat[var_i];
    console.log("mat.y");
    console.log(mat.y);
    if (this.finvert) {
      chartlibs.plotly.add_ys(
          this["var_"+var_i],
          { title: mat.name, xaxis: mat.y_name , yaxis: "Values" },
          (mat.y) ? mat.y : mat.data.map((x,i) => parseInt(i)+1 ),
          [
              { name: "Test"      , data: mat.data.map((x) => x[idx]) },
              { name: "Reference" , data: mat.ref.map((x) => x[idx]) },
          ]
      );
    } else {
      chartlibs.plotly.add_ys(
          this["var_"+var_i],
          { title: mat.name, xaxis: "Values" , yaxis: mat.y_name },
          (mat.x) ? mat.x : mat.data[0].map((x,i) => parseInt(i)+1 ),
          [
              { name: "Test"      , data: mat.data[idx] },
              { name: "Reference" , data: mat.ref[idx] },
          ]
      );
    }
  }
}
Frameseries.config = function(cfg) {for (k in cfg) {CFG[k] = cfg[k];}};
w_1.FramesData = FramesData;
w_1.Frameseries = Frameseries;
})(window);