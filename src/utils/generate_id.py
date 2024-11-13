import random
import string

def generate_id(length=25):
    # Define os caracteres permitidos: letras maiúsculas, minúsculas e dígitos
    characters = string.ascii_lowercase + string.digits
    # Gera um ID aleatório com o comprimento especificado
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id