# Redragon Battery Monitor

Mostra a porcentagem real da bateria do mouse **Redragon M719RGB-PRO** no Ubuntu,
com ícone na barra superior e aviso de bateria baixa.

**Versão atual: 0.1.1**

## Requisitos

- Ubuntu 24.04 (GNOME)
- Redragon M719RGB-PRO conectado pelo **receptor 2.4 GHz** ou pelo **cabo USB-C**
  (Bluetooth não é suportado)

## Instalar

Abra o terminal e cole:

```bash
curl -fsSL https://raw.githubusercontent.com/jean-devbr/redragon-battery-monitor/main/get.sh | bash
```

Não use `sudo` no comando. A senha será pedida durante a instalação.

## Usar

Abra **Redragon Battery Monitor** no menu de aplicativos.

- O ícone na barra superior mostra a porcentagem. Borda amarela = carregando.
- Fechar a janela mantém o programa na barra. Para encerrar: clique no ícone → **Sair**.
- Na janela é possível ativar **Iniciar com o sistema** e ajustar o aviso de bateria baixa.

Pelo terminal:

```bash
redragon-battery
```

## Atualizar

Rode o mesmo comando da instalação.

## Desinstalar

```bash
redragon-battery-uninstall
```

## Problemas comuns

| Mensagem | Solução |
|---|---|
| Mouse indisponível | Mexa o mouse e clique em **Atualizar agora**. Ele não responde enquanto está em repouso ou desligado. |
| Sem permissão para acessar o dispositivo | Desconecte e conecte novamente o receptor ou o cabo. |
| Nenhum Redragon M719RGB-PRO encontrado | Confira se o receptor ou o cabo está conectado. |
| `redragon-battery: command not found` | Saia da sessão e entre novamente. |

## Observações

- O nível exibido é o informado pelo próprio mouse e pode variar de 5 em 5 %.
- Ao conectar o cabo, o nível pode cair um pouco (ex.: 100 % → 95 %). É o comportamento do mouse.

## Licença

[MIT](LICENSE)
