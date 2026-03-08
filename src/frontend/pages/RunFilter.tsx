import React, { useMemo, useState } from "react"
import RunInputCard from "../components/RunInputCard"
import RunOutputCard from "../components/RunOutputCard"

export type RunResponse = {
  ok: boolean
  message?: string
  outputUrl?: string
  logs?: string[]
}

type ActivationType = "relu" | "identity"
type FilterType = "generic" | "sobel"

const ACCEPTED_IMAGES = [".png", ".tif", ".tiff"]
const ACCEPTED_MASKS = [".txt"]

function extOf(name: string) {
  const i = name.lastIndexOf(".")
  return i >= 0 ? name.slice(i).toLowerCase() : ""
}

function isAccepted(name: string, allowed: string[]) {
  return allowed.includes(extOf(name))
}

function buildConfigFile(params: {
  stride: number
  r: number
  activation: ActivationType
  filter_type: FilterType
}) {
  const json = JSON.stringify(params, null, 2)
  return new File([json], "config.json", { type: "application/json" })
}

export default function RunFilter() {
  const [maskFile, setMaskFile] = useState<File | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)

  const [stride, setStride] = useState(1)
  const [dilationRate, setDilationRate] = useState(1)
  const [activation, setActivation] = useState<ActivationType>("identity")
  const [filterType, setFilterType] = useState<FilterType>("generic")

  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resp, setResp] = useState<RunResponse | null>(null)

  const maskName = maskFile?.name ?? ""
  const imageName = imageFile?.name ?? ""

  const maskOk = useMemo(
    () => !!maskFile && isAccepted(maskName, ACCEPTED_MASKS),
    [maskFile, maskName]
  )

  const imageOk = useMemo(
    () => !!imageFile && isAccepted(imageName, ACCEPTED_IMAGES),
    [imageFile, imageName]
  )

  function validateOneToFive(value: number, label: string) {
    if (!Number.isInteger(value) || value < 1 || value > 5) {
      throw new Error(`${label} deve ser um inteiro entre 1 e 5.`)
    }
  }

  async function run() {
    setError(null)
    setResp(null)

    try {
      if (!maskFile) throw new Error("Selecione um arquivo de máscara .txt.")
      if (!imageFile) throw new Error("Selecione uma imagem (.png, .tif ou .tiff).")
      if (!maskOk) throw new Error("Máscara inválida: precisa ser .txt.")
      if (!imageOk) throw new Error("Imagem inválida: precisa ser .png, .tif ou .tiff.")

      validateOneToFive(stride, "Stride")
      validateOneToFive(dilationRate, "Taxa r")

      const configFile = buildConfigFile({
        stride,
        r: dilationRate,
        activation,
        filter_type: filterType,
      })

      const fd = new FormData()
      fd.append("config", configFile)
      fd.append("mask", maskFile)
      fd.append("image", imageFile)

      setBusy(true)

      const r = await fetch("http://127.0.0.1:8000/run", {
        method: "POST",
        body: fd,
      })

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

  function scrollToContent() {
    const el = document.getElementById("run-content")
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" })
    }
  }

  return (
    <div className="page runPage">
      <section className="landingHero">
        <div className="landingOverlay" />

        <div className="landingInner">
          <div className="landingTopbar">
            <div className="landingBrandBlock">
              <h1 className="landingTitle">AtrousLab</h1>
            </div>

            <details className="landingMenu">
              <summary className="landingMenuButton">Menu ▾</summary>

              <div className="landingDropdown">
                <a
                  className="landingDropdownLink"
                  href="https://github.com/marianamartiyns/AtrousLab"
                  target="_blank"
                  rel="noreferrer"
                >
                  Repositório
                </a>

                <a
                  className="landingDropdownLink"
                  href="/Relátorio - Projeto Prático.pdf"
                  target="_blank"
                  rel="noreferrer"
                >
                  Relatório
                </a>

                <button
                  type="button"
                  className="landingDropdownLink landingDropdownButton"
                  onClick={scrollToContent}
                >
                  Processar imagem
                </button>
              </div>
            </details>
          </div>

          <div className="landingVideoWrap">
            <video className="landingVideo" autoPlay muted loop playsInline>
              <source src="/imgs/video_bg.mp4" type="video/mp4" />
            </video>
          </div>
        </div>
      </section>

      <main id="run-content" className="contentSection">
        <div className="contentHeader">
          <h2>Painel de processamento</h2>
          <p>
            Configure os parâmetros, envie os arquivos e visualize o resultado
            do filtro logo abaixo.
          </p>
        </div>

        <div className="grid">
          <RunInputCard
            maskFile={maskFile}
            imageFile={imageFile}
            setMaskFile={setMaskFile}
            setImageFile={setImageFile}
            stride={stride}
            setStride={setStride}
            dilationRate={dilationRate}
            setDilationRate={setDilationRate}
            activation={activation}
            setActivation={setActivation}
            filterType={filterType}
            setFilterType={setFilterType}
            onRun={run}
            busy={busy}
            error={error}
          />

          <RunOutputCard resp={resp} />
        </div>
      </main>

      <footer className="footer">
        <span className="footerText">
          Mariana Martins • Processamento Digital de Imagens • Leonardo Vidal Batista
        </span>
      </footer>
    </div>
  )
}