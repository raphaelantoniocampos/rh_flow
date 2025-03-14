def read_registry_numbers(file_path):
    """Lê o arquivo TXT e retorna uma lista com os números dos registros."""
    registry_numbers = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if 'Erro ao obter registros:' in line:
                continue
            # Extrai o número do registro entre colchetes
            if 'registro' in line:
                start = line.find('[') + 1
                end = line.find(']')
                registry_number = int(line[start:end])
                registry_numbers.append(registry_number)
    return registry_numbers

def filter_lines(input_file, output_file, registry_numbers):
    """Filtra as linhas do arquivo de entrada e escreve no arquivo de saída."""
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for index, line in enumerate(infile, start=1):
            # Verifica se o índice da linha não está na lista de números de registro
            if index not in registry_numbers:
                outfile.write(line)

def main():
    # Caminho para os arquivos
    registry_file = 'registros.txt'  # Arquivo com as linhas de registro
    input_file = 'dados.txt'        # Arquivo com as linhas a serem filtradas
    output_file = 'fixed_lines.txt' # Arquivo de saída com as linhas filtradas

    # Lê os números dos registros que devem ser removidos
    registry_numbers = read_registry_numbers(registry_file)

    # Filtra as linhas e escreve no arquivo de saída
    filter_lines(input_file, output_file, registry_numbers)

    print(f"Arquivo '{output_file}' gerado com sucesso!")

if __name__ == "__main__":
    main()
