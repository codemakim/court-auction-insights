# 2026-05-19 외부 접속 가이드 정리

## 작업 내용
- Tailscale 외부 접속용 URL을 확인했다.
- Vite dev server가 `tailcode-wsl` 및 Tailscale IP Host header를 허용하도록 설정했다.
- 인사이트 화면을 외부에서 볼 수 있도록 Vite를 `0.0.0.0:5173`으로 재기동했다.

## 오류 증상
- 서버 내부에서는 5173 화면을 볼 수 있지만 외부 기기에서는 host/allowed-host 또는 bind 문제로 접근이 막힐 수 있었다.

## 원인
- Vite가 `127.0.0.1`에만 bind되어 있었다.
- allowedHosts에 Tailscale short hostname과 IP가 빠져 있었다.

## 조치
- `frontend/vite.config.ts` allowedHosts에 `tailcode-wsl`, `tailcode-wsl.tail81a535.ts.net`, `100.99.226.35` 추가.
- frontend dev server를 `--host 0.0.0.0`으로 재시작.

## 검증
- `npm run build` 성공.
- 로컬에서 `http://127.0.0.1:5173`, `http://127.0.0.1:8788/status` 확인.

## 결과/남은 확인
- 외부 기기에서는 Tailscale이 켜진 상태에서 `http://tailcode-wsl:5173` 또는 `http://100.99.226.35:5173`으로 확인한다.
