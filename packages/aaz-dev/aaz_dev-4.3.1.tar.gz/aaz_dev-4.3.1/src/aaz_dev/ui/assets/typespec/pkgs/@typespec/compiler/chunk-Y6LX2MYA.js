// src/typespec/core/packages/compiler/dist/src/typekit/define-kit.js
var TypekitPrototype = {};
var TypekitNamespaceSymbol = Symbol.for("TypekitNamespace");
function defineKit(source) {
  for (const [name, fnOrNs] of Object.entries(source)) {
    let kits = fnOrNs;
    if (TypekitPrototype[name] !== void 0) {
      kits = { ...TypekitPrototype[name], ...fnOrNs };
    }
    if (typeof kits === "object" && kits !== null) {
      Object.defineProperty(kits, TypekitNamespaceSymbol, {
        value: true,
        enumerable: false,
        // Keep the symbol non-enumerable
        configurable: false
      });
    }
    TypekitPrototype[name] = kits;
  }
}

// src/typespec/core/packages/compiler/dist/src/experimental/typekit/index.js
function createTypekit(realm) {
  const tk = Object.create(TypekitPrototype);
  const handler = {
    get(target, prop, receiver) {
      if (prop === "program") {
        return realm.program;
      }
      if (prop === "realm") {
        return realm;
      }
      const value = Reflect.get(target, prop, receiver);
      if (typeof value === "function") {
        const proxyWrapper = function(...args) {
          return value.apply(proxy, args);
        };
        for (const propName of Object.keys(value)) {
          const originalPropValue = value[propName];
          if (typeof originalPropValue === "function") {
            proxyWrapper[propName] = function(...args) {
              return originalPropValue.apply(proxy, args);
            };
          } else {
            Reflect.defineProperty(proxyWrapper, propName, Reflect.getOwnPropertyDescriptor(value, propName));
          }
        }
        return proxyWrapper;
      }
      if (typeof value === "object" && value !== null && !Reflect.getOwnPropertyDescriptor(target, prop)?.get) {
        return new Proxy(value, handler);
      }
      return value;
    }
  };
  const proxy = new Proxy(tk, handler);
  return proxy;
}

export {
  defineKit,
  createTypekit
};
