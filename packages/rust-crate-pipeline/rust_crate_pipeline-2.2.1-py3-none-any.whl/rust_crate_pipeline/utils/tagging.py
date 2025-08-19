from __future__ import annotations

from typing import Dict, List, Tuple


WINDOWS_INDICATORS = {"winapi", "windows"}
UNIX_INDICATORS = {"nix", "libc"}
WASM_INDICATORS = {"wasm-bindgen", "web-sys", "js-sys", "wasm-bindgen-futures"}
NO_STD_HINTS = {"no_std", "nostd"}

BUILD_DEPS_HINTS = {"cc", "bindgen", "pkg-config", "cmake"}
PROC_MACRO_HINTS = {"proc-macro", "syn", "quote", "proc-macro2"}


def tag_platforms_and_roles(
    crate_name: str,
    keywords: List[str],
    dependencies: List[Dict[str, str]],
) -> Tuple[List[str], List[str]]:
    deps = {d.get("crate_id", "") or d.get("name", "") for d in dependencies}
    kw = {k.lower() for k in keywords}

    platforms: List[str] = []
    if kw & NO_STD_HINTS:
        platforms.append("no_std")
    if deps & WASM_INDICATORS or ("wasm" in kw):
        platforms.append("wasm32")
    if deps & WINDOWS_INDICATORS:
        platforms.append("windows")
    if deps & UNIX_INDICATORS:
        platforms.append("unix")

    roles: List[str] = ["lib"]  # default assumption

    # Heuristic proc-macro detection
    is_proc_macro = crate_name.endswith("-derive") or (kw & {"proc-macro"}) or (deps & PROC_MACRO_HINTS)
    if is_proc_macro:
        if "lib" in roles:
            roles.remove("lib")
        roles.append("proc-macro")

    # Heuristic build-dep hint
    if deps & BUILD_DEPS_HINTS:
        roles.append("build-dep")

    # 'bin' detection is non-trivial without manifest; omit unless clear signal
    return platforms, roles
