// SPDX-License-Identifier: Apache-2.0
import { describe, expect, it } from "vitest";
import { createElement } from "react";
import { renderToString } from "react-dom/server";
import { App } from "./App";

describe("App", () => {
  it("renders without a wallet, with the native-lane prerequisites and creation disabled", () => {
    const html = renderToString(createElement(App));
    expect(html).toContain("QORE");
    expect(html).toContain("MsgOpenEVMWindow");
    expect(html).toContain("EIP-6963");
    expect(html).toMatch(/<button disabled=""[^>]*>Create token<\/button>/);
  });
});
