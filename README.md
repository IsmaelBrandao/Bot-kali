[![CI](https://github.com/IsmaelBrandao/Bot-kali/actions/workflows/ci.yml/badge.svg)](https://github.com/IsmaelBrandao/Bot-kali/actions/workflows/ci.yml)

<p align="center">
  <img src="https://raw.githubusercontent.com/IsmaelBrandao/Bot-kali/master/kali-icon.png" width="120" alt="Bot-kali logo"/>
</p>

<h1 align="center">Bot-kali</h1>

<p align="center">
  Um bot musical para Discord, desenvolvido em Python, que integra Spotify e YouTube para reprodução de músicas,
  com fila, loop e paginação elegante.
</p>

---

## 🛠️ Tecnologias & Bibliotecas

* **Python 3.9+**
* **discord.py** (v2.x) – interação com a API do Discord e comandos de barra (`app_commands`).
* **yt-dlp** – extração de áudio e metadados do YouTube.

  * Utiliza a opção **`cookiesfrombrowser=['firefox']`** para acessar conteúdos com restrição de idade ou login.
* **spotipy** – integração com a API do Spotify para buscar faixas e metadados.
* **python-dotenv** – carregamento de variáveis de ambiente a partir de `.env`.
* **PyYAML** – leitura de configurações visuais (emojis) via `settings.yaml`.
* **FFmpeg** – decodificação e streaming de áudio no canal de voz do Discord.

---

## 📁 Estrutura do Projeto

```text
Bot-kali/
├── .env                # Variáveis de ambiente (token, credenciais Spotify)
├── .gitignore
├── requirements.txt    # Dependências do Python
├── README.md           # Documentação do projeto
├── LICENSE             # Licença MIT
├── assets/             # Ícone e outros recursos estáticos
├── bot/
│   ├── main.py         # Ponto de entrada; carrega cogs e inicia o bot
│   └── botclient.py    # Classe customizada de `commands.Bot`
├── cogs/
│   └── music.py        # Comandos de música: play, queue, skip, stop, loop, join, leave
├── config/
│   └── settings.yaml   # Emojis e configurações de embed
├── services/
│   ├── spotify_service.py  # Busca no Spotify via spotipy
│   └── youtube_service.py  # Busca no YouTube via yt-dlp (usa cookies para restrição)
└── utils/
    ├── embed_utils.py     # Funções para criar embeds personalizados
    └── music_utils.py     # Roteamento de consultas entre Spotify e YouTube
```

---

## ⚙️ Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/IsmaelBrandao/Bot-kali.git
   cd Bot-kali
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure seu arquivo `.env` (copie o `.env.example` se disponível):

   ```env
   DISCORD_TOKEN=seu_token_aqui
   SPOTIFY_CLIENT_ID=sua_client_id
   SPOTIFY_CLIENT_SECRET=seu_client_secret
   ```

---

## 🚀 Uso

* Inicie o bot:

  ```bash
  python bot/main.py
  ```

* Comandos disponíveis (barra `/` no Discord):

  | Comando          | Descrição                                          |
  | ---------------- | -------------------------------------------------- |
  | `/join`          | Faz o bot entrar no seu canal de voz               |
  | `/leave`         | Faz o bot sair do canal de voz                     |
  | `/play [q]`      | Toca música por link ou termo de busca             |
  | `/queue`         | Exibe fila de músicas com paginação (5 itens/pág.) |
  | `/skip`          | Pula a música atual                                |
  | `/stop`          | Para reprodução e limpa a fila                     |
  | `/loop [on/off]` | Ativa ou desativa loop da faixa atual              |

---

## 🧩 Detalhes de Implementação

1. **Detecção de plataforma**: a cada `/play`, o bot identifica se o link é do Spotify ou YouTube. Termos de busca são enviados ao YouTube.
2. **Serviços dedicados**:

   * `spotify_service.py`: busca metadados e duração via Spotipy.
   * `youtube_service.py`: extrai áudio e metadados via yt-dlp com **`cookiesfrombrowser`** para conteúdos restritos.
3. **Fila e reprodução**:

   * A fila (`self.queue`) armazena dicionários de músicas.
   * `_play_song` conecta ao canal de voz e inicia o fluxo de áudio com **FFmpeg**.
   * `start_time` marca o início da faixa para calcular o tempo restante em embeds.
4. **Embeds personalizados**:

   * `embed_utils.py` gera mensagens ricas com emojis, títulos e detalhes.
   * `QueuePaginator` implementa paginação em `/queue`, mostrando 5 itens por página e navegação por botões.

---

## 🤝 Contribuições

1. Fork este repositório.
2. Crie uma branch para sua feature: `git checkout -b feature/nome-da-feature`
3. Commit suas mudanças: `git commit -m "feat: descrição da feature"`
4. Push para a branch: `git push origin feature/nome-da-feature`
5. Abra um Pull Request aqui no GitHub.

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
