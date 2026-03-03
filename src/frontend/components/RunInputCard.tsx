import React, { useRef } from "react"

type Props = {
  configFile: File | null
  imageFile: File | null
  setConfigFile: (f: File | null) => void
  setImageFile: (f: File | null) => void
  onRun: () => void
  busy: boolean
  error: string | null
}

export default function RunInputCard({
  configFile,
  imageFile,
  setConfigFile,
  setImageFile,
  onRun,
  busy,
  error,
}: Props) {
  const configRef = useRef<HTMLInputElement | null>(null)
  const imageRef = useRef<HTMLInputElement | null>(null)

  return (
    <section className="card">
      <div className="cardHeader">
        <h2>Entradas</h2>
        <span className="badge">UPLOAD</span>
      </div>

      <div className="field">
        <label>Config (JSON)</label>
        <div className="fileRow">
          <button className="btn ghost" type="button" onClick={() => configRef.current?.click()}>
            Selecionar JSON
          </button>
          <span className="fileName">{configFile ? configFile.name : "Nenhum arquivo selecionado"}</span>
        </div>
        <input
          ref={configRef}
          className="hidden"
          type="file"
          accept=".json,application/json"
          onChange={(e) => setConfigFile(e.target.files?.[0] ?? null)}
        />
      </div>

      <div className="field">
        <label>Imagem</label>
        <div className="fileRow">
          <button className="btn ghost" type="button" onClick={() => imageRef.current?.click()}>
            Selecionar Imagem
          </button>
          <span className="fileName">{imageFile ? imageFile.name : "Nenhum arquivo selecionado"}</span>
        </div>
        <input
          ref={imageRef}
          className="hidden"
          type="file"
          accept=".png,.tif,.tiff,image/png,image/tiff"
          onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {error ? <div className="alert">{error}</div> : null}

      <div className="actions">
        <button className="btn" type="button" onClick={onRun} disabled={busy}>
          {busy ? "Processando..." : "RUN"}
        </button>
      </div>

      <div className="hint">
        Dica: o JSON deve conter <code>mask</code>, <code>stride</code>, <code>r</code>, <code>activation</code>.
      </div>
    </section>
  )
}