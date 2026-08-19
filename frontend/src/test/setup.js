import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { randomUUID } from "node:crypto";
import { afterEach } from "vitest";

if (!globalThis.crypto) globalThis.crypto = {};
if (!globalThis.crypto.randomUUID) globalThis.crypto.randomUUID = randomUUID;
if (!globalThis.localStorage) {
	const values = new Map();
	Object.defineProperty(globalThis, "localStorage", {
		configurable: true,
		value: {
			getItem: (key) => values.get(key) ?? null,
			setItem: (key, value) => values.set(key, String(value)),
			removeItem: (key) => values.delete(key),
			clear: () => values.clear(),
		},
	});
}

afterEach(cleanup);