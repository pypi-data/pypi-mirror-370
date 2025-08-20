# TP1 Sintaxis - Analizador Léxico

Trabajo práctico de análisis léxico con autómatas finitos deterministas.

## Instalación

```bash
# Instalar desde GitHub
pip install git+https://github.com/FDFattor/tp1-sintaxis-2025.git

# Instalar versión específica
pip install git+https://github.com/FDFattor/tp1-sintaxis-2025.git@v1.0.0
```

## Uso

```python
# Forma recomendada - Solo importar la función pública
from source import lexer

# Analizar código
codigo = "program ejemplo var x : int begin x = 5; end"
tokens = lexer(codigo)
print(tokens)
```

```python
# También funciona (pero menos recomendado)
import source

tokens = source.lexer("program test var x : int")
print(tokens)
```

## Tokens soportados

- Palabras reservadas: `program`, `var`, `int`, `bool`, `true`, `false`, `begin`, `end`, `if`, `else`, `not`, `and`, `or`, `goto`, `let`
- Operadores: `<=`, `>=`, `<>`, `==`, `<`, `>`, `=`, `+`, `-`, `*`
- Delimitadores: `(`, `)`, `;`, `:`, `.`, `...`
- Identificadores y números

## Desarrollo

```bash
# Clonar y configurar
git clone https://github.com/FDFattor/tp1-sintaxis-2025.git
cd tp1-sintaxis-2025
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar en modo desarrollo
pip install -e .

# Ejecutar tests
python -m pytest tests.py
```
