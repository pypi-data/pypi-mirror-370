import {
  isPathAbsolute,
  isUrl,
  normalizePath,
  resolvePath
} from "./chunk-OV76USRJ.js";

// src/typespec/core/packages/compiler/dist/src/utils/misc.js
function deepFreeze(value) {
  if (Array.isArray(value)) {
    value.forEach(deepFreeze);
  } else if (typeof value === "object") {
    for (const prop in value) {
      deepFreeze(value[prop]);
    }
  }
  return Object.freeze(value);
}
function deepClone(value) {
  if (Array.isArray(value)) {
    return value.map(deepClone);
  }
  if (typeof value === "object") {
    const obj = {};
    for (const prop in value) {
      obj[prop] = deepClone(value[prop]);
    }
    return obj;
  }
  return value;
}
function deepEquals(left, right) {
  if (left === right) {
    return true;
  }
  if (left === null || right === null || typeof left !== "object" || typeof right !== "object") {
    return false;
  }
  if (Array.isArray(left)) {
    return Array.isArray(right) ? arrayEquals(left, right, deepEquals) : false;
  }
  return mapEquals(new Map(Object.entries(left)), new Map(Object.entries(right)), deepEquals);
}
function arrayEquals(left, right, equals = (x, y) => x === y) {
  if (left === right) {
    return true;
  }
  if (left.length !== right.length) {
    return false;
  }
  for (let i = 0; i < left.length; i++) {
    if (!equals(left[i], right[i])) {
      return false;
    }
  }
  return true;
}
function mapEquals(left, right, equals = (x, y) => x === y) {
  if (left === right) {
    return true;
  }
  if (left.size !== right.size) {
    return false;
  }
  for (const [key, value] of left) {
    if (!right.has(key) || !equals(value, right.get(key))) {
      return false;
    }
  }
  return true;
}
async function getNormalizedRealPath(host, path) {
  try {
    return normalizePath(await host.realpath(path));
  } catch (error) {
    if (error.code === "ENOENT") {
      return normalizePath(path);
    }
    throw error;
  }
}
async function readUrlOrPath(host, pathOrUrl) {
  if (isUrl(pathOrUrl)) {
    return host.readUrl(pathOrUrl);
  }
  return host.readFile(pathOrUrl);
}
function resolveRelativeUrlOrPath(base, relativeOrAbsolute) {
  if (isUrl(relativeOrAbsolute)) {
    return relativeOrAbsolute;
  } else if (isPathAbsolute(relativeOrAbsolute)) {
    return relativeOrAbsolute;
  } else if (isUrl(base)) {
    return new URL(relativeOrAbsolute, base).href;
  } else {
    return resolvePath(base, relativeOrAbsolute);
  }
}
function isArray(arg) {
  return Array.isArray(arg);
}
function isDefined(arg) {
  return arg !== void 0;
}
function isWhitespaceStringOrUndefined(str) {
  return !str || /^\s*$/.test(str);
}
function firstNonWhitespaceCharacterIndex(line) {
  return line.search(/\S/);
}
function distinctArray(arr, keySelector) {
  const map = /* @__PURE__ */ new Map();
  for (const item of arr) {
    map.set(keySelector(item), item);
  }
  return Array.from(map.values());
}
function tryParseJson(content) {
  try {
    return JSON.parse(content);
  } catch {
    return void 0;
  }
}
function omitUndefined(data) {
  return Object.fromEntries(Object.entries(data).filter(([k, v]) => v !== void 0));
}
function resolveTspMain(packageJson) {
  if (packageJson?.tspMain !== void 0) {
    return packageJson.tspMain;
  }
  return void 0;
}
var MultiKeyMap = class {
  #currentId = 0;
  #idMap = /* @__PURE__ */ new WeakMap();
  #items = /* @__PURE__ */ new Map();
  get(items) {
    return this.#items.get(this.compositeKeyFor(items));
  }
  set(items, value) {
    const key = this.compositeKeyFor(items);
    this.#items.set(key, value);
  }
  compositeKeyFor(items) {
    return items.map((i) => this.keyFor(i)).join(",");
  }
  keyFor(item) {
    if (this.#idMap.has(item)) {
      return this.#idMap.get(item);
    }
    const id = this.#currentId++;
    this.#idMap.set(item, id);
    return id;
  }
};
var TwoLevelMap = class extends Map {
  /**
   * Get an existing entry in the map or add a new one if not found.
   *
   * @param key1 The first key
   * @param key2 The second key
   * @param create A callback to create the new entry when not found.
   * @param sentinel An optional sentinel value to use to indicate that the
   *                 entry is being created.
   */
  getOrAdd(key1, key2, create, sentinel) {
    let map = this.get(key1);
    if (map === void 0) {
      map = /* @__PURE__ */ new Map();
      this.set(key1, map);
    }
    let entry = map.get(key2);
    if (entry === void 0) {
      if (sentinel !== void 0) {
        map.set(key2, sentinel);
      }
      entry = create();
      map.set(key2, entry);
    }
    return entry;
  }
};
var Queue = class {
  #elements;
  #headIndex = 0;
  constructor(elements) {
    this.#elements = elements?.slice() ?? [];
  }
  isEmpty() {
    return this.#headIndex === this.#elements.length;
  }
  enqueue(...items) {
    this.#elements.push(...items);
  }
  dequeue() {
    if (this.isEmpty()) {
      throw new Error("Queue is empty.");
    }
    const result = this.#elements[this.#headIndex];
    this.#elements[this.#headIndex] = void 0;
    this.#headIndex++;
    if (this.#headIndex > 100 && this.#headIndex > this.#elements.length >> 1) {
      const newLength = this.#elements.length - this.#headIndex;
      this.#elements.copyWithin(0, this.#headIndex);
      this.#elements.length = newLength;
      this.#headIndex = 0;
    }
    return result;
  }
};
function mutate(value) {
  return value;
}
function createRekeyableMap(entries) {
  return new RekeyableMapImpl(entries);
}
var RekeyableMapImpl = class {
  #keys = /* @__PURE__ */ new Map();
  #values = /* @__PURE__ */ new Map();
  constructor(entries) {
    if (entries) {
      for (const [key, value] of entries) {
        this.set(key, value);
      }
    }
  }
  clear() {
    this.#keys.clear();
    this.#values.clear();
  }
  delete(key) {
    const keyItem = this.#keys.get(key);
    if (keyItem) {
      this.#keys.delete(key);
      return this.#values.delete(keyItem);
    }
    return false;
  }
  forEach(callbackfn, thisArg) {
    this.#values.forEach((value, keyItem) => {
      callbackfn(value, keyItem.key, this);
    }, thisArg);
  }
  get(key) {
    const keyItem = this.#keys.get(key);
    return keyItem ? this.#values.get(keyItem) : void 0;
  }
  has(key) {
    return this.#keys.has(key);
  }
  set(key, value) {
    let keyItem = this.#keys.get(key);
    if (!keyItem) {
      keyItem = { key };
      this.#keys.set(key, keyItem);
    }
    this.#values.set(keyItem, value);
    return this;
  }
  get size() {
    return this.#values.size;
  }
  *entries() {
    for (const [k, v] of this.#values) {
      yield [k.key, v];
    }
  }
  *keys() {
    for (const k of this.#values.keys()) {
      yield k.key;
    }
  }
  values() {
    return this.#values.values();
  }
  [Symbol.iterator]() {
    return this.entries();
  }
  [Symbol.toStringTag] = "RekeyableMap";
  rekey(existingKey, newKey) {
    const keyItem = this.#keys.get(existingKey);
    if (!keyItem) {
      return false;
    }
    this.#keys.delete(existingKey);
    const newKeyItem = this.#keys.get(newKey);
    if (newKeyItem) {
      this.#values.delete(newKeyItem);
    }
    keyItem.key = newKey;
    this.#keys.set(newKey, keyItem);
    return true;
  }
};

export {
  deepFreeze,
  deepClone,
  deepEquals,
  mapEquals,
  getNormalizedRealPath,
  readUrlOrPath,
  resolveRelativeUrlOrPath,
  isArray,
  isDefined,
  isWhitespaceStringOrUndefined,
  firstNonWhitespaceCharacterIndex,
  distinctArray,
  tryParseJson,
  omitUndefined,
  resolveTspMain,
  MultiKeyMap,
  TwoLevelMap,
  Queue,
  mutate,
  createRekeyableMap
};
