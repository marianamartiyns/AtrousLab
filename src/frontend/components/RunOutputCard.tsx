import React from "react"
import type { RunResponse } from "../pages/RunFilter"

type Props = {
  resp: RunResponse | null
}

export default function RunOutputCard({ resp }: Props) {
  const imgUrl = resp?.outputUrl ?? null

  return (
    <section className="card">
      <div className="cardHeader">
        <h2>Saídas</h2>
        <span className="badge">OUTPUT</span>
      </div>

      {!resp ? (
        <div className="empty">
          <div className="scanline" />
          <p>Nenhum resultado ainda. Envie a máscara, escolha os parâmetros e rode o filtro.</p>
        </div>
      ) : (
        <>
         {/* <div className="statusRow">
            <span className={resp.ok ? "pill ok" : "pill err"}>
              {resp.ok ? "OK" : "ERRO"}
            </span>
            {resp.message ? <span className="msg">{resp.message}</span> : null}
          </div> */}

          {imgUrl ? (
            <div className="preview">
              <img src={imgUrl} alt="Resultado processado" />
              <div className="previewBar">
                <a className="link" href={imgUrl} target="_blank" rel="noreferrer">
                  Abrir imagem
                </a>
              </div>
            </div>
          ) : (
            <div className="empty">
              <p>Sem outputUrl retornado.</p>
            </div>
          )}

          {resp.logs?.length ? (
            <div className="logs">
              <div className="logsTitle">Logs</div>
              <pre>{resp.logs.join("\n")}</pre>
            </div>
          ) : null}
        </>
      )}
    </section>
  )
}