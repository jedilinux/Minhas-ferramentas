#!/bin/bash

# Função para verificar se a URL é válida
validar_url() {
  if [[ $1 =~ ^https?:// ]]; then
    return 0
  else
    return 1
  fi
}

# Verificar se a URL fornecida é válida
echo "Digite a URL que deseja escanear:"
read alvo
if ! validar_url "$alvo"; then
  echo "URL inválida. Certifique-se de incluir 'http://' ou 'https://'."
  exit 1
fi

# Diretório para armazenar resultados
resultados_dir="resultados"
mkdir -p "$resultados_dir"

# Executar Subfinder para encontrar subdomínios
subfinder -d "$alvo" -silent | dnsx -silent -asn | cut -d ' ' -f1 | grep --color 'api' > "$resultados_dir/subdominios.txt"

# Verificar se o arquivo subdominios.txt existe e não está vazio
if [ -s "$resultados_dir/subdominios.txt" ]; then
  echo "Subdomínios com 'api' encontrados:"
  cat "$resultados_dir/subdominios.txt"
  echo
  echo "Realizando solicitações HTTP POST nos subdomínios..."
  while read -r url; do
    # Usar o curl para fazer uma solicitação HTTP POST para a URL com a estrutura correta
    curl "$url/api" -X POST -H 'X-HTTP-Method-Override: POST' -H 'Content-Type: application/json' --data '{"username":"xyz"}' > "$resultados_dir/response_$url.txt" 2>/dev/null
    # Adicionar um espaço em branco para separar as saídas
    echo
  done < "$resultados_dir/subdominios.txt"
else
  echo "Nenhum subdomínio com 'api' encontrado."
fi

# Limpar arquivos temporários
rm -r "$resultados_dir"

echo "Processo concluído."
