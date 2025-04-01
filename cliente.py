import requests
import json

def main():
    titulo = input("Digite o nome do filme: ")
    try:
        ano = int(input("Digite o ano do filme: "))
    except ValueError:
        print("Ano inválido, digite um número inteiro.")
        return
    payload = {"titulo": titulo, "ano": ano}
    try:
        response = requests.post("http://localhost:8000/movie", json=payload)
        response.raise_for_status()
        resultado = response.json()
        print("\nResultado da consulta:")
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
    except requests.RequestException as e:
        print("Erro ao conectar com o servidor:", e)

if __name__ == "__main__":
    main()
