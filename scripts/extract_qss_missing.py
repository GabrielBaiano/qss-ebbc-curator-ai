import urllib.request
import json
import re
import os

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    word_map = {}
    for word, indices in inverted_index.items():
        for idx in indices:
            word_map[idx] = word
    sorted_words = [word_map[i] for i in sorted(word_map.keys())]
    return " ".join(sorted_words)

def extract_tools(text, keywords):
    tools = []
    text_lower = text.lower()
    for tool_name, pattern in keywords.items():
        if re.search(pattern, text_lower):
            tools.append(tool_name)
    return tools

def extract_sources(text, keywords):
    sources = []
    text_lower = text.lower()
    for source_name, pattern in keywords.items():
        if re.search(pattern, text_lower):
            sources.append(source_name)
    return sources

def main():
    issn = "2641-3337"
    
    # Dicionário de Regex para Ferramentas
    TOOLS_MAP = {
        "VOSviewer": r"\bvosviewer\b",
        "Gephi": r"\bgephi\b",
        "CiteSpace": r"\bcitespace\b",
        "bibliometrix": r"\bbibliometrix\b|\br-bibliometrix\b",
        "Python": r"\bpython\b",
        "R": r"\b[Rr]\b\s+(?:language|programming|script|package|studio|ggplot|\bbase\b|\blibrary\b)",
        "Excel": r"\bexcel\b|\bms\s+excel\b",
        "SPSS": r"\bspss\b",
        "Stata": r"\bstata\b",
        "SAS": r"\bsas\b",
        "Pajek": r"\bpajek\b",
        "Sci2": r"\bsci2\b|\bscience\s+of\s+science\s+tool\b",
        "BibExcel": r"\bbibexcel\b",
        "SQL": r"\bsql\b|\bmysql\b|\bpostgresql\b|\bsqlite\b",
        "Tableau": r"\btableau\b",
        "Power BI": r"\bpower\s*bi\b",
        "ChatGPT": r"\bchatgpt\b|\bgpt-4\b|\bgpt-3\.5\b|\bllm\b|\bgenai\b|\bgenerative\s+ai\b",
    }

    # Dicionário de Regex para Fontes de Coleta de Dados
    SOURCES_MAP = {
        "Web of Science": r"\bweb\s+of\s+science\b|\bwos\b",
        "Scopus": r"\bscopus\b",
        "OpenAlex": r"\bopenalex\b",
        "Dimensions": r"\bdimensions\b",
        "Crossref": r"\bcrossref\b",
        "PubMed": r"\bpubmed\b|\bmedline\b",
        "PubMed Central": r"\bpmc\b|\bpubmed\s+central\b",
        "Google Scholar": r"\bgoogle\s+scholar\b",
        "ORCID": r"\borcid\b",
        "DBLP": r"\bdblp\b",
        "arXiv": r"\barxiv\b",
        "bioRxiv": r"\bbiorxiv\b",
        "GitHub": r"\bgithub\b",
        "Zenodo": r"\bzenodo\b",
        "The Lens": r"\bthe\s+lens\b|\blens\.org\b",
        "Microsoft Academic Graph": r"\bmicrosoft\s+academic\s+graph\b|\bmag\b",
    }

    for volume in range(1, 5):
        year = 2019 + volume
        print(f"Iniciando extração do QSS Volume {volume} (Ano {year})...")
        url = f"https://api.openalex.org/works?filter=locations.source.issn:{issn},biblio.volume:{volume}&per_page=100"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "mailto:gabriel@example.com"}
        )
        
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode("utf-8"))
        except Exception as e:
            print(f"Erro ao conectar com a API do OpenAlex para Volume {volume}: {e}")
            continue

        results = data.get("results", [])
        print(f"Volume {volume}: Total de artigos retornados pelo OpenAlex: {len(results)}")
        
        json_list = []
        
        for w in results:
            doi = w.get("doi", "")
            title = w.get("title", "")
            
            # Obter Autores
            authors = []
            for a in w.get("authorships", []):
                if a.get("author") and a["author"].get("display_name"):
                    authors.append(a["author"]["display_name"])
                    
            # Obter Palavras-chave
            keywords = []
            for k in w.get("keywords", []):
                if k.get("display_name"):
                    keywords.append(k["display_name"])
                    
            # Reconstruir Abstract
            abstract = reconstruct_abstract(w.get("abstract_inverted_index", {}))
            
            # Texto total para busca (Título + Abstract + Keywords)
            full_search_text = f"{title} {abstract} {' '.join(keywords)}"
            
            # Extrair candidatos automaticamente
            extracted_tools = extract_tools(full_search_text, TOOLS_MAP)
            extracted_sources = extract_sources(full_search_text, SOURCES_MAP)
            
            # Decidir Ferramenta
            if extracted_tools:
                ferramenta = ", ".join(extracted_tools)
                identifica = "Sim"
            else:
                ferramenta = "N/A"
                identifica = "N/A"
                
            # Decidir Onde usou (Coleta, análise, visualização)
            onde_usou = []
            for tool in extracted_tools:
                if tool in ["VOSviewer", "Gephi", "CiteSpace", "Pajek", "Tableau", "Power BI"]:
                    onde_usou.append("visualização - gerar gráficos")
                    onde_usou.append("análise dos dados")
                elif tool in ["Python", "R", "SQL", "Excel", "SPSS", "Stata", "SAS", "Sci2", "BibExcel"]:
                    onde_usou.append("análise dos dados")
                    onde_usou.append("coleta dos dados")
                elif tool in ["ChatGPT"]:
                    onde_usou.append("análise dos dados")
                    
            # Garantir elementos únicos e ordenados
            onde_usou_str = ", ".join(sorted(list(set(onde_usou)))) if onde_usou else "N/A"
            
            # Decidir Fonte de Dados
            fonte_dados = ", ".join(extracted_sources) if extracted_sources else "N/A"
            
            # Criar item de dados no formato solicitado
            item = {
                "DOI": doi,
                "Título": title,
                "Autoria": ", ".join(authors),
                "Palavras-chave": ", ".join(keywords),
                "Ferramenta utilizada": ferramenta,
                "Identifica a ferramenta?": identifica,
                "Onde usou (coleta dos dados, análise dos dados ou visualização - gerar gráficos)": onde_usou_str,
                "Fonte de coleta de dados (da onde o pesquisador tirou a informação?)": fonte_dados
            }
            
            json_list.append(item)
            
        output_file = f"qss_volume_{volume}_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_list, f, ensure_ascii=False, indent=2)
            
        print(f"Volume {volume} concluído! Salvo em '{output_file}'.")

if __name__ == "__main__":
    main()
