((w_1, undef) => {

function get_img_data(img) {
  const width = img.width;
  const height = img.height;
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);
  return ctx.getImageData(0, 0, width, height).data;
}

const SLImages = {
  init: function() {
    const nodes = dom.q(document.body, ".sl-diff-image");
    for (const img of nodes) {
      
      const threshold = 0;
      
      const width = img.width;
      const height = img.height;
      const canvas = dom.elt_p(img.parentNode,"canvas",null,{width:width,height:height,class:"img_reader"})
      const comp_ctx = canvas.getContext("2d");
      const comp_data = comp_ctx.createImageData(width, height);

      const img_data = get_img_data(img);

      for (let i = 0; i < img_data.length; i += 4) {
        // channels
        const c_r = img_data[i];
        const c_g = img_data[i + 1];
        const c_b = img_data[i + 2];
        // diff total
        const diff = (c_r + c_g + c_b) / 3;
        // if (c_r != 0 || c_g != 0 || c_b != 0) {
        if (diff > threshold) {
          comp_data.data[i]     = 255; // Rouge
          comp_data.data[i + 1] = 0;
          comp_data.data[i + 2] = 0;
          comp_data.data[i + 3] = 255;        
        } else {
          comp_data.data[i]     = 255; // Blanc
          comp_data.data[i + 1] = 255;
          comp_data.data[i + 2] = 255;
          comp_data.data[i + 3] = 255;
        }
      }
      comp_ctx.putImageData(comp_data, 0, 0);
    }
  },
};
w_1.SLImages = SLImages;

})(window);
