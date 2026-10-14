/**
 * Standalone Client-Side SVG QR Code Generator
 * Minimal, zero-dependency, self-contained implementation for crypto wallet addresses.
 * Supports Byte Mode (UTF-8/ASCII) with Error Correction Level M/L.
 */
(function (global) {
  'use strict';

  // Galois Field GF(256) tables with primitive polynomial 0x11d
  const EXP_TABLE = new Uint8Array(512);
  const LOG_TABLE = new Uint8Array(256);
  (function initGalois() {
    let x = 1;
    for (let i = 0; i < 255; i++) {
      EXP_TABLE[i] = x;
      EXP_TABLE[i + 255] = x;
      LOG_TABLE[x] = i;
      x = (x << 1) ^ (x & 0x80 ? 0x11d : 0);
    }
  })();

  function gfMul(x, y) {
    if (x === 0 || y === 0) return 0;
    return EXP_TABLE[LOG_TABLE[x] + LOG_TABLE[y]];
  }

  // Reed-Solomon generator polynomial computation
  function rsGeneratorPoly(degree) {
    let poly = [1];
    for (let i = 0; i < degree; i++) {
      const next = new Array(poly.length + 1).fill(0);
      for (let j = 0; j < poly.length; j++) {
        next[j] ^= gfMul(poly[j], EXP_TABLE[i]);
        next[j + 1] ^= poly[j];
      }
      poly = next;
    }
    return poly;
  }

  // Calculate Reed-Solomon parity bytes
  function rsCompute(data, numEc) {
    const gen = rsGeneratorPoly(numEc);
    const res = new Uint8Array(numEc);
    for (let i = 0; i < data.length; i++) {
      const factor = data[i] ^ res[0];
      for (let j = 0; j < numEc - 1; j++) {
        res[j] = res[j + 1] ^ gfMul(gen[j + 1], factor);
      }
      res[numEc - 1] = gfMul(gen[numEc], factor);
    }
    return res;
  }

  // Versions table for Byte mode (Level L & M)
  // [version, totalModules, totalDataBytes, ecBytes, blockDataBytes, ecBytesPerBlock]
  const VERSION_SPECS = [
    // Version 1 (21x21)
    { ver: 1, size: 21, dataCap: 16, ec: 10, align: [] },
    // Version 2 (25x25)
    { ver: 2, size: 25, dataCap: 28, ec: 16, align: [6, 18] },
    // Version 3 (29x29)
    { ver: 3, size: 29, dataCap: 44, ec: 26, align: [6, 22] },
    // Version 4 (33x33)
    { ver: 4, size: 33, dataCap: 64, ec: 36, align: [6, 26] },
    // Version 5 (37x37)
    { ver: 5, size: 37, dataCap: 86, ec: 48, align: [6, 30] },
    // Version 6 (41x41)
    { ver: 6, size: 41, dataCap: 108, ec: 64, align: [6, 34] },
    // Version 7 (45x45)
    { ver: 7, size: 45, dataCap: 124, ec: 72, align: [6, 22, 38] },
  ];

  function getVersionSpec(byteLength) {
    for (const spec of VERSION_SPECS) {
      if (spec.dataCap >= byteLength + 3) {
        return spec;
      }
    }
    return VERSION_SPECS[VERSION_SPECS.length - 1];
  }

  class BitBuffer {
    constructor() {
      this.buffer = [];
      this.length = 0;
    }
    put(val, bits) {
      for (let i = bits - 1; i >= 0; i--) {
        this.buffer.push((val >> i) & 1);
        this.length++;
      }
    }
    getBytes() {
      const bytes = new Uint8Array(Math.ceil(this.length / 8));
      for (let i = 0; i < this.length; i++) {
        if (this.buffer[i]) {
          bytes[i >> 3] |= 0x80 >> (i & 7);
        }
      }
      return bytes;
    }
  }

  function encodeData(text, spec) {
    const bb = new BitBuffer();
    // Mode indicator: 0100 for Byte mode
    bb.put(0b0100, 4);
    // Character count indicator (8 bits for versions 1-9)
    const textBytes = new TextEncoder().encode(text);
    bb.put(textBytes.length, 8);
    // Data bytes
    for (let i = 0; i < textBytes.length; i++) {
      bb.put(textBytes[i], 8);
    }
    // Terminator
    const remaining = spec.dataCap * 8 - bb.length;
    bb.put(0, Math.min(4, Math.max(0, remaining)));
    // Byte align
    while (bb.length % 8 !== 0) {
      bb.put(0, 1);
    }
    // Pad bytes
    const padBytes = [0xec, 0x11];
    let padIdx = 0;
    while (bb.length < spec.dataCap * 8) {
      bb.put(padBytes[padIdx % 2], 8);
      padIdx++;
    }
    const rawData = bb.getBytes();
    const ecData = rsCompute(rawData, spec.ec);
    const finalData = new Uint8Array(rawData.length + ecData.length);
    finalData.set(rawData, 0);
    finalData.set(ecData, rawData.length);
    return finalData;
  }

  function createMatrix(spec) {
    const n = spec.size;
    const matrix = Array.from({ length: n }, () => new Int8Array(n).fill(-1));
    const reserved = Array.from({ length: n }, () => new Uint8Array(n).fill(0));

    function setFinder(r, c) {
      for (let i = -1; i <= 7; i++) {
        for (let j = -1; j <= 7; j++) {
          const row = r + i;
          const col = c + j;
          if (row < 0 || row >= n || col < 0 || col >= n) continue;
          reserved[row][col] = 1;
          if (
            (i >= 0 && i <= 6 && (j === 0 || j === 6)) ||
            (j >= 0 && j <= 6 && (i === 0 || i === 6)) ||
            (i >= 2 && i <= 4 && j >= 2 && j <= 4)
          ) {
            matrix[row][col] = 1;
          } else {
            matrix[row][col] = 0;
          }
        }
      }
    }

    // Top-left, top-right, bottom-left finders
    setFinder(0, 0);
    setFinder(0, n - 7);
    setFinder(n - 7, 0);

    // Alignment patterns
    if (spec.align && spec.align.length > 0) {
      for (const r of spec.align) {
        for (const c of spec.align) {
          if (reserved[r][c]) continue;
          for (let i = -2; i <= 2; i++) {
            for (let j = -2; j <= 2; j++) {
              reserved[r + i][c + j] = 1;
              matrix[r + i][c + j] =
                Math.max(Math.abs(i), Math.abs(j)) === 1 ? 0 : 1;
            }
          }
        }
      }
    }

    // Timing patterns
    for (let i = 8; i < n - 8; i++) {
      if (!reserved[6][i]) {
        reserved[6][i] = 1;
        matrix[6][i] = i % 2 === 0 ? 1 : 0;
      }
      if (!reserved[i][6]) {
        reserved[i][6] = 1;
        matrix[i][6] = i % 2 === 0 ? 1 : 0;
      }
    }

    // Dark module
    matrix[4 * spec.ver + 9][8] = 1;
    reserved[4 * spec.ver + 9][8] = 1;

    // Reserve format information areas
    for (let i = 0; i < 9; i++) {
      if (i < n) {
        reserved[8][i] = 1;
        reserved[i][8] = 1;
      }
      if (n - 1 - i >= 0) {
        reserved[8][n - 1 - i] = 1;
        reserved[n - 1 - i][8] = 1;
      }
    }

    return { matrix, reserved, n };
  }

  function placeDataBits(matrix, reserved, data, n) {
    let bitIdx = 0;
    const totalBits = data.length * 8;
    let up = true;
    for (let c = n - 1; c > 0; c -= 2) {
      if (c === 6) c--; // Skip vertical timing column
      const rows = up ? Array.from({ length: n }, (_, i) => n - 1 - i) : Array.from({ length: n }, (_, i) => i);
      for (const r of rows) {
        for (let j = 0; j < 2; j++) {
          const col = c - j;
          if (reserved[r][col]) continue;
          let bit = 0;
          if (bitIdx < totalBits) {
            const byte = data[bitIdx >> 3];
            bit = (byte >> (7 - (bitIdx & 7))) & 1;
            bitIdx++;
          }
          // Apply Mask 0: (r + col) % 2 === 0
          if ((r + col) % 2 === 0) {
            bit ^= 1;
          }
          matrix[r][col] = bit;
        }
      }
      up = !up;
    }
  }

  // Format info for Mask 0 + EC Level L (0b01000) with BCH error correction and 0x5412 XOR
  // Format string for EC Level L, Mask 0 = 0x77c4 -> 0b111011111000100
  const FORMAT_BITS_L_MASK0 = 0x77c4;

  function placeFormatInfo(matrix, n) {
    const bits = FORMAT_BITS_L_MASK0;
    // Around top-left
    for (let i = 0; i <= 5; i++) matrix[8][i] = (bits >> (14 - i)) & 1;
    matrix[8][7] = (bits >> 8) & 1;
    matrix[8][8] = (bits >> 7) & 1;
    matrix[7][8] = (bits >> 6) & 1;
    for (let i = 9; i <= 14; i++) matrix[14 - i][8] = (bits >> (14 - i)) & 1;

    // Split around bottom-left & top-right
    for (let i = 0; i < 7; i++) matrix[n - 1 - i][8] = (bits >> i) & 1;
    for (let i = 0; i < 8; i++) matrix[8][n - 8 + i] = (bits >> (7 + i)) & 1;
  }

  /**
   * Generates an SVG string representation of a QR Code.
   * @param {string} text - The text/URI to encode
   * @param {Object} [options]
   * @param {number} [options.size=180] - Output width and height in px
   * @param {string} [options.fgColor="#0f172a"] - Foreground color (modules)
   * @param {string} [options.bgColor="transparent"] - Background fill
   * @param {number} [options.margin=2] - Module margin/quiet zone
   */
  function generateQrSvg(text, options = {}) {
    const size = options.size || 180;
    const fg = options.fgColor || "#0f172a";
    const bg = options.bgColor || "transparent";
    const margin = options.margin !== undefined ? options.margin : 2;

    const textBytes = new TextEncoder().encode(text);
    const spec = getVersionSpec(textBytes.length);
    const encoded = encodeData(text, spec);
    const { matrix, reserved, n } = createMatrix(spec);

    placeDataBits(matrix, reserved, encoded, n);
    placeFormatInfo(matrix, n);

    const totalModules = n + margin * 2;
    let pathData = "";

    for (let r = 0; r < n; r++) {
      for (let c = 0; c < n; c++) {
        if (matrix[r][c] === 1) {
          const x = c + margin;
          const y = r + margin;
          pathData += `M${x},${y}h1v1h-1z `;
        }
      }
    }

    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${totalModules} ${totalModules}" width="${size}" height="${size}" shape-rendering="crispEdges" aria-label="QR Code">
  ${bg !== "transparent" ? `<rect width="${totalModules}" height="${totalModules}" fill="${bg}" />` : ""}
  <path d="${pathData.trim()}" fill="${fg}" />
</svg>`;
  }

  // Export to global scope
  const PaywallQR = {
    generateQrSvg: generateQrSvg,
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = PaywallQR;
  }
  global.PaywallQR = PaywallQR;
})(typeof window !== "undefined" ? window : globalThis);
