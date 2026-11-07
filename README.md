<div align="center">

# Redragon Battery Monitor

**Nível real da bateria do mouse Redragon M719RGB-PRO no Ubuntu**

[![Versão](https://img.shields.io/badge/vers%C3%A3o-0.4.0-2e9d4f?style=for-the-badge)](https://github.com/jean-devbr/redragon-battery-monitor/tree/v0.4.0)

![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-E95420?style=flat-square&logo=ubuntu&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-blue?style=flat-square)

**Português** · [English](README.en.md)

<img src=".github/assets/screenshot-pt.png" alt="Janela do Redragon Battery Monitor" width="380">

</div>

---

## Recursos

- Porcentagem real informada pelo próprio mouse
- Ícone na barra superior, com indicação de carregamento
- Aviso quando a bateria estiver baixa
- Funciona pelo receptor 2.4 GHz e pelo cabo USB-C
- Opção de iniciar junto com o sistema
- Interface em português e inglês
- Consulta também pelo terminal

## Requisitos

| | |
|---|---|
| **Sistema** | Ubuntu 24.04 (GNOME) |
| **Mouse** | Redragon M719RGB-PRO |
| **Conexão** | Receptor 2.4 GHz ou cabo USB-C (Bluetooth não é suportado) |

## Instalação

Abra o terminal e cole:

```bash
curl -fsSL https://raw.githubusercontent.com/jean-devbr/redragon-battery-monitor/main/get.sh | bash
```

> [!NOTE]
> Não use `sudo` no comando. A senha será pedida durante a instalação.

## Uso

Abra **Redragon Battery Monitor** no menu de aplicativos.

- O ícone na barra superior mostra a porcentagem. Borda amarela indica que está carregando.
- Fechar a janela mantém o programa na barra. Para encerrar, clique no ícone e escolha **Sair**.
- Na janela é possível ativar **Iniciar com o sistema**, ajustar o aviso de bateria baixa e escolher o **idioma**.

Pelo terminal:

```bash
redragon-battery
redragon-battery --lang en
```

## Idioma

O programa usa o idioma do Ubuntu automaticamente: português quando o sistema está em português e inglês nos demais casos. Para trocar, use o campo **Idioma** na janela ou a opção `--lang pt|en` no terminal.

## Atualização

Rode novamente o comando de instalação.

## Desinstalação

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

Distribuído sob a licença [MIT](LICENSE).
