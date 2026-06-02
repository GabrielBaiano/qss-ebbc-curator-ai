import urllib.request
import json
import re
import os
import html
from html.parser import HTMLParser

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
        print(f"Erro ao acessar {url}: {e}")
        return None

def scrape_issue(issue_url, year):
    print(f"\nRaspando edição do EBBC {year} ({issue_url})...")
    issue_html = get_html(issue_url)
    if not issue_html:
        return []
        
    # Extrair todos os links de artigos
    links = re.findall(r'href="(https://ebbc\.inf.br/ojs/index\.php/ebbc/article/view/\d+)"', issue_html)
    unique_links = sorted(list(set(links)))
    print(f"Total de {len(unique_links)} artigos encontrados nesta edição.")
    
    # Dicionário de Regex para Ferramentas (igual ao do QSS)
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

    # Dicionário de Regex para Fontes (igual ao do QSS)
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
    
    articles_data = []
    
    for idx, link in enumerate(unique_links, 1):
        print(f"Processando artigo {idx}/{len(unique_links)}: {link}")
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
        
        # Classificação Automática
        # Texto total para busca (Título + Abstract + Palavras-chave)
        full_search_text = f"{title} {abstract} {keywords}"
        
        # Extrair candidatos automaticamente
        extracted_tools = []
        text_lower = full_search_text.lower()
        for tool_name, pattern in TOOLS_MAP.items():
            if re.search(pattern, text_lower):
                extracted_tools.append(tool_name)
                
        extracted_sources = []
        for source_name, pattern in SOURCES_MAP.items():
            if re.search(pattern, text_lower):
                extracted_sources.append(source_name)
                
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
                
        onde_usou_str = ", ".join(sorted(list(set(onde_usou)))) if onde_usou else "N/A"
        fonte_dados = ", ".join(extracted_sources) if extracted_sources else "N/A"
        
        item = {
            "DOI": doi,
            "Título": title,
            "Autoria": authors,
            "Palavras-chave": keywords,
            "Ferramenta utilizada": ferramenta,
            "Identifica a ferramenta?": identifica,
            "Onde usou (coleta dos dados, análise dos dados ou visualização - gerar gráficos)": onde_usou_str,
            "Fonte de coleta de dados (da onde o pesquisador tirou a informação?)": fonte_dados
        }
        
        articles_data.append(item)
        
    return articles_data

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
            
        print(f"Edição {year} concluída! {len(data)} artigos salvos em '{output_file}'.")

if __name__ == "__main__":
    main()
