((w_1, undef) => {
function dataclass(fields, defaults = {}, validate = () => {}, methods = {}) {
  const Cls = class {
    constructor(...args) {
      fields.forEach((field, index) => {
        this[field] = args[index] !== undefined ? args[index] : defaults[field];
      });
      validate(this);
      // Object.freeze(this); // immutable
    }
    // toString() {
    //   return `${this.constructor.name}(${fields.map(f => `${f}=${this[f]}`).join(', ')})`;
    // }
    // toJSON() {
    //   return Object.fromEntries(fields.map(f => [f, this[f]]));
    // }
  };
  Object.entries(methods).forEach(([name, fn]) => {
    Cls.prototype[name] = fn;
  });
  return Cls;
}
w_1.dataclass = dataclass;
})(window);
