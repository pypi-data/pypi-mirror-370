((w_1, undef) => {

  // ***************************************************************************
  // ***************************************************************************
  // parameters
  // ***************************************************************************
  // ***************************************************************************

  const parameters=[
    {
      id: 'page_mode',
      label: 'Display Mode', 
      is_user: {{ 'true' if meta.config.parameter_page_mode.is_user_preference else 'false' }},
      values: ['onepage', 'tabs'],
      action: "actions.render_page()",
      default: '{{ meta.config.parameter_page_mode.default_value}}',
    },{
      id: 'open_file_in',
      label: 'Open File in',
      is_user: {{ 'true' if meta.config.parameter_open_file_in.is_user_preference else 'false' }},
      values: ['browser', 'vscode'],
      default: '{{ meta.config.parameter_open_file_in.default_value}}',
    },{
      id: 'js_lib',
      label: 'Chart Lib',
      is_user: false,
      values: ['plotly', 'echarts'],
      default: 'plotly',
      // action: load_curves(),
    },
  ];

  function build_parameters() {
    const div = dom.get("parameters");

    const out = dom.tree_o(
      null,
      {out:"root", tag:"form", attrs: {name:"parameters"}, children: parameters.map((p) => {
        return (p.is_user) ? {tag:"fieldset", style:"display: inline-block;", children: [
          {tag:"legend", html: p.label},
          {tag:"div", children: p.values.map((value) => {
            return {tag:"div", children: [
              {tag:"input", attrs: {type:"radio", name: p.id, id: p.id+"_"+value, value: value, onclick: p.action}},
              {tag:"label", attrs: {for: p.id+"_"+value}, html:value},
            ]}
          })}
        ]} : null
      })}
    );
    
    dom.get("section_parameters_form").appendChild(out.root);
    // default values
    parameters.forEach((p) => { if (p.is_user) { dom.get(p.id+"_"+p.default).checked=true; }});    
  };

  function get_parameter(id) {
    for (const p of parameters) {
      if (p.id == id) { return (p.is_user) ? dom.getRadio("parameters", id) : p.default; }
    }
  };

  // ***************************************************************************
  // ***************************************************************************
  // action
  // ***************************************************************************
  // ***************************************************************************
  function openNewTab(text) {
    const blob = new Blob([text], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  }
  function open_file(route) {
    const arr = window.location.pathname.split('/');
    arr.pop();
    const root = arr.join('/');
    const url = root + '/' +  route;
    const open_file_in = get_parameter("open_file_in");
    switch (open_file_in) {
      case "browser": window.open(url, '_blank'); break;
      case "vscode":  window.open('vscode://file' + url, '_blank'); break;
    }
  };

  // const BUTTON_CLASSES = "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded";
  const BUTTON_CLASSES = "text-xs rounded-lg";

  const action = {
    init: function() {
      const elts = document.body.getElementsByTagName("action");
      for (const eAction of elts) {
        dom.tree(
          eAction,
          {
            out:"child",
            tag:"button",
            attrs: {type:"button", class:BUTTON_CLASSES},
            html: eAction.dataset.label,
            click: function() { action.action(eAction); },
          },
          eAction
        );
        if (eAction.dataset.command=="toogle") this.toogleUpdate(eAction);
      }
    },
    action: function(eAction) {
      const command = eAction.dataset.command;
      const args = eAction.dataset.args;
      if (command === "toogle") {
        const inf = this.toogleGetInfo(eAction);
        dom.toogle(inf.eTarget);
        this.toogleUpdate(eAction);
      } else if (command === "open_file") {
        open_file(args);
      }
    },
    toogleGetInfo: function(eAction) {
      const x = dom.get(eAction.dataset.args);
      return { eTarget: x, isHidden: (x.style.display === "none")};
    },
    toogleUpdate: function(eAction) {
      const inf = this.toogleGetInfo(eAction);
      eAction.child.innerHTML = inf.isHidden ? "Show" : "Hide";
    },
  };
  // ***************************************************************************

  const NB_FILES = {{ data.files|length }};
  const NB_SECTIONS = NB_FILES+1;

  w_1.actions = {
    toogle: function(id) {
      const x = dom.get(id);
      x.style.display = (x.style.display === "none") ? "" : "none";
    },
    open_file: function(route) {
      const arr = window.location.pathname.split('/');
      arr.pop();arr.pop();
      const root = arr.join('/');
      const url = root + '/' +  route;
      const open_file_in = get_parameter("open_file_in");
      switch (open_file_in) {
        case "browser": window.open(url, '_blank'); break;
        case "vscode":  window.open('vscode://file' + url, '_blank'); break;
      }
    },
    see_details: function(index) {
      const page_mode = get_parameter("page_mode");
      switch (page_mode) {
        case "onepage":
          location.hash = "#section_" + index;
          break;
        case "tabs":
          // tabs active
          var children =  dom.get("tabs").children;
          for (i = 0; i < children.length; i++) {
            children[i].className = children[i].className.replace(" active", "");
            if (children[i].dataset.tabIndex == index) { children[i].className += " active"; }
          }
          // display section
          for (i = 0; i < NB_SECTIONS; i++) { 
            const section = dom.get("section_"+i);
            if (section) section.style.display = "none"; 
          }
          dom.get("section_"+index).style.display = "";
          break;
      }
    },
    click_tab: function(event, index) {      
      this.see_details(index)
    },
    get_parameter: function(id) {
      return get_parameter(id);
    },
    render_page: function() {
      // by default all sections are hidden
      const page_mode = get_parameter("page_mode");
      // tabs
      dom.get("tabs").style.display = page_mode == "tabs" ? "" : "none";
      // sections
      switch (page_mode) {
        case "onepage":          
          for (i = 0; i < NB_SECTIONS; i++) {
            const sec = dom.get("section_"+i);
            if (sec) sec.style.display = "";
          }
          window.scrollTo(0,0);
          break;
        case "tabs":
          this.see_details(0);
          window.scrollTo(0,0);
          break;
      }
    },
    init_page: function() {
      //console.log(parameters)
      build_parameters();
      action.init();
      this.render_page();
    },
  }
})(window);
