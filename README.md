# 📚 MISSÃO BIBLIOTECA

Jogo 2D educativo feito em Python + Pygame.  
Pegue livros que caem do céu, desvie de itens negativos e suba no ranking!

---

## 🚀 Como rodar

### Requisitos
- Python 3.10 ou superior
- pip

### Instalação rápida

```bash
# 1. Instale o Pygame
pip install pygame

# 2. Entre na pasta do jogo
cd missao_biblioteca

# 3. Rode!
python main.py
```

---

## 🎮 Controles

| Ação              | Tecla / Botão          |
|-------------------|------------------------|
| Mover esquerda    | ← ou A                 |
| Mover direita     | → ou D                 |
| Pausar            | P                      |
| Mutar som         | M                      |
| Sair (em jogo)    | ESC                    |
| Touch (celular)   | Botões ◀ ▶ na tela     |

---

## ⭐ Pontuação

| Item            | Efeito              |
|-----------------|---------------------|
| 📗 Livro comum  | +5 a +20 pts        |
| ⭐ Livro Dourado | +100 pts (3s na tela)|
| 📱 Celular      | -50 pts             |
| 🚬 Cigarro      | ZERA tudo!          |
| ⏰ Relógio      | +10 segundos        |
| 🛡 Escudo       | Bloqueia 1 negativo |
| 🧲 Ímã          | Atrai livros (5s)   |

---

## 🔥 Combos e Modo Febre

- **3 livros seguidos** → +20 bônus  
- **5 livros seguidos** → +50 bônus  
- **10 livros seguidos** → 🔥 MODO FEBRE (pontos ×2 por 5s)

---

## 📁 Estrutura do projeto

```
missao_biblioteca/
├── main.py        ← Ponto de entrada, loop principal
├── config.py      ← Todas as constantes e configurações
├── player.py      ← Personagem e animações
├── items.py       ← Livros, itens negativos, especiais
├── effects.py     ← Partículas, textos flutuantes, flash
├── ui.py          ← HUD, menus, telas
├── ranking.py     ← Camada de ranking
├── database.py    ← SQLite (salvar/ler pontuações)
├── requirements.txt
└── ranking.db     ← Criado automaticamente ao jogar
```

---

## 🛠️ Personalização fácil

Edite `config.py` para ajustar:
- `GAME_DURATION` — duração da partida
- `ITEM_BASE_SPEED` — velocidade inicial
- `BOOKS` — matérias, pontos e cores
- `COMBO_FEVER_AT` — combo necessário para Modo Febre
- `GOLDEN_CHANCE` — frequência do livro dourado

---

## 📱 Futuro (mobile)

O jogo já detecta eventos touch (`FINGERDOWN`/`FINGERUP`) e possui
botões ◀ ▶ na tela. Para compilar para Android use **Buildozer** ou **PyDroid 3**.

---

Feito com ❤️ e Python 🐍
