## Tujuan
- Membangun service FastAPI untuk memonitor transaksi wallet di Sepolia via Etherscan API, dengan validasi alamat, rate limit per IP, logging terstruktur, dan output yang selaras dengan skema database contohDatabase.sql.

## Struktur Proyek
- `app/main.py`: bootstrap FastAPI, middleware, logging, rate limiter, router.
- `app/config.py`: konfigurasi via environment (ETHERSCAN_API_KEY, RATE_LIMIT, LOG_LEVEL).
- `app/logging.py`: setup structured logging (JSON) dan middleware timing.
- `app/routers/monitor.py`: route `/monitor/wallet`.
- `app/services/etherscan_client.py`: pemanggil API Etherscan dengan retry/timeout.
- `app/services/processor.py`: pemrosesan respons (filter 50, transform, konversi wei→ETH, mapping DB).
- `app/models/schemas.py`: Pydantic models untuk request/response & DB mapping.
- `tests/`: unit tests (validator, parsing, error handling) + coverage.
- `requirements.txt`, `Dockerfile`.

## Endpoint & Validasi
- Route: `GET /monitor/wallet`.
- Query param: `address: str`.
- Validasi alamat: regex `^0x[a-fA-F0-9]{40}$`.
- Jika invalid: HTTP 400 dengan payload `{"status": "error", "data": [], "metadata": {"count": 0, "wallet": address, "network": "sepolia"}}`.
- Dokumentasi Swagger: contoh request `?address=0x...` dan contoh response sukses/gagal melalui `examples` di Pydantic.

## Klien Etherscan
- Base URL: `https://api-sepolia.etherscan.io/api`.
- Query wajib: `module=account&action=txlist&address={address}&apikey={ETHERSCAN_API_KEY}`.
- `aiohttp.ClientSession` dengan `ClientTimeout(total=10)`.
- Retry 3x untuk HTTP 5xx: loop manual dengan exponential backoff ringan (mis. 0.2s, 0.5s, 1s), hanya ulang jika status 5xx atau koneksi bermasalah.
- Error handling:
  - Network error/timeout → status `error`.
  - Rate limit Etherscan (`message: NOTOK`, `result: Max rate limit reached`) → status `error` khusus rate limit.
  - Invalid API response (schema tidak sesuai/`status` field tidak ada) → status `error`.
- Structured logging untuk tiap pemanggilan: `wallet`, `attempt`, `status_code`, `latency_ms`, `url`.

## Pemrosesan Respons
- Ambil `result` (list transaksi) dari respons Etherscan.
- Sort desc by `timeStamp` lalu ambil max 50.
- Transform tiap item menjadi:
  - `tx_hash`: `hash`
  - `block_number`: int(`blockNumber`)
  - `timestamp`: ISO8601 UTC dari `timeStamp` (detik → `datetime.utcfromtimestamp(...).isoformat()`)
  - `from`: `from`
  - `to`: `to`
  - `value_eth`: float(wei / 1e18) dari `value`
  - `status`: `success` jika `isError == '0'` else `failed`
  - `gas_used`: int(`gasUsed`)
- Metadata: `count` jumlah item dikembalikan, `wallet` alamat input, `network: 'sepolia'`.
- Kinerja: ukur durasi endpoint dan log sebagai metric.

## Mapping ke Skema Database
- Tabel target: `transaction` (lihat contohDatabase.sql).
- Fungsi mapping `to_db_row(tx_item, wallet_id, network_id)` menghasilkan dict:
  - `network_id`: id jaringan (Sepolia; `chain_id=11155111`).
  - `wallet_id`: di-resolve dari tabel `wallet` (opsional; jika integrasi DB aktif).
  - `tx_hash`, `block_number`, `time_stamp` (datetime from timestamp), `from_address`, `to_address`, `value_eth`, `gas_used`, `tx_fee_eth` (hitung `gasPrice * gasUsed / 1e18` jika tersedia, default 0), `direction` (`in`/`out`/`self` berdasarkan perbandingan alamat), `status` (`success`/`failed`).
- Disediakan model Pydantic `DbTransaction` dengan field sesuai kolom untuk validasi sebelum tulis.
- Catatan: penulisan ke DB dapat diaktifkan kemudian (opsional), saat ini fokus menyelaraskan struktur output.

## Rate Limiting per IP
- Gunakan `slowapi` dengan `Limiter(key_func=get_remote_address, default_limits=[f"{RATE_LIMIT}/minute"])`.
- Tambahkan middleware ke FastAPI; respons 429 otomatis untuk over-limit.
- Log event rate-limit.

## Logging Terstruktur
- `structlog` dengan JSON renderer.
- Context per request: `request_id`, `client_ip`, `path`, `method`.
- Event: setiap API call ke Etherscan, error events (exception, HTTP errors), performance metrics (durasi endpoint, size list transaksi).

## Konfigurasi via ENV
- `ETHERSCAN_API_KEY`: wajib.
- `RATE_LIMIT`: default `5` (requests/minute/IP).
- `LOG_LEVEL`: default `INFO`.
- Loader via `pydantic-settings`, dukung `.env` lokal.

## Pydantic Models
- `WalletQuery`: validasi query `address` (regex).
- `TransactionItem`: model untuk hasil transformasi.
- `MonitorResponse`: `{status, data: List[TransactionItem], metadata}`.
- `DbTransaction`: untuk mapping ke skema DB (tidak dikembalikan ke klien).

## Swagger / OpenAPI
- Tambahkan `response_model=MonitorResponse` pada endpoint.
- Sertakan `examples` untuk sukses dan error.
- Deskripsikan parameter `address` dan batasan regex.

## Pengujian & Coverage ≥80%
- `tests/test_validation.py`: berbagai kasus alamat (valid/invalid panjang, non-hex, tanpa prefix).
- `tests/test_processor.py`: parsing list Etherscan ke `TransactionItem`, sort & limit 50, konversi wei→ETH, status success/failed.
- `tests/test_errors.py`: simulasi network error, 5xx retry berfungsi, rate limit Etherscan → status error.
- Mock `aiohttp` dengan `aioresponses` untuk kontrol respons.
- Jalankan `pytest --cov=app` dan target ≥80%.

## Dockerfile
- Base: `python:3.11-slim`.
- Copy `requirements.txt`, install, copy source.
- Env: `LOG_LEVEL`, `RATE_LIMIT` (default), `ETHERSCAN_API_KEY` via runtime.
- CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

## Requirements (pinned)
- `fastapi==0.115.5`
- `uvicorn[standard]==0.31.0`
- `aiohttp==3.10.10`
- `slowapi==0.1.8`
- `limits==3.10.0`
- `structlog==24.1.0`
- `pydantic==2.8.2`
- `pydantic-settings==2.6.1`
- `aioresponses==0.7.6`
- `pytest==8.3.3`
- `pytest-asyncio==0.24.0`
- `pytest-cov==5.0.0`

## Verifikasi
- Manual: jalankan `GET /monitor/wallet?address=0x...` dan periksa respons format, limit 50, konversi ETH.
- Observasi logs JSON untuk call Etherscan dan metrics durasi.
- Pastikan rate limiting 5/min/IP aktif (uji dengan loop request cepat).

## Setelah Konfirmasi
- Implementasi kode lengkap sesuai struktur di atas, termasuk models, router, services, logging, tests, Dockerfile, dan requirements pinned.
- Opsi berikutnya: menambahkan repository DB (SQLAlchemy) untuk insert `transaction`, resolve `wallet_id/network_id` dari tabel existing, dan seeding network `sepolia (chain_id=11155111)` jika belum ada.