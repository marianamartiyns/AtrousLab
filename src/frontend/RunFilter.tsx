import React, { useMemo, useRef, useState } from "react"

type RunResponse = {
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
  const ext = extOf(name)
  return allowed.includes(ext)
}

function prettyBytes(bytes?: number) {
  if (!bytes && bytes !== 0) return ""
  const units = ["B", "KB", "MB", "GB"]
  let n = bytes
  let u = 0
  while (n >= 1024 && u < units.length - 1) {
    n /= 1024
    u++
  }
  return `${n.toFixed(u === 0 ? 0 : 1)} ${units[u]}`
}

function truncateMiddle(s: string, max = 34) {
  if (!s) return s
  if (s.length <= max) return s
  const left = Math.ceil((max - 3) / 2)
  const right = Math.floor((max - 3) / 2)
  return `${s.slice(0, left)}...${s.slice(s.length - right)}`
}

type FilePickProps = {
  label: string
  hint: string
  accept: string
  file: File | null
  onPick: (f: File | null) => void
  validate: (f: File) => string | null
  buttonText: string
}

function FilePickerRetro({
  label,
  hint,
  accept,
  file,
  onPick,
  validate,
  buttonText,
}: FilePickProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [localErr, setLocalErr] = useState<string>("")

  function openPicker() {
    inputRef.current?.click()
  }

  function handleFile(f: File | null) {
    setLocalErr("")
    if (!f) {
      onPick(null)
      return
    }
    const err = validate(f)
    if (err) {
      setLocalErr(err)
      onPick(null)
      // limpa o input para permitir selecionar o mesmo arquivo depois
      if (inputRef.current) inputRef.current.value = ""
      return
    }
    onPick(f)
  }

  return (
    <div className="min-w-0">
      <div className="flex items-end justify-between gap-3">
        <label className="mono block text-xs text-white/85">{label}</label>

        {file ? (
          <button
            type="button"
            onClick={() => {
              handleFile(null)
              if (inputRef.current) inputRef.current.value = ""
            }}
            className="mono text-[11px] text-white/70 hover:text-white underline decoration-white/30 hover:decoration-white/60"
            title="Remover arquivo"
          >
            remover
          </button>
        ) : null}
      </div>

      {/* input real escondido */}
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0] || null
          handleFile(f)
        }}
      />

      {/* UI custom */}
      <div className="mt-2 glow rounded-2xl border border-[#39ff6a55] bg-[#050905]/70 p-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            {file ? (
              <>
                <div className="mono text-xs font-semibold text-white">
                  {truncateMiddle(file.name, 46)}
                </div>
                <div className="mono mt-1 text-[11px] text-white/65">
                  {prettyBytes(file.size)} • {extOf(file.name) || "—"}
                </div>
              </>
            ) : (
              <>
                <div className="mono text-xs font-semibold text-white/75">
                  Nenhum arquivo selecionado
                </div>
                <div className="mono mt-1 text-[11px] text-white/55">{hint}</div>
              </>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={openPicker}
              className={[
                "mono inline-flex items-center justify-center rounded-xl px-3 py-2 text-xs font-semibold transition",
                "border border-[#39ff6a] bg-[#071107] text-white glow-strong",
                "hover:bg-[#0E240E] active:translate-y-[1px]",
              ].join(" ")}
            >
              {buttonText}
            </button>

            {file ? (
              <div className="mono hidden text-[10px] text-white/60 sm:block">
                STATUS: OK
              </div>
            ) : (
              <div className="mono hidden text-[10px] text-white/45 sm:block">
                STATUS: WAITING
              </div>
            )}
          </div>
        </div>

        {localErr ? (
          <div className="mt-3 rounded-xl border border-[#ff4d4d66] bg-[#220606] p-2 mono text-[11px] text-[#ffd2d2]">
            {localErr}
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default function RunFilter() {
  const [configFile, setConfigFile] = useState<File | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [makeSobelVis, setMakeSobelVis] = useState(true)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>("")
  const [result, setResult] = useState<RunResponse | null>(null)

  const canRun = useMemo(() => {
    return !!configFile && !!imageFile && !loading
  }, [configFile, imageFile, loading])

  async function handleRun() {
    setError("")
    setResult(null)

    if (!configFile) return setError("Selecione o config.json.")
    if (!imageFile) return setError("Selecione uma imagem PNG/TIF.")

    if (!isAccepted(configFile.name, ACCEPTED_CONFIG)) {
      return setError("Config inválido. Use um arquivo .json.")
    }
    if (!isAccepted(imageFile.name, ACCEPTED_IMAGES)) {
      return setError("Imagem inválida. Use .png, .tif ou .tiff.")
    }

    setLoading(true)
    try {
      const form = new FormData()
      form.append("config", configFile)
      form.append("image", imageFile)
      form.append("makeSobelVis", String(makeSobelVis))

      const resp = await fetch("/api/run", {
        method: "POST",
        body: form,
      })

      const ct = resp.headers.get("content-type") || ""
      if (!resp.ok) {
        if (ct.includes("application/json")) {
          const j = await resp.json()
          throw new Error(j.message || j.detail || `Erro HTTP ${resp.status}`)
        } else {
          const t = await resp.text()
          throw new Error(t || `Erro HTTP ${resp.status}`)
        }
      }

      const data = (await resp.json()) as RunResponse
      setResult(data)

      if (!data.ok) setError(data.message || "Falha ao executar.")
    } catch (e: any) {
      setError(e?.message || "Erro desconhecido ao executar.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#070B07] text-white selection:bg-[#35ff6a] selection:text-black">
      <style>{`
        .crt-bg {
          background:
            radial-gradient(1000px 700px at 50% 10%, rgba(56,255,120,0.09), rgba(0,0,0,0) 55%),
            linear-gradient(180deg, rgba(10,16,10,1) 0%, rgba(6,9,6,1) 35%, rgba(3,5,3,1) 100%);
        }
        .crt-overlay::before {
          content: "";
          position: absolute;
          inset: 0;
          pointer-events: none;
          background: repeating-linear-gradient(
            to bottom,
            rgba(0,0,0,0.0),
            rgba(0,0,0,0.0) 2px,
            rgba(0,0,0,0.12) 3px
          );
          mix-blend-mode: overlay;
          opacity: 0.55;
        }
        .crt-overlay::after {
          content: "";
          position: absolute;
          inset: 0;
          pointer-events: none;
          background: radial-gradient(900px 520px at 50% 30%, rgba(80,255,130,0.12), rgba(0,0,0,0) 65%);
          opacity: 0.8;
        }
        .glow {
          box-shadow:
            0 0 0 1px rgba(80,255,130,0.35),
            0 0 18px rgba(80,255,130,0.18),
            inset 0 0 0 1px rgba(80,255,130,0.10);
        }
        .glow-strong {
          box-shadow:
            0 0 0 1px rgba(80,255,130,0.6),
            0 0 28px rgba(80,255,130,0.22),
            0 0 70px rgba(80,255,130,0.10);
        }
        .mono {
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
          letter-spacing: 0.2px;
        }
        .pixel {
          image-rendering: pixelated;
        }
        .focus-ring:focus-visible{
          outline: 2px solid rgba(57,255,106,0.65);
          outline-offset: 2px;
        }
        .soft-shadow{
          box-shadow:
            0 18px 60px rgba(0,0,0,0.55);
        }
      `}</style>

      {/* BG com vídeo */}
      <div className="relative min-h-screen overflow-hidden">
        <video
          className="absolute inset-0 h-full w-full object-cover opacity-20"
          src="public\imgs\video_bg.mp4"
          autoPlay
          loop
          muted
          playsInline
        />
        <div className="absolute inset-0 crt-bg opacity-95" />
        <div className="crt-overlay absolute inset-0" />

        {/* Conteúdo centralizado */}
        <div className="relative mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-10">
          {/* Header central */}
          <header className="mx-auto w-full max-w-4xl text-center">
            <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-[#39ff6a55] bg-[#081008cc] px-3 py-1 mono text-xs">
              <span className="h-2 w-2 rounded-full bg-[#39ff6a] shadow-[0_0_18px_rgba(57,255,106,0.7)]" />
              ORQUESTRADOR • RGB PIPELINE • ATRÓUS LAB
            </div>

            <h1 className="mono mt-4 text-2xl sm:text-3xl font-semibold text-white">
              RETRO UI — EXECUÇÃO DO FILTRO
            </h1>

            <p className="mono mx-auto mt-3 max-w-3xl text-sm text-white/70">
              Fluxo: carregar config → carregar imagem → aplicar filtro → pós-processar (se necessário) → salvar resultado
            </p>
          </header>

          {/* Preview central (moldura) */}
          <section className="mx-auto mt-8 w-full max-w-4xl">
            <div className="glow-strong soft-shadow relative overflow-hidden rounded-2xl border border-[#39ff6a55] bg-black/80">
              <div className="pointer-events-none absolute inset-0">
                <div className="absolute inset-x-0 top-0 h-10 bg-gradient-to-b from-[#39ff6a10] to-transparent" />
                <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-[#000000aa] to-transparent" />
                <div className="absolute left-3 top-3 mono text-[10px] text-white/70">
                  SIGNAL: OK • MODE: PREVIEW • FPS: AUTO
                </div>
                <div className="absolute right-3 top-3 mono text-[10px] text-white/70">
                  public\imgs\video_bg.mp4
                </div>
              </div>

              {/* vídeo decorativo */}
              <video
                className="pixel block aspect-video w-full object-cover opacity-90"
                src="public\imgs\video_bg.mp4"
                autoPlay
                loop
                muted
                playsInline
              />

              <div
                className="pointer-events-none absolute inset-0 opacity-60 mix-blend-overlay"
                style={{
                  background:
                    "repeating-linear-gradient(to bottom, rgba(0,0,0,0), rgba(0,0,0,0) 2px, rgba(0,0,0,0.18) 3px)",
                }}
              />
            </div>

            <div className="mt-4 text-center mono text-xs text-white/60">
              Role para baixo para carregar entradas e visualizar saídas.
            </div>
          </section>

          {/* Cards centralizados */}
          <main className="mx-auto mt-10 w-full max-w-4xl">
            <div className="grid gap-6">
              {/* ENTRADA */}
              <section className="glow relative overflow-hidden rounded-2xl border border-[#39ff6a55] bg-[#050905]/80">
                <div className="border-b border-[#39ff6a33] bg-[#071107]/80 px-5 py-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <h2 className="mono text-sm font-semibold text-white">ENTRADA</h2>
                    <div className="mono text-[10px] text-white/60">
                      ACCEPT: .json • .png/.tif/.tiff
                    </div>
                  </div>
                </div>

                <div className="p-5">
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <FilePickerRetro
                      label="Config (.json)"
                      hint="Selecione o arquivo de configuração do filtro"
                      accept=".json,application/json"
                      file={configFile}
                      buttonText="SELECIONAR"
                      validate={(f) =>
                        isAccepted(f.name, ACCEPTED_CONFIG)
                          ? null
                          : "Config inválido. Use um arquivo .json."
                      }
                      onPick={(f) => {
                        setConfigFile(f)
                        setResult(null)
                        setError("")
                      }}
                    />

                    <FilePickerRetro
                      label="Imagem (PNG/TIF)"
                      hint="Selecione uma imagem .png/.tif/.tiff"
                      accept=".png,.tif,.tiff,image/png,image/tiff"
                      file={imageFile}
                      buttonText="ENVIAR IMG"
                      validate={(f) =>
                        isAccepted(f.name, ACCEPTED_IMAGES)
                          ? null
                          : "Imagem inválida. Use .png, .tif ou .tiff."
                      }
                      onPick={(f) => {
                        setImageFile(f)
                        setResult(null)
                        setError("")
                      }}
                    />
                  </div>

                  <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <label className="flex items-center gap-3">
                      <input
                        id="sobelVis"
                        type="checkbox"
                        className="h-4 w-4 accent-[#39ff6a]"
                        checked={makeSobelVis}
                        onChange={(e) => setMakeSobelVis(e.target.checked)}
                      />
                      <span className="mono text-xs text-white/80">
                        Gerar visualização Sobel (abs → min/max → expansão [0..255])
                      </span>
                    </label>

                    <div className="mono text-[11px] text-white/55">
                      {configFile ? `Config: ${truncateMiddle(configFile.name, 42)}` : "Config: —"}{" "}
                      <span className="mx-2 text-white/25">|</span>
                      {imageFile ? `Imagem: ${truncateMiddle(imageFile.name, 42)}` : "Imagem: —"}
                    </div>
                  </div>

                  <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex flex-wrap items-center gap-3">
                      <button
                        onClick={handleRun}
                        disabled={!canRun}
                        className={[
                          "focus-ring mono inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-xs font-semibold transition",
                          "border",
                          canRun
                            ? "border-[#39ff6a] bg-[#0A1A0A] text-white glow-strong hover:bg-[#0E240E] active:translate-y-[1px]"
                            : "border-[#2b4b2b] bg-[#061006] text-white/35 cursor-not-allowed",
                        ].join(" ")}
                      >
                        {loading ? "EXECUTANDO..." : "EXECUTAR"}
                      </button>

                      <button
                        onClick={() => {
                          setConfigFile(null)
                          setImageFile(null)
                          setResult(null)
                          setError("")
                        }}
                        className="focus-ring mono inline-flex items-center justify-center rounded-xl border border-[#39ff6a55] bg-[#040804] px-5 py-2.5 text-xs font-semibold text-white/80 glow hover:bg-[#071107] active:translate-y-[1px]"
                      >
                        LIMPAR
                      </button>
                    </div>

                    <div className="mono text-[10px] text-white/55">
                      STATE:{" "}
                      <span className={loading ? "text-[#39ff6a]" : "text-white/70"}>
                        {loading ? "RUNNING" : canRun ? "READY" : "IDLE"}
                      </span>
                    </div>
                  </div>

                  {error ? (
                    <div className="glow mt-5 rounded-xl border border-[#ff4d4d66] bg-[#220606] p-3 mono text-xs text-[#ffd2d2]">
                      {error}
                    </div>
                  ) : null}
                </div>
              </section>

              {/* SAÍDA */}
              <section className="glow relative overflow-hidden rounded-2xl border border-[#39ff6a55] bg-[#050905]/80">
                <div className="border-b border-[#39ff6a33] bg-[#071107]/80 px-5 py-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <h2 className="mono text-sm font-semibold text-white">SAÍDA</h2>
                    <div className="mono text-[10px] text-white/60">
                      OUTPUTS • RGB RESULT • SOBEL VIS • LOGS
                    </div>
                  </div>
                </div>

                <div className="p-5">
                  {!result ? (
                    <div className="rounded-2xl border border-[#39ff6a22] bg-black/30 p-6 text-center">
                      <p className="mono text-xs text-white/60">Nenhum resultado ainda.</p>
                      <p className="mono mt-2 text-[11px] text-white/45">
                        Faça upload do config e da imagem e clique em <span className="text-white/70">EXECUTAR</span>.
                      </p>
                    </div>
                  ) : (
                    <div className="grid gap-6">
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div className="glow rounded-2xl border border-[#39ff6a55] bg-[#020402]/70 p-3">
                          <div className="flex items-center justify-between gap-3">
                            <p className="mono text-xs font-semibold text-white">RESULTADO (RGB)</p>
                            {result.outputUrl ? (
                              <a
                                href={result.outputUrl}
                                className="mono text-[11px] font-semibold text-[#39ff6a] hover:underline"
                                download
                              >
                                BAIXAR
                              </a>
                            ) : null}
                          </div>

                          {result.outputUrl ? (
                            <img
                              src={result.outputUrl}
                              alt="Resultado"
                              className="pixel mt-3 w-full rounded-xl border border-[#39ff6a33] object-contain bg-black/20"
                            />
                          ) : (
                            <p className="mono mt-3 text-xs text-white/60">Sem outputUrl.</p>
                          )}
                        </div>

                        <div className="glow rounded-2xl border border-[#39ff6a55] bg-[#020402]/70 p-3">
                          <div className="flex items-center justify-between gap-3">
                            <p className="mono text-xs font-semibold text-white">SOBEL (VISUALIZAÇÃO)</p>
                            {result.sobelVisUrl ? (
                              <a
                                href={result.sobelVisUrl}
                                className="mono text-[11px] font-semibold text-[#39ff6a] hover:underline"
                                download
                              >
                                BAIXAR
                              </a>
                            ) : null}
                          </div>

                          {result.sobelVisUrl ? (
                            <img
                              src={result.sobelVisUrl}
                              alt="Sobel visualização"
                              className="pixel mt-3 w-full rounded-xl border border-[#39ff6a33] object-contain bg-black/20"
                            />
                          ) : (
                            <p className="mono mt-3 text-xs text-white/60">
                              (Opcional) habilite “Gerar visualização Sobel”.
                            </p>
                          )}
                        </div>
                      </div>

                      {result.logs?.length ? (
                        <div className="glow rounded-2xl border border-[#39ff6a55] bg-[#020402]/70 p-3">
                          <div className="flex items-center justify-between">
                            <p className="mono text-xs font-semibold text-white">LOGS</p>
                            <span className="mono text-[10px] text-white/55">
                              linhas: {result.logs.length}
                            </span>
                          </div>
                          <pre className="mono mt-2 max-h-72 overflow-auto rounded-xl border border-[#39ff6a33] bg-black/60 p-3 text-[11px] text-white">
{result.logs.join("\n")}
                          </pre>
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              </section>
            </div>

            <footer className="mt-10 text-center mono text-[10px] text-white/45">
              © AtrousLab • Retro UI • {new Date().getFullYear()}
            </footer>
          </main>
        </div>
      </div>
    </div>
  )
}