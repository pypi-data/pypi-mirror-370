// src/typespec/core/packages/compiler/dist/src/utils/duplicate-tracker.js
var DuplicateTracker = class {
  #entries = /* @__PURE__ */ new Map();
  /**
   * Track usage of K.
   * @param k key that is being checked for duplicate.
   * @param v value that map to the key
   */
  track(k, v) {
    const existing = this.#entries.get(k);
    if (existing === void 0) {
      this.#entries.set(k, [v]);
    } else {
      existing.push(v);
    }
  }
  /**
   * Return iterator of all the duplicate entries.
   */
  *entries() {
    for (const [k, v] of this.#entries.entries()) {
      if (v.length > 1) {
        yield [k, v];
      }
    }
  }
};

// src/typespec/core/packages/compiler/dist/src/utils/state-accessor.js
function useStateMap(key) {
  const getter = (program, target) => program.stateMap(key).get(target);
  const setter = (program, target, value) => program.stateMap(key).set(target, value);
  const mapGetter = (program) => program.stateMap(key);
  return [getter, setter, mapGetter];
}
function useStateSet(key) {
  const getter = (program, target) => program.stateSet(key).has(target);
  const setter = (program, target) => program.stateSet(key).add(target);
  return [getter, setter];
}

export {
  useStateMap,
  useStateSet,
  DuplicateTracker
};
