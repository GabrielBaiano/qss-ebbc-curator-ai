import urllib.request
import json
import re
import os
import time
import urllib.error

API_KEY = "AIzaSyDwg3GS9x3fwfcqEFMbocW8RUpNTWRvU2w"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"

def call_gemini_batch_refine(batch_papers):
    prompt = f"""
You are a expert scientometric research assistant. 
Analyze the following batch of academic paper metadata (Titles, Abstracts, and Keywords).

For each paper, classify and extract the following:
1. "Ferramenta": Specific software, programming language, package, or tool used (e.g. 'VOSviewer', 'Python', 'R', 'R (ggplot)', 'Excel', 'Sci2', 'ChatGPT', etc. If no tool was used or strongly inferred, write 'N/A'). Be specific but concise.
2. "Identifica": 'Sim' (if tools are explicitly identified in the title/abstract), 'Não' (if the paper does not specify the tool used but clearly uses one), 'N/A' (if no tools were used).
3. "Onde": Comma-separated list containing one or more of: 'coleta dos dados', 'análise dos dados', 'visualização - gerar gráficos'. If no tools were used, write 'N/A'.
4. "Fonte": Where the researchers got their data/corpus from (e.g. 'Web of Science', 'Scopus', 'OpenAlex', 'Dimensions', 'PubMed', 'Google Scholar', 'N/A', or specific project repositories).

Return a valid JSON array of objects, each having these keys:
- "id": (MUST match the input paper id exactly)
- "Ferramenta": software/tool
- "Identifica": 'Sim'/'Não'/'N/A'
- "Onde": usage area
- "Fonte": data source

Input articles to classify:
{json.dumps(batch_papers, indent=2, ensure_ascii=False)}
"""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    req = urllib.request.Request(
        GEMINI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                response_data = json.loads(res.read().decode("utf-8"))
                text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except urllib.error.HTTPError as e:
            wait_time = 15 * (2 ** attempt)
            print(f"Tentativa {attempt+1} falhou. HTTP Error {e.code}: {e.reason}. Aguardando {wait_time} segundos...", flush=True)
            time.sleep(wait_time)
        except Exception as e:
            wait_time = 15 * (2 ** attempt)
            print(f"Tentativa {attempt+1} falhou. Erro: {e}. Aguardando {wait_time} segundos...", flush=True)
            time.sleep(wait_time)
            
    print("Falha ao chamar Gemini após todas as tentativas.", flush=True)
    return []

def main():
    targets = [
        ("qss_volume_1_data.json", "QSS Vol 1"),
        ("qss_volume_2_data.json", "QSS Vol 2"),
        ("qss_volume_3_data.json", "QSS Vol 3"),
        ("qss_volume_4_data.json", "QSS Vol 4"),
        ("ebbc_2020_data.json", "EBBC 2020"),
        ("ebbc_2022_data.json", "EBBC 2022"),
        ("ebbc_2024_data.json", "EBBC 2024")
    ]
    
    tool_key = "Ferramenta utilizada"
    id_key = "Identifica a ferramenta?"
    where_key = "Onde usou (coleta dos dados, análise dos dados ou visualização - gerar gráficos)"
    source_key = "Fonte de coleta de dados (da onde o pesquisador tirou a informação?)"
    
    for filename, label in targets:
        if not os.path.exists(filename):
            print(f"Arquivo {filename} não encontrado. Pulando...", flush=True)
            continue
            
        print(f"\n=== Refinando {label} ({filename}) ===", flush=True)
        with open(filename, "r", encoding="utf-8") as f:
            articles = json.load(f)
            
        # Encontrar artigos que precisam de refinação
        missing_indices = []
        prepared_batch_list = []
        
        for idx, art in enumerate(articles):
            is_missing = (
                art.get(tool_key) == "N/A" and
                art.get(id_key) == "N/A" and
                art.get(where_key) == "N/A" and
                art.get(source_key) == "N/A"
            )
            if is_missing:
                missing_indices.append(idx)
                prepared_batch_list.append({
                    "id": idx,
                    "title": art.get("Título", ""),
                    "abstract": "", # O abstract não está salvo no JSON de saída para não poluir, mas título + keywords ajudam muito.
                    "keywords": art.get("Palavras-chave", "")
                })
                
        print(f"Total de artigos: {len(articles)}. Artigos sem informações (N/A completo): {len(missing_indices)}", flush=True)
        
        if not missing_indices:
            print("Nenhum artigo precisa de refinação. Prosseguindo...", flush=True)
            continue
            
        # Processar em lotes de 10 artigos
        batch_size = 10
        refined_count = 0
        
        for i in range(0, len(prepared_batch_list), batch_size):
            batch = prepared_batch_list[i:i+batch_size]
            print(f"Processando lote de refinação {i//batch_size + 1}/{(len(prepared_batch_list)-1)//batch_size + 1} ({len(batch)} artigos)...", flush=True)
            
            classified_batch = call_gemini_batch_refine(batch)
            
            for item in classified_batch:
                ref_id = item.get("id")
                if ref_id is not None and ref_id in missing_indices:
                    articles[ref_id][tool_key] = item.get("Ferramenta", "N/A")
                    articles[ref_id][id_key] = item.get("Identifica", "N/A")
                    articles[ref_id][where_key] = item.get("Onde", "N/A")
                    articles[ref_id][source_key] = item.get("Fonte", "N/A")
                    refined_count += 1
            
            # Atraso seguro de 10 segundos entre chamadas para evitar 429
            time.sleep(10.0)
            
        # Salvar o arquivo atualizado
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
            
        print(f"Refinação concluída para {label}! Atualizados {refined_count} de {len(missing_indices)} artigos.", flush=True)
        
    print("\nTodos os arquivos JSON foram refinados com sucesso!", flush=True)

if __name__ == "__main__":
    main()
