// Copyright 2016 Pixar
//
// Licensed under the terms set forth in the LICENSE.txt file available at
// https://openusd.org/license.
//
// Modified by Jeremy Retailleau.

#include "pxr/plug/pxr.h"
#include "pxr/plug/info.h"
#include <pxr/tf/diagnosticLite.h>
#include <pxr/tf/getenv.h>
#include <pxr/tf/pathUtils.h>
#include <pxr/tf/preprocessorUtilsLite.h>
#include <pxr/tf/stringUtils.h>
#include <pxr/arch/attributes.h>
#include <pxr/arch/fileSystem.h>
#include <pxr/arch/symbols.h>
#include <pxr/arch/systemInfo.h>

PLUG_NAMESPACE_OPEN_SCOPE

namespace {

const char* pathEnvVarName      = TF_PP_STRINGIZE(PXR_PLUGINPATH_NAME);

#ifdef PXR_INSTALL_LOCATION
const char* installLocation     = PXR_INSTALL_LOCATION;
#else
const char* buildLocation       = PXR_BUILD_LOCATION;
const char* pluginBuildLocation = PXR_PLUGIN_BUILD_LOCATION;
#endif // PXR_INSTALL_LOCATION

void
_AppendPathList(
    std::vector<std::string>* result, 
    const std::string& paths, const std::string& sharedLibPath)
{
    for (const auto& path: TfStringSplit(paths, ARCH_PATH_LIST_SEP)) {
        if (path.empty()) {
            continue;
        }

        // Anchor all relative paths to the shared library path.
        const bool isLibraryRelativePath = TfIsRelativePath(path);
        if (isLibraryRelativePath) {
            std::string fullPath = TfStringCatPaths(sharedLibPath, path);
            // Re-add trailing slash if necessary
            // (https://github.com/PixarAnimationStudios/OpenUSD/issues/3679)
            if (TfStringEndsWith(path, "/") && !TfStringEndsWith(fullPath, "/")) {
                fullPath += "/";
            }
            result->push_back(fullPath);
        }
        else {
            result->push_back(path);
        }
    }
}

ARCH_CONSTRUCTOR(Plug_InitConfig, 2)
{
    std::vector<std::string> result;

    std::vector<std::string> debugMessages;

    // Determine the absolute path to the Plug shared library.  Any relative
    // paths specified in the plugin search path will be anchored to this
    // directory, to allow for relocatability.  Note that this can fail when pxr
    // is built as a static library.  In that case, fall back to using
    // ArchGetExecutablePath().  Also provide some diagnostic output if the
    // PLUG_INFO_SEARCH debug flag is enabled.
    std::string binaryPath;
    if (!ArchGetAddressInfo(
        reinterpret_cast<void*>(&Plug_InitConfig), &binaryPath,
            nullptr, nullptr, nullptr)) {
        debugMessages.emplace_back(
            "Failed to determine absolute path for Plug search "
            "using using ArchGetAddressInfo().  This is expected "
            "if pxr is linked as a static library.\n");
    }

    if (binaryPath.empty()) {
        debugMessages.emplace_back(
            "Using ArchGetExecutablePath() to determine absolute "
            "path for Plug search location.\n");
        binaryPath = ArchGetExecutablePath();
    }

    binaryPath = TfGetPathName(binaryPath);

    debugMessages.emplace_back(
        TfStringPrintf(
            "Plug will search for plug infos under '%s'\n",
            binaryPath.c_str()));

    // Environment locations.
    _AppendPathList(&result, TfGetenv(pathEnvVarName), binaryPath);

    // Fallback locations.
#ifdef PXR_INSTALL_LOCATION
    _AppendPathList(&result, installLocation, binaryPath);
#else
    _AppendPathList(&result, buildLocation, binaryPath);
    _AppendPathList(&result, pluginBuildLocation, binaryPath);
#endif // PXR_INSTALL_LOCATION

    // Plugin registration must process these paths in order
    // to ensure deterministic behavior when the same plugin
    // exists in different paths.  The first path containing
    // a particular plug-in will "win".
    const bool pathsAreOrdered = true;
    Plug_SetPaths(result, debugMessages, pathsAreOrdered);
}

}

PLUG_NAMESPACE_CLOSE_SCOPE
