# Cores ANSI para simular o terminal
CYAN = '\033[38;5;51m'      # Input/Comando
ORANGE = '\033[38;5;208m'   # SQL
WHITE = '\033[97m'          # Texto principal
GRAY = '\033[90m'           # Texto secundário
RESET = '\033[0m'

# Largura fixa da caixa
BOX_WIDTH = 100


def print_header(color, title, ajuste=0):
    total_border_space = BOX_WIDTH - 2 - 2 - len(title) + ajuste
    left_side = total_border_space // 2
    right_side = total_border_space - left_side
    print(f"{color}╭{'─' * left_side} {title} {'─' * right_side}╮{RESET}")


def print_footer(color):
    print(f"{color}╰{'─' * (BOX_WIDTH - 2)}╯{RESET}")


def print_line(color, content, indent=0, ajuste=0):
    # Padding: Largura total - bordas - indentação - tamanho do texto + ajuste manual
    padding_len = BOX_WIDTH - 3 - indent - len(content) + ajuste
    padding_len = max(0, padding_len)
    indent_str = " " * indent
    print(f"{color}│ {indent_str}{WHITE}{content}{' ' * padding_len}{color}│{RESET}")


def print_empty(color):
    print(f"{color}│{' ' * (BOX_WIDTH - 2)}│{RESET}")

# ==============================================================================
# CENÁRIO: RETORNO VAZIO (CORRIGIDO)
# ==============================================================================


print("\n")

# 1. CABEÇALHO DO TESTE
# Ajuste=-1 compensa o emoji
print_header(CYAN, "🔍 Teste: Busca SQL Padrão (Sem Fuzzy)", ajuste=-1)
print_empty(CYAN)
print_line(CYAN, "Objetivo: Tentar encontrar 'Enelgisa' (Typo) usando SQL comum.")
print_empty(CYAN)
print_footer(CYAN)

# 2. O COMANDO EXECUTADO
# Ajuste=-1 compensa o emoji
print_header(ORANGE, "💻 Comando SQL Executado", ajuste=-1)
print_empty(ORANGE)
print_line(ORANGE, "SELECT id_favorecido, nome_favorecido")
print_line(ORANGE, "FROM dim_favorecido")
print_line(ORANGE, "WHERE nome_favorecido LIKE '%Enelgisa%';")
print_empty(ORANGE)
print_footer(ORANGE)

# 3. O RESULTADO VAZIO
# Ajuste=-1 compensa o emoji
print_header(WHITE, "📉 Resultado do Banco de Dados", ajuste=-1)
print_empty(WHITE)
print_line(WHITE, "Status: Success (Execution time: 0.002s)")
print_empty(WHITE)

# Tabela Vazia
print_line(
    WHITE, "┌───────────────┬──────────────────────────────────────┐", indent=2)
print_line(
    WHITE, "│ id_favorecido │  nome_favorecido                     │", indent=2)
print_line(
    WHITE, "├───────────────┼──────────────────────────────────────┤", indent=2)
# Sem dados
print_line(
    WHITE, "└───────────────┴──────────────────────────────────────┘", indent=2)
print_empty(WHITE)

# --- CORREÇÃO AQUI ---
# O texto tem códigos de cor (GRAY e RESET) que somam 9 caracteres invisíveis.
# O Python conta eles, mas o terminal não mostra.
# Usamos ajuste=9 para devolver os 9 espaços que o Python roubou.
print_line(WHITE, f"{GRAY}Result: 0 rows returned.{RESET}", indent=2, ajuste=9)

print_empty(WHITE)
print_footer(WHITE)
print("\n")
