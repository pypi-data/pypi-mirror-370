import {
  __export
} from "./chunk-MLKGABMK.js";

// src/typespec/packages/typespec-autorest/dist/src/index.js
var src_exports = {};
__export(src_exports, {
  $decorators: () => $decorators,
  $example: () => $example,
  $lib: () => $lib,
  $onEmit: () => $onEmit,
  $useRef: () => $useRef,
  getAllServicesAtAllVersions: () => getAllServicesAtAllVersions,
  getExamples: () => getExamples,
  getOpenAPIForService: () => getOpenAPIForService,
  getRef: () => getRef,
  namespace: () => namespace,
  resolveAutorestOptions: () => resolveAutorestOptions,
  sortOpenAPIDocument: () => sortOpenAPIDocument
});

// src/typespec/packages/typespec-autorest/dist/src/lib.js
import { createTypeSpecLibrary, paramMessage } from "@typespec/compiler";
var EmitterOptionsSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    "output-dir": {
      type: "string",
      nullable: true,
      deprecated: true,
      description: "Deprecated DO NOT USE. Use built-in emitter-output-dir instead"
    },
    "output-file": {
      type: "string",
      nullable: true,
      description: [
        "Name of the output file.",
        "Output file will interpolate the following values:",
        " - service-name: Name of the service if multiple",
        " - version: Version of the service if multiple",
        " - azure-resource-provider-folder: Value of the azure-resource-provider-folder option",
        " - version-status: Only enabled if azure-resource-provider-folder is set. `preview` if version contains preview, stable otherwise.",
        "",
        "Default: `{azure-resource-provider-folder}/{service-name}/{version-status}/{version}/openapi.json`",
        "",
        "",
        "Example: Single service no versioning",
        " - `openapi.yaml`",
        "",
        "Example: Multiple services no versioning",
        " - `openapi.Org1.Service1.yaml`",
        " - `openapi.Org1.Service2.yaml`",
        "",
        "Example: Single service with versioning",
        " - `openapi.v1.yaml`",
        " - `openapi.v2.yaml`",
        "",
        "Example: Multiple service with versioning",
        " - `openapi.Org1.Service1.v1.yaml`",
        " - `openapi.Org1.Service1.v2.yaml`",
        " - `openapi.Org1.Service2.v1.0.yaml`",
        " - `openapi.Org1.Service2.v1.1.yaml`",
        "",
        "Example: azureResourceProviderFolder is provided",
        " - `arm-folder/AzureService/preview/2020-01-01.yaml`",
        " - `arm-folder/AzureService/preview/2020-01-01.yaml`"
      ].join("\n")
    },
    "examples-dir": {
      type: "string",
      nullable: true,
      description: "Directory where the examples are located. Default: `{project-root}/examples`.",
      format: "absolute-path"
    },
    "examples-directory": {
      type: "string",
      nullable: true,
      deprecated: true,
      description: "DEPRECATED. Use examples-dir instead"
    },
    version: { type: "string", nullable: true },
    "azure-resource-provider-folder": { type: "string", nullable: true },
    "arm-types-dir": {
      type: "string",
      nullable: true,
      description: "Path to the common-types.json file folder. Default: '${project-root}/../../common-types/resource-management'"
    },
    "new-line": {
      type: "string",
      enum: ["crlf", "lf"],
      nullable: true,
      default: "lf",
      description: "Set the newline character for emitting files."
    },
    "omit-unreachable-types": {
      type: "boolean",
      nullable: true,
      description: "Omit unreachable types. By default all types declared under the service namespace will be included. With this flag on only types references in an operation will be emitted."
    },
    "version-enum-strategy": {
      type: "string",
      nullable: true,
      description: "Decide how to deal with the Version enum when when `omit-unreachable-types` is not set. Default to 'omit'",
      default: "omit"
    },
    "include-x-typespec-name": {
      type: "string",
      enum: ["inline-only", "never"],
      nullable: true,
      default: "never",
      description: "If the generated openapi types should have the `x-typespec-name` extension set with the name of the TypeSpec type that created it.\nThis extension is meant for debugging and should not be depended on."
    },
    "use-read-only-status-schema": {
      type: "boolean",
      nullable: true,
      default: false,
      description: "Create read-only property schema for lro status"
    },
    "emit-lro-options": {
      type: "string",
      enum: ["none", "final-state-only", "all"],
      nullable: true,
      default: "final-state-only",
      description: "Determine whether and how to emit x-ms-long-running-operation-options for lro resolution"
    },
    "arm-resource-flattening": {
      type: "boolean",
      nullable: true,
      default: false,
      description: "Back-compat flag. If true, continue to emit `x-ms-client-flatten` in for some of the ARM resource properties."
    },
    "emit-common-types-schema": {
      type: "string",
      enum: ["never", "for-visibility-changes"],
      nullable: true,
      default: "for-visibility-changes",
      description: "Determine whether and how to emit schemas for common-types rather than referencing them"
    }
  },
  required: []
};
var $lib = createTypeSpecLibrary({
  name: "@azure-tools/typespec-autorest",
  capabilities: {
    dryRun: true
  },
  diagnostics: {
    "duplicate-body-types": {
      severity: "error",
      messages: {
        default: "Request has multiple body types"
      }
    },
    "duplicate-header": {
      severity: "error",
      messages: {
        default: paramMessage`The header ${"header"} is defined across multiple content types`
      }
    },
    "duplicate-example": {
      severity: "error",
      messages: {
        default: "Duplicate @example declarations on operation"
      }
    },
    "duplicate-example-file": {
      severity: "error",
      messages: {
        default: paramMessage`Example file ${"filename"} uses duplicate title '${"title"}' for operationId '${"operationId"}'`
      }
    },
    "invalid-schema": {
      severity: "error",
      messages: {
        default: paramMessage`Couldn't get schema for type ${"type"}`
      }
    },
    "union-null": {
      severity: "error",
      messages: {
        default: "Cannot have a union containing only null types."
      }
    },
    "union-unsupported": {
      severity: "warning",
      messages: {
        default: "Unions cannot be emitted to OpenAPI v2 unless all options are literals of the same type.",
        empty: "Empty unions are not supported for OpenAPI v2 - enums must have at least one value."
      }
    },
    "invalid-multi-collection-format": {
      severity: "error",
      messages: {
        default: "Only encode of `ArrayEncoding.pipeDelimited` and `ArrayEncoding.spaceDelimited` is supported for collection format."
      }
    },
    "inline-cycle": {
      severity: "error",
      messages: {
        default: paramMessage`Cycle detected in '${"type"}'. Use @friendlyName decorator to assign an OpenAPI definition name and make it non-inline.`
      }
    },
    "nonspecific-scalar": {
      severity: "warning",
      messages: {
        default: paramMessage`Scalar type '${"type"}' is not specific enough. The more specific type '${"chosenType"}' has been chosen.`
      }
    },
    "example-loading": {
      severity: "warning",
      messages: {
        default: paramMessage`Skipped loading invalid example file: ${"filename"}. Error: ${"error"}`,
        noDirectory: paramMessage`Skipping example loading from ${"directory"} because there was an error reading the directory.`,
        noOperationId: paramMessage`Skipping example file ${"filename"} because it does not contain an operationId and/or title.`
      }
    },
    "unsupported-http-auth-scheme": {
      severity: "warning",
      messages: {
        default: paramMessage`The specified HTTP authentication scheme is not supported by this emitter: ${"scheme"}.`
      }
    },
    "unsupported-status-code-range": {
      severity: "error",
      messages: {
        default: paramMessage`Status code range '${"start"} to '${"end"}' is not supported. OpenAPI 2.0 can only represent range 1XX, 2XX, 3XX, 4XX and 5XX. Example: \`@minValue(400) @maxValue(499)\` for 4XX.`
      }
    },
    "unsupported-multipart-type": {
      severity: "warning",
      messages: {
        default: paramMessage`Multipart parts can only be represented as primitive types in swagger 2.0. Information is lost for part '${"part"}'.`
      }
    },
    "unsupported-param-type": {
      severity: "warning",
      messages: {
        default: paramMessage`Parameter can only be represented as primitive types in swagger 2.0. Information is lost for part '${"part"}'.`
      }
    },
    "cookies-unsupported": {
      severity: "warning",
      messages: {
        default: `Cookies are not supported in Swagger 2.0. Parameter was ignored.`
      }
    },
    "invalid-format": {
      severity: "warning",
      messages: {
        default: paramMessage`'${"schema"}' format '${"format"}' is not supported in Autorest. It will not be emitted.`
      }
    },
    "unsupported-auth": {
      severity: "warning",
      messages: {
        default: paramMessage`Authentication "${"authType"}" is not a known authentication by the openapi3 emitter, it will be ignored.`
      }
    },
    "no-matching-version-found": {
      severity: "error",
      messages: {
        default: "The emitter did not emit any files because the specified version option does not match any versions of the service."
      }
    }
  },
  emitter: {
    options: EmitterOptionsSchema
  },
  state: {
    example: { description: "State for the @example decorator" },
    useRef: { description: "State for the @useRef decorator" }
  }
});
var { reportDiagnostic, createDiagnostic, stateKeys: AutorestStateKeys, getTracer } = $lib;

// src/typespec/packages/typespec-autorest/dist/src/decorators.js
var namespace = "Autorest";
var $example = (context, entity, pathOrUri, title) => {
  const { program } = context;
  if (!program.stateMap(AutorestStateKeys.example).has(entity)) {
    program.stateMap(AutorestStateKeys.example).set(entity, []);
  } else if (program.stateMap(AutorestStateKeys.example).get(entity).find((e) => e.title === title || e.pathOrUri === pathOrUri)) {
    reportDiagnostic(program, {
      code: "duplicate-example",
      target: entity
    });
  }
  program.stateMap(AutorestStateKeys.example).get(entity).push({
    pathOrUri,
    title
  });
};
function getExamples(program, entity) {
  return program.stateMap(AutorestStateKeys.example).get(entity);
}
var $useRef = (context, entity, jsonRef) => {
  context.program.stateMap(AutorestStateKeys.useRef).set(entity, jsonRef);
};
function getRef(program, entity) {
  const refOrProducer = program.stateMap(AutorestStateKeys.useRef).get(entity);
  return refOrProducer;
}

// src/typespec/packages/typespec-autorest/dist/src/emit.js
import { createTCGCContext } from "@azure-tools/typespec-client-generator-core";
import { compilerAssert as compilerAssert2, emitFile, getDirectoryPath as getDirectoryPath2, getNamespaceFullName, getService, interpolatePath as interpolatePath2, listServices, NoTarget as NoTarget2, reportDeprecated as reportDeprecated2, resolvePath as resolvePath2 } from "@typespec/compiler";
import { unsafe_mutateSubgraphWithNamespace } from "@typespec/compiler/experimental";
import { resolveInfo as resolveInfo2 } from "@typespec/openapi";
import { getVersioningMutators } from "@typespec/versioning";

// src/typespec/packages/typespec-autorest/dist/src/openapi.js
import { FinalStateValue, extractLroStates, getArmResourceIdentifierConfig, getAsEmbeddingVector, getLroMetadata, getPagedResult, getUnionAsEnum } from "@azure-tools/typespec-azure-core";
import { getArmCommonTypeOpenAPIRef, getArmIdentifiers, getArmKeyIdentifiers, getExternalTypeRef, isArmCommonType, isArmProviderNamespace, isAzureResource, isConditionallyFlattened } from "@azure-tools/typespec-azure-resource-manager";
import { getClientNameOverride as getClientNameOverride2, shouldFlattenProperty } from "@azure-tools/typespec-client-generator-core";
import { NoTarget, compilerAssert, createDiagnosticCollector, explainStringTemplateNotSerializable, getAllTags, getAnyExtensionFromPath, getDirectoryPath, getDiscriminator, getDoc, getEncode, getFormat, getLifecycleVisibilityEnum as getLifecycleVisibilityEnum2, getMaxItems, getMaxLength, getMaxValue, getMinItems, getMinLength, getMinValue, getPagingOperation, getPattern, getProperty, getPropertyType, getRelativePathFromDirectory, getRootLength, getSummary, getVisibilityForClass as getVisibilityForClass2, ignoreDiagnostics, interpolatePath, isArrayModelType, isDeprecated, isErrorModel, isErrorType, isGlobalNamespace as isGlobalNamespace2, isList, isNeverType, isNullType, isNumericType, isRecordModelType, isSecret, isService as isService2, isStringType, isTemplateDeclaration, isTemplateDeclarationOrInstance, isVoidType, joinPaths, navigateTypesInNamespace, normalizePath, reportDeprecated, resolveEncodedName, resolvePath, serializeValueAsJson } from "@typespec/compiler";
import { SyntaxKind } from "@typespec/compiler/ast";
import { $ } from "@typespec/compiler/typekit";
import { TwoLevelMap } from "@typespec/compiler/utils";
import { Visibility, createMetadataInfo, getAuthentication, getHeaderFieldOptions, getHttpService, getServers, getStatusCodeDescription, getVisibilitySuffix, isSharedRoute, reportIfNoRoutes, resolveRequestVisibility } from "@typespec/http";
import { checkDuplicateTypeName, getExtensions, getExternalDocs, getOpenAPITypeName, getParameterKey, isReadonlyProperty, resolveInfo, shouldInline } from "@typespec/openapi";
import { getVersionsForEnum } from "@typespec/versioning";

// src/typespec/packages/typespec-autorest/dist/src/autorest-openapi-schema.js
var AutorestOpenAPISchema;
try {
  AutorestOpenAPISchema = (await import("./schema-M3HKPJTW.js")).default;
} catch {
  const name = "../schema/dist/schema.js";
  AutorestOpenAPISchema = (await import(
    /* @vite-ignore */
    name
  )).default;
}

// src/typespec/packages/typespec-autorest/dist/src/json-schema-sorter/sorter.js
function sortWithJsonSchema(value, jsonSchema, ref) {
  const schema = ref ? resolveJsonRef(ref, jsonSchema) : jsonSchema;
  return internalSort(value, schema, new JsonSchemaReader(jsonSchema));
}
function internalSort(value, relativeSchema, reader) {
  if (typeof value !== "object" || value === null) {
    return value;
  }
  const resolvedRelativeSchema = relativeSchema && resolveSchema(relativeSchema, reader);
  if (Array.isArray(value)) {
    const itemsSchema = resolvedRelativeSchema?.type === "array" ? resolvedRelativeSchema.items : void 0;
    return value.map((x) => internalSort(x, itemsSchema, reader));
  }
  const objectSchema = resolvedRelativeSchema;
  const properties = objectSchema?.properties && Object.keys(objectSchema.properties);
  const keys = Object.keys(value);
  const ordering = objectSchema?.["x-ordering"];
  if (ordering === "url") {
    keys.sort(compareUrl);
  } else if (ordering !== "keep") {
    keys.sort((a, b) => {
      if (properties) {
        const aIndex = properties.indexOf(a);
        const bIndex = properties.indexOf(b);
        if (aIndex !== -1 && bIndex !== -1) {
          return aIndex - bIndex;
        } else if (aIndex !== -1) {
          return -1;
        } else if (bIndex !== -1) {
          return 1;
        }
      }
      return defaultCompare(a, b);
    });
  }
  return keys.reduce((o, key) => {
    const v = value[key];
    const propertySchema = objectSchema?.properties?.[key] ?? resolvePatternProperties(key, objectSchema?.patternProperties) ?? resolveAdditionalProperties(objectSchema?.unevaluatedProperties) ?? resolveAdditionalProperties(objectSchema?.additionalProperties);
    if (propertySchema !== void 0) {
      o[key] = internalSort(v, propertySchema, reader);
    } else {
      o[key] = v;
    }
    return o;
  }, {});
}
function defaultCompare(a, b) {
  return +(a > b) || -(b > a);
}
function compareUrl(leftPath, rightPath) {
  const leftParts = leftPath.split("/").slice(1);
  const rightParts = rightPath.split("/").slice(1);
  for (let i = 0; i < Math.max(leftParts.length, rightParts.length); i++) {
    if (i === leftParts.length)
      return -1;
    if (i === rightParts.length)
      return 1;
    const leftIsField = leftParts[i][0] === "{";
    const rightIsField = rightParts[i][0] === "{";
    if (leftIsField && rightIsField) {
      continue;
    }
    if (leftIsField || rightIsField) {
      return leftIsField ? -1 : 1;
    }
    const result = defaultCompare(leftParts[i], rightParts[i]);
    if (result !== 0) {
      return result;
    }
  }
  return 0;
}
function resolveSchema(schema, reader) {
  if ("$ref" in schema) {
    return reader.resolveRef(schema.$ref);
  } else {
    return schema;
  }
}
function resolveJsonRef(ref, baseSchema) {
  const [file, path] = ref.split("#");
  if (file !== "") {
    throw new Error(`JsonSchemaSorter: Not supporting cross file ref: "${ref}".`);
  }
  const segments = path.split("/");
  let current = baseSchema;
  for (const segment of segments.slice(1)) {
    if (segment in current) {
      current = current[segment];
    } else {
      throw new Error(`JsonSchemaSorter: ref "${ref}" is invalid`);
    }
  }
  return current;
}
function resolvePatternProperties(key, patternProperties) {
  if (patternProperties === void 0) {
    return void 0;
  }
  for (const [pattern, schema] of Object.entries(patternProperties)) {
    if (key.match(pattern)) {
      return schema;
    }
  }
  return void 0;
}
function resolveAdditionalProperties(additionalProperties) {
  if (typeof additionalProperties === "boolean") {
    return void 0;
  }
  return additionalProperties;
}
var JsonSchemaReader = class {
  #doc;
  #defs = /* @__PURE__ */ new Map();
  constructor(doc) {
    this.#doc = doc;
    if (doc.$defs) {
      for (const value of Object.values(doc.$defs)) {
        if ("$id" in value && value.$id) {
          this.#defs.set(value.$id, value);
        }
      }
    }
  }
  resolveRef(ref) {
    if (ref.includes("#")) {
      return resolveJsonRef(ref, this.#doc);
    } else {
      const schema = this.#defs.get(ref);
      if (schema === void 0) {
        throw new Error(`JsonSchemaSorter: Cannot find schema with $id ${ref}`);
      }
      if ("$ref" in schema) {
        return this.resolveRef(schema.$ref);
      } else {
        return schema;
      }
    }
  }
};

// src/typespec/packages/typespec-autorest/dist/src/utils.js
import { getClientNameOverride } from "@azure-tools/typespec-client-generator-core";
import { getFriendlyName, getLifecycleVisibilityEnum, getVisibilityForClass, isGlobalNamespace, isService, isTemplateInstance } from "@typespec/compiler";
import { getOperationId } from "@typespec/openapi";

// src/typespec/node_modules/.pnpm/change-case@5.4.4/node_modules/change-case/dist/index.js
var SPLIT_LOWER_UPPER_RE = /([\p{Ll}\d])(\p{Lu})/gu;
var SPLIT_UPPER_UPPER_RE = /(\p{Lu})([\p{Lu}][\p{Ll}])/gu;
var SPLIT_SEPARATE_NUMBER_RE = /(\d)\p{Ll}|(\p{L})\d/u;
var DEFAULT_STRIP_REGEXP = /[^\p{L}\d]+/giu;
var SPLIT_REPLACE_VALUE = "$1\0$2";
var DEFAULT_PREFIX_SUFFIX_CHARACTERS = "";
function split(value) {
  let result = value.trim();
  result = result.replace(SPLIT_LOWER_UPPER_RE, SPLIT_REPLACE_VALUE).replace(SPLIT_UPPER_UPPER_RE, SPLIT_REPLACE_VALUE);
  result = result.replace(DEFAULT_STRIP_REGEXP, "\0");
  let start = 0;
  let end = result.length;
  while (result.charAt(start) === "\0")
    start++;
  if (start === end)
    return [];
  while (result.charAt(end - 1) === "\0")
    end--;
  return result.slice(start, end).split(/\0/g);
}
function splitSeparateNumbers(value) {
  const words = split(value);
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    const match = SPLIT_SEPARATE_NUMBER_RE.exec(word);
    if (match) {
      const offset = match.index + (match[1] ?? match[2]).length;
      words.splice(i, 1, word.slice(0, offset), word.slice(offset));
    }
  }
  return words;
}
function pascalCase(input, options) {
  const [prefix, words, suffix] = splitPrefixSuffix(input, options);
  const lower = lowerFactory(options?.locale);
  const upper = upperFactory(options?.locale);
  const transform = options?.mergeAmbiguousCharacters ? capitalCaseTransformFactory(lower, upper) : pascalCaseTransformFactory(lower, upper);
  return prefix + words.map(transform).join(options?.delimiter ?? "") + suffix;
}
function lowerFactory(locale) {
  return locale === false ? (input) => input.toLowerCase() : (input) => input.toLocaleLowerCase(locale);
}
function upperFactory(locale) {
  return locale === false ? (input) => input.toUpperCase() : (input) => input.toLocaleUpperCase(locale);
}
function capitalCaseTransformFactory(lower, upper) {
  return (word) => `${upper(word[0])}${lower(word.slice(1))}`;
}
function pascalCaseTransformFactory(lower, upper) {
  return (word, index) => {
    const char0 = word[0];
    const initial = index > 0 && char0 >= "0" && char0 <= "9" ? "_" + char0 : upper(char0);
    return initial + lower(word.slice(1));
  };
}
function splitPrefixSuffix(input, options = {}) {
  const splitFn = options.split ?? (options.separateNumbers ? splitSeparateNumbers : split);
  const prefixCharacters = options.prefixCharacters ?? DEFAULT_PREFIX_SUFFIX_CHARACTERS;
  const suffixCharacters = options.suffixCharacters ?? DEFAULT_PREFIX_SUFFIX_CHARACTERS;
  let prefixIndex = 0;
  let suffixIndex = input.length;
  while (prefixIndex < input.length) {
    const char = input.charAt(prefixIndex);
    if (!prefixCharacters.includes(char))
      break;
    prefixIndex++;
  }
  while (suffixIndex > prefixIndex) {
    const index = suffixIndex - 1;
    const char = input.charAt(index);
    if (!suffixCharacters.includes(char))
      break;
    suffixIndex = index;
  }
  return [
    input.slice(0, prefixIndex),
    splitFn(input.slice(prefixIndex, suffixIndex)),
    input.slice(suffixIndex)
  ];
}

// src/typespec/packages/typespec-autorest/dist/src/utils.js
function getClientName(context, type) {
  const clientName = getClientNameOverride(context.tcgcSdkContext, type);
  return clientName ?? type.name;
}
function resolveOperationId(context, operation) {
  const { program } = context;
  const explicitOperationId = getOperationId(program, operation);
  if (explicitOperationId) {
    return explicitOperationId;
  }
  const operationName = getClientName(context, operation);
  if (operation.interface) {
    return pascalCaseForOperationId(`${getClientName(context, operation.interface)}_${operationName}`);
  }
  const namespace2 = operation.namespace;
  if (namespace2 === void 0 || isGlobalNamespace(program, namespace2) || isService(program, namespace2)) {
    return pascalCase(operationName);
  }
  return pascalCaseForOperationId(`${namespace2.name}_${operationName}`);
}
function pascalCaseForOperationId(name) {
  return name.split("_").map((s) => pascalCase(s)).join("_");
}

// src/typespec/packages/typespec-autorest/dist/src/openapi.js
var Ref = class {
  value;
  toJSON() {
    compilerAssert(this.value, "Reference value never set.");
    return this.value;
  }
};
async function getOpenAPIForService(context, options) {
  const { program, service } = context;
  const typeNameOptions = {
    // shorten type names by removing TypeSpec and service namespace
    namespaceFilter(ns) {
      return !isService2(program, ns);
    }
  };
  const info = resolveInfo(program, service.type);
  const auth = processAuth(service.type);
  const root = {
    swagger: "2.0",
    info: {
      title: "(title)",
      ...info,
      version: context.version ?? info?.version ?? "0000-00-00",
      "x-typespec-generated": [{ emitter: "@azure-tools/typespec-autorest" }]
    },
    schemes: ["https"],
    ...resolveHost(program, service.type),
    externalDocs: getExternalDocs(program, service.type),
    produces: [],
    // Pre-initialize produces and consumes so that
    consumes: [],
    // they show up at the top of the document
    security: auth?.security,
    securityDefinitions: auth?.securitySchemes ?? {},
    tags: [],
    paths: {},
    "x-ms-paths": {},
    definitions: {},
    parameters: {}
  };
  let currentEndpoint;
  let currentConsumes;
  let currentProduces;
  const metadataInfo = createMetadataInfo(program, {
    canonicalVisibility: Visibility.Read,
    canShareProperty: canSharePropertyUsingReadonlyOrXMSMutability
  });
  const pendingSchemas = new TwoLevelMap();
  const refs = new TwoLevelMap();
  const inProgressInlineTypes = /* @__PURE__ */ new Set();
  const params = /* @__PURE__ */ new Map();
  const paramModels = /* @__PURE__ */ new Set();
  const tags = /* @__PURE__ */ new Set();
  const globalProduces = /* @__PURE__ */ new Set(["application/json"]);
  const globalConsumes = /* @__PURE__ */ new Set(["application/json"]);
  const operationIdsWithExample = /* @__PURE__ */ new Set();
  const [exampleMap, diagnostics] = await loadExamples(program, options, context.version);
  program.reportDiagnostics(diagnostics);
  const httpService = ignoreDiagnostics(getHttpService(program, service.type));
  const routes = httpService.operations;
  reportIfNoRoutes(program, routes);
  routes.forEach(emitOperation);
  emitParameters();
  emitSchemas(service.type);
  emitTags();
  if (globalProduces.size > 0) {
    root.produces = [...globalProduces.values()];
  } else {
    delete root.produces;
  }
  if (globalConsumes.size > 0) {
    root.consumes = [...globalConsumes.values()];
  } else {
    delete root.consumes;
  }
  if (root["x-ms-paths"] && Object.keys(root["x-ms-paths"]).length === 0) {
    delete root["x-ms-paths"];
  }
  if (root.security && Object.keys(root.security).length === 0) {
    delete root["security"];
  }
  if (root.securityDefinitions && Object.keys(root.securityDefinitions).length === 0) {
    delete root["securityDefinitions"];
  }
  return {
    document: root,
    operationExamples: [...operationIdsWithExample].map((operationId) => {
      const data = exampleMap.get(operationId);
      if (data) {
        return { operationId, examples: Object.values(data) };
      } else {
        return void 0;
      }
    }).filter((x) => x),
    outputFile: context.outputFile
  };
  function resolveHost(program2, namespace2) {
    const servers = getServers(program2, namespace2);
    if (servers === void 0) {
      return {};
    }
    if (servers.length > 1) {
      return {
        "x-ms-parameterized-host": {
          hostTemplate: "{url}",
          useSchemePrefix: false,
          parameters: [
            {
              name: "url",
              in: "path",
              description: "Url",
              type: "string",
              format: "uri",
              "x-ms-skip-url-encoding": true
            }
          ]
        }
      };
    }
    const server = servers[0];
    if (server.parameters.size === 0) {
      const [scheme, host] = server.url.split("://");
      return {
        host,
        schemes: [scheme]
      };
    }
    const parameters = [];
    for (const prop of server.parameters.values()) {
      const param = getOpenAPI2Parameter({
        kind: "path",
        path: [],
        property: prop,
        options: {
          allowReserved: false,
          explode: false,
          style: "simple",
          name: prop.name
        }
      }, {
        visibility: Visibility.Read,
        ignoreMetadataAnnotations: false
      });
      if (prop.type.kind === "Scalar" && $(program2).type.isAssignableTo(prop.type, $(program2).builtin.url, prop.type)) {
        param["x-ms-skip-url-encoding"] = true;
      }
      parameters.push(param);
    }
    return {
      "x-ms-parameterized-host": {
        hostTemplate: server.url,
        useSchemePrefix: false,
        parameters
      }
    };
  }
  function getLastSegment(segments) {
    if (segments) {
      return segments[segments.length - 1];
    }
    return void 0;
  }
  function extractPagedMetadataNested(program2, type) {
    let paged = getPagedResult(program2, type);
    if (paged) {
      return paged;
    }
    if (type.baseModel) {
      paged = getPagedResult(program2, type.baseModel);
    }
    if (paged) {
      return paged;
    }
    const templateArguments = type.templateMapper;
    if (templateArguments) {
      for (const argument of templateArguments.args) {
        const modelArgument = argument;
        if (modelArgument) {
          paged = extractPagedMetadataNested(program2, modelArgument);
          if (paged) {
            return paged;
          }
        }
      }
    }
    return paged;
  }
  function resolveXmsPageable(program2, operation) {
    if (isList(program2, operation.operation)) {
      const pagedInfo = ignoreDiagnostics(getPagingOperation(program2, operation.operation));
      return pagedInfo && getXmsPageableForPagingOperation(pagedInfo);
    } else {
      return extractAzureCorePagedMetadata(program2, operation);
    }
  }
  function getXmsPageableForPagingOperation(paging) {
    if (paging.output.nextLink) {
      const itemsName = paging.output.pageItems.property.name;
      return {
        nextLinkName: paging.output.nextLink.property.name,
        itemName: itemsName === "items" ? void 0 : itemsName
      };
    }
    return void 0;
  }
  function extractAzureCorePagedMetadata(program2, operation) {
    for (const response of operation.responses) {
      const paged = extractPagedMetadataNested(program2, response.type);
      if (paged) {
        const nextLinkName = getLastSegment(paged.nextLinkSegments);
        const itemName = getLastSegment(paged.itemsSegments);
        if (nextLinkName) {
          return {
            nextLinkName,
            itemName: itemName !== "value" ? itemName : void 0
          };
        }
        return void 0;
      }
    }
    return void 0;
  }
  function requiresXMsPaths(path, operation) {
    const isShared = isSharedRoute(program, operation) ?? false;
    if (path.includes("?")) {
      return true;
    }
    return isShared;
  }
  function getPathWithoutQuery(path) {
    return path.replace(/\/?\?.*/, "");
  }
  function getFinalStateVia(metadata) {
    switch (metadata.finalStateVia) {
      case FinalStateValue.azureAsyncOperation:
        return "azure-async-operation";
      case FinalStateValue.location:
        return "location";
      case FinalStateValue.operationLocation:
        return "operation-location";
      case FinalStateValue.originalUri:
        return "original-uri";
      default:
        return void 0;
    }
  }
  function getFinalStateSchema(metadata) {
    if (metadata.finalResult !== void 0 && metadata.finalResult !== "void" && metadata.finalResult.name.length > 0) {
      const model = metadata.finalResult;
      const schemaOrRef = resolveExternalRef(metadata.finalResult);
      if (schemaOrRef !== void 0) {
        const ref = new Ref();
        ref.value = schemaOrRef.$ref;
        return { "final-state-schema": ref };
      }
      const pending = pendingSchemas.getOrAdd(metadata.finalResult, Visibility.Read, () => ({
        type: model,
        visibility: Visibility.Read,
        ref: refs.getOrAdd(model, Visibility.Read, () => new Ref())
      }));
      return { "final-state-schema": pending.ref };
    }
    return void 0;
  }
  function emitOperation(operation) {
    let { path: fullPath, operation: op, verb, parameters } = operation;
    let pathsObject = root.paths;
    const pathWithoutAnyQuery = getPathWithoutQuery(fullPath);
    if (root.paths[pathWithoutAnyQuery]?.[verb] === void 0) {
      fullPath = pathWithoutAnyQuery;
      pathsObject = root.paths;
    } else if (requiresXMsPaths(fullPath, op)) {
      if (fullPath.includes("?")) {
        if (root["x-ms-paths"]?.[fullPath] !== void 0) {
          fullPath += `&_overload=${operation.operation.name}`;
        }
      } else {
        fullPath += `?_overload=${operation.operation.name}`;
      }
      pathsObject = root["x-ms-paths"];
    } else {
      compilerAssert(false, `Duplicate route "${fullPath}". This is unexpected.`);
    }
    if (!pathsObject[fullPath]) {
      pathsObject[fullPath] = {};
    }
    const currentPath = pathsObject[fullPath];
    if (!currentPath[verb]) {
      currentPath[verb] = {};
    }
    currentEndpoint = currentPath[verb];
    currentConsumes = /* @__PURE__ */ new Set();
    currentProduces = /* @__PURE__ */ new Set();
    const currentTags = getAllTags(program, op);
    if (currentTags) {
      currentEndpoint.tags = currentTags;
      for (const tag of currentTags) {
        tags.add(tag);
      }
    }
    currentEndpoint.operationId = resolveOperationId(context, op);
    applyExternalDocs(op, currentEndpoint);
    currentEndpoint.summary = getSummary(program, op);
    currentEndpoint.description = getDoc(program, op);
    currentEndpoint.parameters = [];
    currentEndpoint.responses = {};
    const lroMetadata = getLroMetadata(program, op);
    if (lroMetadata !== void 0 && operation.verb !== "get") {
      currentEndpoint["x-ms-long-running-operation"] = true;
      if (options.emitLroOptions !== "none") {
        const finalState = getFinalStateVia(lroMetadata);
        if (finalState !== void 0) {
          const finalSchema = getFinalStateSchema(lroMetadata);
          let lroOptions = {
            "final-state-via": finalState
          };
          if (finalSchema !== void 0 && options.emitLroOptions === "all") {
            lroOptions = {
              "final-state-via": finalState,
              ...finalSchema
            };
          }
          currentEndpoint["x-ms-long-running-operation-options"] = lroOptions;
        }
      }
    }
    const pageable = resolveXmsPageable(program, operation);
    if (pageable) {
      currentEndpoint["x-ms-pageable"] = pageable;
    }
    const visibility = resolveRequestVisibility(program, operation.operation, verb);
    emitEndpointParameters(parameters, visibility);
    emitResponses(operation.responses);
    applyEndpointConsumes();
    applyEndpointProduces();
    if (isDeprecated(program, op)) {
      currentEndpoint.deprecated = true;
    }
    const examples = getExamples(program, op);
    if (examples) {
      currentEndpoint["x-ms-examples"] = examples.reduce((acc, example) => ({ ...acc, [example.title]: { $ref: example.pathOrUri } }), {});
    }
    const autoExamples = exampleMap.get(currentEndpoint.operationId);
    if (autoExamples && currentEndpoint.operationId) {
      operationIdsWithExample.add(currentEndpoint.operationId);
      currentEndpoint["x-ms-examples"] = currentEndpoint["x-ms-examples"] || {};
      for (const [title, example] of Object.entries(autoExamples)) {
        currentEndpoint["x-ms-examples"][title] = { $ref: `./examples/${example.relativePath}` };
      }
    }
    attachExtensions(op, currentEndpoint);
  }
  function applyEndpointProduces() {
    if (currentProduces.size > 0 && !checkLocalAndGlobalEqual(globalProduces, currentProduces)) {
      currentEndpoint.produces = [...currentProduces];
    }
  }
  function applyEndpointConsumes() {
    if (currentConsumes.size > 0 && !checkLocalAndGlobalEqual(globalConsumes, currentConsumes)) {
      currentEndpoint.consumes = [...currentConsumes];
    }
  }
  function checkLocalAndGlobalEqual(global, local) {
    if (global.size !== local.size) {
      return false;
    }
    for (const entry of local) {
      if (!global.has(entry)) {
        return false;
      }
    }
    return true;
  }
  function isBytes(type) {
    return $(program).type.isAssignableTo(type, $(program).builtin.bytes, type);
  }
  function isBinaryPayload(body, contentType) {
    const types = new Set(typeof contentType === "string" ? [contentType] : contentType);
    return body.kind === "Scalar" && body.name === "bytes" && !types.has("application/json") && !types.has("text/plain");
  }
  function emitResponses(responses) {
    for (const response of responses) {
      for (const statusCode of getOpenAPI2StatusCodes(response.statusCodes, response.type)) {
        emitResponseObject(statusCode, response);
      }
    }
  }
  function getOpenAPI2StatusCodes(statusCodes, diagnosticTarget) {
    if (statusCodes === "*") {
      return ["default"];
    } else if (typeof statusCodes === "number") {
      return [String(statusCodes)];
    } else {
      return rangeToOpenAPI(statusCodes, diagnosticTarget);
    }
  }
  function rangeToOpenAPI(range, diagnosticTarget) {
    const reportInvalid = () => reportDiagnostic(program, {
      code: "unsupported-status-code-range",
      format: { start: String(range.start), end: String(range.end) },
      target: diagnosticTarget
    });
    const codes = [];
    let start = range.start;
    let end = range.end;
    if (range.start < 100) {
      reportInvalid();
      start = 100;
      codes.push("default");
    } else if (range.end > 599) {
      reportInvalid();
      codes.push("default");
      end = 599;
    }
    const groups = [1, 2, 3, 4, 5];
    for (const group of groups) {
      if (start > end) {
        break;
      }
      const groupStart = group * 100;
      const groupEnd = groupStart + 99;
      if (start >= groupStart && start <= groupEnd) {
        codes.push(`${group}XX`);
        if (start !== groupStart || end < groupEnd) {
          reportInvalid();
        }
        start = groupStart + 100;
      }
    }
    return codes;
  }
  function getResponseDescriptionForStatusCode(statusCode) {
    if (statusCode === "default") {
      return "An unexpected error response.";
    }
    return getStatusCodeDescription(statusCode) ?? "unknown";
  }
  function emitResponseObject(statusCode, response) {
    const openapiResponse = currentEndpoint.responses[statusCode] ?? {
      description: response.description ?? getResponseDescriptionForStatusCode(statusCode)
    };
    if (isErrorModel(program, response.type) && statusCode !== "default") {
      openapiResponse["x-ms-error-response"] = true;
    }
    const contentTypes = [];
    let body;
    for (const data of response.responses) {
      if (data.headers && Object.keys(data.headers).length > 0) {
        openapiResponse.headers ??= {};
        for (const [key, value] of Object.entries(data.headers)) {
          openapiResponse.headers[key] = getResponseHeader(value);
        }
      }
      if (data.body) {
        if (body && body.type !== data.body.type) {
          reportDiagnostic(program, {
            code: "duplicate-body-types",
            target: response.type
          });
        }
        body = data.body;
        contentTypes.push(...data.body.contentTypes);
      }
    }
    if (body) {
      openapiResponse.schema = getSchemaForResponseBody(body, contentTypes);
    }
    for (const contentType of contentTypes) {
      currentProduces.add(contentType);
    }
    currentEndpoint.responses[statusCode] = openapiResponse;
  }
  function getSchemaForResponseBody(body, contentTypes) {
    const isBinary = contentTypes.every((t) => isBinaryPayload(body.type, t));
    if (body.bodyKind === "file" || isBinary) {
      return { type: "file" };
    }
    if (body.bodyKind === "multipart") {
      return { type: "string" };
    }
    return getSchemaOrRef(body.type, {
      visibility: Visibility.Read,
      ignoreMetadataAnnotations: body.isExplicit && body.containsMetadataAnnotations
    });
  }
  function getResponseHeader(prop) {
    const header = getOpenAPI2HeaderParameter(prop, {
      visibility: Visibility.Read,
      ignoreMetadataAnnotations: false
    });
    Object.assign(header, applyIntrinsicDecorators(prop, {
      type: header.type,
      format: header.format
    }));
    delete header.in;
    delete header.name;
    delete header["x-ms-client-name"];
    delete header.required;
    return header;
  }
  function expandRef(ref) {
    const absoluteRef = interpolatePath(ref, {
      "arm-types-dir": options.armTypesDir
    });
    if (getRootLength(absoluteRef) === 0) {
      return absoluteRef;
    }
    return getRelativePathFromDirectory(getDirectoryPath(context.outputFile), absoluteRef, false);
  }
  function resolveExternalRef(type) {
    const refUrl = getRef(program, type);
    if (refUrl) {
      return {
        $ref: expandRef(refUrl)
      };
    }
    const externalTypeRefUrl = getExternalTypeRef(program, type);
    if (externalTypeRefUrl) {
      return {
        $ref: expandRef(externalTypeRefUrl)
      };
    }
    if (isArmCommonType(type) && (type.kind === "Model" || type.kind === "ModelProperty" || type.kind === "Enum" || type.kind === "Union")) {
      const ref = getArmCommonTypeOpenAPIRef(program, type, {
        version: context.version,
        service: context.service
      });
      if (ref) {
        return {
          $ref: expandRef(ref)
        };
      }
    }
    return void 0;
  }
  function getSchemaOrRef(type, schemaContext, namespace2) {
    let schemaNameOverride = void 0;
    const ref = resolveExternalRef(type);
    if (ref) {
      if (options.emitCommonTypesSchema === "never" || !metadataInfo.isTransformed(type, schemaContext.visibility)) {
        return ref;
      }
      schemaNameOverride = (n, v) => `${n}${getVisibilitySuffix(v, Visibility.Read)}`;
    }
    if (type.kind === "Scalar" && program.checker.isStdType(type)) {
      return getSchemaForScalar(type);
    }
    if (type.kind === "String" || type.kind === "Number" || type.kind === "Boolean") {
      return getSchemaForLiterals(type);
    }
    if (type.kind === "StringTemplate") {
      return getSchemaForStringTemplate(type);
    }
    if (type.kind === "Intrinsic" && type.name === "unknown") {
      return getSchemaForIntrinsicType(type);
    }
    if (type.kind === "EnumMember") {
      if (typeof type.value === "number") {
        return { type: "number", enum: [type.value] };
      } else {
        return { type: "string", enum: [type.value ?? type.name] };
      }
    }
    if (type.kind === "ModelProperty") {
      return resolveProperty(type, schemaContext);
    }
    type = metadataInfo.getEffectivePayloadType(type, schemaContext.visibility);
    const name = getOpenAPITypeName(program, type, typeNameOptions);
    if (shouldInline(program, type)) {
      const schema = getSchemaForInlineType(type, name, schemaContext, namespace2);
      if (schema === void 0 && isErrorType(type)) {
        throw new ErrorTypeFoundError();
      }
      if (schema && options.includeXTypeSpecName !== "never") {
        schema["x-typespec-name"] = name;
      }
      return schema;
    } else {
      if (!metadataInfo.isTransformed(type, schemaContext.visibility)) {
        schemaContext = { ...schemaContext, visibility: Visibility.Read };
      }
      const pending = pendingSchemas.getOrAdd(type, schemaContext.visibility, () => ({
        type,
        visibility: schemaContext.visibility,
        ref: refs.getOrAdd(type, schemaContext.visibility, () => new Ref()),
        getSchemaNameOverride: schemaNameOverride
      }));
      return { $ref: pending.ref };
    }
  }
  function getSchemaForInlineType(type, name, context2, namespace2) {
    if (inProgressInlineTypes.has(type)) {
      reportDiagnostic(program, {
        code: "inline-cycle",
        format: { type: name },
        target: type
      });
      return {};
    }
    inProgressInlineTypes.add(type);
    const schema = getSchemaForType(type, context2, namespace2);
    inProgressInlineTypes.delete(type);
    return schema;
  }
  function getParamPlaceholder(property) {
    let spreadParam = false;
    if (property.sourceProperty) {
      spreadParam = true;
      property = property.sourceProperty;
      while (property.sourceProperty) {
        property = property.sourceProperty;
      }
    }
    const ref = resolveExternalRef(property);
    if (ref) {
      return ref;
    }
    const parameter = params.get(property);
    if (parameter) {
      return parameter;
    }
    const placeholder = {};
    if (spreadParam && property.model && !shouldInline(program, property.model)) {
      params.set(property, placeholder);
      paramModels.add(property.model);
    }
    return placeholder;
  }
  function getJsonName(type) {
    const encodedName = resolveEncodedName(program, type, "application/json");
    return encodedName === type.name ? type.name : encodedName;
  }
  function emitEndpointParameters(methodParams, visibility) {
    const consumes = methodParams.body?.contentTypes ?? [];
    for (const httpProperty of methodParams.properties) {
      const shared = params.get(httpProperty.property);
      if (shared) {
        currentEndpoint.parameters.push(shared);
        continue;
      }
      if (!isHttpParameterProperty(httpProperty)) {
        continue;
      }
      if (httpProperty.kind === "cookie") {
        reportDiagnostic(program, { code: "cookies-unsupported", target: httpProperty.property });
        continue;
      }
      emitParameter(httpProperty.property, () => getOpenAPI2Parameter(httpProperty, { visibility, ignoreMetadataAnnotations: false }));
    }
    if (consumes.length === 0 && methodParams.body) {
      if (getModelOrScalarTypeIfNullable(methodParams.body.type)) {
        consumes.push("application/json");
      }
    }
    for (const consume of consumes) {
      currentConsumes.add(consume);
    }
    if (methodParams.body && !isVoidType(methodParams.body.type)) {
      emitBodyParameters(methodParams.body, visibility);
    }
  }
  function emitBodyParameters(body, visibility) {
    switch (body.bodyKind) {
      case "single":
        emitSingleBodyParameters(body, visibility);
        break;
      case "multipart":
        emitMultipartBodyParameters(body, visibility);
        break;
      case "file":
        const bodySchema = { type: "string", format: "binary" };
        const { property } = body;
        if (property) {
          emitParameter(property, () => getOpenAPI2BodyParameter(property, property.name, bodySchema));
        } else {
          currentEndpoint.parameters.push({
            name: "body",
            in: "body",
            schema: {
              type: "string",
              format: "binary"
            },
            required: true
          });
        }
        break;
    }
  }
  function emitSingleBodyParameters(body, visibility) {
    const isBinary = isBinaryPayload(body.type, body.contentTypes);
    const schemaContext = {
      visibility,
      ignoreMetadataAnnotations: body.isExplicit && body.containsMetadataAnnotations
    };
    const schema = isBinary ? { type: "string", format: "binary" } : getSchemaOrRef(body.type, schemaContext);
    if (body.property) {
      const prop = body.property;
      emitParameter(prop, () => getOpenAPI2BodyParameter(prop, getJsonName(prop), schema));
    } else {
      currentEndpoint.parameters.push({
        name: "body",
        in: "body",
        schema,
        required: true
      });
    }
  }
  function emitMultipartBodyParameters(body, visibility) {
    for (const [index, part] of body.parts.entries()) {
      const partName = part.name ?? `part${index}`;
      let schema = getFormDataSchema(part.body.type, { visibility, ignoreMetadataAnnotations: false }, partName, part.body.type);
      if (schema) {
        if (part.multi) {
          schema = {
            type: "array",
            items: schema.type === "file" ? { type: "string", format: "binary" } : schema
          };
        }
        const param = {
          name: partName,
          in: "formData",
          required: !part.optional,
          ...schema
        };
        if (part.property) {
          param.description = getDoc(program, part.property);
          if (part.property.name !== partName) {
            param["x-ms-client-name"] = part.property.name;
          }
        }
        currentEndpoint.parameters.push(param);
      }
    }
  }
  function getModelOrScalarTypeIfNullable(type) {
    if (type.kind === "Model" || type.kind === "Scalar") {
      return type;
    } else if (type.kind === "Union") {
      const nonNulls = [...type.variants.values()].map((x) => x.type).filter((variant) => !isNullType(variant));
      if (nonNulls.every((t) => t.kind === "Model" || t.kind === "Scalar")) {
        return nonNulls.length === 1 ? nonNulls[0] : void 0;
      }
    }
    return void 0;
  }
  function emitParameter(prop, resolve) {
    if (isNeverType(prop.type)) {
      return;
    }
    const ph = getParamPlaceholder(prop);
    currentEndpoint.parameters.push(ph);
    if (!("$ref" in ph)) {
      Object.assign(ph, resolve());
    }
  }
  function getSchemaForPrimitiveItems(type, schemaContext, paramName, target, multipart) {
    const fullSchema = getSchemaForType(type, schemaContext);
    if (fullSchema === void 0) {
      return void 0;
    }
    if (fullSchema.type === "object") {
      reportDiagnostic(program, {
        code: multipart ? "unsupported-multipart-type" : "unsupported-param-type",
        format: { part: paramName },
        target
      });
      return { type: "string" };
    }
    return fullSchema;
  }
  function getFormDataSchema(type, schemaContext, paramName, target) {
    if (isBytes(type)) {
      return { type: "file" };
    }
    if (type.kind === "Model" && isArrayModelType(program, type)) {
      const elementType = type.indexer.value;
      if (isBytes(elementType)) {
        return { type: "array", items: { type: "string", format: "binary" } };
      }
      const schema = getSchemaForPrimitiveItems(elementType, schemaContext, paramName, target, true);
      if (schema === void 0) {
        return void 0;
      }
      delete schema.description;
      return {
        type: "array",
        items: schema
      };
    } else {
      const schema = getSchemaForPrimitiveItems(type, schemaContext, paramName, target, true);
      if (schema === void 0) {
        return void 0;
      }
      return schema;
    }
  }
  function getOpenAPI2ParameterBase(param, name) {
    const base = {
      name: name ?? param.name,
      required: !param.optional,
      description: getDoc(program, param)
    };
    const clientName = getClientName(context, param);
    if (name !== clientName) {
      base["x-ms-client-name"] = clientName;
    }
    attachExtensions(param, base);
    return base;
  }
  function getOpenAPI2BodyParameter(param, name, bodySchema) {
    const result = {
      in: "body",
      ...getOpenAPI2ParameterBase(param, name),
      schema: bodySchema
    };
    const jsonName = getJsonName(param);
    if (jsonName !== param.name) {
      reportDeprecated(program, "Using encodedName for the body property is meaningless. That property is not serialized as Json. If wanting to rename it use @Azure.ClientGenerator.Core.clientName", param.decorators.find((x) => x.definition?.name === "@encodedName")?.node ?? param);
      result.name = jsonName;
      if (!result["x-ms-client-name"]) {
        result["x-ms-client-name"] = param.name;
      }
    } else {
      if (result["x-ms-client-name"]) {
        result.name = result["x-ms-client-name"];
        delete result["x-ms-client-name"];
      }
    }
    return result;
  }
  function getSimpleParameterSchema(param, schemaContext, name) {
    if (param.type.kind === "Model" && isArrayModelType(program, param.type)) {
      const itemSchema = getSchemaForPrimitiveItems(param.type.indexer.value, schemaContext, name, param);
      const schema = itemSchema && {
        ...itemSchema
      };
      delete schema.description;
      return { type: "array", items: schema };
    } else {
      return getSchemaForPrimitiveItems(param.type, schemaContext, name, param);
    }
  }
  function getCollectionFormat(type, explode) {
    if ($(program).array.is(type.type)) {
      if (explode) {
        return "multi";
      }
      const encode = getEncode(context.program, type);
      if (encode) {
        if (encode?.encoding === "ArrayEncoding.pipeDelimited") {
          return "pipes";
        }
        if (encode?.encoding === "ArrayEncoding.spaceDelimited") {
          return "ssv";
        }
        reportDiagnostic(program, { code: "invalid-multi-collection-format", target: type });
      }
      return "csv";
    }
    return void 0;
  }
  function getOpenAPI2QueryParameter(httpProp, schemaContext) {
    const property = httpProp.property;
    const base = getOpenAPI2ParameterBase(property, httpProp.options.name);
    const collectionFormat = getCollectionFormat(httpProp.property, httpProp.options.explode);
    const schema = getSimpleParameterSchema(property, schemaContext, base.name);
    return {
      in: "query",
      collectionFormat,
      default: property.defaultValue && getDefaultValue(property.defaultValue, property),
      ...base,
      ...schema
    };
  }
  function getOpenAPI2PathParameter(httpProp, schemaContext) {
    const property = httpProp.property;
    const base = getOpenAPI2ParameterBase(property, httpProp.options.name);
    const result = {
      in: "path",
      default: property.defaultValue && getDefaultValue(property.defaultValue, property),
      ...base,
      ...getSimpleParameterSchema(property, schemaContext, base.name)
    };
    if (httpProp.options.allowReserved) {
      result["x-ms-skip-url-encoding"] = true;
    }
    return result;
  }
  function getOpenAPI2HeaderParameter(prop, schemaContext, name) {
    const base = getOpenAPI2ParameterBase(prop, name);
    const headerOptions = getHeaderFieldOptions(program, prop);
    const collectionFormat = getCollectionFormat(prop, headerOptions.explode);
    return {
      in: "header",
      default: prop.defaultValue && getDefaultValue(prop.defaultValue, prop),
      ...base,
      collectionFormat,
      ...getSimpleParameterSchema(prop, schemaContext, base.name)
    };
  }
  function getOpenAPI2ParameterInternal(httpProperty, schemaContext) {
    switch (httpProperty.kind) {
      case "query":
        return getOpenAPI2QueryParameter(httpProperty, schemaContext);
      case "path":
        return getOpenAPI2PathParameter(httpProperty, schemaContext);
      case "header":
        return getOpenAPI2HeaderParameter(httpProperty.property, schemaContext, httpProperty.options.name);
      case "cookie":
        compilerAssert(false, "Should verify cookies before");
        break;
      default:
        const _assertNever = httpProperty;
        compilerAssert(false, "Unreachable");
    }
  }
  function getOpenAPI2Parameter(httpProp, schemaContext) {
    const value = getOpenAPI2ParameterInternal(httpProp, schemaContext);
    Object.assign(value, applyIntrinsicDecorators(httpProp.property, {
      type: value.type,
      format: value.format
    }));
    return value;
  }
  function emitParameters() {
    for (const [property, param] of params) {
      if (param["x-ms-parameter-location"] === void 0) {
        param["x-ms-parameter-location"] = "method";
      }
      const key = getParameterKey(program, property, param, root.parameters, typeNameOptions);
      root.parameters[key] = { ...param };
      const refedParam = param;
      for (const key2 of Object.keys(param)) {
        delete refedParam[key2];
      }
      refedParam["$ref"] = "#/parameters/" + encodeURIComponent(key);
    }
  }
  function emitSchemas(serviceNamespace) {
    const processedSchemas = new TwoLevelMap();
    processSchemas();
    if (!options.omitUnreachableTypes) {
      processUnreferencedSchemas();
    }
    for (const group of processedSchemas.values()) {
      for (const [visibility, processed] of group) {
        let name = getClientNameOverride2(context.tcgcSdkContext, processed.type);
        if (name === void 0) {
          name = getOpenAPITypeName(program, processed.type, typeNameOptions);
        }
        if (processed.getSchemaNameOverride !== void 0) {
          name = processed.getSchemaNameOverride(name, visibility);
        } else if (group.size > 1) {
          name += getVisibilitySuffix(visibility, Visibility.Read);
        }
        checkDuplicateTypeName(program, processed.type, name, root.definitions);
        processed.ref.value = "#/definitions/" + encodeURIComponent(name);
        if (processed.schema) {
          root.definitions[name] = processed.schema;
        }
      }
    }
    function processSchemas() {
      while (pendingSchemas.size > 0) {
        for (const [type, group] of pendingSchemas) {
          for (const [visibility, pending] of group) {
            processedSchemas.getOrAdd(type, visibility, () => ({
              ...pending,
              schema: getSchemaForType(type, {
                visibility,
                ignoreMetadataAnnotations: false
              })
            }));
          }
          pendingSchemas.delete(type);
        }
      }
    }
    function processUnreferencedSchemas() {
      const addSchema = (type) => {
        if (!processedSchemas.has(type) && !paramModels.has(type) && !shouldInline(program, type) && !shouldOmitThisUnreachableType(type)) {
          getSchemaOrRef(type, { visibility: Visibility.Read, ignoreMetadataAnnotations: false });
        }
      };
      const skipSubNamespaces = isGlobalNamespace2(program, serviceNamespace);
      navigateTypesInNamespace(serviceNamespace, {
        model: addSchema,
        scalar: addSchema,
        enum: addSchema,
        union: addSchema
      }, { skipSubNamespaces });
      processSchemas();
    }
    function shouldOmitThisUnreachableType(type) {
      if (options.versionEnumStrategy !== "include" && type.kind === "Enum" && isVersionEnum(program, type)) {
        return true;
      }
      return false;
    }
  }
  function isVersionEnum(program2, enumObj) {
    const [_, map] = getVersionsForEnum(program2, enumObj);
    if (map !== void 0 && map.getVersions()[0].enumMember.enum === enumObj) {
      return true;
    }
    return false;
  }
  function emitTags() {
    for (const tag of tags) {
      root.tags.push({ name: tag });
    }
  }
  function getSchemaForType(type, schemaContext, namespace2) {
    const builtinType = getSchemaForLiterals(type);
    if (builtinType !== void 0) {
      return builtinType;
    }
    switch (type.kind) {
      case "Intrinsic":
        return getSchemaForIntrinsicType(type);
      case "Model":
        return getSchemaForModel(type, schemaContext, namespace2);
      case "ModelProperty":
        return getSchemaForType(type.type, schemaContext);
      case "Scalar":
        return getSchemaForScalar(type);
      case "Union":
        return getSchemaForUnion(type, schemaContext);
      case "UnionVariant":
        return getSchemaForUnionVariant(type, schemaContext);
      case "Enum":
        return getSchemaForEnum(type);
      case "Tuple":
        return { type: "array", items: {} };
    }
    reportDiagnostic(program, {
      code: "invalid-schema",
      format: { type: type.kind },
      target: type
    });
    return void 0;
  }
  function getSchemaForIntrinsicType(type) {
    switch (type.name) {
      case "unknown":
        return {};
    }
    reportDiagnostic(program, {
      code: "invalid-schema",
      format: { type: type.name },
      target: type
    });
    return {};
  }
  function getSchemaForVersionEnum(e, currentVersion) {
    const member = [...e.members.values()].find((x) => (x.value ?? x.name) === currentVersion);
    compilerAssert(member, `Version enum ${e.name} does not have a member for ${currentVersion}.`, e);
    return {
      type: "string",
      description: getDoc(program, e),
      enum: [member.value ?? member.name],
      "x-ms-enum": {
        name: e.name,
        modelAsString: true,
        values: [
          {
            name: member.name,
            value: member.value ?? member.name,
            description: getDoc(program, member)
          }
        ]
      }
    };
  }
  function getSchemaForEnum(e) {
    const values = [];
    if (e.members.size === 0) {
      reportUnsupportedUnion("empty");
      return {};
    }
    const type = getEnumMemberType(e.members.values().next().value);
    for (const option of e.members.values()) {
      if (type !== getEnumMemberType(option)) {
        reportUnsupportedUnion();
        continue;
      } else {
        values.push(option.value ?? option.name);
      }
    }
    if (isVersionEnum(program, e) && context.version) {
      return getSchemaForVersionEnum(e, context.version);
    }
    const schema = { type, description: getDoc(program, e) };
    if (values.length > 0) {
      schema.enum = values;
      addXMSEnum(e, schema);
    }
    if (options.useReadOnlyStatusSchema) {
      const [values2, _] = extractLroStates(program, e);
      if (values2 !== void 0) {
        schema.readOnly = true;
      }
    }
    return schema;
    function getEnumMemberType(member) {
      if (typeof member.value === "number") {
        return "number";
      }
      return "string";
    }
    function reportUnsupportedUnion(messageId = "default") {
      reportDiagnostic(program, { code: "union-unsupported", messageId, target: e });
    }
  }
  function getSchemaForUnionEnum(union, e) {
    const values = [];
    let foundCustom = false;
    for (const [name, member] of e.flattenedMembers.entries()) {
      const description = getDoc(program, member.type);
      const memberClientName = getClientNameOverride2(context.tcgcSdkContext, member.type);
      values.push({
        name: memberClientName ?? (typeof name === "string" ? name : `${member.value}`),
        value: member.value,
        description
      });
      if (description || typeof name === "string") {
        foundCustom = true;
      }
    }
    const clientName = getClientName(context, union);
    const schema = {
      type: e.kind,
      enum: [...e.flattenedMembers.values()].map((x) => x.value),
      "x-ms-enum": {
        name: clientName ?? union.name,
        modelAsString: e.open
      }
    };
    if (foundCustom) {
      schema["x-ms-enum"].values = values;
    }
    if (e.nullable) {
      schema["x-nullable"] = true;
    }
    if (options.useReadOnlyStatusSchema) {
      const [values2, _] = extractLroStates(program, union);
      if (values2 !== void 0) {
        schema.readOnly = true;
      }
    }
    return applyIntrinsicDecorators(union, schema);
  }
  function getSchemaForUnion(union, schemaContext) {
    const nonNullOptions = [...union.variants.values()].map((x) => x.type).filter((t) => !isNullType(t));
    const nullable = union.variants.size !== nonNullOptions.length;
    if (nonNullOptions.length === 0) {
      reportDiagnostic(program, { code: "union-null", target: union });
      return {};
    }
    if (nonNullOptions.length === 1) {
      const type = nonNullOptions[0];
      const schema = getSchemaOrRef(type, schemaContext);
      if (schema.$ref) {
        return { ...schema, "x-nullable": nullable };
      } else {
        schema["x-nullable"] = nullable;
        return schema;
      }
    } else {
      const [asEnum, _] = getUnionAsEnum(union);
      if (asEnum) {
        return getSchemaForUnionEnum(union, asEnum);
      }
      reportDiagnostic(program, {
        code: "union-unsupported",
        target: union
      });
      return {};
    }
  }
  function ifArrayItemContainsIdentifier(program2, array) {
    if (array.indexer.value?.kind !== "Model") {
      return true;
    }
    return getExtensions(program2, array).has("x-ms-identifiers") || getProperty(array.indexer.value, "id");
  }
  function ifArmIdentifiersDefault(armIdentifiers) {
    return armIdentifiers.every((identifier) => identifier === "id" || identifier === "name");
  }
  function getSchemaForUnionVariant(variant, schemaContext) {
    return getSchemaForType(variant.type, schemaContext);
  }
  function getDefaultValue(defaultType, modelProperty) {
    return serializeValueAsJson(program, defaultType, modelProperty);
  }
  function includeDerivedModel(model) {
    return !resolveExternalRef(model) && !isTemplateDeclaration(model) && (model.templateMapper?.args === void 0 || model.templateMapper?.args.length === 0 || model.derivedModels.length > 0);
  }
  function getDiscriminatorValue(model) {
    let discriminator;
    let current = model;
    while (current.baseModel) {
      discriminator = getDiscriminator(program, current.baseModel);
      if (discriminator) {
        break;
      }
      current = current.baseModel;
    }
    if (discriminator === void 0) {
      return void 0;
    }
    const prop = getProperty(model, discriminator.propertyName);
    if (prop) {
      const values = getStringValues(prop.type);
      if (values.length === 1) {
        return values[0];
      }
    }
    return void 0;
  }
  function getSchemaForModel(model, schemaContext, namespace2) {
    const array = getArrayType(model, schemaContext, namespace2);
    if (array) {
      return array;
    }
    const modelSchema = {
      type: "object",
      description: getDoc(program, model)
    };
    if (model.baseModel) {
      const discriminatorValue = getDiscriminatorValue(model);
      if (discriminatorValue) {
        const extensions = getExtensions(program, model);
        if (!extensions.has("x-ms-discriminator-value")) {
          modelSchema["x-ms-discriminator-value"] = discriminatorValue;
        }
      }
    }
    const properties = {};
    if (isRecordModelType(program, model)) {
      modelSchema.additionalProperties = getSchemaOrRef(model.indexer.value, schemaContext);
    }
    const derivedModels = resolveExternalRef(model) ? [] : model.derivedModels.filter(includeDerivedModel);
    for (const child of derivedModels) {
      getSchemaOrRef(child, schemaContext);
    }
    const discriminator = getDiscriminator(program, model);
    if (discriminator) {
      const { propertyName } = discriminator;
      modelSchema.discriminator = propertyName;
      if (!model.properties.get(propertyName)) {
        properties[propertyName] = {
          type: "string",
          description: `Discriminator property for ${model.name}.`
        };
        modelSchema.required = [propertyName];
      }
    }
    applySummary(model, modelSchema);
    applyExternalDocs(model, modelSchema);
    for (const prop of model.properties.values()) {
      if (!metadataInfo.isPayloadProperty(prop, schemaContext.visibility, schemaContext.ignoreMetadataAnnotations)) {
        continue;
      }
      if (isNeverType(prop.type)) {
        continue;
      }
      const jsonName = getJsonName(prop);
      const clientName = getClientName(context, prop);
      const description = getDoc(program, prop);
      if (model.baseModel) {
        const { propertyName } = getDiscriminator(program, model.baseModel) || {};
        if (jsonName === propertyName) {
          continue;
        }
      }
      if (!metadataInfo.isOptional(prop, schemaContext.visibility) || prop.name === discriminator?.propertyName) {
        if (!modelSchema.required) {
          modelSchema.required = [];
        }
        modelSchema.required.push(jsonName);
      }
      properties[jsonName] = resolveProperty(prop, schemaContext);
      const property = properties[jsonName];
      if (jsonName !== clientName) {
        property["x-ms-client-name"] = clientName;
      }
      if (description) {
        property.description = description;
      }
      applySummary(prop, property);
      if (prop.defaultValue && !("$ref" in property)) {
        property.default = getDefaultValue(prop.defaultValue, prop);
      }
      if (isReadonlyProperty(program, prop)) {
        property.readOnly = true;
      } else {
        const lifecycle = getLifecycleVisibilityEnum2(program);
        const vis = getVisibilityForClass2(program, prop, lifecycle);
        const { read, create, update } = {
          read: lifecycle.members.get("Read"),
          create: lifecycle.members.get("Create"),
          update: lifecycle.members.get("Update")
        };
        if (vis.size !== lifecycle.members.size) {
          const mutability = [];
          if (vis.has(read)) {
            mutability.push("read");
          }
          if (vis.has(update)) {
            mutability.push("update");
          }
          if (vis.has(create)) {
            mutability.push("create");
          }
          if (mutability.length > 0) {
            property["x-ms-mutability"] = mutability;
          }
        }
      }
      attachExtensions(prop, property);
    }
    if (model.baseModel && isTemplateDeclarationOrInstance(model.baseModel) && Object.keys(properties).length === 0) {
      const baseSchema = getSchemaForType(model.baseModel, schemaContext);
      Object.assign(modelSchema, baseSchema, { description: modelSchema.description });
    } else if (model.baseModel) {
      const baseSchema = getSchemaOrRef(model.baseModel, schemaContext);
      modelSchema.allOf = [baseSchema];
    }
    if (Object.keys(properties).length > 0) {
      modelSchema.properties = properties;
    }
    attachExtensions(model, modelSchema);
    return modelSchema;
  }
  function canSharePropertyUsingReadonlyOrXMSMutability(prop) {
    const sharedVisibilities = ["Read", "Create", "Update"];
    const lifecycle = getLifecycleVisibilityEnum2(program);
    const visibilities = getVisibilityForClass2(program, prop, lifecycle);
    if (visibilities.size !== lifecycle.members.size) {
      for (const visibility of visibilities) {
        if (!sharedVisibilities.includes(visibility.name)) {
          return false;
        }
      }
    }
    return visibilities.size !== 0;
  }
  function resolveProperty(prop, context2) {
    let propSchema;
    if (prop.type.kind === "Enum" && prop.defaultValue) {
      propSchema = getSchemaForEnum(prop.type);
    } else if (prop.type.kind === "Union" && prop.defaultValue) {
      const [asEnum, _] = getUnionAsEnum(prop.type);
      if (asEnum) {
        propSchema = getSchemaForUnionEnum(prop.type, asEnum);
      } else {
        propSchema = getSchemaOrRef(prop.type, context2);
      }
    } else {
      propSchema = getSchemaOrRef(prop.type, context2);
      applyArmIdentifiersDecorator(prop.type, propSchema, prop);
    }
    if (options.armResourceFlattening && isConditionallyFlattened(program, prop)) {
      return { ...applyIntrinsicDecorators(prop, propSchema), "x-ms-client-flatten": true };
    } else {
      return applyIntrinsicDecorators(prop, propSchema);
    }
  }
  function attachExtensions(type, emitObject) {
    const extensions = getExtensions(program, type);
    if (isAzureResource(program, type)) {
      emitObject["x-ms-azure-resource"] = true;
    }
    if (getAsEmbeddingVector(program, type) !== void 0) {
      emitObject["x-ms-embedding-vector"] = true;
    }
    if (type.kind === "Scalar") {
      const ext = getArmResourceIdentifierConfig(program, type);
      if (ext) {
        emitObject["x-ms-arm-id-details"] = ext;
      }
    }
    if (extensions) {
      for (const key of extensions.keys()) {
        emitObject[key] = extensions.get(key);
      }
    }
  }
  function getStringValues(type) {
    switch (type.kind) {
      case "String":
        return [type.value];
      case "Union":
        return [...type.variants.values()].flatMap((x) => getStringValues(x.type)).filter((x) => x);
      case "EnumMember":
        return typeof type.value !== "number" ? [type.value ?? type.name] : [];
      case "UnionVariant":
        return getStringValues(type.type);
      default:
        return [];
    }
  }
  function applyIntrinsicDecorators(typespecType, target) {
    const newTarget = { ...target };
    const docStr = getDoc(program, typespecType);
    const isString = (typespecType.kind === "Scalar" || typespecType.kind === "ModelProperty") && isStringType(program, getPropertyType(typespecType));
    const isNumeric = (typespecType.kind === "Scalar" || typespecType.kind === "ModelProperty") && isNumericType(program, getPropertyType(typespecType));
    if (docStr) {
      newTarget.description = docStr;
    }
    const title = getSummary(program, typespecType);
    if (title) {
      target.title = title;
    }
    const formatStr = getFormat(program, typespecType);
    if (isString && formatStr) {
      const allowedStringFormats = [
        "char",
        "binary",
        "byte",
        "certificate",
        "date",
        "time",
        "date-time",
        "date-time-rfc1123",
        "date-time-rfc7231",
        "duration",
        "password",
        "uuid",
        "base64url",
        "uri",
        "url",
        "arm-id"
      ];
      if (!allowedStringFormats.includes(formatStr.toLowerCase())) {
        reportDiagnostic(program, {
          code: "invalid-format",
          format: { schema: "string", format: formatStr },
          target: typespecType
        });
      } else {
        newTarget.format = formatStr;
      }
    }
    const pattern = getPattern(program, typespecType);
    if (isString && pattern) {
      newTarget.pattern = pattern;
    }
    const minLength = getMinLength(program, typespecType);
    if (isString && minLength !== void 0) {
      newTarget.minLength = minLength;
    }
    const maxLength = getMaxLength(program, typespecType);
    if (isString && maxLength !== void 0) {
      newTarget.maxLength = maxLength;
    }
    const minValue = getMinValue(program, typespecType);
    if (isNumeric && minValue !== void 0) {
      newTarget.minimum = minValue;
    }
    const maxValue = getMaxValue(program, typespecType);
    if (isNumeric && maxValue !== void 0) {
      newTarget.maximum = maxValue;
    }
    const minItems = getMinItems(program, typespecType);
    if (!target.minItems && minItems !== void 0) {
      newTarget.minItems = minItems;
    }
    const maxItems = getMaxItems(program, typespecType);
    if (!target.maxItems && maxItems !== void 0) {
      newTarget.maxItems = maxItems;
    }
    if (isSecret(program, typespecType)) {
      newTarget.format = "password";
      newTarget["x-ms-secret"] = true;
    }
    if (typespecType.kind === "ModelProperty" && shouldFlattenProperty(context.tcgcSdkContext, typespecType)) {
      newTarget["x-ms-client-flatten"] = true;
    }
    attachExtensions(typespecType, newTarget);
    return typespecType.kind === "Scalar" || typespecType.kind === "ModelProperty" ? applyEncoding(typespecType, newTarget) : newTarget;
  }
  function applyEncoding(typespecType, target) {
    const encodeData = getEncode(program, typespecType);
    if (encodeData) {
      const newTarget = { ...target };
      const newType = getSchemaForScalar(encodeData.type);
      newTarget.type = newType.type;
      newTarget.format = mergeFormatAndEncoding(newTarget.format, encodeData.encoding, newType.format);
      return newTarget;
    }
    return target;
  }
  function mergeFormatAndEncoding(format, encoding, encodeAsFormat) {
    switch (format) {
      case void 0:
        return encodeAsFormat ?? encoding ?? format;
      case "date-time":
        switch (encoding) {
          case "rfc3339":
            return "date-time";
          case "unixTimestamp":
            return "unixtime";
          case "rfc7231":
            return "date-time-rfc7231";
          default:
            return encoding;
        }
      case "duration":
        switch (encoding) {
          case "ISO8601":
            return "duration";
          default:
            return encodeAsFormat ?? encoding;
        }
      default:
        return encodeAsFormat ?? encoding ?? format;
    }
  }
  function applySummary(typespecType, target) {
    const summary = getSummary(program, typespecType);
    if (summary) {
      target.title = summary;
    }
  }
  function applyExternalDocs(typespecType, target) {
    const externalDocs = getExternalDocs(program, typespecType);
    if (externalDocs) {
      target.externalDocs = externalDocs;
    }
  }
  function addXMSEnum(type, schema) {
    if (type.node && type.node.parent && type.node.parent.kind === SyntaxKind.ModelStatement) {
      schema["x-ms-enum"] = {
        name: type.node.parent.id.sv,
        modelAsString: false
      };
    } else if (type.kind === "String") {
      schema["x-ms-enum"] = {
        modelAsString: false
      };
    } else if (type.kind === "Enum") {
      const clientName = getClientName(context, type);
      schema["x-ms-enum"] = {
        name: clientName ?? type.name,
        modelAsString: false
      };
      const values = [];
      let foundCustom = false;
      for (const member of type.members.values()) {
        const description = getDoc(program, member);
        const memberClientName = getClientName(context, member);
        values.push({
          name: member.name,
          value: member.value ?? memberClientName,
          description
        });
        if (description || member.value !== void 0) {
          foundCustom = true;
        }
      }
      if (foundCustom) {
        schema["x-ms-enum"].values = values;
      }
    }
    return schema;
  }
  function getSchemaForStringTemplate(stringTemplate) {
    if (stringTemplate.stringValue === void 0) {
      program.reportDiagnostics(explainStringTemplateNotSerializable(stringTemplate).map((x) => ({
        ...x,
        severity: "warning"
      })));
      return { type: "string" };
    }
    return { type: "string", enum: [stringTemplate.stringValue] };
  }
  function getSchemaForLiterals(typespecType) {
    switch (typespecType.kind) {
      case "Number":
        return { type: "number", enum: [typespecType.value] };
      case "String":
        return addXMSEnum(typespecType, { type: "string", enum: [typespecType.value] });
      case "Boolean":
        return { type: "boolean", enum: [typespecType.value] };
      default:
        return void 0;
    }
  }
  function getArrayType(typespecType, context2, namespace2) {
    if (isArrayModelType(program, typespecType)) {
      const array = {
        type: "array",
        items: getSchemaOrRef(typespecType.indexer.value, {
          ...context2,
          visibility: context2.visibility | Visibility.Item
        })
      };
      const armKeyIdentifiers = getArmKeyIdentifiers(program, typespecType);
      if (isArrayTypeArmProviderNamespace(typespecType, namespace2) && hasValidArmIdentifiers(armKeyIdentifiers)) {
        array["x-ms-identifiers"] = armKeyIdentifiers;
      } else if (!ifArrayItemContainsIdentifier(program, typespecType)) {
        array["x-ms-identifiers"] = [];
      }
      return applyIntrinsicDecorators(typespecType, array);
    }
    return void 0;
  }
  function applyArmIdentifiersDecorator(typespecType, schema, property) {
    const armIdentifiers = getArmIdentifiers(program, property);
    if (typespecType.kind !== "Model" || !isArrayModelType(program, typespecType) || !armIdentifiers) {
      return;
    }
    schema["x-ms-identifiers"] = armIdentifiers;
  }
  function hasValidArmIdentifiers(armIdentifiers) {
    return armIdentifiers !== void 0 && armIdentifiers.length > 0 && !ifArmIdentifiersDefault(armIdentifiers);
  }
  function isArrayTypeArmProviderNamespace(typespecType, namespace2) {
    if (typespecType === void 0) {
      return false;
    }
    if (isArmProviderNamespace(program, namespace2)) {
      return true;
    }
    if (typespecType.indexer?.value.kind === "Model") {
      return isArmProviderNamespace(program, typespecType.indexer.value.namespace);
    }
    return false;
  }
  function getSchemaForScalar(scalar) {
    let result = {};
    const isStd = program.checker.isStdType(scalar);
    if (isStd) {
      result = getSchemaForStdScalars(scalar);
    } else if (scalar.baseScalar) {
      result = getSchemaForScalar(scalar.baseScalar);
    }
    const withDecorators = applyIntrinsicDecorators(scalar, result);
    if (isStd) {
      delete withDecorators.description;
    }
    return withDecorators;
  }
  function getSchemaForStdScalars(scalar) {
    function reportNonspecificScalar(scalarName, chosenScalarName) {
      reportDiagnostic(program, {
        code: "nonspecific-scalar",
        format: { type: scalarName, chosenType: chosenScalarName },
        target: scalar
      });
    }
    switch (scalar.name) {
      case "bytes":
        return { type: "string", format: "byte" };
      case "numeric":
        reportNonspecificScalar("numeric", "int64");
        return { type: "integer", format: "int64" };
      case "integer":
        reportNonspecificScalar("integer", "int64");
        return { type: "integer", format: "int64" };
      case "int8":
        return { type: "integer", format: "int8" };
      case "int16":
        return { type: "integer", format: "int16" };
      case "int32":
        return { type: "integer", format: "int32" };
      case "int64":
        return { type: "integer", format: "int64" };
      case "safeint":
        return { type: "integer", format: "int64" };
      case "uint8":
        return { type: "integer", format: "uint8" };
      case "uint16":
        return { type: "integer", format: "uint16" };
      case "uint32":
        return { type: "integer", format: "uint32" };
      case "uint64":
        return { type: "integer", format: "uint64" };
      case "float":
        reportNonspecificScalar("float", "float64");
        return { type: "number" };
      case "float64":
        return { type: "number", format: "double" };
      case "float32":
        return { type: "number", format: "float" };
      case "decimal":
        return { type: "number", format: "decimal" };
      case "decimal128":
        return { type: "number", format: "decimal" };
      case "string":
        return { type: "string" };
      case "boolean":
        return { type: "boolean" };
      case "plainDate":
        return { type: "string", format: "date" };
      case "utcDateTime":
      case "offsetDateTime":
        return { type: "string", format: "date-time" };
      case "plainTime":
        return { type: "string", format: "time" };
      case "duration":
        return { type: "string", format: "duration" };
      case "url":
        return { type: "string", format: "uri" };
      default:
        const _assertNever = scalar.name;
        return {};
    }
  }
  function processAuth(serviceNamespace) {
    const authentication = getAuthentication(program, serviceNamespace);
    if (authentication) {
      return processServiceAuthentication(authentication, serviceNamespace);
    }
    return void 0;
  }
  function processServiceAuthentication(authentication, serviceNamespace) {
    const oaiSchemes = {};
    const security = [];
    for (const option of authentication.options) {
      const oai3SecurityOption = {};
      for (const scheme of option.schemes) {
        const result = getOpenAPI2Scheme(scheme, serviceNamespace);
        if (result !== void 0) {
          const [oaiScheme, scopes] = result;
          oaiSchemes[scheme.id] = oaiScheme;
          oai3SecurityOption[scheme.id] = scopes;
        }
      }
      if (Object.keys(oai3SecurityOption).length > 0) {
        security.push(oai3SecurityOption);
      }
    }
    return { securitySchemes: oaiSchemes, security };
  }
  function getOpenAPI2Scheme(auth2, serviceNamespace) {
    switch (auth2.type) {
      case "http":
        if (auth2.scheme.toLowerCase() !== "basic") {
          reportDiagnostic(program, {
            code: "unsupported-http-auth-scheme",
            target: serviceNamespace,
            format: { scheme: auth2.scheme }
          });
          return void 0;
        }
        return [{ type: "basic", description: auth2.description }, []];
      case "apiKey":
        if (auth2.in === "cookie") {
          return void 0;
        }
        return [
          { type: "apiKey", description: auth2.description, in: auth2.in, name: auth2.name },
          []
        ];
      case "oauth2":
        const flow = auth2.flows[0];
        if (flow === void 0) {
          return void 0;
        }
        const oaiFlowName = getOpenAPI2Flow(flow.type);
        return [
          {
            type: "oauth2",
            description: auth2.description,
            flow: oaiFlowName,
            authorizationUrl: flow.authorizationUrl,
            tokenUrl: flow.tokenUrl,
            scopes: Object.fromEntries(flow.scopes.map((x) => [x.value, x.description ?? ""]))
          },
          flow.scopes.map((x) => x.value)
        ];
      case "openIdConnect":
      default:
        reportDiagnostic(program, {
          code: "unsupported-auth",
          format: { authType: auth2.type },
          target: service.type
        });
        return void 0;
    }
  }
  function getOpenAPI2Flow(flow) {
    switch (flow) {
      case "authorizationCode":
        return "accessCode";
      case "clientCredentials":
        return "application";
      case "implicit":
        return "implicit";
      case "password":
        return "password";
      default:
        const _assertNever = flow;
        compilerAssert(false, "Unreachable");
    }
  }
}
var ErrorTypeFoundError = class extends Error {
  constructor() {
    super("Error type found in evaluated TypeSpec output");
  }
};
function sortOpenAPIDocument(doc) {
  const unsorted = JSON.parse(JSON.stringify(doc));
  const sorted = sortWithJsonSchema(unsorted, AutorestOpenAPISchema);
  return sorted;
}
async function checkExamplesDirExists(host, dir) {
  try {
    return (await host.stat(dir)).isDirectory();
  } catch (err) {
    return false;
  }
}
async function searchExampleJsonFiles(program, exampleDir) {
  const host = program.host;
  const exampleFiles = [];
  async function recursiveSearch(dir) {
    const fileItems = await host.readDir(dir);
    for (const item of fileItems) {
      const fullPath = joinPaths(dir, item);
      const relativePath = getRelativePathFromDirectory(exampleDir, fullPath, false);
      if ((await host.stat(fullPath)).isDirectory()) {
        await recursiveSearch(fullPath);
      } else if ((await host.stat(fullPath)).isFile() && getAnyExtensionFromPath(item) === ".json") {
        exampleFiles.push(normalizePath(relativePath));
      }
    }
  }
  await recursiveSearch(exampleDir);
  return exampleFiles;
}
async function loadExamples(program, options, version) {
  const host = program.host;
  const diagnostics = createDiagnosticCollector();
  const examplesBaseDir = options.examplesDirectory ?? resolvePath(program.projectRoot, "examples");
  const exampleDir = version ? resolvePath(examplesBaseDir, version) : resolvePath(examplesBaseDir);
  if (!await checkExamplesDirExists(host, exampleDir)) {
    if (options.examplesDirectory) {
      diagnostics.add(createDiagnostic({
        code: "example-loading",
        messageId: "noDirectory",
        format: { directory: exampleDir },
        target: NoTarget
      }));
    }
    return diagnostics.wrap(/* @__PURE__ */ new Map());
  }
  const map = /* @__PURE__ */ new Map();
  const exampleFiles = await searchExampleJsonFiles(program, exampleDir);
  for (const fileName of exampleFiles) {
    try {
      const exampleFile = await host.readFile(resolvePath(exampleDir, fileName));
      const example = JSON.parse(exampleFile.text);
      if (!example.operationId || !example.title) {
        diagnostics.add(createDiagnostic({
          code: "example-loading",
          messageId: "noOperationId",
          format: { filename: fileName },
          target: { file: exampleFile, pos: 0, end: 0 }
        }));
        continue;
      }
      if (!map.has(example.operationId)) {
        map.set(example.operationId, {});
      }
      const examples = map.get(example.operationId);
      if (example.title in examples) {
        diagnostics.add(createDiagnostic({
          code: "duplicate-example-file",
          target: { file: exampleFile, pos: 0, end: 0 },
          format: {
            filename: fileName,
            operationId: example.operationId,
            title: example.title
          }
        }));
      }
      examples[example.title] = {
        relativePath: fileName,
        file: exampleFile,
        data: example
      };
    } catch (err) {
      diagnostics.add(createDiagnostic({
        code: "example-loading",
        messageId: "default",
        format: { filename: fileName, error: err?.toString() ?? "" },
        target: NoTarget
      }));
    }
  }
  return diagnostics.wrap(map);
}
function isHttpParameterProperty(httpProperty) {
  return ["header", "query", "path", "cookie"].includes(httpProperty.kind);
}

// src/typespec/packages/typespec-autorest/dist/src/emit.js
var defaultOptions = {
  "output-file": "{azure-resource-provider-folder}/{service-name}/{version-status}/{version}/openapi.json",
  "new-line": "lf",
  "include-x-typespec-name": "never"
};
async function $onEmit(context) {
  const tracer = getTracer(context.program);
  const options = resolveAutorestOptions(context.program, context.emitterOutputDir, context.options);
  tracer.trace("options", JSON.stringify(options, null, 2));
  await emitAllServiceAtAllVersions(context.program, options);
}
function resolveAutorestOptions(program, emitterOutputDir, options) {
  const resolvedOptions = {
    ...defaultOptions,
    ...options
  };
  const armTypesDir = interpolatePath2(resolvedOptions["arm-types-dir"] ?? "{project-root}/../../common-types/resource-management", {
    "project-root": program.projectRoot,
    "emitter-output-dir": emitterOutputDir
  });
  if (resolvedOptions["examples-directory"]) {
    reportDeprecated2(program, `examples-directory option is deprecated use examples-dir instead or remove it if examples are located in {project-root}/examples`, NoTarget2);
  }
  return {
    outputFile: resolvedOptions["output-file"],
    outputDir: emitterOutputDir,
    azureResourceProviderFolder: resolvedOptions["azure-resource-provider-folder"],
    examplesDirectory: resolvedOptions["examples-dir"] ?? resolvedOptions["examples-directory"],
    version: resolvedOptions["version"],
    newLine: resolvedOptions["new-line"],
    omitUnreachableTypes: resolvedOptions["omit-unreachable-types"],
    versionEnumStrategy: resolvedOptions["version-enum-strategy"],
    includeXTypeSpecName: resolvedOptions["include-x-typespec-name"],
    armTypesDir,
    useReadOnlyStatusSchema: resolvedOptions["use-read-only-status-schema"],
    emitLroOptions: resolvedOptions["emit-lro-options"],
    armResourceFlattening: resolvedOptions["arm-resource-flattening"],
    emitCommonTypesSchema: resolvedOptions["emit-common-types-schema"]
  };
}
async function getAllServicesAtAllVersions(program, options) {
  const tcgcSdkContext = createTCGCContext(program, "@azure-tools/typespec-autorest");
  const services = listServices(program);
  if (services.length === 0) {
    services.push({ type: program.getGlobalNamespaceType() });
  }
  const serviceRecords = [];
  for (const service of services) {
    const versions = getVersioningMutators(program, service.type);
    if (versions === void 0) {
      const context = {
        program,
        outputFile: resolveOutputFile(program, service, services.length > 1, options),
        service,
        tcgcSdkContext
      };
      const result = await getOpenAPIForService(context, options);
      serviceRecords.push({
        service,
        versioned: false,
        ...result
      });
    } else if (versions.kind === "transient") {
      const context = {
        program,
        outputFile: resolveOutputFile(program, service, services.length > 1, options),
        service,
        tcgcSdkContext
      };
      const result = await getVersionSnapshotDocument(context, versions.mutator, options);
      serviceRecords.push({
        service,
        versioned: false,
        ...result
      });
    } else {
      const filteredVersions = versions.snapshots.filter((v) => !options.version || options.version === v.version?.value);
      if (filteredVersions.length === 0 && options.version) {
        reportDiagnostic(program, { code: "no-matching-version-found", target: service.type });
      }
      const serviceRecord = {
        service,
        versioned: true,
        versions: []
      };
      serviceRecords.push(serviceRecord);
      for (const record of filteredVersions) {
        const context = {
          program,
          outputFile: resolveOutputFile(program, service, services.length > 1, options, record.version?.value),
          service,
          version: record.version?.value,
          tcgcSdkContext
        };
        const result = await getVersionSnapshotDocument(context, record.mutator, options);
        serviceRecord.versions.push({
          ...result,
          service,
          version: record.version.value
        });
      }
    }
  }
  return serviceRecords;
}
async function getVersionSnapshotDocument(context, mutator, options) {
  const subgraph = unsafe_mutateSubgraphWithNamespace(context.program, [mutator], context.service.type);
  compilerAssert2(subgraph.type.kind === "Namespace", "Should not have mutated to another type");
  const document = await getOpenAPIForService({ ...context, service: getService(context.program, subgraph.type) }, options);
  return document;
}
async function emitAllServiceAtAllVersions(program, options) {
  const services = await getAllServicesAtAllVersions(program, options);
  if (program.compilerOptions.dryRun || program.hasError()) {
    return;
  }
  for (const serviceRecord of services) {
    if (serviceRecord.versioned) {
      for (const documentRecord of serviceRecord.versions) {
        await emitOutput(program, documentRecord, options);
      }
    } else {
      await emitOutput(program, serviceRecord, options);
    }
  }
}
async function emitOutput(program, result, options) {
  const sortedDocument = sortOpenAPIDocument(result.document);
  await emitFile(program, {
    path: result.outputFile,
    content: prettierOutput(JSON.stringify(sortedDocument, null, 2)),
    newLine: options.newLine
  });
  if (result.operationExamples.length > 0) {
    const examplesPath = resolvePath2(getDirectoryPath2(result.outputFile), "examples");
    await program.host.mkdirp(examplesPath);
    for (const { examples } of result.operationExamples) {
      if (examples) {
        for (const { relativePath, file } of Object.values(examples)) {
          await emitFile(program, {
            path: resolvePath2(examplesPath, relativePath),
            content: file.text,
            newLine: options.newLine
          });
        }
      }
    }
  }
}
function prettierOutput(output) {
  return output + "\n";
}
function resolveOutputFile(program, service, multipleServices, options, version) {
  const azureResourceProviderFolder = options.azureResourceProviderFolder;
  if (azureResourceProviderFolder) {
    const info = resolveInfo2(program, service.type);
    version = version ?? info?.version ?? "0000-00-00";
  }
  const interpolated = interpolatePath2(options.outputFile, {
    "azure-resource-provider-folder": azureResourceProviderFolder,
    "service-name": multipleServices || azureResourceProviderFolder ? getNamespaceFullName(service.type) : void 0,
    "version-status": azureResourceProviderFolder ? version?.includes("preview") ? "preview" : "stable" : void 0,
    version
  });
  return resolvePath2(options.outputDir, interpolated);
}

// src/typespec/packages/typespec-autorest/dist/src/tsp-index.js
var tsp_index_exports = {};
__export(tsp_index_exports, {
  $decorators: () => $decorators,
  $lib: () => $lib
});
var $decorators = {
  Autorest: {
    example: $example,
    useRef: $useRef
  }
};

// virtual:virtual:entry.js
var TypeSpecJSSources = {
  "dist/src/index.js": src_exports,
  "dist/src/tsp-index.js": tsp_index_exports
};
var TypeSpecSources = {
  "package.json": '{"name":"@azure-tools/typespec-autorest","version":"0.56.0","author":"Microsoft Corporation","description":"TypeSpec library for emitting openapi from the TypeSpec REST protocol binding","homepage":"https://azure.github.io/typespec-azure","readme":"https://github.com/Azure/typespec-azure/blob/main/README.md","license":"MIT","repository":{"type":"git","url":"git+https://github.com/Azure/typespec-azure.git"},"bugs":{"url":"https://github.com/Azure/typespec-azure/issues"},"keywords":["typespec","autorest"],"type":"module","main":"dist/src/index.js","tspMain":"lib/autorest.tsp","exports":{".":{"typespec":"./lib/autorest.tsp","types":"./dist/src/index.d.ts","default":"./dist/src/index.js"},"./testing":{"types":"./dist/src/testing/index.d.ts","default":"./dist/src/testing/index.js"}},"engines":{"node":">=20.0.0"},"scripts":{"clean":"rimraf ./dist ./temp","build":"npm run gen-extern-signature && npm run regen-autorest-openapi-schema && tsc -p . && npm run lint-typespec-library","watch":"tsc -p . --watch","gen-extern-signature":"tspd --enable-experimental gen-extern-signature .","lint-typespec-library":"tsp compile . --warn-as-error --import @typespec/library-linter --no-emit","regen-autorest-openapi-schema":"tsp compile ./schema/autorest-openapi-schema.tsp --warn-as-error && node ./.scripts/schema-json-to-js.js","test":"vitest run","test:watch":"vitest -w","test:ui":"vitest --ui","test:ci":"vitest run --coverage --reporter=junit --reporter=default","lint":"eslint .  --max-warnings=0","lint:fix":"eslint . --fix ","regen-docs":"tspd doc .  --enable-experimental  --output-dir ../../website/src/content/docs/docs/emitters/typespec-autorest/reference"},"files":["lib/*.tsp","schema/dist/schema.js","dist/**","!dist/test/**"],"peerDependencies":{"@azure-tools/typespec-azure-core":"workspace:^","@azure-tools/typespec-azure-resource-manager":"workspace:^","@azure-tools/typespec-client-generator-core":"workspace:^","@typespec/compiler":"workspace:^","@typespec/http":"workspace:^","@typespec/openapi":"workspace:^","@typespec/rest":"workspace:^","@typespec/versioning":"workspace:^"},"devDependencies":{"@azure-tools/typespec-azure-core":"workspace:^","@azure-tools/typespec-azure-resource-manager":"workspace:^","@azure-tools/typespec-client-generator-core":"workspace:^","@types/node":"~22.13.11","@typespec/compiler":"workspace:^","@typespec/http":"workspace:^","@typespec/json-schema":"workspace:^","@typespec/library-linter":"workspace:^","@typespec/openapi":"workspace:^","@typespec/rest":"workspace:^","@typespec/tspd":"workspace:^","@typespec/versioning":"workspace:^","@vitest/coverage-v8":"^3.1.2","@vitest/ui":"^3.1.2","c8":"^10.1.3","change-case":"~5.4.4","rimraf":"~6.0.1","typescript":"~5.8.2","vitest":"^3.1.2"}}',
  "../../core/packages/compiler/lib/intrinsics.tsp": 'import "../dist/src/lib/intrinsic/tsp-index.js";\nimport "./prototypes.tsp";\n\n// This file contains all the intrinsic types of typespec. Everything here will always be loaded\nnamespace TypeSpec;\n\n/**\n * Represent a byte array\n */\nscalar bytes;\n\n/**\n * A numeric type\n */\nscalar numeric;\n\n/**\n * A whole number. This represent any `integer` value possible.\n * It is commonly represented as `BigInteger` in some languages.\n */\nscalar integer extends numeric;\n\n/**\n * A number with decimal value\n */\nscalar float extends numeric;\n\n/**\n * A 64-bit integer. (`-9,223,372,036,854,775,808` to `9,223,372,036,854,775,807`)\n */\nscalar int64 extends integer;\n\n/**\n * A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)\n */\nscalar int32 extends int64;\n\n/**\n * A 16-bit integer. (`-32,768` to `32,767`)\n */\nscalar int16 extends int32;\n\n/**\n * A 8-bit integer. (`-128` to `127`)\n */\nscalar int8 extends int16;\n\n/**\n * A 64-bit unsigned integer (`0` to `18,446,744,073,709,551,615`)\n */\nscalar uint64 extends integer;\n\n/**\n * A 32-bit unsigned integer (`0` to `4,294,967,295`)\n */\nscalar uint32 extends uint64;\n\n/**\n * A 16-bit unsigned integer (`0` to `65,535`)\n */\nscalar uint16 extends uint32;\n\n/**\n * A 8-bit unsigned integer (`0` to `255`)\n */\nscalar uint8 extends uint16;\n\n/**\n * An integer that can be serialized to JSON (`\u22129007199254740991 (\u2212(2^53 \u2212 1))` to `9007199254740991 (2^53 \u2212 1)` )\n */\nscalar safeint extends int64;\n\n/**\n * A 64 bit floating point number. (`\xB15.0 \xD7 10^\u2212324` to `\xB11.7 \xD7 10^308`)\n */\nscalar float64 extends float;\n\n/**\n * A 32 bit floating point number. (`\xB11.5 x 10^\u221245` to `\xB13.4 x 10^38`)\n */\nscalar float32 extends float64;\n\n/**\n * A decimal number with any length and precision. This represent any `decimal` value possible.\n * It is commonly represented as `BigDecimal` in some languages.\n */\nscalar decimal extends numeric;\n\n/**\n * A 128-bit decimal number.\n */\nscalar decimal128 extends decimal;\n\n/**\n * A sequence of textual characters.\n */\nscalar string;\n\n/**\n * A date on a calendar without a time zone, e.g. "April 10th"\n */\nscalar plainDate {\n  /**\n   * Create a plain date from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = plainTime.fromISO("2024-05-06");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * A time on a clock without a time zone, e.g. "3:00 am"\n */\nscalar plainTime {\n  /**\n   * Create a plain time from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = plainTime.fromISO("12:34");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * An instant in coordinated universal time (UTC)"\n */\nscalar utcDateTime {\n  /**\n   * Create a date from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = utcDateTime.fromISO("2024-05-06T12:20-12Z");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * A date and time in a particular time zone, e.g. "April 10th at 3:00am in PST"\n */\nscalar offsetDateTime {\n  /**\n   * Create a date from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = offsetDateTime.fromISO("2024-05-06T12:20-12-0700");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * A duration/time period. e.g 5s, 10h\n */\nscalar duration {\n  /**\n   * Create a duration from an ISO 8601 string.\n   * @example\n   *\n   * ```tsp\n   * const time = duration.fromISO("P1Y1D");\n   * ```\n   */\n  init fromISO(value: string);\n}\n\n/**\n * Boolean with `true` and `false` values.\n */\nscalar boolean;\n\n/**\n * @dev Array model type, equivalent to `Element[]`\n * @template Element The type of the array elements\n */\n@indexer(integer, Element)\nmodel Array<Element> {}\n\n/**\n * @dev Model with string properties where all the properties have type `Property`\n * @template Element The type of the properties\n */\n@indexer(string, Element)\nmodel Record<Element> {}\n',
  "../../core/packages/compiler/lib/prototypes.tsp": "namespace TypeSpec.Prototypes;\n\nextern dec getter(target: unknown);\n\nnamespace Types {\n  interface ModelProperty {\n    @getter type(): unknown;\n  }\n\n  interface Operation {\n    @getter returnType(): unknown;\n    @getter parameters(): unknown;\n  }\n\n  interface Array<TElementType> {\n    @getter elementType(): TElementType;\n  }\n}\n",
  "../../core/packages/compiler/lib/std/main.tsp": '// TypeSpec standard library. Everything in here can be omitted by using `--nostdlib` cli flag or `nostdlib` in the config.\nimport "./types.tsp";\nimport "./decorators.tsp";\nimport "./reflection.tsp";\nimport "./visibility.tsp";\n',
  "../../core/packages/compiler/lib/std/types.tsp": 'namespace TypeSpec;\n\n/**\n * Represent a 32-bit unix timestamp datetime with 1s of granularity.\n * It measures time by the number of seconds that have elapsed since 00:00:00 UTC on 1 January 1970.\n */\n@encode("unixTimestamp", int32)\nscalar unixTimestamp32 extends utcDateTime;\n\n/**\n * Represent a URL string as described by https://url.spec.whatwg.org/\n */\nscalar url extends string;\n\n/**\n * Represents a collection of optional properties.\n *\n * @template Source An object whose spread properties are all optional.\n */\n@doc("The template for adding optional properties.")\n@withOptionalProperties\nmodel OptionalProperties<Source> {\n  ...Source;\n}\n\n/**\n * Represents a collection of updateable properties.\n *\n * @template Source An object whose spread properties are all updateable.\n */\n@doc("The template for adding updateable properties.")\n@withUpdateableProperties\nmodel UpdateableProperties<Source> {\n  ...Source;\n}\n\n/**\n * Represents a collection of omitted properties.\n *\n * @template Source An object whose properties are spread.\n * @template Keys The property keys to omit.\n */\n@doc("The template for omitting properties.")\n@withoutOmittedProperties(Keys)\nmodel OmitProperties<Source, Keys extends string> {\n  ...Source;\n}\n\n/**\n * Represents a collection of properties with only the specified keys included.\n *\n * @template Source An object whose properties are spread.\n * @template Keys The property keys to include.\n */\n@doc("The template for picking properties.")\n@withPickedProperties(Keys)\nmodel PickProperties<Source, Keys extends string> {\n  ...Source;\n}\n\n/**\n * Represents a collection of properties with default values omitted.\n *\n * @template Source An object whose spread property defaults are all omitted.\n */\n@withoutDefaultValues\nmodel OmitDefaults<Source> {\n  ...Source;\n}\n\n/**\n * Applies a visibility setting to a collection of properties.\n *\n * @template Source An object whose properties are spread.\n * @template Visibility The visibility to apply to all properties.\n */\n@doc("The template for setting the default visibility of key properties.")\n@withDefaultKeyVisibility(Visibility)\nmodel DefaultKeyVisibility<Source, Visibility extends valueof Reflection.EnumMember> {\n  ...Source;\n}\n',
  "../../core/packages/compiler/lib/std/decorators.tsp": 'import "../../dist/src/lib/tsp-index.js";\n\nusing TypeSpec.Reflection;\n\nnamespace TypeSpec;\n\n/**\n * Typically a short, single-line description.\n * @param summary Summary string.\n *\n * @example\n * ```typespec\n * @summary("This is a pet")\n * model Pet {}\n * ```\n */\nextern dec summary(target: unknown, summary: valueof string);\n\n/**\n * Attach a documentation string. Content support CommonMark markdown formatting.\n * @param doc Documentation string\n * @param formatArgs Record with key value pair that can be interpolated in the doc.\n *\n * @example\n * ```typespec\n * @doc("Represent a Pet available in the PetStore")\n * model Pet {}\n * ```\n */\nextern dec doc(target: unknown, doc: valueof string, formatArgs?: {});\n\n/**\n * Attach a documentation string to describe the successful return types of an operation.\n * If an operation returns a union of success and errors it only describes the success. See `@errorsDoc` for error documentation.\n * @param doc Documentation string\n *\n * @example\n * ```typespec\n * @returnsDoc("Returns doc")\n * op get(): Pet | NotFound;\n * ```\n */\nextern dec returnsDoc(target: Operation, doc: valueof string);\n\n/**\n * Attach a documentation string to describe the error return types of an operation.\n * If an operation returns a union of success and errors it only describes the errors. See `@returnsDoc` for success documentation.\n * @param doc Documentation string\n *\n * @example\n * ```typespec\n * @errorsDoc("Errors doc")\n * op get(): Pet | NotFound;\n * ```\n */\nextern dec errorsDoc(target: Operation, doc: valueof string);\n\n/**\n * Service options.\n */\nmodel ServiceOptions {\n  /**\n   * Title of the service.\n   */\n  title?: string;\n}\n\n/**\n * Mark this namespace as describing a service and configure service properties.\n * @param options Optional configuration for the service.\n *\n * @example\n * ```typespec\n * @service\n * namespace PetStore;\n * ```\n *\n * @example Setting service title\n * ```typespec\n * @service(#{title: "Pet store"})\n * namespace PetStore;\n * ```\n *\n * @example Setting service version\n * ```typespec\n * @service(#{version: "1.0"})\n * namespace PetStore;\n * ```\n */\nextern dec service(target: Namespace, options?: valueof ServiceOptions);\n\n/**\n * Specify that this model is an error type. Operations return error types when the operation has failed.\n *\n * @example\n * ```typespec\n * @error\n * model PetStoreError {\n *   code: string;\n *   message: string;\n * }\n * ```\n */\nextern dec error(target: Model);\n\n/**\n * Applies a media type hint to a TypeSpec type. Emitters and libraries may choose to use this hint to determine how a\n * type should be serialized. For example, the `@typespec/http` library will use the media type hint of the response\n * body type as a default `Content-Type` if one is not explicitly specified in the operation.\n *\n * Media types (also known as MIME types) are defined by RFC 6838. The media type hint should be a valid media type\n * string as defined by the RFC, but the decorator does not enforce or validate this constraint.\n *\n * Notes: the applied media type is _only_ a hint. It may be overridden or not used at all. Media type hints are\n * inherited by subtypes. If a media type hint is applied to a model, it will be inherited by all other models that\n * `extend` it unless they delcare their own media type hint.\n *\n * @param mediaType The media type hint to apply to the target type.\n *\n * @example create a model that serializes as XML by default\n *\n * ```tsp\n * @mediaTypeHint("application/xml")\n * model Example {\n *   @visibility(Lifecycle.Read)\n *   id: string;\n *\n *   name: string;\n * }\n * ```\n */\nextern dec mediaTypeHint(target: Model | Scalar | Enum | Union, mediaType: valueof string);\n\n// Cannot apply this to the scalar itself. Needs to be applied here so that we don\'t crash nostdlib scenarios\n@@mediaTypeHint(TypeSpec.bytes, "application/octet-stream");\n\n// @@mediaTypeHint(TypeSpec.string "text/plain") -- This is hardcoded in the compiler to avoid circularity\n// between the initialization of the string scalar and the `valueof string` required to call the\n// `mediaTypeHint` decorator.\n\n/**\n * Specify a known data format hint for this string type. For example `uuid`, `uri`, etc.\n * This differs from the `@pattern` decorator which is meant to specify a regular expression while `@format` accepts a known format name.\n * The format names are open ended and are left to emitter to interpret.\n *\n * @param format format name.\n *\n * @example\n * ```typespec\n * @format("uuid")\n * scalar uuid extends string;\n * ```\n */\nextern dec format(target: string | ModelProperty, format: valueof string);\n\n/**\n * Specify the the pattern this string should respect using simple regular expression syntax.\n * The following syntax is allowed: alternations (`|`), quantifiers (`?`, `*`, `+`, and `{ }`), wildcard (`.`), and grouping parentheses.\n * Advanced features like look-around, capture groups, and references are not supported.\n *\n * This decorator may optionally provide a custom validation _message_. Emitters may choose to use the message to provide\n * context when pattern validation fails. For the sake of consistency, the message should be a phrase that describes in\n * plain language what sort of content the pattern attempts to validate. For example, a complex regular expression that\n * validates a GUID string might have a message like "Must be a valid GUID."\n *\n * @param pattern Regular expression.\n * @param validationMessage Optional validation message that may provide context when validation fails.\n *\n * @example\n * ```typespec\n * @pattern("[a-z]+", "Must be a string consisting of only lower case letters and of at least one character.")\n * scalar LowerAlpha extends string;\n * ```\n */\nextern dec pattern(\n  target: string | bytes | ModelProperty,\n  pattern: valueof string,\n  validationMessage?: valueof string\n);\n\n/**\n * Specify the minimum length this string type should be.\n * @param value Minimum length\n *\n * @example\n * ```typespec\n * @minLength(2)\n * scalar Username extends string;\n * ```\n */\nextern dec minLength(target: string | ModelProperty, value: valueof integer);\n\n/**\n * Specify the maximum length this string type should be.\n * @param value Maximum length\n *\n * @example\n * ```typespec\n * @maxLength(20)\n * scalar Username extends string;\n * ```\n */\nextern dec maxLength(target: string | ModelProperty, value: valueof integer);\n\n/**\n * Specify the minimum number of items this array should have.\n * @param value Minimum number\n *\n * @example\n * ```typespec\n * @minItems(1)\n * model Endpoints is string[];\n * ```\n */\nextern dec minItems(target: unknown[] | ModelProperty, value: valueof integer);\n\n/**\n * Specify the maximum number of items this array should have.\n * @param value Maximum number\n *\n * @example\n * ```typespec\n * @maxItems(5)\n * model Endpoints is string[];\n * ```\n */\nextern dec maxItems(target: unknown[] | ModelProperty, value: valueof integer);\n\n/**\n * Specify the minimum value this numeric type should be.\n * @param value Minimum value\n *\n * @example\n * ```typespec\n * @minValue(18)\n * scalar Age is int32;\n * ```\n */\nextern dec minValue(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Specify the maximum value this numeric type should be.\n * @param value Maximum value\n *\n * @example\n * ```typespec\n * @maxValue(200)\n * scalar Age is int32;\n * ```\n */\nextern dec maxValue(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Specify the minimum value this numeric type should be, exclusive of the given\n * value.\n * @param value Minimum value\n *\n * @example\n * ```typespec\n * @minValueExclusive(0)\n * scalar distance is float64;\n * ```\n */\nextern dec minValueExclusive(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Specify the maximum value this numeric type should be, exclusive of the given\n * value.\n * @param value Maximum value\n *\n * @example\n * ```typespec\n * @maxValueExclusive(50)\n * scalar distance is float64;\n * ```\n */\nextern dec maxValueExclusive(target: numeric | ModelProperty, value: valueof numeric);\n\n/**\n * Mark this string as a secret value that should be treated carefully to avoid exposure\n *\n * @example\n * ```typespec\n * @secret\n * scalar Password is string;\n * ```\n */\nextern dec secret(target: string | ModelProperty);\n\n/**\n * Attaches a tag to an operation, interface, or namespace. Multiple `@tag` decorators can be specified to attach multiple tags to a TypeSpec element.\n * @param tag Tag value\n */\nextern dec tag(target: Namespace | Interface | Operation, tag: valueof string);\n\n/**\n * Specifies how a templated type should name their instances.\n * @param name name the template instance should take\n * @param formatArgs Model with key value used to interpolate the name\n *\n * @example\n * ```typespec\n * @friendlyName("{name}List", T)\n * model List<Item> {\n *   value: Item[];\n *   nextLink: string;\n * }\n * ```\n */\nextern dec friendlyName(target: unknown, name: valueof string, formatArgs?: unknown);\n\n/**\n * Mark a model property as the key to identify instances of that type\n * @param altName Name of the property. If not specified, the decorated property name is used.\n *\n * @example\n * ```typespec\n * model Pet {\n *   @key id: string;\n * }\n * ```\n */\nextern dec key(target: ModelProperty, altName?: valueof string);\n\n/**\n * Specify this operation is an overload of the given operation.\n * @param overloadbase Base operation that should be a union of all overloads\n *\n * @example\n * ```typespec\n * op upload(data: string | bytes, @header contentType: "text/plain" | "application/octet-stream"): void;\n * @overload(upload)\n * op uploadString(data: string, @header contentType: "text/plain" ): void;\n * @overload(upload)\n * op uploadBytes(data: bytes, @header contentType: "application/octet-stream"): void;\n * ```\n */\nextern dec overload(target: Operation, overloadbase: Operation);\n\n/**\n * Provide an alternative name for this type when serialized to the given mime type.\n * @param mimeType Mime type this should apply to. The mime type should be a known mime type as described here https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types without any suffix (e.g. `+json`)\n * @param name Alternative name\n *\n * @example\n *\n * ```typespec\n * model Certificate {\n *   @encodedName("application/json", "exp")\n *   @encodedName("application/xml", "expiry")\n *   expireAt: int32;\n * }\n * ```\n *\n * @example Invalid values\n *\n * ```typespec\n * @encodedName("application/merge-patch+json", "exp")\n *              ^ error cannot use subtype\n * ```\n */\nextern dec encodedName(target: unknown, mimeType: valueof string, name: valueof string);\n\n/**\n * Options for `@discriminated` decorator.\n */\nmodel DiscriminatedOptions {\n  /**\n   * How is the discriminated union serialized.\n   * @default object\n   */\n  envelope?: "object" | "none";\n\n  /** Name of the discriminator property */\n  discriminatorPropertyName?: string;\n\n  /** Name of the property envelopping the data */\n  envelopePropertyName?: string;\n}\n\n/**\n * Specify that this union is discriminated.\n * @param options Options to configure the serialization of the discriminated union.\n *\n * @example\n *\n * ```typespec\n * @discriminated\n * union Pet{ cat: Cat, dog: Dog }\n *\n * model Cat { name: string, meow: boolean }\n * model Dog { name: string, bark: boolean }\n * ```\n * Serialized as:\n * ```json\n * {\n *   "kind": "cat",\n *   "value": {\n *     "name": "Whiskers",\n *     "meow": true\n *   }\n * },\n * {\n *   "kind": "dog",\n *   "value": {\n *     "name": "Rex",\n *     "bark": false\n *   }\n * }\n * ```\n *\n * @example Custom property names\n *\n * ```typespec\n * @discriminated(#{discriminatorPropertyName: "dataKind", envelopePropertyName: "data"})\n * union Pet{ cat: Cat, dog: Dog }\n *\n * model Cat { name: string, meow: boolean }\n * model Dog { name: string, bark: boolean }\n * ```\n * Serialized as:\n * ```json\n * {\n *   "dataKind": "cat",\n *   "data": {\n *     "name": "Whiskers",\n *     "meow": true\n *   }\n * },\n * {\n *   "dataKind": "dog",\n *   "data": {\n *     "name": "Rex",\n *     "bark": false\n *   }\n * }\n * ```\n */\nextern dec discriminated(target: Union, options?: valueof DiscriminatedOptions);\n\n/**\n * Specify the property to be used to discriminate this type.\n * @param propertyName The property name to use for discrimination\n *\n * @example\n *\n * ```typespec\n * @discriminator("kind")\n * model Pet{ kind: string }\n *\n * model Cat extends Pet {kind: "cat", meow: boolean}\n * model Dog extends Pet  {kind: "dog", bark: boolean}\n * ```\n */\nextern dec discriminator(target: Model, propertyName: valueof string);\n\n/**\n * Known encoding to use on utcDateTime or offsetDateTime\n */\nenum DateTimeKnownEncoding {\n  /**\n   * RFC 3339 standard. https://www.ietf.org/rfc/rfc3339.txt\n   * Encode to string.\n   */\n  rfc3339: "rfc3339",\n\n  /**\n   * RFC 7231 standard. https://www.ietf.org/rfc/rfc7231.txt\n   * Encode to string.\n   */\n  rfc7231: "rfc7231",\n\n  /**\n   * Encode a datetime to a unix timestamp.\n   * Unix timestamps are represented as an integer number of seconds since the Unix epoch and usually encoded as an int32.\n   */\n  unixTimestamp: "unixTimestamp",\n}\n\n/**\n * Known encoding to use on duration\n */\nenum DurationKnownEncoding {\n  /**\n   * ISO8601 duration\n   */\n  ISO8601: "ISO8601",\n\n  /**\n   * Encode to integer or float\n   */\n  seconds: "seconds",\n}\n\n/**\n * Known encoding to use on bytes\n */\nenum BytesKnownEncoding {\n  /**\n   * Encode to Base64\n   */\n  base64: "base64",\n\n  /**\n   * Encode to Base64 Url\n   */\n  base64url: "base64url",\n}\n\n/**\n * Encoding for serializing arrays\n */\nenum ArrayEncoding {\n  /** Each values of the array is separated by a | */\n  pipeDelimited,\n\n  /** Each values of the array is separated by a <space> */\n  spaceDelimited,\n}\n\n/**\n * Specify how to encode the target type.\n * @param encodingOrEncodeAs Known name of an encoding or a scalar type to encode as(Only for numeric types to encode as string).\n * @param encodedAs What target type is this being encoded as. Default to string.\n *\n * @example offsetDateTime encoded with rfc7231\n *\n * ```tsp\n * @encode("rfc7231")\n * scalar myDateTime extends offsetDateTime;\n * ```\n *\n * @example utcDateTime encoded with unixTimestamp\n *\n * ```tsp\n * @encode("unixTimestamp", int32)\n * scalar myDateTime extends unixTimestamp;\n * ```\n *\n * @example encode numeric type to string\n *\n * ```tsp\n * model Pet {\n *   @encode(string) id: int64;\n * }\n * ```\n */\nextern dec encode(\n  target: Scalar | ModelProperty,\n  encodingOrEncodeAs: (valueof string | EnumMember) | Scalar,\n  encodedAs?: Scalar\n);\n\n/** Options for example decorators */\nmodel ExampleOptions {\n  /** The title of the example */\n  title?: string;\n\n  /** Description of the example */\n  description?: string;\n}\n\n/**\n * Provide an example value for a data type.\n *\n * @param example Example value.\n * @param options Optional metadata for the example.\n *\n * @example\n *\n * ```tsp\n * @example(#{name: "Fluffy", age: 2})\n * model Pet {\n *  name: string;\n *  age: int32;\n * }\n * ```\n */\nextern dec example(\n  target: Model | Enum | Scalar | Union | ModelProperty | UnionVariant,\n  example: valueof unknown,\n  options?: valueof ExampleOptions\n);\n\n/**\n * Operation example configuration.\n */\nmodel OperationExample {\n  /** Example request body. */\n  parameters?: unknown;\n\n  /** Example response body. */\n  returnType?: unknown;\n}\n\n/**\n * Provide example values for an operation\'s parameters and corresponding return type.\n *\n * @param example Example value.\n * @param options Optional metadata for the example.\n *\n * @example\n *\n * ```tsp\n * @opExample(#{parameters: #{name: "Fluffy", age: 2}, returnType: #{name: "Fluffy", age: 2, id: "abc"})\n * op createPet(pet: Pet): Pet;\n * ```\n */\nextern dec opExample(\n  target: Operation,\n  example: valueof OperationExample,\n  options?: valueof ExampleOptions\n);\n\n/**\n * Returns the model with required properties removed.\n */\nextern dec withOptionalProperties(target: Model);\n\n/**\n * Returns the model with any default values removed.\n */\nextern dec withoutDefaultValues(target: Model);\n\n/**\n * Returns the model with the given properties omitted.\n * @param omit List of properties to omit\n */\nextern dec withoutOmittedProperties(target: Model, omit: string | Union);\n\n/**\n * Returns the model with only the given properties included.\n * @param pick List of properties to include\n */\nextern dec withPickedProperties(target: Model, pick: string | Union);\n\n//---------------------------------------------------------------------------\n// Paging\n//---------------------------------------------------------------------------\n\n/**\n * Mark this operation as a `list` operation that returns a paginated list of items.\n */\nextern dec list(target: Operation);\n\n/**\n * Pagination property defining the number of items to skip.\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@offset skip: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec offset(target: ModelProperty);\n\n/**\n * Pagination property defining the page index.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@pageIndex page: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec pageIndex(target: ModelProperty);\n\n/**\n * Specify the pagination parameter that controls the maximum number of items to include in a page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@pageIndex page: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec pageSize(target: ModelProperty);\n\n/**\n * Specify the the property that contains the array of page items.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n * }\n * @list op listPets(@pageIndex page: int32, @pageSize pageSize: int8): Page<Pet>;\n * ```\n */\nextern dec pageItems(target: ModelProperty);\n\n/**\n * Pagination property defining the token to get to the next page.\n * It MUST be specified both on the request parameter and the response.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @continuationToken continuationToken: string;\n * }\n * @list op listPets(@continuationToken continuationToken: string): Page<Pet>;\n * ```\n */\nextern dec continuationToken(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the next page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec nextLink(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the previous page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec prevLink(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the first page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec firstLink(target: ModelProperty);\n\n/**\n * Pagination property defining a link to the last page.\n *\n * It is expected that navigating to the link will return the same set of responses as the operation that returned the current page.\n *\n * @example\n * ```tsp\n * model Page<T> {\n *   @pageItems items: T[];\n *   @nextLink next: url;\n *   @prevLink prev: url;\n *   @firstLink first: url;\n *   @lastLink last: url;\n * }\n * @list op listPets(): Page<Pet>;\n * ```\n */\nextern dec lastLink(target: ModelProperty);\n\n//---------------------------------------------------------------------------\n// Debugging\n//---------------------------------------------------------------------------\n\n/**\n * A debugging decorator used to inspect a type.\n * @param text Custom text to log\n */\nextern dec inspectType(target: unknown, text: valueof string);\n\n/**\n * A debugging decorator used to inspect a type name.\n * @param text Custom text to log\n */\nextern dec inspectTypeName(target: unknown, text: valueof string);\n',
  "../../core/packages/compiler/lib/std/reflection.tsp": "namespace TypeSpec.Reflection;\n\nmodel Enum {}\nmodel EnumMember {}\nmodel Interface {}\nmodel Model {}\nmodel ModelProperty {}\nmodel Namespace {}\nmodel Operation {}\nmodel Scalar {}\nmodel Union {}\nmodel UnionVariant {}\nmodel StringTemplate {}\n",
  "../../core/packages/compiler/lib/std/visibility.tsp": '// Copyright (c) Microsoft Corporation\n// Licensed under the MIT license.\n\nimport "../../dist/src/lib/tsp-index.js";\n\nusing TypeSpec.Reflection;\n\nnamespace TypeSpec;\n\n/**\n * Sets the visibility modifiers that are active on a property, indicating that it is only considered to be present\n * (or "visible") in contexts that select for the given modifiers.\n *\n * A property without any visibility settings applied for any visibility class (e.g. `Lifecycle`) is considered to have\n * the default visibility settings for that class.\n *\n * If visibility for the property has already been set for a visibility class (for example, using `@invisible` or\n * `@removeVisibility`), this decorator will **add** the specified visibility modifiers to the property.\n *\n * See: [Visibility](https://typespec.io/docs/language-basics/visibility)\n *\n * The `@typespec/http` library uses `Lifecycle` visibility to determine which properties are included in the request or\n * response bodies of HTTP operations. By default, it uses the following visibility settings:\n *\n * - For the return type of operations, properties are included if they have `Lifecycle.Read` visibility.\n * - For POST operation parameters, properties are included if they have `Lifecycle.Create` visibility.\n * - For PUT operation parameters, properties are included if they have `Lifecycle.Create` or `Lifecycle.Update` visibility.\n * - For PATCH operation parameters, properties are included if they have `Lifecycle.Update` visibility.\n * - For DELETE operation parameters, properties are included if they have `Lifecycle.Delete` visibility.\n * - For GET or HEAD operation parameters, properties are included if they have `Lifecycle.Query` visibility.\n *\n * By default, properties have all five Lifecycle visibility modifiers enabled, so a property is visible in all contexts\n * by default.\n *\n * The default settings may be overridden using the `@returnTypeVisibility` and `@parameterVisibility` decorators.\n *\n * See also: [Automatic visibility](https://typespec.io/docs/libraries/http/operations#automatic-visibility)\n *\n * @param visibilities List of visibilities which apply to this property.\n *\n * @example\n *\n * ```typespec\n * model Dog {\n *   // The service will generate an ID, so you don\'t need to send it.\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   // The service will store this secret name, but won\'t ever return it.\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   // The regular name has all vi\n *   name: string;\n * }\n * ```\n */\nextern dec visibility(target: ModelProperty, ...visibilities: valueof EnumMember[]);\n\n/**\n * Indicates that a property is not visible in the given visibility class.\n *\n * This decorator removes all active visibility modifiers from the property within\n * the given visibility class, making it invisible to any context that selects for\n * visibility modifiers within that class.\n *\n * @param visibilityClass The visibility class to make the property invisible within.\n *\n * @example\n * ```typespec\n * model Example {\n *   @invisible(Lifecycle)\n *   hidden_property: string;\n * }\n * ```\n */\nextern dec invisible(target: ModelProperty, visibilityClass: Enum);\n\n/**\n * Removes visibility modifiers from a property.\n *\n * If the visibility modifiers for a visibility class have not been initialized,\n * this decorator will use the default visibility modifiers for the visibility\n * class as the default modifier set.\n *\n * @param target The property to remove visibility from.\n * @param visibilities The visibility modifiers to remove from the target property.\n *\n * @example\n * ```typespec\n * model Example {\n *   // This property will have all Lifecycle visibilities except the Read\n *   // visibility, since it is removed.\n *   @removeVisibility(Lifecycle.Read)\n *   secret_property: string;\n * }\n * ```\n */\nextern dec removeVisibility(target: ModelProperty, ...visibilities: valueof EnumMember[]);\n\n/**\n * Removes properties that do not have at least one of the given visibility modifiers\n * active.\n *\n * If no visibility modifiers are supplied, this decorator has no effect.\n *\n * See also: [Automatic visibility](https://typespec.io/docs/libraries/http/operations#automatic-visibility)\n *\n * When using an emitter that applies visibility automatically, it is generally\n * not necessary to use this decorator.\n *\n * @param visibilities List of visibilities that apply to this property.\n *\n * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // The spread operator will copy all the properties of Dog into DogRead,\n * // and @withVisibility will then remove those that are not visible with\n * // create or update visibility.\n * //\n * // In this case, the id property is removed, and the name and secretName\n * // properties are kept.\n * @withVisibility(Lifecycle.Create, Lifecycle.Update)\n * model DogCreateOrUpdate {\n *   ...Dog;\n * }\n *\n * // In this case the id and name properties are kept and the secretName property\n * // is removed.\n * @withVisibility(Lifecycle.Read)\n * model DogRead {\n *   ...Dog;\n * }\n * ```\n */\nextern dec withVisibility(target: Model, ...visibilities: valueof EnumMember[]);\n\n/**\n * Set the visibility of key properties in a model if not already set.\n *\n * This will set the visibility modifiers of all key properties in the model if the visibility is not already _explicitly_ set,\n * but will not change the visibility of any properties that have visibility set _explicitly_, even if the visibility\n * is the same as the default visibility.\n *\n * Visibility may be set explicitly using any of the following decorators:\n *\n * - `@visibility`\n * - `@removeVisibility`\n * - `@invisible`\n *\n * @param visibility The desired default visibility value. If a key property already has visibility set, it will not be changed.\n */\nextern dec withDefaultKeyVisibility(target: Model, visibility: valueof EnumMember);\n\n/**\n * Declares the visibility constraint of the parameters of a given operation.\n *\n * A parameter or property nested within a parameter will be visible if it has _any_ of the visibilities\n * in the list.\n *\n * It is invalid to call this decorator with no visibility modifiers.\n *\n * @param visibilities List of visibility modifiers that apply to the parameters of this operation.\n */\nextern dec parameterVisibility(target: Operation, ...visibilities: valueof EnumMember[]);\n\n/**\n * Declares the visibility constraint of the return type of a given operation.\n *\n * A property within the return type of the operation will be visible if it has _any_ of the visibilities\n * in the list.\n *\n * It is invalid to call this decorator with no visibility modifiers.\n *\n * @param visibilities List of visibility modifiers that apply to the return type of this operation.\n */\nextern dec returnTypeVisibility(target: Operation, ...visibilities: valueof EnumMember[]);\n\n/**\n * Returns the model with non-updateable properties removed.\n */\nextern dec withUpdateableProperties(target: Model);\n\n/**\n * Declares the default visibility modifiers for a visibility class.\n *\n * The default modifiers are used when a property does not have any visibility decorators\n * applied to it.\n *\n * The modifiers passed to this decorator _MUST_ be members of the target Enum.\n *\n * @param visibilities the list of modifiers to use as the default visibility modifiers.\n */\nextern dec defaultVisibility(target: Enum, ...visibilities: valueof EnumMember[]);\n\n/**\n * A visibility class for resource lifecycle phases.\n *\n * These visibilities control whether a property is visible during the various phases of a resource\'s lifecycle.\n *\n * @example\n * ```typespec\n * model Dog {\n *  @visibility(Lifecycle.Read)\n *  id: int32;\n *\n *  @visibility(Lifecycle.Create, Lifecycle.Update)\n *  secretName: string;\n *\n *  name: string;\n * }\n * ```\n *\n * In this example, the `id` property is only visible during the read phase, and the `secretName` property is only visible\n * during the create and update phases. This means that the server will return the `id` property when returning a `Dog`,\n * but the client will not be able to set or update it. In contrast, the `secretName` property can be set when creating\n * or updating a `Dog`, but the server will never return it. The `name` property has no visibility modifiers and is\n * therefore visible in all phases.\n */\nenum Lifecycle {\n  /**\n   * The property is visible when a resource is being created.\n   */\n  Create,\n\n  /**\n   * The property is visible when a resource is being read.\n   */\n  Read,\n\n  /**\n   * The property is visible when a resource is being updated.\n   */\n  Update,\n\n  /**\n   * The property is visible when a resource is being deleted.\n   */\n  Delete,\n\n  /**\n   * The property is visible when a resource is being queried.\n   *\n   * In HTTP APIs, this visibility applies to parameters of GET or HEAD operations.\n   */\n  Query,\n}\n\n/**\n * A visibility filter, used to specify which properties should be included when\n * using the `withVisibilityFilter` decorator.\n *\n * The filter matches any property with ALL of the following:\n * - If the `any` key is present, the property must have at least one of the specified visibilities.\n * - If the `all` key is present, the property must have all of the specified visibilities.\n * - If the `none` key is present, the property must have none of the specified visibilities.\n */\nmodel VisibilityFilter {\n  any?: EnumMember[];\n  all?: EnumMember[];\n  none?: EnumMember[];\n}\n\n/**\n * Applies the given visibility filter to the properties of the target model.\n *\n * This transformation is recursive, so it will also apply the filter to any nested\n * or referenced models that are the types of any properties in the `target`.\n *\n * If a `nameTemplate` is provided, newly-created type instances will be named according\n * to the template. See the `@friendlyName` decorator for more information on the template\n * syntax. The transformed type is provided as the argument to the template.\n *\n * @param target The model to apply the visibility filter to.\n * @param filter The visibility filter to apply to the properties of the target model.\n * @param nameTemplate The name template to use when renaming new model instances.\n *\n * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   name: string;\n * }\n *\n * @withVisibilityFilter(#{ all: #[Lifecycle.Read] })\n * model DogRead {\n *  ...Dog\n * }\n * ```\n */\nextern dec withVisibilityFilter(\n  target: Model,\n  filter: valueof VisibilityFilter,\n  nameTemplate?: valueof string\n);\n\n/**\n * Transforms the `target` model to include only properties that are visible during the\n * "Update" lifecycle phase.\n *\n * Any nested models of optional properties will be transformed into the "CreateOrUpdate"\n * lifecycle phase instead of the "Update" lifecycle phase, so that nested models may be\n * fully updated.\n *\n * If a `nameTemplate` is provided, newly-created type instances will be named according\n * to the template. See the `@friendlyName` decorator for more information on the template\n * syntax. The transformed type is provided as the argument to the template.\n *\n * @param target The model to apply the transformation to.\n * @param nameTemplate The name template to use when renaming new model instances.\n *\n * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * @withLifecycleUpdate\n * model DogUpdate {\n *   ...Dog\n * }\n * ```\n */\nextern dec withLifecycleUpdate(target: Model, nameTemplate?: valueof string);\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Create" resource lifecycle phase.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Create` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   name: string;\n * }\n *\n * // This model has only the `name` field.\n * model CreateDog is Create<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Create] }, NameTemplate)\nmodel Create<T extends Reflection.Model, NameTemplate extends valueof string = "Create{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Read" resource lifecycle phase.\n *\n * The "Read" lifecycle phase is used for properties returned by operations that read data, like\n * HTTP GET operations.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Read` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // This model has the `id` and `name` fields, but not `secretName`.\n * model ReadDog is Read<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Read] }, NameTemplate)\nmodel Read<T extends Reflection.Model, NameTemplate extends valueof string = "Read{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Update" resource lifecycle phase.\n *\n * The "Update" lifecycle phase is used for properties passed as parameters to operations\n * that update data, like HTTP PATCH operations.\n *\n * This transformation will include only the properties that have the `Lifecycle.Update`\n * visibility modifier, and the types of all properties will be replaced with the\n * equivalent `CreateOrUpdate` transformation.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // This model will have the `secretName` and `name` fields, but not the `id` field.\n * model UpdateDog is Update<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withLifecycleUpdate(NameTemplate)\nmodel Update<T extends Reflection.Model, NameTemplate extends valueof string = "Update{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Create" or "Update" resource lifecycle phases.\n *\n * The "CreateOrUpdate" lifecycle phase is used by default for properties passed as parameters to operations\n * that can create _or_ update data, like HTTP PUT operations.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Create` or `Lifecycle.Update` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   @visibility(Lifecycle.Create)\n *   immutableSecret: string;\n *\n *   @visibility(Lifecycle.Create, Lifecycle.Update)\n *   secretName: string;\n *\n *   name: string;\n * }\n *\n * // This model will have the `immutableSecret`, `secretName`, and `name` fields, but not the `id` field.\n * model CreateOrUpdateDog is CreateOrUpdate<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ any: #[Lifecycle.Create, Lifecycle.Update] }, NameTemplate)\nmodel CreateOrUpdate<\n  T extends Reflection.Model,\n  NameTemplate extends valueof string = "CreateOrUpdate{name}"\n> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Delete" resource lifecycle phase.\n *\n * The "Delete" lifecycle phase is used for properties passed as parameters to operations\n * that delete data, like HTTP DELETE operations.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Delete` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   // Set when the Dog is removed from our data store. This happens when the\n *   // Dog is re-homed to a new owner.\n *   @visibility(Lifecycle.Delete)\n *   nextOwner: string;\n *\n *   name: string;\n * }\n *\n * // This model will have the `nextOwner` and `name` fields, but not the `id` field.\n * model DeleteDog is Delete<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Delete] }, NameTemplate)\nmodel Delete<T extends Reflection.Model, NameTemplate extends valueof string = "Delete{name}"> {\n  ...T;\n}\n\n/**\n * A copy of the input model `T` with only the properties that are visible during the\n * "Query" resource lifecycle phase.\n *\n * The "Query" lifecycle phase is used for properties passed as parameters to operations\n * that read data, like HTTP GET or HEAD operations. This should not be confused for\n * the `@query` decorator, which specifies that the property is transmitted in the\n * query string of an HTTP request.\n *\n * This transformation is recursive, and will include only properties that have the\n * `Lifecycle.Query` visibility modifier.\n *\n * If a `NameTemplate` is provided, the new model will be named according to the template.\n * The template uses the same syntax as the `@friendlyName` decorator.\n *\n * @template T The model to transform.\n * @template NameTemplate The name template to use for the new model.\n *\n *  * @example\n * ```typespec\n * model Dog {\n *   @visibility(Lifecycle.Read)\n *   id: int32;\n *\n *   // When getting information for a Dog, you can set this field to true to include\n *   // some extra information about the Dog\'s pedigree that is normally not returned.\n *   // Alternatively, you could just use a separate option parameter to get this\n *   // information.\n *   @visibility(Lifecycle.Query)\n *   includePedigree?: boolean;\n *\n *   name: string;\n *\n *   // Only included if `includePedigree` is set to true in the request.\n *   @visibility(Lifecycle.Read)\n *   pedigree?: string;\n * }\n *\n * // This model will have the `includePedigree` and `name` fields, but not `id` or `pedigree`.\n * model QueryDog is Query<Dog>;\n * ```\n */\n@doc("")\n@friendlyName(NameTemplate, T)\n@withVisibilityFilter(#{ all: #[Lifecycle.Query] }, NameTemplate)\nmodel Query<T extends Reflection.Model, NameTemplate extends valueof string = "Query{name}"> {\n  ...T;\n}\n',
  "lib/autorest.tsp": 'import "./decorators.tsp";\nimport "../dist/src/tsp-index.js";\n',
  "lib/decorators.tsp": "using Reflection;\n\nnamespace Autorest;\n\n/**\n * `@example` - attaches example files to an operation. Multiple examples can be specified.\n *\n * `@example` can be specified on Operations.\n *\n * @param pathOrUri - path or Uri to the example file.\n * @param title - name or description of the example file.\n */\nextern dec example(target: Operation, pathOrUri: valueof string, title: valueof string);\n\n/**\n * `@useRef` - is used to replace the TypeSpec model type in emitter output with a pre-existing named OpenAPI schema such as Azure Resource Manager common types.\n *\n * `@useRef` can be specified on Models and ModelProperty.\n *\n * @param jsonRef - path or Uri to an OpenAPI schema.\n */\nextern dec useRef(entity: Model | ModelProperty, jsonRef: valueof string);\n"
};
var _TypeSpecLibrary_ = {
  jsSourceFiles: TypeSpecJSSources,
  typespecSourceFiles: TypeSpecSources
};
export {
  $decorators,
  $example,
  $lib,
  $onEmit,
  $useRef,
  _TypeSpecLibrary_,
  getAllServicesAtAllVersions,
  getExamples,
  getOpenAPIForService,
  getRef,
  namespace,
  resolveAutorestOptions,
  sortOpenAPIDocument
};
