import {
  DefaultRouteProducer,
  getRouteProducer,
  setRouteOptionsForNamespace,
  setRouteProducer
} from "./chunk-LSKC7TLM.js";
import "./chunk-QJATEWBM.js";

// src/typespec/core/packages/http/dist/src/experimental/streams.js
var getStreamOf;
try {
  getStreamOf = (await import("@typespec/streams")).getStreamOf;
} catch {
  getStreamOf = () => {
    throw new Error("@typespec/streams was not found");
  };
}
function getStreamMetadata(program, httpParametersOrResponse) {
  const body = httpParametersOrResponse.body;
  if (!body)
    return;
  const contentTypes = body.contentTypes;
  if (!contentTypes.length)
    return;
  const bodyProperty = body.property;
  if (!bodyProperty)
    return;
  const streamData = getStreamFromBodyProperty(program, bodyProperty);
  if (!streamData)
    return;
  return {
    bodyType: body.type,
    originalType: streamData.model,
    streamType: streamData.streamOf,
    contentTypes
  };
}
function getStreamFromBodyProperty(program, bodyProperty) {
  const streamOf = bodyProperty.model ? getStreamOf(program, bodyProperty.model) : void 0;
  if (streamOf) {
    return { model: bodyProperty.model, streamOf };
  }
  if (bodyProperty.sourceProperty) {
    return getStreamFromBodyProperty(program, bodyProperty.sourceProperty);
  }
  return;
}
export {
  getStreamMetadata,
  DefaultRouteProducer as unsafe_DefaultRouteProducer,
  getRouteProducer as unsafe_getRouteProducer,
  setRouteOptionsForNamespace as unsafe_setRouteOptionsForNamespace,
  setRouteProducer as unsafe_setRouteProducer
};
