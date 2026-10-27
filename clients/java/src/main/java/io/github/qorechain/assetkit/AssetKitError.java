// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

/** Base class of every error thrown by this library. */
public class AssetKitError extends RuntimeException {
    private static final long serialVersionUID = 1L;

    private final String code;
    private final String module;

    public AssetKitError(String message, String code, String module) {
        super(message);
        this.code = code;
        this.module = module;
    }

    /** Stable machine-readable code. */
    public String code() {
        return code;
    }

    /** Module the error belongs to, for example {@code "x/asset"}. */
    public String module() {
        return module;
    }
}
