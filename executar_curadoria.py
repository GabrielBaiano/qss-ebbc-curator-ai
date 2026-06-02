import os
import sys

# Adicionar a pasta 'scripts' ao path de busca do Python
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(root_dir, "scripts"))

try:
    import refine_with_abstracts
    refine_with_abstracts.main()
except KeyboardInterrupt:
    print("\n\nExecução interrompida pelo usuário. Saindo...")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")
    import traceback
    traceback.print_exc()
