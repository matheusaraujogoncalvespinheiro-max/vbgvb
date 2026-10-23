# Veredito: A Balança do Poder ⚖️💵

Jogo desenvolvido em Python utilizando **Pygame** e **OpenCV**, preparado para compilação em executável (.exe).

## 🌟 Funcionalidades Atuais
- **Menu Principal Interativo**: Design com estilo *glassmorphism*, botões com animação suave e efeitos sonoros/visuais preparados.
- **Vídeo de Fundo em Loop Ping-Pong**: O vídeo roda em sentido normal até o fim, depois roda em reverso até o início, criando um loop contínuo e sem emendas a 24 FPS.
- **Atalhos Rápidos**:
  - `H`: Ocultar ou exibir a interface para apreciar o fundo em tela cheia.
  - `ESC`: Sair do jogo.

## 🚀 Como Executar

### Opção 1: Via atalho rápido
Basta dar dois cliques no arquivo:
```
jogar.bat
```

### Opção 2: Via terminal Python
```bash
pip install pygame opencv-python pyinstaller
python main.py
```

### 📦 Como Gerar o Executável (.exe)
Basta dar dois cliques no arquivo:
```
gerar_executavel.bat
```
O executável será gerado automaticamente na pasta `dist/MeuJogo/`.
