import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { fetchBookFromR2, parseRangeHeader, sanitizeSlug, buildContentDisposition, } from "../src/storage.js";
// Helper to create a mock R2ObjectBody
function createMockR2Object(key, content, range) {
    let slice = content;
    let effectiveOffset = 0;
    let effectiveLength = content.byteLength;
    if (range) {
        if (typeof range.offset === "number" && typeof range.length === "number") {
            effectiveOffset = range.offset;
            effectiveLength = range.length;
            slice = content.subarray(range.offset, range.offset + range.length);
        }
        else if (typeof range.offset === "number") {
            effectiveOffset = range.offset;
            effectiveLength = content.byteLength - range.offset;
            slice = content.subarray(range.offset);
        }
        else if (typeof range.suffix === "number") {
            effectiveOffset = Math.max(0, content.byteLength - range.suffix);
            effectiveLength = Math.min(content.byteLength, range.suffix);
            slice = content.subarray(effectiveOffset);
        }
    }
    const stream = new ReadableStream({
        start(controller) {
            controller.enqueue(slice);
            controller.close();
        },
    });
    return {
        key,
        version: "v1",
        size: slice.byteLength,
        etag: '"mock-etag-12345"',
        httpEtag: '"mock-etag-12345"',
        range: range ? { offset: effectiveOffset, length: effectiveLength } : undefined,
        uploaded: new Date(),
        storageClass: "Standard",
        checksums: { toJSON: () => ({}) },
        writeHttpMetadata: () => { },
        body: stream,
        bodyUsed: false,
        async arrayBuffer() {
            return slice.buffer;
        },
        async bytes() {
            return slice;
        },
        async text() {
            return new TextDecoder().decode(slice);
        },
        async json() {
            return JSON.parse(new TextDecoder().decode(slice));
        },
        async blob() {
            return new Blob([slice]);
        },
    };
}
// Helper to create a mock R2Bucket
function createMockR2Bucket(files) {
    return {
        async get(key, options) {
            const data = files.get(key);
            if (!data)
                return null;
            const range = options?.range;
            return createMockR2Object(key, data, range);
        },
    };
}
describe("Cloudflare R2 Storage & Streaming Delivery Engine", () => {
    const samplePdfBytes = new TextEncoder().encode("%PDF-1.7\n1 0 obj\n<< /Title (TheMiniCEO Test Book) >>\nendobj\ntrailer\n<< /Size 2 >>\n%%EOF");
    const files = new Map([
        ["The_Lean_Startup.pdf", samplePdfBytes],
        ["Actionable_Gamification.pdf", samplePdfBytes],
    ]);
    const bucket = createMockR2Bucket(files);
    const env = { BOOKS_BUCKET: bucket };
    test("parseRangeHeader parses byte ranges correctly", () => {
        assert.deepEqual(parseRangeHeader("bytes=0-15"), { offset: 0, length: 16 });
        assert.deepEqual(parseRangeHeader("bytes=100-200"), { offset: 100, length: 101 });
        assert.deepEqual(parseRangeHeader("bytes=50-"), { offset: 50 });
        assert.deepEqual(parseRangeHeader("bytes=-30"), { suffix: 30 });
        assert.equal(parseRangeHeader("invalid-range"), undefined);
        assert.equal(parseRangeHeader(""), undefined);
    });
    test("sanitizeSlug neutralizes directory traversal and special characters", () => {
        assert.equal(sanitizeSlug("the-lean-startup"), "the-lean-startup");
        assert.equal(sanitizeSlug("../../etc/passwd"), "etc-passwd");
        assert.equal(sanitizeSlug("..\\..\\windows\\system32"), "windows-system32");
        assert.equal(sanitizeSlug("کتاب-نوپای-ناب"), "کتاب-نوپای-ناب");
        assert.equal(sanitizeSlug("Actionable Gamification [Yu Kai Chon]"), "Actionable-Gamification--Yu-Kai-Chon");
    });
    test("buildContentDisposition sets RFC 6266 attachment with UTF-8 filename*", () => {
        const cd = buildContentDisposition("the-lean-startup", "The Lean Startup");
        assert.ok(cd.includes('attachment; filename="the-lean-startup.pdf"'));
        assert.ok(cd.includes("filename*=UTF-8''The%20Lean%20Startup.pdf"));
        const cdPersian = buildContentDisposition("lean-startup", "نوپای ناب");
        assert.ok(cdPersian.includes('filename="lean-startup.pdf"'));
        assert.ok(cdPersian.includes("filename*=UTF-8''%D9%86%D9%88%D9%BE%D8%A7%DB%8C%20%D9%86%D8%A7%D8%A8.pdf"));
    });
    test("fetchBookFromR2 streams full file with status 200 and standard headers", async () => {
        const res = await fetchBookFromR2(env, "The_Lean_Startup.pdf", null, {
            bookId: "the-lean-startup",
            bookTitle: "The Lean Startup",
        });
        assert.equal(res.status, 200);
        assert.equal(res.headers.get("Content-Type"), "application/pdf");
        assert.equal(res.headers.get("Accept-Ranges"), "bytes");
        assert.equal(res.headers.get("ETag"), '"mock-etag-12345"');
        assert.equal(res.headers.get("Content-Length"), String(samplePdfBytes.byteLength));
        assert.ok(res.headers.get("Content-Disposition")?.includes("the-lean-startup.pdf"));
        const bodyBytes = new Uint8Array(await res.arrayBuffer());
        assert.equal(bodyBytes.byteLength, samplePdfBytes.byteLength);
        assert.ok(new TextDecoder().decode(bodyBytes).startsWith("%PDF-"));
    });
    test("fetchBookFromR2 handles HTTP Range requests with status 206 Partial Content", async () => {
        const rangeHeader = "bytes=0-15";
        const res = await fetchBookFromR2(env, "The_Lean_Startup.pdf", rangeHeader, {
            bookId: "the-lean-startup",
            totalSize: samplePdfBytes.byteLength,
        });
        assert.equal(res.status, 206);
        assert.equal(res.headers.get("Content-Type"), "application/pdf");
        assert.equal(res.headers.get("Content-Length"), "16");
        assert.ok(res.headers.get("Content-Range")?.startsWith("bytes 0-15/"));
        const chunk = new Uint8Array(await res.arrayBuffer());
        assert.equal(chunk.byteLength, 16);
        assert.deepEqual(chunk, samplePdfBytes.subarray(0, 16));
    });
    test("fetchBookFromR2 returns 404 FILE_NOT_FOUND when object does not exist in bucket", async () => {
        const res = await fetchBookFromR2(env, "Non_Existent_Book.pdf");
        assert.equal(res.status, 404);
        const json = (await res.json());
        assert.equal(json.success, false);
        assert.equal(json.error, "FILE_NOT_FOUND");
    });
    test("fetchBookFromR2 returns 404 FILE_NOT_FOUND when BOOKS_BUCKET is not configured", async () => {
        const emptyEnv = {};
        const res = await fetchBookFromR2(emptyEnv, "The_Lean_Startup.pdf");
        assert.equal(res.status, 404);
        const json = (await res.json());
        assert.equal(json.success, false);
        assert.equal(json.error, "FILE_NOT_FOUND");
    });
});
