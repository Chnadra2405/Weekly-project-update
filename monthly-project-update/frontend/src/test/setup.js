import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { randomUUID } from "node:crypto";
import { afterEach } from "vitest";

if (!globalThis.crypto) globalThis.crypto = {};
if (!globalThis.crypto.randomUUID) globalThis.crypto.randomUUID = randomUUID;

afterEach(cleanup);