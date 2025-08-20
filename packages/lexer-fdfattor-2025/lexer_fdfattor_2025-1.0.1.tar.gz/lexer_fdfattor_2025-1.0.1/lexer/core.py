ESTADO_FINAL = "ESTADO FINAL"
ESTADO_NO_FINAL = "NO ACEPTADO"
ESTADO_TRAMPA = "EN ESTADO TRAMPA"

def afd_id(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c.isalpha():
            estado = 1
        elif estado == 1 and c.isalnum():
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_num(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c.isdigit():
            estado = 1
        elif estado == 1 and c.isdigit():
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL

def afd_program(lexema):
    estado = 0
    estados_finales = [7]
    for c in lexema:
        if estado == 0 and c == 'p':
            estado = 1
        elif estado == 1 and c == 'r':
            estado = 2
        elif estado == 2 and c == 'o':
            estado = 3
        elif estado == 3 and c == 'g':
            estado = 4
        elif estado == 4 and c == 'r':
            estado = 5
        elif estado == 5 and c == 'a':
            estado = 6
        elif estado == 6 and c == 'm':
            estado = 7
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL

def afd_var(lexema):
    estado = 0
    estados_finales = [3]
    for c in lexema:
        if estado == 0 and c == 'v':
            estado = 1
        elif estado == 1 and c == 'a':
            estado = 2
        elif estado == 2 and c == 'r':
            estado = 3
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_punto(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '.':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_terminar(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == ';':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_asignar(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '=':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_int(lexema):
    estado = 0
    estados_finales = [3]
    for c in lexema:
        if estado == 0 and c == 'i':
            estado = 1
        elif estado == 1 and c == 'n':
            estado = 2
        elif estado == 2 and c == 't':
            estado = 3
        else:
            estado = -1
            
    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_bool(lexema):
    estado = 0
    estados_finales = [4]
    for c in lexema:
        if estado == 0 and c == 'b':
            estado = 1
        elif estado == 1 and c == 'o':
            estado = 2
        elif estado == 2 and c == 'o':
            estado = 3
        elif estado == 3 and c == 'l':
            estado = 4
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_true(lexema):
    estado = 0
    estados_finales = [4]
    for c in lexema:
        if estado == 0 and c == 't':
            estado = 1
        elif estado == 1 and c == 'r':
            estado = 2
        elif estado == 2 and c == 'u':
            estado = 3
        elif estado == 3 and c == 'e':
            estado = 4
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_false(lexema):
    estado = 0
    estados_finales = [5]
    for c in lexema:
        if estado == 0 and c == 'f':
            estado = 1
        elif estado == 1 and c == 'a':
            estado = 2
        elif estado == 2 and c == 'l':
            estado = 3
        elif estado == 3 and c == 's':
            estado = 4
        elif estado == 4 and c == 'e':
            estado = 5
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_begin(lexema):
    estado = 0
    estados_finales = [5]
    for c in lexema:
        if estado == 0 and c == 'b':
            estado = 1
        elif estado == 1 and c == 'e':
            estado = 2
        elif estado == 2 and c == 'g':
            estado = 3
        elif estado == 3 and c == 'i':
            estado = 4
        elif estado == 4 and c == 'n':
            estado = 5
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_end(lexema):
    estado = 0
    estados_finales = [3]
    for c in lexema:
        if estado == 0 and c == 'e':
            estado = 1
        elif estado == 1 and c == 'n':
            estado = 2
        elif estado == 2 and c == 'd':
            estado = 3
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_if(lexema):
    estado = 0
    estados_finales = [2]
    for c in lexema:
        if estado == 0 and c == 'i':
            estado = 1
        elif estado == 1 and c == 'f':
            estado = 2
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_else(lexema):
    estado = 0
    estados_finales = [4]
    for c in lexema:
        if estado == 0 and c == 'e':
            estado = 1
        elif estado == 1 and c == 'l':
            estado = 2
        elif estado == 2 and c == 's':
            estado = 3
        elif estado == 3 and c == 'e':
            estado = 4
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_not(lexema):
    estado = 0
    estados_finales = [3]
    for c in lexema:
        if estado == 0 and c == 'n':
            estado = 1
        elif estado == 1 and c == 'o':
            estado = 2
        elif estado == 2 and c == 't':
            estado = 3
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_menor(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '<':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_mayor(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '>':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_distinto(lexema):
    estado = 0
    estados_finales = [2]
    for c in lexema:
        if estado == 0 and c == '<':
            estado = 1
        elif estado == 1 and c == '>':
            estado = 2
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_menor_igual(lexema):
    estado = 0
    estados_finales = [2]
    for c in lexema:
        if estado == 0 and c == '<':
            estado = 1
        elif estado == 1 and c == '=':
            estado = 2
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_mayor_igual(lexema):
    estado = 0
    estados_finales = [2]
    for c in lexema:
        if estado == 0 and c == '>':
            estado = 1
        elif estado == 1 and c == '=':
            estado = 2
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_suma(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '+':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_resta(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '-':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_multiplicacion(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '*':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_igual(lexema):
    estado = 0
    estados_finales = [2]
    for c in lexema:
        if estado == 0 and c == '=':
            estado = 1
        elif estado == 1 and c == '=':
            estado = 2
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_parentesis_izquierdo(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == '(':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_parentesis_derecho(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == ')':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_rango(lexema):
    estado = 0
    estados_finales = [3]
    for c in lexema:
        if estado == 0 and c == '.':
            estado = 1
        elif estado == 1 and c == '.':
            estado = 2
        elif estado == 2 and c == '.':
            estado = 3
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_and(lexema):
    estado = 0
    estados_finales = [3]
    for c in lexema:
        if estado == 0 and c == 'a':
            estado = 1
        elif estado == 1 and c == 'n':
            estado = 2
        elif estado == 2 and c == 'd':
            estado = 3
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_or(lexema):
    estado = 0
    estados_finales = [2]
    for c in lexema:
        if estado == 0 and c == 'o':
            estado = 1
        elif estado == 1 and c == 'r':
            estado = 2
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_blanco(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == ' ':
            estado = 1
        elif estado == 0 and c == '\n':
            estado = 1
        elif estado == 0 and c == '\t':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_dos_puntos(lexema):
    estado = 0
    estados_finales = [1]
    for c in lexema:
        if estado == 0 and c == ':':
            estado = 1
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_goto(lexema):
    estado = 0
    estados_finales = [4]
    for c in lexema:
        if estado == 0 and c == 'g':
            estado = 1
        elif estado == 1 and c == 'o':
            estado = 2
        elif estado == 2 and c == 't':
            estado = 3
        elif estado == 3 and c == 'o':
            estado = 4
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL
    
def afd_let(lexema):
    estado = 0
    estados_finales = [3]
    for c in lexema:
        if estado == 0 and c == 'l':
            estado = 1
        elif estado == 1 and c == 'e':
            estado = 2
        elif estado == 2 and c == 't':
            estado = 3
        else:
            estado = -1

    if estado == -1:
        return ESTADO_TRAMPA
    if estado in estados_finales:
        return ESTADO_FINAL
    else:
        return ESTADO_NO_FINAL