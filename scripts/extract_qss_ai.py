import urllib.request
import json
import re
import os
import time

API_KEY = "AIzaSyDwg3GS9x3fwfcqEFMbocW8RUpNTWRvU2w"
# Usar gemini-flash-lite-latest que possui cota livre de 1500 requisições diárias
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    word_map = {}
    for word, indices in inverted_index.items():
        for idx in indices:
            word_map[idx] = word
    sorted_words = [word_map[i] for i in sorted(word_map.keys())]
    return " ".join(sorted_words)

def call_gemini_batch(batch_papers):
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
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                response_data = json.loads(res.read().decode("utf-8"))
                text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            wait_time = 10 * (attempt + 1)
            print(f"Tentativa {attempt+1} falhou ao chamar API do Gemini: {e}. Aguardando {wait_time} segundos...", flush=True)
            time.sleep(wait_time)
            
    print("Falha ao chamar Gemini após 5 tentativas.", flush=True)
    return []

def main():
    issn = "2641-3337"
    
    for volume in range(1, 5):
        year = 2019 + volume
        print(f"\n==========================================", flush=True)
        print(f"Iniciando extração inteligente (IA) do QSS Volume {volume} (Ano {year})...", flush=True)
        print(f"==========================================", flush=True)
        
        url = f"https://api.openalex.org/works?filter=locations.source.issn:{issn},biblio.volume:{volume}&per_page=100"
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "mailto:gabriel@example.com"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                data = json.loads(res.read().decode("utf-8"))
        except Exception as e:
            print(f"Erro ao conectar com a API do OpenAlex para Volume {volume}: {e}", flush=True)
            continue

        results = data.get("results", [])
        print(f"Volume {volume}: Total de {len(results)} artigos retornados pelo OpenAlex.", flush=True)
        
        # 1. Preparar lista com metadados para envio
        prepared_articles = []
        original_mappings = {}
        
        for idx, w in enumerate(results):
            doi = w.get("doi", "")
            title = w.get("title", "")
            authors = [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author") and a["author"].get("display_name")]
            keywords = [k.get("display_name", "") for k in w.get("keywords", []) if k.get("display_name")]
            abstract = reconstruct_abstract(w.get("abstract_inverted_index", {}))
            
            prepared_articles.append({
                "id": idx,
                "title": title,
                "abstract": abstract,
                "keywords": ", ".join(keywords)
            })
            
            original_mappings[idx] = {
                "DOI": doi,
                "Título": title,
                "Autoria": ", ".join(authors),
                "Palavras-chave": ", ".join(keywords)
            }
            
        # 2. Processar em lotes de 10 artigos
        batch_size = 10
        refined_items_map = {}
        
        for i in range(0, len(prepared_articles), batch_size):
            batch = prepared_articles[i:i+batch_size]
            print(f"Processando lote de IA {i//batch_size + 1}/{(len(prepared_articles)-1)//batch_size + 1} (Artigos {i} a {i+len(batch)-1})...", flush=True)
            
            classified_batch = call_gemini_batch(batch)
            
            for item in classified_batch:
                ref_id = item.get("id")
                if ref_id is not None:
                    refined_items_map[ref_id] = item
                    
            # Atraso seguro de 5.5 segundos
            time.sleep(5.5)
            
        # 3. Reconstruir lista final unindo dados originais e classificação de IA
        final_list = []
        for idx, orig in original_mappings.items():
            ai_data = refined_items_map.get(idx, {})
            
            final_list.append({
                "DOI": orig["DOI"],
                "Título": orig["Título"],
                "Autoria": orig["Autoria"],
                "Palavras-chave": orig["Palavras-chave"],
                "Ferramenta utilizada": ai_data.get("Ferramenta", "N/A"),
                "Identifica a ferramenta?": ai_data.get("Identifica", "N/A"),
                "Onde usou (coleta dos dados, análise dos dados ou visualização - gerar gráficos)": ai_data.get("Onde", "N/A"),
                "Fonte de coleta de dados (da onde o pesquisador tirou a informação?)": ai_data.get("Fonte", "N/A")
            })
            
        output_file = f"qss_volume_{volume}_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=2)
            
        print(f"Concluído QSS Volume {volume}! Salvo {len(final_list)} artigos em '{output_file}'.", flush=True)

if __name__ == "__main__":
    main()
