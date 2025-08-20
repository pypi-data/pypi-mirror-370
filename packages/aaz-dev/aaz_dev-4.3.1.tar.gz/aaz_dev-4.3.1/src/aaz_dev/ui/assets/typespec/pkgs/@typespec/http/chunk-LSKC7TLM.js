import {
  HttpStateKeys,
  createDiagnostic,
  getMergePatchPropertySource,
  isMergePatch,
  reportDiagnostic
} from "./chunk-QJATEWBM.js";

// src/typespec/core/packages/http/dist/src/content-types.js
import { createDiagnosticCollector } from "@typespec/compiler";
function getContentTypes(property) {
  const diagnostics = createDiagnosticCollector();
  if (property.type.kind === "String") {
    return [[property.type.value], []];
  } else if (property.type.kind === "Union") {
    const contentTypes = [];
    for (const option of property.type.variants.values()) {
      if (option.type.kind === "String") {
        contentTypes.push(option.type.value);
      } else {
        diagnostics.add(createDiagnostic({
          code: "content-type-string",
          target: property
        }));
        continue;
      }
    }
    return diagnostics.wrap(contentTypes);
  } else if (property.type.kind === "Scalar" && property.type.name === "string") {
    return [["*/*"], []];
  }
  return [[], [createDiagnostic({ code: "content-type-string", target: property })]];
}

// src/typespec/core/packages/http/dist/src/private.decorators.js
import { NoTarget, getProperty, getTypeName, walkPropertiesInherited } from "@typespec/compiler";
import { SyntaxKind } from "@typespec/compiler/ast";
var $plainData = (context, entity) => {
  const { program } = context;
  const decoratorsToRemove = ["$header", "$body", "$query", "$path", "$statusCode"];
  const [headers, bodies, queries, paths, statusCodes] = [
    program.stateMap(HttpStateKeys.header),
    program.stateSet(HttpStateKeys.body),
    program.stateMap(HttpStateKeys.query),
    program.stateMap(HttpStateKeys.path),
    program.stateMap(HttpStateKeys.statusCode)
  ];
  for (const property of entity.properties.values()) {
    property.decorators = property.decorators.filter((d) => !decoratorsToRemove.includes(d.decorator.name));
    headers.delete(property);
    bodies.delete(property);
    queries.delete(property);
    paths.delete(property);
    statusCodes.delete(property);
  }
};
function getFileTemplateMetadata(target) {
  if (target.sourceModels.length)
    return;
  const templateMapper = target.templateMapper;
  if (!templateMapper || !templateMapper.args)
    return;
  const [contentTypeArg, contentsArg] = templateMapper.args;
  if (!contentTypeArg || !contentsArg)
    return;
  return { contentTypeArg, contentsArg, templateMapper: target.templateMapper };
}
function getFileDiagFormatName(t) {
  if (t?.entityKind === "Type") {
    return getTypeName(t, { printable: true });
  } else if (t?.type.kind === "String") {
    return `"${t.type.value}"`;
  }
  return;
}
var $httpFile = (context, target) => {
  const aliasModel = target.sourceModels.length > 0 ? target : void 0;
  const templateMetadata = getFileTemplateMetadata(target);
  const templateMapper = templateMetadata?.templateMapper;
  const contentType = target.properties.get("contentType").type;
  if (!(contentType.kind === "String" || // is string literal
  context.program.checker.isStdType(contentType, "string") || // is TypeSpec.string
  contentType.kind === "Union" && [...contentType.variants.values()].every((v) => v.type.kind === "String"))) {
    const contentTypeDiagnosticTarget = getTemplateArgumentTarget(templateMapper?.source, "ContentType", 0) ?? templateMetadata?.contentTypeArg;
    const contentTypeArg = templateMetadata?.contentTypeArg;
    const typeName = getFileDiagFormatName(contentTypeArg) ?? getFileDiagFormatName(contentType) ?? "<unknown>";
    reportDiagnostic(context.program, {
      code: "http-file-content-type-not-string",
      format: { type: typeName },
      target: contentTypeDiagnosticTarget ?? aliasModel ?? NoTarget
    });
  }
  const contents = target.properties.get("contents").type;
  if (contents.kind !== "Scalar") {
    const contentsArg = templateMetadata?.contentsArg;
    const contentsDiagnosticTarget = getTemplateArgumentTarget(templateMapper?.source, "Contents", 1) ?? contentsArg;
    const typeName = getFileDiagFormatName(contentsArg) ?? getFileDiagFormatName(contents) ?? "<unknown>";
    reportDiagnostic(context.program, {
      code: "http-file-contents-not-scalar",
      format: { type: typeName },
      target: contentsDiagnosticTarget ?? aliasModel ?? NoTarget
    });
  }
  context.program.stateSet(HttpStateKeys.file).add(target);
  function getTemplateArgumentTarget(source, name, argumentPosition) {
    if (source?.node.kind === SyntaxKind.TypeReference) {
      const argument = source.node.arguments.find((n) => n.name?.sv === name);
      if (argument)
        return argument;
      const templateNode = target.templateNode;
      const position = templateNode?.templateParameters.map((n, idx) => [idx, n]).find(([_, n]) => n.id.sv)?.[0] ?? argumentPosition;
      if (position === void 0)
        return void 0;
      return source.node.arguments[position];
    }
    return void 0;
  }
};
function isHttpFile(program, type) {
  return program.stateSet(HttpStateKeys.file).has(type);
}
function isOrExtendsHttpFile(program, type) {
  if (type.kind !== "Model") {
    return false;
  }
  let current = type;
  while (current) {
    if (isHttpFile(program, current)) {
      return true;
    }
    current = current.baseModel;
  }
  return false;
}
function getHttpFileModel(program, type, filter) {
  if (type.kind !== "Model")
    return void 0;
  const contentType = getProperty(type, "contentType");
  const filename = getProperty(type, "filename");
  const contents = getProperty(type, "contents");
  if (!contentType || !filename || !contents) {
    return void 0;
  }
  if (!propertyIsFromHttpFile(program, contentType) || !propertyIsFromHttpFile(program, filename) || !propertyIsFromHttpFile(program, contents)) {
    return void 0;
  }
  const effectiveProperties = new Set(walkPropertiesInherited(type));
  if (filter) {
    for (const prop of effectiveProperties) {
      if (!filter(prop)) {
        effectiveProperties.delete(prop);
      }
    }
  }
  if (effectiveProperties.size !== 3) {
    return void 0;
  }
  return { contents, contentType, filename, type };
}
function propertyIsFromHttpFile(program, property) {
  const isFile = property.model ? isOrExtendsHttpFile(program, property.model) : false;
  if (isFile)
    return true;
  if (property.sourceProperty) {
    return propertyIsFromHttpFile(program, property.sourceProperty);
  }
  return false;
}
var $httpPart = (context, target, type, options) => {
  context.program.stateMap(HttpStateKeys.httpPart).set(target, { type, options });
};
function getHttpPart(program, target) {
  return program.stateMap(HttpStateKeys.httpPart).get(target);
}
function $includeInapplicableMetadataInPayload(context, entity, value) {
  const state = context.program.stateMap(HttpStateKeys.includeInapplicableMetadataInPayload);
  state.set(entity, value);
}
function includeInapplicableMetadataInPayload(program, property) {
  let e;
  for (e = property; e; e = e.kind === "ModelProperty" ? e.model : e.namespace) {
    const value = program.stateMap(HttpStateKeys.includeInapplicableMetadataInPayload).get(e);
    if (value !== void 0) {
      return value;
    }
  }
  return true;
}

// src/typespec/core/packages/http/dist/src/responses.js
import { createDiagnosticCollector as createDiagnosticCollector9, getDoc as getDoc2, getErrorsDoc, getReturnsDoc, isErrorModel, isNullType, isVoidType } from "@typespec/compiler";
import { $ as $3 } from "@typespec/compiler/typekit";

// src/typespec/core/packages/http/dist/src/decorators.js
import { createDiagnosticCollector as createDiagnosticCollector8, getDoc, ignoreDiagnostics, typespecTypeToJson, validateDecoratorUniqueOnNode } from "@typespec/compiler";
import { SyntaxKind as SyntaxKind3 } from "@typespec/compiler/ast";
import { useStateMap } from "@typespec/compiler/utils";

// src/typespec/core/packages/http/dist/src/route.js
import { createDiagnosticCollector as createDiagnosticCollector6 } from "@typespec/compiler";

// src/typespec/core/packages/http/dist/src/parameters.js
import { createDiagnosticCollector as createDiagnosticCollector5 } from "@typespec/compiler";

// src/typespec/core/packages/http/dist/src/experimental/merge-patch/internal.js
import { $ } from "@typespec/compiler/typekit";
function isMergePatchBody(program, bodyType) {
  const _visitedTypes = /* @__PURE__ */ new WeakMap();
  function isMergePatchModel(type) {
    if (_visitedTypes.has(type))
      return false;
    _visitedTypes.set(bodyType, true);
    if (!$(program).model.is(type))
      return false;
    if (isMergePatch(program, type))
      return true;
    if ($(program).array.is(type) || $(program).record.is(type)) {
      return isMergePatchModel(type.indexer.value);
    }
    return false;
  }
  switch (bodyType.kind) {
    case "Model":
      return isMergePatchModel(bodyType) || bodyType.sourceModels.some((m) => isMergePatchModel(m.model)) || [...bodyType.properties.values()].some((p) => getMergePatchPropertySource(program, p) !== void 0 || isMergePatchModel(p.type));
    case "ModelProperty":
      return isMergePatchModel(bodyType.type);
    case "Union":
      return [...bodyType.variants.values()].some((v) => isMergePatchModel(v.type));
    case "UnionVariant":
      return isMergePatchModel(bodyType.type);
    case "Tuple":
      return bodyType.values.some((v) => isMergePatchModel(v));
    default:
      return false;
  }
}

// src/typespec/core/packages/http/dist/src/metadata.js
import { compilerAssert, getEffectiveModelType, getLifecycleVisibilityEnum, getParameterVisibilityFilter, isVisible as isVisibleCore } from "@typespec/compiler";
import { TwoLevelMap } from "@typespec/compiler/utils";

// src/typespec/core/packages/http/dist/src/operations.js
import { createDiagnosticCollector as createDiagnosticCollector2, getOverloadedOperation, getOverloads, listOperationsIn, listServices, navigateProgram } from "@typespec/compiler";

// src/typespec/core/packages/http/dist/src/auth.js
import { deepClone, deepEquals } from "@typespec/compiler/utils";
function getAuthenticationForOperation(program, operation) {
  const operationAuth = getAuthentication(program, operation);
  if (operationAuth) {
    return operationAuth;
  }
  if (operation.interface !== void 0) {
    const interfaceAuth = getAuthentication(program, operation.interface);
    if (interfaceAuth) {
      return interfaceAuth;
    }
  }
  let namespace = operation.namespace;
  while (namespace) {
    const namespaceAuth = getAuthentication(program, namespace);
    if (namespaceAuth) {
      return namespaceAuth;
    }
    namespace = namespace.namespace;
  }
  return void 0;
}
function resolveAuthentication(service) {
  let schemes = {};
  let defaultAuth = { options: [] };
  const operationsAuth = /* @__PURE__ */ new Map();
  if (service.authentication) {
    const { newServiceSchemes, authOptions } = gatherAuth(service.authentication, {});
    schemes = newServiceSchemes;
    defaultAuth = authOptions;
  }
  for (const op of service.operations) {
    if (op.authentication) {
      const { newServiceSchemes, authOptions } = gatherAuth(op.authentication, schemes);
      schemes = newServiceSchemes;
      operationsAuth.set(op.operation, authOptions);
    }
  }
  return { schemes: Object.values(schemes), defaultAuth, operationsAuth };
}
function gatherAuth(authentication, serviceSchemes) {
  const newServiceSchemes = serviceSchemes;
  const authOptions = { options: [] };
  for (const option of authentication.options) {
    const authOption = { all: [] };
    for (const optionScheme of option.schemes) {
      const serviceScheme = serviceSchemes[optionScheme.id];
      let newServiceScheme = optionScheme;
      if (serviceScheme) {
        if (!authsAreEqual(serviceScheme, optionScheme)) {
          while (serviceSchemes[newServiceScheme.id]) {
            newServiceScheme.id = newServiceScheme.id + "_";
          }
        } else if (serviceScheme.type === "oauth2" && optionScheme.type === "oauth2") {
          const x = mergeOAuthScopes(serviceScheme, optionScheme);
          newServiceScheme = x;
        }
      }
      const httpAuthRef = makeHttpAuthRef(optionScheme, newServiceScheme);
      newServiceSchemes[newServiceScheme.id] = newServiceScheme;
      authOption.all.push(httpAuthRef);
    }
    authOptions.options.push(authOption);
  }
  return { newServiceSchemes, authOptions };
}
function makeHttpAuthRef(local, reference) {
  if (reference.type === "oauth2" && local.type === "oauth2") {
    const scopes = [];
    for (const flow of local.flows) {
      scopes.push(...flow.scopes.map((x) => x.value));
    }
    return { kind: "oauth2", auth: reference, scopes };
  } else if (reference.type === "noAuth") {
    return { kind: "noAuth", auth: reference };
  } else {
    return { kind: "any", auth: reference };
  }
}
function mergeOAuthScopes(scheme1, scheme2) {
  const flows = deepClone(scheme1.flows);
  flows.forEach((flow1, i) => {
    const flow2 = scheme2.flows[i];
    const scopes = Array.from(new Set(flow1.scopes.concat(flow2.scopes)));
    flows[i].scopes = scopes;
  });
  return {
    ...scheme1,
    flows
  };
}
function ignoreScopes(scheme) {
  const flows = deepClone(scheme.flows);
  flows.forEach((flow) => {
    flow.scopes = [];
  });
  return {
    ...scheme,
    flows
  };
}
function authsAreEqual(scheme1, scheme2) {
  const { model: _model1, ...withoutModel1 } = scheme1;
  const { model: _model2, ...withoutModel2 } = scheme2;
  if (withoutModel1.type === "oauth2" && withoutModel2.type === "oauth2") {
    return deepEquals(ignoreScopes(withoutModel1), ignoreScopes(withoutModel2));
  }
  return deepEquals(withoutModel1, withoutModel2);
}

// src/typespec/core/packages/http/dist/src/operations.js
function getHttpOperation(program, operation, options) {
  return getHttpOperationInternal(program, operation, options, /* @__PURE__ */ new Map());
}
function listHttpOperationsIn(program, container, options) {
  const diagnostics = createDiagnosticCollector2();
  const operations = listOperationsIn(container, options?.listOptions);
  const cache = /* @__PURE__ */ new Map();
  const httpOperations = operations.map((x) => diagnostics.pipe(getHttpOperationInternal(program, x, options, cache)));
  return diagnostics.wrap(httpOperations);
}
function getAllHttpServices(program, options) {
  const diagnostics = createDiagnosticCollector2();
  const serviceNamespaces = listServices(program);
  const services = serviceNamespaces.map((x) => diagnostics.pipe(getHttpService(program, x.type, options)));
  if (serviceNamespaces.length === 0) {
    services.push(diagnostics.pipe(getHttpService(program, program.getGlobalNamespaceType(), options)));
  }
  return diagnostics.wrap(services);
}
function getHttpService(program, serviceNamespace, options) {
  const diagnostics = createDiagnosticCollector2();
  const httpOperations = diagnostics.pipe(listHttpOperationsIn(program, serviceNamespace, {
    ...options,
    listOptions: {
      recursive: serviceNamespace !== program.getGlobalNamespaceType()
    }
  }));
  const authentication = getAuthentication(program, serviceNamespace);
  validateRouteUnique(program, diagnostics, httpOperations);
  const service = {
    namespace: serviceNamespace,
    operations: httpOperations,
    authentication
  };
  return diagnostics.wrap(service);
}
function reportIfNoRoutes(program, routes) {
  if (routes.length === 0) {
    navigateProgram(program, {
      namespace: (namespace) => {
        if (namespace.operations.size > 0) {
          reportDiagnostic(program, {
            code: "no-service-found",
            format: {
              namespace: namespace.name
            },
            target: namespace
          });
        }
      }
    });
  }
}
function validateRouteUnique(program, diagnostics, operations) {
  const grouped = /* @__PURE__ */ new Map();
  for (const operation of operations) {
    const { verb, path } = operation;
    if (operation.overloading !== void 0 && isOverloadSameEndpoint(operation)) {
      continue;
    }
    if (isSharedRoute(program, operation.operation)) {
      continue;
    }
    let map = grouped.get(path);
    if (map === void 0) {
      map = /* @__PURE__ */ new Map();
      grouped.set(path, map);
    }
    let list = map.get(verb);
    if (list === void 0) {
      list = [];
      map.set(verb, list);
    }
    list.push(operation);
  }
  for (const [path, map] of grouped) {
    for (const [verb, routes] of map) {
      if (routes.length >= 2) {
        for (const route of routes) {
          diagnostics.add(createDiagnostic({
            code: "duplicate-operation",
            format: { path, verb, operationName: route.operation.name },
            target: route.operation
          }));
        }
      }
    }
  }
}
function isOverloadSameEndpoint(overload) {
  return overload.path === overload.overloading.path && overload.verb === overload.overloading.verb;
}
function getHttpOperationInternal(program, operation, options, cache) {
  const existing = cache.get(operation);
  if (existing) {
    return [existing, []];
  }
  const diagnostics = createDiagnosticCollector2();
  const httpOperationRef = { operation };
  cache.set(operation, httpOperationRef);
  const overloadBase = getOverloadedOperation(program, operation);
  let overloading;
  if (overloadBase) {
    overloading = httpOperationRef.overloading = diagnostics.pipe(getHttpOperationInternal(program, overloadBase, options, cache));
  }
  const route = diagnostics.pipe(resolvePathAndParameters(program, operation, overloading, options ?? {}));
  const responses = diagnostics.pipe(getResponsesForOperation(program, operation));
  const authentication = getAuthenticationForOperation(program, operation);
  const httpOperation = {
    path: route.path,
    uriTemplate: route.uriTemplate,
    verb: route.parameters.verb,
    container: operation.interface ?? operation.namespace ?? program.getGlobalNamespaceType(),
    parameters: route.parameters,
    responses,
    operation,
    authentication
  };
  Object.assign(httpOperationRef, httpOperation);
  const overloads = getOverloads(program, operation);
  if (overloads) {
    httpOperationRef.overloads = overloads.map((x) => diagnostics.pipe(getHttpOperationInternal(program, x, options, cache)));
  }
  return diagnostics.wrap(httpOperationRef);
}

// src/typespec/core/packages/http/dist/src/metadata.js
var Visibility;
(function(Visibility2) {
  Visibility2[Visibility2["Read"] = 1] = "Read";
  Visibility2[Visibility2["Create"] = 2] = "Create";
  Visibility2[Visibility2["Update"] = 4] = "Update";
  Visibility2[Visibility2["Delete"] = 8] = "Delete";
  Visibility2[Visibility2["Query"] = 16] = "Query";
  Visibility2[Visibility2["None"] = 0] = "None";
  Visibility2[Visibility2["All"] = 31] = "All";
  Visibility2[Visibility2["Item"] = 1048576] = "Item";
  Visibility2[Visibility2["Patch"] = 2097152] = "Patch";
  Visibility2[Visibility2["Synthetic"] = 3145728] = "Synthetic";
})(Visibility || (Visibility = {}));
var visibilityToArrayMap = /* @__PURE__ */ new Map();
function visibilityToArray(visibility) {
  visibility &= ~Visibility.Synthetic;
  let result = visibilityToArrayMap.get(visibility);
  if (!result) {
    result = [];
    if (visibility & Visibility.Read) {
      result.push("read");
    }
    if (visibility & Visibility.Create) {
      result.push("create");
    }
    if (visibility & Visibility.Update) {
      result.push("update");
    }
    if (visibility & Visibility.Delete) {
      result.push("delete");
    }
    if (visibility & Visibility.Query) {
      result.push("query");
    }
    compilerAssert(result.length > 0 || visibility === Visibility.None, "invalid visibility");
    visibilityToArrayMap.set(visibility, result);
  }
  return result;
}
function filterToVisibility(program, filter) {
  const Lifecycle = getLifecycleVisibilityEnum(program);
  compilerAssert(!filter.all, "Unexpected: `all` constraint in visibility filter passed to filterToVisibility");
  compilerAssert(!filter.none, "Unexpected: `none` constraint in visibility filter passed to filterToVisibility");
  if (!filter.any) {
    return Visibility.All;
  } else {
    let visibility = Visibility.None;
    for (const modifierConstraint of filter.any ?? []) {
      if (modifierConstraint.enum !== Lifecycle)
        continue;
      switch (modifierConstraint.name) {
        case "Read":
          visibility |= Visibility.Read;
          break;
        case "Create":
          visibility |= Visibility.Create;
          break;
        case "Update":
          visibility |= Visibility.Update;
          break;
        case "Delete":
          visibility |= Visibility.Delete;
          break;
        case "Query":
          visibility |= Visibility.Query;
          break;
        default:
          compilerAssert(false, `Unreachable: unrecognized Lifecycle visibility member: '${modifierConstraint.name}'`);
      }
    }
    return visibility;
  }
}
var VISIBILITY_FILTER_CACHE_MAP = /* @__PURE__ */ new WeakMap();
function getVisibilityFilterCache(program) {
  let cache = VISIBILITY_FILTER_CACHE_MAP.get(program);
  if (!cache) {
    cache = /* @__PURE__ */ new Map();
    VISIBILITY_FILTER_CACHE_MAP.set(program, cache);
  }
  return cache;
}
function visibilityToFilter(program, visibility) {
  visibility &= ~Visibility.Synthetic;
  if (visibility === Visibility.All)
    return {};
  const cache = getVisibilityFilterCache(program);
  let filter = cache.get(visibility);
  if (!filter) {
    const LifecycleEnum = getLifecycleVisibilityEnum(program);
    const Lifecycle = {
      Create: LifecycleEnum.members.get("Create"),
      Read: LifecycleEnum.members.get("Read"),
      Update: LifecycleEnum.members.get("Update"),
      Delete: LifecycleEnum.members.get("Delete"),
      Query: LifecycleEnum.members.get("Query")
    };
    const any = /* @__PURE__ */ new Set();
    if (visibility & Visibility.Read) {
      any.add(Lifecycle.Read);
    }
    if (visibility & Visibility.Create) {
      any.add(Lifecycle.Create);
    }
    if (visibility & Visibility.Update) {
      any.add(Lifecycle.Update);
    }
    if (visibility & Visibility.Delete) {
      any.add(Lifecycle.Delete);
    }
    if (visibility & Visibility.Query) {
      any.add(Lifecycle.Query);
    }
    compilerAssert(any.size > 0 || visibility === Visibility.None, "invalid visibility");
    filter = { any };
    cache.set(visibility, filter);
  }
  return filter;
}
function getVisibilitySuffix(visibility, canonicalVisibility = Visibility.All) {
  let suffix = "";
  if ((visibility & ~Visibility.Synthetic) !== canonicalVisibility) {
    const visibilities = visibilityToArray(visibility);
    suffix += visibilities.map((v) => v[0].toUpperCase() + v.slice(1)).join("Or");
  }
  if (visibility & Visibility.Item) {
    suffix += "Item";
  }
  return suffix;
}
function getDefaultVisibilityForVerb(verb) {
  switch (verb) {
    case "get":
    case "head":
      return Visibility.Query;
    case "post":
      return Visibility.Create;
    case "put":
      return Visibility.Create | Visibility.Update;
    case "patch":
      return Visibility.Update;
    case "delete":
      return Visibility.Delete;
    default:
      compilerAssert(false, `Unreachable: unrecognized HTTP verb: '${verb}'`);
  }
}
function HttpVisibilityProvider(verbOrParameterOptions) {
  const hasVerb = typeof verbOrParameterOptions === "string";
  return {
    parameters: (program, operation) => {
      let verb = hasVerb ? verbOrParameterOptions : verbOrParameterOptions?.verbSelector?.(program, operation) ?? getOperationVerb(program, operation);
      if (!verb) {
        const [httpOperation] = getHttpOperation(program, operation);
        verb = httpOperation.verb;
      }
      return visibilityToFilter(program, getDefaultVisibilityForVerb(verb));
    },
    returnType: (program, _) => {
      const Read = getLifecycleVisibilityEnum(program).members.get("Read");
      return { any: /* @__PURE__ */ new Set([Read]) };
    }
  };
}
function resolveRequestVisibility(program, operation, verb) {
  const parameterVisibilityFilter = getParameterVisibilityFilter(program, operation, HttpVisibilityProvider(verb));
  let visibility = filterToVisibility(program, parameterVisibilityFilter);
  if (verb === "patch") {
    const implicitOptionality = getPatchOptions(program, operation)?.implicitOptionality;
    if (implicitOptionality) {
      visibility |= Visibility.Patch;
    }
  }
  return visibility;
}
function isMetadata(program, property) {
  return isHeader(program, property) || isCookieParam(program, property) || isQueryParam(program, property) || isPathParam(program, property) || isStatusCode(program, property);
}
function isVisible(program, property, visibility) {
  return isVisibleCore(program, property, visibilityToFilter(program, visibility));
}
function isApplicableMetadata(program, property, visibility, isMetadataCallback = isMetadata) {
  return isApplicableMetadataCore(program, property, visibility, false, isMetadataCallback);
}
function isApplicableMetadataOrBody(program, property, visibility, isMetadataCallback = isMetadata) {
  return isApplicableMetadataCore(program, property, visibility, true, isMetadataCallback);
}
function isApplicableMetadataCore(program, property, visibility, treatBodyAsMetadata, isMetadataCallback) {
  if (visibility & Visibility.Item) {
    return false;
  }
  if (treatBodyAsMetadata && (isBody(program, property) || isBodyRoot(program, property) || isMultipartBodyProperty(program, property))) {
    return true;
  }
  if (!isMetadataCallback(program, property)) {
    return false;
  }
  if (visibility & Visibility.Read) {
    return isHeader(program, property) || isStatusCode(program, property);
  }
  if (!(visibility & Visibility.Read)) {
    return !isStatusCode(program, property);
  }
  return true;
}
function createMetadataInfo(program, options) {
  const canonicalVisibility = options?.canonicalVisibility ?? Visibility.All;
  const stateMap = new TwoLevelMap();
  return {
    isTransformed,
    isPayloadProperty,
    isOptional,
    getEffectivePayloadType
  };
  function isEmptied(type, visibility) {
    if (!type) {
      return false;
    }
    const state = getState(type, visibility);
    return state === 2;
  }
  function isTransformed(type, visibility) {
    if (!type) {
      return false;
    }
    const state = getState(type, visibility);
    switch (state) {
      case 1:
        return true;
      case 2:
        return visibility === canonicalVisibility || !isEmptied(type, canonicalVisibility);
      default:
        return false;
    }
  }
  function getState(type, visibility) {
    return stateMap.getOrAdd(
      type,
      visibility,
      () => computeState(type, visibility),
      3
      /* State.ComputationInProgress */
    );
  }
  function computeState(type, visibility) {
    switch (type.kind) {
      case "Model":
        return computeStateForModel(type, visibility);
      case "Union":
        return computeStateForUnion(type, visibility);
      default:
        return 0;
    }
  }
  function computeStateForModel(model, visibility) {
    if (computeIsEmptied(model, visibility)) {
      return 2;
    }
    if (isTransformed(model.indexer?.value, visibility | Visibility.Item) || isTransformed(model.baseModel, visibility)) {
      return 1;
    }
    for (const property of model.properties.values()) {
      if (isAddedRemovedOrMadeOptional(property, visibility) || isTransformed(property.type, visibility)) {
        return 1;
      }
    }
    return 0;
  }
  function computeStateForUnion(union, visibility) {
    for (const variant of union.variants.values()) {
      if (isTransformed(variant.type, visibility)) {
        return 1;
      }
    }
    return 0;
  }
  function isAddedRemovedOrMadeOptional(property, visibility) {
    if (visibility === canonicalVisibility) {
      return false;
    }
    if (isOptional(property, canonicalVisibility) !== isOptional(property, visibility)) {
      return true;
    }
    return isPayloadProperty(
      property,
      visibility,
      void 0,
      /* keep shared */
      true
    ) !== isPayloadProperty(
      property,
      canonicalVisibility,
      void 0,
      /*keep shared*/
      true
    );
  }
  function computeIsEmptied(model, visibility) {
    if (model.baseModel || model.indexer || model.properties.size === 0) {
      return false;
    }
    for (const property of model.properties.values()) {
      if (isPayloadProperty(
        property,
        visibility,
        void 0,
        /* keep shared */
        true
      )) {
        return false;
      }
    }
    return true;
  }
  function isOptional(property, visibility) {
    const hasUpdate = (visibility & Visibility.Update) !== 0;
    const isPatch = (visibility & Visibility.Patch) !== 0;
    const isItem = (visibility & Visibility.Item) !== 0;
    return property.optional || hasUpdate && isPatch && !isItem;
  }
  function isPayloadProperty(property, visibility, inExplicitBody, keepShareableProperties) {
    if (!inExplicitBody && (isBodyIgnore(program, property) || isApplicableMetadata(program, property, visibility) || isMetadata(program, property) && !includeInapplicableMetadataInPayload(program, property))) {
      return false;
    }
    if (!isVisible(program, property, visibility)) {
      keepShareableProperties ??= visibility === canonicalVisibility;
      return !!(keepShareableProperties && options?.canShareProperty?.(property));
    }
    return true;
  }
  function getEffectivePayloadType(type, visibility) {
    if (type.kind === "Model" && !type.name) {
      const effective = getEffectiveModelType(program, type, (p) => isPayloadProperty(
        p,
        visibility,
        void 0,
        /* keep shared */
        false
      ));
      if (effective.name) {
        return effective;
      }
    }
    return type;
  }
}

// src/typespec/core/packages/http/dist/src/payload.js
import { createDiagnosticCollector as createDiagnosticCollector4, filterModelProperties, getDiscriminator, getEncode, getMediaTypeHint, isArrayModelType, navigateType } from "@typespec/compiler";
import { SyntaxKind as SyntaxKind2 } from "@typespec/compiler/ast";
import { DuplicateTracker } from "@typespec/compiler/utils";

// src/typespec/core/packages/http/dist/src/http-property.js
import { compilerAssert as compilerAssert2, createDiagnosticCollector as createDiagnosticCollector3, walkPropertiesInherited as walkPropertiesInherited2 } from "@typespec/compiler";
function getHttpProperty(program, property, path, options = {}) {
  const diagnostics = [];
  function createResult(opts) {
    return [{ ...opts, property, path }, diagnostics];
  }
  const annotations = {
    header: getHeaderFieldOptions(program, property),
    cookie: getCookieParamOptions(program, property),
    query: getQueryOptions(program, property),
    path: getPathOptions(program, property),
    body: isBody(program, property),
    bodyRoot: isBodyRoot(program, property),
    multipartBody: isMultipartBodyProperty(program, property),
    statusCode: isStatusCode(program, property)
  };
  const defined = Object.entries(annotations).filter((x) => !!x[1]);
  const implicit = options.implicitParameter?.(property);
  if (implicit && defined.length > 0) {
    if (implicit.type === "path" && annotations.path) {
      if (annotations.path.explode !== void 0 || annotations.path.style !== void 0 || annotations.path.allowReserved !== void 0) {
        diagnostics.push(createDiagnostic({
          code: "use-uri-template",
          format: {
            param: property.name
          },
          target: property
        }));
      }
    } else if (implicit.type === "query" && annotations.query) {
      if (annotations.query.explode !== void 0) {
        diagnostics.push(createDiagnostic({
          code: "use-uri-template",
          format: {
            param: property.name
          },
          target: property
        }));
      }
    } else {
      diagnostics.push(createDiagnostic({
        code: "incompatible-uri-param",
        format: {
          param: property.name,
          uriKind: implicit.type,
          annotationKind: defined[0][0]
        },
        target: property
      }));
    }
  }
  if (implicit) {
    return createResult({
      kind: implicit.type,
      options: implicit,
      property
    });
  }
  if (defined.length === 0) {
    return createResult({ kind: "bodyProperty" });
  } else if (defined.length > 1) {
    diagnostics.push(createDiagnostic({
      code: "operation-param-duplicate-type",
      format: { paramName: property.name, types: defined.map((x) => x[0]).join(", ") },
      target: property
    }));
  }
  if (annotations.header) {
    if (annotations.header.name.toLowerCase() === "content-type") {
      return createResult({ kind: "contentType" });
    } else {
      return createResult({ kind: "header", options: annotations.header });
    }
  } else if (annotations.cookie) {
    return createResult({ kind: "cookie", options: annotations.cookie });
  } else if (annotations.query) {
    return createResult({
      kind: "query",
      options: resolveQueryOptionsWithDefaults(annotations.query)
    });
  } else if (annotations.path) {
    return createResult({
      kind: "path",
      options: resolvePathOptionsWithDefaults(annotations.path)
    });
  } else if (annotations.statusCode) {
    return createResult({ kind: "statusCode" });
  } else if (annotations.body) {
    return createResult({ kind: "body" });
  } else if (annotations.bodyRoot) {
    return createResult({ kind: "bodyRoot" });
  } else if (annotations.multipartBody) {
    return createResult({ kind: "multipartBody" });
  }
  compilerAssert2(false, `Unexpected http property type`);
}
function resolvePayloadProperties(program, type, visibility, disposition, options = {}) {
  const diagnostics = createDiagnosticCollector3();
  const httpProperties = /* @__PURE__ */ new Map();
  if (type.kind !== "Model" || type.properties.size === 0) {
    return diagnostics.wrap([]);
  }
  const visited = /* @__PURE__ */ new Set();
  function checkModel(model, path) {
    visited.add(model);
    let foundBody = false;
    let foundBodyProperty = false;
    for (const property of walkPropertiesInherited2(model)) {
      const propPath = [...path, property.name];
      if (!isVisible(program, property, visibility)) {
        continue;
      }
      let httpProperty = diagnostics.pipe(getHttpProperty(program, property, propPath, options));
      if (shouldTreatAsBodyProperty(httpProperty, disposition)) {
        httpProperty = { kind: "bodyProperty", property, path: propPath };
      }
      if (httpProperty.kind === "cookie" && disposition === HttpPayloadDisposition.Response) {
        diagnostics.add(createDiagnostic({
          code: "response-cookie-not-supported",
          target: property,
          format: { propName: property.name }
        }));
        continue;
      }
      if (httpProperty.kind === "body" || httpProperty.kind === "bodyRoot" || httpProperty.kind === "multipartBody") {
        foundBody = true;
      }
      if (!(httpProperty.kind === "body" || httpProperty.kind === "multipartBody") && isModelWithProperties(property.type) && !visited.has(property.type)) {
        if (checkModel(property.type, propPath)) {
          foundBody = true;
          continue;
        }
      }
      if (httpProperty.kind === "bodyProperty") {
        foundBodyProperty = true;
      }
      httpProperties.set(property, httpProperty);
    }
    return foundBody && !foundBodyProperty;
  }
  checkModel(type, []);
  return diagnostics.wrap([...httpProperties.values()]);
}
function isModelWithProperties(type) {
  return type.kind === "Model" && !type.indexer && type.properties.size > 0;
}
function shouldTreatAsBodyProperty(property, disposition) {
  switch (disposition) {
    case HttpPayloadDisposition.Request:
      return property.kind === "statusCode";
    case HttpPayloadDisposition.Response:
      return property.kind === "query" || property.kind === "path";
    case HttpPayloadDisposition.Multipart:
      return property.kind === "path" || property.kind === "query" || property.kind === "statusCode";
    default:
      void disposition;
      return false;
  }
}

// src/typespec/core/packages/http/dist/src/payload.js
var HttpPayloadDisposition;
(function(HttpPayloadDisposition2) {
  HttpPayloadDisposition2[HttpPayloadDisposition2["Request"] = 0] = "Request";
  HttpPayloadDisposition2[HttpPayloadDisposition2["Response"] = 1] = "Response";
  HttpPayloadDisposition2[HttpPayloadDisposition2["Multipart"] = 2] = "Multipart";
})(HttpPayloadDisposition || (HttpPayloadDisposition = {}));
function resolveHttpPayload(program, type, visibility, disposition, options = {}) {
  const diagnostics = createDiagnosticCollector4();
  const metadata = diagnostics.pipe(resolvePayloadProperties(program, type, visibility, disposition, options));
  const body = diagnostics.pipe(resolveBody(program, type, metadata, visibility, disposition));
  if (body) {
    if (body.contentTypes.some((x) => x.startsWith("multipart/")) && body.bodyKind !== "multipart") {
      diagnostics.add(createDiagnostic({
        code: "no-implicit-multipart",
        target: body.property ?? type
      }));
      return diagnostics.wrap({ body: void 0, metadata });
    }
  }
  return diagnostics.wrap({ body, metadata });
}
function resolveBody(program, requestOrResponseType, metadata, visibility, disposition) {
  const diagnostics = createDiagnosticCollector4();
  const contentTypeProperty = metadata.find((x) => x.kind === "contentType");
  const file = getHttpFileModel(program, requestOrResponseType, createHttpFileModelFilter(metadata));
  if (file !== void 0) {
    if (!contentTypeProperty) {
      return diagnostics.join(getFileBody(file));
    } else {
      const contentTypes = contentTypeProperty && diagnostics.pipe(getContentTypes(contentTypeProperty.property));
      reportDiagnostic(program, {
        code: "http-file-structured",
        format: {
          contentTypes: contentTypes.join(", ")
        },
        target: contentTypeProperty.property
      });
    }
  }
  if (requestOrResponseType.kind !== "Model" || isArrayModelType(program, requestOrResponseType)) {
    return diagnostics.wrap({
      bodyKind: "single",
      ...diagnostics.pipe(resolveContentTypesForBody(program, contentTypeProperty, requestOrResponseType)),
      type: requestOrResponseType,
      isExplicit: false,
      containsMetadataAnnotations: false
    });
  }
  const resolvedBody = diagnostics.pipe(resolveExplicitBodyProperty(program, metadata, contentTypeProperty, visibility, disposition));
  if (resolvedBody === void 0) {
    if (requestOrResponseType.baseModel || requestOrResponseType.indexer) {
      return diagnostics.wrap({
        bodyKind: "single",
        ...diagnostics.pipe(resolveContentTypesForBody(program, contentTypeProperty, requestOrResponseType)),
        type: requestOrResponseType,
        isExplicit: false,
        containsMetadataAnnotations: false
      });
    }
    if (requestOrResponseType.derivedModels.length > 0 && getDiscriminator(program, requestOrResponseType)) {
      return diagnostics.wrap({
        bodyKind: "single",
        ...diagnostics.pipe(resolveContentTypesForBody(program, contentTypeProperty, requestOrResponseType)),
        type: requestOrResponseType,
        isExplicit: false,
        containsMetadataAnnotations: false
      });
    }
  }
  const unannotatedProperties = filterModelProperties(program, requestOrResponseType, (p) => metadata.some((x) => x.property === p && x.kind === "bodyProperty"));
  if (unannotatedProperties.properties.size > 0) {
    if (resolvedBody === void 0) {
      return diagnostics.wrap({
        bodyKind: "single",
        ...diagnostics.pipe(resolveContentTypesForBody(program, contentTypeProperty, requestOrResponseType)),
        type: unannotatedProperties,
        isExplicit: false,
        containsMetadataAnnotations: false
      });
    } else {
      diagnostics.add(createDiagnostic({
        code: "duplicate-body",
        messageId: "bodyAndUnannotated",
        target: requestOrResponseType
      }));
    }
  }
  if (resolvedBody === void 0 && contentTypeProperty) {
    diagnostics.add(createDiagnostic({
      code: "content-type-ignored",
      target: contentTypeProperty.property
    }));
  }
  return diagnostics.wrap(resolvedBody);
}
function resolveExplicitBodyProperty(program, metadata, contentTypeProperty, visibility, disposition) {
  const diagnostics = createDiagnosticCollector4();
  let resolvedBody;
  const duplicateTracker = new DuplicateTracker();
  for (const item of metadata) {
    if (item.kind === "body" || item.kind === "bodyRoot" || item.kind === "multipartBody") {
      duplicateTracker.track("body", item.property);
    }
    switch (item.kind) {
      case "body":
      case "bodyRoot":
        let containsMetadataAnnotations = false;
        if (item.kind === "body") {
          const valid = diagnostics.pipe(validateBodyProperty(program, item.property, disposition));
          containsMetadataAnnotations = !valid;
        }
        const file = getHttpFileModel(program, item.property.type, createHttpFileModelFilter(metadata));
        const isFile = file !== void 0 && !contentTypeProperty;
        if (file && contentTypeProperty) {
          const contentTypes = diagnostics.pipe(getContentTypes(contentTypeProperty.property));
          reportDiagnostic(program, {
            code: "http-file-structured",
            format: {
              contentTypes: contentTypes.join(", ")
            },
            target: contentTypeProperty.property
          });
        }
        if (item.property.type.kind === "Union" && unionContainsFile(program, item.property.type)) {
          reportDiagnostic(program, {
            code: "http-file-structured",
            messageId: "union",
            target: item.property.node?.kind === SyntaxKind2.ModelProperty ? item.property.node.value : item.property
          });
        }
        resolvedBody ??= isFile ? diagnostics.pipe(getFileBody(file, item.property)) : {
          bodyKind: "single",
          ...diagnostics.pipe(resolveContentTypesForBody(program, contentTypeProperty, item.property.type)),
          type: item.property.type,
          isExplicit: item.kind === "body",
          containsMetadataAnnotations,
          property: item.property
        };
        break;
      case "multipartBody":
        resolvedBody = diagnostics.pipe(resolveMultiPartBody(program, item.property, contentTypeProperty, visibility));
        break;
    }
  }
  for (const [_, items] of duplicateTracker.entries()) {
    for (const prop of items) {
      diagnostics.add(createDiagnostic({
        code: "duplicate-body",
        target: prop
      }));
    }
  }
  return diagnostics.wrap(resolvedBody);
}
function unionContainsFile(program, u) {
  return unionContainsFileWorker(u);
  function unionContainsFileWorker(u2, visited = /* @__PURE__ */ new Set()) {
    if (visited.has(u2))
      return false;
    visited.add(u2);
    for (const { type } of u2.variants.values()) {
      if (!!getHttpFileModel(program, type) || type.kind === "Union" && unionContainsFileWorker(type, visited)) {
        return true;
      }
    }
    return false;
  }
}
function validateBodyProperty(program, property, disposition) {
  const diagnostics = createDiagnosticCollector4();
  navigateType(property.type, {
    modelProperty: (prop) => {
      const kind = isHeader(program, prop) ? "header" : (
        // also emit metadata-ignored for response cookie
        (disposition === HttpPayloadDisposition.Request || disposition === HttpPayloadDisposition.Response) && isCookieParam(program, prop) ? "cookie" : (disposition === HttpPayloadDisposition.Request || disposition === HttpPayloadDisposition.Multipart) && isQueryParam(program, prop) ? "query" : disposition === HttpPayloadDisposition.Request && isPathParam(program, prop) ? "path" : disposition === HttpPayloadDisposition.Response && isStatusCode(program, prop) ? "statusCode" : void 0
      );
      if (kind) {
        diagnostics.add(createDiagnostic({
          code: "metadata-ignored",
          format: { kind },
          target: prop
        }));
      }
    }
  }, {});
  return diagnostics.wrap(diagnostics.diagnostics.length === 0);
}
function resolveMultiPartBody(program, property, contentTypeProperty, visibility) {
  const diagnostics = createDiagnosticCollector4();
  const type = property.type;
  const contentTypes = contentTypeProperty && diagnostics.pipe(getContentTypes(contentTypeProperty.property));
  for (const contentType of contentTypes ?? []) {
    if (!multipartContentTypesValues.includes(contentType)) {
      diagnostics.add(createDiagnostic({
        code: "multipart-invalid-content-type",
        format: { contentType, supportedContentTypes: multipartContentTypesValues.join(", ") },
        target: type
      }));
    }
  }
  if (type.kind === "Model") {
    return diagnostics.join(resolveMultiPartBodyFromModel(program, property, type, contentTypeProperty, visibility));
  } else if (type.kind === "Tuple") {
    return diagnostics.join(resolveMultiPartBodyFromTuple(program, property, type, contentTypeProperty, visibility));
  } else {
    diagnostics.add(createDiagnostic({ code: "multipart-model", target: property }));
    return diagnostics.wrap(void 0);
  }
}
function resolveMultiPartBodyFromModel(program, property, type, contentTypeProperty, visibility) {
  const diagnostics = createDiagnosticCollector4();
  const parts = [];
  for (const item of type.properties.values()) {
    const part = diagnostics.pipe(resolvePartOrParts(program, item.type, visibility, item));
    if (part) {
      parts.push({
        partKind: "model",
        ...part,
        name: part.name ?? item.name,
        optional: item.optional,
        property: item
      });
    }
  }
  const resolvedContentTypes = contentTypeProperty ? {
    contentTypeProperty: contentTypeProperty.property,
    contentTypes: diagnostics.pipe(getContentTypes(contentTypeProperty.property))
  } : {
    contentTypes: [multipartContentTypes.formData]
  };
  return diagnostics.wrap({
    bodyKind: "multipart",
    multipartKind: "model",
    ...resolvedContentTypes,
    parts,
    property,
    type
  });
}
var multipartContentTypes = {
  formData: "multipart/form-data",
  mixed: "multipart/mixed"
};
var multipartContentTypesValues = Object.values(multipartContentTypes);
function resolveMultiPartBodyFromTuple(program, property, type, contentTypeProperty, visibility) {
  const diagnostics = createDiagnosticCollector4();
  const parts = [];
  const contentTypes = contentTypeProperty && diagnostics.pipe(getContentTypes(contentTypeProperty?.property));
  for (const [index, item] of type.values.entries()) {
    const part = diagnostics.pipe(resolvePartOrParts(program, item, visibility));
    if (part?.name === void 0 && contentTypes?.includes(multipartContentTypes.formData)) {
      diagnostics.add(createDiagnostic({
        code: "formdata-no-part-name",
        target: type.node?.values[index] ?? type.values[index]
      }));
    }
    if (part) {
      parts.push({ partKind: "tuple", ...part, optional: false });
    }
  }
  const resolvedContentTypes = contentTypeProperty ? {
    contentTypeProperty: contentTypeProperty.property,
    contentTypes: diagnostics.pipe(getContentTypes(contentTypeProperty.property))
  } : {
    contentTypes: [multipartContentTypes.formData]
  };
  return diagnostics.wrap({
    bodyKind: "multipart",
    multipartKind: "tuple",
    ...resolvedContentTypes,
    parts,
    property,
    type
  });
}
function resolvePartOrParts(program, type, visibility, property) {
  if (type.kind === "Model" && isArrayModelType(program, type)) {
    const [part, diagnostics] = resolvePart(program, type.indexer.value, visibility, property);
    if (part) {
      return [{ ...part, multi: true }, diagnostics];
    }
    return [part, diagnostics];
  } else {
    return resolvePart(program, type, visibility, property);
  }
}
function resolvePart(program, type, visibility, property) {
  const diagnostics = createDiagnosticCollector4();
  const part = getHttpPart(program, type);
  if (part) {
    let { body, metadata } = diagnostics.pipe(resolveHttpPayload(program, part.type, visibility, HttpPayloadDisposition.Multipart));
    const contentTypeProperty = metadata.find((x) => x.kind === "contentType");
    if (body === void 0) {
      return diagnostics.wrap(void 0);
    } else if (body.bodyKind === "multipart") {
      diagnostics.add(createDiagnostic({ code: "multipart-nested", target: type }));
      return diagnostics.wrap(void 0);
    }
    if (body.contentTypes.length === 0) {
      body = {
        ...body,
        contentTypes: diagnostics.pipe(resolveContentTypesForBody(program, contentTypeProperty, body.type)).contentTypes
      };
    }
    return diagnostics.wrap({
      multi: false,
      property,
      name: part.options.name,
      body,
      optional: false,
      headers: metadata.filter((x) => x.kind === "header"),
      filename: body.bodyKind === "file" ? body.filename : void 0
    });
  }
  diagnostics.add(createDiagnostic({ code: "multipart-part", target: type }));
  return diagnostics.wrap(void 0);
}
function createHttpFileModelFilter(metadata) {
  const metadataPropToMetadata = new Map(metadata.map((x) => [x.property, x]));
  return function isApplicableMetadata2(property) {
    const httpProperty = metadataPropToMetadata.get(property);
    if (["filename"].includes(property.name))
      return true;
    if (!httpProperty)
      return true;
    if (httpProperty.kind !== "bodyProperty")
      return false;
    return true;
  };
}
function getFileBody(file, property) {
  const [contentTypes, diagnostics] = getContentTypes(file.contentType);
  const isText = isOrExtendsString(file.contents.type);
  return [
    {
      bodyKind: "file",
      type: file.type,
      contents: file.contents,
      filename: file.filename,
      isText,
      contentTypeProperty: file.contentType,
      contentTypes,
      property
    },
    diagnostics
  ];
  function isOrExtendsString(type) {
    return isString(type) || !!type.baseScalar && isOrExtendsString(type.baseScalar);
    function isString(type2) {
      return type2.name === "string" && !!type2.namespace && type2.namespace.name === "TypeSpec" && !!type2.namespace.namespace && type2.namespace.namespace.name === "" && !type2.namespace.namespace.namespace;
    }
  }
}
function getDefaultContentTypeForKind(type) {
  return type.kind === "Scalar" ? "text/plain" : "application/json";
}
function isLiteralType(type) {
  return type.kind === "String" || type.kind === "Number" || type.kind === "Boolean" || type.kind === "StringTemplate";
}
function resolveContentTypesForBody(program, contentTypeProperty, type, getDefaultContentType = getDefaultContentTypeForKind) {
  const diagnostics = createDiagnosticCollector4();
  return diagnostics.wrap(resolve());
  function resolve() {
    let mpContentType;
    if (isMergePatchBody(program, type)) {
      mpContentType = "application/merge-patch+json";
    }
    if (contentTypeProperty) {
      const explicitContentTypes = diagnostics.pipe(getContentTypes(contentTypeProperty.property));
      if (mpContentType) {
        const badContentTypes = explicitContentTypes.filter((c) => !c.startsWith(mpContentType));
        if (badContentTypes.length > 0) {
          diagnostics.add(createDiagnostic({
            code: "merge-patch-content-type",
            target: contentTypeProperty.property ?? type,
            format: { contentType: badContentTypes[0] }
          }));
        }
      }
      return {
        contentTypes: explicitContentTypes,
        contentTypeProperty: contentTypeProperty.property
      };
    }
    if (mpContentType)
      return { contentTypes: [mpContentType] };
    if (isLiteralType(type)) {
      switch (type.kind) {
        case "StringTemplate":
        case "String":
          type = program.checker.getStdType("string");
          break;
        case "Boolean":
          type = program.checker.getStdType("boolean");
          break;
        case "Number":
          type = program.checker.getStdType("numeric");
          break;
        default:
          void type;
      }
    }
    let encoded;
    while ((type.kind === "Scalar" || type.kind === "ModelProperty") && (encoded = getEncode(program, type))) {
      type = encoded.type;
    }
    if (type.kind === "Union") {
      const variants = [...type.variants.values()];
      const containsNull = variants.some((v) => v.type.kind === "Intrinsic" && v.type.name === "null");
      if (containsNull) {
        return { contentTypes: ["application/json"] };
      }
      const set = /* @__PURE__ */ new Set();
      for (const variant of variants) {
        const resolved = diagnostics.pipe(resolveContentTypesForBody(program, contentTypeProperty, variant.type));
        for (const contentType of resolved.contentTypes) {
          set.add(contentType);
        }
      }
      return { contentTypes: [...set] };
    } else {
      const contentType = getMediaTypeHint(program, type) ?? getDefaultContentType(type);
      return { contentTypes: [contentType] };
    }
  }
}

// src/typespec/core/packages/http/dist/src/uri-template.js
var operators = ["+", "#", ".", "/", ";", "?", "&"];
var uriTemplateRegex = /\{([^{}]+)\}|([^{}]+)/g;
var expressionRegex = /([^:*]*)(?::(\d+)|(\*))?/;
function parseUriTemplate(template) {
  const parameters = [];
  const segments = [];
  const matches = template.matchAll(uriTemplateRegex);
  for (let [_, expression, literal] of matches) {
    if (expression) {
      let operator;
      if (operators.includes(expression[0])) {
        operator = expression[0];
        expression = expression.slice(1);
      }
      const items = expression.split(",");
      for (const item of items) {
        const match = item.match(expressionRegex);
        const name = match[1];
        const parameter = {
          name,
          operator,
          modifier: match[3] ? { type: "explode" } : match[2] ? { type: "prefix", value: Number(match[2]) } : void 0
        };
        parameters.push(parameter);
        segments.push(parameter);
      }
    } else {
      segments.push(literal);
    }
  }
  return { segments, parameters };
}

// src/typespec/core/packages/http/dist/src/parameters.js
function getOperationParameters(program, operation, partialUriTemplate, overloadBase, options = {}) {
  const verb = (options?.verbSelector && options.verbSelector(program, operation)) ?? getOperationVerb(program, operation) ?? overloadBase?.verb;
  if (verb) {
    return getOperationParametersForVerb(program, operation, verb, partialUriTemplate);
  }
  const post = getOperationParametersForVerb(program, operation, "post", partialUriTemplate);
  return post[0].body ? post : getOperationParametersForVerb(program, operation, "get", partialUriTemplate);
}
var operatorToStyle = {
  ";": "matrix",
  "#": "fragment",
  ".": "label",
  "/": "path"
};
function getOperationParametersForVerb(program, operation, verb, partialUriTemplate) {
  const diagnostics = createDiagnosticCollector5();
  const visibility = resolveRequestVisibility(program, operation, verb);
  const parsedUriTemplate = parseUriTemplate(partialUriTemplate);
  const parameters = [];
  const { body: resolvedBody, metadata } = diagnostics.pipe(resolveHttpPayload(program, operation.parameters, visibility, HttpPayloadDisposition.Request, {
    implicitParameter: (param) => {
      const isTopLevel = param.model === operation.parameters;
      const uriParam = isTopLevel && parsedUriTemplate.parameters.find((x) => x.name === param.name);
      if (!uriParam) {
        const pathOptions = getPathOptions(program, param);
        if (pathOptions && param.optional) {
          return {
            type: "path",
            name: pathOptions.name,
            explode: false,
            allowReserved: false,
            style: operatorToStyle["/"]
          };
        }
        return void 0;
      }
      const explode = uriParam.modifier?.type === "explode";
      if (uriParam.operator === "?" || uriParam.operator === "&") {
        return {
          type: "query",
          name: uriParam.name,
          explode
        };
      } else if (uriParam.operator === "+") {
        return {
          type: "path",
          name: uriParam.name,
          explode,
          allowReserved: true,
          style: "simple"
        };
      } else {
        return {
          type: "path",
          name: uriParam.name,
          explode,
          allowReserved: false,
          style: (uriParam.operator && operatorToStyle[uriParam.operator]) ?? "simple"
        };
      }
    }
  }));
  const implicitOptionality = getPatchOptions(program, operation)?.implicitOptionality;
  if (verb === "patch" && resolvedBody && implicitOptionality === void 0 && !isMergePatchBody(program, resolvedBody?.type) && !resolvedBody.contentTypes.includes("application/merge-patch+json")) {
    diagnostics.add(createDiagnostic({
      code: "patch-implicit-optional",
      target: operation
    }));
  }
  for (const item of metadata) {
    switch (item.kind) {
      case "contentType":
        parameters.push({
          name: "Content-Type",
          type: "header",
          param: item.property
        });
        break;
      case "path":
      case "query":
      case "cookie":
      case "header":
        parameters.push({
          type: item.kind,
          // TODO: why is this not passing
          ...item.options,
          param: item.property
        });
        break;
    }
  }
  const body = resolvedBody;
  return diagnostics.wrap({
    properties: metadata,
    parameters,
    verb,
    body,
    get bodyType() {
      return body?.type;
    },
    get bodyParameter() {
      return body?.property;
    }
  });
}

// src/typespec/core/packages/http/dist/src/route.js
var AllowedSegmentSeparators = ["/", ":"];
function needsSlashPrefix(fragment) {
  return !(AllowedSegmentSeparators.indexOf(fragment[0]) !== -1 || fragment[0] === "{" && fragment[1] === "/");
}
function normalizeFragment(fragment, trimLast = false) {
  if (fragment.length > 0 && needsSlashPrefix(fragment)) {
    fragment = `/${fragment}`;
  }
  if (trimLast && fragment[fragment.length - 1] === "/") {
    return fragment.slice(0, -1);
  }
  return fragment;
}
function joinPathSegments(rest) {
  let current = "";
  for (const [index, segment] of rest.entries()) {
    current += normalizeFragment(segment, index < rest.length - 1);
  }
  return current;
}
function buildPath(pathFragments) {
  const path = pathFragments.length === 0 ? "/" : joinPathSegments(pathFragments);
  return path[0] === "/" || path[0] === "{" && path[1] === "/" ? path : `/${path}`;
}
function resolvePathAndParameters(program, operation, overloadBase, options) {
  const diagnostics = createDiagnosticCollector6();
  const { uriTemplate, parameters } = diagnostics.pipe(getUriTemplateAndParameters(program, operation, overloadBase, options));
  const parsedUriTemplate = parseUriTemplate(uriTemplate);
  const paramByName = new Set(parameters.parameters.filter(({ type }) => type === "path" || type === "query").map((x) => x.name));
  validateDoubleSlash(parsedUriTemplate, operation, parameters).forEach((d) => diagnostics.add(d));
  for (const routeParam of parsedUriTemplate.parameters) {
    const decoded = decodeURIComponent(routeParam.name);
    if (!paramByName.has(routeParam.name) && !paramByName.has(decoded)) {
      diagnostics.add(createDiagnostic({
        code: "missing-uri-param",
        format: { param: routeParam.name },
        target: operation
      }));
    }
  }
  const path = produceLegacyPathFromUriTemplate(parsedUriTemplate);
  return diagnostics.wrap({
    uriTemplate,
    path,
    parameters
  });
}
function validateDoubleSlash(parsedUriTemplate, operation, parameters) {
  const diagnostics = createDiagnosticCollector6();
  if (parsedUriTemplate.segments) {
    const [firstSeg, ...rest] = parsedUriTemplate.segments;
    let lastSeg = firstSeg;
    for (const seg of rest) {
      if (typeof seg !== "string") {
        const parameter = parameters.parameters.find((x) => x.name === seg.name);
        if (seg.operator === "/") {
          if (typeof lastSeg === "string" && lastSeg.endsWith("/")) {
            diagnostics.add(createDiagnostic({
              code: "double-slash",
              messageId: parameter?.param.optional ? "optionalUnset" : "default",
              format: { paramName: seg.name },
              target: operation
            }));
          }
        }
        lastSeg = seg;
      }
    }
  }
  return diagnostics.diagnostics;
}
function produceLegacyPathFromUriTemplate(uriTemplate) {
  let result = "";
  for (const segment of uriTemplate.segments ?? []) {
    if (typeof segment === "string") {
      result += segment;
    } else if (segment.operator !== "?" && segment.operator !== "&") {
      result += `{${segment.name}}`;
    }
  }
  return result;
}
function collectSegmentsAndOptions(program, source) {
  if (source === void 0)
    return [[], {}];
  const [parentSegments, parentOptions] = collectSegmentsAndOptions(program, source.namespace);
  const route = getRoutePath(program, source)?.path;
  const options = source.kind === "Namespace" ? getRouteOptionsForNamespace(program, source) ?? {} : {};
  return [[...parentSegments, ...route ? [route] : []], { ...parentOptions, ...options }];
}
function getUriTemplateAndParameters(program, operation, overloadBase, options) {
  const [parentSegments, parentOptions] = collectSegmentsAndOptions(program, operation.interface ?? operation.namespace);
  const routeProducer = getRouteProducer(program, operation) ?? DefaultRouteProducer;
  const [result, diagnostics] = routeProducer(program, operation, parentSegments, overloadBase, {
    ...parentOptions,
    ...options
  });
  return [
    { uriTemplate: buildPath([result.uriTemplate]), parameters: result.parameters },
    diagnostics
  ];
}
function DefaultRouteProducer(program, operation, parentSegments, overloadBase, options) {
  const diagnostics = createDiagnosticCollector6();
  const routePath = getRoutePath(program, operation)?.path;
  const uriTemplate = !routePath && overloadBase ? overloadBase.uriTemplate : joinPathSegments([...parentSegments, ...routePath ? [routePath] : []]);
  const parsedUriTemplate = parseUriTemplate(uriTemplate);
  const parameters = diagnostics.pipe(getOperationParameters(program, operation, uriTemplate, overloadBase, options.paramOptions));
  const unreferencedPathParamNames = new Map(parameters.parameters.filter(({ type }) => type === "path" || type === "query").map((x) => [x.name, x]));
  for (const uriParam of parsedUriTemplate.parameters) {
    unreferencedPathParamNames.delete(uriParam.name);
  }
  const resolvedUriTemplate = addOperationTemplateToUriTemplate(uriTemplate, [
    ...unreferencedPathParamNames.values()
  ]);
  return diagnostics.wrap({
    uriTemplate: resolvedUriTemplate,
    parameters
  });
}
var styleToOperator = {
  matrix: ";",
  label: ".",
  simple: "",
  path: "/",
  fragment: "#"
};
function getUriTemplatePathParam(param) {
  const operator = param.param.optional ? "/" : param.allowReserved ? "+" : styleToOperator[param.style];
  return `{${operator}${param.name}${param.explode ? "*" : ""}}`;
}
function getUriTemplateQueryParamPart(param) {
  return `${escapeUriTemplateParamName(param.name)}${param.explode ? "*" : ""}`;
}
function addQueryParamsToUriTemplate(uriTemplate, params) {
  const queryParams = params.filter((x) => x.type === "query");
  return uriTemplate + (queryParams.length > 0 ? `{?${queryParams.map((x) => getUriTemplateQueryParamPart(x)).join(",")}}` : "");
}
function addOperationTemplateToUriTemplate(uriTemplate, params) {
  const pathParams = params.filter((x) => x.type === "path").map(getUriTemplatePathParam);
  const queryParams = params.filter((x) => x.type === "query");
  const pathPart = joinPathSegments([uriTemplate, ...pathParams]);
  return addQueryParamsToUriTemplate(pathPart, queryParams);
}
function escapeUriTemplateParamName(name) {
  return encodeURIComponent(name).replace(/[:-]/g, function(c) {
    return "%" + c.charCodeAt(0).toString(16).toUpperCase();
  });
}
function setRouteProducer(program, operation, routeProducer) {
  program.stateMap(HttpStateKeys.routeProducer).set(operation, routeProducer);
}
function getRouteProducer(program, operation) {
  return program.stateMap(HttpStateKeys.routeProducer).get(operation);
}
function setRoute(context, entity, details) {
  const state = context.program.stateMap(HttpStateKeys.routes);
  if (state.has(entity) && entity.kind === "Namespace") {
    const existingPath = state.get(entity);
    if (existingPath !== details.path) {
      reportDiagnostic(context.program, {
        code: "duplicate-route-decorator",
        messageId: "namespace",
        target: entity
      });
    }
  } else {
    state.set(entity, details.path);
    if (entity.kind === "Operation" && details.shared) {
      setSharedRoute(context.program, entity);
    }
  }
}
function setSharedRoute(program, operation) {
  program.stateMap(HttpStateKeys.sharedRoutes).set(operation, true);
}
function isSharedRoute(program, operation) {
  return program.stateMap(HttpStateKeys.sharedRoutes).get(operation) === true;
}
function getRoutePath(program, entity) {
  const path = program.stateMap(HttpStateKeys.routes).get(entity);
  return path ? {
    path,
    shared: entity.kind === "Operation" && isSharedRoute(program, entity)
  } : void 0;
}
function setRouteOptionsForNamespace(program, namespace, options) {
  program.stateMap(HttpStateKeys.routeOptions).set(namespace, options);
}
function getRouteOptionsForNamespace(program, namespace) {
  return program.stateMap(HttpStateKeys.routeOptions).get(namespace);
}

// src/typespec/core/packages/http/dist/src/status-codes.js
import { createDiagnosticCollector as createDiagnosticCollector7, getMaxValue, getMinValue } from "@typespec/compiler";
import { $ as $2 } from "@typespec/compiler/typekit";
function error(target) {
  return [
    [],
    [
      createDiagnostic({
        code: "status-code-invalid",
        target,
        messageId: "value"
      })
    ]
  ];
}
function validateStatusCode(code, diagnosticTarget) {
  const codeAsNumber = typeof code === "string" ? parseInt(code, 10) : code;
  if (isNaN(codeAsNumber)) {
    return error(diagnosticTarget);
  }
  if (!Number.isInteger(codeAsNumber)) {
    return error(diagnosticTarget);
  }
  if (codeAsNumber < 100 || codeAsNumber > 599) {
    return error(diagnosticTarget);
  }
  return [[codeAsNumber], []];
}
function getStatusCodesFromType(program, type, diagnosticTarget) {
  switch (type.kind) {
    case "String":
    case "Number":
      return validateStatusCode(type.value, diagnosticTarget);
    case "Union":
      const diagnostics = createDiagnosticCollector7();
      const statusCodes = [...type.variants.values()].flatMap((variant) => {
        return diagnostics.pipe(getStatusCodesFromType(program, variant.type, diagnosticTarget));
      });
      return diagnostics.wrap(statusCodes);
    case "Scalar":
      return validateStatusCodeRange(program, type, type, diagnosticTarget);
    case "ModelProperty":
      if (type.type.kind === "Scalar") {
        return validateStatusCodeRange(program, type, type.type, diagnosticTarget);
      } else {
        return getStatusCodesFromType(program, type.type, diagnosticTarget);
      }
    default:
      return error(diagnosticTarget);
  }
}
function validateStatusCodeRange(program, type, scalar, diagnosticTarget) {
  if (!isInt32(program, scalar)) {
    return error(diagnosticTarget);
  }
  const range = getStatusCodesRange(program, type, diagnosticTarget);
  if (isRangeComplete(range)) {
    return [[range], []];
  } else {
    return error(diagnosticTarget);
  }
}
function isRangeComplete(range) {
  return range.start !== void 0 && range.end !== void 0;
}
function getStatusCodesRange(program, type, diagnosticTarget) {
  const start = getMinValue(program, type);
  const end = getMaxValue(program, type);
  let baseRange = {};
  if (type.kind === "ModelProperty" && (type.type.kind === "Scalar" || type.type.kind === "ModelProperty")) {
    baseRange = getStatusCodesRange(program, type.type, diagnosticTarget);
  } else if (type.kind === "Scalar" && type.baseScalar) {
    baseRange = getStatusCodesRange(program, type.baseScalar, diagnosticTarget);
  }
  return { ...baseRange, start, end };
}
function isInt32(program, type) {
  const tk = $2(program);
  return tk.type.isAssignableTo(type, tk.builtin.int32, type);
}

// src/typespec/core/packages/http/dist/src/utils.js
function extractParamsFromPath(path) {
  return path.match(/\{[^}]+\}/g)?.map((s) => s.slice(1, -1)) ?? [];
}

// src/typespec/core/packages/http/dist/src/decorators.js
var $header = (context, entity, headerNameOrOptions) => {
  const options = {
    type: "header",
    name: entity.name.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()
  };
  if (headerNameOrOptions) {
    if (typeof headerNameOrOptions === "string") {
      options.name = headerNameOrOptions;
    } else {
      const name = headerNameOrOptions.name;
      if (name) {
        options.name = name;
      }
      if (headerNameOrOptions.explode) {
        options.explode = true;
      }
    }
  }
  context.program.stateMap(HttpStateKeys.header).set(entity, options);
};
function getHeaderFieldOptions(program, entity) {
  return program.stateMap(HttpStateKeys.header).get(entity);
}
function getHeaderFieldName(program, entity) {
  return getHeaderFieldOptions(program, entity)?.name;
}
function isHeader(program, entity) {
  return program.stateMap(HttpStateKeys.header).has(entity);
}
var $cookie = (context, entity, cookieNameOrOptions) => {
  const paramName = typeof cookieNameOrOptions === "string" ? cookieNameOrOptions : cookieNameOrOptions?.name ?? entity.name.replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase();
  const options = {
    type: "cookie",
    name: paramName
  };
  context.program.stateMap(HttpStateKeys.cookie).set(entity, options);
};
function getCookieParamOptions(program, entity) {
  return program.stateMap(HttpStateKeys.cookie).get(entity);
}
function isCookieParam(program, entity) {
  return program.stateMap(HttpStateKeys.cookie).has(entity);
}
var [getQueryOptions, setQueryOptions] = useStateMap(HttpStateKeys.query);
var $query = (context, entity, queryNameOrOptions) => {
  const paramName = typeof queryNameOrOptions === "string" ? queryNameOrOptions : queryNameOrOptions?.name ?? entity.name;
  const userOptions = typeof queryNameOrOptions === "object" ? queryNameOrOptions : {};
  setQueryOptions(context.program, entity, {
    explode: userOptions.explode,
    name: paramName
  });
};
function resolveQueryOptionsWithDefaults(options) {
  return {
    explode: options.explode ?? false,
    name: options.name
  };
}
function getQueryParamOptions(program, entity) {
  const userOptions = getQueryOptions(program, entity);
  if (!userOptions)
    return void 0;
  return { type: "query", ...resolveQueryOptionsWithDefaults(userOptions) };
}
function getQueryParamName(program, entity) {
  return getQueryParamOptions(program, entity)?.name;
}
function isQueryParam(program, entity) {
  return program.stateMap(HttpStateKeys.query).has(entity);
}
var [getPathOptions, setPathOptions] = useStateMap(HttpStateKeys.path);
var $path = (context, entity, paramNameOrOptions) => {
  const paramName = typeof paramNameOrOptions === "string" ? paramNameOrOptions : paramNameOrOptions?.name ?? entity.name;
  const userOptions = typeof paramNameOrOptions === "object" ? paramNameOrOptions : {};
  setPathOptions(context.program, entity, {
    explode: userOptions.explode,
    allowReserved: userOptions.allowReserved,
    style: userOptions.style,
    name: paramName
  });
};
function resolvePathOptionsWithDefaults(options) {
  return {
    explode: options.explode ?? false,
    allowReserved: options.allowReserved ?? false,
    style: options.style ?? "simple",
    name: options.name
  };
}
function getPathParamOptions(program, entity) {
  const userOptions = getPathOptions(program, entity);
  if (!userOptions)
    return void 0;
  return { type: "path", ...resolvePathOptionsWithDefaults(userOptions) };
}
function getPathParamName(program, entity) {
  return getPathOptions(program, entity)?.name;
}
function isPathParam(program, entity) {
  return program.stateMap(HttpStateKeys.path).has(entity);
}
var $body = (context, entity) => {
  context.program.stateSet(HttpStateKeys.body).add(entity);
};
var $bodyRoot = (context, entity) => {
  context.program.stateSet(HttpStateKeys.bodyRoot).add(entity);
};
var $bodyIgnore = (context, entity) => {
  context.program.stateSet(HttpStateKeys.bodyIgnore).add(entity);
};
function isBody(program, entity) {
  return program.stateSet(HttpStateKeys.body).has(entity);
}
function isBodyRoot(program, entity) {
  return program.stateSet(HttpStateKeys.bodyRoot).has(entity);
}
function isBodyIgnore(program, entity) {
  return program.stateSet(HttpStateKeys.bodyIgnore).has(entity);
}
var $multipartBody = (context, entity) => {
  context.program.stateSet(HttpStateKeys.multipartBody).add(entity);
};
function isMultipartBodyProperty(program, entity) {
  return program.stateSet(HttpStateKeys.multipartBody).has(entity);
}
var $statusCode = (context, entity) => {
  context.program.stateSet(HttpStateKeys.statusCode).add(entity);
};
function setStatusCode(program, entity, codes) {
  program.stateMap(HttpStateKeys.statusCode).set(entity, codes);
}
function isStatusCode(program, entity) {
  return program.stateSet(HttpStateKeys.statusCode).has(entity);
}
function getStatusCodesWithDiagnostics(program, type) {
  return getStatusCodesFromType(program, type, type);
}
function getStatusCodes(program, entity) {
  return ignoreDiagnostics(getStatusCodesWithDiagnostics(program, entity));
}
function getStatusCodeDescription(statusCode) {
  if (typeof statusCode === "object") {
    return rangeDescription(statusCode.start, statusCode.end);
  }
  const statusCodeNumber = typeof statusCode === "string" ? parseInt(statusCode, 10) : statusCode;
  switch (statusCodeNumber) {
    case 200:
      return "The request has succeeded.";
    case 201:
      return "The request has succeeded and a new resource has been created as a result.";
    case 202:
      return "The request has been accepted for processing, but processing has not yet completed.";
    case 204:
      return "There is no content to send for this request, but the headers may be useful. ";
    case 301:
      return "The URL of the requested resource has been changed permanently. The new URL is given in the response.";
    case 304:
      return "The client has made a conditional request and the resource has not been modified.";
    case 400:
      return "The server could not understand the request due to invalid syntax.";
    case 401:
      return "Access is unauthorized.";
    case 403:
      return "Access is forbidden.";
    case 404:
      return "The server cannot find the requested resource.";
    case 409:
      return "The request conflicts with the current state of the server.";
    case 412:
      return "Precondition failed.";
    case 503:
      return "Service unavailable.";
  }
  return rangeDescription(statusCodeNumber, statusCodeNumber);
}
function rangeDescription(start, end) {
  if (start >= 100 && end <= 199) {
    return "Informational";
  } else if (start >= 200 && end <= 299) {
    return "Successful";
  } else if (start >= 300 && end <= 399) {
    return "Redirection";
  } else if (start >= 400 && end <= 499) {
    return "Client error";
  } else if (start >= 500 && end <= 599) {
    return "Server error";
  }
  return void 0;
}
function setOperationVerb(context, entity, verb) {
  validateVerbUniqueOnNode(context, entity);
  context.program.stateMap(HttpStateKeys.verbs).set(entity, verb);
}
function validateVerbUniqueOnNode(context, type) {
  const verbDecorators = type.decorators.filter((x) => VERB_DECORATORS.includes(x.decorator) && x.node?.kind === SyntaxKind3.DecoratorExpression && x.node?.parent === type.node);
  if (verbDecorators.length > 1) {
    reportDiagnostic(context.program, {
      code: "http-verb-duplicate",
      format: { entityName: type.name },
      target: context.decoratorTarget
    });
    return false;
  }
  return true;
}
function getOperationVerb(program, entity) {
  return program.stateMap(HttpStateKeys.verbs).get(entity);
}
function createVerbDecorator(verb) {
  return (context, entity) => {
    setOperationVerb(context, entity, verb);
  };
}
var $get = createVerbDecorator("get");
var $put = createVerbDecorator("put");
var $post = createVerbDecorator("post");
var $delete = createVerbDecorator("delete");
var $head = createVerbDecorator("head");
var _patch = createVerbDecorator("patch");
var [_getPatchOptions, setPatchOptions] = useStateMap(HttpStateKeys.patchOptions);
var $patch = (context, entity, options) => {
  _patch(context, entity);
  if (options)
    setPatchOptions(context.program, entity, options);
};
function getPatchOptions(program, operation) {
  return _getPatchOptions(program, operation);
}
var VERB_DECORATORS = [$get, $head, $post, $put, $patch, $delete];
var $server = (context, target, url, description, parameters) => {
  const params = extractParamsFromPath(url);
  const parameterMap = new Map(parameters?.properties ?? []);
  for (const declaredParam of params) {
    const param = parameterMap.get(declaredParam);
    if (!param) {
      reportDiagnostic(context.program, {
        code: "missing-server-param",
        format: { param: declaredParam },
        target: context.getArgumentTarget(0)
      });
      parameterMap.delete(declaredParam);
    }
  }
  let servers = context.program.stateMap(HttpStateKeys.servers).get(target);
  if (servers === void 0) {
    servers = [];
    context.program.stateMap(HttpStateKeys.servers).set(target, servers);
  }
  servers.push({ url, description, parameters: parameterMap });
};
function getServers(program, type) {
  return program.stateMap(HttpStateKeys.servers).get(type);
}
function $useAuth(context, entity, authConfig) {
  validateDecoratorUniqueOnNode(context, entity, $useAuth);
  const [auth, diagnostics] = extractAuthentication(context.program, authConfig);
  if (diagnostics.length > 0)
    context.program.reportDiagnostics(diagnostics);
  if (auth !== void 0) {
    setAuthentication(context.program, entity, auth);
  }
}
function setAuthentication(program, entity, auth) {
  program.stateMap(HttpStateKeys.authentication).set(entity, auth);
}
function extractAuthentication(program, type) {
  const diagnostics = createDiagnosticCollector8();
  switch (type.kind) {
    case "Model":
      const auth = diagnostics.pipe(extractHttpAuthentication(program, type, type));
      if (auth === void 0)
        return diagnostics.wrap(void 0);
      return diagnostics.wrap({ options: [{ schemes: [auth] }] });
    case "Tuple":
      const option = diagnostics.pipe(extractHttpAuthenticationOption(program, type, type));
      return diagnostics.wrap({ options: [option] });
    case "Union":
      return extractHttpAuthenticationOptions(program, type, type);
    default:
      return [
        void 0,
        [
          createDiagnostic({
            code: "invalid-type-for-auth",
            format: { kind: type.kind },
            target: type
          })
        ]
      ];
  }
}
function extractHttpAuthenticationOptions(program, tuple, diagnosticTarget) {
  const options = [];
  const diagnostics = createDiagnosticCollector8();
  for (const variant of tuple.variants.values()) {
    const value = variant.type;
    switch (value.kind) {
      case "Model":
        const result = diagnostics.pipe(extractHttpAuthentication(program, value, diagnosticTarget));
        if (result !== void 0) {
          options.push({ schemes: [result] });
        }
        break;
      case "Tuple":
        const option = diagnostics.pipe(extractHttpAuthenticationOption(program, value, diagnosticTarget));
        options.push(option);
        break;
      default:
        diagnostics.add(createDiagnostic({
          code: "invalid-type-for-auth",
          format: { kind: value.kind },
          target: value
        }));
    }
  }
  return diagnostics.wrap({ options });
}
function extractHttpAuthenticationOption(program, tuple, diagnosticTarget) {
  const schemes = [];
  const diagnostics = createDiagnosticCollector8();
  for (const value of tuple.values) {
    switch (value.kind) {
      case "Model":
        const result = diagnostics.pipe(extractHttpAuthentication(program, value, diagnosticTarget));
        if (result !== void 0) {
          schemes.push(result);
        }
        break;
      default:
        diagnostics.add(createDiagnostic({
          code: "invalid-type-for-auth",
          format: { kind: value.kind },
          target: value
        }));
    }
  }
  return diagnostics.wrap({ schemes });
}
function extractHttpAuthentication(program, modelType, diagnosticTarget) {
  const [result, diagnostics] = typespecTypeToJson(modelType, diagnosticTarget);
  if (result === void 0) {
    return [result, diagnostics];
  }
  const description = getDoc(program, modelType);
  const auth = result.type === "oauth2" ? extractOAuth2Auth(modelType, result) : { ...result, model: modelType };
  return [
    {
      ...auth,
      id: modelType.name || result.type,
      ...description && { description }
    },
    diagnostics
  ];
}
function extractOAuth2Auth(modelType, data) {
  const flows = Array.isArray(data.flows) && data.flows.every((x) => typeof x === "object") ? data.flows : [];
  const defaultScopes = Array.isArray(data.defaultScopes) ? data.defaultScopes : [];
  return {
    id: data.id,
    type: data.type,
    model: modelType,
    flows: flows.map((flow) => {
      const scopes = flow.scopes ? flow.scopes : defaultScopes;
      return {
        ...flow,
        scopes: scopes.map((x) => ({ value: x }))
      };
    })
  };
}
function getAuthentication(program, entity) {
  return program.stateMap(HttpStateKeys.authentication).get(entity);
}
var $route = (context, entity, path, parameters) => {
  validateDecoratorUniqueOnNode(context, entity, $route);
  setRoute(context, entity, {
    path,
    shared: false
  });
};
var $sharedRoute = (context, entity) => {
  setSharedRoute(context.program, entity);
};

// src/typespec/core/packages/http/dist/src/responses.js
function getResponsesForOperation(program, operation) {
  const diagnostics = createDiagnosticCollector9();
  const responseType = operation.returnType;
  const responses = new ResponseIndex();
  const tk = $3(program);
  if (tk.union.is(responseType) && !tk.union.getDiscriminatedUnion(responseType)) {
    for (const option of responseType.variants.values()) {
      if (isNullType(option.type)) {
        continue;
      }
      processResponseType(program, diagnostics, operation, responses, option.type);
    }
  } else {
    processResponseType(program, diagnostics, operation, responses, responseType);
  }
  return diagnostics.wrap(responses.values());
}
var ResponseIndex = class {
  #index = /* @__PURE__ */ new Map();
  get(statusCode) {
    return this.#index.get(this.#indexKey(statusCode));
  }
  set(statusCode, response) {
    this.#index.set(this.#indexKey(statusCode), response);
  }
  values() {
    return [...this.#index.values()];
  }
  #indexKey(statusCode) {
    if (typeof statusCode === "number" || statusCode === "*") {
      return String(statusCode);
    } else {
      return `${statusCode.start}-${statusCode.end}`;
    }
  }
};
function processResponseType(program, diagnostics, operation, responses, responseType) {
  let { body: resolvedBody, metadata } = diagnostics.pipe(resolveHttpPayload(program, responseType, Visibility.Read, HttpPayloadDisposition.Response));
  const statusCodes = diagnostics.pipe(getResponseStatusCodes(program, responseType, metadata));
  const headers = getResponseHeaders(program, metadata);
  if (statusCodes.length === 0) {
    if (isErrorModel(program, responseType)) {
      statusCodes.push("*");
    } else if (isVoidType(responseType)) {
      resolvedBody = void 0;
      statusCodes.push(204);
    } else if (resolvedBody === void 0 || isVoidType(resolvedBody.type)) {
      resolvedBody = void 0;
      statusCodes.push(200);
    } else {
      statusCodes.push(200);
    }
  }
  for (const statusCode of statusCodes) {
    const response = responses.get(statusCode) ?? {
      statusCodes: statusCode,
      type: responseType,
      description: getResponseDescription(program, operation, responseType, statusCode, metadata),
      responses: []
    };
    if (resolvedBody !== void 0) {
      response.responses.push({
        body: resolvedBody,
        headers,
        properties: metadata
      });
    } else {
      response.responses.push({ headers, properties: metadata });
    }
    responses.set(statusCode, response);
  }
}
function getResponseStatusCodes(program, responseType, metadata) {
  const codes = [];
  const diagnostics = createDiagnosticCollector9();
  let statusFound = false;
  for (const prop of metadata) {
    if (prop.kind === "statusCode") {
      if (statusFound) {
        reportDiagnostic(program, {
          code: "multiple-status-codes",
          target: responseType
        });
      }
      statusFound = true;
      codes.push(...diagnostics.pipe(getStatusCodesWithDiagnostics(program, prop.property)));
    }
  }
  if (responseType.kind === "Model") {
    for (let t = responseType; t; t = t.baseModel) {
      codes.push(...getExplicitSetStatusCode(program, t));
    }
  }
  return diagnostics.wrap(codes);
}
function getExplicitSetStatusCode(program, entity) {
  return program.stateMap(HttpStateKeys.statusCode).get(entity) ?? [];
}
function getResponseHeaders(program, metadata) {
  const responseHeaders = {};
  for (const prop of metadata) {
    if (prop.kind === "header") {
      responseHeaders[prop.options.name] = prop.property;
    }
  }
  return responseHeaders;
}
function isResponseEnvelope(metadata) {
  return metadata.some((prop) => prop.kind === "body" || prop.kind === "bodyRoot" || prop.kind === "multipartBody" || prop.kind === "statusCode");
}
function getResponseDescription(program, operation, responseType, statusCode, metadata) {
  if (isResponseEnvelope(metadata)) {
    const desc2 = getDoc2(program, responseType);
    if (desc2) {
      return desc2;
    }
  }
  const desc = isErrorModel(program, responseType) ? getErrorsDoc(program, operation) : getReturnsDoc(program, operation);
  if (desc) {
    return desc;
  }
  return getStatusCodeDescription(statusCode);
}

export {
  getContentTypes,
  $plainData,
  $httpFile,
  isHttpFile,
  isOrExtendsHttpFile,
  getHttpFileModel,
  $httpPart,
  getHttpPart,
  $includeInapplicableMetadataInPayload,
  getResponsesForOperation,
  getHttpOperation,
  listHttpOperationsIn,
  getAllHttpServices,
  getHttpService,
  reportIfNoRoutes,
  isOverloadSameEndpoint,
  Visibility,
  getVisibilitySuffix,
  HttpVisibilityProvider,
  resolveRequestVisibility,
  isMetadata,
  isVisible,
  isApplicableMetadata,
  isApplicableMetadataOrBody,
  createMetadataInfo,
  getOperationParameters,
  joinPathSegments,
  DefaultRouteProducer,
  getUriTemplatePathParam,
  addQueryParamsToUriTemplate,
  setRouteProducer,
  getRouteProducer,
  setRoute,
  setSharedRoute,
  isSharedRoute,
  getRoutePath,
  setRouteOptionsForNamespace,
  getRouteOptionsForNamespace,
  $header,
  getHeaderFieldOptions,
  getHeaderFieldName,
  isHeader,
  $cookie,
  getCookieParamOptions,
  isCookieParam,
  getQueryOptions,
  $query,
  getQueryParamOptions,
  getQueryParamName,
  isQueryParam,
  getPathOptions,
  $path,
  getPathParamOptions,
  getPathParamName,
  isPathParam,
  $body,
  $bodyRoot,
  $bodyIgnore,
  isBody,
  isBodyRoot,
  isBodyIgnore,
  $multipartBody,
  isMultipartBodyProperty,
  $statusCode,
  setStatusCode,
  isStatusCode,
  getStatusCodesWithDiagnostics,
  getStatusCodes,
  getStatusCodeDescription,
  getOperationVerb,
  $get,
  $put,
  $post,
  $delete,
  $head,
  $patch,
  getPatchOptions,
  $server,
  getServers,
  $useAuth,
  setAuthentication,
  getAuthentication,
  $route,
  $sharedRoute,
  getAuthenticationForOperation,
  resolveAuthentication
};
