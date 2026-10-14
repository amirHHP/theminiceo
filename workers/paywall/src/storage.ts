/**
 * Cloudflare R2 Storage & Streaming Delivery Engine
 * Accesses private R2 bucket, sets RFC 6266 headers, and streams with zero memory buffering
 */

export interface StorageEnv {
  BOOKS_BUCKET?: R2Bucket;
}

export interface StorageOptions {
  bookTitle?: string;
  bookId?: string;
  totalSize?: number;
}

/**
 * Parses HTTP byte range header (e.g. bytes=0-15, bytes=100-, bytes=-50)
 */
export function parseRangeHeader(rangeHeader: string): R2Range | undefined {
  if (!rangeHeader || !rangeHeader.startsWith("bytes=")) {
    return undefined;
  }
  const match = rangeHeader.trim().match(/^bytes=(\d*)-(\d*)$/);
  if (!match) return undefined;

  const startStr = match[1];
  const endStr = match[2];

  if (startStr && endStr) {
    const start = parseInt(startStr, 10);
    const end = parseInt(endStr, 10);
    if (!isNaN(start) && !isNaN(end) && end >= start) {
      return { offset: start, length: end - start + 1 };
    }
  } else if (startStr && !endStr) {
    const start = parseInt(startStr, 10);
    if (!isNaN(start)) {
      return { offset: start };
    }
  } else if (!startStr && endStr) {
    const suffix = parseInt(endStr, 10);
    if (!isNaN(suffix)) {
      return { suffix };
    }
  }
  return undefined;
}

/**
 * Sanitizes book identifier / slug to prevent path traversal attacks
 * and ensure safe filename in Content-Disposition.
 */
export function sanitizeSlug(input: string): string {
  if (!input) return "book";
  // Replace slashes and directory navigation
  const clean = input.replace(/[\\/]/g, "-").replace(/^\.+/, "");
  // Replace non-word/non-persian chars
  const slugified = clean.replace(/[^\w\u0600-\u06FF-]/g, "-").replace(/^-+|-+$/g, "");
  return slugified || "book";
}

/**
 * Builds RFC 6266 / RFC 5987 Content-Disposition header
 */
export function buildContentDisposition(slug: string, title?: string): string {
  const safeSlug = sanitizeSlug(slug);
  const displayTitle = title || safeSlug;
  const encodedTitle = encodeURIComponent(displayTitle);
  return `attachment; filename="${safeSlug}.pdf"; filename*=UTF-8''${encodedTitle}.pdf`;
}

/**
 * Fetches PDF object from Cloudflare R2 bucket and returns streamed response
 */
export async function fetchBookFromR2(
  env: StorageEnv,
  filename: string,
  rangeHeaderOrOptions?: string | null | StorageOptions,
  optionsOrTitle?: StorageOptions | string
): Promise<Response> {
  let rangeHeader: string | null | undefined;
  let options: StorageOptions = {};

  if (typeof rangeHeaderOrOptions === "string") {
    rangeHeader = rangeHeaderOrOptions;
    if (typeof optionsOrTitle === "string") {
      options = { bookTitle: optionsOrTitle };
    } else if (optionsOrTitle && typeof optionsOrTitle === "object") {
      options = optionsOrTitle;
    }
  } else if (rangeHeaderOrOptions && typeof rangeHeaderOrOptions === "object") {
    options = rangeHeaderOrOptions;
  } else if (optionsOrTitle && typeof optionsOrTitle === "object") {
    options = optionsOrTitle;
  } else if (typeof optionsOrTitle === "string") {
    options = { bookTitle: optionsOrTitle };
  }

  if (!env.BOOKS_BUCKET) {
    return new Response(
      JSON.stringify({
        success: false,
        error: "FILE_NOT_FOUND",
        message: "The requested book file is not available in storage.",
      }),
      {
        status: 404,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      }
    );
  }

  const parsedRange = rangeHeader ? parseRangeHeader(rangeHeader) : undefined;
  const getOptions: R2GetOptions = parsedRange ? { range: parsedRange } : {};

  const object = await env.BOOKS_BUCKET.get(filename, getOptions);

  if (!object) {
    return new Response(
      JSON.stringify({
        success: false,
        error: "FILE_NOT_FOUND",
        message: "The requested book file is not available in storage.",
      }),
      {
        status: 404,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      }
    );
  }

  const headers = new Headers();
  headers.set("Content-Type", "application/pdf");
  headers.set("Accept-Ranges", "bytes");
  headers.set("Cache-Control", "private, no-transform, max-age=0");

  const etag = object.httpEtag || object.etag;
  if (etag) {
    headers.set("ETag", etag);
  }

  const slug = options.bookId || filename.replace(/\.pdf$/i, "");
  headers.set("Content-Disposition", buildContentDisposition(slug, options.bookTitle));

  const isRangeRequest = Boolean(parsedRange);
  let status = 200;

  if (isRangeRequest) {
    status = 206;
    let start = 0;
    let length = object.size;

    if (parsedRange) {
      if ("offset" in parsedRange && typeof parsedRange.offset === "number") {
        start = parsedRange.offset;
        if ("length" in parsedRange && typeof parsedRange.length === "number") {
          length = parsedRange.length;
        }
      } else if ("suffix" in parsedRange && typeof parsedRange.suffix === "number") {
        start = Math.max(0, object.size - parsedRange.suffix);
        length = Math.min(object.size, parsedRange.suffix);
      }
    }

    const end = start + length - 1;
    const total = options.totalSize || object.size;
    headers.set("Content-Range", `bytes ${start}-${end}/${total}`);
    headers.set("Content-Length", String(length));
  } else {
    headers.set("Content-Length", String(object.size));
  }

  // Stream object.body directly with zero memory buffering
  return new Response(object.body, {
    status,
    headers,
  });
}
