var __defProp = Object.defineProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// src/typespec/core/packages/events/dist/src/experimental/get-event-definitions.js
import { createDiagnosticCollector, navigateType } from "@typespec/compiler";

// src/typespec/core/packages/events/dist/src/decorators.js
import {} from "@typespec/compiler";
import { useStateMap, useStateSet } from "@typespec/compiler/utils";

// src/typespec/core/packages/events/dist/src/lib.js
import { createTypeSpecLibrary, paramMessage } from "@typespec/compiler";
var $lib = createTypeSpecLibrary({
  name: "@typespec/events",
  diagnostics: {
    "invalid-content-type-target": {
      severity: "error",
      messages: {
        default: `@contentType can only be specified on the top-level event envelope, or the event payload marked with @data`
      }
    },
    "multiple-event-payloads": {
      severity: "error",
      messages: {
        default: paramMessage`Event payload already applied to ${"dataPath"} but also exists under ${"currentPath"}`,
        payloadInIndexedModel: paramMessage`Event payload applied from inside a Record or Array at ${"dataPath"}`
      }
    }
  },
  state: {
    events: { description: "State for the @events decorator." },
    contentType: { description: "State for the @contentType decorator." },
    data: { description: "State for the @data decorator." }
  }
});
var { reportDiagnostic, createDiagnostic, stateKeys: EventsStateKeys } = $lib;

// src/typespec/core/packages/events/dist/src/decorators.js
var [isEvents, setEvents] = useStateSet(EventsStateKeys.events);
var $eventsDecorator = (context, target) => {
  setEvents(context.program, target);
};
var [getContentType, setContentType] = useStateMap(EventsStateKeys.contentType);
var $contentTypeDecorator = (context, target, contentType) => {
  setContentType(context.program, target, contentType);
};
var [isEventData, setEventData] = useStateSet(EventsStateKeys.data);
var $dataDecorator = (context, target) => {
  setEventData(context.program, target);
};

// src/typespec/core/packages/events/dist/src/experimental/get-event-definitions.js
function validateContentType(program, target) {
  const contentType = getContentType(program, target);
  if (!contentType || isEventData(program, target))
    return;
  return createDiagnostic({
    code: "invalid-content-type-target",
    target
  });
}
function stringifyPropertyPath(path) {
  return path.map((p) => {
    switch (p.kind) {
      case "ModelProperty":
        return p.name;
      case "Tuple":
        return "[]";
      case "Model":
        return;
    }
  }).filter(Boolean).join(".");
}
function getEventDefinition(program, target) {
  const diagnostics = createDiagnosticCollector();
  const eventType = typeof target.name === "string" ? target.name : void 0;
  const envelopeContentType = getContentType(program, target);
  let payloadType;
  let payloadContentType;
  let pathToPayload = "";
  let indexerDepth = 0;
  const currentPropertyPath = [];
  const typesThatChainToPayload = /* @__PURE__ */ new Set();
  navigateType(target.type, {
    modelProperty(prop) {
      currentPropertyPath.push(prop);
      const contentTypeDiagnostic = validateContentType(program, prop);
      if (contentTypeDiagnostic) {
        diagnostics.add(contentTypeDiagnostic);
      }
      if (typesThatChainToPayload.has(prop.type)) {
        diagnostics.add(createDiagnostic({
          code: "multiple-event-payloads",
          format: {
            dataPath: pathToPayload,
            currentPath: stringifyPropertyPath(currentPropertyPath)
          },
          target
        }));
        return;
      }
      if (!isEventData(program, prop))
        return;
      currentPropertyPath.forEach((p) => {
        if (p.kind === "ModelProperty") {
          typesThatChainToPayload.add(p.type);
        } else if (p.kind === "Model" || p.kind === "Tuple") {
          typesThatChainToPayload.add(p);
        }
      });
      if (indexerDepth > 0) {
        diagnostics.add(createDiagnostic({
          code: "multiple-event-payloads",
          messageId: "payloadInIndexedModel",
          format: {
            dataPath: stringifyPropertyPath(currentPropertyPath.slice(0, -1))
          },
          target
        }));
        return;
      }
      if (payloadType) {
        diagnostics.add(createDiagnostic({
          code: "multiple-event-payloads",
          format: {
            dataPath: pathToPayload,
            currentPath: stringifyPropertyPath(currentPropertyPath)
          },
          target
        }));
        return;
      }
      payloadType = prop.type;
      payloadContentType = getContentType(program, prop);
      pathToPayload = stringifyPropertyPath(currentPropertyPath);
    },
    exitModelProperty() {
      currentPropertyPath.pop();
    },
    tuple(tuple) {
      currentPropertyPath.push(tuple);
      tuple.values.forEach((value) => {
        if (typesThatChainToPayload.has(value)) {
          diagnostics.add(createDiagnostic({
            code: "multiple-event-payloads",
            format: {
              dataPath: pathToPayload,
              currentPath: stringifyPropertyPath(currentPropertyPath)
            },
            target
          }));
          return;
        }
      });
    },
    exitTuple() {
      currentPropertyPath.pop();
    },
    model(model) {
      if (model.indexer) {
        indexerDepth++;
      }
      currentPropertyPath.push(model);
    },
    exitModel(model) {
      if (model.indexer) {
        indexerDepth--;
      }
      currentPropertyPath.pop();
    }
  }, {});
  const eventDefinition = {
    eventType,
    root: target,
    isEventEnvelope: !!payloadType,
    type: target.type,
    contentType: envelopeContentType,
    payloadType: payloadType ?? target.type,
    payloadContentType: payloadType ? payloadContentType : envelopeContentType
  };
  return diagnostics.wrap(eventDefinition);
}
function getEventDefinitions(program, target) {
  const diagnostics = createDiagnosticCollector();
  const events = [];
  target.variants.forEach((variant) => {
    events.push(diagnostics.pipe(getEventDefinition(program, variant)));
  });
  return diagnostics.wrap(events);
}

export {
  __export,
  $lib,
  EventsStateKeys,
  isEvents,
  $eventsDecorator,
  getContentType,
  $contentTypeDecorator,
  isEventData,
  $dataDecorator,
  getEventDefinitions
};
