# SOP: dominio, DNS, web y correo

> **Validado** el 2026-10-31. Configuración de una sola vez; este documento sirve para
> saber qué hay montado y para rehacerlo si algo se rompe.

## Quién hace qué

| Pieza | Dónde | Notas |
|---|---|---|
| Registro del dominio `spanishnav.al` | **Upflare** (app.upflare.com) | Cuenta de Andrei. Renovación automática, vence el 2028-05-25 |
| DNS (la lista de registros) | **Cloudflare**, plan Free | Servidores `ara.ns.cloudflare.com` y `jasper.ns.cloudflare.com`. Zona activa desde el 2026-10-31 |
| Web | **Vercel** | Repo `DreiSup/spanishnaval-web`, rama `main` |
| Correo `podcast@spanishnav.al` | **Zoho Mail** (región EU) | SPF, DKIM y DMARC en el DNS |
| Audio público | **Cloudflare R2**, bucket `spanishnaval` | Servido en `audio.spanishnav.al`. Ver [`audio-r2.md`](audio-r2.md) |

Hasta el 2026-10-31 el DNS lo servía Upflare (`park1/park2.uwsdns.com`). Se pasó a
Cloudflare porque R2 solo admite un subdominio propio si el dominio entero está en la misma
cuenta de Cloudflare; la alternativa (configuración parcial) es solo de los planes de pago
Business y Enterprise.

## Registros DNS

En Cloudflare → `spanishnav.al` → **DNS** → **Records**. Son 12, más el de R2:

| Tipo | Nombre | Valor | Proxy | Para qué |
|---|---|---|---|---|
| A | `spanishnav.al` | `216.198.79.1` | DNS only | Web en Vercel |
| CNAME | `www` | `2cedac491a9b6f67.vercel-dns-017.com` | DNS only | Web en Vercel |
| MX 10 | `spanishnav.al` | `mx.zoho.eu` | — | Correo |
| MX 20 | `spanishnav.al` | `mx2.zoho.eu` | — | Correo |
| MX 50 | `spanishnav.al` | `mx3.zoho.eu` | — | Correo |
| TXT | `spanishnav.al` | `v=spf1 include:zohomail.eu ip4:94.130.228.177 +include:relay.mailchannels.net ~all` | — | SPF |
| TXT | `zmail._domainkey` | `v=DKIM1; k=rsa; p=…` (clave pública de Zoho) | — | DKIM |
| TXT | `_dmarc` | `v=DMARC1; p=reject; sp=reject; rf=afrf; pct=100; ri=86400` | — | DMARC |
| TXT | `spanishnav.al` | `zoho-verification=zb07076434.zmverify.zoho.eu` | — | Verificación de Zoho |
| CNAME | `zb07076434` | `zmverify.zoho.eu` | DNS only | Verificación de Zoho |
| CNAME | `mail` | `spanishnav.al` | DNS only | Resto de Upflare, sin uso |
| CNAME | `ftp` | `spanishnav.al` | DNS only | Resto de Upflare, sin uso |
| R2 | `audio` | bucket `spanishnaval` | Proxied | Lo crea R2 solo al conectar el dominio |

Reglas:

- **Los registros de la web van en "DNS only" (nube gris).** Vercel desaconseja poner el
  proxy de Cloudflare delante. Cloudflare avisa de que el dominio "no está protegido": se
  ignora.
- **DMARC está en `p=reject`.** Si la clave DKIM se corta o se pierde un registro de Zoho,
  el correo saliente se rechaza. Cualquier cambio en los TXT del correo, con cuidado.
- `mail`, `ftp`, la parte `ip4:…` y `mailchannels` del SPF vienen de la configuración por
  defecto de Upflare. No los usa nadie. Se pueden limpiar más adelante, de uno en uno y
  comprobando el correo después de cada cambio.

## Si hay que rehacer el paso a Cloudflare

Lo que se hizo, en orden:

1. En el panel DNS del proveedor antiguo, captura de todos los registros.
2. Cloudflare → **Add a domain** → `spanishnav.al` → plan **Free** → importación automática.
   No marcar "I monetize pages that serve ads" ni bloquear bots de Search.
3. Comparar lo importado con la captura. La importación se dejó fuera el CNAME
   `zb07076434` y hubo que añadirlo a mano. Poner A y CNAME en **DNS only**.
4. Comprobar que el dominio no tiene DNSSEC en el registrador (no tenía).
5. En Upflare → **My Domains** → `spanishnav.al` → **Nameservers** → **Use custom
   nameservers**, poner solo los dos de Cloudflare y guardar. **Ojo**: es la pestaña
   Nameservers del dominio, no el "DNS Manager". La primera vez el cambio no se aplicó y
   hubo que repetirlo.
6. Esperar a que Cloudflare marque la zona como **Active** (llega un correo). Tardó más de
   un día desde el primer intento.
7. Comprobar que la web carga y que el correo entra y sale.

## Comprobaciones rápidas

- **Servidores DNS actuales:** `nslookup -type=NS spanishnav.al 1.1.1.1`, o
  whatsmydns.net con tipo NS.
- **Web:** abrir https://spanishnav.al.
- **Correo:** mandar un correo a `podcast@spanishnav.al` desde otra cuenta y contestar
  desde Zoho.
