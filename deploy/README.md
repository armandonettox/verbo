# Deploy do verbo na VPS

O verbo roda na mesma VM Oracle do hera, em um projeto e um pod proprios (`pod_verbo`),
atras do Cloudflare em `verbo.armandonetto.com`.

```
visitante -> Cloudflare -> nginx do host (443) -> container frontend (127.0.0.1:8020)
                                                      |-> arquivos do React
                                                      |-> /api -> container backend (:8000)
```

## O que o deploy automatico faz

O workflow `.github/workflows/deploy.yml` roda quando o workflow `testes` passa na `master`
(ou manualmente em Actions > deploy > Run workflow):

1. Constroi as imagens do backend e do frontend para ARM64 e envia ao GHCR
   (`ghcr.io/armandonettox/verbo-backend` e `verbo-frontend`, tag com os 12 primeiros
   caracteres do commit).
2. Entra na VPS por SSH, envia `docker-compose.yml` e `deploy/`, baixa as imagens e reinicia
   o verbo (`verbo-compose.service`).
3. Confere a saude por ate 90 s. Se falhar, volta para as imagens anteriores e o job termina
   com erro.
4. Sincroniza a config do nginx do host, mas so se o certificado do Cloudflare ja existir, e
   desfaz a copia se o `nginx -t` falhar (para nao quebrar o proximo deploy do hera).
5. Apaga imagens antigas, mantendo a atual e a anterior.

O script nunca mexe no pod do hera e nao mata o `aardvark-dns`.

## Passos manuais, uma unica vez

Estes passos mudam a VPS e o Cloudflare. Faca na ordem.

### 1. Cloudflare

- DNS: registro `verbo` apontando para o mesmo destino do `hera`, com o proxy ligado.
- SSL/TLS: nao precisa gerar certificado. O verbo reaproveita o Origin Certificate do hera,
  que e wildcard (`*.armandonetto.com`, valido ate 2041) e ja esta na VM em
  `/etc/ssl/cloudflare/hera.armandonetto.com.pem` e `.key`. Para conferir os nomes cobertos:
  `sudo openssl x509 -in /etc/ssl/cloudflare/hera.armandonetto.com.pem -noout -ext subjectAltName`.
  Nao apague nem renomeie esses arquivos, porque o verbo depende deles.
- Authenticated Origin Pulls ja esta ativo para o dominio, e a CA
  `/etc/ssl/cloudflare/origin_pull_ca.pem` ja existe por causa do hera.

### 2. VPS

```bash
mkdir -p ~/verbo
# arquivo com a chave da NVIDIA (nao versionado, nao enviar para o git)
umask 077 && printf 'NVIDIA_API_KEY=cole_a_chave_aqui\n' > ~/verbo/.env
```

### 3. Indices vetoriais

Os indices (`biblia-nemotron` e `biblia-local`, ~110 MB) sao gerados na maquina de
desenvolvimento e ficam em `.indices/chroma-db`, fora do git. Eles precisam ir para o volume
do backend uma vez, depois que a primeira imagem existir (o primeiro deploy sobe o app com
a saude "degradada" ate isso ser feito):

```bash
# na maquina de desenvolvimento
scp -r .indices/chroma-db USUARIO@IP_DA_VPS:~/indices-verbo/

# na VPS (um container descartavel com o volume montado; ajuste a tag da imagem)
podman run --rm --user 0 \
  -v verbo_verbo-dados:/dados \
  -v ~/indices-verbo:/origem:ro,Z \
  ghcr.io/armandonettox/verbo-backend:TAG \
  sh -c 'cp -r /origem/chroma-db /dados/ && chown -R 1000:1000 /dados'
systemctl --user restart verbo-compose.service
```

O nome do volume depende do nome do projeto no podman-compose (`podman volume ls` mostra o
certo). O Chroma escreve no arquivo mesmo so lendo, por isso o `chown` para o usuario do
container.

### 4. Secrets do GitHub

Em Settings > Secrets and variables > Actions, no repositorio `verbo`:

| Secret | Valor |
|--------|-------|
| `VPS_HOST` | IP publico (reservado) da VM |
| `VPS_USER` | usuario SSH da VM |
| `VPS_SSH_KEY` | chave privada dedicada ao deploy do verbo (gere um par novo; nao reutilize a do hera) |
| `VPS_KNOWN_HOSTS` | saida de `ssh-keyscan -t ed25519 IP_DA_VPS`, conferida com a impressao digital do servidor antes de salvar |

A chave publica do par vai em `~/.ssh/authorized_keys` da VM. O usuario precisa de `sudo` sem
senha (o hera ja depende disso) para o nginx do host.

### 5. Primeiro deploy

Rode manualmente o workflow `deploy` e acompanhe o log. Depois confira:

```bash
curl -s http://127.0.0.1:8020/api/saude     # na VPS
curl -sI https://verbo.armandonetto.com/    # de fora
```

## Operacao

- Ver o estado: `podman ps --filter name=verbo` e `journalctl --user -u verbo-compose.service`.
- Reiniciar: `systemctl --user restart verbo-compose.service`. Nao use `podman rm -f` em um
  container solto: no podman-compose isso derruba a rede dos outros do mesmo pod.
- Rollback manual: copie `~/verbo/.env.imagens.anterior` para `~/verbo/.env.imagens` e
  reinicie o servico.
- Trocar o modelo da NVIDIA quando ele for aposentado: defina `VERBO_EMBEDDING_MODEL`,
  `VERBO_CHAT_MODEL` e `VERBO_COLLECTION_NAME` no `~/verbo/.env`, gere um indice novo (veja
  `scripts/construir_banco.py`) e copie para o volume como no passo 3.

## Riscos conhecidos

- O fallback local carrega o modelo na primeira vez que a NVIDIA falha e passa a ocupar
  ~1 GiB de RAM. O container tem limite de 1,5 GB para nao afetar o hera.
- O rate limit por IP depende de o nginx do host mandar `X-Real-IP` com o valor de
  `CF-Connecting-IP`. Sem isso, todos os visitantes dividem o mesmo limite.
- O modo "pod" do podman-compose (frontend chegando no backend por `127.0.0.1`) foi
  desenhado a partir da documentacao do hera, mas nao foi testado nesta VM.
