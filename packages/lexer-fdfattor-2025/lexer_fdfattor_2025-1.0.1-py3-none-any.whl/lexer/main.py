from . import core

AFDS = [
    ("program", core.afd_program),                              # program
    ("var", core.afd_var),                                      # var
    ("int", core.afd_int),                                      # int
    ("bool", core.afd_bool),                                    # bool
    ("true", core.afd_true),                                    # true
    ("false", core.afd_false),                                  # false
    ("begin", core.afd_begin),                                  # begin
    ("end", core.afd_end),                                      # end
    ("if", core.afd_if),                                        # if
    ("else", core.afd_else),                                    # else
    ("not", core.afd_not),                                      # not
    ("and", core.afd_and),                                      # and
    ("or", core.afd_or),                                        # or
    ("goto", core.afd_goto),                                    # goto
    ("let", core.afd_let),                                      # let
    ("menor_igual", core.afd_menor_igual),                      # <=
    ("mayor_igual", core.afd_mayor_igual),                      # >=
    ("distinto", core.afd_distinto),                            # <>
    ("igual", core.afd_igual),                                  # ==
    ("menor", core.afd_menor),                                  # <
    ("mayor", core.afd_mayor),                                  # >
    ("asignar", core.afd_asignar),                              # =
    ("suma", core.afd_suma),                                    # +
    ("resta", core.afd_resta),                                  # -
    ("multiplicacion", core.afd_multiplicacion),                # *
    ("parentesis_izquierdo", core.afd_parentesis_izquierdo),    # (
    ("parentesis_derecho", core.afd_parentesis_derecho),        # )
    ("rango", core.afd_rango),                                  # ...
    ("punto", core.afd_punto),                                  # .
    ("terminar", core.afd_terminar),                            # ;
    ("dos_puntos", core.afd_dos_puntos),                        # :
    ("num", core.afd_num),                                      # num
    ("id", core.afd_id),                                        # id
]

def lexer(cadena):
    tokens = []
    indice = 0
    cadena_len = len(cadena)
    
    while indice < cadena_len:
        # Saltar espacios en blanco sin agregarlos a los tokens
        if core.afd_blanco(cadena[indice]) == core.ESTADO_FINAL:
            indice += 1
            continue
            
        # Buscar el token más largo posible desde la posición actual
        mejor_token = None
        mejor_longitud = 0
        
        # Probar subcadenas de longitud creciente
        for longitud in range(1, cadena_len - indice + 1):
            subcadena = cadena[indice:indice + longitud]
            
            # Verificar si algún AFD acepta esta subcadena
            token_encontrado = None
            for nombre_token, afd in AFDS:
                if afd(subcadena) == core.ESTADO_FINAL:
                    token_encontrado = (nombre_token, subcadena)
                    break
            
            if token_encontrado:
                # Encontramos un token válido, guardarlo como candidato
                mejor_token = token_encontrado
                mejor_longitud = longitud
            else:
                # Si no encontramos token válido, verificar si todos los AFDs están en trampa
                todos_en_trampa = True
                for nombre_token, afd in AFDS:
                    if afd(subcadena) != core.ESTADO_TRAMPA:
                        todos_en_trampa = False
                        break
                
                # Si todos están en trampa, usar el mejor token encontrado hasta ahora
                if todos_en_trampa:
                    break
        
        # Agregar el mejor token encontrado o ERROR si no encontramos ninguno
        if mejor_token:
            tokens.append(mejor_token)
            indice += mejor_longitud
        else:
            # No se encontró ningún token válido, agregar como ERROR
            tokens.append(("ERROR", cadena[indice]))
            indice += 1
    
    return tokens
