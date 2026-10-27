// SPDX-License-Identifier: Apache-2.0
package io.github.qorechain.assetkit;

import com.google.protobuf.Message;

/**
 * One recorded MockChain event, in emission order.
 *
 * @param type full proto name, for example {@code qorechain.asset.v1.EventMinted}
 * @param height block height at emission
 * @param data the typed event message
 */
public record Event(String type, long height, Message data) {}
