# VEREDITO: A Balança do Poder ⚖️💵

Jogo interativo desenvolvido em Python utilizando **Pygame** e **OpenCV**, preparado para compilação em executável (.exe).

---

## 🌟 Funcionalidades e Sistema de Capas Dinâmicas

- **Menu Principal Glassmorphism**: Interface visual elegante com botões translúcidos, efeitos de elevação e transições de cor suaves.
- **Sistema de Capas Dinâmicas (`CoverManager`)**:
  - **Capa Principal (Padrão)**: Vídeo em loop contínuo Ping-Pong (`frente` -> `reverso`) a velocidade cinematográfica de **0.8x**.
  - **Final Ruim 1 (Animação Estendida)**: Sequência encadeada das Animações 1 e 2 rodando a **0.8x de velocidade** com **piscar de preto de 0.5 segundos no plano de fundo** na transição de um vídeo para o outro (mantendo os menus e interface do jogo visíveis e interativos).
- **Trilha Sonora Sincronizada (`AudioManager`)**:
  - Toca `msc final ruim 1.mp3` de forma contínua durante todo o ciclo das animações de vídeo.
  - **Loop com Pausa**: Quando a música termina de tocar, aguarda **2 segundos** de silêncio e reinicia automaticamente do começo.
  - Interrompe a música com fade-out suave ao retornar à Capa Principal.
- **Sistema de História & Escolhas**:
  - No modo **"NOVO JOGO"**, o jogador assume o papel do magistrado e enfrenta dilemas éticos.
  - Conforme as escolhas são feitas, a capa e a trilha sonora mudam em tempo real.
  - A escolha corrupta desencadeia o **Final Ruim 1**, ativando imediatamente a nova capa animada e a música temática.
- **Galeria de Capas**: Permite visualizar e alternar diretamente entre as capas desbloqueadas.

---

## 🎮 Controles e Atalhos Rápidos

| Tecla / Ação | Função |
| :---: | :--- |
| **`1`** | Ativar **Capa Principal** (Ping-Pong) |
| **`2`** | Ativar **Final Ruim 1** (Animação Estendida Partes 1 & 2 + Música) |
| **`C`** | Alternar rapidamente entre as capas |
| **`H`** | Ocultar / Exibir interface para assistir ao vídeo em tela cheia |
| **`M`** | *(Debug)* Adiantar a música perto do fim para testar a pausa de 2 segundos |
| **`ESC`** | Voltar ao menu anterior / Sair do jogo |

---

## 🚀 Como Executar

### Opção 1: Via atalho rápido
Basta dar dois cliques no arquivo:
```bat
jogar.bat
```

### Opção 2: Via terminal Python
```bash
python main.py
```

---

## 📦 Como Gerar o Executável (.exe)

Basta dar dois cliques no arquivo:
```bat
gerar_executavel.bat
```
Todas as mídias (vídeos normais, vídeos da sequência estendida e a trilha sonora) serão empacotadas automaticamente na pasta `dist/MeuJogo/`.
