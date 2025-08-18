((w_1, undef) => {
const Framesseries = function (elt, data, data_ref) {
    const that = this;
    // data
    this.data = data
    this.data_ref = data_ref
    // frames
    const nb = data.variables.length;
    this.size = 3000/nb;
    this.frame_len = data.frames_variable.data.length;
    this.frame_min = data.frames_variable.data[0];
    this.frame_max = data.frames_variable.data[this.frame_len-1];
    //
    // const vars_templ = data.variables.map((x,i) => { return {out:"variable_"+i, tag:"div", style:"width: 600px; height: 400px;"} ; } );

    const vars_templ = data.variables.map((x,i) => { return {out:"variable_"+i, tag:"div", style:"width:"+this.size+"px;height:"+this.size+"px;"} ; } );
    //
    // frames_steps_variable
    this.steps = null;
    let dom_steps = null;
    if (data.frames_steps_variable) {
        // steps
        const steps = []
        data.frames_steps_variable.data.forEach((e,i) => {
            // console.log(e)
            steps.push({
                start: e,
                color: palette.get(i),
            })
        });
        this.steps = steps;
        // dom
        const divs = []
        steps.forEach((s,i) => {
            if (s.start >= this.frame_max) return;
            const start = (s.start < this.frame_min) ? this.frame_min : s.start;
            let stop = (i+1 < steps.length) ? steps[i+1].start : this.frame_max;
            if (stop < this.frame_min) return;
            if (stop > this.frame_max) stop = this.frame_max;
            
            const m = ( ! divs.length && start > this.frame_min) ? "margin-left:"+(100*(start-this.frame_min)/(this.frame_max-this.frame_min))+"%;" : "";
            divs.push({tag:"div", style:"display: inline-block;"+m+"width: "+(100*(stop-start)/(this.frame_max-this.frame_min))+"%; height: 15px; background-color: "+s.color+";"});
        });

        dom_steps = {tag:"div", children: [
            {out:"step_label", tag:"div", style:"text-align: center;"},
            {tag:"div", style:"height:15px;background-color:#eee;", children: divs},
        ]}
    }
    //
    dom.tree(
        null,
        {out:"root", tag:"div", children: [
            {tag:"div", children: [
                {out:"plus",  tag:"button", html: '+ Increase' },
                {out:"minus", tag:"button", html: '- Decrease' },
            ]},
            dom_steps,
            {out:"sli", tag:"input", style:"width: 100%;", attrs: {"type":"range","value":1,"min":1,"max":this.frame_len}},
            {out:"lab", tag:"div", style:"text-align: center;"},
            {tag:"div", style:"display: flex; flex-wrap: wrap;", children: vars_templ},
        ]},
        this
    );
    this.sli.addEventListener('input', function(){that.update();}, true);
    this.plus.addEventListener('click', function(){that.resize(1);}, true);
    this.minus.addEventListener('click', function(){that.resize(-1);}, true);
    
    elt.appendChild(this.root);
    
    // create curves
    data.variables.forEach((variable,i) => {
        // check names ??
        // variable.name == data_ref.variables[i].name
        chartlibs.plotly.add_ys(
            that["variable_"+i],
            { title: variable.name, xaxis: "Indexes" , yaxis: "Values " + variable.unit },
            variable.data[0].map((x,i) => parseInt(i)+1 ),
            [
                { name: "Test"      , data: variable.data[0] },
                { name: "Reference" , data: data_ref.variables[i].data[0] },
            ]
        )
    });
    this.update();
};
Framesseries.prototype = {
    resize: function (direction) {
        const that = this;
        // myDiv.style.height
        this.size = this.size + (direction * this.size * 0.1);
        var update = {
            width: this.size,
            height: this.size,
          };
        this.data.variables.forEach((variable,i) => {
            that["variable_"+i].style.width = that.size + "px";
            that["variable_"+i].style.height = that.size + "px";
            Plotly.relayout(that["variable_"+i], update);
        });
          
    },
    update: function () {
        const labels = []
        const that = this;
        // frames
        const index = this.sli.value;
        const frame_val = this.data.frames_variable.data[index-1];
        const label = this.data.frames_variable.name + (this.data.frames_variable.unit ? " (" + this.data.frames_variable.unit + ")" : "");
        labels.push({label: label, val: frame_val, max: this.frame_max})
        labels.push({label: "Frame", val: index, max: this.frame_len})
        // curves
        this.data.variables.forEach((variable,i) => {
            chartlibs.plotly.upd_y_all(
                that["variable_"+i],
                [variable.data[index-1], that.data_ref.variables[i].data[index-1]],
            )
        });
        // steps
        if (this.steps) {
            const steps = this.steps
            let step = 0
            let color = ""
            let val2 = null 
            for (let i=0; i<steps.length; i++) {
                if (frame_val >= steps[i].start) {
                    step = i+1
                    color = steps[i].color
                    val2 = steps[i].start
                }
            }
            labels.push({label: "Step", val: step, max: steps.length, color: color, val2: val2})
        }   
        // labels
        // console.log(labels)
        this.lab.innerHTML =  labels.map(x => '<span style="padding:3px 5px;background-color:'+x.color+';"><b> ' + x.label + "</b> " + x.val + "/" + x.max + ( x.val2 ? " (" + x.val2 + ")" : "") +"</span>").join(" - ");


    },
};
Framesseries.create = function(parent, options, options_2) {
    new Framesseries(parent, options, options_2)
}
w_1.Framesseries = Framesseries;
})(window);