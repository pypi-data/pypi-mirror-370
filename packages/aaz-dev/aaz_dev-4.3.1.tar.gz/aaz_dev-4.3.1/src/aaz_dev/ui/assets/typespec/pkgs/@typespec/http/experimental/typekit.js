import {
  getHeaderFieldOptions,
  getHttpOperation,
  getHttpPart,
  getPathParamOptions,
  getQueryParamOptions,
  isHeader,
  isHttpFile,
  isMultipartBodyProperty,
  isPathParam,
  isQueryParam
} from "../chunk-LSKC7TLM.js";
import "../chunk-QJATEWBM.js";

// src/typespec/core/packages/http/dist/src/experimental/typekit/kits/http-operation.js
import { createDiagnosable, defineKit } from "@typespec/compiler/typekit";
defineKit({
  httpOperation: {
    get: createDiagnosable(function(op) {
      return getHttpOperation(this.program, op);
    }),
    getReturnType(httpOperation, options) {
      let responses = this.httpOperation.flattenResponses(httpOperation);
      if (!options?.includeErrors) {
        responses = responses.filter((r) => !this.httpResponse.isErrorResponse(r));
      }
      const voidType = { kind: "Intrinsic", name: "void" };
      let httpReturnType = voidType;
      if (!responses.length) {
        return voidType;
      }
      if (responses.length > 1) {
        const res = [...new Set(responses.map((r) => r.responseContent.body?.type))];
        httpReturnType = this.union.create({
          variants: res.map((t) => {
            return this.unionVariant.create({
              type: getEffectiveType(this, t)
            });
          })
        });
      } else {
        httpReturnType = getEffectiveType(this, responses[0].responseContent.body?.type);
      }
      return httpReturnType;
    },
    flattenResponses(httpOperation) {
      const responsesMap = [];
      for (const response of httpOperation.responses) {
        for (const responseContent of response.responses) {
          const contentTypeProperty = responseContent.properties.find((property) => property.kind === "contentType");
          let contentType;
          if (contentTypeProperty) {
            contentType = contentTypeProperty.property.type.value;
          } else if (responseContent.body) {
            contentType = "application/json";
          }
          responsesMap.push({
            statusCode: response.statusCodes,
            contentType,
            responseContent,
            type: response.type
          });
        }
      }
      return responsesMap;
    }
  }
});
function getEffectiveType(typekit, type) {
  if (type === void 0) {
    return { kind: "Intrinsic", name: "void" };
  }
  if (typekit.model.is(type)) {
    return typekit.model.getEffectiveModel(type);
  }
  return type;
}

// src/typespec/core/packages/http/dist/src/experimental/typekit/kits/http-part.js
import { defineKit as defineKit2 } from "@typespec/compiler/typekit";
defineKit2({
  httpPart: {
    is(type) {
      return this.model.is(type) && this.httpPart.get(type) !== void 0;
    },
    get(type) {
      return getHttpPart(this.program, type);
    },
    unpack(type) {
      const part = this.httpPart.get(type);
      if (part) {
        return part.type;
      }
      return type;
    }
  }
});

// src/typespec/core/packages/http/dist/src/experimental/typekit/kits/http-request.js
import { defineKit as defineKit3 } from "@typespec/compiler/typekit";
defineKit3({
  httpRequest: {
    body: {
      isExplicit(httpOperation) {
        return httpOperation.parameters.properties.find((p) => p.kind === "body" || p.kind === "bodyRoot" || p.kind === "multipartBody") !== void 0;
      }
    },
    getBodyParameters(httpOperation) {
      const body = httpOperation.parameters.body;
      if (!body) {
        return void 0;
      }
      const bodyProperty = body.property;
      if (!bodyProperty) {
        if (body.type.kind === "Model") {
          return body.type;
        }
        throw new Error("Body property not found");
      }
      const bodyPropertyName = bodyProperty.name ? bodyProperty.name : "body";
      return this.model.create({
        properties: { [bodyPropertyName]: bodyProperty }
      });
    },
    getParameters(httpOperation, kind) {
      const kinds = new Set(Array.isArray(kind) ? kind : [kind]);
      const parameterProperties = /* @__PURE__ */ new Map();
      kinds.forEach((kind2) => {
        if (kind2 === "body") {
          this.httpRequest.getBodyParameters(httpOperation)?.properties.forEach((value, key) => parameterProperties.set(key, value));
        } else {
          httpOperation.parameters.properties.filter((p) => p.kind === kind2 && p.property).forEach((p) => parameterProperties.set(p.property.name, p.property));
        }
      });
      if (parameterProperties.size === 0) {
        return void 0;
      }
      const properties = Object.fromEntries(parameterProperties);
      return this.model.create({ properties });
    }
  }
});

// src/typespec/core/packages/http/dist/src/experimental/typekit/kits/http-response.js
import { isErrorModel } from "@typespec/compiler";
import { defineKit as defineKit4 } from "@typespec/compiler/typekit";
defineKit4({
  httpResponse: {
    isErrorResponse(response) {
      return this.model.is(response.type) ? isErrorModel(this.program, response.type) : false;
    },
    statusCode: {
      isSingle(statusCode) {
        return typeof statusCode === "number";
      },
      isRange(statusCode) {
        return typeof statusCode === "object" && "start" in statusCode && "end" in statusCode;
      },
      isDefault(statusCode) {
        return statusCode === "*";
      }
    }
  }
});

// src/typespec/core/packages/http/dist/src/experimental/typekit/kits/model-property.js
import { defineKit as defineKit5 } from "@typespec/compiler/typekit";
defineKit5({
  modelProperty: {
    getHttpParamOptions(prop) {
      if (isHeader(this.program, prop)) {
        return getHeaderFieldOptions(this.program, prop);
      }
      if (isPathParam(this.program, prop)) {
        return getPathParamOptions(this.program, prop);
      }
      if (isQueryParam(this.program, prop)) {
        return getQueryParamOptions(this.program, prop);
      }
      return void 0;
    },
    getHttpHeaderOptions(prop) {
      return getHeaderFieldOptions(this.program, prop);
    },
    getHttpPathOptions(prop) {
      return getPathParamOptions(this.program, prop);
    },
    getHttpQueryOptions(prop) {
      return getQueryParamOptions(this.program, prop);
    },
    isHttpHeader(prop) {
      return isHeader(this.program, prop);
    },
    isHttpPathParam(prop) {
      return isPathParam(this.program, prop);
    },
    isHttpQueryParam(prop) {
      return isQueryParam(this.program, prop);
    },
    isHttpMultipartBody(prop) {
      return isMultipartBodyProperty(this.program, prop);
    }
  }
});

// src/typespec/core/packages/http/dist/src/experimental/typekit/kits/model.js
import { defineKit as defineKit6 } from "@typespec/compiler/typekit";
defineKit6({
  model: {
    isHttpFile(model) {
      return isHttpFile(this.program, model);
    }
  }
});
