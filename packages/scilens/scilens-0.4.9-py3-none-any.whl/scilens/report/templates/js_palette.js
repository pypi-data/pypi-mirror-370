((w_1, undef) => {
const a = ['#845ec2','#d65db1','#ff6f91','#ff9671','#ffc75f','#f9f871'];
w_1.palette = {
  get: function(n) { return a[n % a.length]; },
  get1: function(n) { return this.get(n-1); },
};
})(window);
