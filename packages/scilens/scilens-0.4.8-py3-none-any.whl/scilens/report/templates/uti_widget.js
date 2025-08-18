((w_1, undef) => {
const CLASSES = "text-xs rounded-lg mx-1 my-1";
const CLASSES_ACTIVE = "text-xs rounded-lg mx-1 my-1 bg-slate-500 text-white";
const Buttons = {
  add: function(elt, specs) {
    const that = this;
    specs.forEach((spec) => {
      dom.but_p(elt,"",{"class":(spec.state===true)?CLASSES_ACTIVE:CLASSES},spec.label,that.click).fn = spec.fn;
    });
  },
  click: function(e) {
    const b = e.target;
    const r = b.fn();
    if (r === true || r=== false) { b.className = (r)?CLASSES_ACTIVE:CLASSES; } // toggle
  },
};
w_1.Buttons = Buttons;
})(window);





((w_1, undef) => {

function plotlycopy(e, new_e) {
  const  layout = JSON.parse(JSON.stringify(e.layout))
  layout.width = null; layout.height = null; // force to null to apply responsive
  // layout.margin = {l: 40, r: 40, t: 40, b: 40}; // remove margins
  Plotly.newPlot(
    new_e, 
    JSON.parse(JSON.stringify(e.data)), // data
    layout, // layout
    {responsive: true, displayModeBar: true},
  );
  // fixed bug with modebar position
  dom.q(new_e, ".modebar-container")[0].style.position = "fixed"; // fix position of modebar
}
const WFull = {
  add: function(elt) {
    elt.addEventListener("dblclick", function(){WFull.show(elt);}, true);
  },
  show: function(elt) {
    document.body.style.overflow = 'hidden';
    this.fe = dom.div_p(document.body,"position:fixed;top:0;left:0;width: 100%;height: 100vh;display:flex;z-index: 9998;");
    this.fb = dom.but_p(document.body,"position:fixed;top:0;left:0;z-index: 9999;padding:10px;", null, "Close", WFull.hide);
    plotlycopy(elt, this.fe);
  },
  hide: function() {
    document.body.style.overflow = 'auto';
    WFull.fe.remove();
    WFull.fb.remove();
  },
};
w_1.WFull = WFull;
})(window);

