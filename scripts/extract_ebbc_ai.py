import urllib.request
import json
import re
import os
import time
import html
from html.parser import HTMLParser

API_KEY = "AIzaSyDwg3GS9x3fwfcqEFMbocW8RUpNTWRvU2w"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"

class OJSArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta_data = {}
        
    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            attr_dict = dict(attrs)
            name = attr_dict.get("name")
            content = attr_dict.get("content")
            if name and content is not None:
                content_unescaped = html.unescape(content).strip()
                if name not in self.meta_data:
                    self.meta_data[name] = []
                self.meta_data[name].append(content_unescaped)

def get_html(url):
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            return res.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}", flush=True)
        return None

def call_gemini_batch(batch_papers):
    prompt = f"""
You are an expert scientometric research assistant.
Analyze the following batch of academic paper metadata (Titles, Abstracts, and Keywords) from the Brazilian Meeting on Bibliometrics and Scientometrics (EBBC).

For each paper, classify and extract the following:
1. "Ferramenta": Specific software, programming language, package, or tool used (e.g. 'VOSviewer', 'Python', 'R', 'Excel', 'Sci2', 'ChatGPT', etc. If no tool was used or strongly inferred, write 'N/A'). Be specific but concise.
2. "Identifica": 'Sim' (if tools are explicitly identified in the title/abstract), 'Não' (if the paper does not specify the tool used but clearly uses one), 'N/A' (if no tools were used).
3. "Onde": Comma-separated list containing one or more of: 'coleta dos dados', 'análise dos dados', 'visualização - gerar gráficos'. If no tools were used, write 'N/A'.
4. "Fonte": Where the researchers got their data/corpus from (e.g. 'Web of Science', 'Scopus', 'OpenAlex', 'Dimensions', 'PubMed', 'Google Scholar', 'N/A', or specific project repositories like 'Brapci', 'Plataforma Lattes', 'CNPq', 'Sucupira', etc.).

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

def scrape_issue(issue_url, year):
    print(f"\n==========================================", flush=True)
    print(f"Raspando edição do EBBC {year} ({issue_url})...", flush=True)
    print(f"==========================================", flush=True)
    
    issue_html = get_html(issue_url)
    if not issue_html:
        return []
        
    links = re.findall(r'href="(https://ebbc\.inf.br/ojs/index\.php/ebbc/article/view/\d+)"', issue_html)
    unique_links = sorted(list(set(links)))
    print(f"Total de {len(unique_links)} artigos encontrados nesta edição.", flush=True)
    
    scraped_articles = []
    
    for idx, link in enumerate(unique_links, 1):
        print(f"Carregando metadados do artigo {idx}/{len(unique_links)}...", flush=True)
        art_html = get_html(link)
        if not art_html:
            continue
            
        parser = OJSArticleParser()
        parser.feed(art_html)
        
        meta = parser.meta_data
        
        # Obter Título
        title_list = meta.get("citation_title") or meta.get("DC.Title") or ["N/A"]
        title = title_list[0]
        
        # Obter Autores
        authors_list = meta.get("citation_author") or meta.get("DC.Creator.PersonalName") or []
        authors = ", ".join(authors_list) if authors_list else "N/A"
        
        # Obter DOI
        doi_list = meta.get("citation_doi") or meta.get("DC.Identifier.DOI") or []
        doi = doi_list[0] if doi_list else "N/A"
        if doi != "N/A" and not doi.startswith("http"):
            doi = f"https://doi.org/{doi}"
            
        # Obter Keywords
        keywords_list = meta.get("citation_keywords") or meta.get("DC.Subject") or []
        keywords = ", ".join(keywords_list) if keywords_list else ""
        
        # Obter Resumo (Abstract)
        abstract_list = meta.get("DC.Description") or meta.get("description") or [""]
        abstract = abstract_list[0]
        
        scraped_articles.append({
            "idx": idx,
            "DOI": doi,
            "Título": title,
            "Autoria": authors,
            "Palavras-chave": keywords,
            "Abstract": abstract
        })
        
    # Processar em lotes de 10 com o Gemini
    batch_size = 10
    refined_items_map = {}
    prepared_inputs = []
    
    for a in scraped_articles:
        prepared_inputs.append({
            "id": a["idx"],
            "title": a["Título"],
            "abstract": a["Abstract"],
            "keywords": a["Palavras-chave"]
        })
        
    for i in range(0, len(prepared_inputs), batch_size):
        batch = prepared_inputs[i:i+batch_size]
        print(f"Processando lote de IA {i//batch_size + 1}/{(len(prepared_inputs)-1)//batch_size + 1} (Artigos {i} a {i+len(batch)-1})...", flush=True)
        
        classified_batch = call_gemini_batch(batch)
        
        for item in classified_batch:
            ref_id = item.get("id")
            if ref_id is not None:
                refined_items_map[ref_id] = item
                
        # Atraso seguro de 5.5 segundos (INDENTAÇÃO CORRIGIDA - FORA DO LOOP INTERNO!)
        time.sleep(5.5)
        
    # Reconstruir lista final
    final_list = []
    for a in scraped_articles:
        ai_data = refined_items_map.get(a["idx"], {})
        
        final_list.append({
            "DOI": a["DOI"],
            "Título": a["Título"],
            "Autoria": a["Autoria"],
            "Palavras-chave": a["Palavras-chave"],
            "Ferramenta utilizada": ai_data.get("Ferramenta", "N/A"),
            "Identifica a ferramenta?": ai_data.get("Identifica", "N/A"),
            "Onde usou (coleta dos dados, análise dos dados ou visualização - gerar gráficos)": ai_data.get("Onde", "N/A"),
            "Fonte de coleta de dados (da onde o pesquisador tirou a informação?)": ai_data.get("Fonte", "N/A")
        })
        
    return final_list

def main():
    editions = {
        2020: "https://ebbc.inf.br/ojs/index.php/ebbc/issue/view/12",
        2022: "https://ebbc.inf.br/ojs/index.php/ebbc/issue/view/13",
        2024: "https://ebbc.inf.br/ojs/index.php/ebbc/issue/view/5"
    }
    
    for year, url in editions.items():
        data = scrape_issue(url, year)
        
        output_file = f"ebbc_{year}_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Edição {year} concluída com sucesso via IA! {len(data)} artigos salvos em '{output_file}'.", flush=True)

if __name__ == "__main__":
    main()
