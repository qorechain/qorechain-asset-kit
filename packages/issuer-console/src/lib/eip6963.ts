// SPDX-License-Identifier: Apache-2.0
//
// EIP-6963: multi injected provider discovery.

export interface Eip1193Provider {
  request(args: { method: string; params?: unknown[] | Record<string, unknown> }): Promise<unknown>;
  on?(event: string, listener: (...args: unknown[]) => void): void;
  removeListener?(event: string, listener: (...args: unknown[]) => void): void;
}

export interface Eip6963ProviderInfo {
  uuid: string;
  name: string;
  icon: string;
  rdns: string;
}

export interface Eip6963ProviderDetail {
  info: Eip6963ProviderInfo;
  provider: Eip1193Provider;
}

/** Adds or replaces an announced provider, keyed by uuid; keeps announcement order. */
export function mergeAnnouncement(list: Eip6963ProviderDetail[], detail: Eip6963ProviderDetail): Eip6963ProviderDetail[] {
  if (!detail?.info?.uuid || typeof detail.provider?.request !== "function") return list;
  const i = list.findIndex((d) => d.info.uuid === detail.info.uuid);
  if (i === -1) return [...list, detail];
  const next = [...list];
  next[i] = detail;
  return next;
}

/** Only data: URIs are rendered as icons, so a wallet cannot make the page load a remote resource. */
export function safeIcon(icon: string): string | undefined {
  return /^data:image\/(png|svg\+xml|webp|jpeg|gif);/i.test(icon) ? icon : undefined;
}

/** Subscribes to announcements and asks wallets to announce. Returns an unsubscribe function. */
export function discoverProviders(target: Window, onChange: (list: Eip6963ProviderDetail[]) => void): () => void {
  let list: Eip6963ProviderDetail[] = [];
  const handler = (event: Event) => {
    list = mergeAnnouncement(list, (event as CustomEvent<Eip6963ProviderDetail>).detail);
    onChange(list);
  };
  target.addEventListener("eip6963:announceProvider", handler);
  target.dispatchEvent(new Event("eip6963:requestProvider"));
  return () => target.removeEventListener("eip6963:announceProvider", handler);
}
