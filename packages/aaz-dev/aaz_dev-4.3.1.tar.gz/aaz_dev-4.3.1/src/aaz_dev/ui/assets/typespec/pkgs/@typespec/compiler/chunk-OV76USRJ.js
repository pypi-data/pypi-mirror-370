// src/typespec/core/packages/compiler/dist/src/core/path-utils.js
var directorySeparator = "/";
var altDirectorySeparator = "\\";
var urlSchemeSeparator = "://";
var backslashRegExp = /\\/g;
var relativePathSegmentRegExp = /(?:\/\/)|(?:^|\/)\.\.?(?:$|\/)/;
function isAnyDirectorySeparator(charCode) {
  return charCode === 47 || charCode === 92;
}
function isUrl(path) {
  return getEncodedRootLength(path) < 0;
}
function isPathAbsolute(path) {
  return getEncodedRootLength(path) !== 0;
}
function isVolumeCharacter(charCode) {
  return charCode >= 97 && charCode <= 122 || charCode >= 65 && charCode <= 90;
}
function getFileUrlVolumeSeparatorEnd(url, start) {
  const ch0 = url.charCodeAt(start);
  if (ch0 === 58)
    return start + 1;
  if (ch0 === 37 && url.charCodeAt(start + 1) === 51) {
    const ch2 = url.charCodeAt(start + 2);
    if (ch2 === 97 || ch2 === 65)
      return start + 3;
  }
  return -1;
}
function getRootLength(path) {
  const rootLength = getEncodedRootLength(path);
  return rootLength < 0 ? ~rootLength : rootLength;
}
function getEncodedRootLength(path) {
  if (!path)
    return 0;
  const ch0 = path.charCodeAt(0);
  if (ch0 === 47 || ch0 === 92) {
    if (path.charCodeAt(1) !== ch0)
      return 1;
    const p1 = path.indexOf(ch0 === 47 ? directorySeparator : altDirectorySeparator, 2);
    if (p1 < 0)
      return path.length;
    return p1 + 1;
  }
  if (isVolumeCharacter(ch0) && path.charCodeAt(1) === 58) {
    const ch2 = path.charCodeAt(2);
    if (ch2 === 47 || ch2 === 92)
      return 3;
    if (path.length === 2)
      return 2;
  }
  const schemeEnd = path.indexOf(urlSchemeSeparator);
  if (schemeEnd !== -1) {
    const authorityStart = schemeEnd + urlSchemeSeparator.length;
    const authorityEnd = path.indexOf(directorySeparator, authorityStart);
    if (authorityEnd !== -1) {
      const scheme = path.slice(0, schemeEnd);
      const authority = path.slice(authorityStart, authorityEnd);
      if (scheme === "file" && (authority === "" || authority === "localhost") && isVolumeCharacter(path.charCodeAt(authorityEnd + 1))) {
        const volumeSeparatorEnd = getFileUrlVolumeSeparatorEnd(path, authorityEnd + 2);
        if (volumeSeparatorEnd !== -1) {
          if (path.charCodeAt(volumeSeparatorEnd) === 47) {
            return ~(volumeSeparatorEnd + 1);
          }
          if (volumeSeparatorEnd === path.length) {
            return ~volumeSeparatorEnd;
          }
        }
      }
      return ~(authorityEnd + 1);
    }
    return ~path.length;
  }
  return 0;
}
function getDirectoryPath(path) {
  path = normalizeSlashes(path);
  const rootLength = getRootLength(path);
  if (rootLength === path.length)
    return path;
  path = removeTrailingDirectorySeparator(path);
  return path.slice(0, Math.max(rootLength, path.lastIndexOf(directorySeparator)));
}
function getBaseFileName(path) {
  path = normalizeSlashes(path);
  const rootLength = getRootLength(path);
  if (rootLength === path.length)
    return "";
  path = removeTrailingDirectorySeparator(path);
  return path.slice(Math.max(getRootLength(path), path.lastIndexOf(directorySeparator) + 1));
}
function getAnyExtensionFromPath(path) {
  const baseFileName = getBaseFileName(path);
  const extensionIndex = baseFileName.lastIndexOf(".");
  if (extensionIndex >= 0) {
    return baseFileName.substring(extensionIndex).toLowerCase();
  }
  return "";
}
function pathComponents(path, rootLength) {
  const root = path.substring(0, rootLength);
  const rest = path.substring(rootLength).split(directorySeparator);
  if (rest.length && !rest[rest.length - 1])
    rest.pop();
  return [root, ...rest];
}
function getPathComponents(path, currentDirectory = "") {
  path = joinPaths(currentDirectory, path);
  return pathComponents(path, getRootLength(path));
}
function reducePathComponents(components) {
  if (!components.some((x) => x !== void 0))
    return [];
  const reduced = [components[0]];
  for (let i = 1; i < components.length; i++) {
    const component = components[i];
    if (!component)
      continue;
    if (component === ".")
      continue;
    if (component === "..") {
      if (reduced.length > 1) {
        if (reduced[reduced.length - 1] !== "..") {
          reduced.pop();
          continue;
        }
      } else if (reduced[0])
        continue;
    }
    reduced.push(component);
  }
  return reduced;
}
function joinPaths(path, ...paths) {
  if (path)
    path = normalizeSlashes(path);
  for (let relativePath of paths) {
    if (!relativePath)
      continue;
    relativePath = normalizeSlashes(relativePath);
    if (!path || getRootLength(relativePath) !== 0) {
      path = relativePath;
    } else {
      path = ensureTrailingDirectorySeparator(path) + relativePath;
    }
  }
  return path;
}
function resolvePath(path, ...paths) {
  return normalizePath(paths.some((x) => x !== void 0) ? joinPaths(path, ...paths) : normalizeSlashes(path));
}
function getNormalizedPathComponents(path, currentDirectory) {
  return reducePathComponents(getPathComponents(path, currentDirectory));
}
function getNormalizedAbsolutePath(fileName, currentDirectory) {
  return getPathFromPathComponents(getNormalizedPathComponents(fileName, currentDirectory));
}
function normalizePath(path) {
  path = normalizeSlashes(path);
  if (!relativePathSegmentRegExp.test(path)) {
    return path;
  }
  const simplified = path.replace(/\/\.\//g, "/").replace(/^\.\//, "");
  if (simplified !== path) {
    path = simplified;
    if (!relativePathSegmentRegExp.test(path)) {
      return path;
    }
  }
  const normalized = getPathFromPathComponents(reducePathComponents(getPathComponents(path)));
  return normalized && hasTrailingDirectorySeparator(path) ? ensureTrailingDirectorySeparator(normalized) : normalized;
}
function getPathWithoutRoot(pathComponents2) {
  if (pathComponents2.length === 0)
    return "";
  return pathComponents2.slice(1).join(directorySeparator);
}
function getNormalizedAbsolutePathWithoutRoot(fileName, currentDirectory) {
  return getPathWithoutRoot(getNormalizedPathComponents(fileName, currentDirectory));
}
function getPathFromPathComponents(pathComponents2) {
  if (pathComponents2.length === 0)
    return "";
  const root = pathComponents2[0] && ensureTrailingDirectorySeparator(pathComponents2[0]);
  return root + pathComponents2.slice(1).join(directorySeparator);
}
function removeTrailingDirectorySeparator(path) {
  if (hasTrailingDirectorySeparator(path)) {
    return path.substring(0, path.length - 1);
  }
  return path;
}
function ensureTrailingDirectorySeparator(path) {
  if (!hasTrailingDirectorySeparator(path)) {
    return path + directorySeparator;
  }
  return path;
}
function hasTrailingDirectorySeparator(path) {
  return path.length > 0 && isAnyDirectorySeparator(path.charCodeAt(path.length - 1));
}
function normalizeSlashes(path) {
  const index = path.indexOf("\\");
  if (index === -1) {
    return path;
  }
  backslashRegExp.lastIndex = index;
  return path.replace(backslashRegExp, directorySeparator);
}
function equateValues(a, b) {
  return a === b;
}
function equateStringsCaseInsensitive(a, b) {
  return a === b || a !== void 0 && b !== void 0 && a.toUpperCase() === b.toUpperCase();
}
function equateStringsCaseSensitive(a, b) {
  return equateValues(a, b);
}
function identity(x) {
  return x;
}
function getPathComponentsRelativeTo(from, to, stringEqualityComparer, getCanonicalFileName) {
  const fromComponents = reducePathComponents(getPathComponents(from));
  const toComponents = reducePathComponents(getPathComponents(to));
  let start;
  for (start = 0; start < fromComponents.length && start < toComponents.length; start++) {
    const fromComponent = getCanonicalFileName(fromComponents[start]);
    const toComponent = getCanonicalFileName(toComponents[start]);
    const comparer = start === 0 ? equateStringsCaseInsensitive : stringEqualityComparer;
    if (!comparer(fromComponent, toComponent))
      break;
  }
  if (start === 0) {
    return toComponents;
  }
  const components = toComponents.slice(start);
  const relative = [];
  for (; start < fromComponents.length; start++) {
    relative.push("..");
  }
  return ["", ...relative, ...components];
}
function getRelativePathFromDirectory(fromDirectory, to, getCanonicalFileNameOrIgnoreCase) {
  if (getRootLength(fromDirectory) > 0 !== getRootLength(to) > 0) {
    throw new Error("Paths must either both be absolute or both be relative");
  }
  const getCanonicalFileName = typeof getCanonicalFileNameOrIgnoreCase === "function" ? getCanonicalFileNameOrIgnoreCase : identity;
  const ignoreCase = typeof getCanonicalFileNameOrIgnoreCase === "boolean" ? getCanonicalFileNameOrIgnoreCase : false;
  const pathComponents2 = getPathComponentsRelativeTo(fromDirectory, to, ignoreCase ? equateStringsCaseInsensitive : equateStringsCaseSensitive, getCanonicalFileName);
  return getPathFromPathComponents(pathComponents2);
}

export {
  isAnyDirectorySeparator,
  isUrl,
  isPathAbsolute,
  getRootLength,
  getDirectoryPath,
  getBaseFileName,
  getAnyExtensionFromPath,
  getPathComponents,
  reducePathComponents,
  joinPaths,
  resolvePath,
  getNormalizedPathComponents,
  getNormalizedAbsolutePath,
  normalizePath,
  getNormalizedAbsolutePathWithoutRoot,
  getPathFromPathComponents,
  removeTrailingDirectorySeparator,
  ensureTrailingDirectorySeparator,
  hasTrailingDirectorySeparator,
  normalizeSlashes,
  getRelativePathFromDirectory
};
