((w_1, undef) => {
const Anim = function (elt, options, options_2) {
    const that = this;
    // options
    this.images = options.images;
    this.len = this.images.length;
    this.prefix = options.prefix || "";
    this.suffix = options.suffix || "";
    //
    const width = options.width || 250;
    console.log(options)
    console.log(width)
    const height = 250;
    // index
    this.index = 1
    // elements
    const img_size = `width:${width}px;`
    // console.log(img_size)
    if (options_2) {
        dom.tree(
            null,
            {out:"root", tag:"div", style:`width:${width*3}px;`, children: [
                {tag:"div", style:"display:table;width:100%;", children: [
                {tag:"div", style:"display:table-cell;width:33.33%;", html:"Test"},
                {tag:"div", style:"display:table-cell;width:33.33%;", html:"Reference"},
                {tag:"div", style:"display:table-cell;width:33.33%;", html:"Test vs Reference"},
                ]},
                {tag:"div", style:"display:table;", children: [
                {tag:"div", style:"display:table-cell;width:33.33%;", children: [
                    {out:"img", tag:"img", style:img_size},
                ]},
                {tag:"div", style:"display:table-cell;width:33.33%;", children: [
                    {out:"img_2", tag:"img", style:img_size},
                ]},
                {tag:"div", style:"display:table-cell;width:33.33%;", children: [
                    {out:"img_o_1", tag:"img", style:"position:absolute;opacity:0.5;"+img_size},
                    {out:"img_o_2", tag:"img", style:"position:absolute;opacity:0.5;"+img_size},
                ]},
                ]},
                {out:"sli", tag:"input", style:"width: 100%;", attrs: {"type":"range","value":this.index,"min":this.index,"max":this.len}},
                {out:"lab", tag:"div", style:"text-align: center;"},
            ]},
            this
        )
    } else {
        dom.tree(
            null,
            {out:"root", tag:"div", style:img_size, children: [
                {out:"img", tag:"img", style:img_size},
                {out:"sli", tag:"input", style:"width: 100%;", attrs: {"type":"range","value":this.index,"min":this.index,"max":this.len}},
                {out:"lab", tag:"div", style:"text-align: center;"},
            ]},
            this
        )
    }
    this.sli.addEventListener('input', function(){that.update();}, true);
    this.update();
    elt.appendChild(this.root);
};
Anim.prototype = {
update: function () {
    const index = this.sli.value;
    this.lab.innerHTML = String(index) + "/" + this.len;
    // 1
    const attrs = ["img", "img_2", "img_o_1", "img_o_2"];
    for (const i in attrs) {
    const e = this[attrs[i]]
    if (e) { e.src = this.prefix + this.images[index-1] + this.suffix; }
    }
},
};
Anim.create = function(parent, options, options_2) {
    new Anim(parent, options, options_2)
}
w_1.Anim = Anim;
})(window);