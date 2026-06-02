import os
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import re
import html
import unicodedata
from html.parser import HTMLParser

# Garantir que a pasta scripts esteja no path para importação
sys.path.append(os.path.dirname(__file__))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDwg3GS9x3fwfcqEFMbocW8RUpNTWRvU2w")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"

# Mapeamento de chaves
TOOL_KEY = "Ferramenta utilizada"
IDENT_KEY = "Identifica a ferramenta?"
WHERE_KEY = "Onde usou (coleta dos dados, análise dos dados ou visualização - gerar gráficos)"
SOURCE_KEY = "Fonte de coleta de dados (da onde o pesquisador tirou a informação?)"

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

def normalize_title(title):
    if not title:
        return ""
    # Converter para minúsculas, remover acentos e caracteres especiais
    title = title.lower()
    title = ''.join(c for c in unicodedata.normalize('NFD', title) if unicodedata.category(c) != 'Mn')
    title = re.sub(r'[^a-z0-9]', '', title)
    return title

def print_progress(iteration, total, prefix='', suffix='', length=30, fill='#'):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()

def get_html(url, retries=3):
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                return res.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt == retries - 1:
                return None
            time.sleep(2)
    return None

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    word_map = {}
    for word, indices in inverted_index.items():
        for idx in indices:
            word_map[idx] = word
    sorted_words = [word_map[i] for i in sorted(word_map.keys())]
    return " ".join(sorted_words)

# ----------------- Recuperadores de Abstracts -----------------

def get_qss_abstracts(volume):
    """Busca todos os artigos de um volume do QSS no OpenAlex e reconstrói os abstracts."""
    print(f"\n[OpenAlex] Buscando metadados completos do QSS Volume {volume}...", flush=True)
    issn = "2641-3337"
    url = f"https://api.openalex.org/works?filter=locations.source.issn:{issn},biblio.volume:{volume}&per_page=200"
    
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "mailto:gabriel@example.com"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.loads(res.read().decode("utf-8"))
            results = data.get("results", [])
            print(f"[OpenAlex] Sucesso! {len(results)} artigos retornados para o Volume {volume}.", flush=True)
            
            abstracts_map = {}
            for w in results:
                doi = w.get("doi", "")
                title = w.get("title", "")
                abstract = reconstruct_abstract(w.get("abstract_inverted_index", {}))
                
                # Mapear por DOI (se disponível) e por Título Normalizado
                if doi:
                    abstracts_map[doi.lower().strip()] = abstract
                if title:
                    abstracts_map[normalize_title(title)] = abstract
            return abstracts_map
    except Exception as e:
        print(f"[OpenAlex] Erro ao conectar na API: {e}", flush=True)
        return {}

def get_ebbc_abstracts(year):
    """Busca e raspa os abstracts do EBBC para o ano selecionado, usando cache local."""
    cache_filepath = os.path.join(ROOT_DIR, "datasets", "cache", f"ebbc_{year}_abstracts_cache.json")
    if os.path.exists(cache_filepath):
        print(f"\n[Cache] Carregando abstracts do EBBC {year} a partir do cache local...", flush=True)
        with open(cache_filepath, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # URLs das edições
    editions = {
        2020: "https://ebbc.inf.br/ojs/index.php/ebbc/issue/view/12",
        2022: "https://ebbc.inf.br/ojs/index.php/ebbc/issue/view/13",
        2024: "https://ebbc.inf.br/ojs/index.php/ebbc/issue/view/5"
    }
    
    if year not in editions:
        return {}
        
    issue_url = editions[year]
    print(f"\n[Scraper] Iniciando raspagem das URLs dos artigos do EBBC {year}...", flush=True)
    issue_html = get_html(issue_url)
    if not issue_html:
        print("[Scraper] Falha ao carregar a página da edição.", flush=True)
        return {}
        
    links = re.findall(r'href="(https://ebbc\.inf.br/ojs/index\.php/ebbc/article/view/\d+)"', issue_html)
    unique_links = sorted(list(set(links)))
    total_articles = len(unique_links)
    print(f"[Scraper] Encontrados {total_articles} artigos. Baixando abstracts...", flush=True)
    
    abstracts_map = {}
    
    for idx, link in enumerate(unique_links, 1):
        print_progress(idx, total_articles, prefix="Raspando OJS", suffix=f"Artigo {idx}/{total_articles}")
        art_html = get_html(link)
        if not art_html:
            continue
            
        parser = OJSArticleParser()
        parser.feed(art_html)
        meta = parser.meta_data
        
        # Obter Título
        title_list = meta.get("citation_title") or meta.get("DC.Title") or [""]
        title = title_list[0]
        
        # Obter Abstract
        abstract_list = meta.get("DC.Description") or meta.get("description") or [""]
        abstract = abstract_list[0]
        
        # Obter DOI
        doi_list = meta.get("citation_doi") or meta.get("DC.Identifier.DOI") or []
        doi = doi_list[0] if doi_list else ""
        if doi and not doi.startswith("http"):
            doi = f"https://doi.org/{doi}"
            
        if title:
            norm = normalize_title(title)
            abstracts_map[norm] = abstract
            if doi:
                abstracts_map[doi.lower().strip()] = abstract
                
        # Atraso ético leve de 0.2s para não sobrecarregar o servidor
        time.sleep(0.2)
        
    # Salvar cache
    os.makedirs(os.path.dirname(cache_filepath), exist_ok=True)
    with open(cache_filepath, "w", encoding="utf-8") as f:
        json.dump(abstracts_map, f, ensure_ascii=False, indent=2)
    print(f"\n[Cache] Abstracts do EBBC {year} salvos em cache local com sucesso!", flush=True)
    return abstracts_map

# ----------------- Chamada Gemini -----------------

def call_gemini_refine_batch(batch_papers):
    prompt = f"""
You are an expert scientometric research assistant. 
Analyze the following batch of academic paper metadata (Titles, Abstracts, and Keywords).
Note: The papers may be in English or Portuguese.

For each paper, classify and extract the following:
1. "Ferramenta": Specific software, programming language, package, or tool used (e.g. 'VOSviewer', 'Python', 'R', 'Excel', 'Iramuteq', 'Gephi', 'CiteSpace', etc. If no tool was used, write 'N/A'). Be specific but concise.
2. "Identifica": 'Sim' (if tools are explicitly identified/named in the title/abstract), 'Não' (if the paper clearly uses a software/tool but does not name it explicitly, e.g. "performed statistical regression"), 'N/A' (if no tools were used).
3. "Onde": Comma-separated list containing one or more of: 'coleta dos dados', 'análise dos dados', 'visualização - gerar gráficos'. If no tools were used, write 'N/A'.
4. "Fonte": Where the researchers got their data/corpus from (e.g. 'Web of Science', 'Scopus', 'OpenAlex', 'Dimensions', 'PubMed', 'Google Scholar', 'Brapci', 'Plataforma Lattes', 'CNPq', 'N/A', or specific project repositories).

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
            print(f"\n[Gemini] Tentativa {attempt+1} falhou (HTTP {e.code}). Retrying in {wait_time}s...", flush=True)
            time.sleep(wait_time)
        except Exception as e:
            wait_time = 15 * (2 ** attempt)
            print(f"\n[Gemini] Tentativa {attempt+1} falhou (Erro: {e}). Retrying in {wait_time}s...", flush=True)
            time.sleep(wait_time)
            
    print("\n[Gemini] Falha crítica: não foi possível chamar a API do Gemini.", flush=True)
    return []

# ----------------- Pipeline de Refinamento -----------------

def run_refinement(filename, is_qss, val_label):
    print(f"\n==========================================")
    print(f" Iniciando Refinamento: {val_label}")
    print(f"==========================================")
    
    filepath = os.path.join(ROOT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Erro: Arquivo '{filepath}' não encontrado!", flush=True)
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    # 1. Obter os abstracts reais do volume/edição correspondente
    if is_qss:
        # Extrair o número do volume do nome do arquivo (ex: qss_volume_1_data.json -> 1)
        m = re.search(r'volume_(\d+)_data', filename)
        vol = int(m.group(1)) if m else 1
        abstracts_map = get_qss_abstracts(vol)
    else:
        # Extrair o ano do nome do arquivo (ex: ebbc_2020_data.json -> 2020)
        m = re.search(r'ebbc_(\d+)_data', filename)
        year = int(m.group(1)) if m else 2020
        abstracts_map = get_ebbc_abstracts(year)
        
    # 2. Identificar quais registros estão com ALL N/A
    missing_indices = []
    prepared_batch_list = []
    
    for idx, art in enumerate(articles):
        is_missing = (
            art.get(TOOL_KEY) == "N/A" and
            art.get(IDENT_KEY) == "N/A" and
            art.get(WHERE_KEY) == "N/A" and
            art.get(SOURCE_KEY) == "N/A" and
            not art.get("_refined", False)
        )
        if is_missing:
            # Buscar abstract no mapa
            doi = art.get("DOI", "").lower().strip()
            title = art.get("Título", "")
            norm_title = normalize_title(title)
            
            abstract = abstracts_map.get(doi, "")
            if not abstract:
                abstract = abstracts_map.get(norm_title, "")
                
            missing_indices.append(idx)
            prepared_batch_list.append({
                "id": idx,
                "title": title,
                "abstract": abstract,
                "keywords": art.get("Palavras-chave", "")
            })
            
    total_missing = len(missing_indices)
    print(f"\n[Refinamento] Total de artigos: {len(articles)}.")
    print(f"[Refinamento] Artigos sem informações (N/A completo): {total_missing}.", flush=True)
    
    if total_missing == 0:
        print("[Refinamento] Excelente! 100% dos artigos já estão preenchidos. Nada a fazer.", flush=True)
        return
        
    # 3. Processar em lotes de 10
    batch_size = 10
    success_count = 0
    error_count = 0
    
    for i in range(0, len(prepared_batch_list), batch_size):
        batch = prepared_batch_list[i:i+batch_size]
        lote_num = i // batch_size + 1
        lote_total = (len(prepared_batch_list) - 1) // batch_size + 1
        
        print_progress(i, len(prepared_batch_list), prefix="Refinando com Gemini", suffix=f"Lote {lote_num}/{lote_total} | Sucessos: {success_count} | Erros: {error_count}")
        
        classified_batch = call_gemini_refine_batch(batch)
        
        if not classified_batch:
            error_count += len(batch)
            continue
            
        # Tratamento defensivo caso o Gemini retorne um objeto dicionário envelopado
        if isinstance(classified_batch, dict):
            for val in classified_batch.values():
                if isinstance(val, list):
                    classified_batch = val
                    break
                    
        if not isinstance(classified_batch, list):
            print("\n[Erro] Resposta do Gemini não retornou uma lista válida de artigos.", flush=True)
            error_count += len(batch)
            continue
            
        # Marcar todos do lote como processados pela IA
        for item in batch:
            ref_id = item.get("id")
            if ref_id is not None:
                articles[ref_id]["_refined"] = True

        for item in classified_batch:
            ref_id = item.get("id")
            if ref_id is not None and ref_id in missing_indices:
                articles[ref_id][TOOL_KEY] = item.get("Ferramenta", "N/A")
                articles[ref_id][IDENT_KEY] = item.get("Identifica", "N/A")
                articles[ref_id][WHERE_KEY] = item.get("Onde", "N/A")
                articles[ref_id][SOURCE_KEY] = item.get("Fonte", "N/A")
                success_count += 1
                
        # Atraso de 8 segundos entre chamadas para evitar Rate Limit (429) do Gemini
        time.sleep(8.0)
        
    # Finalizar barra de progresso
    print_progress(len(prepared_batch_list), len(prepared_batch_list), prefix="Refinando com Gemini", suffix=f"Concluído! | Sucessos: {success_count} | Erros: {error_count}")
    
    # 4. Salvar arquivo JSON atualizado
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        
    print(f"[Refinamento] Sucesso! Arquivo '{filename}' atualizado. {success_count} artigos refinados.", flush=True)

# ----------------- Consolidador de Planilha -----------------

def rebuild_excel():
    print("\n[Excel] Reconstruindo a planilha consolidada 'coleta de dados gabriel.xlsx'...", flush=True)
    try:
        import generate_styled_xlsx_all
        generate_styled_xlsx_all.main()
        print("[Excel] Planilha reconstruída com sucesso!", flush=True)
    except Exception as e:
        print(f"[Excel] Erro ao reconstruir planilha: {e}", flush=True)

# ----------------- Menu Principal -----------------

def display_menu():
    # Calcular estatísticas atuais
    targets = [
        ("datasets/qss_volume_1_data.json", True, "QSS Vol 1 (2020)"),
        ("datasets/qss_volume_2_data.json", True, "QSS Vol 2 (2021)"),
        ("datasets/qss_volume_3_data.json", True, "QSS Vol 3 (2022)"),
        ("datasets/qss_volume_4_data.json", True, "QSS Vol 4 (2023)"),
        ("datasets/ebbc_2020_data.json", False, "EBBC 2020"),
        ("datasets/ebbc_2022_data.json", False, "EBBC 2022"),
        ("datasets/ebbc_2024_data.json", False, "EBBC 2024")
    ]
    
    print("\n" + "=" * 60)
    print("      SISTEMA DE CURADORIA DE PESQUISAS ACADÊMICAS (IA)")
    print("=" * 60)
    print(f"{'Opção':<6} | {'Dataset':<20} | {'Total':<6} | {'Todos N/A (Incompletos)':<22}")
    print("-" * 60)
    
    stats = {}
    for idx, (filename, is_qss, label) in enumerate(targets, 1):
        total = 0
        all_na = 0
        filepath = os.path.join(ROOT_DIR, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    total = len(data)
                    for item in data:
                        is_all_na = (
                            item.get(TOOL_KEY) == "N/A" and
                            item.get(IDENT_KEY) == "N/A" and
                            item.get(WHERE_KEY) == "N/A" and
                            item.get(SOURCE_KEY) == "N/A" and
                            not item.get("_refined", False)
                        )
                        if is_all_na:
                            all_na += 1
            except:
                pass
        stats[idx] = (filename, is_qss, label, all_na)
        print(f" {idx:<4} | {label:<20} | {total:<6} | {all_na:<22}")
        
    print("-" * 60)
    print(" 8    | REFINE TODOS os datasets acima consecutivamente")
    print(" 9    | RECONSTRUIR Planilha Excel (coleta de dados gabriel.xlsx)")
    print(" 10   | SAIR")
    print("=" * 60)
    
    try:
        opt = input("Selecione uma opção (1-10): ").strip()
        if opt == "10":
            return False
        elif opt == "9":
            rebuild_excel()
        elif opt == "8":
            # Rodar tudo
            for idx, (filename, is_qss, label, all_na) in stats.items():
                if all_na > 0:
                    run_refinement(filename, is_qss, label)
            rebuild_excel()
        else:
            opt_idx = int(opt)
            if opt_idx in stats:
                filename, is_qss, label, all_na = stats[opt_idx]
                run_refinement(filename, is_qss, label)
                rebuild_excel()
            else:
                print("Opção inválida!")
    except ValueError:
        print("Opção inválida! Digite um número.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        
    return True

def main():
    while True:
        if not display_menu():
            print("\nSaindo... Obrigado por usar o Sistema de Curadoria!")
            break
            
if __name__ == "__main__":
    main()
