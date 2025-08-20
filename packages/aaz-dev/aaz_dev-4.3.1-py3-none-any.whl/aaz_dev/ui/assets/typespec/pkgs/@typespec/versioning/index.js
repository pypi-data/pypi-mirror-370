var __defProp = Object.defineProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// src/typespec/core/packages/versioning/dist/src/index.js
var src_exports = {};
__export(src_exports, {
  $added: () => $added,
  $decorators: () => $decorators,
  $madeOptional: () => $madeOptional,
  $madeRequired: () => $madeRequired,
  $onValidate: () => $onValidate,
  $removed: () => $removed,
  $renamedFrom: () => $renamedFrom,
  $returnTypeChangedFrom: () => $returnTypeChangedFrom,
  $typeChangedFrom: () => $typeChangedFrom,
  $useDependency: () => $useDependency,
  $versioned: () => $versioned,
  Availability: () => Availability,
  VersionMap: () => VersionMap,
  createVersionMutator: () => createVersionMutator,
  findVersionedNamespace: () => findVersionedNamespace,
  getAddedOnVersions: () => getAddedOnVersions,
  getAllVersions: () => getAllVersions,
  getAvailabilityMap: () => getAvailabilityMap,
  getAvailabilityMapInTimeline: () => getAvailabilityMapInTimeline,
  getMadeOptionalOn: () => getMadeOptionalOn,
  getRemovedOnVersions: () => getRemovedOnVersions,
  getRenamedFrom: () => getRenamedFrom,
  getRenamedFromVersions: () => getRenamedFromVersions,
  getReturnTypeChangedFrom: () => getReturnTypeChangedFrom,
  getTypeChangedFrom: () => getTypeChangedFrom,
  getUseDependencies: () => getUseDependencies,
  getVersion: () => getVersion,
  getVersionDependencies: () => getVersionDependencies,
  getVersionForEnumMember: () => getVersionForEnumMember,
  getVersioningMutators: () => getVersioningMutators,
  getVersions: () => getVersions,
  getVersionsForEnum: () => getVersionsForEnum,
  resolveVersions: () => resolveVersions
});

// src/typespec/core/packages/versioning/dist/src/decorators.js
var decorators_exports = {};
__export(decorators_exports, {
  $added: () => $added,
  $madeOptional: () => $madeOptional,
  $madeRequired: () => $madeRequired,
  $removed: () => $removed,
  $renamedFrom: () => $renamedFrom,
  $returnTypeChangedFrom: () => $returnTypeChangedFrom,
  $typeChangedFrom: () => $typeChangedFrom,
  $useDependency: () => $useDependency,
  $versioned: () => $versioned,
  VersionMap: () => VersionMap,
  findVersionedNamespace: () => findVersionedNamespace,
  getAddedOnVersions: () => getAddedOnVersions,
  getMadeOptionalOn: () => getMadeOptionalOn,
  getMadeRequiredOn: () => getMadeRequiredOn,
  getRemovedOnVersions: () => getRemovedOnVersions,
  getRenamedFrom: () => getRenamedFrom,
  getRenamedFromVersions: () => getRenamedFromVersions,
  getReturnTypeChangedFrom: () => getReturnTypeChangedFrom,
  getTypeChangedFrom: () => getTypeChangedFrom,
  getUseDependencies: () => getUseDependencies,
  getVersion: () => getVersion,
  namespace: () => namespace
});

// src/typespec/core/packages/versioning/dist/src/lib.js
import { createTypeSpecLibrary, paramMessage } from "@typespec/compiler";
var $lib = createTypeSpecLibrary({
  name: "@typespec/versioning",
  diagnostics: {
    "versioned-dependency-tuple": {
      severity: "error",
      messages: {
        default: `Versioned dependency mapping must be a tuple [SourceVersion, TargetVersion].`
      }
    },
    "versioned-dependency-tuple-enum-member": {
      severity: "error",
      messages: {
        default: `Versioned dependency mapping must be between enum members.`
      }
    },
    "versioned-dependency-same-namespace": {
      severity: "error",
      messages: {
        default: `Versioned dependency mapping must all point to the same namespace but 2 versions have different namespaces '${"namespace1"}' and '${"namespace2"}'.`
      }
    },
    "versioned-dependency-record-not-mapping": {
      severity: "error",
      messages: {
        default: paramMessage`The versionedDependency decorator must provide a model mapping local versions to dependency '${"dependency"}' versions`
      }
    },
    "versioned-dependency-not-picked": {
      severity: "error",
      messages: {
        default: paramMessage`The versionedDependency decorator must provide a version of the dependency '${"dependency"}'.`
      }
    },
    "version-not-found": {
      severity: "error",
      messages: {
        default: paramMessage`The provided version '${"version"}' from '${"enumName"}' is not declared as a version enum. Use '@versioned(${"enumName"})' on the containing namespace.`
      }
    },
    "version-duplicate": {
      severity: "error",
      messages: {
        default: paramMessage`Multiple versions from '${"name"}' resolve to the same value. Version enums must resolve to unique values.`
      }
    },
    "using-versioned-library": {
      severity: "error",
      messages: {
        default: paramMessage`Namespace '${"sourceNs"}' is referencing types from versioned namespace '${"targetNs"}' but didn't specify which versions with @useDependency.`
      }
    },
    "invalid-renamed-from-value": {
      severity: "error",
      messages: {
        default: "@renamedFrom.oldName cannot be empty string."
      }
    },
    "incompatible-versioned-reference": {
      severity: "error",
      messages: {
        default: paramMessage`'${"sourceName"}' is referencing versioned type '${"targetName"}' but is not versioned itself.`,
        addedAfter: paramMessage`'${"sourceName"}' was added in version '${"sourceAddedOn"}' but referencing type '${"targetName"}' added in version '${"targetAddedOn"}'.`,
        dependentAddedAfter: paramMessage`'${"sourceName"}' was added in version '${"sourceAddedOn"}' but contains type '${"targetName"}' added in version '${"targetAddedOn"}'.`,
        removedBefore: paramMessage`'${"sourceName"}' was removed in version '${"sourceRemovedOn"}' but referencing type '${"targetName"}' removed in version '${"targetRemovedOn"}'.`,
        dependentRemovedBefore: paramMessage`'${"sourceName"}' was removed in version '${"sourceRemovedOn"}' but contains type '${"targetName"}' removed in version '${"targetRemovedOn"}'.`,
        versionedDependencyAddedAfter: paramMessage`'${"sourceName"}' is referencing type '${"targetName"}' added in version '${"targetAddedOn"}' but version used is '${"dependencyVersion"}'.`,
        versionedDependencyRemovedBefore: paramMessage`'${"sourceName"}' is referencing type '${"targetName"}' removed in version '${"targetAddedOn"}' but version used is '${"dependencyVersion"}'.`,
        doesNotExist: paramMessage`'${"sourceName"}' is referencing type '${"targetName"}' which does not exist in version '${"version"}'.`
      }
    },
    "incompatible-versioned-namespace-use-dependency": {
      severity: "error",
      messages: {
        default: "The useDependency decorator can only be used on a Namespace if the namespace is unversioned. For versioned namespaces, put the useDependency decorator on the version enum members."
      }
    },
    "made-optional-not-optional": {
      severity: "error",
      messages: {
        default: paramMessage`Property '${"name"}' marked with @madeOptional but is required. Should be '${"name"}?'`
      }
    },
    "made-required-optional": {
      severity: "error",
      messages: {
        default: paramMessage`Property '${"name"}?' marked with @madeRequired but is optional. Should be '${"name"}'`
      }
    },
    "renamed-duplicate-property": {
      severity: "error",
      messages: {
        default: paramMessage`Property '${"name"}' marked with '@renamedFrom' conflicts with existing property in version ${"version"}.`
      }
    }
  },
  state: {
    versionIndex: { description: "Version index" },
    addedOn: { description: "State for @addedOn decorator" },
    removedOn: { description: "State for @removedOn decorator" },
    versions: { description: "State for @versioned decorator" },
    useDependencyNamespace: { description: "State for @useDependency decorator on Namespaces" },
    useDependencyEnum: { description: "State for @useDependency decorator on Enums" },
    renamedFrom: { description: "State for @renamedFrom decorator" },
    madeOptional: { description: "State for @madeOptional decorator" },
    madeRequired: { description: "State for @madeRequired decorator" },
    typeChangedFrom: { description: "State for @typeChangedFrom decorator" },
    returnTypeChangedFrom: { description: "State for @returnTypeChangedFrom decorator" }
  }
});
var { reportDiagnostic, createStateSymbol, stateKeys: VersioningStateKeys } = $lib;

// src/typespec/core/packages/versioning/dist/src/versioning.js
import { getNamespaceFullName } from "@typespec/compiler";

// src/typespec/core/packages/versioning/dist/src/versioning-timeline.js
import { compilerAssert, getTypeName } from "@typespec/compiler";
var VersioningTimeline = class {
  #namespaces;
  #timeline;
  #momentIndex;
  #versionIndex;
  constructor(program, resolutions) {
    const indexedVersions = /* @__PURE__ */ new Set();
    const namespaces = /* @__PURE__ */ new Set();
    const timeline = this.#timeline = resolutions.map((x) => new TimelineMoment(x));
    for (const resolution of resolutions) {
      for (const [namespace2, version] of resolution.entries()) {
        indexedVersions.add(version);
        namespaces.add(namespace2);
      }
    }
    this.#namespaces = [...namespaces];
    function findIndexToInsert(version) {
      for (const [index, moment] of timeline.entries()) {
        const versionAtMoment = moment.getVersion(version.namespace);
        if (versionAtMoment && version.index < versionAtMoment.index) {
          return index;
        }
      }
      return -1;
    }
    for (const namespace2 of namespaces) {
      const [, versions] = getVersions(program, namespace2);
      if (versions === void 0) {
        continue;
      }
      for (const version of versions.getVersions()) {
        if (!indexedVersions.has(version)) {
          indexedVersions.add(version);
          const index = findIndexToInsert(version);
          const newMoment = new TimelineMoment(/* @__PURE__ */ new Map([[version.namespace, version]]));
          if (index === -1) {
            timeline.push(newMoment);
          } else {
            timeline.splice(index, 0, newMoment);
          }
        }
      }
    }
    this.#versionIndex = /* @__PURE__ */ new Map();
    this.#momentIndex = /* @__PURE__ */ new Map();
    for (const [index, moment] of timeline.entries()) {
      this.#momentIndex.set(moment, index);
      for (const version of moment.versions()) {
        if (!this.#versionIndex.has(version)) {
          this.#versionIndex.set(version, index);
        }
      }
    }
  }
  prettySerialize() {
    const hSep = "-".repeat(this.#namespaces.length * 13 + 1);
    const content = this.#timeline.map((moment) => {
      return "| " + this.#namespaces.map((x) => (moment.getVersion(x)?.name ?? "").padEnd(10, " ")).join(" | ") + " |";
    }).join(`
${hSep}
`);
    return ["", hSep, content, hSep].join("\n");
  }
  get(version) {
    const index = this.getIndex(version);
    if (index === -1) {
      if (version instanceof TimelineMoment) {
        compilerAssert(false, `Timeline moment "${version?.name}" should have been resolved`);
      } else {
        compilerAssert(false, `Version "${version?.name}" from ${getTypeName(version.namespace)} should have been resolved. ${this.prettySerialize()}`);
      }
    }
    return this.#timeline[index];
  }
  /**
   * Return index in the timeline that this version points to
   * Returns -1 if version is not found.
   */
  getIndex(version) {
    const index = version instanceof TimelineMoment ? this.#momentIndex.get(version) : this.#versionIndex.get(version);
    if (index === void 0) {
      return -1;
    }
    return index;
  }
  /**
   * Return true if {@link isBefore} is before {@link base}
   * @param isBefore
   * @param base
   */
  isBefore(isBefore, base) {
    const isBeforeIndex = this.getIndex(isBefore);
    const baseIndex = this.getIndex(base);
    return isBeforeIndex < baseIndex;
  }
  first() {
    return this.#timeline[0];
  }
  [Symbol.iterator]() {
    return this.#timeline[Symbol.iterator]();
  }
  entries() {
    return this.#timeline.entries();
  }
};
var TimelineMoment = class {
  name;
  #versionMap;
  constructor(versionMap) {
    this.#versionMap = versionMap;
    this.name = versionMap.values().next().value?.name ?? "";
  }
  getVersion(namespace2) {
    return this.#versionMap.get(namespace2);
  }
  versions() {
    return this.#versionMap.values();
  }
};

// src/typespec/core/packages/versioning/dist/src/versioning.js
function getVersionDependencies(program, namespace2) {
  const useDeps = getUseDependencies(program, namespace2);
  if (useDeps) {
    return useDeps;
  }
  return void 0;
}
function resolveDependencyVersions(program, initialResolutions) {
  const resolutions = new Map(initialResolutions);
  const namespacesToCheck = [...initialResolutions.entries()];
  while (namespacesToCheck.length > 0) {
    const [current, currentVersion] = namespacesToCheck.pop();
    const dependencies = getVersionDependencies(program, current);
    for (const [dependencyNs, versionMap] of dependencies ?? /* @__PURE__ */ new Map()) {
      if (resolutions.has(dependencyNs)) {
        continue;
      }
      if (!(versionMap instanceof Map)) {
        const rootNsName = getNamespaceFullName(current);
        const dependencyNsName = getNamespaceFullName(dependencyNs);
        throw new Error(`Unexpected error: Namespace ${rootNsName} version dependency to ${dependencyNsName} should be a mapping of version.`);
      }
      const dependencyVersion = versionMap.get(currentVersion);
      namespacesToCheck.push([dependencyNs, dependencyVersion]);
      resolutions.set(dependencyNs, dependencyVersion);
    }
  }
  return resolutions;
}
function resolveVersions(program, namespace2) {
  const [rootNs, versions] = getVersions(program, namespace2);
  const dependencies = (rootNs && getVersionDependencies(program, rootNs)) ?? /* @__PURE__ */ new Map();
  if (!versions) {
    if (dependencies.size === 0) {
      return [{ rootVersion: void 0, versions: /* @__PURE__ */ new Map() }];
    } else {
      const map = /* @__PURE__ */ new Map();
      for (const [dependencyNs, version] of dependencies) {
        if (version instanceof Map) {
          const rootNsName = getNamespaceFullName(namespace2);
          const dependencyNsName = getNamespaceFullName(dependencyNs);
          throw new Error(`Unexpected error: Namespace ${rootNsName} version dependency to ${dependencyNsName} should be a picked version.`);
        }
        map.set(dependencyNs, version);
      }
      return [{ rootVersion: void 0, versions: resolveDependencyVersions(program, map) }];
    }
  } else {
    return versions.getVersions().map((version) => {
      const resolutions = resolveDependencyVersions(program, /* @__PURE__ */ new Map([[rootNs, version]]));
      return {
        rootVersion: version,
        versions: resolutions
      };
    });
  }
}
var versionCache = /* @__PURE__ */ new WeakMap();
function cacheVersion(key, versions) {
  versionCache.set(key, versions);
  return versions;
}
function getVersionsForEnum(program, en) {
  const namespace2 = en.namespace;
  if (namespace2 === void 0) {
    return [];
  }
  const nsVersion = getVersion(program, namespace2);
  if (nsVersion === void 0) {
    return [];
  }
  return [namespace2, nsVersion];
}
function getVersions(p, t) {
  const existing = versionCache.get(t);
  if (existing) {
    return existing;
  }
  switch (t.kind) {
    case "Namespace":
      return resolveVersionsForNamespace(p, t);
    case "Operation":
    case "Interface":
    case "Model":
    case "Union":
    case "Scalar":
    case "Enum":
      if (t.namespace) {
        return cacheVersion(t, getVersions(p, t.namespace) || []);
      } else if (t.kind === "Operation" && t.interface) {
        return cacheVersion(t, getVersions(p, t.interface) || []);
      } else {
        return cacheVersion(t, []);
      }
    case "ModelProperty":
      if (t.sourceProperty) {
        return getVersions(p, t.sourceProperty);
      } else if (t.model) {
        return getVersions(p, t.model);
      } else {
        return cacheVersion(t, []);
      }
    case "EnumMember":
      return cacheVersion(t, getVersions(p, t.enum) || []);
    case "UnionVariant":
      return cacheVersion(t, getVersions(p, t.union) || []);
    default:
      return cacheVersion(t, []);
  }
}
function resolveVersionsForNamespace(program, namespace2) {
  const nsVersion = getVersion(program, namespace2);
  if (nsVersion !== void 0) {
    return cacheVersion(namespace2, [namespace2, nsVersion]);
  }
  const parentNamespaceVersion = namespace2.namespace && getVersions(program, namespace2.namespace)[1];
  const hasDependencies = getUseDependencies(program, namespace2);
  if (parentNamespaceVersion || hasDependencies) {
    return cacheVersion(namespace2, [namespace2, parentNamespaceVersion]);
  } else {
    return cacheVersion(namespace2, [namespace2, void 0]);
  }
}
function getAllVersions(p, t) {
  const [namespace2, _] = getVersions(p, t);
  if (namespace2 === void 0)
    return void 0;
  return getVersion(p, namespace2)?.getVersions();
}
var Availability;
(function(Availability2) {
  Availability2["Unavailable"] = "Unavailable";
  Availability2["Added"] = "Added";
  Availability2["Available"] = "Available";
  Availability2["Removed"] = "Removed";
})(Availability || (Availability = {}));
function getParentAddedVersion(program, type, versions) {
  let parentMap = void 0;
  if (type.kind === "ModelProperty" && type.model !== void 0) {
    parentMap = getAvailabilityMap(program, type.model);
  } else if (type.kind === "Operation" && type.interface !== void 0) {
    parentMap = getAvailabilityMap(program, type.interface);
  }
  if (parentMap === void 0)
    return void 0;
  for (const [key, value] of parentMap.entries()) {
    if (value === Availability.Added) {
      return versions.find((x) => x.name === key);
    }
  }
  return void 0;
}
function getParentRemovedVersion(program, type, versions) {
  let parentMap = void 0;
  if (type.kind === "ModelProperty" && type.model !== void 0) {
    parentMap = getAvailabilityMap(program, type.model);
  } else if (type.kind === "Operation" && type.interface !== void 0) {
    parentMap = getAvailabilityMap(program, type.interface);
  }
  if (parentMap === void 0)
    return void 0;
  for (const [key, value] of parentMap.entries()) {
    if (value === Availability.Removed) {
      return versions.find((x) => x.name === key);
    }
  }
  return void 0;
}
function getParentAddedVersionInTimeline(program, type, timeline) {
  let parentMap = void 0;
  if (type.kind === "ModelProperty" && type.model !== void 0) {
    parentMap = getAvailabilityMapInTimeline(program, type.model, timeline);
  } else if (type.kind === "Operation" && type.interface !== void 0) {
    parentMap = getAvailabilityMapInTimeline(program, type.interface, timeline);
  }
  if (parentMap === void 0)
    return void 0;
  for (const [moment, availability] of parentMap.entries()) {
    if (availability === Availability.Added) {
      return moment.versions().next().value;
    }
  }
  return void 0;
}
function resolveWhenFirstAdded(added, removed, parentAdded) {
  const implicitlyAvailable = !added.length && !removed.length;
  if (implicitlyAvailable) {
    return [parentAdded];
  }
  if (added.length) {
    const addedFirst = !removed.length || added[0].index < removed[0].index;
    if (addedFirst) {
      return added;
    }
  }
  if (removed.length) {
    const removedFirst = !added.length || removed[0].index < added[0].index;
    if (removedFirst) {
      return [parentAdded, ...added];
    }
  }
  return added;
}
function resolveRemoved(added, removed, parentRemoved) {
  if (removed.length) {
    return removed;
  }
  const implicitlyRemoved = !added.length || parentRemoved && added[0].index < parentRemoved.index;
  if (parentRemoved && implicitlyRemoved) {
    return [parentRemoved];
  }
  return [];
}
function getAvailabilityMap(program, type) {
  const avail = /* @__PURE__ */ new Map();
  const allVersions = getAllVersions(program, type);
  if (allVersions === void 0)
    return void 0;
  const firstVersion = allVersions[0];
  const parentAdded = getParentAddedVersion(program, type, allVersions) ?? firstVersion;
  const parentRemoved = getParentRemovedVersion(program, type, allVersions);
  let added = getAddedOnVersions(program, type) ?? [];
  let removed = getRemovedOnVersions(program, type) ?? [];
  const typeChanged = getTypeChangedFrom(program, type);
  const returnTypeChanged = getReturnTypeChangedFrom(program, type);
  if (!added.length && !removed.length && typeChanged === void 0 && returnTypeChanged === void 0)
    return void 0;
  added = resolveWhenFirstAdded(added, removed, parentAdded);
  removed = resolveRemoved(added, removed, parentRemoved);
  let isAvail = false;
  for (const ver of allVersions) {
    const add = added.find((x) => x.index === ver.index);
    const rem = removed.find((x) => x.index === ver.index);
    if (rem) {
      isAvail = false;
      avail.set(ver.name, Availability.Removed);
    } else if (add) {
      isAvail = true;
      avail.set(ver.name, Availability.Added);
    } else if (isAvail) {
      avail.set(ver.name, Availability.Available);
    } else {
      avail.set(ver.name, Availability.Unavailable);
    }
  }
  return avail;
}
function getAvailabilityMapInTimeline(program, type, timeline) {
  const avail = /* @__PURE__ */ new Map();
  const firstVersion = timeline.first().versions().next().value;
  const parentAdded = getParentAddedVersionInTimeline(program, type, timeline) ?? firstVersion;
  let added = getAddedOnVersions(program, type) ?? [];
  const removed = getRemovedOnVersions(program, type) ?? [];
  const typeChanged = getTypeChangedFrom(program, type);
  const returnTypeChanged = getReturnTypeChangedFrom(program, type);
  if (!added.length && !removed.length && typeChanged === void 0 && returnTypeChanged === void 0)
    return void 0;
  added = resolveWhenFirstAdded(added, removed, parentAdded);
  let isAvail = false;
  for (const [index, moment] of timeline.entries()) {
    const add = added.find((x) => timeline.getIndex(x) === index);
    const rem = removed.find((x) => timeline.getIndex(x) === index);
    if (rem) {
      isAvail = false;
      avail.set(moment, Availability.Removed);
    } else if (add) {
      isAvail = true;
      avail.set(moment, Availability.Added);
    } else if (isAvail) {
      avail.set(moment, Availability.Available);
    } else {
      avail.set(moment, Availability.Unavailable);
    }
  }
  return avail;
}
function getVersionForEnumMember(program, member) {
  const parentEnum = member.enum;
  const [, versions] = getVersionsForEnum(program, parentEnum);
  return versions?.getVersionForEnumMember(member);
}

// src/typespec/core/packages/versioning/dist/src/decorators.js
var namespace = "TypeSpec.Versioning";
function checkIsVersion(program, enumMember, diagnosticTarget) {
  const version = getVersionForEnumMember(program, enumMember);
  if (!version) {
    reportDiagnostic(program, {
      code: "version-not-found",
      target: diagnosticTarget,
      format: { version: enumMember.name, enumName: enumMember.enum.name }
    });
  }
  return version;
}
var $added = (context, t, v) => {
  const { program } = context;
  const version = checkIsVersion(context.program, v, context.getArgumentTarget(0));
  if (!version) {
    return;
  }
  const record = program.stateMap(VersioningStateKeys.addedOn).get(t) ?? new Array();
  record.push(version);
  record.sort((a, b) => a.index - b.index);
  program.stateMap(VersioningStateKeys.addedOn).set(t, record);
};
function $removed(context, t, v) {
  const { program } = context;
  const version = checkIsVersion(context.program, v, context.getArgumentTarget(0));
  if (!version) {
    return;
  }
  const record = program.stateMap(VersioningStateKeys.removedOn).get(t) ?? new Array();
  record.push(version);
  record.sort((a, b) => a.index - b.index);
  program.stateMap(VersioningStateKeys.removedOn).set(t, record);
}
function getTypeChangedFrom(p, t) {
  return p.stateMap(VersioningStateKeys.typeChangedFrom).get(t);
}
var $typeChangedFrom = (context, prop, v, oldType) => {
  const { program } = context;
  const version = checkIsVersion(context.program, v, context.getArgumentTarget(0));
  if (!version) {
    return;
  }
  let record = getTypeChangedFrom(program, prop) ?? /* @__PURE__ */ new Map();
  record.set(version, oldType);
  record = new Map([...record.entries()].sort((a, b) => a[0].index - b[0].index));
  program.stateMap(VersioningStateKeys.typeChangedFrom).set(prop, record);
};
function getReturnTypeChangedFrom(p, t) {
  return p.stateMap(VersioningStateKeys.returnTypeChangedFrom).get(t);
}
var $returnTypeChangedFrom = (context, op, v, oldReturnType) => {
  const { program } = context;
  const version = checkIsVersion(context.program, v, context.getArgumentTarget(0));
  if (!version) {
    return;
  }
  let record = getReturnTypeChangedFrom(program, op) ?? /* @__PURE__ */ new Map();
  record.set(version, oldReturnType);
  record = new Map([...record.entries()].sort((a, b) => a[0].index - b[0].index));
  program.stateMap(VersioningStateKeys.returnTypeChangedFrom).set(op, record);
};
var $renamedFrom = (context, t, v, oldName) => {
  const { program } = context;
  const version = checkIsVersion(context.program, v, context.getArgumentTarget(0));
  if (!version) {
    return;
  }
  if (oldName === "") {
    reportDiagnostic(program, {
      code: "invalid-renamed-from-value",
      target: t
    });
  }
  const record = getRenamedFrom(program, t) ?? [];
  record.push({ version, oldName });
  record.sort((a, b) => a.version.index - b.version.index);
  program.stateMap(VersioningStateKeys.renamedFrom).set(t, record);
};
var $madeOptional = (context, t, v) => {
  const { program } = context;
  const version = checkIsVersion(context.program, v, context.getArgumentTarget(0));
  if (!version) {
    return;
  }
  program.stateMap(VersioningStateKeys.madeOptional).set(t, version);
};
var $madeRequired = (context, t, v) => {
  const { program } = context;
  const version = checkIsVersion(context.program, v, context.getArgumentTarget(0));
  if (!version) {
    return;
  }
  program.stateMap(VersioningStateKeys.madeRequired).set(t, version);
};
function getMadeRequiredOn(p, t) {
  return p.stateMap(VersioningStateKeys.madeRequired).get(t);
}
function getRenamedFrom(p, t) {
  return p.stateMap(VersioningStateKeys.renamedFrom).get(t);
}
function getRenamedFromVersions(p, t) {
  return getRenamedFrom(p, t)?.map((x) => x.version);
}
function getAddedOnVersions(p, t) {
  return p.stateMap(VersioningStateKeys.addedOn).get(t);
}
function getRemovedOnVersions(p, t) {
  return p.stateMap(VersioningStateKeys.removedOn).get(t);
}
function getMadeOptionalOn(p, t) {
  return p.stateMap(VersioningStateKeys.madeOptional).get(t);
}
var VersionMap = class {
  map = /* @__PURE__ */ new Map();
  constructor(namespace2, enumType) {
    let index = 0;
    for (const member of enumType.members.values()) {
      this.map.set(member, {
        name: member.name,
        value: member.value?.toString() ?? member.name,
        enumMember: member,
        index,
        namespace: namespace2
      });
      index++;
    }
  }
  getVersionForEnumMember(member) {
    return this.map.get(member);
  }
  getVersions() {
    return [...this.map.values()];
  }
  get size() {
    return this.map.size;
  }
};
var $versioned = (context, t, versions) => {
  context.program.stateMap(VersioningStateKeys.versions).set(t, new VersionMap(t, versions));
};
function getVersion(program, namespace2) {
  return program.stateMap(VersioningStateKeys.versions).get(namespace2);
}
function findVersionedNamespace(program, namespace2) {
  let current = namespace2;
  while (current) {
    if (program.stateMap(VersioningStateKeys.versions).has(current)) {
      return current;
    }
    current = current.namespace;
  }
  return void 0;
}
function $useDependency(context, target, ...versionRecords) {
  const versions = [];
  for (const record of versionRecords) {
    const ver = checkIsVersion(context.program, record, context.getArgumentTarget(0));
    if (ver) {
      versions.push(ver);
    }
  }
  if (target.kind === "Namespace") {
    let state = getNamespaceUseDependencyState(context.program, target);
    if (!state) {
      state = versions;
    } else {
      state.push(...versions);
    }
    context.program.stateMap(VersioningStateKeys.useDependencyNamespace).set(target, state);
  } else if (target.kind === "EnumMember") {
    const targetEnum = target.enum;
    let state = context.program.stateMap(VersioningStateKeys.useDependencyEnum).get(targetEnum);
    if (!state) {
      state = /* @__PURE__ */ new Map();
    }
    const currentVersions = state.get(target) ?? [];
    currentVersions.push(...versions);
    state.set(target, currentVersions);
    context.program.stateMap(VersioningStateKeys.useDependencyEnum).set(targetEnum, state);
  }
}
function getNamespaceUseDependencyState(program, target) {
  return program.stateMap(VersioningStateKeys.useDependencyNamespace).get(target);
}
function getUseDependencies(program, target, searchEnum = true) {
  const result = /* @__PURE__ */ new Map();
  if (target.kind === "Namespace") {
    let current = target;
    while (current) {
      const data = getNamespaceUseDependencyState(program, current);
      if (!data) {
        if (searchEnum) {
          const versions = getVersion(program, current)?.getVersions();
          if (versions?.length) {
            const enumDeps = getUseDependencies(program, versions[0].enumMember.enum);
            if (enumDeps) {
              return enumDeps;
            }
          }
        }
        current = current.namespace;
      } else {
        for (const v of data) {
          result.set(v.namespace, v);
        }
        return result;
      }
    }
    return void 0;
  } else if (target.kind === "Enum") {
    const data = program.stateMap(VersioningStateKeys.useDependencyEnum).get(target);
    if (!data) {
      return void 0;
    }
    const resolved = resolveVersionDependency(program, data);
    if (resolved instanceof Map) {
      for (const [enumVer, value] of resolved) {
        for (const val of value) {
          const targetNamespace = val.enumMember.enum.namespace;
          if (!targetNamespace) {
            reportDiagnostic(program, {
              code: "version-not-found",
              target: val.enumMember.enum,
              format: { version: val.enumMember.name, enumName: val.enumMember.enum.name }
            });
            return void 0;
          }
          let subMap = result.get(targetNamespace);
          if (subMap) {
            subMap.set(enumVer, val);
          } else {
            subMap = /* @__PURE__ */ new Map([[enumVer, val]]);
          }
          result.set(targetNamespace, subMap);
        }
      }
    }
  }
  return result;
}
function resolveVersionDependency(program, data) {
  if (!(data instanceof Map)) {
    return data;
  }
  const mapping = /* @__PURE__ */ new Map();
  for (const [key, value] of data) {
    const sourceVersion = getVersionForEnumMember(program, key);
    if (sourceVersion !== void 0) {
      mapping.set(sourceVersion, value);
    }
  }
  return mapping;
}

// src/typespec/core/packages/versioning/dist/src/validate.js
var validate_exports = {};
__export(validate_exports, {
  $onValidate: () => $onValidate
});
import { NoTarget, getNamespaceFullName as getNamespaceFullName2, getTypeName as getTypeName3, isTemplateInstance, isType, navigateProgram } from "@typespec/compiler";

// src/typespec/core/packages/versioning/dist/src/validate.codefix.js
import { getSourceLocation, getTypeName as getTypeName2 } from "@typespec/compiler";
function getVersionAdditionCodefixes(version, type, program, typeOptions) {
  if (typeof version === "string") {
    return getVersionAdditionCodeFixFromString(version, type, program, typeOptions);
  }
  return getVersionAdditionCodeFixFromVersion(version, type, typeOptions);
}
function getVersionAdditionCodeFixFromVersion(version, type, typeOptions) {
  if (type.node === void 0)
    return void 0;
  const enumMember = version.enumMember;
  const decoratorDeclaration = `@added(${enumMember.enum.name}.${enumMember.name})`;
  return [
    getDecorationAdditionCodeFix("add-version-to-type", decoratorDeclaration, getTypeName2(type, typeOptions), getSourceLocation(type.node))
  ];
}
function getVersionAdditionCodeFixFromString(version, type, program, typeOptions) {
  const targetVersion = getAllVersions(program, type)?.find((v) => v.value === version);
  if (targetVersion === void 0)
    return void 0;
  return getVersionAdditionCodeFixFromVersion(targetVersion, type, typeOptions);
}
function getVersionRemovalCodeFixes(version, type, program, typeOptions) {
  if (type.node === void 0)
    return void 0;
  const targetVersion = getAllVersions(program, type)?.find((v) => v.value === version);
  if (targetVersion === void 0)
    return;
  const enumMember = targetVersion.enumMember;
  const decoratorDeclaration = `@removed(${enumMember.enum.name}.${enumMember.name})`;
  return [
    getDecorationAdditionCodeFix("remove-version-from-type", decoratorDeclaration, getTypeName2(type, typeOptions), getSourceLocation(type.node))
  ];
}
function getDecorationAdditionCodeFix(id, decoratorDeclaration, typeName, location) {
  return {
    id,
    label: `Add '${decoratorDeclaration}' to '${typeName}'`,
    fix: (context) => {
      return context.prependText(location, `${decoratorDeclaration}
`);
    }
  };
}

// src/typespec/core/packages/versioning/dist/src/validate.js
function $onValidate(program) {
  const namespaceDependencies = /* @__PURE__ */ new Map();
  function addNamespaceDependency(source, target) {
    if (!target || !("namespace" in target) || !target.namespace) {
      return;
    }
    const set = namespaceDependencies.get(source) ?? /* @__PURE__ */ new Set();
    if (target.namespace !== source) {
      set.add(target.namespace);
    }
    namespaceDependencies.set(source, set);
  }
  navigateProgram(program, {
    model: (model) => {
      if (isTemplateInstance(model)) {
        return;
      }
      addNamespaceDependency(model.namespace, model.sourceModel);
      addNamespaceDependency(model.namespace, model.baseModel);
      for (const prop of model.properties.values()) {
        addNamespaceDependency(model.namespace, prop.type);
        validateTargetVersionCompatible(program, model, prop, {
          isTargetADependent: true
        });
        const typeChangedFrom = getTypeChangedFrom(program, prop);
        if (typeChangedFrom !== void 0) {
          validateMultiTypeReference(program, prop);
        } else {
          validateReference(program, prop, prop.type);
        }
        validateMadeOptional(program, prop);
        validateMadeRequired(program, prop);
      }
      validateVersionedPropertyNames(program, model);
    },
    union: (union) => {
      if (isTemplateInstance(union)) {
        return;
      }
      if (union.namespace === void 0) {
        return;
      }
      for (const variant of union.variants.values()) {
        addNamespaceDependency(union.namespace, variant.type);
      }
      validateVersionedPropertyNames(program, union);
    },
    operation: (op) => {
      if (isTemplateInstance(op)) {
        return;
      }
      const namespace2 = op.namespace ?? op.interface?.namespace;
      addNamespaceDependency(namespace2, op.sourceOperation);
      addNamespaceDependency(namespace2, op.returnType);
      if (op.interface) {
        validateTargetVersionCompatible(program, op.interface, op, { isTargetADependent: true });
      }
      validateReference(program, op, op.returnType);
      for (const sourceModel of op.parameters.sourceModels) {
        validateReference(program, op, sourceModel.model);
      }
      for (const prop of op.parameters.properties.values()) {
        validateTargetVersionCompatible(program, op, prop, {
          isTargetADependent: true
        });
        const typeChangedFrom = getTypeChangedFrom(program, prop);
        if (typeChangedFrom !== void 0) {
          validateMultiTypeReference(program, prop);
        } else {
          validateReference(program, [prop, op], prop.type);
        }
      }
    },
    interface: (iface) => {
      for (const source of iface.sourceInterfaces) {
        validateReference(program, iface, source);
      }
    },
    namespace: (namespace2) => {
      validateVersionEnumValuesUnique(program, namespace2);
      const versionedNamespace = findVersionedNamespace(program, namespace2);
      const dependencies = getVersionDependencies(program, namespace2);
      if (dependencies === void 0) {
        return;
      }
      for (const [dependencyNs, value] of dependencies.entries()) {
        if (versionedNamespace) {
          const usingUseDependency = getUseDependencies(program, namespace2, false) !== void 0;
          if (usingUseDependency) {
            reportDiagnostic(program, {
              code: "incompatible-versioned-namespace-use-dependency",
              target: namespace2
            });
          } else if (!(value instanceof Map)) {
            reportDiagnostic(program, {
              code: "versioned-dependency-record-not-mapping",
              format: { dependency: getNamespaceFullName2(dependencyNs) },
              target: namespace2
            });
          }
        } else {
          if (value instanceof Map) {
            reportDiagnostic(program, {
              code: "versioned-dependency-not-picked",
              format: { dependency: getNamespaceFullName2(dependencyNs) },
              target: namespace2
            });
          }
        }
      }
    },
    enum: (en) => {
      validateVersionedPropertyNames(program, en);
      const useDependencies = getUseDependencies(program, en);
      if (!useDependencies) {
        return;
      }
      for (const [depNs, deps] of useDependencies) {
        const set = /* @__PURE__ */ new Set();
        if (deps instanceof Map) {
          for (const val of deps.values()) {
            set.add(val.namespace);
          }
        } else {
          set.add(deps.namespace);
        }
        namespaceDependencies.set(depNs, set);
      }
    }
  }, { includeTemplateDeclaration: true });
  validateVersionedNamespaceUsage(program, namespaceDependencies);
}
function validateMultiTypeReference(program, source, options) {
  const versionTypeMap = getVersionedTypeMap(program, source);
  if (versionTypeMap === void 0)
    return;
  for (const [version, type] of versionTypeMap) {
    if (type === void 0)
      continue;
    validateTypeAvailability(program, version, type, source, options);
  }
}
function validateTypeAvailability(program, version, targetType, source, options) {
  const typesToCheck = [targetType];
  while (typesToCheck.length) {
    const type = typesToCheck.pop();
    const availMap = getAvailabilityMap(program, type);
    const availability = availMap?.get(version?.name) ?? Availability.Available;
    if (![Availability.Added, Availability.Available].includes(availability)) {
      reportDiagnostic(program, {
        code: "incompatible-versioned-reference",
        messageId: "doesNotExist",
        format: {
          sourceName: getTypeName3(source, options),
          targetName: getTypeName3(type, options),
          version: prettyVersion(version)
        },
        target: source,
        codefixes: getVersionAdditionCodefixes(version, type, program, options)
      });
    }
    if (isTemplateInstance(type)) {
      for (const arg of type.templateMapper.args) {
        if (isType(arg)) {
          typesToCheck.push(arg);
        }
      }
    } else if (type.kind === "Union") {
      for (const variant of type.variants.values()) {
        if (type.expression) {
          typesToCheck.push(variant.type);
        } else {
          validateTargetVersionCompatible(program, variant, variant.type);
        }
      }
    } else if (type.kind === "Tuple") {
      for (const value of type.values) {
        typesToCheck.push(value);
      }
    }
  }
}
function getVersionedNameMap(program, source) {
  const allVersions = getAllVersions(program, source);
  if (allVersions === void 0)
    return void 0;
  const map = new Map(allVersions.map((v) => [v, void 0]));
  const availMap = getAvailabilityMap(program, source);
  const alwaysAvail = availMap === void 0;
  const renamedFrom = getRenamedFrom(program, source);
  if (renamedFrom !== void 0) {
    for (const rename of renamedFrom) {
      const version = rename.version;
      const oldName = rename.oldName;
      const versionIndex = allVersions.indexOf(version);
      if (versionIndex !== -1) {
        map.set(allVersions[versionIndex - 1], oldName);
      }
    }
  }
  let lastName = void 0;
  switch (source.kind) {
    case "ModelProperty":
      lastName = source.name;
      break;
    case "UnionVariant":
      if (typeof source.name === "string") {
        lastName = source.name;
      }
      break;
    case "EnumMember":
      lastName = source.name;
      break;
    default:
      throw new Error(`Not implemented '${source.kind}'.`);
  }
  for (const version of allVersions.reverse()) {
    const isAvail = alwaysAvail || [Availability.Added, Availability.Available].includes(availMap.get(version.name));
    if (!isAvail) {
      map.set(version, void 0);
      continue;
    }
    const mapType = map.get(version);
    if (mapType !== void 0) {
      lastName = mapType;
    } else {
      map.set(version, lastName);
    }
  }
  return map;
}
function getVersionedTypeMap(program, source) {
  const allVersions = getAllVersions(program, source);
  if (allVersions === void 0)
    return void 0;
  const map = new Map(allVersions.map((v) => [v, void 0]));
  const availMap = getAvailabilityMap(program, source);
  const alwaysAvail = availMap === void 0;
  const typeChangedFrom = getTypeChangedFrom(program, source);
  if (typeChangedFrom !== void 0) {
    for (const [version, type] of typeChangedFrom) {
      const versionIndex = allVersions.indexOf(version);
      if (versionIndex !== -1) {
        map.set(allVersions[versionIndex - 1], type);
      }
    }
  }
  let lastType = void 0;
  switch (source.kind) {
    case "ModelProperty":
      lastType = source.type;
      break;
    default:
      throw new Error(`Not implemented '${source.kind}'.`);
  }
  for (const version of allVersions.reverse()) {
    const isAvail = alwaysAvail || [Availability.Added, Availability.Available].includes(availMap.get(version.name));
    if (!isAvail) {
      map.set(version, void 0);
      continue;
    }
    const mapType = map.get(version);
    if (mapType !== void 0) {
      lastType = mapType;
    } else {
      map.set(version, lastType);
    }
  }
  return map;
}
function validateVersionEnumValuesUnique(program, namespace2) {
  const [_, versionMap] = getVersions(program, namespace2);
  if (versionMap === void 0)
    return;
  const values = new Set(versionMap.getVersions().map((v) => v.value));
  if (versionMap.size !== values.size) {
    const enumName = versionMap.getVersions()[0].enumMember.enum.name;
    reportDiagnostic(program, {
      code: "version-duplicate",
      format: { name: enumName },
      target: namespace2
    });
  }
}
function validateVersionedNamespaceUsage(program, namespaceDependencies) {
  for (const [source, targets] of namespaceDependencies.entries()) {
    const dependencies = source && getVersionDependencies(program, source);
    for (const target of targets) {
      const targetVersionedNamespace = findVersionedNamespace(program, target);
      const sourceVersionedNamespace = source && findVersionedNamespace(program, source);
      if (targetVersionedNamespace !== void 0 && !(source && (isSubNamespace(target, source) || isSubNamespace(source, target))) && sourceVersionedNamespace !== targetVersionedNamespace && dependencies?.get(targetVersionedNamespace) === void 0) {
        reportDiagnostic(program, {
          code: "using-versioned-library",
          format: {
            sourceNs: source ? getNamespaceFullName2(source) : "global",
            targetNs: getNamespaceFullName2(target)
          },
          target: source ?? NoTarget
        });
      }
    }
  }
}
function validateVersionedPropertyNames(program, source) {
  const allVersions = getAllVersions(program, source);
  if (allVersions === void 0)
    return;
  const versionedNameMap = new Map(allVersions.map((v) => [v, []]));
  let values = [];
  if (source.kind === "Model") {
    values = source.properties.values();
  } else if (source.kind === "Enum") {
    values = source.members.values();
  } else if (source.kind === "Union") {
    values = source.variants.values();
  }
  for (const value of values) {
    const nameMap = getVersionedNameMap(program, value);
    if (nameMap === void 0)
      continue;
    for (const [version, name] of nameMap) {
      if (name === void 0)
        continue;
      versionedNameMap.get(version)?.push(name);
    }
  }
  for (const [version, names] of versionedNameMap.entries()) {
    const nameCounts = /* @__PURE__ */ new Map();
    for (const name of names) {
      const count = nameCounts.get(name) ?? 0;
      nameCounts.set(name, count + 1);
    }
    for (const [name, count] of nameCounts.entries()) {
      if (name === void 0)
        continue;
      if (count > 1) {
        reportDiagnostic(program, {
          code: "renamed-duplicate-property",
          format: {
            name,
            version: prettyVersion(version)
          },
          target: source
        });
      }
    }
  }
}
function isSubNamespace(parent, child) {
  let current = child;
  while (current && current.name !== "") {
    if (current === parent) {
      return true;
    }
    current = current.namespace;
  }
  return false;
}
function validateMadeOptional(program, target) {
  if (target.kind === "ModelProperty") {
    const madeOptionalOn = getMadeOptionalOn(program, target);
    if (!madeOptionalOn) {
      return;
    }
    if (!target.optional) {
      reportDiagnostic(program, {
        code: "made-optional-not-optional",
        format: {
          name: target.name
        },
        target
      });
      return;
    }
  }
}
function validateMadeRequired(program, target) {
  if (target.kind === "ModelProperty") {
    const madeRequiredOn = getMadeRequiredOn(program, target);
    if (!madeRequiredOn) {
      return;
    }
    if (target.optional) {
      reportDiagnostic(program, {
        code: "made-required-optional",
        format: {
          name: target.name
        },
        target
      });
      return;
    }
  }
}
function validateReference(program, source, target) {
  validateTargetVersionCompatible(program, source, target);
  if ("templateMapper" in target) {
    for (const param of target.templateMapper?.args ?? []) {
      if (isType(param)) {
        validateReference(program, source, param);
      }
    }
  }
  switch (target.kind) {
    case "Union":
      if (typeof target.name !== "string") {
        for (const variant of target.variants.values()) {
          validateReference(program, source, variant.type);
        }
      }
      break;
    case "Tuple":
      for (const value of target.values) {
        validateReference(program, source, value);
      }
      break;
  }
}
function resolveAvailabilityForStack(program, type) {
  const types = Array.isArray(type) ? type : [type];
  const first = types[0];
  const map = getAvailabilityMapFromStack(program, types);
  return { type: first, map };
}
function getAvailabilityMapFromStack(program, typeStack) {
  for (const type of typeStack) {
    const map = getAvailabilityMap(program, type);
    if (map) {
      return map;
    }
    switch (type.kind) {
      case "Operation": {
        const parentMap = type.interface && getAvailabilityMap(program, type.interface);
        if (parentMap) {
          return parentMap;
        }
        break;
      }
      case "ModelProperty": {
        const parentMap = type.model && getAvailabilityMap(program, type.model);
        if (parentMap) {
          return parentMap;
        }
        break;
      }
    }
  }
  return void 0;
}
function validateTargetVersionCompatible(program, source, target, validateOptions = {}) {
  const sourceAvailability = resolveAvailabilityForStack(program, source);
  const [sourceNamespace] = getVersions(program, sourceAvailability.type);
  if (sourceAvailability.map === void 0) {
    const sources = Array.isArray(source) ? source : [source];
    const baseNs = getVersions(program, sources[0]);
    for (const type of sources) {
      const ns = getVersions(program, type);
      if (ns !== baseNs) {
        return void 0;
      }
    }
  }
  const targetAvailability = resolveAvailabilityForStack(program, target);
  const [targetNamespace] = getVersions(program, targetAvailability.type);
  if (!targetAvailability.map || !targetNamespace)
    return;
  let versionMap;
  if (sourceNamespace !== targetNamespace) {
    const dependencies = sourceNamespace && getVersionDependencies(program, sourceNamespace);
    versionMap = dependencies?.get(targetNamespace);
    if (versionMap === void 0)
      return;
    targetAvailability.map = translateAvailability(program, targetAvailability.map, versionMap, sourceAvailability.type, targetAvailability.type);
    if (!targetAvailability.map) {
      return;
    }
  }
  if (validateOptions.isTargetADependent) {
    validateAvailabilityForContains(program, sourceAvailability.map, targetAvailability.map, sourceAvailability.type, targetAvailability.type);
  } else {
    validateAvailabilityForRef(program, sourceAvailability.map, targetAvailability.map, sourceAvailability.type, targetAvailability.type, versionMap instanceof Map ? versionMap : void 0);
  }
}
function translateAvailability(program, avail, versionMap, source, target) {
  if (!(versionMap instanceof Map)) {
    const version = versionMap;
    if ([Availability.Removed, Availability.Unavailable].includes(avail.get(version.name))) {
      const addedAfter = findAvailabilityAfterVersion(version.name, Availability.Added, avail);
      const removedBefore = findAvailabilityOnOrBeforeVersion(version.name, Availability.Removed, avail);
      if (addedAfter) {
        reportDiagnostic(program, {
          code: "incompatible-versioned-reference",
          messageId: "versionedDependencyAddedAfter",
          format: {
            sourceName: getTypeName3(source),
            targetName: getTypeName3(target),
            dependencyVersion: prettyVersion(version),
            targetAddedOn: addedAfter
          },
          target: source,
          codefixes: getVersionAdditionCodefixes(version, target, program)
        });
      }
      if (removedBefore) {
        reportDiagnostic(program, {
          code: "incompatible-versioned-reference",
          messageId: "versionedDependencyRemovedBefore",
          format: {
            sourceName: getTypeName3(source),
            targetName: getTypeName3(target),
            dependencyVersion: prettyVersion(version),
            targetAddedOn: removedBefore
          },
          target: source,
          codefixes: getVersionAdditionCodefixes(version, target, program)
        });
      }
    }
    return void 0;
  } else {
    const newAvail = /* @__PURE__ */ new Map();
    for (const [key, val] of versionMap) {
      const isAvail = avail.get(val.name);
      newAvail.set(key.name, isAvail);
    }
    return newAvail;
  }
}
function findAvailabilityAfterVersion(version, status, avail) {
  let search = false;
  for (const [key, val] of avail) {
    if (version === key) {
      search = true;
      continue;
    }
    if (!search)
      continue;
    if (val === status)
      return key;
  }
  return void 0;
}
function findAvailabilityOnOrBeforeVersion(version, status, avail) {
  let search = false;
  for (const [key, val] of avail) {
    if ([Availability.Added, Availability.Added].includes(val)) {
      search = true;
    }
    if (!search)
      continue;
    if (val === status) {
      return key;
    }
    if (key === version) {
      break;
    }
  }
  return void 0;
}
function validateAvailabilityForRef(program, sourceAvail, targetAvail, source, target, versionMap) {
  if (sourceAvail === void 0) {
    if (!isAvailableInAllVersion(targetAvail)) {
      const firstAvailableVersion = Array.from(targetAvail.entries()).filter(([_, val]) => val === Availability.Available || val === Availability.Added).map(([key, _]) => key).sort().shift();
      reportDiagnostic(program, {
        code: "incompatible-versioned-reference",
        messageId: "default",
        format: {
          sourceName: getTypeName3(source),
          targetName: getTypeName3(target)
        },
        target: source,
        codefixes: firstAvailableVersion ? getVersionAdditionCodefixes(firstAvailableVersion, source, program) : void 0
      });
    }
    return;
  }
  let keyValSource = [...sourceAvail.keys(), ...targetAvail.keys()];
  const sourceTypeChanged = getTypeChangedFrom(program, source);
  if (sourceTypeChanged !== void 0) {
    const sourceTypeChangedKeys = [...sourceTypeChanged.keys()].map((item) => item.name);
    keyValSource = [...keyValSource, ...sourceTypeChangedKeys];
  }
  const sourceReturnTypeChanged = getReturnTypeChangedFrom(program, source);
  if (sourceReturnTypeChanged !== void 0) {
    const sourceReturnTypeChangedKeys = [...sourceReturnTypeChanged.keys()].map((item) => item.name);
    keyValSource = [...keyValSource, ...sourceReturnTypeChangedKeys];
  }
  const keySet = new Set(keyValSource);
  for (const key of keySet) {
    const sourceVal = sourceAvail.get(key);
    const targetVal = targetAvail.get(key);
    if ([Availability.Added].includes(sourceVal) && [Availability.Removed, Availability.Unavailable].includes(targetVal)) {
      const targetAddedOn = findAvailabilityAfterVersion(key, Availability.Added, targetAvail);
      let targetVersion = key;
      if (versionMap) {
        targetVersion = findMatchingTargetVersion(key, versionMap) ?? key;
      }
      reportDiagnostic(program, {
        code: "incompatible-versioned-reference",
        messageId: "addedAfter",
        format: {
          sourceName: getTypeName3(source),
          targetName: getTypeName3(target),
          sourceAddedOn: key,
          targetAddedOn
        },
        target: source,
        codefixes: getVersionAdditionCodefixes(targetVersion, target, program)
      });
    }
    if ([Availability.Removed].includes(sourceVal) && [Availability.Unavailable].includes(targetVal)) {
      const targetRemovedOn = findAvailabilityOnOrBeforeVersion(key, Availability.Removed, targetAvail);
      let targetVersion = key;
      if (versionMap) {
        targetVersion = findMatchingTargetVersion(key, versionMap) ?? key;
      }
      reportDiagnostic(program, {
        code: "incompatible-versioned-reference",
        messageId: "removedBefore",
        format: {
          sourceName: getTypeName3(source),
          targetName: getTypeName3(target),
          sourceRemovedOn: key,
          targetRemovedOn
        },
        target: source,
        codefixes: getVersionAdditionCodefixes(targetVersion, target, program)
      });
    }
  }
}
function canIgnoreDependentVersioning(type, versioning) {
  if (type.kind === "ModelProperty") {
    return canIgnoreVersioningOnProperty(type, versioning);
  }
  return false;
}
function canIgnoreVersioningOnProperty(prop, versioning) {
  if (prop.sourceProperty === void 0) {
    return false;
  }
  const decoratorFn = versioning === "added" ? $added : $removed;
  const selfDecorators = prop.decorators.filter((x) => x.decorator === decoratorFn);
  const sourceDecorators = prop.sourceProperty.decorators.filter((x) => x.decorator === decoratorFn);
  return !selfDecorators.some((x) => !sourceDecorators.some((y) => x.node === y.node));
}
function validateAvailabilityForContains(program, sourceAvail, targetAvail, source, target, sourceOptions, targetOptions) {
  if (!sourceAvail)
    return;
  const keySet = /* @__PURE__ */ new Set([...sourceAvail.keys(), ...targetAvail.keys()]);
  for (const key of keySet) {
    const sourceVal = sourceAvail.get(key);
    const targetVal = targetAvail.get(key);
    if (sourceVal === targetVal)
      continue;
    if ([Availability.Added].includes(targetVal) && [Availability.Removed, Availability.Unavailable].includes(sourceVal) && !canIgnoreDependentVersioning(target, "added")) {
      const sourceAddedOn = findAvailabilityOnOrBeforeVersion(key, Availability.Added, sourceAvail);
      reportDiagnostic(program, {
        code: "incompatible-versioned-reference",
        messageId: "dependentAddedAfter",
        format: {
          sourceName: getTypeName3(source, sourceOptions),
          targetName: getTypeName3(target, targetOptions),
          sourceAddedOn,
          targetAddedOn: key
        },
        target,
        codefixes: getVersionAdditionCodefixes(key, source, program, targetOptions)
      });
    }
    if ([Availability.Removed].includes(sourceVal) && [Availability.Added, Availability.Available].includes(targetVal) && !canIgnoreDependentVersioning(target, "removed")) {
      const targetRemovedOn = findAvailabilityAfterVersion(key, Availability.Removed, targetAvail);
      reportDiagnostic(program, {
        code: "incompatible-versioned-reference",
        messageId: "dependentRemovedBefore",
        format: {
          sourceName: getTypeName3(source),
          targetName: getTypeName3(target),
          sourceRemovedOn: key,
          targetRemovedOn
        },
        target,
        codefixes: getVersionRemovalCodeFixes(key, target, program, targetOptions)
      });
    }
  }
}
function isAvailableInAllVersion(avail) {
  for (const val of avail.values()) {
    if ([Availability.Removed, Availability.Unavailable].includes(val))
      return false;
  }
  return true;
}
function prettyVersion(version) {
  return version?.value ?? "<n/a>";
}
function findMatchingTargetVersion(sourceVersion, versionMap) {
  for (const [source, target] of versionMap.entries()) {
    if (source.value === sourceVersion) {
      return target;
    }
  }
  return void 0;
}

// src/typespec/core/packages/versioning/dist/src/tsp-index.js
var $decorators = {
  "TypeSpec.Versioning": {
    versioned: $versioned,
    useDependency: $useDependency,
    added: $added,
    removed: $removed,
    renamedFrom: $renamedFrom,
    madeOptional: $madeOptional,
    madeRequired: $madeRequired,
    typeChangedFrom: $typeChangedFrom,
    returnTypeChangedFrom: $returnTypeChangedFrom
  }
};

// src/typespec/core/packages/versioning/dist/src/mutator.js
import {} from "@typespec/compiler/experimental";
function getVersioningMutators(program, namespace2) {
  const versions = resolveVersions(program, namespace2);
  const timeline = new VersioningTimeline(program, versions.map((x) => x.versions));
  const helper = new VersioningHelper(program, timeline);
  if (versions.length === 1 && versions[0].rootVersion === void 0 && versions[0].versions.size > 0) {
    return {
      kind: "transient",
      mutator: createVersionMutator(helper, timeline.get(versions[0].versions.values().next().value))
    };
  }
  const snapshots = versions.map((resolution) => {
    if (resolution.versions.size === 0) {
      return void 0;
    } else {
      return {
        version: resolution.rootVersion,
        mutator: createVersionMutator(helper, timeline.get(resolution.versions.values().next().value))
      };
    }
  }).filter((x) => x !== void 0);
  if (snapshots.length === 0) {
    return void 0;
  }
  return {
    kind: "versioned",
    snapshots
  };
}
function createVersionMutator(versioning, moment) {
  function deleteFromMap(map) {
    for (const [name, type] of map) {
      if (!versioning.existsAtVersion(type, moment)) {
        map.delete(name);
      }
    }
  }
  function deleteFromArray(array) {
    for (let i = array.length - 1; i >= 0; i--) {
      if (!versioning.existsAtVersion(array[i], moment)) {
        array.splice(i, 1);
      }
    }
  }
  function rename(original, type) {
    if (type.name !== void 0) {
      const nameAtVersion = versioning.getNameAtVersion(original, moment);
      if (nameAtVersion !== void 0 && nameAtVersion !== type.name) {
        type.name = nameAtVersion;
      }
    }
  }
  return {
    name: `VersionSnapshot ${moment.name}`,
    Namespace: {
      mutate: (original, clone, p, realm) => {
        deleteFromMap(clone.models);
        deleteFromMap(clone.operations);
        deleteFromMap(clone.interfaces);
        deleteFromMap(clone.enums);
        deleteFromMap(clone.unions);
        deleteFromMap(clone.namespaces);
        deleteFromMap(clone.scalars);
      }
    },
    Interface: (original, clone, p, realm) => {
      rename(original, clone);
      deleteFromMap(clone.operations);
    },
    Model: (original, clone, p, realm) => {
      rename(original, clone);
      deleteFromMap(clone.properties);
      deleteFromArray(clone.derivedModels);
    },
    Union: (original, clone, p, realm) => {
      rename(original, clone);
      deleteFromMap(clone.variants);
    },
    UnionVariant: (original, clone, p, realm) => {
      rename(original, clone);
    },
    Enum: (original, clone, p, realm) => {
      rename(original, clone);
      deleteFromMap(clone.members);
    },
    Scalar: (original, clone, p, realm) => {
      rename(original, clone);
      deleteFromArray(clone.derivedScalars);
    },
    EnumMember: (original, clone, p, realm) => {
      rename(original, clone);
    },
    Operation: (original, clone, p, realm) => {
      rename(original, clone);
      const returnTypeAtVersion = versioning.getReturnTypeAtVersion(original, moment);
      if (returnTypeAtVersion !== clone.returnType) {
        clone.returnType = returnTypeAtVersion;
      }
    },
    ModelProperty: (original, clone, p, realm) => {
      rename(original, clone);
      clone.optional = versioning.getOptionalAtVersion(original, moment);
      const typeAtVersion = versioning.getTypeAtVersion(original, moment);
      if (typeAtVersion !== clone.type) {
        clone.type = typeAtVersion;
      }
    }
  };
}
var VersioningHelper = class {
  #program;
  #timeline;
  constructor(program, timeline) {
    this.#program = program;
    this.#timeline = timeline;
  }
  existsAtVersion(type, moment) {
    const availability = getAvailabilityMapInTimeline(this.#program, type, this.#timeline);
    if (!availability)
      return true;
    const isAvail = availability.get(moment);
    return isAvail === Availability.Added || isAvail === Availability.Available;
  }
  getNameAtVersion(type, moment) {
    const allValues = getRenamedFrom(this.#program, type);
    if (!allValues)
      return type.name;
    for (const val of allValues) {
      if (this.#timeline.isBefore(moment, val.version)) {
        return val.oldName;
      }
    }
    return type.name;
  }
  getTypeAtVersion(type, moment) {
    const map = getTypeChangedFrom(this.#program, type);
    if (!map)
      return type.type;
    for (const [changedAtVersion, val] of map) {
      if (this.#timeline.isBefore(moment, changedAtVersion)) {
        return val;
      }
    }
    return type.type;
  }
  getReturnTypeAtVersion(type, moment) {
    const map = getReturnTypeChangedFrom(this.#program, type);
    if (!map)
      return type.returnType;
    for (const [changedAtVersion, val] of map) {
      if (this.#timeline.isBefore(moment, changedAtVersion)) {
        return val;
      }
    }
    return type.returnType;
  }
  getOptionalAtVersion(type, moment) {
    const optionalAt = getMadeOptionalOn(this.#program, type);
    const requiredAt = getMadeRequiredOn(this.#program, type);
    if (!optionalAt && !requiredAt)
      return type.optional;
    if (optionalAt) {
      if (this.#timeline.isBefore(moment, optionalAt)) {
        return false;
      } else {
        return true;
      }
    }
    if (requiredAt) {
      if (this.#timeline.isBefore(moment, requiredAt)) {
        return true;
      } else {
        return false;
      }
    }
    return type.optional;
  }
};

// virtual:virtual:entry.js
var TypeSpecJSSources = {
  "dist/src/index.js": src_exports,
  "dist/src/decorators.js": decorators_exports,
  "dist/src/validate.js": validate_exports
};
var TypeSpecSources = {
  "package.json": '{"name":"@typespec/versioning","version":"0.70.0","author":"Microsoft Corporation","description":"TypeSpec library for declaring and emitting versioned APIs","homepage":"https://typespec.io","readme":"https://github.com/microsoft/typespec/blob/main/README.md","license":"MIT","repository":{"type":"git","url":"git+https://github.com/microsoft/typespec.git"},"bugs":{"url":"https://github.com/microsoft/typespec/issues"},"keywords":["typespec"],"type":"module","main":"dist/src/index.js","tspMain":"lib/main.tsp","exports":{".":{"typespec":"./lib/main.tsp","types":"./dist/src/index.d.ts","default":"./dist/src/index.js"},"./testing":{"types":"./dist/src/testing/index.d.ts","default":"./dist/src/testing/index.js"}},"engines":{"node":">=20.0.0"},"scripts":{"clean":"rimraf ./dist ./temp","build":"pnpm gen-extern-signature && tsc -p . && pnpm lint-typespec-library","watch":"tsc -p . --watch","gen-extern-signature":"tspd --enable-experimental gen-extern-signature .","lint-typespec-library":"tsp compile . --warn-as-error --import @typespec/library-linter --no-emit","test":"vitest run","test:ui":"vitest --ui","test:ci":"vitest run --coverage --reporter=junit --reporter=default","lint":"eslint . --max-warnings=0","lint:fix":"eslint . --fix","regen-docs":"tspd doc .  --enable-experimental  --output-dir ../../website/src/content/docs/docs/libraries/versioning/reference"},"files":["lib/*.tsp","dist/**","!dist/test/**"],"peerDependencies":{"@typespec/compiler":"workspace:^"},"devDependencies":{"@types/node":"~22.13.11","@typespec/compiler":"workspace:^","@typespec/library-linter":"workspace:^","@typespec/tspd":"workspace:^","@vitest/coverage-v8":"^3.1.2","@vitest/ui":"^3.1.2","c8":"^10.1.3","rimraf":"~6.0.1","typescript":"~5.8.2","vitest":"^3.1.2"}}',
  "../compiler/lib/intrinsics.tsp": 'import "../dist/src/lib/intrinsic/tsp-index.js";\nimport "./prototypes.tsp";\n\n// This file contains all the intrinsic types of typespec. Everything here will always be loaded\nnamespace TypeSpec;\n\n/**\n * Represent a byte array\n */\nscalar bytes;\n\n/**\n * A numeric type\n */\nscalar numeric;\n\n/**\n * A whole number. This represent any `integer` value possible.\n * It is commonly represented as `BigInteger` in some languages.\n */\nscalar integer extends numeric;\n\n/**\n * A number with decimal value\n */\nscalar float extends numeric;\n\n/**\n * A 64-bit integer. (`-9,223,372,036,854,775,808` to `9,223,372,036,854,775,807`)\n */\nscalar int64 extends integer;\n\n/**\n * A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)\n */\nscalar int32 extends int64;\n\n/**\n * A 16-bit integer. (`-32,768` to `32,767`)\n */\nscalar int16 extends int32;\n\n/**\n * A 8-bit integer. (`-128` to `127`)\n */\nscalar int8 extends int16;\n\n/**\n * A 64-bit unsigned integer (`0` to `18,446,744,073,709,551,615`)\n */\nscalar uint64 extends integer;\n\n/**\n * A 32-bit unsigned integer (`0` to `4,294,967,295`)\n */\nscalar uint32 extends uint64;\n\n/**\n * A 16-bit unsigned integer (`0` to `65,535`)\n */\nscalar uint16 extends uint32;\n\n/**\n * A 8-bit unsigned integer (`0` to `255`)\n */\nscalar uint8 extends uint16;\n\n/**\n * An integer that can be serialized to JSON (`\u22129007199254740991 (\u2212(2^53 \u2212 1))` to `9007199254740991 (2^53 \u2212 1)` )\n */\nscalar safeint extends int64;\n\n/**\n * A 64 bit floating point number. (`\xB15.0 \xD7 10^\u2212324` to `\xB11.7 \xD7 10^308`)\n */\nscalar float64 extends float;\n\n/**\n * A 32 bit floating point number. (`\xB11.5 x 10^\u221245` to `\xB13.4 x 10^38`)\n */\nscalar float32 extends float64;\n\n/**\n * A decimal number with any length and precision. This represent any `decimal` value possible.\n * It is commonly represented as `BigDecimal` in some languages.\n */\nscalar decimal extends numeric;\n\n/**\n * A 128-bit decimal number.\n */\nscalar decimal128 extends decimal;\n\n/**\n * A sequence of textual characters.\n */\nscalar string;\n\n/**\n * A date on a calendar without a time zone, e.g. "April 10th"\n */\nscalar plainDate {\n  /**\n   * Create a plain date from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = plainTime.fromISO("2024-05-06");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * A time on a clock without a time zone, e.g. "3:00 am"\n */\nscalar plainTime {\n  /**\n   * Create a plain time from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = plainTime.fromISO("12:34");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * An instant in coordinated universal time (UTC)"\n */\nscalar utcDateTime {\n  /**\n   * Create a date from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = utcDateTime.fromISO("2024-05-06T12:20-12Z");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * A date and time in a particular time zone, e.g. "April 10th at 3:00am in PST"\n */\nscalar offsetDateTime {\n  /**\n   * Create a date from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = offsetDateTime.fromISO("2024-05-06T12:20-12-0700");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * A duration/time period. e.g 5s, 10h\n */\nscalar duration {\n  /**\n   * Create a duration from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = duration.fromISO("P1Y1D");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * Boolean with `true` and `false` values.\n */\nscalar boolean;\n\n/**\n * @dev Array model type, equivalent to `Element[]`\n * @template Element The type of the array elements\n */\n@indexer(integer, Element)\nmodel Array<Element> {}\n\n/**\n * @dev Model with string properties where all the properties have type `Property`\n * @template Element The type of the properties\n */\n@indexer(string, Element)\nmodel Record<Element> {}\n',
  "../compiler/lib/prototypes.tsp": "namespace TypeSpec.Prototypes;\n\nextern dec getter(target: unknown);\n\nnamespace Types {\n  interface ModelProperty {\n    @getter type(): unknown;\n  }\n\n  interface Operation {\n    @getter returnType(): unknown;\n    @getter parameters(): unknown;\n  }\n\n  interface Array<TElementType> {\n    @getter elementType(): TElementType;\n  }\n}\n",
  "../compiler/lib/std/main.tsp": '// TypeSpec standard library. Everything in here can be omitted by using `--nostdlib` cli flag or `nostdlib` in the config.\nimport "./types.tsp";\nimport "./decorators.tsp";\nimport "./reflection.tsp";\nimport "./visibility.tsp";\n',
  "../compiler/lib/std/types.tsp": 'namespace TypeSpec;\n\n/**\n * Represent a 32-bit unix timestamp datetime with 1s of granularity.\n * It measures time by the number of seconds that have elapsed since 00:00:00 UTC on 1 January 1970.\n */\n@encode("unixTimestamp", int32)\nscalar unixTimestamp32 extends utcDateTime;\n\n/**\n * Represent a URL string as described by https://url.spec.whatwg.org/\n */\nscalar url extends string;\n\n/**\n * Represents a collection of optional properties.\n *\n * @template Source An object whose spread properties are all optional.\n */\n@doc("The template for adding optional properties.")\n@withOptionalProperties\nmodel OptionalProperties<Source> {\n  ...Source;\n}\n\n/**\n * Represents a collection of updateable properties.\n *\n * @template Source An object whose spread properties are all updateable.\n */\n@doc("The template for adding updateable properties.")\n@withUpdateableProperties\nmodel UpdateableProperties<Source> {\n  ...Source;\n}\n\n/**\n * Represents a collection of omitted properties.\n *\n * @template Source An object whose properties are spread.\n * @template Keys The property keys to omit.\n */\n@doc("The template for omitting properties.")\n@withoutOmittedProperties(Keys)\nmodel OmitProperties<Source, Keys extends string> {\n  ...Source;\n}\n\n/**\n * Represents a collection of properties with only the specified keys included.\n *\n * @template Source An object whose properties are spread.\n * @template Keys The property keys to include.\n */\n@doc("The template for picking properties.")\n@withPickedProperties(Keys)\nmodel PickProperties<Source, Keys extends string> {\n  ...Source;\n}\n\n/**\n * Represents a collection of properties with default values omitted.\n *\n * @template Source An object whose spread property defaults are all omitted.\n */\n@withoutDefaultValues\nmodel OmitDefaults<Source> {\n  ...Source;\n}\n\n/**\n * Applies a visibility setting to a collection of properties.\n *\n * @template Source An object whose properties are spread.\n * @template Visibility The visibility to apply to all properties.\n */\n@doc("The template for setting the default visibility of key properties.")\n@withDefaultKeyVisibility(Visibility)\nmodel DefaultKeyVisibility<Source, Visibility extends valueof Reflection.EnumMember> {\n  ...Source;\n}\n',
  "../compiler/lib/std/decorators.tsp": 'import "../../dist/src/lib/tsp-index.js";\n\nusing TypeSpec.Reflection;\n\nnamespace TypeSpec;\n\n/**\n * Typically a short, single-line description.\n * @param summary Summary string.\n *\n * @example\n * ```typespec\n * @summary("This is a pet")\n * model Pet {}\n * ```\n */\nextern dec summary(target: unknown, summary: valueof string);\n\n/**\n * Attach a documentation string. Content support CommonMark markdown formatting.\n * @param doc Documentation string\n * @param formatArgs Record with key value pair that can be interpolated in the doc.\n *\n * @example\n * ```typespec\n * @doc("Represent a Pet available in the PetStore")\n * model Pet {}\n * ```\n */\nextern dec doc(target: unknown, doc: valueof string, formatArgs?: {});\n\n/**\n * Attach a documentation string to describe the successful return types of an operation.\n * If an operation returns a union of success and errors it only describes the success. See `@errorsDoc` for error documentation.\n * @param doc Documentation string\n *\n * @example\n * ```typespec\n * @returnsDoc("Returns doc")\n * op get(): Pet | NotFound;\n * ```\n */\nextern dec returnsDoc(target: Operation, doc: valueof string);\n\n/**\n * Attach a documentation string to describe the error return types of an operation.\n * If an operation returns a union of success and errors it only describes the errors. See `@returnsDoc` for success documentation.\n * @param doc Documentation string\n *\n * @example\n * ```typespec\n * @errorsDoc("Errors doc")\n * op get(): Pet | NotFound;\n * ```\n */\nextern dec errorsDoc(target: Operation, doc: valueof string);\n\n/**\n * Service options.\n */\nmodel ServiceOptions {\n  /**\n   * Title of the service.\n   */\n  title?: string;\n}\n\n/**\n * Mark this namespace as describing a service and configure service properties.\n * @param options Optional configuration for the service.\n *\n * @example\n * ```typespec\n * @service\n * namespace PetStore;\n * ```\n *\n * @example Setting service title\n * ```typespec\n * @service(#{title: "Pet store"})\n * namespace PetStore;\n * ```\n *\n * @example Setting service version\n * ```typespec\n * @service(#{version: "1.0"})\n * namespace PetStore;\n * ```\n */\nextern dec service(target: Namespace, options?: valueof ServiceOptions);\n\n/**\n * Specify that this model is an error type. Operations return error types when the operation has failed.\n *\n * @example\n * ```typespec\n * @error\n * model PetStoreError {\n *   code: string;\n *   message: string;\n * }\n * ```\n */\nextern dec error(target: Model);\n\n/**\n * Applies a media type hint to a TypeSpec type. Emitters and libraries may choose to use this hint to determine how a\n * type should be serialized. For example, the `@typespec/http` library will use the media type hint of the response\n * body type as a default `Content-Type` if one is not explicitly specified in the operation.\n *\n * Media types (also known as MIME types) are defined by RFC 6838. The media type hint should be a valid media type\n * string as defined by the RFC, but the decorator does not enforce or validate this constraint.\n *\n * Notes: the applied media type is _only_ a hint. It may be overridden or not used at all. Media type hints are\n * inherited by subtypes. If a media type hint is applied to a model, it will be inherited by all other models that\n * `extend` it unless they delcare their own media type hint.\n *\n * @param mediaType The media type hint to apply to the target type.\n *\n * @example create a model that serializes as XML by default\n *\n * ```tsp\n * @mediaTypeHint("application/xml")\n * model Example {\n *   @visibility(Lifecycle.Read)\n *   id: string;\n *\n *   name: string;\n * }\n * ```\n */\nextern dec mediaTypeHint(target: Model | Scalar | Enum | Union, mediaType: valueof string);\n\n// Cannot apply this to the scalar itself. Needs to be applied here so that we don\'t crash nostdlib scenarios\n@@mediaTypeHint(TypeSpec.bytes, "application/octet-stream");\n\n// @@mediaTypeHint(TypeSpec.string "text/plain") -- This is hardcoded in the compiler to avoid circularity\n// between the initialization of the string scalar and the `valueof string` required to call the\n// `mediaTypeHint` decorator.\n\n/**\n * Specify a known data format hint for this string type. For example `uuid`, `uri`, etc.\n * This differs from the `@pattern` decorator which is meant to specify a regular expression while `@format` accepts a known format name.\n * The format names are open ended and are left to emitter to interpret.\n *\n * @param format format name.\n *\n * @example\n * ```typespec\n * @format("uuid")\n * scalar uuid extends string;\n * ```\n */\nextern dec format(target: string | ModelProperty, format: valueof string);\n\n/**\n * Specify the the pattern this string should respect using simple regular expression syntax.\n * The following syntax is allowed: alternations (`|`), quantifiers (`?`, `*`, `+`, and `{ }`), wildcard (`.`), and grouping parentheses.\n * Advanced features like look-around, capture groups, and references are not supported.\n *\n * This decorator may optionally provide a custom validation _message_. Emitters may choose to use the message to provide\n * context when pattern validation fails. For the sake of consistency, the message should be a phrase that describes in\n * plain language what sort of content the pattern attempts to validate. For example, a complex regular expression that\n * validates a GUID string might have a message like "Must be a valid GUID."\n *\n * @param pattern Regular expression.\n * @param validationMessage Optional validation message that may provide context when validation fails.\n *\n * @example\n * ```typespec\n * @pattern("[a-z]+", "Must be a string consisting of only lower case letters and of at least one character.")\n * scalar LowerAlpha extends string;\n * ```\n */\nextern dec pattern(\n  target: string | bytes | ModelProperty,\n  pattern: valueof string,\n  validationMessage?: valueof string\n);\n\n/**\n * Specify the minimum length this string type should be.\n * @param value Minimum length\n *\n * @example\n * ```typespec\n * @minLength(2)\n * scalar Username extends string;\n * ```\n */\nextern dec minLength(target: string | ModelProperty, value: valueof integer);\n\n/**\n * Specify the maximum length this string type should be.\n * @param value Maximum length\n *\n * @example\n * ```typespec\n * @maxLength(20)\n * scalar Username extends string;\n * ```\n */\nextern dec maxLength(target: string | ModelProperty, value: valueof integer);\n\n/**\n * Specify the minimum number of items this array should have.\n * @param value Minimum number\n *\n * @example\n * ```typespec\n * @minItems(1)\n * model Endpoints is string[];\n * ```\n */\nextern dec minItems(target: unknown[] | ModelProperty, value: valueof integer);\n\n/**\n * Specify the maximum number of items this array should have.\n * @param value Maximum number\n *\n * @example\n * ```typespec\n * @maxItems(5)\n * model Endpoints is string[];\n * ```\n */\nextern dec maxItems(target: unknown[] | ModelProperty, value: valueof integer);\n\n/**\n * Specify the minimum value this numeric type should be.\n * @param value Minimum value\n *\n * @example\n * ```typespec\n * @minValue(18)\n * scalar Age is int32;\n * ```\n */\nextern dec minValue(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Specify the maximum value this numeric type should be.\n * @param value Maximum value\n *\n * @example\n * ```typespec\n * @maxValue(200)\n * scalar Age is int32;\n * ```\n */\nextern dec maxValue(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Specify the minimum value this numeric type should be, exclusive of the given\n * value.\n * @param value Minimum value\n *\n * @example\n * ```typespec\n * @minValueExclusive(0)\n * scalar distance is float64;\n * ```\n */\nextern dec minValueExclusive(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Specify the maximum value this numeric type should be, exclusive of the given\n * value.\n * @param value Maximum value\n *\n * @example\n * ```typespec\n * @maxValueExclusive(50)\n * scalar distance is float64;\n * ```\n */\nextern dec maxValueExclusive(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Mark this string as a secret value that should be treated carefully to avoid exposure\n *\n * @example\n * ```typespec\n * @secret\n * scalar Password is string;\n * ```\n */\nextern dec secret(target: string | ModelProperty);\n\n/**\n * Attaches a tag to an operation, interface, or namespace. Multiple `@tag` decorators can be specified to attach multiple tags to a TypeSpec element.\n * @param tag Tag value\n */\nextern dec tag(target: Namespace | Interface | Operation, tag: valueof string);\n\n/**\n * Specifies how a templated type should name their instances.\n * @param name name the template instance should take\n * @param formatArgs Model with key value used to interpolate the name\n *\n * @example\n * ```typespec\n * @friendlyName("{name}List", T)\n * model List<Item> {\n *   value: Item[];\n *   nextLink: string;\n * }\n * ```\n */\nextern dec friendlyName(target: unknown, name: valueof string, formatArgs?: unknown);\n\n/**\n * Mark a model property as the key to identify instances of that type\n * @param altName Name of the property. If not specified, the decorated property name is used.\n *\n * @example\n * ```typespec\n * model Pet {\n *   @key id: string;\n * }\n * ```\n */\nextern dec key(target: ModelProperty, altName?: valueof string);\n\n/**\n * Specify this operation is an overload of the given operation.\n * @param overloadbase Base operation that should be a union of all overloads\n *\n * @example\n * ```typespec\n * op upload(data: string | bytes, @header contentType: "text/plain" | "application/octet-stream"): void;\n * @overload(upload)\n * op uploadString(data: string, @header contentType: "text/plain" ): void;\n * @overload(upload)\n * op uploadBytes(data: bytes, @header contentType: "application/octet-stream"): void;\n * ```\n */\nextern dec overload(target: Operation, overloadbase: Operation);\n\n/**\n * Provide an alternative name for this type when serialized to the given mime type.\n * @param mimeType Mime type this should apply to. The mime type should be a known mime type as described here https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types without any suffix (e.g. `+json`)\n * @param name Alternative name\n *\n * @example\n *\n * ```typespec\n * model Certificate {\n *   @encodedName("application/json", "exp")\n *   @encodedName("application/xml", "expiry")\n *   expireAt: int32;\n * }\n * ```\n *\n * @example Invalid values\n *\n * ```typespec\n * @encodedName("application/merge-patch+json", "exp")\n *              ^ error cannot use subtype\n * ```\n */\nextern dec encodedName(target: unknown, mimeType: valueof string, name: valueof string);\n\n/**\n * Options for `@discriminated` decorator.\n */\nmodel DiscriminatedOptions {\n  /**\n   * How is the discriminated union serialized.\n   * @default object\n   */\n  envelope?: "object" | "none";\n\n  /** Name of the discriminator property */\n  discriminatorPropertyName?: string;\n\n  /** Name of the property envelopping the data */\n  envelopePropertyName?: string;\n}\n\n/**\n * Specify that this union is discriminated.\n * @param options Options to configure the serialization of the discriminated union.\n *\n * @example\n *\n * ```typespec\n * @discriminated\n * union Pet{ cat: Cat, dog: Dog }\n *\n * model Cat { name: string, meow: boolean }\n * model Dog { name: string, bark: boolean }\n * ```\n * Serialized as:\n * ```json\n * {\n *   "kind": "cat",\n *   "value": {\n *     "name": "Whiskers",\n *     "meow": true\n *   }\n * },\n * {\n *   "kind": "dog",\n *   "value": {\n *     "name": "Rex",\n *     "bark": false\n *   }\n * }\n * ```\n *\n * @example Custom property names\n *\n * ```typespec\n * @discriminated(#{discriminatorPropertyName: "dataKind", envelopePropertyName: "data"})\n * union Pet{ cat: Cat, dog: Dog }\n *\n * model Cat { name: string, meow: boolean }\n * model Dog { name: string, bark: boolean }\n * ```\n * Serialized as:\n * ```json\n * {\n *   "dataKind": "cat",\n *   "data": {\n *     "name": "Whiskers",\n *     "meow": true\n *   }\n * },\n * {\n *   "dataKind": "dog",\n *   "data": {\n *     "name": "Rex",\n *     "bark": false\n *   }\n * }\n * ```\n */\nextern dec discriminated(target: Union, options?: valueof DiscriminatedOptions);\n\n/**\n * Specify the property to be used to discriminate this type.\n * @param propertyName The property name to use for discrimination\n *\n * @example\n *\n * ```typespec\n * @discriminator("kind")\n * model Pet{ kind: string }\n *\n * model Cat extends Pet {kind: "cat", meow: boolean}\n * model Dog extends Pet  {kind: "dog", bark: boolean}\n * ```\n */\nextern dec discriminator(target: Model, propertyName: valueof string);\n\n/**\n * Known encoding to use on utcDateTime or offsetDateTime\n */\nenum DateTimeKnownEncoding {\n  /**\n   * RFC 3339 standard. https://www.ietf.org/rfc/rfc3339.txt\n   * Encode to string.\n   */\n  rfc3339: "rfc3339",\n\n  /**\n   * RFC 7231 standard. https://www.ietf.org/rfc/rfc7231.txt\n   * Encode to string.\n   */\n  rfc7231: "rfc7231",\n\n  /**\n   * Encode a datetime to a unix timestamp.\n   * Unix timestamps are represented as an integer number of seconds since the Unix epoch and usually encoded as an int32.\n   */\n  unixTimestamp: "unixTimestamp",\n}\n\n/**\n * Known encoding to use on duration\n */\nenum DurationKnownEncoding {\n  /**\n   * ISO8601 duration\n   */\n  ISO8601: "ISO8601",\n\n  /**\n   * Encode to integer or float\n   */\n  seconds: "seconds",\n}\n\n/**\n * Known encoding to use on bytes\n */\nenum BytesKnownEncoding {\n  /**\n   * Encode to Base64\n   */\n  base64: "base64",\n\n  /**\n   * Encode to Base64 Url\n   */\n  base64url: "base64url",\n}\n\n/**\n * Encoding for serializing arrays\n */\nenum ArrayEncoding {\n  /** Each values of the array is separated by a | */\n  pipeDelimited,\n\n  /** Each values of the array is separated by a <space> */\n  spaceDelimited,\n}\n\n/**\n * Specify how to encode the target type.\n * @param encodingOrEncodeAs Known name of an encoding or a scalar type to encode as(Only for numeric types to encode as string).\n * @param encodedAs What target type is this being encoded as. Default to string.\n *\n * @example offsetDateTime encoded with rfc7231\n *\n * ```tsp\n * @encode("rfc7231")\n * scalar myDateTime extends offsetDateTime;\n * ```\n *\n * @example utcDateTime encoded with unixTimestamp\n *\n * ```tsp\n * @encode("unixTimestamp", int32)\n * scalar myDateTime extends unixTimestamp;\n * ```\n *\n * @example encode numeric type to string\n *\n * ```tsp\n * model Pet {\n *   @encode(string) id: int64;\n * }\n * ```\n */\nextern dec encode(\n  target: Scalar | ModelProperty,\n  encodingOrEncodeAs: (valueof string | EnumMember) | Scalar,\n  encodedAs?: Scalar\n);\n\n/** Options for example decorators */\nmodel ExampleOptions {\n  /** The title of the example */\n  title?: string;\n\n  /** Description of the example */\n  description?: string;\n}\n\n/**\n * Provide an example value for a data type.\n *\n * @param example Example value.\n * @param options Optional metadata for the example.\n *\n * @example\n *\n * ```tsp\n * @example(#{name: "Fluffy", age: 2})\n * model Pet {\n *  name: string;\n *  age: int32;\n * }\n * ```\n */\nextern dec example(\n  target: Model | Enum | Scalar | Union | ModelProperty | UnionVariant,\n  example: valueof unknown,\n  options?: valueof ExampleOptions\n);\n\n/**\n * Operation example configuration.\n */\nmodel OperationExample {\n  /** Example request body. */\n  parameters?: unknown;\n\n  /** Example response body. */\n  returnType?: unknown;\n}\n\n/**\n * Provide example values for an operation\'s parameters and corresponding return type.\n *\n * @param example Example value.\n * @param options Optional metadata for the example.\n *\n * @example\n *\n * ```tsp\n * @opExample(#{parameters: #{name: "Fluffy", age: 2}, returnType: #{name: "Fluffy", age: 2, id: "abc"})\n * op createPet(pet: Pet): Pet;\n * ```\n */\nextern dec opExample(\n  target: Operation,\n  example: valueof OperationExample,\n  options?: valueof ExampleOptions\n);\n\n/**\n * Returns the model with required properties removed.\n */\nextern dec withOptionalProperties(target: Model);\n\n/**\n * Returns the model with any default values removed.\n */\nextern dec withoutDefaultValues(target: Model);\n\n/**\n * Returns the model with the given properties omitted.\n * @param omit List of properties to omit\n */\nextern dec withoutOmittedProperties(target: Model, omit: string | Union);\n\n/**\n * Returns the model with only the given properties included.\n * @param pick List of properties to include\n */\nextern dec withPickedProperties(target: Model, pick: string | Union);\n\n//---------------------------------------------------------------------------\n// Paging\n//---------------------------------------------------------------------------\n\n/**\n * Mark this operation as a `list` operation that returns a paginated list of items.\n */\nextern dec list(target: Operation);\n\n/**\n * Pagination property defining the number of items to skip.\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@offset skip: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec offset(target: ModelProperty);\n\n/**\n * Pagination property defining the page index.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@pageIndex page: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec pageIndex(target: ModelProperty);\n\n/**\n * Specify the pagination parameter that controls the maximum number of items to include in a page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@pageIndex page: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec pageSize(target: ModelProperty);\n\n/**\n * Specify the the property that contains the array of page items.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@pageIndex page: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec pageItems(target: ModelProperty);\n\n/**\n * Pagination property defining the token to get to the next page.\n * It MUST be specified both on the request parameter and the response.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @continuationToken continuationToken: string;\n * }\n * @list op listPets(@continuationToken continuationToken: string): Page<Pet>;\n * ```\n */\nextern dec continuationToken(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the next page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec nextLink(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the previous page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec prevLink(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the first page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec firstLink(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the last page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec lastLink(target: ModelProperty);\n\n//---------------------------------------------------------------------------\n// Debugging\n//---------------------------------------------------------------------------\n\n/**\n * A debugging decorator used to inspect a type.\n * @param text Custom text to log\n */\nextern dec inspectType(target: unknown, text: valueof string);\n\n/**\n * A debugging decorator used to inspect a type name.\n * @param text Custom text to log\n */\nextern dec inspectTypeName(target: unknown, text: valueof string);\n',
  "../compiler/lib/std/reflection.tsp": "namespace TypeSpec.Reflection;\n\nmodel Enum {}\nmodel EnumMember {}\nmodel Interface {}\nmodel Model {}\nmodel ModelProperty {}\nmodel Namespace {}\nmodel Operation {}\nmodel Scalar {}\nmodel Union {}\nmodel UnionVariant {}\nmodel StringTemplate {}\n",
  "../compiler/lib/std/visibility.tsp": '// Copyright (c) Microsoft Corporation\n// Licensed under the MIT license.\n\nimport "../../dist/src/lib/tsp-index.js";\n\nusing TypeSpec.Reflection;\n\nnamespace TypeSpec;\n\n/**\n * Sets the visibility modifiers that are active on a property, indicating that it is only considered to be present\n * (or "visible") in contexts that select for the given modifiers.\n *\n * A property without any visibility settings applied for any visibility class (e.g. `Lifecycle`) is considered to have\n * the default visibility settings for that class.\n *\n * If visibility for the property has already been set for a visibility class (for example, using `@invisible` or\n * `@removeVisibility`), this decorator will **add** the specified visibility modifiers to the property.\n *\n * See: [Visibility](https://typespec.io/docs/language-basics/visibility)\n *\n * The `@typespec/http` library uses `Lifecycle` visibility to determine which properties are included in the request or\n * response bodies of HTTP operations. By default, it uses the following visibility settings:\n *\n * - For the return type of operations, properties are included if they have `Lifecycle.Read` visibility.\n * - For POST operation parameters, properties are included if they have `Lifecycle.Create` visibility.\n * - For PUT operation parameters, properties are included if they have `Lifecycle.Create` or `Lifecycle.Update` visibility.\n * - For PATCH operation parameters, properties are included if they have `Lifecycle.Update` visibility.\n * - For DELETE operation parameters, properties are included if they have `Lifecycle.Delete` visibility.\n * - For GET or HEAD operation parameters, properties are included if they have `Lifecycle.Query` visibility.\n *\n * By default, properties have all five Lifecycle visibility modifiers enabled, so a property is visible in all contexts\n * by default.\n *\n * The default settings may be overridden using the `@returnTypeVisibility` and `@parameterVisibility` decorators.\n *\n * See also: [Automatic visibility](https://typespec.io/docs/libraries/http/operations#automatic-visibility)\n *\n * @param visibilities List of visibilities which apply to this property.\n *\n * @example\n *\n * ```typespec\n * model Dog {\n *   // The service will generate an ID, so you don\'t need to send it.\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   // The service will store this secret name, but won\'t ever return it.\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   // The regular name has all vi\n *   name: string;\n * }\n * ```\n */\nextern dec visibility(target: ModelProperty, ...visibilities: valueof EnumMember[]);\n\n/**\n * Indicates that a property is not visible in the given visibility class.\n *\n * This decorator removes all active visibility modifiers from the property within\n * the given visibility class, making it invisible to any context that selects for\n * visibility modifiers within that class.\n *\n * @param visibilityClass The visibility class to make the property invisible within.\n *\n * @example\n * ```typespec\n * model Example {\n *   @invisible(Lifecycle)\n *   hidden_property: string;\n * }\n * ```\n */\nextern dec invisible(target: ModelProperty, visibilityClass: Enum);\n\n/**\n * Removes visibility modifiers from a property.\n *\n * If the visibility modifiers for a visibility class have not been initialized,\n * this decorator will use the default visibility modifiers for the visibility\n * class as the default modifier set.\n *\n * @param target The property to remove visibility from.\n * @param visibilities The visibility modifiers to remove from the target property.\n *\n * @example\n * ```typespec\n * model Example {\n *   // This property will have all Lifecycle visibilities except the Read\n *   // visibility, since it is removed.\n *   @removeVisibility(Lifecycle.Read)\n *   secret_property: string;\n * }\n * ```\n */\nextern dec removeVisibility(target: ModelProperty, ...visibilities: valueof EnumMember[]);\n\n/**\n * Removes properties that do not have at least one of the given visibility modifiers\n * active.\n *\n * If no visibility modifiers are supplied, this decorator has no effect.\n *\n * See also: [Automatic visibility](https://typespec.io/docs/libraries/http/operations#automatic-visibility)\n *\n * When using an emitter that applies visibility automatically, it is generally\n * not necessary to use this decorator.\n *\n * @param visibilities List of visibilities that apply to this property.\n *\n * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // The spread operator will copy all the properties of Dog into DogRead,\n * // and @withVisibility will then remove those that are not visible with\n * // create or update visibility.\n * //\n * // In this case, the id property is removed, and the name and secretName\n * // properties are kept.\n * @withVisibility(Lifecycle.Create, Lifecycle.Update)\n * model DogCreateOrUpdate {\n *   ...Dog;\n * }\n *\n * // In this case the id and name properties are kept and the secretName property\n * // is removed.\n * @withVisibility(Lifecycle.Read)\n * model DogRead {\n *   ...Dog;\n * }\n * ```\n */\nextern dec withVisibility(target: Model, ...visibilities: valueof EnumMember[]);\n\n/**\n * Set the visibility of key properties in a model if not already set.\n *\n * This will set the visibility modifiers of all key properties in the model if the visibility is not already _explicitly_ set,\n * but will not change the visibility of any properties that have visibility set _explicitly_, even if the visibility\n * is the same as the default visibility.\n *\n * Visibility may be set explicitly using any of the following decorators:\n *\n * - `@visibility`\n * - `@removeVisibility`\n * - `@invisible`\n *\n * @param visibility The desired default visibility value. If a key property already has visibility set, it will not be changed.\n */\nextern dec withDefaultKeyVisibility(target: Model, visibility: valueof EnumMember);\n\n/**\n * Declares the visibility constraint of the parameters of a given operation.\n *\n * A parameter or property nested within a parameter will be visible if it has _any_ of the visibilities\n * in the list.\n *\n * It is invalid to call this decorator with no visibility modifiers.\n *\n * @param visibilities List of visibility modifiers that apply to the parameters of this operation.\n */\nextern dec parameterVisibility(target: Operation, ...visibilities: valueof EnumMember[]);\n\n/**\n * Declares the visibility constraint of the return type of a given operation.\n *\n * A property within the return type of the operation will be visible if it has _any_ of the visibilities\n * in the list.\n *\n * It is invalid to call this decorator with no visibility modifiers.\n *\n * @param visibilities List of visibility modifiers that apply to the return type of this operation.\n */\nextern dec returnTypeVisibility(target: Operation, ...visibilities: valueof EnumMember[]);\n\n/**\n * Returns the model with non-updateable properties removed.\n */\nextern dec withUpdateableProperties(target: Model);\n\n/**\n * Declares the default visibility modifiers for a visibility class.\n *\n * The default modifiers are used when a property does not have any visibility decorators\n * applied to it.\n *\n * The modifiers passed to this decorator _MUST_ be members of the target Enum.\n *\n * @param visibilities the list of modifiers to use as the default visibility modifiers.\n */\nextern dec defaultVisibility(target: Enum, ...visibilities: valueof EnumMember[]);\n\n/**\n * A visibility class for resource lifecycle phases.\n *\n * These visibilities control whether a property is visible during the various phases of a resource\'s lifecycle.\n *\n * @example\n * ```typespec\n * model Dog {\n *  @visibility(Lifecycle.Read)\n *  id: int32;\n *\n *  @visibility(Lifecycle.Create, Lifecycle.Update)\n *  secretName: string;\n *\n *  name: string;\n * }\n * ```\n *\n * In this example, the `id` property is only visible during the read phase, and the `secretName` property is only visible\n * during the create and update phases. This means that the server will return the `id` property when returning a `Dog`,\n * but the client will not be able to set or update it. In contrast, the `secretName` property can be set when creating\n * or updating a `Dog`, but the server will never return it. The `name` property has no visibility modifiers and is\n * therefore visible in all phases.\n */\nenum Lifecycle {\n  /**\n   * The property is visible when a resource is being created.\n   */\n  Create,\n\n  /**\n   * The property is visible when a resource is being read.\n   */\n  Read,\n\n  /**\n   * The property is visible when a resource is being updated.\n   */\n  Update,\n\n  /**\n   * The property is visible when a resource is being deleted.\n   */\n  Delete,\n\n  /**\n   * The property is visible when a resource is being queried.\n   *\n   * In HTTP APIs, this visibility applies to parameters of GET or HEAD operations.\n   */\n  Query,\n}\n\n/**\n * A visibility filter, used to specify which properties should be included when\n * using the `withVisibilityFilter` decorator.\n *\n * The filter matches any property with ALL of the following:\n * - If the `any` key is present, the property must have at least one of the specified visibilities.\n * - If the `all` key is present, the property must have all of the specified visibilities.\n * - If the `none` key is present, the property must have none of the specified visibilities.\n */\nmodel VisibilityFilter {\n  any?: EnumMember[];\n  all?: EnumMember[];\n  none?: EnumMember[];\n}\n\n/**\n * Applies the given visibility filter to the properties of the target model.\n *\n * This transformation is recursive, so it will also apply the filter to any nested\n * or referenced models that are the types of any properties in the `target`.\n *\n * If a `nameTemplate` is provided, newly-created type instances will be named according\n * to the template. See the `@friendlyName` decorator for more information on the template\n * syntax. The transformed type is provided as the argument to the template.\n *\n * @param target The model to apply the visibility filter to.\n * @param filter The visibility filter to apply to the properties of the target model.\n * @param nameTemplate The name template to use when renaming new model instances.\n *\n * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   name: string;\n * }\n *\n * @withVisibilityFilter(#{ all: #[Lifecycle.Read] })\n * model DogRead {\n *  ...Dog\n * }\n * ```\n */\nextern dec withVisibilityFilter(\n  target: Model,\n  filter: valueof VisibilityFilter,\n  nameTemplate?: valueof string\n);\n\n/**\n * Transforms the `target` model to include only properties that are visible during the\n * "Update" lifecycle phase.\n *\n * Any nested models of optional properties will be transformed into the "CreateOrUpdate"\n * lifecycle phase instead of the "Update" lifecycle phase, so that nested models may be\n * fully updated.\n *\n * If a `nameTemplate` is provided, newly-created type instances will be named according\n * to the template. See the `@friendlyName` decorator for more information on the template\n * syntax. The transformed type is provided as the argument to the template.\n *\n * @param target The model to apply the transformation to.\n * @param nameTemplate The name template to use when renaming new model instances.\n *\n * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * @withLifecycleUpdate\n * model DogUpdate {\n *   ...Dog\n * }\n * ```\n */\nextern dec withLifecycleUpdate(target: Model, nameTemplate?: valueof string);\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Create" resource lifecycle phase.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Create` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   name: string;\n * }\n *\n * // This model has only the `name` field.\n * model CreateDog is Create<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Create] }, NameTemplate)\nmodel Create<T extends Reflection.Model, NameTemplate extends valueof string = "Create{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Read" resource lifecycle phase.\n *\n * The "Read" lifecycle phase is used for properties returned by operations that read data, like\n * HTTP GET operations.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Read` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // This model has the `id` and `name` fields, but not `secretName`.\n * model ReadDog is Read<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Read] }, NameTemplate)\nmodel Read<T extends Reflection.Model, NameTemplate extends valueof string = "Read{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Update" resource lifecycle phase.\n *\n * The "Update" lifecycle phase is used for properties passed as parameters to operations\n * that update data, like HTTP PATCH operations.\n *\n * This transformation will include only the properties that have the `Lifecycle.Update`\n * visibility modifier, and the types of all properties will be replaced with the\n * equivalent `CreateOrUpdate` transformation.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // This model will have the `secretName` and `name` fields, but not the `id` field.\n * model UpdateDog is Update<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withLifecycleUpdate(NameTemplate)\nmodel Update<T extends Reflection.Model, NameTemplate extends valueof string = "Update{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Create" or "Update" resource lifecycle phases.\n *\n * The "CreateOrUpdate" lifecycle phase is used by default for properties passed as parameters to operations\n * that can create _or_ update data, like HTTP PUT operations.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Create` or `Lifecycle.Update` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create)\n *   immutableSecret: string;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // This model will have the `immutableSecret`, `secretName`, and `name` fields, but not the `id` field.\n * model CreateOrUpdateDog is CreateOrUpdate<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ any: #[Lifecycle.Create, Lifecycle.Update] }, NameTemplate)\nmodel CreateOrUpdate<\n  T extends Reflection.Model,\n  NameTemplate extends valueof string = "CreateOrUpdate{name}"\n> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Delete" resource lifecycle phase.\n *\n * The "Delete" lifecycle phase is used for properties passed as parameters to operations\n * that delete data, like HTTP DELETE operations.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Delete` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   // Set when the Dog is removed from our data store. This happens when the\n *   // Dog is re-homed to a new owner.\n *   @visibility(Lifecycle.Delete)\n *   nextOwner: string;\n *\n *   name: string;\n * }\n *\n * // This model will have the `nextOwner` and `name` fields, but not the `id` field.\n * model DeleteDog is Delete<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Delete] }, NameTemplate)\nmodel Delete<T extends Reflection.Model, NameTemplate extends valueof string = "Delete{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Query" resource lifecycle phase.\n *\n * The "Query" lifecycle phase is used for properties passed as parameters to operations\n * that read data, like HTTP GET or HEAD operations. This should not be confused for\n * the `@query` decorator, which specifies that the property is transmitted in the\n * query string of an HTTP request.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Query` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   // When getting information for a Dog, you can set this field to true to include\n *   // some extra information about the Dog\'s pedigree that is normally not returned.\n *   // Alternatively, you could just use a separate option parameter to get this\n *   // information.\n *   @visibility(Lifecycle.Query)\n *   includePedigree?: boolean;\n *\n *   name: string;\n *\n *   // Only included if `includePedigree` is set to true in the request.\n *   @visibility(Lifecycle.Read)\n *   pedigree?: string;\n * }\n *\n * // This model will have the `includePedigree` and `name` fields, but not `id` or `pedigree`.\n * model QueryDog is Query<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Query] }, NameTemplate)\nmodel Query<T extends Reflection.Model, NameTemplate extends valueof string = "Query{name}"> {\n  ...T;\n}\n',
  "lib/main.tsp": 'import "./decorators.tsp";\nimport "../dist/src/validate.js";\n',
  "lib/decorators.tsp": 'import "../dist/src/decorators.js";\n\nusing TypeSpec.Reflection;\n\nnamespace TypeSpec.Versioning;\n\n/**\n * Identifies that the decorated namespace is versioned by the provided enum.\n * @param versions The enum that describes the supported versions.\n *\n * @example\n *\n * ```tsp\n * @versioned(Versions)\n * namespace MyService;\n * enum Versions {\n *   v1,\n *   v2,\n *   v3,\n * }\n * ```\n */\nextern dec versioned(target: Namespace, versions: Enum);\n\n/**\n * Identifies that a namespace or a given versioning enum member relies upon a versioned package.\n * @param versionRecords The dependent library version(s) for the target namespace or version.\n *\n * @example Select a single version of `MyLib` to use\n *\n * ```tsp\n * @useDependency(MyLib.Versions.v1_1)\n * namespace NonVersionedService;\n * ```\n *\n * @example Select which version of the library match to which version of the service.\n *\n * ```tsp\n * @versioned(Versions)\n * namespace MyService1;\n * enum Version {\n *   @useDependency(MyLib.Versions.v1_1) // V1 use lib v1_1\n *   v1,\n *   @useDependency(MyLib.Versions.v1_1) // V2 use lib v1_1\n *   v2,\n *   @useDependency(MyLib.Versions.v2) // V3 use lib v2\n *   v3,\n * }\n * ```\n */\nextern dec useDependency(target: EnumMember | Namespace, ...versionRecords: EnumMember[]);\n\n/**\n * Identifies when the target was added.\n * @param version The version that the target was added in.\n *\n * @example\n *\n * ```tsp\n * @added(Versions.v2)\n * op addedInV2(): void;\n *\n * @added(Versions.v2)\n * model AlsoAddedInV2 {}\n *\n * model Foo {\n *   name: string;\n *\n *   @added(Versions.v3)\n *   addedInV3: string;\n * }\n * ```\n */\nextern dec added(\n  target:\n    | Model\n    | ModelProperty\n    | Operation\n    | Enum\n    | EnumMember\n    | Union\n    | UnionVariant\n    | Scalar\n    | Interface,\n  version: EnumMember\n);\n\n/**\n * Identifies when the target was removed.\n * @param version The version that the target was removed in.\n *\n * @example\n * ```tsp\n * @removed(Versions.v2)\n * op removedInV2(): void;\n *\n * @removed(Versions.v2)\n * model AlsoRemovedInV2 {}\n *\n * model Foo {\n *   name: string;\n *\n *   @removed(Versions.v3)\n *   removedInV3: string;\n * }\n * ```\n */\nextern dec removed(\n  target:\n    | Model\n    | ModelProperty\n    | Operation\n    | Enum\n    | EnumMember\n    | Union\n    | UnionVariant\n    | Scalar\n    | Interface,\n  version: EnumMember\n);\n\n/**\n * Identifies when the target has been renamed.\n * @param version The version that the target was renamed in.\n * @param oldName The previous name of the target.\n *\n * @example\n * ```tsp\n * @renamedFrom(Versions.v2, "oldName")\n * op newName(): void;\n * ```\n */\nextern dec renamedFrom(\n  target:\n    | Model\n    | ModelProperty\n    | Operation\n    | Enum\n    | EnumMember\n    | Union\n    | UnionVariant\n    | Scalar\n    | Interface,\n  version: EnumMember,\n  oldName: valueof string\n);\n\n/**\n * Identifies when a target was made optional.\n * @param version The version that the target was made optional in.\n *\n * @example\n *\n * ```tsp\n * model Foo {\n *   name: string;\n *   @madeOptional(Versions.v2)\n *   nickname?: string;\n * }\n * ```\n */\nextern dec madeOptional(target: ModelProperty, version: EnumMember);\n\n/**\n * Identifies when a target was made required.\n * @param version The version that the target was made required in.\n *\n * @example\n *\n * ```tsp\n * model Foo {\n *   name: string;\n *   @madeRequired(Versions.v2)\n *   nickname: string;\n * }\n * ```\n */\nextern dec madeRequired(target: ModelProperty, version: EnumMember);\n\n/**\n * Identifies when the target type changed.\n * @param version The version that the target type changed in.\n * @param oldType The previous type of the target.\n */\nextern dec typeChangedFrom(target: ModelProperty, version: EnumMember, oldType: unknown);\n\n/**\n * Identifies when the target type changed.\n * @param version The version that the target type changed in.\n * @param oldType The previous type of the target.\n */\nextern dec returnTypeChangedFrom(target: Operation, version: EnumMember, oldType: unknown);\n'
};
var _TypeSpecLibrary_ = {
  jsSourceFiles: TypeSpecJSSources,
  typespecSourceFiles: TypeSpecSources
};
export {
  $added,
  $decorators,
  $madeOptional,
  $madeRequired,
  $onValidate,
  $removed,
  $renamedFrom,
  $returnTypeChangedFrom,
  $typeChangedFrom,
  $useDependency,
  $versioned,
  Availability,
  VersionMap,
  _TypeSpecLibrary_,
  createVersionMutator,
  findVersionedNamespace,
  getAddedOnVersions,
  getAllVersions,
  getAvailabilityMap,
  getAvailabilityMapInTimeline,
  getMadeOptionalOn,
  getRemovedOnVersions,
  getRenamedFrom,
  getRenamedFromVersions,
  getReturnTypeChangedFrom,
  getTypeChangedFrom,
  getUseDependencies,
  getVersion,
  getVersionDependencies,
  getVersionForEnumMember,
  getVersioningMutators,
  getVersions,
  getVersionsForEnum,
  resolveVersions
};
