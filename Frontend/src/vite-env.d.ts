/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;   // 👈 this line adds support for your env var
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}