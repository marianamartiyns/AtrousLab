import React, { useMemo, useRef } from "react"

type ActivationType = "relu" | "identity"
type FilterType = "generic" | "sobel"

type Props = {
  maskFile: File | null
  imageFile: File | null
  setMaskFile: (f: File | null) => void
  setImageFile: (f: File | null) => void

  stride: number
  setStride: (v: number) => void

  dilationRate: number
  setDilationRate: (v: number) => void

  activation: ActivationType
  setActivation: (v: ActivationType) => void

  filterType: FilterType
  setFilterType: (v: FilterType) => void

  onRun: () => void
  busy: boolean
  error: string | null
}

export default function RunInputCard({
  maskFile,
  imageFile,
  setMaskFile,
  setImageFile,
  stride,
  setStride,
  dilationRate,
  setDilationRate,
  activation,
  setActivation,
  filterType,
  setFilterType,
  onRun,
  busy,
  error,
}: Props) {
  const maskRef = useRef<HTMLInputElement | null>(null)
  const imageRef = useRef<HTMLInputElement | null>(null)

  function clampOneToFive(value: string) {
    const parsed = Number(value)
    if (!Number.isFinite(parsed)) return 1
    return Math.min(5, Math.max(1, Math.trunc(parsed)))
  }

  const configPreview = useMemo(() => {
    return JSON.stringify(
      {
        stride,
        r: dilationRate,
        activation,
        filter_type: filterType,
      },
      null,
      2
    )
  }, [stride, dilationRate, activation, filterType])

  return (
    <section className="card">
      <div className="cardHeader">
        <h2>Entradas</h2>
        <span className="badge">UPLOAD</span>
      </div>

      <div className="field">
        <label>Máscara (.txt)</label>
        <div className="fileRow">
          <button
            className="btn ghost"
            type="button"
            onClick={() => maskRef.current?.click()}
          >
            Selecionar Máscara
          </button>
          <span className="fileName">
            {maskFile ? maskFile.name : "Nenhum arquivo selecionado"}
          </span>
        </div>
        <input
          ref={maskRef}
          className="hidden"
          type="file"
          accept=".txt,text/plain"
          onChange={(e) => setMaskFile(e.target.files?.[0] ?? null)}
        />
      </div>

      <div className="field">
        <label>Imagem (.png, .tif, .tiff)</label>
        <div className="fileRow">
          <button
            className="btn ghost"
            type="button"
            onClick={() => imageRef.current?.click()}
          >
            Selecionar Imagem
          </button>
          <span className="fileName">
            {imageFile ? imageFile.name : "Nenhum arquivo selecionado"}
          </span>
        </div>
        <input
          ref={imageRef}
          className="hidden"
          type="file"
          accept=".png,.tif,.tiff,image/png,image/tiff"
          onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
        />
      </div>

      <div className="field">
        <label htmlFor="stride">Stride (1 a 5)</label>
        <input
          id="stride"
          className="input"
          type="number"
          min={1}
          max={5}
          step={1}
          value={stride}
          onChange={(e) => setStride(clampOneToFive(e.target.value))}
        />
      </div>

      <div className="field">
        <label htmlFor="dilationRate">Taxa r / Dilatação (1 a 5)</label>
        <input
          id="dilationRate"
          className="input"
          type="number"
          min={1}
          max={5}
          step={1}
          value={dilationRate}
          onChange={(e) => setDilationRate(clampOneToFive(e.target.value))}
        />
      </div>

      <div className="field">
        <label htmlFor="activation">Função de ativação</label>
        <select
          id="activation"
          className="input"
          value={activation}
          onChange={(e) => setActivation(e.target.value as ActivationType)}
        >
          <option value="identity">Identidade</option>
          <option value="relu">ReLU</option>
        </select>
      </div>

      <div className="field">
        <label htmlFor="filterType">Tipo de filtro</label>
        <select
          id="filterType"
          className="input"
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as FilterType)}
        >
          <option value="generic">Genérico</option>
          <option value="sobel">Sobel</option>
        </select>
      </div>

      <div className="field">
        <label>Prévia do config.json gerado</label>
        <div className="configPreview">
          <pre>{configPreview}</pre>
        </div>
      </div>

      {error ? <div className="alert">{error}</div> : null}

      <div className="actions">
        <button className="btn" type="button" onClick={onRun} disabled={busy}>
          {busy ? "Processando..." : "RUN"}
        </button>
      </div>
    </section>
  )
}