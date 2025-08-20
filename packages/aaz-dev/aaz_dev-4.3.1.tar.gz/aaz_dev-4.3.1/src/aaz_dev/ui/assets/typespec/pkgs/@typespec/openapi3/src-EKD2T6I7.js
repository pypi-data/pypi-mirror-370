import "./chunk-QRPWKJ4C.js";

// src/typespec/core/packages/xml/dist/src/decorators.js
import { $encodedName } from "@typespec/compiler";

// src/typespec/core/packages/xml/dist/src/lib.js
import { createTypeSpecLibrary, paramMessage } from "@typespec/compiler";
var $lib = createTypeSpecLibrary({
  name: "@typespec/xml",
  diagnostics: {
    "ns-enum-not-declaration": {
      severity: "error",
      messages: {
        default: "Enum member used as namespace must be part of an enum marked with @nsDeclaration."
      }
    },
    "invalid-ns-declaration-member": {
      severity: "error",
      messages: {
        default: paramMessage`Enum member ${"name"} must have a value that is the XML namespace url.`
      }
    },
    "ns-missing-prefix": {
      severity: "error",
      messages: {
        default: "When using a string namespace you must provide a prefix as the 2nd argument."
      }
    },
    "prefix-not-allowed": {
      severity: "error",
      messages: {
        default: "@ns decorator cannot have the prefix parameter set when using an enum member."
      }
    },
    "ns-not-uri": {
      severity: "error",
      messages: {
        default: `Namespace ${"namespace"} is not a valid URI.`
      }
    }
  },
  state: {
    attribute: { description: "Mark a model property to be serialized as xml attribute" },
    unwrapped: {
      description: "Mark a model property to be serialized without a node wrapping the content."
    },
    ns: { description: "Namespace data" },
    nsDeclaration: { description: "Mark an enum that declares Xml Namespaces" }
  }
});
var { reportDiagnostic, createStateSymbol, stateKeys: XmlStateKeys } = $lib;

// src/typespec/core/packages/xml/dist/src/decorators.js
var $name = (context, target, name) => {
  context.call($encodedName, target, "application/xml", name);
};
var $attribute = (context, target) => {
  context.program.stateSet(XmlStateKeys.attribute).add(target);
};
function isAttribute(program, target) {
  return program.stateSet(XmlStateKeys.attribute).has(target);
}
var $unwrapped = (context, target) => {
  context.program.stateSet(XmlStateKeys.unwrapped).add(target);
};
function isUnwrapped(program, target) {
  return program.stateSet(XmlStateKeys.unwrapped).has(target);
}
var $nsDeclarations = (context, target) => {
  context.program.stateSet(XmlStateKeys.nsDeclaration).add(target);
};
function isNsDeclarationsEnum(program, target) {
  return program.stateSet(XmlStateKeys.nsDeclaration).has(target);
}
var $ns = (context, target, namespace, prefix) => {
  const data = getData(context, namespace, prefix);
  if (data) {
    if (validateNamespaceIsUri(context, data.namespace)) {
      context.program.stateMap(XmlStateKeys.nsDeclaration).set(target, data);
    }
  }
};
function getNs(program, target) {
  return program.stateMap(XmlStateKeys.nsDeclaration).get(target);
}
function getData(context, namespace, prefix) {
  switch (namespace.kind) {
    case "String":
      if (!prefix) {
        reportDiagnostic(context.program, {
          code: "ns-missing-prefix",
          target: context.decoratorTarget
        });
        return void 0;
      }
      return { namespace: namespace.value, prefix };
    case "EnumMember":
      if (!isNsDeclarationsEnum(context.program, namespace.enum)) {
        reportDiagnostic(context.program, {
          code: "ns-enum-not-declaration",
          target: context.decoratorTarget
        });
        return void 0;
      }
      if (prefix !== void 0) {
        reportDiagnostic(context.program, {
          code: "prefix-not-allowed",
          target: context.getArgumentTarget(1),
          format: { name: namespace.name }
        });
      }
      if (typeof namespace.value !== "string") {
        reportDiagnostic(context.program, {
          code: "invalid-ns-declaration-member",
          target: context.decoratorTarget,
          format: { name: namespace.name }
        });
        return void 0;
      }
      return { namespace: namespace.value, prefix: namespace.name };
    default:
      return void 0;
  }
}
function validateNamespaceIsUri(context, namespace) {
  try {
    new URL(namespace);
    return true;
  } catch {
    reportDiagnostic(context.program, {
      code: "ns-not-uri",
      target: context.getArgumentTarget(0),
      format: { namespace }
    });
    return false;
  }
}

// src/typespec/core/packages/xml/dist/src/encoding.js
import { getEncode } from "@typespec/compiler";
function getXmlEncoding(program, type) {
  const encodeData = getEncode(program, type);
  if (encodeData) {
    return encodeData;
  }
  const def = getDefaultEncoding(type.kind === "Scalar" ? type : type.type);
  if (def === void 0) {
    return void 0;
  }
  return { encoding: def, type: program.checker.getStdType("string") };
}
function getDefaultEncoding(type) {
  switch (type.name) {
    case "utcDateTime":
    case "offsetDateTime":
      return "TypeSpec.Xml.Encoding.xmlDateTime";
    case "plainDate":
      return "TypeSpec.Xml.Encoding.xmlDate";
    case "plainTime":
      return "TypeSpec.Xml.Encoding.xmlTime";
    case "duration":
      return "TypeSpec.Xml.Encoding.xmlDuration";
    case "bytes":
      return "TypeSpec.Xml.Encoding.xmlBase64Binary";
    default:
      return void 0;
  }
}

// src/typespec/core/packages/xml/dist/src/tsp-index.js
var $decorators = {
  "TypeSpec.Xml": {
    attribute: $attribute,
    name: $name,
    ns: $ns,
    nsDeclarations: $nsDeclarations,
    unwrapped: $unwrapped
  }
};
export {
  $attribute,
  $decorators,
  $lib,
  $name,
  $ns,
  $nsDeclarations,
  $unwrapped,
  getNs,
  getXmlEncoding,
  isAttribute,
  isUnwrapped
};
