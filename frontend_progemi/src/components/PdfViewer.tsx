/* -------------------------------------------------------------------- */
/* PdfViewer.tsx                                                        */
/* -------------------------------------------------------------------- */
"use client";
import { useEffect, useRef, useState } from "react";
import type { PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";

export interface Highlight {
  polygon: number[];   // [x1 y1 x2 y2 x3 y3 x4 y4] – en pouces
  page:    number;     // 1-based
}

interface Props { file: string; highlight: Highlight | null }

export default function PdfViewer({ file, highlight }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const [pageSizes, setPageSizes] = useState<{ w: number; h: number }[]>([]);

  /* 1. Rendu du PDF -------------------------------------------------- */
  useEffect(() => {
    if (!file) return;
    let pdf: PDFDocumentProxy | undefined;
    (async () => {
      const pdfjs = await import("pdfjs-dist/build/pdf.mjs");
      pdfjs.GlobalWorkerOptions.workerSrc = new URL(
        "pdfjs-dist/build/pdf.worker.mjs", import.meta.url,
      ).href;

      pdf = await pdfjs.getDocument({ url: file }).promise;
      container.current!.innerHTML = "";
      const sizes: { w: number; h: number }[] = [];

      for (let p = 1; p <= pdf.numPages; p++) {
        const page: PDFPageProxy = await pdf.getPage(p);
        const vp = page.getViewport({ scale: 1 });
        sizes.push({ w: vp.width, h: vp.height });

        /* wrapper RELATIF ------------------------------------------- */
        const pageDiv = document.createElement("div");
        pageDiv.className = "pdf-page";
        pageDiv.dataset.pageNumber = String(p);
        pageDiv.style.position = "relative";
        pageDiv.style.display  = "block";

        const canvas = document.createElement("canvas");
        canvas.width  = vp.width;
        canvas.height = vp.height;
        await page.render({ canvasContext: canvas.getContext("2d")!, viewport: vp }).promise;

        pageDiv.appendChild(canvas);
        container.current!.appendChild(pageDiv);
      }
      setPageSizes(sizes);
    })();
    return () => pdf?.destroy();
  }, [file]);

  /* 2. Rectangle + auto-scroll -------------------------------------- */
  useEffect(() => {
    if (!highlight || !pageSizes.length) return;

    const pageDiv = container.current!
      .querySelector<HTMLDivElement>(`.pdf-page[data-page-number="${highlight.page}"]`);
    if (!pageDiv) return;

    pageDiv.scrollIntoView({ block: "center", behavior: "smooth" });

    /* conversion pouces → px                                          */
    const vpWpt      = pageSizes[highlight.page - 1].w;   // largeur en points
    const dpi        = (pageDiv.firstElementChild as HTMLCanvasElement).width / (vpWpt / 72);
    const xs = [0,2,4,6].map(i => highlight.polygon[i] * dpi);
    const ys = [1,3,5,7].map(i => highlight.polygon[i] * dpi);

    const box = {
      left  : Math.min(...xs),
      top   : Math.min(...ys),
      width : Math.max(...xs) - Math.min(...xs),
      height: Math.max(...ys) - Math.min(...ys),
    };

    /* un seul highlight par page ------------------------------------ */
    pageDiv.querySelectorAll(".pdf-highlight").forEach(el => el.remove());

    const hl = document.createElement("div");
    hl.className = "pdf-highlight";
    Object.assign(hl.style, {
      position      : "absolute",
      border        : "2px solid red",
      pointerEvents : "none",
      left : box.left + "px",
      top  : box.top  + "px",
      width: box.width  + "px",
      height: box.height + "px",
    });
    pageDiv.appendChild(hl);
  }, [highlight, pageSizes]);

  return (
    <div ref={container} className="w-full h-full overflow-auto bg-neutral-200" />
  );
}
