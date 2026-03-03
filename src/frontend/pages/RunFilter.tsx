import React, { useMemo, useState } from "react"
import RunInputCard from "../components/RunInputCard"
import RunOutputCard from "../components/RunOutputCard"

export type RunResponse = {
  ok: boolean
  message?: string
  outputUrl?: string
  sobelVisUrl?: string
  logs?: string[]
}

const ACCEPTED_IMAGES = [".png", ".tif", ".tiff"]
const ACCEPTED_CONFIG = [".json"]

function extOf(name: string) {
  const i = name.lastIndexOf(".")
  return i >= 0 ? name.slice(i).toLowerCase() : ""
}

function isAccepted(name: string, allowed: string[]) {
  return allowed.includes(extOf(name))
}

export default function RunFilter() {
  const [configFile, setConfigFile] = useState<File | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)

  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resp, setResp] = useState<RunResponse | null>(null)

  const configName = configFile?.name ?? ""
  const imageName = imageFile?.name ?? ""

  const configOk = useMemo(() => !!configFile && isAccepted(configName, ACCEPTED_CONFIG), [configFile, configName])
  const imageOk = useMemo(() => !!imageFile && isAccepted(imageName, ACCEPTED_IMAGES), [imageFile, imageName])

  async function run() {
    setError(null)
    setResp(null)

    if (!configFile) return setError("Selecione um arquivo .json de configuração.")
    if (!imageFile) return setError("Selecione uma imagem (.png, .tif ou .tiff).")
    if (!configOk) return setError("Config inválida: precisa ser .json.")
    if (!imageOk) return setError("Imagem inválida: precisa ser .png, .tif ou .tiff.")

    setBusy(true)
    try {
      const fd = new FormData()
      // nomes precisam bater com o FastAPI: run_filter(config=File(...), image=File(...))
      fd.append("config", configFile)
      fd.append("image", imageFile)

      const r = await fetch("/run", { method: "POST", body: fd })
      const data = (await r.json()) as any

      if (!r.ok) {
        const detail = data?.detail ? String(data.detail) : `HTTP ${r.status}`
        throw new Error(detail)
      }

      setResp(data as RunResponse)
    } catch (e: any) {
      setError(e?.message ?? "Erro desconhecido")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      {/* Vídeo de fundo */}
      <video className="bgVideo" autoPlay muted loop playsInline>
        <source src="imgs/video_bg.mp4" type="video/mp4" />
      </video>
      <div className="bgOverlay" />

      <header className="hero">
        <div className="heroInner">
          <div className="brand">
            <div className="brandMark">█</div>
            <div>
              <h1>Filtro RGB • Orquestrador</h1>
              <p>Envie a máscara (JSON) + imagem e gere o output.</p>
            </div>
          </div>

          <div className="heroCard">
            <div className="grid">
              <RunInputCard
                configFile={configFile}
                imageFile={imageFile}
                setConfigFile={setConfigFile}
                setImageFile={setImageFile}
                onRun={run}
                busy={busy}
                error={error}
              />
              <RunOutputCard resp={resp} />
            </div>
          </div>
        </div>
      </header>

      <footer className="footer">
        <span className="footerText">Tema Retro UI • Mariana Martins • Processamento Digital de Imagens</span>
      </footer>
    </div>
  )
}