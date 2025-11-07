declare module 'mammoth' {
  export function extractRawText(options: { arrayBuffer: ArrayBuffer }): Promise<{ value: string }>; 
  export default any;
}

declare module 'pdfjs-dist/legacy/build/pdf' {
  const pdfjs: any;
  export = pdfjs;
}
