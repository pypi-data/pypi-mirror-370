import {
  isArray,
  mutate
} from "./chunk-3K4NAOXV.js";
import {
  getAnyExtensionFromPath
} from "./chunk-OV76USRJ.js";

// src/typespec/core/packages/compiler/dist/src/core/param-message.js
function paramMessage(strings, ...keys) {
  const template = (dict) => {
    const result = [strings[0]];
    keys.forEach((key, i) => {
      const value = dict[key];
      if (value !== void 0) {
        result.push(value);
      }
      result.push(strings[i + 1]);
    });
    return result.join("");
  };
  template.keys = keys;
  return template;
}

// src/typespec/core/packages/compiler/dist/src/core/source-file.js
function createSourceFile(text, path) {
  let lineStarts = void 0;
  return {
    text,
    path,
    getLineStarts,
    getLineAndCharacterOfPosition
  };
  function getLineStarts() {
    return lineStarts = lineStarts ?? scanLineStarts(text);
  }
  function getLineAndCharacterOfPosition(position) {
    const starts = getLineStarts();
    let line = binarySearch(starts, position);
    if (line < 0) {
      line = ~line - 1;
    }
    return {
      line,
      character: position - starts[line]
    };
  }
}
function getSourceFileKindFromExt(path) {
  const ext = getAnyExtensionFromPath(path);
  if (ext === ".js" || ext === ".mjs") {
    return "js";
  } else if (ext === ".tsp") {
    return "typespec";
  } else {
    return void 0;
  }
}
function scanLineStarts(text) {
  const starts = [];
  let start = 0;
  let pos = 0;
  while (pos < text.length) {
    const ch = text.charCodeAt(pos);
    pos++;
    switch (ch) {
      case 13:
        if (text.charCodeAt(pos) === 10) {
          pos++;
        }
      // fallthrough
      case 10:
        starts.push(start);
        start = pos;
        break;
    }
  }
  starts.push(start);
  return starts;
}
function binarySearch(array, value) {
  let low = 0;
  let high = array.length - 1;
  while (low <= high) {
    const middle = low + (high - low >> 1);
    const v = array[middle];
    if (v < value) {
      low = middle + 1;
    } else if (v > value) {
      high = middle - 1;
    } else {
      return middle;
    }
  }
  return ~low;
}

// src/typespec/core/packages/compiler/dist/src/core/types.js
var ResolutionResultFlags;
(function(ResolutionResultFlags2) {
  ResolutionResultFlags2[ResolutionResultFlags2["None"] = 0] = "None";
  ResolutionResultFlags2[ResolutionResultFlags2["Resolved"] = 2] = "Resolved";
  ResolutionResultFlags2[ResolutionResultFlags2["Unknown"] = 4] = "Unknown";
  ResolutionResultFlags2[ResolutionResultFlags2["Ambiguous"] = 8] = "Ambiguous";
  ResolutionResultFlags2[ResolutionResultFlags2["NotFound"] = 16] = "NotFound";
  ResolutionResultFlags2[ResolutionResultFlags2["ResolutionFailed"] = 28] = "ResolutionFailed";
})(ResolutionResultFlags || (ResolutionResultFlags = {}));
var SyntaxKind;
(function(SyntaxKind2) {
  SyntaxKind2[SyntaxKind2["TypeSpecScript"] = 0] = "TypeSpecScript";
  SyntaxKind2[SyntaxKind2["JsSourceFile"] = 1] = "JsSourceFile";
  SyntaxKind2[SyntaxKind2["ImportStatement"] = 2] = "ImportStatement";
  SyntaxKind2[SyntaxKind2["Identifier"] = 3] = "Identifier";
  SyntaxKind2[SyntaxKind2["AugmentDecoratorStatement"] = 4] = "AugmentDecoratorStatement";
  SyntaxKind2[SyntaxKind2["DecoratorExpression"] = 5] = "DecoratorExpression";
  SyntaxKind2[SyntaxKind2["DirectiveExpression"] = 6] = "DirectiveExpression";
  SyntaxKind2[SyntaxKind2["MemberExpression"] = 7] = "MemberExpression";
  SyntaxKind2[SyntaxKind2["NamespaceStatement"] = 8] = "NamespaceStatement";
  SyntaxKind2[SyntaxKind2["UsingStatement"] = 9] = "UsingStatement";
  SyntaxKind2[SyntaxKind2["OperationStatement"] = 10] = "OperationStatement";
  SyntaxKind2[SyntaxKind2["OperationSignatureDeclaration"] = 11] = "OperationSignatureDeclaration";
  SyntaxKind2[SyntaxKind2["OperationSignatureReference"] = 12] = "OperationSignatureReference";
  SyntaxKind2[SyntaxKind2["ModelStatement"] = 13] = "ModelStatement";
  SyntaxKind2[SyntaxKind2["ModelExpression"] = 14] = "ModelExpression";
  SyntaxKind2[SyntaxKind2["ModelProperty"] = 15] = "ModelProperty";
  SyntaxKind2[SyntaxKind2["ModelSpreadProperty"] = 16] = "ModelSpreadProperty";
  SyntaxKind2[SyntaxKind2["ScalarStatement"] = 17] = "ScalarStatement";
  SyntaxKind2[SyntaxKind2["InterfaceStatement"] = 18] = "InterfaceStatement";
  SyntaxKind2[SyntaxKind2["UnionStatement"] = 19] = "UnionStatement";
  SyntaxKind2[SyntaxKind2["UnionVariant"] = 20] = "UnionVariant";
  SyntaxKind2[SyntaxKind2["EnumStatement"] = 21] = "EnumStatement";
  SyntaxKind2[SyntaxKind2["EnumMember"] = 22] = "EnumMember";
  SyntaxKind2[SyntaxKind2["EnumSpreadMember"] = 23] = "EnumSpreadMember";
  SyntaxKind2[SyntaxKind2["AliasStatement"] = 24] = "AliasStatement";
  SyntaxKind2[SyntaxKind2["DecoratorDeclarationStatement"] = 25] = "DecoratorDeclarationStatement";
  SyntaxKind2[SyntaxKind2["FunctionDeclarationStatement"] = 26] = "FunctionDeclarationStatement";
  SyntaxKind2[SyntaxKind2["FunctionParameter"] = 27] = "FunctionParameter";
  SyntaxKind2[SyntaxKind2["UnionExpression"] = 28] = "UnionExpression";
  SyntaxKind2[SyntaxKind2["IntersectionExpression"] = 29] = "IntersectionExpression";
  SyntaxKind2[SyntaxKind2["TupleExpression"] = 30] = "TupleExpression";
  SyntaxKind2[SyntaxKind2["ArrayExpression"] = 31] = "ArrayExpression";
  SyntaxKind2[SyntaxKind2["StringLiteral"] = 32] = "StringLiteral";
  SyntaxKind2[SyntaxKind2["NumericLiteral"] = 33] = "NumericLiteral";
  SyntaxKind2[SyntaxKind2["BooleanLiteral"] = 34] = "BooleanLiteral";
  SyntaxKind2[SyntaxKind2["StringTemplateExpression"] = 35] = "StringTemplateExpression";
  SyntaxKind2[SyntaxKind2["StringTemplateHead"] = 36] = "StringTemplateHead";
  SyntaxKind2[SyntaxKind2["StringTemplateMiddle"] = 37] = "StringTemplateMiddle";
  SyntaxKind2[SyntaxKind2["StringTemplateTail"] = 38] = "StringTemplateTail";
  SyntaxKind2[SyntaxKind2["StringTemplateSpan"] = 39] = "StringTemplateSpan";
  SyntaxKind2[SyntaxKind2["ExternKeyword"] = 40] = "ExternKeyword";
  SyntaxKind2[SyntaxKind2["VoidKeyword"] = 41] = "VoidKeyword";
  SyntaxKind2[SyntaxKind2["NeverKeyword"] = 42] = "NeverKeyword";
  SyntaxKind2[SyntaxKind2["UnknownKeyword"] = 43] = "UnknownKeyword";
  SyntaxKind2[SyntaxKind2["ValueOfExpression"] = 44] = "ValueOfExpression";
  SyntaxKind2[SyntaxKind2["TypeReference"] = 45] = "TypeReference";
  SyntaxKind2[SyntaxKind2["TemplateParameterDeclaration"] = 46] = "TemplateParameterDeclaration";
  SyntaxKind2[SyntaxKind2["EmptyStatement"] = 47] = "EmptyStatement";
  SyntaxKind2[SyntaxKind2["InvalidStatement"] = 48] = "InvalidStatement";
  SyntaxKind2[SyntaxKind2["LineComment"] = 49] = "LineComment";
  SyntaxKind2[SyntaxKind2["BlockComment"] = 50] = "BlockComment";
  SyntaxKind2[SyntaxKind2["Doc"] = 51] = "Doc";
  SyntaxKind2[SyntaxKind2["DocText"] = 52] = "DocText";
  SyntaxKind2[SyntaxKind2["DocParamTag"] = 53] = "DocParamTag";
  SyntaxKind2[SyntaxKind2["DocPropTag"] = 54] = "DocPropTag";
  SyntaxKind2[SyntaxKind2["DocReturnsTag"] = 55] = "DocReturnsTag";
  SyntaxKind2[SyntaxKind2["DocErrorsTag"] = 56] = "DocErrorsTag";
  SyntaxKind2[SyntaxKind2["DocTemplateTag"] = 57] = "DocTemplateTag";
  SyntaxKind2[SyntaxKind2["DocUnknownTag"] = 58] = "DocUnknownTag";
  SyntaxKind2[SyntaxKind2["Return"] = 59] = "Return";
  SyntaxKind2[SyntaxKind2["JsNamespaceDeclaration"] = 60] = "JsNamespaceDeclaration";
  SyntaxKind2[SyntaxKind2["TemplateArgument"] = 61] = "TemplateArgument";
  SyntaxKind2[SyntaxKind2["TypeOfExpression"] = 62] = "TypeOfExpression";
  SyntaxKind2[SyntaxKind2["ObjectLiteral"] = 63] = "ObjectLiteral";
  SyntaxKind2[SyntaxKind2["ObjectLiteralProperty"] = 64] = "ObjectLiteralProperty";
  SyntaxKind2[SyntaxKind2["ObjectLiteralSpreadProperty"] = 65] = "ObjectLiteralSpreadProperty";
  SyntaxKind2[SyntaxKind2["ArrayLiteral"] = 66] = "ArrayLiteral";
  SyntaxKind2[SyntaxKind2["ConstStatement"] = 67] = "ConstStatement";
  SyntaxKind2[SyntaxKind2["CallExpression"] = 68] = "CallExpression";
  SyntaxKind2[SyntaxKind2["ScalarConstructor"] = 69] = "ScalarConstructor";
})(SyntaxKind || (SyntaxKind = {}));
var IdentifierKind;
(function(IdentifierKind2) {
  IdentifierKind2[IdentifierKind2["TypeReference"] = 0] = "TypeReference";
  IdentifierKind2[IdentifierKind2["TemplateArgument"] = 1] = "TemplateArgument";
  IdentifierKind2[IdentifierKind2["Decorator"] = 2] = "Decorator";
  IdentifierKind2[IdentifierKind2["Function"] = 3] = "Function";
  IdentifierKind2[IdentifierKind2["Using"] = 4] = "Using";
  IdentifierKind2[IdentifierKind2["Declaration"] = 5] = "Declaration";
  IdentifierKind2[IdentifierKind2["ModelExpressionProperty"] = 6] = "ModelExpressionProperty";
  IdentifierKind2[IdentifierKind2["ModelStatementProperty"] = 7] = "ModelStatementProperty";
  IdentifierKind2[IdentifierKind2["ObjectLiteralProperty"] = 8] = "ObjectLiteralProperty";
  IdentifierKind2[IdentifierKind2["Other"] = 9] = "Other";
})(IdentifierKind || (IdentifierKind = {}));
var NoTarget = Symbol.for("NoTarget");
var ListenerFlow;
(function(ListenerFlow2) {
  ListenerFlow2[ListenerFlow2["NoRecursion"] = 1] = "NoRecursion";
})(ListenerFlow || (ListenerFlow = {}));

// src/typespec/core/packages/compiler/dist/src/core/diagnostics.js
function logDiagnostics(diagnostics2, logger) {
  for (const diagnostic of diagnostics2) {
    logger.log({
      level: diagnostic.severity,
      message: diagnostic.message,
      code: diagnostic.code,
      url: diagnostic.url,
      sourceLocation: getSourceLocation(diagnostic.target, { locateId: true }),
      related: getRelatedLocations(diagnostic)
    });
  }
}
function getRelatedLocations(diagnostic) {
  return getDiagnosticTemplateInstantitationTrace(diagnostic.target).map((x) => {
    return {
      message: "occurred while instantiating template",
      location: getSourceLocation(x)
    };
  });
}
function getSourceLocation(target, options = {}) {
  if (target === NoTarget || target === void 0) {
    return void 0;
  }
  if ("file" in target) {
    return target;
  }
  if (!("kind" in target) && !("entityKind" in target)) {
    if (!("declarations" in target)) {
      return getSourceLocationOfNode(target.node, options);
    }
    if (target.flags & 8192) {
      target = target.symbolSource;
    }
    if (!target.declarations[0]) {
      return createSyntheticSourceLocation();
    }
    return getSourceLocationOfNode(target.declarations[0], options);
  } else if ("kind" in target && typeof target.kind === "number") {
    return getSourceLocationOfNode(target, options);
  } else {
    const targetNode = target.node;
    if (targetNode) {
      return getSourceLocationOfNode(targetNode, options);
    }
    return createSyntheticSourceLocation();
  }
}
function getDiagnosticTemplateInstantitationTrace(target) {
  if (typeof target !== "object" || !("templateMapper" in target)) {
    return [];
  }
  const result = [];
  let current = target.templateMapper;
  while (current) {
    result.push(current.source.node);
    current = current.source.mapper;
  }
  return result;
}
function createSyntheticSourceLocation(loc = "<unknown location>") {
  return {
    file: createSourceFile("", loc),
    pos: 0,
    end: 0,
    isSynthetic: true
  };
}
function getSourceLocationOfNode(node, options) {
  let root = node;
  while (root.parent !== void 0) {
    root = root.parent;
  }
  if (root.kind !== SyntaxKind.TypeSpecScript && root.kind !== SyntaxKind.JsSourceFile) {
    return createSyntheticSourceLocation(node.flags & 8 ? void 0 : "<unknown location - cannot obtain source location of unbound node - file bug at https://github.com/microsoft/typespec>");
  }
  if (options.locateId && "id" in node && node.id !== void 0) {
    node = node.id;
  }
  return {
    file: root.file,
    pos: node.pos,
    end: node.end
  };
}
function compilerAssert(condition, message, target) {
  if (condition) {
    return;
  }
  if (target) {
    let location;
    try {
      location = getSourceLocation(target);
    } catch (err) {
    }
    if (location) {
      const pos = location.file.getLineAndCharacterOfPosition(location.pos);
      const file = location.file.path;
      const line = pos.line + 1;
      const col = pos.character + 1;
      message += `
Occurred while compiling code in ${file} near line ${line}, column ${col}`;
    }
  }
  throw new Error(message);
}
function assertType(typeDescription, t, ...kinds) {
  if (kinds.indexOf(t.kind) === -1) {
    throw new Error(`Expected ${typeDescription} to be type ${kinds.join(", ")}`);
  }
}
function reportDeprecated(program, message, target) {
  program.reportDiagnostic({
    severity: "warning",
    code: "deprecated",
    message: `Deprecated: ${message}`,
    target
  });
}
function createDiagnosticCollector() {
  const diagnostics2 = [];
  return {
    diagnostics: diagnostics2,
    add,
    pipe,
    wrap,
    join
  };
  function add(diagnostic) {
    diagnostics2.push(diagnostic);
  }
  function pipe(result) {
    const [value, diags] = result;
    for (const diag of diags) {
      diagnostics2.push(diag);
    }
    return value;
  }
  function wrap(value) {
    return [value, diagnostics2];
  }
  function join(result) {
    const [value, diags] = result;
    for (const diag of diags) {
      diagnostics2.push(diag);
    }
    return [value, diagnostics2];
  }
}
function ignoreDiagnostics(result) {
  return result[0];
}
function defineCodeFix(fix) {
  return fix;
}

// src/typespec/core/packages/compiler/dist/src/core/nonascii.js
var nonAsciiIdentifierMap = [
  160,
  887,
  890,
  895,
  900,
  906,
  908,
  908,
  910,
  929,
  931,
  1327,
  1329,
  1366,
  1369,
  1418,
  1421,
  1423,
  1425,
  1479,
  1488,
  1514,
  1519,
  1524,
  1536,
  1805,
  1807,
  1866,
  1869,
  1969,
  1984,
  2042,
  2045,
  2093,
  2096,
  2110,
  2112,
  2139,
  2142,
  2142,
  2144,
  2154,
  2160,
  2190,
  2192,
  2193,
  2200,
  2435,
  2437,
  2444,
  2447,
  2448,
  2451,
  2472,
  2474,
  2480,
  2482,
  2482,
  2486,
  2489,
  2492,
  2500,
  2503,
  2504,
  2507,
  2510,
  2519,
  2519,
  2524,
  2525,
  2527,
  2531,
  2534,
  2558,
  2561,
  2563,
  2565,
  2570,
  2575,
  2576,
  2579,
  2600,
  2602,
  2608,
  2610,
  2611,
  2613,
  2614,
  2616,
  2617,
  2620,
  2620,
  2622,
  2626,
  2631,
  2632,
  2635,
  2637,
  2641,
  2641,
  2649,
  2652,
  2654,
  2654,
  2662,
  2678,
  2689,
  2691,
  2693,
  2701,
  2703,
  2705,
  2707,
  2728,
  2730,
  2736,
  2738,
  2739,
  2741,
  2745,
  2748,
  2757,
  2759,
  2761,
  2763,
  2765,
  2768,
  2768,
  2784,
  2787,
  2790,
  2801,
  2809,
  2815,
  2817,
  2819,
  2821,
  2828,
  2831,
  2832,
  2835,
  2856,
  2858,
  2864,
  2866,
  2867,
  2869,
  2873,
  2876,
  2884,
  2887,
  2888,
  2891,
  2893,
  2901,
  2903,
  2908,
  2909,
  2911,
  2915,
  2918,
  2935,
  2946,
  2947,
  2949,
  2954,
  2958,
  2960,
  2962,
  2965,
  2969,
  2970,
  2972,
  2972,
  2974,
  2975,
  2979,
  2980,
  2984,
  2986,
  2990,
  3001,
  3006,
  3010,
  3014,
  3016,
  3018,
  3021,
  3024,
  3024,
  3031,
  3031,
  3046,
  3066,
  3072,
  3084,
  3086,
  3088,
  3090,
  3112,
  3114,
  3129,
  3132,
  3140,
  3142,
  3144,
  3146,
  3149,
  3157,
  3158,
  3160,
  3162,
  3165,
  3165,
  3168,
  3171,
  3174,
  3183,
  3191,
  3212,
  3214,
  3216,
  3218,
  3240,
  3242,
  3251,
  3253,
  3257,
  3260,
  3268,
  3270,
  3272,
  3274,
  3277,
  3285,
  3286,
  3293,
  3294,
  3296,
  3299,
  3302,
  3311,
  3313,
  3315,
  3328,
  3340,
  3342,
  3344,
  3346,
  3396,
  3398,
  3400,
  3402,
  3407,
  3412,
  3427,
  3430,
  3455,
  3457,
  3459,
  3461,
  3478,
  3482,
  3505,
  3507,
  3515,
  3517,
  3517,
  3520,
  3526,
  3530,
  3530,
  3535,
  3540,
  3542,
  3542,
  3544,
  3551,
  3558,
  3567,
  3570,
  3572,
  3585,
  3642,
  3647,
  3675,
  3713,
  3714,
  3716,
  3716,
  3718,
  3722,
  3724,
  3747,
  3749,
  3749,
  3751,
  3773,
  3776,
  3780,
  3782,
  3782,
  3784,
  3790,
  3792,
  3801,
  3804,
  3807,
  3840,
  3911,
  3913,
  3948,
  3953,
  3991,
  3993,
  4028,
  4030,
  4044,
  4046,
  4058,
  4096,
  4293,
  4295,
  4295,
  4301,
  4301,
  4304,
  4680,
  4682,
  4685,
  4688,
  4694,
  4696,
  4696,
  4698,
  4701,
  4704,
  4744,
  4746,
  4749,
  4752,
  4784,
  4786,
  4789,
  4792,
  4798,
  4800,
  4800,
  4802,
  4805,
  4808,
  4822,
  4824,
  4880,
  4882,
  4885,
  4888,
  4954,
  4957,
  4988,
  4992,
  5017,
  5024,
  5109,
  5112,
  5117,
  5120,
  5788,
  5792,
  5880,
  5888,
  5909,
  5919,
  5942,
  5952,
  5971,
  5984,
  5996,
  5998,
  6e3,
  6002,
  6003,
  6016,
  6109,
  6112,
  6121,
  6128,
  6137,
  6144,
  6169,
  6176,
  6264,
  6272,
  6314,
  6320,
  6389,
  6400,
  6430,
  6432,
  6443,
  6448,
  6459,
  6464,
  6464,
  6468,
  6509,
  6512,
  6516,
  6528,
  6571,
  6576,
  6601,
  6608,
  6618,
  6622,
  6683,
  6686,
  6750,
  6752,
  6780,
  6783,
  6793,
  6800,
  6809,
  6816,
  6829,
  6832,
  6862,
  6912,
  6988,
  6992,
  7038,
  7040,
  7155,
  7164,
  7223,
  7227,
  7241,
  7245,
  7304,
  7312,
  7354,
  7357,
  7367,
  7376,
  7418,
  7424,
  7957,
  7960,
  7965,
  7968,
  8005,
  8008,
  8013,
  8016,
  8023,
  8025,
  8025,
  8027,
  8027,
  8029,
  8029,
  8031,
  8061,
  8064,
  8116,
  8118,
  8132,
  8134,
  8147,
  8150,
  8155,
  8157,
  8175,
  8178,
  8180,
  8182,
  8190,
  8192,
  8205,
  8208,
  8231,
  8234,
  8292,
  8294,
  8305,
  8308,
  8334,
  8336,
  8348,
  8352,
  8384,
  8400,
  8432,
  8448,
  8587,
  8592,
  9254,
  9280,
  9290,
  9312,
  11123,
  11126,
  11157,
  11159,
  11507,
  11513,
  11557,
  11559,
  11559,
  11565,
  11565,
  11568,
  11623,
  11631,
  11632,
  11647,
  11670,
  11680,
  11686,
  11688,
  11694,
  11696,
  11702,
  11704,
  11710,
  11712,
  11718,
  11720,
  11726,
  11728,
  11734,
  11736,
  11742,
  11744,
  11869,
  11904,
  11929,
  11931,
  12019,
  12032,
  12245,
  12272,
  12283,
  12288,
  12351,
  12353,
  12438,
  12441,
  12543,
  12549,
  12591,
  12593,
  12686,
  12688,
  12771,
  12784,
  12830,
  12832,
  42124,
  42128,
  42182,
  42192,
  42539,
  42560,
  42743,
  42752,
  42954,
  42960,
  42961,
  42963,
  42963,
  42965,
  42969,
  42994,
  43052,
  43056,
  43065,
  43072,
  43127,
  43136,
  43205,
  43214,
  43225,
  43232,
  43347,
  43359,
  43388,
  43392,
  43469,
  43471,
  43481,
  43486,
  43518,
  43520,
  43574,
  43584,
  43597,
  43600,
  43609,
  43612,
  43714,
  43739,
  43766,
  43777,
  43782,
  43785,
  43790,
  43793,
  43798,
  43808,
  43814,
  43816,
  43822,
  43824,
  43883,
  43888,
  44013,
  44016,
  44025,
  44032,
  55203,
  55216,
  55238,
  55243,
  55291,
  63744,
  64109,
  64112,
  64217,
  64256,
  64262,
  64275,
  64279,
  64285,
  64310,
  64312,
  64316,
  64318,
  64318,
  64320,
  64321,
  64323,
  64324,
  64326,
  64450,
  64467,
  64911,
  64914,
  64967,
  64975,
  64975,
  65008,
  65049,
  65056,
  65106,
  65108,
  65126,
  65128,
  65131,
  65136,
  65140,
  65142,
  65276,
  65279,
  65279,
  65281,
  65470,
  65474,
  65479,
  65482,
  65487,
  65490,
  65495,
  65498,
  65500,
  65504,
  65510,
  65512,
  65518,
  65529,
  65532,
  65536,
  65547,
  65549,
  65574,
  65576,
  65594,
  65596,
  65597,
  65599,
  65613,
  65616,
  65629,
  65664,
  65786,
  65792,
  65794,
  65799,
  65843,
  65847,
  65934,
  65936,
  65948,
  65952,
  65952,
  66e3,
  66045,
  66176,
  66204,
  66208,
  66256,
  66272,
  66299,
  66304,
  66339,
  66349,
  66378,
  66384,
  66426,
  66432,
  66461,
  66463,
  66499,
  66504,
  66517,
  66560,
  66717,
  66720,
  66729,
  66736,
  66771,
  66776,
  66811,
  66816,
  66855,
  66864,
  66915,
  66927,
  66938,
  66940,
  66954,
  66956,
  66962,
  66964,
  66965,
  66967,
  66977,
  66979,
  66993,
  66995,
  67001,
  67003,
  67004,
  67072,
  67382,
  67392,
  67413,
  67424,
  67431,
  67456,
  67461,
  67463,
  67504,
  67506,
  67514,
  67584,
  67589,
  67592,
  67592,
  67594,
  67637,
  67639,
  67640,
  67644,
  67644,
  67647,
  67669,
  67671,
  67742,
  67751,
  67759,
  67808,
  67826,
  67828,
  67829,
  67835,
  67867,
  67871,
  67897,
  67903,
  67903,
  67968,
  68023,
  68028,
  68047,
  68050,
  68099,
  68101,
  68102,
  68108,
  68115,
  68117,
  68119,
  68121,
  68149,
  68152,
  68154,
  68159,
  68168,
  68176,
  68184,
  68192,
  68255,
  68288,
  68326,
  68331,
  68342,
  68352,
  68405,
  68409,
  68437,
  68440,
  68466,
  68472,
  68497,
  68505,
  68508,
  68521,
  68527,
  68608,
  68680,
  68736,
  68786,
  68800,
  68850,
  68858,
  68903,
  68912,
  68921,
  69216,
  69246,
  69248,
  69289,
  69291,
  69293,
  69296,
  69297,
  69373,
  69415,
  69424,
  69465,
  69488,
  69513,
  69552,
  69579,
  69600,
  69622,
  69632,
  69709,
  69714,
  69749,
  69759,
  69826,
  69837,
  69837,
  69840,
  69864,
  69872,
  69881,
  69888,
  69940,
  69942,
  69959,
  69968,
  70006,
  70016,
  70111,
  70113,
  70132,
  70144,
  70161,
  70163,
  70209,
  70272,
  70278,
  70280,
  70280,
  70282,
  70285,
  70287,
  70301,
  70303,
  70313,
  70320,
  70378,
  70384,
  70393,
  70400,
  70403,
  70405,
  70412,
  70415,
  70416,
  70419,
  70440,
  70442,
  70448,
  70450,
  70451,
  70453,
  70457,
  70459,
  70468,
  70471,
  70472,
  70475,
  70477,
  70480,
  70480,
  70487,
  70487,
  70493,
  70499,
  70502,
  70508,
  70512,
  70516,
  70656,
  70747,
  70749,
  70753,
  70784,
  70855,
  70864,
  70873,
  71040,
  71093,
  71096,
  71133,
  71168,
  71236,
  71248,
  71257,
  71264,
  71276,
  71296,
  71353,
  71360,
  71369,
  71424,
  71450,
  71453,
  71467,
  71472,
  71494,
  71680,
  71739,
  71840,
  71922,
  71935,
  71942,
  71945,
  71945,
  71948,
  71955,
  71957,
  71958,
  71960,
  71989,
  71991,
  71992,
  71995,
  72006,
  72016,
  72025,
  72096,
  72103,
  72106,
  72151,
  72154,
  72164,
  72192,
  72263,
  72272,
  72354,
  72368,
  72440,
  72448,
  72457,
  72704,
  72712,
  72714,
  72758,
  72760,
  72773,
  72784,
  72812,
  72816,
  72847,
  72850,
  72871,
  72873,
  72886,
  72960,
  72966,
  72968,
  72969,
  72971,
  73014,
  73018,
  73018,
  73020,
  73021,
  73023,
  73031,
  73040,
  73049,
  73056,
  73061,
  73063,
  73064,
  73066,
  73102,
  73104,
  73105,
  73107,
  73112,
  73120,
  73129,
  73440,
  73464,
  73472,
  73488,
  73490,
  73530,
  73534,
  73561,
  73648,
  73648,
  73664,
  73713,
  73727,
  74649,
  74752,
  74862,
  74864,
  74868,
  74880,
  75075,
  77712,
  77810,
  77824,
  78933,
  82944,
  83526,
  92160,
  92728,
  92736,
  92766,
  92768,
  92777,
  92782,
  92862,
  92864,
  92873,
  92880,
  92909,
  92912,
  92917,
  92928,
  92997,
  93008,
  93017,
  93019,
  93025,
  93027,
  93047,
  93053,
  93071,
  93760,
  93850,
  93952,
  94026,
  94031,
  94087,
  94095,
  94111,
  94176,
  94180,
  94192,
  94193,
  94208,
  100343,
  100352,
  101589,
  101632,
  101640,
  110576,
  110579,
  110581,
  110587,
  110589,
  110590,
  110592,
  110882,
  110898,
  110898,
  110928,
  110930,
  110933,
  110933,
  110948,
  110951,
  110960,
  111355,
  113664,
  113770,
  113776,
  113788,
  113792,
  113800,
  113808,
  113817,
  113820,
  113827,
  118528,
  118573,
  118576,
  118598,
  118608,
  118723,
  118784,
  119029,
  119040,
  119078,
  119081,
  119274,
  119296,
  119365,
  119488,
  119507,
  119520,
  119539,
  119552,
  119638,
  119648,
  119672,
  119808,
  119892,
  119894,
  119964,
  119966,
  119967,
  119970,
  119970,
  119973,
  119974,
  119977,
  119980,
  119982,
  119993,
  119995,
  119995,
  119997,
  120003,
  120005,
  120069,
  120071,
  120074,
  120077,
  120084,
  120086,
  120092,
  120094,
  120121,
  120123,
  120126,
  120128,
  120132,
  120134,
  120134,
  120138,
  120144,
  120146,
  120485,
  120488,
  120779,
  120782,
  121483,
  121499,
  121503,
  121505,
  121519,
  122624,
  122654,
  122661,
  122666,
  122880,
  122886,
  122888,
  122904,
  122907,
  122913,
  122915,
  122916,
  122918,
  122922,
  122928,
  122989,
  123023,
  123023,
  123136,
  123180,
  123184,
  123197,
  123200,
  123209,
  123214,
  123215,
  123536,
  123566,
  123584,
  123641,
  123647,
  123647,
  124112,
  124153,
  124896,
  124902,
  124904,
  124907,
  124909,
  124910,
  124912,
  124926,
  124928,
  125124,
  125127,
  125142,
  125184,
  125259,
  125264,
  125273,
  125278,
  125279,
  126065,
  126132,
  126209,
  126269,
  126464,
  126467,
  126469,
  126495,
  126497,
  126498,
  126500,
  126500,
  126503,
  126503,
  126505,
  126514,
  126516,
  126519,
  126521,
  126521,
  126523,
  126523,
  126530,
  126530,
  126535,
  126535,
  126537,
  126537,
  126539,
  126539,
  126541,
  126543,
  126545,
  126546,
  126548,
  126548,
  126551,
  126551,
  126553,
  126553,
  126555,
  126555,
  126557,
  126557,
  126559,
  126559,
  126561,
  126562,
  126564,
  126564,
  126567,
  126570,
  126572,
  126578,
  126580,
  126583,
  126585,
  126588,
  126590,
  126590,
  126592,
  126601,
  126603,
  126619,
  126625,
  126627,
  126629,
  126633,
  126635,
  126651,
  126704,
  126705,
  126976,
  127019,
  127024,
  127123,
  127136,
  127150,
  127153,
  127167,
  127169,
  127183,
  127185,
  127221,
  127232,
  127405,
  127462,
  127490,
  127504,
  127547,
  127552,
  127560,
  127568,
  127569,
  127584,
  127589,
  127744,
  128727,
  128732,
  128748,
  128752,
  128764,
  128768,
  128886,
  128891,
  128985,
  128992,
  129003,
  129008,
  129008,
  129024,
  129035,
  129040,
  129095,
  129104,
  129113,
  129120,
  129159,
  129168,
  129197,
  129200,
  129201,
  129280,
  129619,
  129632,
  129645,
  129648,
  129660,
  129664,
  129672,
  129680,
  129725,
  129727,
  129733,
  129742,
  129755,
  129760,
  129768,
  129776,
  129784,
  129792,
  129938,
  129940,
  129994,
  130032,
  130041,
  131072,
  173791,
  173824,
  177977,
  177984,
  178205,
  178208,
  183969,
  183984,
  191456,
  194560,
  195101,
  196608,
  201546,
  201552,
  205743,
  917505,
  917505,
  917536,
  917631,
  917760,
  917999
];

// src/typespec/core/packages/compiler/dist/src/core/charcode.js
function utf16CodeUnits(codePoint) {
  return codePoint >= 65536 ? 2 : 1;
}
function isHighSurrogate(ch) {
  return ch >= 55296 && ch <= 56319;
}
function isLowSurrogate(ch) {
  return ch >= 56320 && ch <= 57343;
}
function isLineBreak(ch) {
  return ch === 10 || ch === 13;
}
function isAsciiWhiteSpaceSingleLine(ch) {
  return ch === 32 || ch === 9 || ch === 11 || ch === 12;
}
function isNonAsciiWhiteSpaceSingleLine(ch) {
  return ch === 133 || // not considered a line break
  ch === 8206 || ch === 8207 || ch === 8232 || ch === 8233;
}
function isWhiteSpace(ch) {
  return isWhiteSpaceSingleLine(ch) || isLineBreak(ch);
}
function isWhiteSpaceSingleLine(ch) {
  return isAsciiWhiteSpaceSingleLine(ch) || ch > 127 && isNonAsciiWhiteSpaceSingleLine(ch);
}
function trim(str) {
  let start = 0;
  let end = str.length - 1;
  if (!isWhiteSpace(str.charCodeAt(start)) && !isWhiteSpace(str.charCodeAt(end))) {
    return str;
  }
  while (isWhiteSpace(str.charCodeAt(start))) {
    start++;
  }
  while (isWhiteSpace(str.charCodeAt(end))) {
    end--;
  }
  return str.substring(start, end + 1);
}
function isDigit(ch) {
  return ch >= 48 && ch <= 57;
}
function isHexDigit(ch) {
  return isDigit(ch) || ch >= 65 && ch <= 70 || ch >= 97 && ch <= 102;
}
function isBinaryDigit(ch) {
  return ch === 48 || ch === 49;
}
function isLowercaseAsciiLetter(ch) {
  return ch >= 97 && ch <= 122;
}
function isAsciiIdentifierStart(ch) {
  return ch >= 65 && ch <= 90 || ch >= 97 && ch <= 122 || ch === 36 || ch === 95;
}
function isAsciiIdentifierContinue(ch) {
  return ch >= 65 && ch <= 90 || ch >= 97 && ch <= 122 || ch >= 48 && ch <= 57 || ch === 36 || ch === 95;
}
function isIdentifierStart(codePoint) {
  return isAsciiIdentifierStart(codePoint) || codePoint > 127 && isNonAsciiIdentifierCharacter(codePoint);
}
function isIdentifierContinue(codePoint) {
  return isAsciiIdentifierContinue(codePoint) || codePoint > 127 && isNonAsciiIdentifierCharacter(codePoint);
}
function isNonAsciiIdentifierCharacter(codePoint) {
  return lookupInNonAsciiMap(codePoint, nonAsciiIdentifierMap);
}
function codePointBefore(text, pos) {
  if (pos <= 0 || pos > text.length) {
    return { char: void 0, size: 0 };
  }
  const ch = text.charCodeAt(pos - 1);
  if (!isLowSurrogate(ch) || !isHighSurrogate(text.charCodeAt(pos - 2))) {
    return { char: ch, size: 1 };
  }
  return { char: text.codePointAt(pos - 2), size: 2 };
}
function lookupInNonAsciiMap(codePoint, map) {
  let lo = 0;
  let hi = map.length;
  let mid;
  while (lo + 1 < hi) {
    mid = lo + (hi - lo) / 2;
    mid -= mid % 2;
    if (map[mid] <= codePoint && codePoint <= map[mid + 1]) {
      return true;
    }
    if (codePoint < map[mid]) {
      hi = mid;
    } else {
      lo = mid + 2;
    }
  }
  return false;
}

// src/typespec/core/packages/compiler/dist/src/core/parser-utils.js
function getCommentAtPosition(script, pos) {
  if (!script.parseOptions.comments) {
    throw new Error("ParseOptions.comments must be enabled to use getCommentAtPosition.");
  }
  let low = 0;
  let high = script.comments.length - 1;
  while (low <= high) {
    const middle = low + (high - low >> 1);
    const candidate = script.comments[middle];
    if (pos >= candidate.end) {
      low = middle + 1;
    } else if (pos < candidate.pos) {
      high = middle - 1;
    } else {
      return candidate;
    }
  }
  return void 0;
}
function getPositionBeforeTrivia(script, pos) {
  if (!script.parseOptions.comments) {
    throw new Error("ParseOptions.comments must be enabled to use getPositionBeforeTrivia.");
  }
  let comment;
  while (pos > 0) {
    if (isWhiteSpace(script.file.text.charCodeAt(pos - 1))) {
      do {
        pos--;
      } while (isWhiteSpace(script.file.text.charCodeAt(pos - 1)));
    } else if (comment = getCommentAtPosition(script, pos - 1)) {
      pos = comment.pos;
    } else {
      break;
    }
  }
  return pos;
}

// src/typespec/core/packages/compiler/dist/src/core/compiler-code-fixes/triple-quote-indent.codefix.js
function createTripleQuoteIndentCodeFix(location) {
  return defineCodeFix({
    id: "triple-quote-indent",
    label: "Format triple-quote-indent",
    fix: (context) => {
      const splitStr = "\n";
      const tripleQuote = '"""';
      const tripleQuoteLen = tripleQuote.length;
      const text = location.file.text.slice(location.pos + tripleQuoteLen, location.end - tripleQuoteLen);
      const lines = splitLines(text);
      if (lines.length === 0) {
        return;
      }
      if (lines.length === 1) {
        const indentNumb = getIndentNumbInLine(lines[0]);
        const prefix2 = " ".repeat(indentNumb);
        return context.replaceText(location, [tripleQuote, lines[0], `${prefix2}${tripleQuote}`].join(splitStr));
      }
      if (lines[0].trim() === "") {
        lines.shift();
      }
      const lastLine = lines[lines.length - 1];
      if (lastLine.trim() === "") {
        lines.pop();
      }
      let prefix = "";
      const minIndentNumb = Math.min(...lines.map((line) => getIndentNumbInLine(line)));
      const lastLineIndentNumb = getIndentNumbInLine(lastLine);
      if (minIndentNumb < lastLineIndentNumb) {
        const indentDiff = lastLineIndentNumb - minIndentNumb;
        prefix = " ".repeat(indentDiff);
      }
      const middle = lines.map((line) => `${prefix}${line}`).join(splitStr);
      return context.replaceText(location, `${tripleQuote}${splitStr}${middle}${splitStr}${" ".repeat(lastLineIndentNumb)}${tripleQuote}`);
      function getIndentNumbInLine(lineText) {
        let curStart = 0;
        while (curStart < lineText.length && isWhiteSpaceSingleLine(lineText.charCodeAt(curStart))) {
          curStart++;
        }
        return curStart;
      }
    }
  });
}

// src/typespec/core/packages/compiler/dist/src/core/diagnostic-creator.js
function createDiagnosticCreator(diagnostics2, libraryName) {
  const errorMessage = libraryName ? `It must match one of the code defined in the library '${libraryName}'` : "It must match one of the code defined in the compiler.";
  function createDiagnostic2(diagnostic) {
    const diagnosticDef = diagnostics2[diagnostic.code];
    if (!diagnosticDef) {
      const codeStr = Object.keys(diagnostics2).map((x) => ` - ${x}`).join("\n");
      const code = String(diagnostic.code);
      throw new Error(`Unexpected diagnostic code '${code}'. ${errorMessage}. Defined codes:
${codeStr}`);
    }
    const message = diagnosticDef.messages[diagnostic.messageId ?? "default"];
    if (!message) {
      const codeStr = Object.keys(diagnosticDef.messages).map((x) => ` - ${x}`).join("\n");
      const messageId = String(diagnostic.messageId);
      const code = String(diagnostic.code);
      throw new Error(`Unexpected message id '${messageId}'. ${errorMessage} for code '${code}'. Defined codes:
${codeStr}`);
    }
    const messageStr = typeof message === "string" ? message : message(diagnostic.format);
    const result = {
      code: libraryName ? `${libraryName}/${String(diagnostic.code)}` : diagnostic.code.toString(),
      severity: diagnosticDef.severity,
      message: messageStr,
      target: diagnostic.target
    };
    if (diagnosticDef.url) {
      mutate(result).url = diagnosticDef.url;
    }
    if (diagnostic.codefixes) {
      mutate(result).codefixes = diagnostic.codefixes;
    }
    return result;
  }
  function reportDiagnostic2(program, diagnostic) {
    const diag = createDiagnostic2(diagnostic);
    program.reportDiagnostic(diag);
  }
  return {
    diagnostics: diagnostics2,
    createDiagnostic: createDiagnostic2,
    reportDiagnostic: reportDiagnostic2
  };
}

// src/typespec/core/packages/compiler/dist/src/core/messages.js
var diagnostics = {
  /**
   * Scanner errors.
   */
  "digit-expected": {
    severity: "error",
    messages: {
      default: "Digit expected."
    }
  },
  "hex-digit-expected": {
    severity: "error",
    messages: {
      default: "Hexadecimal digit expected."
    }
  },
  "binary-digit-expected": {
    severity: "error",
    messages: {
      default: "Binary digit expected."
    }
  },
  unterminated: {
    severity: "error",
    messages: {
      default: paramMessage`Unterminated ${"token"}.`
    }
  },
  "creating-file": {
    severity: "error",
    messages: {
      default: paramMessage`Error creating single file: ${"filename"},  ${"error"}`
    }
  },
  "invalid-escape-sequence": {
    severity: "error",
    messages: {
      default: "Invalid escape sequence."
    }
  },
  "no-new-line-start-triple-quote": {
    severity: "error",
    messages: {
      default: "String content in triple quotes must begin on a new line."
    }
  },
  "no-new-line-end-triple-quote": {
    severity: "error",
    messages: {
      default: "Closing triple quotes must begin on a new line."
    }
  },
  "triple-quote-indent": {
    severity: "error",
    description: "Report when a triple-quoted string has lines with less indentation as the closing triple quotes.",
    url: "https://typespec.io/docs/standard-library/diags/triple-quote-indent",
    messages: {
      default: "All lines in triple-quoted string lines must have the same indentation as closing triple quotes."
    }
  },
  "invalid-character": {
    severity: "error",
    messages: {
      default: "Invalid character."
    }
  },
  /**
   * Utils
   */
  "file-not-found": {
    severity: "error",
    messages: {
      default: paramMessage`File ${"path"} not found.`
    }
  },
  "file-load": {
    severity: "error",
    messages: {
      default: paramMessage`${"message"}`
    }
  },
  /**
   * Init templates
   */
  "init-template-invalid-json": {
    severity: "error",
    messages: {
      default: paramMessage`Unable to parse ${"url"}: ${"message"}. Check that the template URL is correct.`
    }
  },
  "init-template-download-failed": {
    severity: "error",
    messages: {
      default: paramMessage`Failed to download template from ${"url"}: ${"message"}. Check that the template URL is correct.`
    }
  },
  /**
   * Parser errors.
   */
  "multiple-blockless-namespace": {
    severity: "error",
    messages: {
      default: "Cannot use multiple blockless namespaces."
    }
  },
  "blockless-namespace-first": {
    severity: "error",
    messages: {
      default: "Blockless namespaces can't follow other declarations.",
      topLevel: "Blockless namespace can only be top-level."
    }
  },
  "import-first": {
    severity: "error",
    messages: {
      default: "Imports must come prior to namespaces or other declarations.",
      topLevel: "Imports must be top-level and come prior to namespaces or other declarations."
    }
  },
  "token-expected": {
    severity: "error",
    messages: {
      default: paramMessage`${"token"} expected.`,
      unexpected: paramMessage`Unexpected token ${"token"}`,
      numericOrStringLiteral: "Expected numeric or string literal.",
      identifier: "Identifier expected.",
      expression: "Expression expected.",
      statement: "Statement expected.",
      property: "Property expected.",
      enumMember: "Enum member expected.",
      typeofTarget: "Typeof expects a value literal or value reference."
    }
  },
  "unknown-directive": {
    severity: "error",
    messages: {
      default: paramMessage`Unknown directive '#${"id"}'`
    }
  },
  "augment-decorator-target": {
    severity: "error",
    messages: {
      default: `Augment decorator first argument must be a type reference.`,
      noInstance: `Cannot reference template instances.`,
      noModelExpression: `Cannot augment model expressions.`,
      noUnionExpression: `Cannot augment union expressions.`
    }
  },
  "duplicate-decorator": {
    severity: "warning",
    messages: {
      default: paramMessage`Decorator ${"decoratorName"} cannot be used twice on the same declaration.`
    }
  },
  "decorator-conflict": {
    severity: "warning",
    messages: {
      default: paramMessage`Decorator ${"decoratorName"} cannot be used with decorator ${"otherDecoratorName"} on the same declaration.`
    }
  },
  "reserved-identifier": {
    severity: "error",
    messages: {
      default: "Keyword cannot be used as identifier.",
      future: paramMessage`${"name"} is a reserved keyword`
    }
  },
  "invalid-directive-location": {
    severity: "error",
    messages: {
      default: paramMessage`Cannot place directive on ${"nodeName"}.`
    }
  },
  "invalid-decorator-location": {
    severity: "error",
    messages: {
      default: paramMessage`Cannot decorate ${"nodeName"}.`
    }
  },
  "default-required": {
    severity: "error",
    messages: {
      default: "Required template parameters must not follow optional template parameters"
    }
  },
  "invalid-template-argument-name": {
    severity: "error",
    messages: {
      default: "Template parameter argument names must be valid, bare identifiers."
    }
  },
  "invalid-template-default": {
    severity: "error",
    messages: {
      default: "Template parameter defaults can only reference previously declared type parameters."
    }
  },
  "required-parameter-first": {
    severity: "error",
    messages: {
      default: "A required parameter cannot follow an optional parameter."
    }
  },
  "rest-parameter-last": {
    severity: "error",
    messages: {
      default: "A rest parameter must be last in a parameter list."
    }
  },
  "rest-parameter-required": {
    severity: "error",
    messages: {
      default: "A rest parameter cannot be optional."
    }
  },
  /**
   * Parser doc comment warnings.
   * Design goal: Malformed doc comments should only produce warnings, not errors.
   */
  "doc-invalid-identifier": {
    severity: "warning",
    messages: {
      default: "Invalid identifier.",
      tag: "Invalid tag name. Use backticks around code if this was not meant to be a tag.",
      param: "Invalid parameter name.",
      prop: "Invalid property name.",
      templateParam: "Invalid template parameter name."
    }
  },
  /**
   * Checker
   */
  "using-invalid-ref": {
    severity: "error",
    messages: {
      default: "Using must refer to a namespace"
    }
  },
  "invalid-type-ref": {
    severity: "error",
    messages: {
      default: "Invalid type reference",
      decorator: "Can't put a decorator in a type",
      function: "Can't use a function as a type"
    }
  },
  "invalid-template-args": {
    severity: "error",
    messages: {
      default: "Invalid template arguments.",
      notTemplate: "Can't pass template arguments to non-templated type",
      tooMany: "Too many template arguments provided.",
      unknownName: paramMessage`No parameter named '${"name"}' exists in the target template.`,
      positionalAfterNamed: "Positional template arguments cannot follow named arguments in the same argument list.",
      missing: paramMessage`Template argument '${"name"}' is required and not specified.`,
      specifiedAgain: paramMessage`Cannot specify template argument '${"name"}' again.`
    }
  },
  "intersect-non-model": {
    severity: "error",
    messages: {
      default: "Cannot intersect non-model types (including union types)."
    }
  },
  "intersect-invalid-index": {
    severity: "error",
    messages: {
      default: "Cannot intersect incompatible models.",
      never: "Cannot intersect a model that cannot hold properties.",
      array: "Cannot intersect an array model."
    }
  },
  "incompatible-indexer": {
    severity: "error",
    messages: {
      default: paramMessage`Property is incompatible with indexer:\n${"message"}`
    }
  },
  "no-array-properties": {
    severity: "error",
    messages: {
      default: "Array models cannot have any properties."
    }
  },
  "intersect-duplicate-property": {
    severity: "error",
    messages: {
      default: paramMessage`Intersection contains duplicate property definitions for ${"propName"}`
    }
  },
  "invalid-decorator": {
    severity: "error",
    messages: {
      default: paramMessage`${"id"} is not a decorator`
    }
  },
  "invalid-ref": {
    severity: "error",
    messages: {
      default: paramMessage`Cannot resolve ${"id"}`,
      identifier: paramMessage`Unknown identifier ${"id"}`,
      decorator: paramMessage`Unknown decorator @${"id"}`,
      inDecorator: paramMessage`Cannot resolve ${"id"} in decorator`,
      underNamespace: paramMessage`Namespace ${"namespace"} doesn't have member ${"id"}`,
      member: paramMessage`${"kind"} doesn't have member ${"id"}`,
      metaProperty: paramMessage`${"kind"} doesn't have meta property ${"id"}`,
      node: paramMessage`Cannot resolve '${"id"}' in node ${"nodeName"} since it has no members. Did you mean to use "::" instead of "."?`
    }
  },
  "duplicate-property": {
    severity: "error",
    messages: {
      default: paramMessage`Model already has a property named ${"propName"}`
    }
  },
  "override-property-mismatch": {
    severity: "error",
    messages: {
      default: paramMessage`Model has an inherited property named ${"propName"} of type ${"propType"} which cannot override type ${"parentType"}`,
      disallowedOptionalOverride: paramMessage`Model has a required inherited property named ${"propName"} which cannot be overridden as optional`
    }
  },
  "extend-scalar": {
    severity: "error",
    messages: {
      default: "Scalar must extend other scalars."
    }
  },
  "extend-model": {
    severity: "error",
    messages: {
      default: "Models must extend other models.",
      modelExpression: "Models cannot extend model expressions."
    }
  },
  "is-model": {
    severity: "error",
    messages: {
      default: "Model `is` must specify another model.",
      modelExpression: "Model `is` cannot specify a model expression."
    }
  },
  "is-operation": {
    severity: "error",
    messages: {
      default: "Operation can only reuse the signature of another operation."
    }
  },
  "spread-model": {
    severity: "error",
    messages: {
      default: "Cannot spread properties of non-model type.",
      neverIndex: "Cannot spread type because it cannot hold properties.",
      selfSpread: "Cannot spread type within its own declaration."
    }
  },
  "unsupported-default": {
    severity: "error",
    messages: {
      default: paramMessage`Default must be have a value type but has type '${"type"}'.`
    }
  },
  "spread-object": {
    severity: "error",
    messages: {
      default: "Cannot spread properties of non-object type."
    }
  },
  "expect-value": {
    severity: "error",
    messages: {
      default: paramMessage`${"name"} refers to a type, but is being used as a value here.`,
      model: paramMessage`${"name"} refers to a model type, but is being used as a value here. Use #{} to create an object value.`,
      modelExpression: `Is a model expression type, but is being used as a value here. Use #{} to create an object value.`,
      tuple: `Is a tuple type, but is being used as a value here. Use #[] to create an array value.`,
      templateConstraint: paramMessage`${"name"} template parameter can be a type but is being used as a value here.`
    }
  },
  "non-callable": {
    severity: "error",
    messages: {
      default: paramMessage`Type ${"type"} is not is not callable.`
    }
  },
  "named-init-required": {
    severity: "error",
    messages: {
      default: paramMessage`Only scalar deriving from 'string', 'numeric' or 'boolean' can be instantited without a named constructor.`
    }
  },
  "invalid-primitive-init": {
    severity: "error",
    messages: {
      default: `Instantiating scalar deriving from 'string', 'numeric' or 'boolean' can only take a single argument.`,
      invalidArg: paramMessage`Expected a single argument of type ${"expected"} but got ${"actual"}.`
    }
  },
  "ambiguous-scalar-type": {
    severity: "error",
    messages: {
      default: paramMessage`Value ${"value"} type is ambiguous between ${"types"}. To resolve be explicit when instantiating this value(e.g. '${"example"}(${"value"})').`
    }
  },
  unassignable: {
    severity: "error",
    messages: {
      default: paramMessage`Type '${"sourceType"}' is not assignable to type '${"targetType"}'`
    }
  },
  "property-unassignable": {
    severity: "error",
    messages: {
      default: paramMessage`Types of property '${"propName"}' are incompatible`
    }
  },
  "property-required": {
    severity: "error",
    messages: {
      default: paramMessage`Property '${"propName"}' is required in type '${"targetType"}' but here is optional.`
    }
  },
  "value-in-type": {
    severity: "error",
    messages: {
      default: "A value cannot be used as a type.",
      referenceTemplate: "Template parameter can be passed values but is used as a type.",
      noTemplateConstraint: "Template parameter has no constraint but a value is passed. Add `extends valueof unknown` to accept any value."
    }
  },
  "no-prop": {
    severity: "error",
    messages: {
      default: paramMessage`Property '${"propName"}' cannot be defined because model cannot hold properties.`
    }
  },
  "missing-index": {
    severity: "error",
    messages: {
      default: paramMessage`Index signature for type '${"indexType"}' is missing in type '${"sourceType"}'.`
    }
  },
  "missing-property": {
    severity: "error",
    messages: {
      default: paramMessage`Property '${"propertyName"}' is missing on type '${"sourceType"}' but required in '${"targetType"}'`
    }
  },
  "unexpected-property": {
    severity: "error",
    messages: {
      default: paramMessage`Object value may only specify known properties, and '${"propertyName"}' does not exist in type '${"type"}'.`
    }
  },
  "extends-interface": {
    severity: "error",
    messages: {
      default: "Interfaces can only extend other interfaces"
    }
  },
  "extends-interface-duplicate": {
    severity: "error",
    messages: {
      default: paramMessage`Interface extends cannot have duplicate members. The duplicate member is named ${"name"}`
    }
  },
  "interface-duplicate": {
    severity: "error",
    messages: {
      default: paramMessage`Interface already has a member named ${"name"}`
    }
  },
  "union-duplicate": {
    severity: "error",
    messages: {
      default: paramMessage`Union already has a variant named ${"name"}`
    }
  },
  "enum-member-duplicate": {
    severity: "error",
    messages: {
      default: paramMessage`Enum already has a member named ${"name"}`
    }
  },
  "constructor-duplicate": {
    severity: "error",
    messages: {
      default: paramMessage`A constructor already exists with name ${"name"}`
    }
  },
  "spread-enum": {
    severity: "error",
    messages: {
      default: "Cannot spread members of non-enum type."
    }
  },
  "decorator-fail": {
    severity: "error",
    messages: {
      default: paramMessage`Decorator ${"decoratorName"} failed!\n\n${"error"}`
    }
  },
  "rest-parameter-array": {
    severity: "error",
    messages: {
      default: "A rest parameter must be of an array type."
    }
  },
  "decorator-extern": {
    severity: "error",
    messages: {
      default: "A decorator declaration must be prefixed with the 'extern' modifier."
    }
  },
  "function-extern": {
    severity: "error",
    messages: {
      default: "A function declaration must be prefixed with the 'extern' modifier."
    }
  },
  "function-unsupported": {
    severity: "error",
    messages: {
      default: "Function are currently not supported."
    }
  },
  "missing-implementation": {
    severity: "error",
    messages: {
      default: "Extern declaration must have an implementation in JS file."
    }
  },
  "overload-same-parent": {
    severity: "error",
    messages: {
      default: `Overload must be in the same interface or namespace.`
    }
  },
  shadow: {
    severity: "warning",
    messages: {
      default: paramMessage`Shadowing parent template parameter with the same name "${"name"}"`
    }
  },
  "invalid-deprecation-argument": {
    severity: "error",
    messages: {
      default: paramMessage`#deprecation directive is expecting a string literal as the message but got a "${"kind"}"`,
      missing: "#deprecation directive is expecting a message argument but none was provided."
    }
  },
  "duplicate-deprecation": {
    severity: "warning",
    messages: {
      default: "The #deprecated directive cannot be used more than once on the same declaration."
    }
  },
  /**
   * Configuration
   */
  "config-invalid-argument": {
    severity: "error",
    messages: {
      default: paramMessage`Argument "${"name"}" is not defined as a parameter in the config.`
    }
  },
  "config-circular-variable": {
    severity: "error",
    messages: {
      default: paramMessage`There is a circular reference to variable "${"name"}" in the cli configuration or arguments.`
    }
  },
  "config-path-absolute": {
    severity: "error",
    messages: {
      default: paramMessage`Path "${"path"}" cannot be relative. Use {cwd} or {project-root} to specify what the path should be relative to.`
    }
  },
  "config-invalid-name": {
    severity: "error",
    messages: {
      default: paramMessage`The configuration name "${"name"}" is invalid because it contains a dot ("."). Using a dot will conflict with using nested configuration values.`
    }
  },
  "path-unix-style": {
    severity: "warning",
    messages: {
      default: paramMessage`Path should use unix style separators. Use "/" instead of "\\".`
    }
  },
  "config-path-not-found": {
    severity: "error",
    messages: {
      default: paramMessage`No configuration file found at config path "${"path"}".`
    }
  },
  /**
   * Program
   */
  "dynamic-import": {
    severity: "error",
    messages: {
      default: "Dynamically generated TypeSpec cannot have imports"
    }
  },
  "invalid-import": {
    severity: "error",
    messages: {
      default: "Import paths must reference either a directory, a .tsp file, or .js file"
    }
  },
  "invalid-main": {
    severity: "error",
    messages: {
      default: "Main file must either be a .tsp file or a .js file."
    }
  },
  "import-not-found": {
    severity: "error",
    messages: {
      default: paramMessage`Couldn't resolve import "${"path"}"`
    }
  },
  "library-invalid": {
    severity: "error",
    messages: {
      default: paramMessage`Library "${"path"}" is invalid: ${"message"}`
    }
  },
  "incompatible-library": {
    severity: "warning",
    messages: {
      default: paramMessage`Multiple versions of "${"name"}" library were loaded:\n${"versionMap"}`
    }
  },
  "compiler-version-mismatch": {
    severity: "warning",
    messages: {
      default: paramMessage`Current TypeSpec compiler conflicts with local version of @typespec/compiler referenced in ${"basedir"}. \nIf this warning occurs on the command line, try running \`typespec\` with a working directory of ${"basedir"}. \nIf this warning occurs in the IDE, try configuring the \`tsp-server\` path to ${"betterTypeSpecServerPath"}.\n  Expected: ${"expected"}\n  Resolved: ${"actual"}`
    }
  },
  "duplicate-symbol": {
    severity: "error",
    messages: {
      default: paramMessage`Duplicate name: "${"name"}"`
    }
  },
  "decorator-decl-target": {
    severity: "error",
    messages: {
      default: "dec must have at least one parameter.",
      required: "dec first parameter must be required."
    }
  },
  "mixed-string-template": {
    severity: "error",
    messages: {
      default: "String template is interpolating values and types. It must be either all values to produce a string value or or all types for string template type."
    }
  },
  "non-literal-string-template": {
    severity: "error",
    messages: {
      default: "Value interpolated in this string template cannot be converted to a string. Only literal types can be automatically interpolated."
    }
  },
  /**
   * Binder
   */
  "ambiguous-symbol": {
    severity: "error",
    messages: {
      default: paramMessage`"${"name"}" is an ambiguous name between ${"duplicateNames"}. Try using fully qualified name instead: ${"duplicateNames"}`
    }
  },
  "duplicate-using": {
    severity: "error",
    messages: {
      default: paramMessage`duplicate using of "${"usingName"}" namespace`
    }
  },
  /**
   * Library
   */
  "on-validate-fail": {
    severity: "error",
    messages: {
      default: paramMessage`onValidate failed with errors. ${"error"}`
    }
  },
  "invalid-emitter": {
    severity: "error",
    messages: {
      default: paramMessage`Requested emitter package ${"emitterPackage"} does not provide an "$onEmit" function.`
    }
  },
  "js-error": {
    severity: "error",
    messages: {
      default: paramMessage`Failed to load ${"specifier"} due to the following JS error: ${"error"}`
    }
  },
  "missing-import": {
    severity: "error",
    messages: {
      default: paramMessage`Emitter '${"emitterName"}' requires '${"requiredImport"}' to be imported. Add 'import "${"requiredImport"}".`
    }
  },
  /**
   * Linter
   */
  "invalid-rule-ref": {
    severity: "error",
    messages: {
      default: paramMessage`Reference "${"ref"}" is not a valid reference to a rule or ruleset. It must be in the following format: "<library-name>:<rule-name>"`
    }
  },
  "unknown-rule": {
    severity: "error",
    messages: {
      default: paramMessage`Rule "${"ruleName"}" is not found in library "${"libraryName"}"`
    }
  },
  "unknown-rule-set": {
    severity: "error",
    messages: {
      default: paramMessage`Rule set "${"ruleSetName"}" is not found in library "${"libraryName"}"`
    }
  },
  "rule-enabled-disabled": {
    severity: "error",
    messages: {
      default: paramMessage`Rule "${"ruleName"}" has been enabled and disabled in the same ruleset.`
    }
  },
  /**
   * Formatter
   */
  "format-failed": {
    severity: "error",
    messages: {
      default: paramMessage`File '${"file"}' failed to format. ${"details"}`
    }
  },
  /**
   * Decorator
   */
  "invalid-pattern-regex": {
    severity: "warning",
    messages: {
      default: "@pattern decorator expects a valid regular expression pattern."
    }
  },
  "decorator-wrong-target": {
    severity: "error",
    messages: {
      default: paramMessage`Cannot apply ${"decorator"} decorator to ${"to"}`,
      withExpected: paramMessage`Cannot apply ${"decorator"} decorator to ${"to"} since it is not assignable to ${"expected"}`
    }
  },
  "invalid-argument": {
    severity: "error",
    messages: {
      default: paramMessage`Argument of type '${"value"}' is not assignable to parameter of type '${"expected"}'`
    }
  },
  "invalid-argument-count": {
    severity: "error",
    messages: {
      default: paramMessage`Expected ${"expected"} arguments, but got ${"actual"}.`,
      atLeast: paramMessage`Expected at least ${"expected"} arguments, but got ${"actual"}.`
    }
  },
  "known-values-invalid-enum": {
    severity: "error",
    messages: {
      default: paramMessage`Enum cannot be used on this type. Member ${"member"} is not assignable to type ${"type"}.`
    }
  },
  "invalid-value": {
    severity: "error",
    messages: {
      default: paramMessage`Type '${"kind"}' is not a value type.`,
      atPath: paramMessage`Type '${"kind"}' of '${"path"}' is not a value type.`
    }
  },
  deprecated: {
    severity: "warning",
    messages: {
      default: paramMessage`Deprecated: ${"message"}`
    }
  },
  "no-optional-key": {
    severity: "error",
    messages: {
      default: paramMessage`Property '${"propertyName"}' marked as key cannot be optional.`
    }
  },
  "invalid-discriminated-union": {
    severity: "error",
    messages: {
      default: "",
      noAnonVariants: "Unions with anonymous variants cannot be discriminated"
    }
  },
  "invalid-discriminated-union-variant": {
    severity: "error",
    messages: {
      default: paramMessage`Union variant "${"name"}" must be a model type.`,
      noEnvelopeModel: paramMessage`Union variant "${"name"}" must be a model type when the union has envelope: none.`,
      discriminantMismatch: paramMessage`Variant "${"name"}" explicitly defines the discriminator property "${"discriminant"}" but the value "${"propertyValue"}" do not match the variant name "${"variantName"}".`,
      duplicateDefaultVariant: `Discriminated union only allow a single default variant(Without a variant name).`,
      noDiscriminant: paramMessage`Variant "${"name"}" type is missing the discriminant property "${"discriminant"}".`,
      wrongDiscriminantType: paramMessage`Variant "${"name"}" type's discriminant property "${"discriminant"}" must be a string literal or string enum member.`
    }
  },
  "missing-discriminator-property": {
    severity: "error",
    messages: {
      default: paramMessage`Each derived model of a discriminated model type should have set the discriminator property("${"discriminator"}") or have a derived model which has. Add \`${"discriminator"}: "<discriminator-value>"\``
    }
  },
  "invalid-discriminator-value": {
    severity: "error",
    messages: {
      default: paramMessage`Discriminator value should be a string, union of string or string enum but was ${"kind"}.`,
      required: "The discriminator property must be a required property.",
      duplicate: paramMessage`Discriminator value "${"discriminator"}" is already used in another variant.`
    }
  },
  "invalid-encode": {
    severity: "error",
    messages: {
      default: "Invalid encoding",
      wrongType: paramMessage`Encoding '${"encoding"}' cannot be used on type '${"type"}'. Expected: ${"expected"}.`,
      wrongEncodingType: paramMessage`Encoding '${"encoding"}' on type '${"type"}' is expected to be serialized as '${"expected"}' but got '${"actual"}'.`,
      wrongNumericEncodingType: paramMessage`Encoding '${"encoding"}' on type '${"type"}' is expected to be serialized as '${"expected"}' but got '${"actual"}'. Set '@encode' 2nd parameter to be of type ${"expected"}. e.g. '@encode("${"encoding"}", int32)'`,
      firstArg: `First argument of "@encode" must be the encoding name or the string type when encoding numeric types.`
    }
  },
  "invalid-mime-type": {
    severity: "error",
    messages: {
      default: paramMessage`Invalid mime type '${"mimeType"}'`
    }
  },
  "no-mime-type-suffix": {
    severity: "error",
    messages: {
      default: paramMessage`Cannot use mime type '${"mimeType"}' with suffix '${"suffix"}'. Use a simple mime \`type/subtype\` instead.`
    }
  },
  "encoded-name-conflict": {
    severity: "error",
    messages: {
      default: paramMessage`Encoded name '${"name"}' conflicts with existing member name for mime type '${"mimeType"}'`,
      duplicate: paramMessage`Same encoded name '${"name"}' is used for 2 members '${"mimeType"}'`
    }
  },
  "incompatible-paging-props": {
    severity: "error",
    messages: {
      default: paramMessage`Paging property has multiple types: '${"kinds"}'`
    }
  },
  "invalid-paging-prop": {
    severity: "error",
    messages: {
      default: paramMessage`Paging property '${"kind"}' is not valid in this context.`,
      input: paramMessage`Paging property '${"kind"}' cannot be used in the parameters of an operation.`,
      output: paramMessage`Paging property '${"kind"}' cannot be used in the return type of an operation.`
    }
  },
  "duplicate-paging-prop": {
    severity: "error",
    messages: {
      default: paramMessage`Duplicate property paging '${"kind"}' for operation ${"operationName"}.`
    }
  },
  "missing-paging-items": {
    severity: "error",
    messages: {
      default: paramMessage`Paged operation '${"operationName"}' return type must have a property annotated with @pageItems.`
    }
  },
  /**
   * Service
   */
  "service-decorator-duplicate": {
    severity: "error",
    messages: {
      default: `@service can only be set once per TypeSpec document.`
    }
  },
  "list-type-not-model": {
    severity: "error",
    messages: {
      default: "@list decorator's parameter must be a model type."
    }
  },
  "invalid-range": {
    severity: "error",
    messages: {
      default: paramMessage`Range "${"start"}..${"end"}" is invalid.`
    }
  },
  /**
   * Mutator
   */
  "add-response": {
    severity: "error",
    messages: {
      default: "Cannot add a response to anything except an operation statement."
    }
  },
  "add-parameter": {
    severity: "error",
    messages: {
      default: "Cannot add a parameter to anything except an operation statement."
    }
  },
  "add-model-property": {
    severity: "error",
    messages: {
      default: "Cannot add a model property to anything except a model statement."
    }
  },
  "add-model-property-fail": {
    severity: "error",
    messages: {
      default: paramMessage`Could not add property/parameter "${"propertyName"}" of type "${"propertyTypeName"}"`
    }
  },
  "add-response-type": {
    severity: "error",
    messages: {
      default: paramMessage`Could not add response type "${"responseTypeName"}" to operation ${"operationName"}"`
    }
  },
  "circular-base-type": {
    severity: "error",
    messages: {
      default: paramMessage`Type '${"typeName"}' recursively references itself as a base type.`
    }
  },
  "circular-constraint": {
    severity: "error",
    messages: {
      default: paramMessage`Type parameter '${"typeName"}' has a circular constraint.`
    }
  },
  "circular-op-signature": {
    severity: "error",
    messages: {
      default: paramMessage`Operation '${"typeName"}' recursively references itself.`
    }
  },
  "circular-alias-type": {
    severity: "error",
    messages: {
      default: paramMessage`Alias type '${"typeName"}' recursively references itself.`
    }
  },
  "circular-const": {
    severity: "error",
    messages: {
      default: paramMessage`const '${"name"}' recursively references itself.`
    }
  },
  "circular-prop": {
    severity: "error",
    messages: {
      default: paramMessage`Property '${"propName"}' recursively references itself.`
    }
  },
  "conflict-marker": {
    severity: "error",
    messages: {
      default: "Conflict marker encountered."
    }
  },
  // #region Visibility
  "visibility-sealed": {
    severity: "error",
    messages: {
      default: paramMessage`Visibility of property '${"propName"}' is sealed and cannot be changed.`
    }
  },
  "default-visibility-not-member": {
    severity: "error",
    messages: {
      default: "The default visibility modifiers of a class must be members of the class enum."
    }
  },
  "operation-visibility-constraint-empty": {
    severity: "error",
    messages: {
      default: "Operation visibility constraints with no arguments are not allowed.",
      returnType: "Return type visibility constraints with no arguments are not allowed.",
      parameter: "Parameter visibility constraints with no arguments are not allowed. To disable effective PATCH optionality, use @patch(#{ implicitOptionality: false }) instead."
    }
  },
  // #endregion
  // #region CLI
  "no-compatible-vs-installed": {
    severity: "error",
    messages: {
      default: "No compatible version of Visual Studio found."
    }
  },
  "vs-extension-windows-only": {
    severity: "error",
    messages: {
      default: "Visual Studio extension is not supported on non-Windows."
    }
  },
  "vscode-in-path": {
    severity: "error",
    messages: {
      default: "Couldn't find VS Code 'code' command in PATH. Make sure you have the VS Code executable added to the system PATH.",
      osx: "Couldn't find VS Code 'code' command in PATH. Make sure you have the VS Code executable added to the system PATH.\nSee instruction for Mac OS here https://code.visualstudio.com/docs/setup/mac"
    }
  },
  "invalid-option-flag": {
    severity: "error",
    messages: {
      default: paramMessage`The --option parameter value "${"value"}" must be in the format: <emitterName>.some-options=value`
    }
  }
  // #endregion CLI
};
var { createDiagnostic, reportDiagnostic } = createDiagnosticCreator(diagnostics);

// src/typespec/core/packages/compiler/dist/src/core/scanner.js
var mergeConflictMarkerLength = 7;
var Token;
(function(Token2) {
  Token2[Token2["None"] = 0] = "None";
  Token2[Token2["Invalid"] = 1] = "Invalid";
  Token2[Token2["EndOfFile"] = 2] = "EndOfFile";
  Token2[Token2["Identifier"] = 3] = "Identifier";
  Token2[Token2["NumericLiteral"] = 4] = "NumericLiteral";
  Token2[Token2["StringLiteral"] = 5] = "StringLiteral";
  Token2[Token2["StringTemplateHead"] = 6] = "StringTemplateHead";
  Token2[Token2["StringTemplateMiddle"] = 7] = "StringTemplateMiddle";
  Token2[Token2["StringTemplateTail"] = 8] = "StringTemplateTail";
  Token2[Token2["__StartTrivia"] = 9] = "__StartTrivia";
  Token2[Token2["SingleLineComment"] = 9] = "SingleLineComment";
  Token2[Token2["MultiLineComment"] = 10] = "MultiLineComment";
  Token2[Token2["NewLine"] = 11] = "NewLine";
  Token2[Token2["Whitespace"] = 12] = "Whitespace";
  Token2[Token2["ConflictMarker"] = 13] = "ConflictMarker";
  Token2[Token2["__EndTrivia"] = 14] = "__EndTrivia";
  Token2[Token2["__StartDocComment"] = 14] = "__StartDocComment";
  Token2[Token2["DocText"] = 14] = "DocText";
  Token2[Token2["DocCodeSpan"] = 15] = "DocCodeSpan";
  Token2[Token2["DocCodeFenceDelimiter"] = 16] = "DocCodeFenceDelimiter";
  Token2[Token2["__EndDocComment"] = 17] = "__EndDocComment";
  Token2[Token2["__StartPunctuation"] = 17] = "__StartPunctuation";
  Token2[Token2["OpenBrace"] = 17] = "OpenBrace";
  Token2[Token2["CloseBrace"] = 18] = "CloseBrace";
  Token2[Token2["OpenParen"] = 19] = "OpenParen";
  Token2[Token2["CloseParen"] = 20] = "CloseParen";
  Token2[Token2["OpenBracket"] = 21] = "OpenBracket";
  Token2[Token2["CloseBracket"] = 22] = "CloseBracket";
  Token2[Token2["Dot"] = 23] = "Dot";
  Token2[Token2["Ellipsis"] = 24] = "Ellipsis";
  Token2[Token2["Semicolon"] = 25] = "Semicolon";
  Token2[Token2["Comma"] = 26] = "Comma";
  Token2[Token2["LessThan"] = 27] = "LessThan";
  Token2[Token2["GreaterThan"] = 28] = "GreaterThan";
  Token2[Token2["Equals"] = 29] = "Equals";
  Token2[Token2["Ampersand"] = 30] = "Ampersand";
  Token2[Token2["Bar"] = 31] = "Bar";
  Token2[Token2["Question"] = 32] = "Question";
  Token2[Token2["Colon"] = 33] = "Colon";
  Token2[Token2["ColonColon"] = 34] = "ColonColon";
  Token2[Token2["At"] = 35] = "At";
  Token2[Token2["AtAt"] = 36] = "AtAt";
  Token2[Token2["Hash"] = 37] = "Hash";
  Token2[Token2["HashBrace"] = 38] = "HashBrace";
  Token2[Token2["HashBracket"] = 39] = "HashBracket";
  Token2[Token2["Star"] = 40] = "Star";
  Token2[Token2["ForwardSlash"] = 41] = "ForwardSlash";
  Token2[Token2["Plus"] = 42] = "Plus";
  Token2[Token2["Hyphen"] = 43] = "Hyphen";
  Token2[Token2["Exclamation"] = 44] = "Exclamation";
  Token2[Token2["LessThanEquals"] = 45] = "LessThanEquals";
  Token2[Token2["GreaterThanEquals"] = 46] = "GreaterThanEquals";
  Token2[Token2["AmpsersandAmpersand"] = 47] = "AmpsersandAmpersand";
  Token2[Token2["BarBar"] = 48] = "BarBar";
  Token2[Token2["EqualsEquals"] = 49] = "EqualsEquals";
  Token2[Token2["ExclamationEquals"] = 50] = "ExclamationEquals";
  Token2[Token2["EqualsGreaterThan"] = 51] = "EqualsGreaterThan";
  Token2[Token2["__EndPunctuation"] = 52] = "__EndPunctuation";
  Token2[Token2["__StartKeyword"] = 52] = "__StartKeyword";
  Token2[Token2["__StartStatementKeyword"] = 52] = "__StartStatementKeyword";
  Token2[Token2["ImportKeyword"] = 52] = "ImportKeyword";
  Token2[Token2["ModelKeyword"] = 53] = "ModelKeyword";
  Token2[Token2["ScalarKeyword"] = 54] = "ScalarKeyword";
  Token2[Token2["NamespaceKeyword"] = 55] = "NamespaceKeyword";
  Token2[Token2["UsingKeyword"] = 56] = "UsingKeyword";
  Token2[Token2["OpKeyword"] = 57] = "OpKeyword";
  Token2[Token2["EnumKeyword"] = 58] = "EnumKeyword";
  Token2[Token2["AliasKeyword"] = 59] = "AliasKeyword";
  Token2[Token2["IsKeyword"] = 60] = "IsKeyword";
  Token2[Token2["InterfaceKeyword"] = 61] = "InterfaceKeyword";
  Token2[Token2["UnionKeyword"] = 62] = "UnionKeyword";
  Token2[Token2["ProjectionKeyword"] = 63] = "ProjectionKeyword";
  Token2[Token2["ElseKeyword"] = 64] = "ElseKeyword";
  Token2[Token2["IfKeyword"] = 65] = "IfKeyword";
  Token2[Token2["DecKeyword"] = 66] = "DecKeyword";
  Token2[Token2["FnKeyword"] = 67] = "FnKeyword";
  Token2[Token2["ConstKeyword"] = 68] = "ConstKeyword";
  Token2[Token2["InitKeyword"] = 69] = "InitKeyword";
  Token2[Token2["__EndStatementKeyword"] = 70] = "__EndStatementKeyword";
  Token2[Token2["__StartModifierKeyword"] = 70] = "__StartModifierKeyword";
  Token2[Token2["ExternKeyword"] = 70] = "ExternKeyword";
  Token2[Token2["__EndModifierKeyword"] = 71] = "__EndModifierKeyword";
  Token2[Token2["ExtendsKeyword"] = 71] = "ExtendsKeyword";
  Token2[Token2["TrueKeyword"] = 72] = "TrueKeyword";
  Token2[Token2["FalseKeyword"] = 73] = "FalseKeyword";
  Token2[Token2["ReturnKeyword"] = 74] = "ReturnKeyword";
  Token2[Token2["VoidKeyword"] = 75] = "VoidKeyword";
  Token2[Token2["NeverKeyword"] = 76] = "NeverKeyword";
  Token2[Token2["UnknownKeyword"] = 77] = "UnknownKeyword";
  Token2[Token2["ValueOfKeyword"] = 78] = "ValueOfKeyword";
  Token2[Token2["TypeOfKeyword"] = 79] = "TypeOfKeyword";
  Token2[Token2["__EndKeyword"] = 80] = "__EndKeyword";
  Token2[Token2["__StartReservedKeyword"] = 80] = "__StartReservedKeyword";
  Token2[Token2["StatemachineKeyword"] = 80] = "StatemachineKeyword";
  Token2[Token2["MacroKeyword"] = 81] = "MacroKeyword";
  Token2[Token2["PackageKeyword"] = 82] = "PackageKeyword";
  Token2[Token2["MetadataKeyword"] = 83] = "MetadataKeyword";
  Token2[Token2["EnvKeyword"] = 84] = "EnvKeyword";
  Token2[Token2["ArgKeyword"] = 85] = "ArgKeyword";
  Token2[Token2["DeclareKeyword"] = 86] = "DeclareKeyword";
  Token2[Token2["ArrayKeyword"] = 87] = "ArrayKeyword";
  Token2[Token2["StructKeyword"] = 88] = "StructKeyword";
  Token2[Token2["RecordKeyword"] = 89] = "RecordKeyword";
  Token2[Token2["ModuleKeyword"] = 90] = "ModuleKeyword";
  Token2[Token2["ModKeyword"] = 91] = "ModKeyword";
  Token2[Token2["SymKeyword"] = 92] = "SymKeyword";
  Token2[Token2["ContextKeyword"] = 93] = "ContextKeyword";
  Token2[Token2["PropKeyword"] = 94] = "PropKeyword";
  Token2[Token2["PropertyKeyword"] = 95] = "PropertyKeyword";
  Token2[Token2["ScenarioKeyword"] = 96] = "ScenarioKeyword";
  Token2[Token2["PubKeyword"] = 97] = "PubKeyword";
  Token2[Token2["SubKeyword"] = 98] = "SubKeyword";
  Token2[Token2["TypeRefKeyword"] = 99] = "TypeRefKeyword";
  Token2[Token2["TraitKeyword"] = 100] = "TraitKeyword";
  Token2[Token2["ThisKeyword"] = 101] = "ThisKeyword";
  Token2[Token2["SelfKeyword"] = 102] = "SelfKeyword";
  Token2[Token2["SuperKeyword"] = 103] = "SuperKeyword";
  Token2[Token2["KeyofKeyword"] = 104] = "KeyofKeyword";
  Token2[Token2["WithKeyword"] = 105] = "WithKeyword";
  Token2[Token2["ImplementsKeyword"] = 106] = "ImplementsKeyword";
  Token2[Token2["ImplKeyword"] = 107] = "ImplKeyword";
  Token2[Token2["SatisfiesKeyword"] = 108] = "SatisfiesKeyword";
  Token2[Token2["FlagKeyword"] = 109] = "FlagKeyword";
  Token2[Token2["AutoKeyword"] = 110] = "AutoKeyword";
  Token2[Token2["PartialKeyword"] = 111] = "PartialKeyword";
  Token2[Token2["PrivateKeyword"] = 112] = "PrivateKeyword";
  Token2[Token2["PublicKeyword"] = 113] = "PublicKeyword";
  Token2[Token2["ProtectedKeyword"] = 114] = "ProtectedKeyword";
  Token2[Token2["InternalKeyword"] = 115] = "InternalKeyword";
  Token2[Token2["SealedKeyword"] = 116] = "SealedKeyword";
  Token2[Token2["LocalKeyword"] = 117] = "LocalKeyword";
  Token2[Token2["AsyncKeyword"] = 118] = "AsyncKeyword";
  Token2[Token2["__EndReservedKeyword"] = 119] = "__EndReservedKeyword";
  Token2[Token2["__Count"] = 119] = "__Count";
})(Token || (Token = {}));
var TokenDisplay = getTokenDisplayTable([
  [Token.None, "none"],
  [Token.Invalid, "invalid"],
  [Token.EndOfFile, "end of file"],
  [Token.SingleLineComment, "single-line comment"],
  [Token.MultiLineComment, "multi-line comment"],
  [Token.ConflictMarker, "conflict marker"],
  [Token.NumericLiteral, "numeric literal"],
  [Token.StringLiteral, "string literal"],
  [Token.StringTemplateHead, "string template head"],
  [Token.StringTemplateMiddle, "string template middle"],
  [Token.StringTemplateTail, "string template tail"],
  [Token.NewLine, "newline"],
  [Token.Whitespace, "whitespace"],
  [Token.DocCodeFenceDelimiter, "doc code fence delimiter"],
  [Token.DocCodeSpan, "doc code span"],
  [Token.DocText, "doc text"],
  [Token.OpenBrace, "'{'"],
  [Token.CloseBrace, "'}'"],
  [Token.OpenParen, "'('"],
  [Token.CloseParen, "')'"],
  [Token.OpenBracket, "'['"],
  [Token.CloseBracket, "']'"],
  [Token.Dot, "'.'"],
  [Token.Ellipsis, "'...'"],
  [Token.Semicolon, "';'"],
  [Token.Comma, "','"],
  [Token.LessThan, "'<'"],
  [Token.GreaterThan, "'>'"],
  [Token.Equals, "'='"],
  [Token.Ampersand, "'&'"],
  [Token.Bar, "'|'"],
  [Token.Question, "'?'"],
  [Token.Colon, "':'"],
  [Token.ColonColon, "'::'"],
  [Token.At, "'@'"],
  [Token.AtAt, "'@@'"],
  [Token.Hash, "'#'"],
  [Token.HashBrace, "'#{'"],
  [Token.HashBracket, "'#['"],
  [Token.Star, "'*'"],
  [Token.ForwardSlash, "'/'"],
  [Token.Plus, "'+'"],
  [Token.Hyphen, "'-'"],
  [Token.Exclamation, "'!'"],
  [Token.LessThanEquals, "'<='"],
  [Token.GreaterThanEquals, "'>='"],
  [Token.AmpsersandAmpersand, "'&&'"],
  [Token.BarBar, "'||'"],
  [Token.EqualsEquals, "'=='"],
  [Token.ExclamationEquals, "'!='"],
  [Token.EqualsGreaterThan, "'=>'"],
  [Token.Identifier, "identifier"],
  [Token.ImportKeyword, "'import'"],
  [Token.ModelKeyword, "'model'"],
  [Token.ScalarKeyword, "'scalar'"],
  [Token.NamespaceKeyword, "'namespace'"],
  [Token.UsingKeyword, "'using'"],
  [Token.OpKeyword, "'op'"],
  [Token.EnumKeyword, "'enum'"],
  [Token.AliasKeyword, "'alias'"],
  [Token.IsKeyword, "'is'"],
  [Token.InterfaceKeyword, "'interface'"],
  [Token.UnionKeyword, "'union'"],
  [Token.ProjectionKeyword, "'projection'"],
  [Token.ElseKeyword, "'else'"],
  [Token.IfKeyword, "'if'"],
  [Token.DecKeyword, "'dec'"],
  [Token.FnKeyword, "'fn'"],
  [Token.ValueOfKeyword, "'valueof'"],
  [Token.TypeOfKeyword, "'typeof'"],
  [Token.ConstKeyword, "'const'"],
  [Token.InitKeyword, "'init'"],
  [Token.ExtendsKeyword, "'extends'"],
  [Token.TrueKeyword, "'true'"],
  [Token.FalseKeyword, "'false'"],
  [Token.ReturnKeyword, "'return'"],
  [Token.VoidKeyword, "'void'"],
  [Token.NeverKeyword, "'never'"],
  [Token.UnknownKeyword, "'unknown'"],
  [Token.ExternKeyword, "'extern'"],
  // Reserved keywords
  [Token.StatemachineKeyword, "'statemachine'"],
  [Token.MacroKeyword, "'macro'"],
  [Token.PackageKeyword, "'package'"],
  [Token.MetadataKeyword, "'metadata'"],
  [Token.EnvKeyword, "'env'"],
  [Token.ArgKeyword, "'arg'"],
  [Token.DeclareKeyword, "'declare'"],
  [Token.ArrayKeyword, "'array'"],
  [Token.StructKeyword, "'struct'"],
  [Token.RecordKeyword, "'record'"],
  [Token.ModuleKeyword, "'module'"],
  [Token.ModKeyword, "'mod'"],
  [Token.SymKeyword, "'sym'"],
  [Token.ContextKeyword, "'context'"],
  [Token.PropKeyword, "'prop'"],
  [Token.PropertyKeyword, "'property'"],
  [Token.ScenarioKeyword, "'scenario'"],
  [Token.PubKeyword, "'pub'"],
  [Token.SubKeyword, "'sub'"],
  [Token.TypeRefKeyword, "'typeref'"],
  [Token.TraitKeyword, "'trait'"],
  [Token.ThisKeyword, "'this'"],
  [Token.SelfKeyword, "'self'"],
  [Token.SuperKeyword, "'super'"],
  [Token.KeyofKeyword, "'keyof'"],
  [Token.WithKeyword, "'with'"],
  [Token.ImplementsKeyword, "'implements'"],
  [Token.ImplKeyword, "'impl'"],
  [Token.SatisfiesKeyword, "'satisfies'"],
  [Token.FlagKeyword, "'flag'"],
  [Token.AutoKeyword, "'auto'"],
  [Token.PartialKeyword, "'partial'"],
  [Token.PrivateKeyword, "'private'"],
  [Token.PublicKeyword, "'public'"],
  [Token.ProtectedKeyword, "'protected'"],
  [Token.InternalKeyword, "'internal'"],
  [Token.SealedKeyword, "'sealed'"],
  [Token.LocalKeyword, "'local'"],
  [Token.AsyncKeyword, "'async'"]
]);
var Keywords = /* @__PURE__ */ new Map([
  ["import", Token.ImportKeyword],
  ["model", Token.ModelKeyword],
  ["scalar", Token.ScalarKeyword],
  ["namespace", Token.NamespaceKeyword],
  ["interface", Token.InterfaceKeyword],
  ["union", Token.UnionKeyword],
  ["if", Token.IfKeyword],
  ["else", Token.ElseKeyword],
  ["projection", Token.ProjectionKeyword],
  ["using", Token.UsingKeyword],
  ["op", Token.OpKeyword],
  ["extends", Token.ExtendsKeyword],
  ["is", Token.IsKeyword],
  ["enum", Token.EnumKeyword],
  ["alias", Token.AliasKeyword],
  ["dec", Token.DecKeyword],
  ["fn", Token.FnKeyword],
  ["valueof", Token.ValueOfKeyword],
  ["typeof", Token.TypeOfKeyword],
  ["const", Token.ConstKeyword],
  ["init", Token.InitKeyword],
  ["true", Token.TrueKeyword],
  ["false", Token.FalseKeyword],
  ["return", Token.ReturnKeyword],
  ["void", Token.VoidKeyword],
  ["never", Token.NeverKeyword],
  ["unknown", Token.UnknownKeyword],
  ["extern", Token.ExternKeyword],
  // Reserved keywords
  ["statemachine", Token.StatemachineKeyword],
  ["macro", Token.MacroKeyword],
  ["package", Token.PackageKeyword],
  ["metadata", Token.MetadataKeyword],
  ["env", Token.EnvKeyword],
  ["arg", Token.ArgKeyword],
  ["declare", Token.DeclareKeyword],
  ["array", Token.ArrayKeyword],
  ["struct", Token.StructKeyword],
  ["record", Token.RecordKeyword],
  ["module", Token.ModuleKeyword],
  ["mod", Token.ModKeyword],
  ["sym", Token.SymKeyword],
  ["context", Token.ContextKeyword],
  ["prop", Token.PropKeyword],
  ["property", Token.PropertyKeyword],
  ["scenario", Token.ScenarioKeyword],
  ["pub", Token.PubKeyword],
  ["sub", Token.SubKeyword],
  ["typeref", Token.TypeRefKeyword],
  ["trait", Token.TraitKeyword],
  ["this", Token.ThisKeyword],
  ["self", Token.SelfKeyword],
  ["super", Token.SuperKeyword],
  ["keyof", Token.KeyofKeyword],
  ["with", Token.WithKeyword],
  ["implements", Token.ImplementsKeyword],
  ["impl", Token.ImplKeyword],
  ["satisfies", Token.SatisfiesKeyword],
  ["flag", Token.FlagKeyword],
  ["auto", Token.AutoKeyword],
  ["partial", Token.PartialKeyword],
  ["private", Token.PrivateKeyword],
  ["public", Token.PublicKeyword],
  ["protected", Token.ProtectedKeyword],
  ["internal", Token.InternalKeyword],
  ["sealed", Token.SealedKeyword],
  ["local", Token.LocalKeyword],
  ["async", Token.AsyncKeyword]
]);
var ReservedKeywords = /* @__PURE__ */ new Map([
  // Reserved keywords
  ["statemachine", Token.StatemachineKeyword],
  ["macro", Token.MacroKeyword],
  ["package", Token.PackageKeyword],
  ["metadata", Token.MetadataKeyword],
  ["env", Token.EnvKeyword],
  ["arg", Token.ArgKeyword],
  ["declare", Token.DeclareKeyword],
  ["array", Token.ArrayKeyword],
  ["struct", Token.StructKeyword],
  ["record", Token.RecordKeyword],
  ["module", Token.ModuleKeyword],
  ["mod", Token.ModuleKeyword],
  ["sym", Token.SymKeyword],
  ["context", Token.ContextKeyword],
  ["prop", Token.PropKeyword],
  ["property", Token.PropertyKeyword],
  ["scenario", Token.ScenarioKeyword],
  ["trait", Token.TraitKeyword],
  ["this", Token.ThisKeyword],
  ["self", Token.SelfKeyword],
  ["super", Token.SuperKeyword],
  ["keyof", Token.KeyofKeyword],
  ["with", Token.WithKeyword],
  ["implements", Token.ImplementsKeyword],
  ["impl", Token.ImplKeyword],
  ["satisfies", Token.SatisfiesKeyword],
  ["flag", Token.FlagKeyword],
  ["auto", Token.AutoKeyword],
  ["partial", Token.PartialKeyword],
  ["private", Token.PrivateKeyword],
  ["public", Token.PublicKeyword],
  ["protected", Token.ProtectedKeyword],
  ["internal", Token.InternalKeyword],
  ["sealed", Token.SealedKeyword],
  ["local", Token.LocalKeyword],
  ["async", Token.AsyncKeyword]
]);
var TokenFlags;
(function(TokenFlags2) {
  TokenFlags2[TokenFlags2["None"] = 0] = "None";
  TokenFlags2[TokenFlags2["Escaped"] = 1] = "Escaped";
  TokenFlags2[TokenFlags2["TripleQuoted"] = 2] = "TripleQuoted";
  TokenFlags2[TokenFlags2["Unterminated"] = 4] = "Unterminated";
  TokenFlags2[TokenFlags2["NonAscii"] = 8] = "NonAscii";
  TokenFlags2[TokenFlags2["DocComment"] = 16] = "DocComment";
  TokenFlags2[TokenFlags2["Backticked"] = 32] = "Backticked";
})(TokenFlags || (TokenFlags = {}));
function isTrivia(token) {
  return token >= Token.__StartTrivia && token < Token.__EndTrivia;
}
function isComment(token) {
  return token === Token.SingleLineComment || token === Token.MultiLineComment;
}
function isKeyword(token) {
  return token >= Token.__StartKeyword && token < Token.__EndKeyword;
}
function isReservedKeyword(token) {
  return token >= Token.__StartReservedKeyword && token < Token.__EndReservedKeyword;
}
function isPunctuation(token) {
  return token >= Token.__StartPunctuation && token < Token.__EndPunctuation;
}
function isStatementKeyword(token) {
  return token >= Token.__StartStatementKeyword && token < Token.__EndStatementKeyword;
}
function createScanner(source, diagnosticHandler) {
  const file = typeof source === "string" ? createSourceFile(source, "<anonymous file>") : source;
  const input = file.text;
  let position = 0;
  let endPosition = input.length;
  let token = Token.None;
  let tokenPosition = -1;
  let tokenFlags = TokenFlags.None;
  if (position < endPosition && input.charCodeAt(position) === 65279) {
    position++;
  }
  return {
    get position() {
      return position;
    },
    get token() {
      return token;
    },
    get tokenPosition() {
      return tokenPosition;
    },
    get tokenFlags() {
      return tokenFlags;
    },
    file,
    scan,
    scanRange,
    scanDoc,
    reScanStringTemplate,
    findTripleQuotedStringIndent,
    unindentAndUnescapeTripleQuotedString,
    eof,
    getTokenText,
    getTokenValue
  };
  function eof() {
    return position >= endPosition;
  }
  function getTokenText() {
    return input.substring(tokenPosition, position);
  }
  function getTokenValue() {
    switch (token) {
      case Token.StringLiteral:
      case Token.StringTemplateHead:
      case Token.StringTemplateMiddle:
      case Token.StringTemplateTail:
        return getStringTokenValue(token, tokenFlags);
      case Token.Identifier:
        return getIdentifierTokenValue();
      case Token.DocText:
        return getDocTextValue();
      default:
        return getTokenText();
    }
  }
  function lookAhead(offset) {
    const p = position + offset;
    if (p >= endPosition) {
      return Number.NaN;
    }
    return input.charCodeAt(p);
  }
  function scan() {
    tokenPosition = position;
    tokenFlags = TokenFlags.None;
    if (!eof()) {
      const ch = input.charCodeAt(position);
      switch (ch) {
        case 13:
          if (lookAhead(1) === 10) {
            position++;
          }
        // fallthrough
        case 10:
          return next(Token.NewLine);
        case 32:
        case 9:
        case 11:
        case 12:
          return scanWhitespace();
        case 40:
          return next(Token.OpenParen);
        case 41:
          return next(Token.CloseParen);
        case 44:
          return next(Token.Comma);
        case 58:
          return lookAhead(1) === 58 ? next(Token.ColonColon, 2) : next(Token.Colon);
        case 59:
          return next(Token.Semicolon);
        case 91:
          return next(Token.OpenBracket);
        case 93:
          return next(Token.CloseBracket);
        case 123:
          return next(Token.OpenBrace);
        case 125:
          return next(Token.CloseBrace);
        case 64:
          return lookAhead(1) === 64 ? next(Token.AtAt, 2) : next(Token.At);
        case 35:
          const ahead = lookAhead(1);
          switch (ahead) {
            case 123:
              return next(Token.HashBrace, 2);
            case 91:
              return next(Token.HashBracket, 2);
            default:
              return next(Token.Hash);
          }
        case 43:
          return isDigit(lookAhead(1)) ? scanSignedNumber() : next(Token.Plus);
        case 45:
          return isDigit(lookAhead(1)) ? scanSignedNumber() : next(Token.Hyphen);
        case 42:
          return next(Token.Star);
        case 63:
          return next(Token.Question);
        case 38:
          return lookAhead(1) === 38 ? next(Token.AmpsersandAmpersand, 2) : next(Token.Ampersand);
        case 46:
          return lookAhead(1) === 46 && lookAhead(2) === 46 ? next(Token.Ellipsis, 3) : next(Token.Dot);
        case 47:
          switch (lookAhead(1)) {
            case 47:
              return scanSingleLineComment();
            case 42:
              return scanMultiLineComment();
          }
          return next(Token.ForwardSlash);
        case 48:
          switch (lookAhead(1)) {
            case 120:
              return scanHexNumber();
            case 98:
              return scanBinaryNumber();
          }
        // fallthrough
        case 49:
        case 50:
        case 51:
        case 52:
        case 53:
        case 54:
        case 55:
        case 56:
        case 57:
          return scanNumber();
        case 60:
          if (atConflictMarker())
            return scanConflictMarker();
          return lookAhead(1) === 61 ? next(Token.LessThanEquals, 2) : next(Token.LessThan);
        case 62:
          if (atConflictMarker())
            return scanConflictMarker();
          return lookAhead(1) === 61 ? next(Token.GreaterThanEquals, 2) : next(Token.GreaterThan);
        case 61:
          if (atConflictMarker())
            return scanConflictMarker();
          switch (lookAhead(1)) {
            case 61:
              return next(Token.EqualsEquals, 2);
            case 62:
              return next(Token.EqualsGreaterThan, 2);
          }
          return next(Token.Equals);
        case 124:
          if (atConflictMarker())
            return scanConflictMarker();
          return lookAhead(1) === 124 ? next(Token.BarBar, 2) : next(Token.Bar);
        case 34:
          return lookAhead(1) === 34 && lookAhead(2) === 34 ? scanString(TokenFlags.TripleQuoted) : scanString(TokenFlags.None);
        case 33:
          return lookAhead(1) === 61 ? next(Token.ExclamationEquals, 2) : next(Token.Exclamation);
        case 96:
          return scanBacktickedIdentifier();
        default:
          if (isLowercaseAsciiLetter(ch)) {
            return scanIdentifierOrKeyword();
          }
          if (isAsciiIdentifierStart(ch)) {
            return scanIdentifier();
          }
          if (ch <= 127) {
            return scanInvalidCharacter();
          }
          return scanNonAsciiToken();
      }
    }
    return token = Token.EndOfFile;
  }
  function scanDoc() {
    tokenPosition = position;
    tokenFlags = TokenFlags.None;
    if (!eof()) {
      const ch = input.charCodeAt(position);
      switch (ch) {
        case 13:
          if (lookAhead(1) === 10) {
            position++;
          }
        // fallthrough
        case 10:
          return next(Token.NewLine);
        case 92:
          if (lookAhead(1) === 64) {
            tokenFlags |= TokenFlags.Escaped;
            return next(Token.DocText, 2);
          }
          return next(Token.DocText);
        case 32:
        case 9:
        case 11:
        case 12:
          return scanWhitespace();
        case 125:
          return next(Token.CloseBrace);
        case 64:
          return next(Token.At);
        case 42:
          return next(Token.Star);
        case 96:
          return lookAhead(1) === 96 && lookAhead(2) === 96 ? next(Token.DocCodeFenceDelimiter, 3) : scanDocCodeSpan();
        case 60:
        case 62:
        case 61:
        case 124:
          if (atConflictMarker())
            return scanConflictMarker();
          return next(Token.DocText);
        case 45:
          return next(Token.Hyphen);
      }
      if (isAsciiIdentifierStart(ch)) {
        return scanIdentifier();
      }
      if (ch <= 127) {
        return next(Token.DocText);
      }
      const cp = input.codePointAt(position);
      if (isIdentifierStart(cp)) {
        return scanNonAsciiIdentifier(cp);
      }
      return scanUnknown(Token.DocText);
    }
    return token = Token.EndOfFile;
  }
  function reScanStringTemplate(lastTokenFlags) {
    position = tokenPosition;
    tokenFlags = TokenFlags.None;
    return scanStringTemplateSpan(lastTokenFlags);
  }
  function scanRange(range, callback) {
    const savedPosition = position;
    const savedEndPosition = endPosition;
    const savedToken = token;
    const savedTokenPosition = tokenPosition;
    const savedTokenFlags = tokenFlags;
    position = range.pos;
    endPosition = range.end;
    token = Token.None;
    tokenPosition = -1;
    tokenFlags = TokenFlags.None;
    const result = callback();
    position = savedPosition;
    endPosition = savedEndPosition;
    token = savedToken;
    tokenPosition = savedTokenPosition;
    tokenFlags = savedTokenFlags;
    return result;
  }
  function next(t, count = 1) {
    position += count;
    return token = t;
  }
  function unterminated(t) {
    tokenFlags |= TokenFlags.Unterminated;
    error({ code: "unterminated", format: { token: TokenDisplay[t] } });
    return token = t;
  }
  function scanNonAsciiToken() {
    tokenFlags |= TokenFlags.NonAscii;
    const ch = input.charCodeAt(position);
    if (isNonAsciiWhiteSpaceSingleLine(ch)) {
      return scanWhitespace();
    }
    const cp = input.codePointAt(position);
    if (isNonAsciiIdentifierCharacter(cp)) {
      return scanNonAsciiIdentifier(cp);
    }
    return scanInvalidCharacter();
  }
  function scanInvalidCharacter() {
    token = scanUnknown(Token.Invalid);
    error({ code: "invalid-character" });
    return token;
  }
  function scanUnknown(t) {
    const codePoint = input.codePointAt(position);
    return token = next(t, utf16CodeUnits(codePoint));
  }
  function error(report, pos, end) {
    const diagnostic = createDiagnostic({
      ...report,
      target: { file, pos: pos ?? tokenPosition, end: end ?? position }
    });
    diagnosticHandler(diagnostic);
  }
  function scanWhitespace() {
    do {
      position++;
    } while (!eof() && isWhiteSpaceSingleLine(input.charCodeAt(position)));
    return token = Token.Whitespace;
  }
  function scanSignedNumber() {
    position++;
    return scanNumber();
  }
  function scanNumber() {
    scanKnownDigits();
    if (!eof() && input.charCodeAt(position) === 46) {
      position++;
      scanRequiredDigits();
    }
    if (!eof() && input.charCodeAt(position) === 101) {
      position++;
      const ch = input.charCodeAt(position);
      if (ch === 43 || ch === 45) {
        position++;
      }
      scanRequiredDigits();
    }
    return token = Token.NumericLiteral;
  }
  function scanKnownDigits() {
    do {
      position++;
    } while (!eof() && isDigit(input.charCodeAt(position)));
  }
  function scanRequiredDigits() {
    if (eof() || !isDigit(input.charCodeAt(position))) {
      error({ code: "digit-expected" });
      return;
    }
    scanKnownDigits();
  }
  function scanHexNumber() {
    position += 2;
    if (eof() || !isHexDigit(input.charCodeAt(position))) {
      error({ code: "hex-digit-expected" });
      return token = Token.NumericLiteral;
    }
    do {
      position++;
    } while (!eof() && isHexDigit(input.charCodeAt(position)));
    return token = Token.NumericLiteral;
  }
  function scanBinaryNumber() {
    position += 2;
    if (eof() || !isBinaryDigit(input.charCodeAt(position))) {
      error({ code: "binary-digit-expected" });
      return token = Token.NumericLiteral;
    }
    do {
      position++;
    } while (!eof() && isBinaryDigit(input.charCodeAt(position)));
    return token = Token.NumericLiteral;
  }
  function scanSingleLineComment() {
    position = skipSingleLineComment(input, position, endPosition);
    return token = Token.SingleLineComment;
  }
  function scanMultiLineComment() {
    token = Token.MultiLineComment;
    if (lookAhead(2) === 42) {
      tokenFlags |= TokenFlags.DocComment;
    }
    const [newPosition, terminated] = skipMultiLineComment(input, position);
    position = newPosition;
    return terminated ? token : unterminated(token);
  }
  function scanDocCodeSpan() {
    position++;
    loop: for (; !eof(); position++) {
      const ch = input.charCodeAt(position);
      switch (ch) {
        case 96:
          position++;
          return token = Token.DocCodeSpan;
        case 13:
        case 10:
          break loop;
      }
    }
    return unterminated(Token.DocCodeSpan);
  }
  function scanString(tokenFlags2) {
    if (tokenFlags2 & TokenFlags.TripleQuoted) {
      position += 3;
    } else {
      position++;
    }
    return scanStringLiteralLike(tokenFlags2, Token.StringTemplateHead, Token.StringLiteral);
  }
  function scanStringTemplateSpan(tokenFlags2) {
    position++;
    return scanStringLiteralLike(tokenFlags2, Token.StringTemplateMiddle, Token.StringTemplateTail);
  }
  function scanStringLiteralLike(requestedTokenFlags, template, tail) {
    const multiLine = requestedTokenFlags & TokenFlags.TripleQuoted;
    tokenFlags = requestedTokenFlags;
    loop: for (; !eof(); position++) {
      const ch = input.charCodeAt(position);
      switch (ch) {
        case 92:
          tokenFlags |= TokenFlags.Escaped;
          position++;
          if (eof()) {
            break loop;
          }
          continue;
        case 34:
          if (multiLine) {
            if (lookAhead(1) === 34 && lookAhead(2) === 34) {
              position += 3;
              token = tail;
              return tail;
            } else {
              continue;
            }
          } else {
            position++;
            token = tail;
            return tail;
          }
        case 36:
          if (lookAhead(1) === 123) {
            position += 2;
            token = template;
            return template;
          }
          continue;
        case 13:
        case 10:
          if (multiLine) {
            continue;
          } else {
            break loop;
          }
      }
    }
    return unterminated(tail);
  }
  function getStringLiteralOffsetStart(token2, tokenFlags2) {
    switch (token2) {
      case Token.StringLiteral:
      case Token.StringTemplateHead:
        return tokenFlags2 & TokenFlags.TripleQuoted ? 3 : 1;
      // """ or "
      default:
        return 1;
    }
  }
  function getStringLiteralOffsetEnd(token2, tokenFlags2) {
    switch (token2) {
      case Token.StringLiteral:
      case Token.StringTemplateTail:
        return tokenFlags2 & TokenFlags.TripleQuoted ? 3 : 1;
      // """ or "
      default:
        return 2;
    }
  }
  function getStringTokenValue(token2, tokenFlags2) {
    if (tokenFlags2 & TokenFlags.TripleQuoted) {
      const start2 = tokenPosition;
      const end2 = position;
      const [indentationStart, indentationEnd] = findTripleQuotedStringIndent(start2, end2);
      return unindentAndUnescapeTripleQuotedString(start2, end2, indentationStart, indentationEnd, token2, tokenFlags2);
    }
    const startOffset = getStringLiteralOffsetStart(token2, tokenFlags2);
    const endOffset = getStringLiteralOffsetEnd(token2, tokenFlags2);
    const start = tokenPosition + startOffset;
    const end = tokenFlags2 & TokenFlags.Unterminated ? position : position - endOffset;
    if (tokenFlags2 & TokenFlags.Escaped) {
      return unescapeString(start, end);
    }
    return input.substring(start, end);
  }
  function getIdentifierTokenValue() {
    const start = tokenFlags & TokenFlags.Backticked ? tokenPosition + 1 : tokenPosition;
    const end = tokenFlags & TokenFlags.Backticked && !(tokenFlags & TokenFlags.Unterminated) ? position - 1 : position;
    const text = tokenFlags & TokenFlags.Escaped ? unescapeString(start, end) : input.substring(start, end);
    if (tokenFlags & TokenFlags.NonAscii) {
      return text.normalize("NFC");
    }
    return text;
  }
  function getDocTextValue() {
    if (tokenFlags & TokenFlags.Escaped) {
      let start = tokenPosition;
      const end = position;
      let result = "";
      let pos = start;
      while (pos < end) {
        const ch = input.charCodeAt(pos);
        if (ch !== 92) {
          pos++;
          continue;
        }
        if (pos === end - 1) {
          break;
        }
        result += input.substring(start, pos);
        switch (input.charCodeAt(pos + 1)) {
          case 64:
            result += "@";
            break;
          default:
            result += input.substring(pos, pos + 2);
        }
        pos += 2;
        start = pos;
      }
      result += input.substring(start, end);
      return result;
    } else {
      return input.substring(tokenPosition, position);
    }
  }
  function findTripleQuotedStringIndent(start, end) {
    end = end - 3;
    const indentationEnd = end;
    while (end > start && isWhiteSpaceSingleLine(input.charCodeAt(end - 1))) {
      end--;
    }
    const indentationStart = end;
    if (isLineBreak(input.charCodeAt(end - 1))) {
      if (isCrlf(end - 2, 0, end)) {
        end--;
      }
      end--;
    }
    return [indentationStart, indentationEnd];
  }
  function unindentAndUnescapeTripleQuotedString(start, end, indentationStart, indentationEnd, token2, tokenFlags2) {
    const startOffset = getStringLiteralOffsetStart(token2, tokenFlags2);
    const endOffset = getStringLiteralOffsetEnd(token2, tokenFlags2);
    start = start + startOffset;
    end = tokenFlags2 & TokenFlags.Unterminated ? end : end - endOffset;
    if (token2 === Token.StringLiteral || token2 === Token.StringTemplateHead) {
      while (start < end && isWhiteSpaceSingleLine(input.charCodeAt(start))) {
        start++;
      }
      if (isLineBreak(input.charCodeAt(start))) {
        if (isCrlf(start, start, end)) {
          start++;
        }
        start++;
      } else {
        error({
          code: "no-new-line-start-triple-quote",
          codefixes: [createTripleQuoteIndentCodeFix({ file, pos: tokenPosition, end: position })]
        });
      }
    }
    if (token2 === Token.StringLiteral || token2 === Token.StringTemplateTail) {
      while (end > start && isWhiteSpaceSingleLine(input.charCodeAt(end - 1))) {
        end--;
      }
      if (isLineBreak(input.charCodeAt(end - 1))) {
        if (isCrlf(end - 2, start, end)) {
          end--;
        }
        end--;
      } else {
        error({
          code: "no-new-line-end-triple-quote",
          codefixes: [createTripleQuoteIndentCodeFix({ file, pos: tokenPosition, end: position })]
        });
      }
    }
    let skipUnindentOnce = false;
    if (token2 === Token.StringTemplateMiddle || token2 === Token.StringTemplateTail) {
      skipUnindentOnce = true;
    }
    let result = "";
    let pos = start;
    while (pos < end) {
      if (skipUnindentOnce) {
        skipUnindentOnce = false;
      } else {
        start = skipMatchingIndentation(pos, end, indentationStart, indentationEnd);
      }
      let ch;
      while (pos < end && !isLineBreak(ch = input.charCodeAt(pos))) {
        if (ch !== 92) {
          pos++;
          continue;
        }
        result += input.substring(start, pos);
        if (pos === end - 1) {
          error({ code: "invalid-escape-sequence" }, pos, pos);
          pos++;
        } else {
          result += unescapeOne(pos);
          pos += 2;
        }
        start = pos;
      }
      if (pos < end) {
        if (isCrlf(pos, start, end)) {
          result += input.substring(start, pos);
          result += "\n";
          pos += 2;
        } else {
          pos++;
          result += input.substring(start, pos);
        }
        start = pos;
      }
    }
    result += input.substring(start, pos);
    return result;
  }
  function isCrlf(pos, start, end) {
    return pos >= start && pos < end - 1 && input.charCodeAt(pos) === 13 && input.charCodeAt(pos + 1) === 10;
  }
  function skipMatchingIndentation(pos, end, indentationStart, indentationEnd) {
    let indentationPos = indentationStart;
    end = Math.min(end, pos + (indentationEnd - indentationStart));
    while (pos < end) {
      const ch = input.charCodeAt(pos);
      if (isLineBreak(ch)) {
        break;
      }
      if (ch !== input.charCodeAt(indentationPos)) {
        error({
          code: "triple-quote-indent",
          codefixes: [createTripleQuoteIndentCodeFix({ file, pos: tokenPosition, end: position })]
        });
        break;
      }
      indentationPos++;
      pos++;
    }
    return pos;
  }
  function unescapeString(start, end) {
    let result = "";
    let pos = start;
    while (pos < end) {
      const ch = input.charCodeAt(pos);
      if (ch !== 92) {
        pos++;
        continue;
      }
      if (pos === end - 1) {
        error({ code: "invalid-escape-sequence" }, pos, pos);
        break;
      }
      result += input.substring(start, pos);
      result += unescapeOne(pos);
      pos += 2;
      start = pos;
    }
    result += input.substring(start, pos);
    return result;
  }
  function unescapeOne(pos) {
    const ch = input.charCodeAt(pos + 1);
    switch (ch) {
      case 114:
        return "\r";
      case 110:
        return "\n";
      case 116:
        return "	";
      case 34:
        return '"';
      case 92:
        return "\\";
      case 36:
        return "$";
      case 64:
        return "@";
      case 96:
        return "`";
      default:
        error({ code: "invalid-escape-sequence" }, pos, pos + 2);
        return String.fromCharCode(ch);
    }
  }
  function scanIdentifierOrKeyword() {
    let count = 0;
    let ch = input.charCodeAt(position);
    while (true) {
      position++;
      count++;
      if (eof()) {
        break;
      }
      ch = input.charCodeAt(position);
      if (count < 12 && isLowercaseAsciiLetter(ch)) {
        continue;
      }
      if (isAsciiIdentifierContinue(ch)) {
        return scanIdentifier();
      }
      if (ch > 127) {
        const cp = input.codePointAt(position);
        if (isNonAsciiIdentifierCharacter(cp)) {
          return scanNonAsciiIdentifier(cp);
        }
      }
      break;
    }
    if (count >= 2 && count <= 12) {
      const keyword = Keywords.get(getTokenText());
      if (keyword) {
        return token = keyword;
      }
    }
    return token = Token.Identifier;
  }
  function scanIdentifier() {
    let ch;
    do {
      position++;
      if (eof()) {
        return token = Token.Identifier;
      }
    } while (isAsciiIdentifierContinue(ch = input.charCodeAt(position)));
    if (ch > 127) {
      const cp = input.codePointAt(position);
      if (isNonAsciiIdentifierCharacter(cp)) {
        return scanNonAsciiIdentifier(cp);
      }
    }
    return token = Token.Identifier;
  }
  function scanBacktickedIdentifier() {
    position++;
    tokenFlags |= TokenFlags.Backticked;
    loop: for (; !eof(); position++) {
      const ch = input.charCodeAt(position);
      switch (ch) {
        case 92:
          position++;
          tokenFlags |= TokenFlags.Escaped;
          continue;
        case 96:
          position++;
          return token = Token.Identifier;
        case 13:
        case 10:
          break loop;
        default:
          if (ch > 127) {
            tokenFlags |= TokenFlags.NonAscii;
          }
      }
    }
    return unterminated(Token.Identifier);
  }
  function scanNonAsciiIdentifier(startCodePoint) {
    tokenFlags |= TokenFlags.NonAscii;
    let cp = startCodePoint;
    do {
      position += utf16CodeUnits(cp);
    } while (!eof() && isIdentifierContinue(cp = input.codePointAt(position)));
    return token = Token.Identifier;
  }
  function atConflictMarker() {
    return isConflictMarker(input, position, endPosition);
  }
  function scanConflictMarker() {
    const marker = input.charCodeAt(position);
    position += mergeConflictMarkerLength;
    error({ code: "conflict-marker" });
    if (marker === 60 || marker === 62) {
      while (position < endPosition && !isLineBreak(input.charCodeAt(position))) {
        position++;
      }
    } else {
      while (position < endPosition) {
        const ch = input.charCodeAt(position);
        if ((ch === 61 || ch === 62) && ch !== marker && isConflictMarker(input, position, endPosition)) {
          break;
        }
        position++;
      }
    }
    return token = Token.ConflictMarker;
  }
}
function skipTriviaBackward(script, position, endPosition = -1) {
  endPosition = endPosition < -1 ? -1 : endPosition;
  const input = script.file.text;
  if (position === input.length) {
    position--;
  } else if (position > input.length) {
    compilerAssert(false, "position out of range");
  }
  while (position > endPosition) {
    const ch = input.charCodeAt(position);
    if (isWhiteSpace(ch)) {
      position--;
    } else {
      const comment = getCommentAtPosition(script, position);
      if (comment) {
        position = comment.pos - 1;
      } else {
        break;
      }
    }
  }
  return position;
}
function skipTrivia(input, position, endPosition = input.length) {
  endPosition = endPosition > input.length ? input.length : endPosition;
  while (position < endPosition) {
    const ch = input.charCodeAt(position);
    if (isWhiteSpace(ch)) {
      position++;
      continue;
    }
    if (ch === 47) {
      switch (input.charCodeAt(position + 1)) {
        case 47:
          position = skipSingleLineComment(input, position, endPosition);
          continue;
        case 42:
          position = skipMultiLineComment(input, position, endPosition)[0];
          continue;
      }
    }
    break;
  }
  return position;
}
function skipWhiteSpace(input, position, endPosition = input.length) {
  while (position < endPosition) {
    const ch = input.charCodeAt(position);
    if (!isWhiteSpace(ch)) {
      break;
    }
    position++;
  }
  return position;
}
function skipSingleLineComment(input, position, endPosition = input.length) {
  position += 2;
  for (; position < endPosition; position++) {
    if (isLineBreak(input.charCodeAt(position))) {
      break;
    }
  }
  return position;
}
function skipMultiLineComment(input, position, endPosition = input.length) {
  position += 2;
  for (; position < endPosition; position++) {
    if (input.charCodeAt(position) === 42 && input.charCodeAt(position + 1) === 47) {
      return [position + 2, true];
    }
  }
  return [position, false];
}
function skipContinuousIdentifier(input, position, isBackward = false) {
  let cur = position;
  const direction = isBackward ? -1 : 1;
  const bar = isBackward ? (p) => p >= 0 : (p) => p < input.length;
  while (bar(cur)) {
    const { char: cp, size } = codePointBefore(input, cur);
    cur += direction * size;
    if (!cp || !isIdentifierContinue(cp)) {
      break;
    }
  }
  return cur;
}
function isConflictMarker(input, position, endPosition = input.length) {
  const ch = input.charCodeAt(position);
  if (position === 0 || isLineBreak(input.charCodeAt(position - 1))) {
    if (position + mergeConflictMarkerLength < endPosition) {
      for (let i = 0; i < mergeConflictMarkerLength; i++) {
        if (input.charCodeAt(position + i) !== ch) {
          return false;
        }
      }
      return ch === 61 || input.charCodeAt(position + mergeConflictMarkerLength) === 32;
    }
  }
  return false;
}
function getTokenDisplayTable(entries) {
  const table = new Array(entries.length);
  for (const [token, display] of entries) {
    compilerAssert(token >= 0 && token < Token.__Count, `Invalid entry in token display table, ${token}, ${Token[token]}, ${display}`);
    compilerAssert(!table[token], `Duplicate entry in token display table for: ${token}, ${Token[token]}, ${display}`);
    table[token] = display;
  }
  for (let token = 0; token < Token.__Count; token++) {
    compilerAssert(table[token], `Missing entry in token display table: ${token}, ${Token[token]}`);
  }
  return table;
}

// src/typespec/core/packages/compiler/dist/src/core/helpers/syntax-utils.js
function printIdentifier(sv, context = "disallow-reserved") {
  if (needBacktick(sv, context)) {
    const escapedString = sv.replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/\r/g, "\\r").replace(/\t/g, "\\t").replace(/`/g, "\\`");
    return `\`${escapedString}\``;
  } else {
    return sv;
  }
}
function needBacktick(sv, context) {
  if (sv.length === 0) {
    return false;
  }
  if (context === "allow-reserved" && ReservedKeywords.has(sv)) {
    return false;
  }
  if (Keywords.has(sv)) {
    return true;
  }
  let cp = sv.codePointAt(0);
  if (!isIdentifierStart(cp)) {
    return true;
  }
  let pos = 0;
  do {
    pos += utf16CodeUnits(cp);
  } while (pos < sv.length && isIdentifierContinue(cp = sv.codePointAt(pos)));
  return pos < sv.length;
}
function typeReferenceToString(node) {
  switch (node.kind) {
    case SyntaxKind.MemberExpression:
      return `${typeReferenceToString(node.base)}${node.selector}${typeReferenceToString(node.id)}`;
    case SyntaxKind.TypeReference:
      return typeReferenceToString(node.target);
    case SyntaxKind.Identifier:
      return node.sv;
  }
}
function splitLines(text) {
  const lines = [];
  let start = 0;
  let pos = 0;
  while (pos < text.length) {
    const ch = text.charCodeAt(pos);
    switch (ch) {
      case 13:
        if (text.charCodeAt(pos + 1) === 10) {
          lines.push(text.slice(start, pos));
          start = pos + 2;
          pos++;
        } else {
          lines.push(text.slice(start, pos));
          start = pos + 1;
        }
        break;
      case 10:
        lines.push(text.slice(start, pos));
        start = pos + 1;
        break;
    }
    pos++;
  }
  lines.push(text.slice(start));
  return lines;
}

// src/typespec/core/packages/compiler/dist/src/core/parser.js
var ListKind;
(function(ListKind2) {
  const PropertiesBase = {
    allowEmpty: true,
    toleratedDelimiterIsValid: true,
    allowedStatementKeyword: Token.None
  };
  ListKind2.OperationParameters = {
    ...PropertiesBase,
    open: Token.OpenParen,
    close: Token.CloseParen,
    delimiter: Token.Comma,
    toleratedDelimiter: Token.Semicolon
  };
  ListKind2.DecoratorArguments = {
    ...ListKind2.OperationParameters,
    invalidAnnotationTarget: "expression"
  };
  ListKind2.FunctionArguments = {
    ...ListKind2.OperationParameters,
    invalidAnnotationTarget: "expression"
  };
  ListKind2.ModelProperties = {
    ...PropertiesBase,
    open: Token.OpenBrace,
    close: Token.CloseBrace,
    delimiter: Token.Semicolon,
    toleratedDelimiter: Token.Comma
  };
  ListKind2.ObjectLiteralProperties = {
    ...PropertiesBase,
    open: Token.HashBrace,
    close: Token.CloseBrace,
    delimiter: Token.Comma,
    toleratedDelimiter: Token.Comma
  };
  ListKind2.InterfaceMembers = {
    ...PropertiesBase,
    open: Token.OpenBrace,
    close: Token.CloseBrace,
    delimiter: Token.Semicolon,
    toleratedDelimiter: Token.Comma,
    toleratedDelimiterIsValid: false,
    allowedStatementKeyword: Token.OpKeyword
  };
  ListKind2.ScalarMembers = {
    ...PropertiesBase,
    open: Token.OpenBrace,
    close: Token.CloseBrace,
    delimiter: Token.Semicolon,
    toleratedDelimiter: Token.Comma,
    toleratedDelimiterIsValid: false,
    allowedStatementKeyword: Token.InitKeyword
  };
  ListKind2.UnionVariants = {
    ...PropertiesBase,
    open: Token.OpenBrace,
    close: Token.CloseBrace,
    delimiter: Token.Semicolon,
    toleratedDelimiter: Token.Comma,
    toleratedDelimiterIsValid: true
  };
  ListKind2.EnumMembers = {
    ...ListKind2.ModelProperties
  };
  const ExpresionsBase = {
    allowEmpty: true,
    delimiter: Token.Comma,
    toleratedDelimiter: Token.Semicolon,
    toleratedDelimiterIsValid: false,
    invalidAnnotationTarget: "expression",
    allowedStatementKeyword: Token.None
  };
  ListKind2.TemplateParameters = {
    ...ExpresionsBase,
    allowEmpty: false,
    open: Token.LessThan,
    close: Token.GreaterThan,
    invalidAnnotationTarget: "template parameter"
  };
  ListKind2.TemplateArguments = {
    ...ListKind2.TemplateParameters
  };
  ListKind2.CallArguments = {
    ...ExpresionsBase,
    allowEmpty: true,
    open: Token.OpenParen,
    close: Token.CloseParen
  };
  ListKind2.Heritage = {
    ...ExpresionsBase,
    allowEmpty: false,
    open: Token.None,
    close: Token.None
  };
  ListKind2.Tuple = {
    ...ExpresionsBase,
    allowEmpty: true,
    open: Token.OpenBracket,
    close: Token.CloseBracket
  };
  ListKind2.ArrayLiteral = {
    ...ExpresionsBase,
    allowEmpty: true,
    open: Token.HashBracket,
    close: Token.CloseBracket
  };
  ListKind2.FunctionParameters = {
    ...ExpresionsBase,
    allowEmpty: true,
    open: Token.OpenParen,
    close: Token.CloseParen,
    invalidAnnotationTarget: "expression"
  };
})(ListKind || (ListKind = {}));
function parse(code, options = {}) {
  const parser = createParser(code, options);
  return parser.parseTypeSpecScript();
}
function parseStandaloneTypeReference(code) {
  const parser = createParser(code);
  const node = parser.parseStandaloneReferenceExpression();
  return [node, parser.parseDiagnostics];
}
function createParser(code, options = {}) {
  let parseErrorInNextFinishedNode = false;
  let previousTokenEnd = -1;
  let realPositionOfLastError = -1;
  let missingIdentifierCounter = 0;
  let treePrintable = true;
  let newLineIsTrivia = true;
  let currentMode = 0;
  const parseDiagnostics = [];
  const scanner = createScanner(code, reportDiagnostic2);
  const comments = [];
  let docRanges = [];
  nextToken();
  return {
    parseDiagnostics,
    parseTypeSpecScript,
    parseStandaloneReferenceExpression
  };
  function parseTypeSpecScript() {
    const statements = parseTypeSpecScriptItemList();
    return {
      kind: SyntaxKind.TypeSpecScript,
      statements,
      file: scanner.file,
      id: {
        kind: SyntaxKind.Identifier,
        sv: scanner.file.path,
        pos: 0,
        end: 0,
        flags: 8
      },
      namespaces: [],
      usings: [],
      locals: void 0,
      inScopeNamespaces: [],
      parseDiagnostics,
      comments,
      printable: treePrintable,
      parseOptions: options,
      ...finishNode(0)
    };
  }
  function parseAnnotations({ skipParsingDocNodes } = {}) {
    const directives = [];
    const decorators = [];
    const docs = [];
    let pos = tokenPos();
    if (!skipParsingDocNodes) {
      const [firstPos, addedDocs] = parseDocList();
      pos = firstPos;
      for (const doc of addedDocs) {
        docs.push(doc);
      }
    }
    while (token() === Token.Hash || token() === Token.At) {
      if (token() === Token.Hash) {
        directives.push(parseDirectiveExpression());
      } else if (token() === Token.At) {
        decorators.push(parseDecoratorExpression());
      }
      if (!skipParsingDocNodes) {
        const [_, addedDocs] = parseDocList();
        for (const doc of addedDocs) {
          docs.push(doc);
        }
      }
    }
    return { pos, docs, directives, decorators };
  }
  function parseTypeSpecScriptItemList() {
    const stmts = [];
    let seenBlocklessNs = false;
    let seenDecl = false;
    let seenUsing = false;
    while (token() !== Token.EndOfFile) {
      const { pos, docs, directives, decorators } = parseAnnotations();
      const tok = token();
      let item;
      switch (tok) {
        case Token.AtAt:
          reportInvalidDecorators(decorators, "augment decorator statement");
          item = parseAugmentDecorator();
          break;
        case Token.ImportKeyword:
          reportInvalidDecorators(decorators, "import statement");
          item = parseImportStatement();
          break;
        case Token.ModelKeyword:
          item = parseModelStatement(pos, decorators);
          break;
        case Token.ScalarKeyword:
          item = parseScalarStatement(pos, decorators);
          break;
        case Token.NamespaceKeyword:
          item = parseNamespaceStatement(pos, decorators, docs, directives);
          break;
        case Token.InterfaceKeyword:
          item = parseInterfaceStatement(pos, decorators);
          break;
        case Token.UnionKeyword:
          item = parseUnionStatement(pos, decorators);
          break;
        case Token.OpKeyword:
          item = parseOperationStatement(pos, decorators);
          break;
        case Token.EnumKeyword:
          item = parseEnumStatement(pos, decorators);
          break;
        case Token.AliasKeyword:
          reportInvalidDecorators(decorators, "alias statement");
          item = parseAliasStatement(pos);
          break;
        case Token.ConstKeyword:
          reportInvalidDecorators(decorators, "const statement");
          item = parseConstStatement(pos);
          break;
        case Token.UsingKeyword:
          reportInvalidDecorators(decorators, "using statement");
          item = parseUsingStatement(pos);
          break;
        case Token.Semicolon:
          reportInvalidDecorators(decorators, "empty statement");
          item = parseEmptyStatement(pos);
          break;
        // Start of declaration with modifiers
        case Token.ExternKeyword:
        case Token.FnKeyword:
        case Token.DecKeyword:
          item = parseDeclaration(pos);
          break;
        default:
          item = parseInvalidStatement(pos, decorators);
          break;
      }
      if (tok !== Token.NamespaceKeyword) {
        mutate(item).directives = directives;
        mutate(item).docs = docs;
      }
      if (isBlocklessNamespace(item)) {
        if (seenBlocklessNs) {
          error({ code: "multiple-blockless-namespace", target: item });
        }
        if (seenDecl) {
          error({ code: "blockless-namespace-first", target: item });
        }
        seenBlocklessNs = true;
      } else if (item.kind === SyntaxKind.ImportStatement) {
        if (seenDecl || seenBlocklessNs || seenUsing) {
          error({ code: "import-first", target: item });
        }
      } else if (item.kind === SyntaxKind.UsingStatement) {
        seenUsing = true;
      } else {
        seenDecl = true;
      }
      stmts.push(item);
    }
    return stmts;
  }
  function parseStatementList() {
    const stmts = [];
    while (token() !== Token.CloseBrace) {
      const { pos, docs, directives, decorators } = parseAnnotations();
      const tok = token();
      let item;
      switch (tok) {
        case Token.AtAt:
          reportInvalidDecorators(decorators, "augment decorator statement");
          item = parseAugmentDecorator();
          break;
        case Token.ImportKeyword:
          reportInvalidDecorators(decorators, "import statement");
          item = parseImportStatement();
          error({ code: "import-first", messageId: "topLevel", target: item });
          break;
        case Token.ModelKeyword:
          item = parseModelStatement(pos, decorators);
          break;
        case Token.ScalarKeyword:
          item = parseScalarStatement(pos, decorators);
          break;
        case Token.NamespaceKeyword:
          const ns = parseNamespaceStatement(pos, decorators, docs, directives);
          if (isBlocklessNamespace(ns)) {
            error({ code: "blockless-namespace-first", messageId: "topLevel", target: ns });
          }
          item = ns;
          break;
        case Token.InterfaceKeyword:
          item = parseInterfaceStatement(pos, decorators);
          break;
        case Token.UnionKeyword:
          item = parseUnionStatement(pos, decorators);
          break;
        case Token.OpKeyword:
          item = parseOperationStatement(pos, decorators);
          break;
        case Token.EnumKeyword:
          item = parseEnumStatement(pos, decorators);
          break;
        case Token.AliasKeyword:
          reportInvalidDecorators(decorators, "alias statement");
          item = parseAliasStatement(pos);
          break;
        case Token.ConstKeyword:
          reportInvalidDecorators(decorators, "const statement");
          item = parseConstStatement(pos);
          break;
        case Token.UsingKeyword:
          reportInvalidDecorators(decorators, "using statement");
          item = parseUsingStatement(pos);
          break;
        case Token.ExternKeyword:
        case Token.FnKeyword:
        case Token.DecKeyword:
          item = parseDeclaration(pos);
          break;
        case Token.EndOfFile:
          parseExpected(Token.CloseBrace);
          return stmts;
        case Token.Semicolon:
          reportInvalidDecorators(decorators, "empty statement");
          item = parseEmptyStatement(pos);
          break;
        default:
          item = parseInvalidStatement(pos, decorators);
          break;
      }
      mutate(item).directives = directives;
      if (tok !== Token.NamespaceKeyword) {
        mutate(item).docs = docs;
      }
      stmts.push(item);
    }
    return stmts;
  }
  function parseDecoratorList() {
    const decorators = [];
    while (token() === Token.At) {
      decorators.push(parseDecoratorExpression());
    }
    return decorators;
  }
  function parseDirectiveList() {
    const directives = [];
    while (token() === Token.Hash) {
      directives.push(parseDirectiveExpression());
    }
    return directives;
  }
  function parseNamespaceStatement(pos, decorators, docs, directives) {
    parseExpected(Token.NamespaceKeyword);
    let currentName = parseIdentifierOrMemberExpression();
    const nsSegments = [];
    while (currentName.kind !== SyntaxKind.Identifier) {
      nsSegments.push(currentName.id);
      currentName = currentName.base;
    }
    nsSegments.push(currentName);
    const nextTok = parseExpectedOneOf(Token.Semicolon, Token.OpenBrace);
    let statements;
    if (nextTok === Token.OpenBrace) {
      statements = parseStatementList();
      parseExpected(Token.CloseBrace);
    }
    let outerNs = {
      kind: SyntaxKind.NamespaceStatement,
      decorators,
      docs,
      id: nsSegments[0],
      locals: void 0,
      statements,
      directives,
      ...finishNode(pos)
    };
    for (let i = 1; i < nsSegments.length; i++) {
      outerNs = {
        kind: SyntaxKind.NamespaceStatement,
        decorators: [],
        directives: [],
        id: nsSegments[i],
        statements: outerNs,
        locals: void 0,
        ...finishNode(pos)
      };
    }
    return outerNs;
  }
  function parseInterfaceStatement(pos, decorators) {
    parseExpected(Token.InterfaceKeyword);
    const id = parseIdentifier();
    const { items: templateParameters, range: templateParametersRange } = parseTemplateParameterList();
    let extendList = createEmptyList();
    if (token() === Token.ExtendsKeyword) {
      nextToken();
      extendList = parseList(ListKind.Heritage, parseReferenceExpression);
    } else if (token() === Token.Identifier) {
      error({ code: "token-expected", format: { token: "'extends' or '{'" } });
      nextToken();
    }
    const { items: operations, range: bodyRange } = parseList(ListKind.InterfaceMembers, (pos2, decorators2) => parseOperationStatement(pos2, decorators2, true));
    return {
      kind: SyntaxKind.InterfaceStatement,
      id,
      templateParameters,
      templateParametersRange,
      operations,
      bodyRange,
      extends: extendList.items,
      decorators,
      ...finishNode(pos)
    };
  }
  function parseTemplateParameterList() {
    const detail = parseOptionalList(ListKind.TemplateParameters, parseTemplateParameter);
    let setDefault = false;
    for (const item of detail.items) {
      if (!item.default && setDefault) {
        error({ code: "default-required", target: item });
        continue;
      }
      if (item.default) {
        setDefault = true;
      }
    }
    return detail;
  }
  function parseUnionStatement(pos, decorators) {
    parseExpected(Token.UnionKeyword);
    const id = parseIdentifier();
    const { items: templateParameters, range: templateParametersRange } = parseTemplateParameterList();
    const { items: options2 } = parseList(ListKind.UnionVariants, parseUnionVariant);
    return {
      kind: SyntaxKind.UnionStatement,
      id,
      templateParameters,
      templateParametersRange,
      decorators,
      options: options2,
      ...finishNode(pos)
    };
  }
  function parseIdOrValueForVariant() {
    const nextToken2 = token();
    let id;
    if (isReservedKeyword(nextToken2)) {
      id = parseIdentifier({ allowReservedIdentifier: true });
      if (token() !== Token.Colon) {
        error({ code: "reserved-identifier", messageId: "future", format: { name: id.sv } });
      }
      return {
        kind: SyntaxKind.TypeReference,
        target: id,
        arguments: [],
        ...finishNode(id.pos)
      };
    } else {
      return parseExpression();
    }
  }
  function parseUnionVariant(pos, decorators) {
    const idOrExpr = parseIdOrValueForVariant();
    if (parseOptional(Token.Colon)) {
      let id = void 0;
      if (idOrExpr.kind !== SyntaxKind.TypeReference && idOrExpr.kind !== SyntaxKind.StringLiteral) {
        error({ code: "token-expected", messageId: "identifier" });
      } else if (idOrExpr.kind === SyntaxKind.StringLiteral) {
        id = {
          kind: SyntaxKind.Identifier,
          sv: idOrExpr.value,
          ...finishNode(idOrExpr.pos)
        };
      } else {
        const target = idOrExpr.target;
        if (target.kind === SyntaxKind.Identifier) {
          id = target;
        } else {
          error({ code: "token-expected", messageId: "identifier" });
        }
      }
      const value = parseExpression();
      return {
        kind: SyntaxKind.UnionVariant,
        id,
        value,
        decorators,
        ...finishNode(pos)
      };
    }
    return {
      kind: SyntaxKind.UnionVariant,
      id: void 0,
      value: idOrExpr,
      decorators,
      ...finishNode(pos)
    };
  }
  function parseUsingStatement(pos) {
    parseExpected(Token.UsingKeyword);
    const name = parseIdentifierOrMemberExpression();
    parseExpected(Token.Semicolon);
    return {
      kind: SyntaxKind.UsingStatement,
      name,
      ...finishNode(pos)
    };
  }
  function parseOperationStatement(pos, decorators, inInterface) {
    if (inInterface) {
      parseOptional(Token.OpKeyword);
    } else {
      parseExpected(Token.OpKeyword);
    }
    const id = parseIdentifier();
    const { items: templateParameters, range: templateParametersRange } = parseTemplateParameterList();
    const token2 = expectTokenIsOneOf(Token.OpenParen, Token.IsKeyword);
    let signature;
    const signaturePos = tokenPos();
    if (token2 === Token.OpenParen) {
      const parameters = parseOperationParameters();
      parseExpected(Token.Colon);
      const returnType = parseExpression();
      signature = {
        kind: SyntaxKind.OperationSignatureDeclaration,
        parameters,
        returnType,
        ...finishNode(signaturePos)
      };
    } else {
      parseExpected(Token.IsKeyword);
      const opReference = parseReferenceExpression();
      signature = {
        kind: SyntaxKind.OperationSignatureReference,
        baseOperation: opReference,
        ...finishNode(signaturePos)
      };
    }
    if (!inInterface) {
      parseExpected(Token.Semicolon);
    }
    return {
      kind: SyntaxKind.OperationStatement,
      id,
      templateParameters,
      templateParametersRange,
      signature,
      decorators,
      ...finishNode(pos)
    };
  }
  function parseOperationParameters() {
    const pos = tokenPos();
    const { items: properties, range: bodyRange } = parseList(ListKind.OperationParameters, parseModelPropertyOrSpread);
    const parameters = {
      kind: SyntaxKind.ModelExpression,
      properties,
      bodyRange,
      ...finishNode(pos)
    };
    return parameters;
  }
  function parseModelStatement(pos, decorators) {
    parseExpected(Token.ModelKeyword);
    const id = parseIdentifier();
    const { items: templateParameters, range: templateParametersRange } = parseTemplateParameterList();
    expectTokenIsOneOf(Token.OpenBrace, Token.Equals, Token.ExtendsKeyword, Token.IsKeyword);
    const optionalExtends = parseOptionalModelExtends();
    const optionalIs = optionalExtends ? void 0 : parseOptionalModelIs();
    let propDetail = createEmptyList();
    if (optionalIs) {
      const tok = expectTokenIsOneOf(Token.Semicolon, Token.OpenBrace);
      if (tok === Token.Semicolon) {
        nextToken();
      } else {
        propDetail = parseList(ListKind.ModelProperties, parseModelPropertyOrSpread);
      }
    } else {
      propDetail = parseList(ListKind.ModelProperties, parseModelPropertyOrSpread);
    }
    return {
      kind: SyntaxKind.ModelStatement,
      id,
      extends: optionalExtends,
      is: optionalIs,
      templateParameters,
      templateParametersRange,
      decorators,
      properties: propDetail.items,
      bodyRange: propDetail.range,
      ...finishNode(pos)
    };
  }
  function parseOptionalModelExtends() {
    if (parseOptional(Token.ExtendsKeyword)) {
      return parseExpression();
    }
    return void 0;
  }
  function parseOptionalModelIs() {
    if (parseOptional(Token.IsKeyword)) {
      return parseExpression();
    }
    return;
  }
  function parseTemplateParameter() {
    const pos = tokenPos();
    const id = parseIdentifier();
    let constraint;
    if (parseOptional(Token.ExtendsKeyword)) {
      constraint = parseMixedParameterConstraint();
    }
    let def;
    if (parseOptional(Token.Equals)) {
      def = parseExpression();
    }
    return {
      kind: SyntaxKind.TemplateParameterDeclaration,
      id,
      constraint,
      default: def,
      ...finishNode(pos)
    };
  }
  function parseValueOfExpressionOrIntersectionOrHigher() {
    if (token() === Token.ValueOfKeyword) {
      return parseValueOfExpression();
    } else if (parseOptional(Token.OpenParen)) {
      const expr = parseMixedParameterConstraint();
      parseExpected(Token.CloseParen);
      return expr;
    }
    return parseIntersectionExpressionOrHigher();
  }
  function parseMixedParameterConstraint() {
    const pos = tokenPos();
    parseOptional(Token.Bar);
    const node = parseValueOfExpressionOrIntersectionOrHigher();
    if (token() !== Token.Bar) {
      return node;
    }
    const options2 = [node];
    while (parseOptional(Token.Bar)) {
      const expr = parseValueOfExpressionOrIntersectionOrHigher();
      options2.push(expr);
    }
    return {
      kind: SyntaxKind.UnionExpression,
      options: options2,
      ...finishNode(pos)
    };
  }
  function parseModelPropertyOrSpread(pos, decorators) {
    return token() === Token.Ellipsis ? parseModelSpreadProperty(pos, decorators) : parseModelProperty(pos, decorators);
  }
  function parseModelSpreadProperty(pos, decorators) {
    parseExpected(Token.Ellipsis);
    reportInvalidDecorators(decorators, "spread property");
    const target = parseReferenceExpression();
    return {
      kind: SyntaxKind.ModelSpreadProperty,
      target,
      ...finishNode(pos)
    };
  }
  function parseModelProperty(pos, decorators) {
    const id = parseIdentifier({
      message: "property",
      allowStringLiteral: true,
      allowReservedIdentifier: true
    });
    const optional = parseOptional(Token.Question);
    parseExpected(Token.Colon);
    const value = parseExpression();
    const hasDefault = parseOptional(Token.Equals);
    const defaultValue = hasDefault ? parseExpression() : void 0;
    return {
      kind: SyntaxKind.ModelProperty,
      id,
      decorators,
      value,
      optional,
      default: defaultValue,
      ...finishNode(pos)
    };
  }
  function parseObjectLiteralPropertyOrSpread(pos, decorators) {
    reportInvalidDecorators(decorators, "object literal property");
    return token() === Token.Ellipsis ? parseObjectLiteralSpreadProperty(pos) : parseObjectLiteralProperty(pos);
  }
  function parseObjectLiteralSpreadProperty(pos) {
    parseExpected(Token.Ellipsis);
    const target = parseReferenceExpression();
    return {
      kind: SyntaxKind.ObjectLiteralSpreadProperty,
      target,
      ...finishNode(pos)
    };
  }
  function parseObjectLiteralProperty(pos) {
    const id = parseIdentifier({
      message: "property",
      allowReservedIdentifier: true
    });
    parseExpected(Token.Colon);
    const value = parseExpression();
    return {
      kind: SyntaxKind.ObjectLiteralProperty,
      id,
      value,
      ...finishNode(pos)
    };
  }
  function parseScalarStatement(pos, decorators) {
    parseExpected(Token.ScalarKeyword);
    const id = parseIdentifier();
    const { items: templateParameters, range: templateParametersRange } = parseTemplateParameterList();
    const optionalExtends = parseOptionalScalarExtends();
    const { items: members, range: bodyRange } = parseScalarMembers();
    return {
      kind: SyntaxKind.ScalarStatement,
      id,
      templateParameters,
      templateParametersRange,
      extends: optionalExtends,
      members,
      bodyRange,
      decorators,
      ...finishNode(pos)
    };
  }
  function parseOptionalScalarExtends() {
    if (parseOptional(Token.ExtendsKeyword)) {
      return parseReferenceExpression();
    }
    return void 0;
  }
  function parseScalarMembers() {
    if (token() === Token.Semicolon) {
      nextToken();
      return createEmptyList();
    } else {
      return parseList(ListKind.ScalarMembers, parseScalarMember);
    }
  }
  function parseScalarMember(pos, decorators) {
    reportInvalidDecorators(decorators, "scalar member");
    parseExpected(Token.InitKeyword);
    const id = parseIdentifier();
    const { items: parameters } = parseFunctionParameters();
    return {
      kind: SyntaxKind.ScalarConstructor,
      id,
      parameters,
      ...finishNode(pos)
    };
  }
  function parseEnumStatement(pos, decorators) {
    parseExpected(Token.EnumKeyword);
    const id = parseIdentifier();
    const { items: members } = parseList(ListKind.EnumMembers, parseEnumMemberOrSpread);
    return {
      kind: SyntaxKind.EnumStatement,
      id,
      decorators,
      members,
      ...finishNode(pos)
    };
  }
  function parseEnumMemberOrSpread(pos, decorators) {
    return token() === Token.Ellipsis ? parseEnumSpreadMember(pos, decorators) : parseEnumMember(pos, decorators);
  }
  function parseEnumSpreadMember(pos, decorators) {
    parseExpected(Token.Ellipsis);
    reportInvalidDecorators(decorators, "spread enum");
    const target = parseReferenceExpression();
    return {
      kind: SyntaxKind.EnumSpreadMember,
      target,
      ...finishNode(pos)
    };
  }
  function parseEnumMember(pos, decorators) {
    const id = parseIdentifier({
      message: "enumMember",
      allowStringLiteral: true,
      allowReservedIdentifier: true
    });
    let value;
    if (parseOptional(Token.Colon)) {
      const expr = parseExpression();
      if (expr.kind === SyntaxKind.StringLiteral || expr.kind === SyntaxKind.NumericLiteral) {
        value = expr;
      } else if (expr.kind === SyntaxKind.TypeReference && expr.target.flags & 2) {
        parseErrorInNextFinishedNode = true;
      } else {
        error({ code: "token-expected", messageId: "numericOrStringLiteral", target: expr });
      }
    }
    return {
      kind: SyntaxKind.EnumMember,
      id,
      value,
      decorators,
      ...finishNode(pos)
    };
  }
  function parseAliasStatement(pos) {
    parseExpected(Token.AliasKeyword);
    const id = parseIdentifier();
    const { items: templateParameters, range: templateParametersRange } = parseTemplateParameterList();
    parseExpected(Token.Equals);
    const value = parseExpression();
    parseExpected(Token.Semicolon);
    return {
      kind: SyntaxKind.AliasStatement,
      id,
      templateParameters,
      templateParametersRange,
      value,
      ...finishNode(pos)
    };
  }
  function parseConstStatement(pos) {
    parseExpected(Token.ConstKeyword);
    const id = parseIdentifier();
    const type = parseOptionalTypeAnnotation();
    parseExpected(Token.Equals);
    const value = parseExpression();
    parseExpected(Token.Semicolon);
    return {
      kind: SyntaxKind.ConstStatement,
      id,
      value,
      type,
      ...finishNode(pos)
    };
  }
  function parseOptionalTypeAnnotation() {
    if (parseOptional(Token.Colon)) {
      return parseExpression();
    }
    return void 0;
  }
  function parseExpression() {
    return parseUnionExpressionOrHigher();
  }
  function parseUnionExpressionOrHigher() {
    const pos = tokenPos();
    parseOptional(Token.Bar);
    const node = parseIntersectionExpressionOrHigher();
    if (token() !== Token.Bar) {
      return node;
    }
    const options2 = [node];
    while (parseOptional(Token.Bar)) {
      const expr = parseIntersectionExpressionOrHigher();
      options2.push(expr);
    }
    return {
      kind: SyntaxKind.UnionExpression,
      options: options2,
      ...finishNode(pos)
    };
  }
  function parseIntersectionExpressionOrHigher() {
    const pos = tokenPos();
    parseOptional(Token.Ampersand);
    const node = parseArrayExpressionOrHigher();
    if (token() !== Token.Ampersand) {
      return node;
    }
    const options2 = [node];
    while (parseOptional(Token.Ampersand)) {
      const expr = parseArrayExpressionOrHigher();
      options2.push(expr);
    }
    return {
      kind: SyntaxKind.IntersectionExpression,
      options: options2,
      ...finishNode(pos)
    };
  }
  function parseArrayExpressionOrHigher() {
    const pos = tokenPos();
    let expr = parsePrimaryExpression();
    while (parseOptional(Token.OpenBracket)) {
      parseExpected(Token.CloseBracket);
      expr = {
        kind: SyntaxKind.ArrayExpression,
        elementType: expr,
        ...finishNode(pos)
      };
    }
    return expr;
  }
  function parseStandaloneReferenceExpression() {
    const expr = parseReferenceExpression();
    if (parseDiagnostics.length === 0 && token() !== Token.EndOfFile) {
      error({ code: "token-expected", messageId: "unexpected", format: { token: Token[token()] } });
    }
    return expr;
  }
  function parseValueOfExpression() {
    const pos = tokenPos();
    parseExpected(Token.ValueOfKeyword);
    const target = parseExpression();
    return {
      kind: SyntaxKind.ValueOfExpression,
      target,
      ...finishNode(pos)
    };
  }
  function parseTypeOfExpression() {
    const pos = tokenPos();
    parseExpected(Token.TypeOfKeyword);
    const target = parseTypeOfTarget();
    return {
      kind: SyntaxKind.TypeOfExpression,
      target,
      ...finishNode(pos)
    };
  }
  function parseTypeOfTarget() {
    while (true) {
      switch (token()) {
        case Token.TypeOfKeyword:
          return parseTypeOfExpression();
        case Token.Identifier:
          return parseCallOrReferenceExpression();
        case Token.StringLiteral:
          return parseStringLiteral();
        case Token.StringTemplateHead:
          return parseStringTemplateExpression();
        case Token.TrueKeyword:
        case Token.FalseKeyword:
          return parseBooleanLiteral();
        case Token.NumericLiteral:
          return parseNumericLiteral();
        case Token.OpenParen:
          parseExpected(Token.OpenParen);
          const target = parseTypeOfTarget();
          parseExpected(Token.CloseParen);
          return target;
        default:
          return parseReferenceExpression("typeofTarget");
      }
    }
  }
  function parseReferenceExpression(message) {
    const pos = tokenPos();
    const target = parseIdentifierOrMemberExpression({
      message,
      allowReservedIdentifierInMember: true
    });
    return parseReferenceExpressionInternal(target, pos);
  }
  function parseCallOrReferenceExpression(message) {
    const pos = tokenPos();
    const target = parseIdentifierOrMemberExpression({
      message,
      allowReservedIdentifierInMember: true
    });
    if (token() === Token.OpenParen) {
      const { items: args } = parseList(ListKind.FunctionArguments, parseExpression);
      return {
        kind: SyntaxKind.CallExpression,
        target,
        arguments: args,
        ...finishNode(pos)
      };
    }
    return parseReferenceExpressionInternal(target, pos);
  }
  function parseReferenceExpressionInternal(target, pos) {
    const { items: args } = parseOptionalList(ListKind.TemplateArguments, parseTemplateArgument);
    return {
      kind: SyntaxKind.TypeReference,
      target,
      arguments: args,
      ...finishNode(pos)
    };
  }
  function parseTemplateArgument() {
    const pos = tokenPos();
    if (token() === Token.Equals) {
      error({ code: "token-expected", messageId: "identifier" });
      nextToken();
      return {
        kind: SyntaxKind.TemplateArgument,
        name: createMissingIdentifier(),
        argument: parseExpression(),
        ...finishNode(pos)
      };
    }
    const expr = parseExpression();
    const eq = parseOptional(Token.Equals);
    if (eq) {
      const isBareIdentifier = exprIsBareIdentifier(expr);
      if (!isBareIdentifier) {
        error({ code: "invalid-template-argument-name", target: expr });
      }
      return {
        kind: SyntaxKind.TemplateArgument,
        name: isBareIdentifier ? expr.target : createMissingIdentifier(),
        argument: parseExpression(),
        ...finishNode(pos)
      };
    } else {
      return {
        kind: SyntaxKind.TemplateArgument,
        argument: expr,
        ...finishNode(pos)
      };
    }
  }
  function parseAugmentDecorator() {
    const pos = tokenPos();
    parseExpected(Token.AtAt);
    const target = parseIdentifierOrMemberExpression({
      allowReservedIdentifier: true,
      allowReservedIdentifierInMember: true
    });
    const { items: args } = parseOptionalList(ListKind.DecoratorArguments, parseExpression);
    if (args.length === 0) {
      error({ code: "augment-decorator-target" });
      const emptyList = createEmptyList();
      return {
        kind: SyntaxKind.AugmentDecoratorStatement,
        target,
        targetType: {
          kind: SyntaxKind.TypeReference,
          target: createMissingIdentifier(),
          arguments: emptyList.items,
          ...finishNode(pos)
        },
        arguments: args,
        ...finishNode(pos)
      };
    }
    let [targetEntity, ...decoratorArgs] = args;
    if (targetEntity.kind !== SyntaxKind.TypeReference) {
      error({ code: "augment-decorator-target", target: targetEntity });
      const emptyList = createEmptyList();
      targetEntity = {
        kind: SyntaxKind.TypeReference,
        target: createMissingIdentifier(),
        arguments: emptyList.items,
        ...finishNode(pos)
      };
    }
    parseExpected(Token.Semicolon);
    return {
      kind: SyntaxKind.AugmentDecoratorStatement,
      target,
      targetType: targetEntity,
      arguments: decoratorArgs,
      ...finishNode(pos)
    };
  }
  function parseImportStatement() {
    const pos = tokenPos();
    parseExpected(Token.ImportKeyword);
    const path = parseStringLiteral();
    parseExpected(Token.Semicolon);
    return {
      kind: SyntaxKind.ImportStatement,
      path,
      ...finishNode(pos)
    };
  }
  function parseDecoratorExpression() {
    const pos = tokenPos();
    parseExpected(Token.At);
    const target = parseIdentifierOrMemberExpression({
      allowReservedIdentifier: true,
      allowReservedIdentifierInMember: true
    });
    const { items: args } = parseOptionalList(ListKind.DecoratorArguments, parseExpression);
    return {
      kind: SyntaxKind.DecoratorExpression,
      arguments: args,
      target,
      ...finishNode(pos)
    };
  }
  function parseDirectiveExpression() {
    const pos = tokenPos();
    parseExpected(Token.Hash);
    const target = parseIdentifier();
    if (target.sv !== "suppress" && target.sv !== "deprecated") {
      error({
        code: "unknown-directive",
        format: { id: target.sv },
        target: { pos, end: pos + target.sv.length },
        printable: true
      });
    }
    newLineIsTrivia = false;
    const args = [];
    while (token() !== Token.NewLine && token() !== Token.EndOfFile) {
      const param = parseDirectiveParameter();
      if (param) {
        args.push(param);
      }
    }
    newLineIsTrivia = true;
    nextToken();
    return {
      kind: SyntaxKind.DirectiveExpression,
      arguments: args,
      target,
      ...finishNode(pos)
    };
  }
  function parseDirectiveParameter() {
    switch (token()) {
      case Token.Identifier:
        return parseIdentifier();
      case Token.StringLiteral:
        return parseStringLiteral();
      default:
        error({
          code: "token-expected",
          messageId: "unexpected",
          format: { token: Token[token()] }
        });
        do {
          nextToken();
        } while (!isStatementKeyword(token()) && token() !== Token.NewLine && token() !== Token.At && token() !== Token.Semicolon && token() !== Token.EndOfFile);
        return void 0;
    }
  }
  function parseIdentifierOrMemberExpression(options2) {
    const pos = tokenPos();
    let base = parseIdentifier({
      message: options2?.message,
      allowReservedIdentifier: options2?.allowReservedIdentifier
    });
    while (token() !== Token.EndOfFile) {
      if (parseOptional(Token.Dot)) {
        base = {
          kind: SyntaxKind.MemberExpression,
          base,
          // Error recovery: false arg here means don't treat a keyword as an
          // identifier after `.` in member expression. Otherwise we will
          // parse `@Outer.<missing identifier> model M{}` as having decorator
          // `@Outer.model` applied to invalid statement `M {}` instead of
          // having incomplete decorator `@Outer.` applied to `model M {}`.
          id: parseIdentifier({
            allowReservedIdentifier: options2?.allowReservedIdentifierInMember
          }),
          selector: ".",
          ...finishNode(pos)
        };
      } else if (parseOptional(Token.ColonColon)) {
        base = {
          kind: SyntaxKind.MemberExpression,
          base,
          id: parseIdentifier(),
          selector: "::",
          ...finishNode(pos)
        };
      } else {
        break;
      }
    }
    return base;
  }
  function parsePrimaryExpression() {
    while (true) {
      switch (token()) {
        case Token.TypeOfKeyword:
          return parseTypeOfExpression();
        case Token.Identifier:
          return parseCallOrReferenceExpression();
        case Token.StringLiteral:
          return parseStringLiteral();
        case Token.StringTemplateHead:
          return parseStringTemplateExpression();
        case Token.TrueKeyword:
        case Token.FalseKeyword:
          return parseBooleanLiteral();
        case Token.NumericLiteral:
          return parseNumericLiteral();
        case Token.OpenBrace:
          return parseModelExpression();
        case Token.OpenBracket:
          return parseTupleExpression();
        case Token.OpenParen:
          return parseParenthesizedExpression();
        case Token.At:
          const decorators = parseDecoratorList();
          reportInvalidDecorators(decorators, "expression");
          continue;
        case Token.Hash:
          const directives = parseDirectiveList();
          reportInvalidDirective(directives, "expression");
          continue;
        case Token.HashBrace:
          return parseObjectLiteral();
        case Token.HashBracket:
          return parseArrayLiteral();
        case Token.VoidKeyword:
          return parseVoidKeyword();
        case Token.NeverKeyword:
          return parseNeverKeyword();
        case Token.UnknownKeyword:
          return parseUnknownKeyword();
        default:
          return parseReferenceExpression("expression");
      }
    }
  }
  function parseExternKeyword() {
    const pos = tokenPos();
    parseExpected(Token.ExternKeyword);
    return {
      kind: SyntaxKind.ExternKeyword,
      ...finishNode(pos)
    };
  }
  function parseVoidKeyword() {
    const pos = tokenPos();
    parseExpected(Token.VoidKeyword);
    return {
      kind: SyntaxKind.VoidKeyword,
      ...finishNode(pos)
    };
  }
  function parseNeverKeyword() {
    const pos = tokenPos();
    parseExpected(Token.NeverKeyword);
    return {
      kind: SyntaxKind.NeverKeyword,
      ...finishNode(pos)
    };
  }
  function parseUnknownKeyword() {
    const pos = tokenPos();
    parseExpected(Token.UnknownKeyword);
    return {
      kind: SyntaxKind.UnknownKeyword,
      ...finishNode(pos)
    };
  }
  function parseParenthesizedExpression() {
    const pos = tokenPos();
    parseExpected(Token.OpenParen);
    const expr = parseExpression();
    parseExpected(Token.CloseParen);
    return { ...expr, ...finishNode(pos) };
  }
  function parseTupleExpression() {
    const pos = tokenPos();
    const { items: values } = parseList(ListKind.Tuple, parseExpression);
    return {
      kind: SyntaxKind.TupleExpression,
      values,
      ...finishNode(pos)
    };
  }
  function parseModelExpression() {
    const pos = tokenPos();
    const { items: properties, range: bodyRange } = parseList(ListKind.ModelProperties, parseModelPropertyOrSpread);
    return {
      kind: SyntaxKind.ModelExpression,
      properties,
      bodyRange,
      ...finishNode(pos)
    };
  }
  function parseObjectLiteral() {
    const pos = tokenPos();
    const { items: properties, range: bodyRange } = parseList(ListKind.ObjectLiteralProperties, parseObjectLiteralPropertyOrSpread);
    return {
      kind: SyntaxKind.ObjectLiteral,
      properties,
      bodyRange,
      ...finishNode(pos)
    };
  }
  function parseArrayLiteral() {
    const pos = tokenPos();
    const { items: values } = parseList(ListKind.ArrayLiteral, parseExpression);
    return {
      kind: SyntaxKind.ArrayLiteral,
      values,
      ...finishNode(pos)
    };
  }
  function parseStringLiteral() {
    const pos = tokenPos();
    const value = tokenValue();
    parseExpected(Token.StringLiteral);
    return {
      kind: SyntaxKind.StringLiteral,
      value,
      ...finishNode(pos)
    };
  }
  function parseStringTemplateExpression() {
    const pos = tokenPos();
    const head = parseStringTemplateHead();
    const spans = parseStringTemplateSpans(head.tokenFlags);
    const last = spans[spans.length - 1];
    if (head.tokenFlags & TokenFlags.TripleQuoted) {
      const [indentationsStart, indentationEnd] = scanner.findTripleQuotedStringIndent(last.literal.pos, last.literal.end);
      mutate(head).value = scanner.unindentAndUnescapeTripleQuotedString(head.pos, head.end, indentationsStart, indentationEnd, Token.StringTemplateHead, head.tokenFlags);
      for (const span of spans) {
        mutate(span.literal).value = scanner.unindentAndUnescapeTripleQuotedString(span.literal.pos, span.literal.end, indentationsStart, indentationEnd, span === last ? Token.StringTemplateTail : Token.StringTemplateMiddle, head.tokenFlags);
      }
    }
    return {
      kind: SyntaxKind.StringTemplateExpression,
      head,
      spans,
      ...finishNode(pos)
    };
  }
  function parseStringTemplateHead() {
    const pos = tokenPos();
    const flags = tokenFlags();
    const text = flags & TokenFlags.TripleQuoted ? "" : tokenValue();
    parseExpected(Token.StringTemplateHead);
    return {
      kind: SyntaxKind.StringTemplateHead,
      value: text,
      tokenFlags: flags,
      ...finishNode(pos)
    };
  }
  function parseStringTemplateSpans(tokenFlags2) {
    const list = [];
    let node;
    do {
      node = parseTemplateTypeSpan(tokenFlags2);
      list.push(node);
    } while (node.literal.kind === SyntaxKind.StringTemplateMiddle);
    return list;
  }
  function parseTemplateTypeSpan(tokenFlags2) {
    const pos = tokenPos();
    const expression = parseExpression();
    const literal = parseLiteralOfTemplateSpan(tokenFlags2);
    return {
      kind: SyntaxKind.StringTemplateSpan,
      literal,
      expression,
      ...finishNode(pos)
    };
  }
  function parseLiteralOfTemplateSpan(headTokenFlags) {
    const pos = tokenPos();
    const flags = tokenFlags();
    const text = flags & TokenFlags.TripleQuoted ? "" : tokenValue();
    if (token() === Token.CloseBrace) {
      nextStringTemplateToken(headTokenFlags);
      return parseTemplateMiddleOrTemplateTail();
    } else {
      parseExpected(Token.StringTemplateTail);
      return {
        kind: SyntaxKind.StringTemplateTail,
        value: text,
        tokenFlags: flags,
        ...finishNode(pos)
      };
    }
  }
  function parseTemplateMiddleOrTemplateTail() {
    const pos = tokenPos();
    const flags = tokenFlags();
    const text = flags & TokenFlags.TripleQuoted ? "" : tokenValue();
    const kind = token() === Token.StringTemplateMiddle ? SyntaxKind.StringTemplateMiddle : SyntaxKind.StringTemplateTail;
    nextToken();
    return {
      kind,
      value: text,
      tokenFlags: flags,
      ...finishNode(pos)
    };
  }
  function parseNumericLiteral() {
    const pos = tokenPos();
    const valueAsString = tokenValue();
    const value = Number(valueAsString);
    parseExpected(Token.NumericLiteral);
    return {
      kind: SyntaxKind.NumericLiteral,
      value,
      valueAsString,
      ...finishNode(pos)
    };
  }
  function parseBooleanLiteral() {
    const pos = tokenPos();
    const token2 = parseExpectedOneOf(Token.TrueKeyword, Token.FalseKeyword);
    const value = token2 === Token.TrueKeyword;
    return {
      kind: SyntaxKind.BooleanLiteral,
      value,
      ...finishNode(pos)
    };
  }
  function parseIdentifier(options2) {
    if (isKeyword(token())) {
      error({ code: "reserved-identifier" });
      return createMissingIdentifier();
    } else if (isReservedKeyword(token())) {
      if (!options2?.allowReservedIdentifier) {
        error({ code: "reserved-identifier", messageId: "future", format: { name: tokenValue() } });
      }
    } else if (token() !== Token.Identifier && (!options2?.allowStringLiteral || token() !== Token.StringLiteral)) {
      error({ code: "token-expected", messageId: options2?.message ?? "identifier" });
      return createMissingIdentifier();
    }
    const pos = tokenPos();
    const sv = tokenValue();
    nextToken();
    return {
      kind: SyntaxKind.Identifier,
      sv,
      ...finishNode(pos)
    };
  }
  function parseDeclaration(pos) {
    const modifiers = parseModifiers();
    switch (token()) {
      case Token.DecKeyword:
        return parseDecoratorDeclarationStatement(pos, modifiers);
      case Token.FnKeyword:
        return parseFunctionDeclarationStatement(pos, modifiers);
    }
    return parseInvalidStatement(pos, []);
  }
  function parseModifiers() {
    const modifiers = [];
    let modifier;
    while (modifier = parseModifier()) {
      modifiers.push(modifier);
    }
    return modifiers;
  }
  function parseModifier() {
    switch (token()) {
      case Token.ExternKeyword:
        return parseExternKeyword();
      default:
        return void 0;
    }
  }
  function parseDecoratorDeclarationStatement(pos, modifiers) {
    const modifierFlags = modifiersToFlags(modifiers);
    parseExpected(Token.DecKeyword);
    const id = parseIdentifier();
    const allParamListDetail = parseFunctionParameters();
    let [target, ...parameters] = allParamListDetail.items;
    if (target === void 0) {
      error({ code: "decorator-decl-target", target: { pos, end: previousTokenEnd } });
      target = {
        kind: SyntaxKind.FunctionParameter,
        id: createMissingIdentifier(),
        type: createMissingTypeReference(),
        optional: false,
        rest: false,
        ...finishNode(pos)
      };
    }
    if (target.optional) {
      error({ code: "decorator-decl-target", messageId: "required" });
    }
    parseExpected(Token.Semicolon);
    return {
      kind: SyntaxKind.DecoratorDeclarationStatement,
      modifiers,
      modifierFlags,
      id,
      target,
      parameters,
      ...finishNode(pos)
    };
  }
  function parseFunctionDeclarationStatement(pos, modifiers) {
    const modifierFlags = modifiersToFlags(modifiers);
    parseExpected(Token.FnKeyword);
    const id = parseIdentifier();
    const { items: parameters } = parseFunctionParameters();
    let returnType;
    if (parseOptional(Token.Colon)) {
      returnType = parseExpression();
    }
    parseExpected(Token.Semicolon);
    return {
      kind: SyntaxKind.FunctionDeclarationStatement,
      modifiers,
      modifierFlags,
      id,
      parameters,
      returnType,
      ...finishNode(pos)
    };
  }
  function parseFunctionParameters() {
    const parameters = parseList(ListKind.FunctionParameters, parseFunctionParameter);
    let foundOptional = false;
    for (const [index, item] of parameters.items.entries()) {
      if (!item.optional && foundOptional) {
        error({ code: "required-parameter-first", target: item });
        continue;
      }
      if (item.optional) {
        foundOptional = true;
      }
      if (item.rest && item.optional) {
        error({ code: "rest-parameter-required", target: item });
      }
      if (item.rest && index !== parameters.items.length - 1) {
        error({ code: "rest-parameter-last", target: item });
      }
    }
    return parameters;
  }
  function parseFunctionParameter() {
    const pos = tokenPos();
    const rest = parseOptional(Token.Ellipsis);
    const id = parseIdentifier({ message: "property", allowReservedIdentifier: true });
    const optional = parseOptional(Token.Question);
    let type;
    if (parseOptional(Token.Colon)) {
      type = parseMixedParameterConstraint();
    }
    return {
      kind: SyntaxKind.FunctionParameter,
      id,
      type,
      optional,
      rest,
      ...finishNode(pos)
    };
  }
  function modifiersToFlags(modifiers) {
    let flags = 0;
    for (const modifier of modifiers) {
      switch (modifier.kind) {
        case SyntaxKind.ExternKeyword:
          flags |= 2;
          break;
      }
    }
    return flags;
  }
  function parseRange(mode, range, callback) {
    const savedMode = currentMode;
    const result = scanner.scanRange(range, () => {
      currentMode = mode;
      nextToken();
      return callback();
    });
    currentMode = savedMode;
    return result;
  }
  function innerDocRange(range) {
    return {
      pos: range.pos + 3,
      end: tokenFlags() & TokenFlags.Unterminated ? range.end : range.end - 2
    };
  }
  function parseDocList() {
    if (docRanges.length === 0 || options.docs === false) {
      return [tokenPos(), []];
    }
    const docs = [];
    for (const range of docRanges) {
      const doc = parseRange(1, innerDocRange(range), () => parseDoc(range));
      docs.push(doc);
      if (range.comment) {
        mutate(range.comment).parsedAsDocs = true;
      }
    }
    return [docRanges[0].pos, docs];
  }
  function parseDoc(range) {
    const content = [];
    const tags = [];
    loop: while (true) {
      switch (token()) {
        case Token.EndOfFile:
          break loop;
        case Token.At:
          const tag = parseDocTag();
          tags.push(tag);
          break;
        default:
          content.push(...parseDocContent());
          break;
      }
    }
    return {
      kind: SyntaxKind.Doc,
      content,
      tags,
      ...finishNode(range.pos),
      end: range.end
    };
  }
  function parseDocContent() {
    const parts = [];
    const source = scanner.file.text;
    const pos = tokenPos();
    let start = pos;
    let inCodeFence = false;
    loop: while (true) {
      switch (token()) {
        case Token.DocCodeFenceDelimiter:
          inCodeFence = !inCodeFence;
          nextToken();
          break;
        case Token.NewLine:
          parts.push(source.substring(start, tokenPos()));
          parts.push("\n");
          nextToken();
          start = tokenPos();
          while (parseOptional(Token.Whitespace))
            ;
          if (!parseOptional(Token.Star)) {
            break;
          }
          if (!inCodeFence) {
            parseOptional(Token.Whitespace);
            start = tokenPos();
            break;
          }
          const whitespaceStart = tokenPos();
          parseOptional(Token.Whitespace);
          start = Math.min(whitespaceStart + 1, tokenPos());
          break;
        case Token.EndOfFile:
          break loop;
        case Token.At:
          if (!inCodeFence) {
            break loop;
          }
          nextToken();
          break;
        case Token.DocText:
          parts.push(source.substring(start, tokenPos()));
          parts.push(tokenValue());
          nextToken();
          start = tokenPos();
          break;
        default:
          nextToken();
          break;
      }
    }
    parts.push(source.substring(start, tokenPos()));
    const text = trim(parts.join(""));
    return [
      {
        kind: SyntaxKind.DocText,
        text,
        ...finishNode(pos)
      }
    ];
  }
  function parseDocTag() {
    const pos = tokenPos();
    parseExpected(Token.At);
    const tagName = parseDocIdentifier("tag");
    switch (tagName.sv) {
      case "param":
        return parseDocParamLikeTag(pos, tagName, SyntaxKind.DocParamTag, "param");
      case "template":
        return parseDocParamLikeTag(pos, tagName, SyntaxKind.DocTemplateTag, "templateParam");
      case "prop":
        return parseDocPropTag(pos, tagName);
      case "return":
      case "returns":
        return parseDocSimpleTag(pos, tagName, SyntaxKind.DocReturnsTag);
      case "errors":
        return parseDocSimpleTag(pos, tagName, SyntaxKind.DocErrorsTag);
      default:
        return parseDocSimpleTag(pos, tagName, SyntaxKind.DocUnknownTag);
    }
  }
  function parseDocParamLikeTag(pos, tagName, kind, messageId) {
    const { name, content } = parseDocParamLikeTagInternal(messageId);
    return {
      kind,
      tagName,
      paramName: name,
      content,
      ...finishNode(pos)
    };
  }
  function parseDocPropTag(pos, tagName) {
    const { name, content } = parseDocParamLikeTagInternal("prop");
    return {
      kind: SyntaxKind.DocPropTag,
      tagName,
      propName: name,
      content,
      ...finishNode(pos)
    };
  }
  function parseDocParamLikeTagInternal(messageId) {
    const name = parseDocIdentifier(messageId);
    parseOptionalHyphenDocParamLikeTag();
    const content = parseDocContent();
    return { name, content };
  }
  function parseOptionalHyphenDocParamLikeTag() {
    while (parseOptional(Token.Whitespace))
      ;
    if (parseOptional(Token.Hyphen)) {
      while (parseOptional(Token.Whitespace))
        ;
    }
  }
  function parseDocSimpleTag(pos, tagName, kind) {
    const content = parseDocContent();
    return {
      kind,
      tagName,
      content,
      ...finishNode(pos)
    };
  }
  function parseDocIdentifier(messageId) {
    if (messageId !== "tag") {
      while (parseOptional(Token.Whitespace))
        ;
    }
    const pos = tokenPos();
    let sv;
    if (token() === Token.Identifier) {
      sv = tokenValue();
      nextToken();
    } else {
      sv = "";
      warning({ code: "doc-invalid-identifier", messageId });
    }
    return {
      kind: SyntaxKind.Identifier,
      sv,
      ...finishNode(pos)
    };
  }
  function token() {
    return scanner.token;
  }
  function tokenFlags() {
    return scanner.tokenFlags;
  }
  function tokenValue() {
    return scanner.getTokenValue();
  }
  function tokenPos() {
    return scanner.tokenPosition;
  }
  function tokenEnd() {
    return scanner.position;
  }
  function nextToken() {
    previousTokenEnd = scanner.position;
    return currentMode === 0 ? nextSyntaxToken() : nextDocToken();
  }
  function nextSyntaxToken() {
    docRanges = [];
    for (; ; ) {
      scanner.scan();
      if (isTrivia(token())) {
        if (!newLineIsTrivia && token() === Token.NewLine) {
          break;
        }
        let comment = void 0;
        if (options.comments && isComment(token())) {
          comment = {
            kind: token() === Token.SingleLineComment ? SyntaxKind.LineComment : SyntaxKind.BlockComment,
            pos: tokenPos(),
            end: tokenEnd()
          };
          comments.push(comment);
        }
        if (tokenFlags() & TokenFlags.DocComment) {
          docRanges.push({
            pos: tokenPos(),
            end: tokenEnd(),
            comment
          });
        }
      } else {
        break;
      }
    }
  }
  function nextDocToken() {
    scanner.scanDoc();
  }
  function nextStringTemplateToken(tokenFlags2) {
    scanner.reScanStringTemplate(tokenFlags2);
  }
  function createMissingIdentifier() {
    const pos = tokenPos();
    previousTokenEnd = pos;
    missingIdentifierCounter++;
    return {
      kind: SyntaxKind.Identifier,
      sv: "<missing identifier>" + missingIdentifierCounter,
      ...finishNode(pos)
    };
  }
  function createMissingTypeReference() {
    const pos = tokenPos();
    const { items: args } = createEmptyList();
    return {
      kind: SyntaxKind.TypeReference,
      target: createMissingIdentifier(),
      arguments: args,
      ...finishNode(pos)
    };
  }
  function finishNode(pos) {
    const flags = parseErrorInNextFinishedNode ? 2 : 0;
    parseErrorInNextFinishedNode = false;
    return withSymbol({ pos, end: previousTokenEnd, flags });
  }
  function withSymbol(obj) {
    return obj;
  }
  function createEmptyList(range = { pos: -1, end: -1 }) {
    return {
      items: [],
      range
    };
  }
  function parseList(kind, parseItem) {
    const r = createEmptyList();
    if (kind.open !== Token.None) {
      const t = tokenPos();
      if (parseExpected(kind.open)) {
        mutate(r.range).pos = t;
      }
    }
    if (kind.allowEmpty && parseOptional(kind.close)) {
      mutate(r.range).end = previousTokenEnd;
      return r;
    }
    while (true) {
      const startingPos = tokenPos();
      const { pos, docs, directives, decorators } = parseAnnotations({
        skipParsingDocNodes: Boolean(kind.invalidAnnotationTarget)
      });
      if (kind.invalidAnnotationTarget) {
        reportInvalidDecorators(decorators, kind.invalidAnnotationTarget);
        reportInvalidDirective(directives, kind.invalidAnnotationTarget);
      }
      if (directives.length === 0 && decorators.length === 0 && atEndOfListWithError(kind)) {
        if (parseExpected(kind.close)) {
          mutate(r.range).end = previousTokenEnd;
        }
        break;
      }
      let item;
      if (kind.invalidAnnotationTarget) {
        item = parseItem();
      } else {
        item = parseItem(pos, decorators);
        mutate(item).docs = docs;
        mutate(item).directives = directives;
      }
      r.items.push(item);
      if (parseOptionalDelimiter(kind)) {
        if (parseOptional(kind.close)) {
          mutate(r.range).end = previousTokenEnd;
          break;
        }
        continue;
      } else if (kind.close === Token.None) {
        break;
      } else if (parseOptional(kind.close)) {
        mutate(r.range).end = previousTokenEnd;
        break;
      } else if (atEndOfListWithError(kind)) {
        if (parseExpected(kind.close)) {
          mutate(r.range).end = previousTokenEnd;
        }
        break;
      } else {
        parseExpected(kind.delimiter);
      }
      if (startingPos === tokenPos()) {
        if (parseExpected(kind.close)) {
          mutate(r.range).end = previousTokenEnd;
        }
        nextToken();
        r.items.pop();
        break;
      }
    }
    return r;
  }
  function parseOptionalList(kind, parseItem) {
    return token() === kind.open ? parseList(kind, parseItem) : createEmptyList();
  }
  function parseOptionalDelimiter(kind) {
    if (parseOptional(kind.delimiter)) {
      return true;
    }
    if (token() === kind.toleratedDelimiter) {
      if (!kind.toleratedDelimiterIsValid) {
        parseExpected(kind.delimiter);
      }
      nextToken();
      return true;
    }
    return false;
  }
  function atEndOfListWithError(kind) {
    return kind.close !== Token.None && (isStatementKeyword(token()) || token() === Token.EndOfFile) && token() !== kind.allowedStatementKeyword;
  }
  function parseEmptyStatement(pos) {
    parseExpected(Token.Semicolon);
    return { kind: SyntaxKind.EmptyStatement, ...finishNode(pos) };
  }
  function parseInvalidStatement(pos, decorators) {
    do {
      nextToken();
    } while (!isStatementKeyword(token()) && token() !== Token.At && token() !== Token.Semicolon && token() !== Token.EndOfFile);
    error({
      code: "token-expected",
      messageId: "statement",
      target: { pos, end: previousTokenEnd }
    });
    return { kind: SyntaxKind.InvalidStatement, decorators, ...finishNode(pos) };
  }
  function error(report) {
    parseErrorInNextFinishedNode = true;
    const location = {
      file: scanner.file,
      pos: report.target?.pos ?? tokenPos(),
      end: report.target?.end ?? tokenEnd()
    };
    if (!report.printable) {
      treePrintable = false;
    }
    const realPos = report.target?.realPos ?? location.pos;
    if (realPositionOfLastError === realPos) {
      return;
    }
    realPositionOfLastError = realPos;
    const diagnostic = createDiagnostic({
      ...report,
      target: location
    });
    assert(diagnostic.severity === "error", "This function is for reporting errors. Use warning() for warnings.");
    parseDiagnostics.push(diagnostic);
  }
  function warning(report) {
    const location = {
      file: scanner.file,
      pos: report.target?.pos ?? tokenPos(),
      end: report.target?.end ?? tokenEnd()
    };
    const diagnostic = createDiagnostic({
      ...report,
      target: location
    });
    assert(diagnostic.severity === "warning", "This function is for reporting warnings only. Use error() for errors.");
    parseDiagnostics.push(diagnostic);
  }
  function reportDiagnostic2(diagnostic) {
    if (diagnostic.severity === "error") {
      parseErrorInNextFinishedNode = true;
      treePrintable = false;
    }
    parseDiagnostics.push(diagnostic);
  }
  function assert(condition, message) {
    const location = {
      file: scanner.file,
      pos: tokenPos(),
      end: tokenEnd()
    };
    compilerAssert(condition, message, location);
  }
  function reportInvalidDecorators(decorators, nodeName) {
    for (const decorator of decorators) {
      error({ code: "invalid-decorator-location", format: { nodeName }, target: decorator });
    }
  }
  function reportInvalidDirective(directives, nodeName) {
    for (const directive of directives) {
      error({ code: "invalid-directive-location", format: { nodeName }, target: directive });
    }
  }
  function parseExpected(expectedToken) {
    if (token() === expectedToken) {
      nextToken();
      return true;
    }
    const location = getAdjustedDefaultLocation(expectedToken);
    error({
      code: "token-expected",
      format: { token: TokenDisplay[expectedToken] },
      target: location,
      printable: isPunctuation(expectedToken)
    });
    return false;
  }
  function expectTokenIsOneOf(...args) {
    const tok = token();
    for (const expected of args) {
      if (expected === Token.None) {
        continue;
      }
      if (tok === expected) {
        return tok;
      }
    }
    errorTokenIsNotOneOf(...args);
    return Token.None;
  }
  function parseExpectedOneOf(...args) {
    const tok = expectTokenIsOneOf(...args);
    if (tok !== Token.None) {
      nextToken();
    }
    return tok;
  }
  function errorTokenIsNotOneOf(...args) {
    const location = getAdjustedDefaultLocation(args[0]);
    const displayList = args.map((t, i) => {
      if (i === args.length - 1) {
        return `or ${TokenDisplay[t]}`;
      }
      return TokenDisplay[t];
    });
    error({ code: "token-expected", format: { token: displayList.join(", ") }, target: location });
  }
  function parseOptional(optionalToken) {
    if (token() === optionalToken) {
      nextToken();
      return true;
    }
    return false;
  }
  function getAdjustedDefaultLocation(token2) {
    return isPunctuation(token2) ? { pos: previousTokenEnd, end: previousTokenEnd + 1, realPos: tokenPos() } : void 0;
  }
}
function exprIsBareIdentifier(expr) {
  return expr.kind === SyntaxKind.TypeReference && expr.target.kind === SyntaxKind.Identifier && expr.arguments.length === 0;
}
function visitChildren(node, cb) {
  if (node.directives) {
    const result = visitEach(cb, node.directives);
    if (result)
      return result;
  }
  if (node.docs) {
    const result = visitEach(cb, node.docs);
    if (result)
      return result;
  }
  switch (node.kind) {
    case SyntaxKind.TypeSpecScript:
      return visitNode(cb, node.id) || visitEach(cb, node.statements);
    case SyntaxKind.ArrayExpression:
      return visitNode(cb, node.elementType);
    case SyntaxKind.AugmentDecoratorStatement:
      return visitNode(cb, node.target) || visitNode(cb, node.targetType) || visitEach(cb, node.arguments);
    case SyntaxKind.DecoratorExpression:
      return visitNode(cb, node.target) || visitEach(cb, node.arguments);
    case SyntaxKind.CallExpression:
      return visitNode(cb, node.target) || visitEach(cb, node.arguments);
    case SyntaxKind.DirectiveExpression:
      return visitNode(cb, node.target) || visitEach(cb, node.arguments);
    case SyntaxKind.ImportStatement:
      return visitNode(cb, node.path);
    case SyntaxKind.OperationStatement:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitEach(cb, node.templateParameters) || visitNode(cb, node.signature);
    case SyntaxKind.OperationSignatureDeclaration:
      return visitNode(cb, node.parameters) || visitNode(cb, node.returnType);
    case SyntaxKind.OperationSignatureReference:
      return visitNode(cb, node.baseOperation);
    case SyntaxKind.NamespaceStatement:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || (isArray(node.statements) ? visitEach(cb, node.statements) : visitNode(cb, node.statements));
    case SyntaxKind.InterfaceStatement:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitEach(cb, node.templateParameters) || visitEach(cb, node.extends) || visitEach(cb, node.operations);
    case SyntaxKind.UsingStatement:
      return visitNode(cb, node.name);
    case SyntaxKind.IntersectionExpression:
      return visitEach(cb, node.options);
    case SyntaxKind.MemberExpression:
      return visitNode(cb, node.base) || visitNode(cb, node.id);
    case SyntaxKind.ModelExpression:
      return visitEach(cb, node.properties);
    case SyntaxKind.ModelProperty:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitNode(cb, node.value) || visitNode(cb, node.default);
    case SyntaxKind.ModelSpreadProperty:
      return visitNode(cb, node.target);
    case SyntaxKind.ModelStatement:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitEach(cb, node.templateParameters) || visitNode(cb, node.extends) || visitNode(cb, node.is) || visitEach(cb, node.properties);
    case SyntaxKind.ScalarStatement:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitEach(cb, node.templateParameters) || visitEach(cb, node.members) || visitNode(cb, node.extends);
    case SyntaxKind.ScalarConstructor:
      return visitNode(cb, node.id) || visitEach(cb, node.parameters);
    case SyntaxKind.UnionStatement:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitEach(cb, node.templateParameters) || visitEach(cb, node.options);
    case SyntaxKind.UnionVariant:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitNode(cb, node.value);
    case SyntaxKind.EnumStatement:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitEach(cb, node.members);
    case SyntaxKind.EnumMember:
      return visitEach(cb, node.decorators) || visitNode(cb, node.id) || visitNode(cb, node.value);
    case SyntaxKind.EnumSpreadMember:
      return visitNode(cb, node.target);
    case SyntaxKind.AliasStatement:
      return visitNode(cb, node.id) || visitEach(cb, node.templateParameters) || visitNode(cb, node.value);
    case SyntaxKind.ConstStatement:
      return visitNode(cb, node.id) || visitNode(cb, node.value) || visitNode(cb, node.type);
    case SyntaxKind.DecoratorDeclarationStatement:
      return visitEach(cb, node.modifiers) || visitNode(cb, node.id) || visitNode(cb, node.target) || visitEach(cb, node.parameters);
    case SyntaxKind.FunctionDeclarationStatement:
      return visitEach(cb, node.modifiers) || visitNode(cb, node.id) || visitEach(cb, node.parameters) || visitNode(cb, node.returnType);
    case SyntaxKind.FunctionParameter:
      return visitNode(cb, node.id) || visitNode(cb, node.type);
    case SyntaxKind.TypeReference:
      return visitNode(cb, node.target) || visitEach(cb, node.arguments);
    case SyntaxKind.ValueOfExpression:
      return visitNode(cb, node.target);
    case SyntaxKind.TypeOfExpression:
      return visitNode(cb, node.target);
    case SyntaxKind.TupleExpression:
      return visitEach(cb, node.values);
    case SyntaxKind.UnionExpression:
      return visitEach(cb, node.options);
    case SyntaxKind.InvalidStatement:
      return visitEach(cb, node.decorators);
    case SyntaxKind.TemplateParameterDeclaration:
      return visitNode(cb, node.id) || visitNode(cb, node.constraint) || visitNode(cb, node.default);
    case SyntaxKind.TemplateArgument:
      return node.name && visitNode(cb, node.name) || visitNode(cb, node.argument);
    case SyntaxKind.Doc:
      return visitEach(cb, node.content) || visitEach(cb, node.tags);
    case SyntaxKind.DocParamTag:
    case SyntaxKind.DocTemplateTag:
      return visitNode(cb, node.tagName) || visitNode(cb, node.paramName) || visitEach(cb, node.content);
    case SyntaxKind.DocPropTag:
      return visitNode(cb, node.tagName) || visitNode(cb, node.propName) || visitEach(cb, node.content);
    case SyntaxKind.DocReturnsTag:
    case SyntaxKind.DocErrorsTag:
    case SyntaxKind.DocUnknownTag:
      return visitNode(cb, node.tagName) || visitEach(cb, node.content);
    case SyntaxKind.StringTemplateExpression:
      return visitNode(cb, node.head) || visitEach(cb, node.spans);
    case SyntaxKind.StringTemplateSpan:
      return visitNode(cb, node.expression) || visitNode(cb, node.literal);
    case SyntaxKind.ObjectLiteral:
      return visitEach(cb, node.properties);
    case SyntaxKind.ObjectLiteralProperty:
      return visitNode(cb, node.id) || visitNode(cb, node.value);
    case SyntaxKind.ObjectLiteralSpreadProperty:
      return visitNode(cb, node.target);
    case SyntaxKind.ArrayLiteral:
      return visitEach(cb, node.values);
    // no children for the rest of these.
    case SyntaxKind.StringTemplateHead:
    case SyntaxKind.StringTemplateMiddle:
    case SyntaxKind.StringTemplateTail:
    case SyntaxKind.StringLiteral:
    case SyntaxKind.NumericLiteral:
    case SyntaxKind.BooleanLiteral:
    case SyntaxKind.Identifier:
    case SyntaxKind.EmptyStatement:
    case SyntaxKind.VoidKeyword:
    case SyntaxKind.NeverKeyword:
    case SyntaxKind.ExternKeyword:
    case SyntaxKind.UnknownKeyword:
    case SyntaxKind.JsSourceFile:
    case SyntaxKind.JsNamespaceDeclaration:
    case SyntaxKind.DocText:
      return;
    default:
      const _assertNever = node;
      return;
  }
}
function visitNode(cb, node) {
  return node && cb(node);
}
function visitEach(cb, nodes) {
  if (!nodes) {
    return;
  }
  for (const node of nodes) {
    const result = cb(node);
    if (result) {
      return result;
    }
  }
  return;
}
function positionInRange(position, range) {
  return range.pos >= 0 && position > range.pos && (range.end === -1 || position < range.end);
}
function getNodeAtPositionDetail(script, position, filter = () => true) {
  const cur = getNodeAtPosition(script, position, (n) => filter(n, "cur"));
  const input = script.file.text;
  const char = input.charCodeAt(position);
  const preChar = position >= 0 ? input.charCodeAt(position - 1) : NaN;
  const nextChar = position < input.length ? input.charCodeAt(position + 1) : NaN;
  let inTrivia = false;
  let triviaStart;
  let triviaEnd;
  if (!cur || cur.kind !== SyntaxKind.StringLiteral) {
    const { char: cp } = codePointBefore(input, position);
    if (!cp || !isIdentifierContinue(cp)) {
      triviaEnd = skipTrivia(input, position);
      triviaStart = skipTriviaBackward(script, position) + 1;
      inTrivia = triviaEnd !== position;
    }
  }
  if (!inTrivia) {
    const beforeId = skipContinuousIdentifier(
      input,
      position,
      true
      /*isBackward*/
    );
    triviaStart = skipTriviaBackward(script, beforeId) + 1;
    const afterId = skipContinuousIdentifier(
      input,
      position,
      false
      /*isBackward*/
    );
    triviaEnd = skipTrivia(input, afterId);
  }
  if (triviaStart === void 0 || triviaEnd === void 0) {
    compilerAssert(false, "unexpected, triviaStart and triviaEnd should be defined");
  }
  return {
    node: cur,
    char,
    preChar,
    nextChar,
    position,
    inTrivia,
    triviaStartPosition: triviaStart,
    triviaEndPosition: triviaEnd,
    getPositionDetailBeforeTrivia: () => {
      return getNodeAtPositionDetail(script, triviaStart, (n) => filter(n, "pre"));
    },
    getPositionDetailAfterTrivia: () => {
      return getNodeAtPositionDetail(script, triviaEnd, (n) => filter(n, "post"));
    }
  };
}
function getNodeAtPosition(script, position, filter = (node) => true) {
  return visit(script);
  function visit(node) {
    if (node.pos <= position && position <= node.end) {
      const child = visitChildren(node, visit);
      if (child) {
        return child;
      }
      if (filter(node)) {
        return node;
      }
    }
    return void 0;
  }
}
function hasParseError(node) {
  if (node.flags & 2) {
    return true;
  }
  checkForDescendantErrors(node);
  return node.flags & 4;
}
function checkForDescendantErrors(node) {
  if (node.flags & 1) {
    return;
  }
  mutate(node).flags |= 1;
  visitChildren(node, (child) => {
    if (child.flags & 2) {
      mutate(node).flags |= 4 | 1;
      return true;
    }
    checkForDescendantErrors(child);
    if (child.flags & 4) {
      mutate(node).flags |= 4 | 1;
      return true;
    }
    mutate(child).flags |= 1;
    return false;
  });
}
function isImportStatement(node) {
  return node.kind === SyntaxKind.ImportStatement;
}
function isBlocklessNamespace(node) {
  if (node.kind !== SyntaxKind.NamespaceStatement) {
    return false;
  }
  while (!isArray(node.statements) && node.statements) {
    node = node.statements;
  }
  return node.statements === void 0;
}
function getFirstAncestor(node, test, includeSelf = false) {
  if (includeSelf && test(node)) {
    return node;
  }
  for (let n = node.parent; n; n = n.parent) {
    if (test(n)) {
      return n;
    }
  }
  return void 0;
}
function getIdentifierContext(id) {
  const node = getFirstAncestor(id, (n) => n.kind !== SyntaxKind.MemberExpression);
  compilerAssert(node, "Identifier with no non-member-expression ancestor.");
  let kind;
  switch (node.kind) {
    case SyntaxKind.TypeReference:
      kind = IdentifierKind.TypeReference;
      break;
    case SyntaxKind.AugmentDecoratorStatement:
    case SyntaxKind.DecoratorExpression:
      kind = IdentifierKind.Decorator;
      break;
    case SyntaxKind.UsingStatement:
      kind = IdentifierKind.Using;
      break;
    case SyntaxKind.TemplateArgument:
      kind = IdentifierKind.TemplateArgument;
      break;
    case SyntaxKind.ObjectLiteralProperty:
      kind = IdentifierKind.ObjectLiteralProperty;
      break;
    case SyntaxKind.ModelProperty:
      switch (node.parent?.kind) {
        case SyntaxKind.ModelExpression:
          kind = IdentifierKind.ModelExpressionProperty;
          break;
        case SyntaxKind.ModelStatement:
          kind = IdentifierKind.ModelStatementProperty;
          break;
        default:
          compilerAssert("false", "ModelProperty with unexpected parent kind.");
          kind = id.parent.id === id ? IdentifierKind.Declaration : IdentifierKind.Other;
          break;
      }
      break;
    default:
      kind = id.parent.id === id ? IdentifierKind.Declaration : IdentifierKind.Other;
      break;
  }
  return { node, kind };
}

export {
  createDiagnosticCreator,
  paramMessage,
  createDiagnostic,
  reportDiagnostic,
  createSourceFile,
  getSourceFileKindFromExt,
  ResolutionResultFlags,
  SyntaxKind,
  IdentifierKind,
  NoTarget,
  ListenerFlow,
  logDiagnostics,
  getSourceLocation,
  getDiagnosticTemplateInstantitationTrace,
  compilerAssert,
  assertType,
  reportDeprecated,
  createDiagnosticCollector,
  ignoreDiagnostics,
  defineCodeFix,
  isWhiteSpace,
  getPositionBeforeTrivia,
  Token,
  TokenFlags,
  isKeyword,
  isReservedKeyword,
  isPunctuation,
  createScanner,
  skipTrivia,
  skipWhiteSpace,
  printIdentifier,
  typeReferenceToString,
  splitLines,
  parse,
  parseStandaloneTypeReference,
  exprIsBareIdentifier,
  visitChildren,
  positionInRange,
  getNodeAtPositionDetail,
  getNodeAtPosition,
  hasParseError,
  isImportStatement,
  getFirstAncestor,
  getIdentifierContext
};
