import {
  getDirectoryPath,
  joinPaths,
  normalizePath,
  resolvePath
} from "./chunk-OV76USRJ.js";

// src/typespec/core/packages/compiler/dist/src/module-resolver/esm/utils.js
function createBaseErrorMsg(importSpecifier) {
  return `Could not resolve import "${importSpecifier}" `;
}
function createErrorMsg(context, reason, isImports) {
  const { specifier, packageUrl } = context;
  const base = createBaseErrorMsg(specifier);
  const field = isImports ? "imports" : "exports";
  return `${base} using ${field} defined in ${packageUrl}.${reason ? ` ${reason}` : ""}`;
}
var EsmResolveError = class extends Error {
};
var InvalidModuleSpecifierError = class extends EsmResolveError {
  constructor(context, isImports, reason) {
    super(createErrorMsg(context, reason, isImports));
  }
};
var InvalidPackageTargetError = class extends EsmResolveError {
  constructor(context, reason) {
    super(createErrorMsg(context, reason));
  }
};
var NoMatchingConditionsError = class extends InvalidPackageTargetError {
  constructor(context) {
    super(context, `No conditions matched`);
  }
};
var PackageImportNotDefinedError = class extends EsmResolveError {
  constructor(context) {
    super(createErrorMsg(context, void 0, true));
  }
};
function isUrl(str) {
  try {
    return !!new URL(str);
  } catch (_) {
    return false;
  }
}

// src/typespec/core/packages/compiler/dist/src/module-resolver/esm/resolve-package-target.js
async function resolvePackageTarget(context, { target, patternMatch, isImports }) {
  const { packageUrl } = context;
  const packageUrlWithTrailingSlash = packageUrl.endsWith("/") ? packageUrl : `${packageUrl}/`;
  if (typeof target === "string") {
    if (!target.startsWith("./")) {
      if (!isImports || target.startsWith("../") || target.startsWith("/") || isUrl(target)) {
        throw new InvalidPackageTargetError(context, `Invalid mapping: "${target}".`);
      }
      if (typeof patternMatch === "string") {
        return await context.resolveId(target.replace(/\*/g, patternMatch), packageUrlWithTrailingSlash);
      }
      return await context.resolveId(target, packageUrlWithTrailingSlash);
    }
    checkInvalidSegment(context, target);
    const resolvedTarget = resolvePath(packageUrlWithTrailingSlash, target);
    if (!resolvedTarget.startsWith(packageUrl)) {
      throw new InvalidPackageTargetError(context, `Resolved to ${resolvedTarget} which is outside package ${packageUrl}`);
    }
    if (!patternMatch) {
      return resolvedTarget;
    }
    if (includesInvalidSegments(patternMatch.split(/\/|\\/), context.moduleDirs)) {
      throw new InvalidModuleSpecifierError(context);
    }
    return resolvedTarget.replace(/\*/g, patternMatch);
  }
  if (Array.isArray(target)) {
    if (target.length === 0) {
      return null;
    }
    let lastError = null;
    for (const item of target) {
      try {
        const resolved = await resolvePackageTarget(context, {
          target: item,
          patternMatch,
          isImports
        });
        if (resolved !== void 0) {
          return resolved;
        }
      } catch (error) {
        if (!(error instanceof InvalidPackageTargetError)) {
          throw error;
        } else {
          lastError = error;
        }
      }
    }
    if (lastError) {
      throw lastError;
    }
    return null;
  }
  if (target && typeof target === "object") {
    for (const [key, value] of Object.entries(target)) {
      if (key === "default" && !context.ignoreDefaultCondition || context.conditions.includes(key)) {
        const resolved = await resolvePackageTarget(context, {
          target: value,
          patternMatch,
          isImports
        });
        if (resolved !== void 0) {
          return resolved;
        }
      }
    }
    return void 0;
  }
  if (target === null) {
    return null;
  }
  throw new InvalidPackageTargetError(context, `Invalid exports field.`);
}
function includesInvalidSegments(pathSegments, moduleDirs) {
  const invalidSegments = ["", ".", "..", ...moduleDirs];
  return pathSegments.some((v) => invalidSegments.includes(v) || invalidSegments.includes(decodeURI(v)));
}
function checkInvalidSegment(context, target) {
  const pathSegments = target.split(/\/|\\/);
  const firstDot = pathSegments.indexOf(".");
  firstDot !== -1 && pathSegments.slice(firstDot);
  if (firstDot !== -1 && firstDot < pathSegments.length - 1 && includesInvalidSegments(pathSegments.slice(firstDot + 1), context.moduleDirs)) {
    throw new InvalidPackageTargetError(context, `Invalid mapping: "${target}".`);
  }
}

// src/typespec/core/packages/compiler/dist/src/module-resolver/esm/resolve-package-imports-exports.js
async function resolvePackageImportsExports(context, { matchKey, matchObj, isImports }) {
  if (!matchKey.includes("*") && matchKey in matchObj) {
    const target = matchObj[matchKey];
    const resolved = await resolvePackageTarget(context, { target, patternMatch: "", isImports });
    return resolved;
  }
  const expansionKeys = Object.keys(matchObj).filter((k) => k.endsWith("/") || k.includes("*")).sort(nodePatternKeyCompare);
  for (const expansionKey of expansionKeys) {
    const indexOfAsterisk = expansionKey.indexOf("*");
    const patternBase = indexOfAsterisk === -1 ? expansionKey : expansionKey.substring(0, indexOfAsterisk);
    if (matchKey.startsWith(patternBase) && matchKey !== patternBase) {
      const patternTrailer = indexOfAsterisk !== -1 ? expansionKey.substring(indexOfAsterisk + 1) : "";
      if (patternTrailer.length === 0 || // or if matchKey ends with patternTrailer and the length of matchKey is greater than or equal to the length of expansionKey, then
      matchKey.endsWith(patternTrailer) && matchKey.length >= expansionKey.length) {
        const target = matchObj[expansionKey];
        const patternMatch = matchKey.substring(patternBase.length, matchKey.length - patternTrailer.length);
        const resolved = await resolvePackageTarget(context, {
          target,
          patternMatch,
          isImports
        });
        return resolved;
      }
    }
  }
  throw new InvalidModuleSpecifierError(context, isImports);
}
function nodePatternKeyCompare(keyA, keyB) {
  const baseLengthA = keyA.includes("*") ? keyA.indexOf("*") + 1 : keyA.length;
  const baseLengthB = keyB.includes("*") ? keyB.indexOf("*") + 1 : keyB.length;
  const rval = baseLengthB - baseLengthA;
  if (rval !== 0)
    return rval;
  if (!keyA.includes("*"))
    return 1;
  if (!keyB.includes("*"))
    return -1;
  return keyB.length - keyA.length;
}

// src/typespec/core/packages/compiler/dist/src/module-resolver/esm/resolve-package-exports.js
async function resolvePackageExports(context, subpath, exports) {
  if (exports === null)
    return void 0;
  if (subpath === ".") {
    let mainExport;
    if (typeof exports === "string" || Array.isArray(exports) || isConditions(exports)) {
      mainExport = exports;
    } else if (exports["."]) {
      mainExport = exports["."];
    }
    if (mainExport) {
      if (context.ignoreDefaultCondition && typeof mainExport === "string") {
        return void 0;
      }
      const resolved = await resolvePackageTarget(context, {
        target: mainExport,
        isImports: false
      });
      if (resolved) {
        return resolved;
      } else {
        throw new NoMatchingConditionsError(context);
      }
    }
  } else if (isMappings(exports)) {
    const resolvedMatch = await resolvePackageImportsExports(context, {
      matchKey: subpath,
      matchObj: exports,
      isImports: false
    });
    if (resolvedMatch) {
      return resolvedMatch;
    }
  }
  throw new InvalidModuleSpecifierError(context);
}
function isConditions(item) {
  return typeof item === "object" && Object.keys(item).every((k) => !k.startsWith("."));
}
function isMappings(exports) {
  return typeof exports === "object" && !isConditions(exports);
}

// src/typespec/core/packages/compiler/dist/src/module-resolver/esm/resolve-package-imports.js
async function resolvePackageImports(context, imports) {
  if (context.specifier === "#" || context.specifier.startsWith("#/")) {
    throw new InvalidModuleSpecifierError(context);
  }
  if (imports !== null) {
    const resolvedMatch = await resolvePackageImportsExports(context, {
      matchKey: context.specifier,
      matchObj: imports,
      isImports: true
    });
    if (resolvedMatch) {
      return resolvedMatch;
    }
  }
  throw new PackageImportNotDefinedError(context);
}

// src/typespec/core/packages/compiler/dist/src/module-resolver/utils.js
function parseNodeModuleSpecifier(id) {
  if (id.startsWith(".") || id.startsWith("/")) {
    return null;
  }
  const split = id.split("/");
  if (split[0][0] === "@") {
    return { packageName: `${split[0]}/${split[1]}`, subPath: split.slice(2).join("/") };
  }
  return { packageName: split[0], subPath: split.slice(1).join("/") };
}

// src/typespec/core/packages/compiler/dist/src/module-resolver/module-resolver.js
var ResolveModuleError = class extends Error {
  code;
  pkgJson;
  constructor(code, message, pkgJson) {
    super(message);
    this.code = code;
    this.pkgJson = pkgJson;
  }
};
var defaultDirectoryIndexFiles = ["index.mjs", "index.js"];
async function resolveModule(host, specifier, options) {
  const { baseDir } = options;
  const absoluteStart = await realpath(resolvePath(baseDir));
  if (!await isDirectory(host, absoluteStart)) {
    throw new TypeError(`Provided basedir '${baseDir}'is not a directory.`);
  }
  if (/^(?:\.\.?(?:\/|$)|\/|([A-Za-z]:)?[/\\])/.test(specifier)) {
    const res = resolvePath(absoluteStart, specifier);
    const m = await loadAsFile(res) || await loadAsDirectory(res);
    if (m) {
      return m;
    }
  }
  if (specifier.startsWith("#")) {
    const dirs = listDirHierarchy(baseDir);
    for (const dir of dirs) {
      const pkgFile = resolvePath(dir, "package.json");
      if (!await isFile(host, pkgFile))
        continue;
      const pkg = await readPackage(host, pkgFile);
      const module2 = await resolveNodePackageImports(pkg, dir);
      if (module2)
        return module2;
    }
  }
  const self = await resolveSelf(specifier, absoluteStart);
  if (self)
    return self;
  const module = await resolveAsNodeModule(specifier, absoluteStart);
  if (module)
    return module;
  throw new ResolveModuleError("MODULE_NOT_FOUND", `Cannot find module '${specifier}' from '${baseDir}'`);
  async function realpath(path) {
    try {
      return normalizePath(await host.realpath(path));
    } catch (e) {
      if (e.code === "ENOENT" || e.code === "ENOTDIR") {
        return path;
      }
      throw e;
    }
  }
  function listDirHierarchy(baseDir2) {
    const paths = [baseDir2];
    let current = getDirectoryPath(baseDir2);
    while (current !== paths[paths.length - 1]) {
      paths.push(current);
      current = getDirectoryPath(current);
    }
    return paths;
  }
  async function resolveSelf(name, baseDir2) {
    for (const dir of listDirHierarchy(baseDir2)) {
      const pkgFile = resolvePath(dir, "package.json");
      if (!await isFile(host, pkgFile))
        continue;
      const pkg = await readPackage(host, pkgFile);
      if (pkg.name === name) {
        return loadPackage(dir, pkg);
      } else {
        return void 0;
      }
    }
    return void 0;
  }
  async function resolveAsNodeModule(importSpecifier, baseDir2) {
    const module2 = parseNodeModuleSpecifier(importSpecifier);
    if (module2 === null)
      return void 0;
    const dirs = listDirHierarchy(baseDir2);
    for (const dir of dirs) {
      const n = await loadPackageAtPath(joinPaths(dir, "node_modules", module2.packageName), module2.subPath);
      if (n)
        return n;
    }
    return void 0;
  }
  async function loadPackageAtPath(path, subPath) {
    const pkgFile = resolvePath(path, "package.json");
    if (!await isFile(host, pkgFile))
      return void 0;
    const pkg = await readPackage(host, pkgFile);
    const n = await loadPackage(path, pkg, subPath);
    if (n)
      return n;
    return void 0;
  }
  async function resolveNodePackageImports(pkg, pkgDir) {
    if (!pkg.imports)
      return void 0;
    let match;
    try {
      match = await resolvePackageImports({
        packageUrl: pathToFileURL(pkgDir),
        specifier,
        moduleDirs: ["node_modules"],
        conditions: options.conditions ?? [],
        ignoreDefaultCondition: options.fallbackOnMissingCondition,
        resolveId: async (id, baseDir2) => {
          const resolved2 = await resolveAsNodeModule(id, fileURLToPath(baseDir2.toString()));
          return resolved2 && pathToFileURL(resolved2.mainFile);
        }
      }, pkg.imports);
    } catch (error) {
      if (error instanceof InvalidPackageTargetError) {
        throw new ResolveModuleError("INVALID_MODULE_IMPORT_TARGET", error.message, pkg);
      } else if (error instanceof EsmResolveError) {
        throw new ResolveModuleError("INVALID_MODULE", error.message, pkg);
      } else {
        throw error;
      }
    }
    if (!match)
      return void 0;
    const resolved = await resolveEsmMatch(match, true, pkg);
    return {
      type: "module",
      mainFile: resolved,
      manifest: pkg,
      path: pkgDir
    };
  }
  async function resolveNodePackageExports(subPath, pkg, pkgDir) {
    if (!pkg.exports)
      return void 0;
    let match;
    try {
      match = await resolvePackageExports({
        packageUrl: pathToFileURL(pkgDir),
        specifier,
        moduleDirs: ["node_modules"],
        conditions: options.conditions ?? [],
        ignoreDefaultCondition: options.fallbackOnMissingCondition,
        resolveId: (id, baseDir2) => {
          throw new ResolveModuleError("INVALID_MODULE", "Not supported", pkg);
        }
      }, subPath === "" ? "." : `./${subPath}`, pkg.exports);
    } catch (error) {
      if (error instanceof NoMatchingConditionsError) {
        if (subPath === "") {
          return;
        } else {
          throw new ResolveModuleError("INVALID_MODULE", error.message, pkg);
        }
      } else if (error instanceof InvalidPackageTargetError) {
        throw new ResolveModuleError("INVALID_MODULE_EXPORT_TARGET", error.message, pkg);
      } else if (error instanceof EsmResolveError) {
        throw new ResolveModuleError("INVALID_MODULE", error.message, pkg);
      } else {
        throw error;
      }
    }
    if (!match)
      return void 0;
    const resolved = await resolveEsmMatch(match, false, pkg);
    return {
      type: "module",
      mainFile: resolved,
      manifest: pkg,
      path: pkgDir
    };
  }
  async function resolveEsmMatch(match, isImports, pkg) {
    const resolved = await realpath(fileURLToPath(match));
    if (await isFile(host, resolved)) {
      return resolved;
    }
    throw new ResolveModuleError(isImports ? "INVALID_MODULE_IMPORT_TARGET" : "INVALID_MODULE_EXPORT_TARGET", `Import "${specifier}" resolving to "${resolved}" is not a file.`, pkg);
  }
  async function loadAsDirectory(directory) {
    const pkg = await loadPackageAtPath(directory);
    if (pkg) {
      return pkg;
    }
    for (const file of options.directoryIndexFiles ?? defaultDirectoryIndexFiles) {
      const resolvedFile2 = await loadAsFile(joinPaths(directory, file));
      if (resolvedFile2) {
        return resolvedFile2;
      }
    }
    return void 0;
  }
  async function loadPackage(directory, pkg, subPath) {
    const e = await resolveNodePackageExports(subPath ?? "", pkg, directory);
    if (e)
      return e;
    if (subPath !== void 0 && subPath !== "") {
      return void 0;
    }
    return loadPackageLegacy(directory, pkg);
  }
  async function loadPackageLegacy(directory, pkg) {
    const mainFile = options.resolveMain ? options.resolveMain(pkg) : pkg.main;
    if (mainFile === void 0 || mainFile === null) {
      throw new ResolveModuleError("INVALID_MODULE", `Package ${pkg.name} is missing a main file or exports field.`, pkg);
    }
    if (typeof mainFile !== "string") {
      throw new ResolveModuleError("INVALID_MAIN", `Package ${pkg.name} main file "${mainFile}" must be a string.`, pkg);
    }
    const mainFullPath = resolvePath(directory, mainFile);
    let loaded;
    try {
      loaded = await loadAsFile(mainFullPath) ?? await loadAsDirectory(mainFullPath);
    } catch (e) {
      throw new ResolveModuleError("INVALID_MAIN", `Package ${pkg.name} main file "${mainFile}" is not pointing to a valid file or directory.`, pkg);
    }
    if (loaded) {
      if (loaded.type === "module") {
        return loaded;
      }
      return {
        type: "module",
        path: await realpath(directory),
        mainFile: loaded.path,
        manifest: pkg
      };
    } else {
      throw new ResolveModuleError("INVALID_MAIN", `Package ${pkg.name} main file "${mainFile}" is not pointing to a valid file or directory.`, pkg);
    }
  }
  async function loadAsFile(file) {
    if (await isFile(host, file)) {
      return resolvedFile(file);
    }
    const extensions = [".mjs", ".js"];
    for (const ext of extensions) {
      const fileWithExtension = file + ext;
      if (await isFile(host, fileWithExtension)) {
        return resolvedFile(fileWithExtension);
      }
    }
    return void 0;
  }
  async function resolvedFile(path) {
    return { type: "file", path: await realpath(path) };
  }
}
async function readPackage(host, pkgfile) {
  const content = await host.readFile(pkgfile);
  return {
    ...JSON.parse(content),
    file: {
      path: pkgfile,
      text: content
    }
  };
}
async function isDirectory(host, path) {
  try {
    const stats = await host.stat(path);
    return stats.isDirectory();
  } catch (e) {
    if (e.code === "ENOENT" || e.code === "ENOTDIR") {
      return false;
    }
    throw e;
  }
}
async function isFile(host, path) {
  try {
    const stats = await host.stat(path);
    return stats.isFile();
  } catch (e) {
    if (e.code === "ENOENT" || e.code === "ENOTDIR") {
      return false;
    }
    throw e;
  }
}
function pathToFileURL(path) {
  return `file://${path}`;
}
function fileURLToPath(url) {
  if (!url.startsWith("file://"))
    throw new Error("Cannot convert non file: URL to path");
  const pathname = url.slice("file://".length);
  for (let n = 0; n < pathname.length; n++) {
    if (pathname[n] === "%") {
      const third = pathname.codePointAt(n + 2) | 32;
      if (pathname[n + 1] === "2" && third === 102) {
        throw new Error("Invalid url to path: must not include encoded / characters");
      }
    }
  }
  return decodeURIComponent(pathname);
}

export {
  ResolveModuleError,
  resolveModule
};
