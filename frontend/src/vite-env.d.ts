/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_WS: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

