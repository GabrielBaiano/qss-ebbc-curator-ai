import json

# Mapeamento detalhado e validado manualmente para os 61 artigos do Volume 6 da QSS
REFINED_DATA = {
    1: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "N/A",
        "Fonte": "N/A"
    },
    2: {
        "Ferramenta": "Journal Checker Tool (cOAlition S)",
        "Identifica": "Sim",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Journal Checker Tool, Crossref, OpenAlex"
    },
    3: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "análise dos dados",
        "Fonte": "Metadados de universidades (ranking e citações globais)"
    },
    4: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados",
        "Fonte": "Bases de dados bibliográficas (5 bases), Servidores de preprints (3 servidores)"
    },
    5: {
        "Ferramenta": "Diretório de Periódicos de Acesso Aberto (DOAJ) Benchmark",
        "Identifica": "Sim",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "DOAJ, OpenAlex, Web of Science (WoS), Scopus"
    },
    6: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "análise dos dados",
        "Fonte": "Sistemas de Organização do Conhecimento (45 KOSs)"
    },
    7: {
        "Ferramenta": "Modelos de Atores Estocásticos (SAOM) / RSiena",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Web of Science, Varieties of Democracy Project (Academic Freedom Index)"
    },
    8: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Diretrizes de autores e declarações de acesso aberto de 300 periódicos"
    },
    9: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Retraction Watch, Amostra de 1 milhão de publicações"
    },
    10: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Publons"
    },
    11: {
        "Ferramenta": "Classificador de texto baseado em Machine Learning (ChatGPT Detector)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "arXiv, bioRxiv, medRxiv, OpenAI ChatGPT"
    },
    12: {
        "Ferramenta": "Lei de Sivertsen, Rousseau e Zhang (MFC)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "N/A (Análise puramente matemática e teórica)"
    },
    13: {
        "Ferramenta": "Journal Checker Tool (cOAlition S)",
        "Identifica": "Sim",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Journal Checker Tool, OpenAlex, Consórcio UKB (bibliotecas holandesas)"
    },
    14: {
        "Ferramenta": "Modelos de Linguagem Transformers (NLP), Classificadores Supervisionados (XGBoost/BERT)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Fundação Nacional de Ciência da Suíça (SNSF)"
    },
    15: {
        "Ferramenta": "Algoritmos de Desambiguação de Nomes de Autores",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "OpenAlex, ORCID"
    },
    16: {
        "Ferramenta": "ISSN International Centre Custom Classification",
        "Identifica": "Sim",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Web of Science (WoS), ISSN International Centre"
    },
    17: {
        "Ferramenta": "Modelos de Regressão Longitudinal",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Scopus (dados brutos)"
    },
    18: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "OpenAlex, Open Journal Systems (OJS), Crossref"
    },
    19: {
        "Ferramenta": "ChatGPT 4o-mini (OpenAI LLM)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "U.K. Research Excellence Framework (REF) 2021, OpenAI ChatGPT"
    },
    20: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "N/A",
        "Fonte": "Literatura científica secundária (Revisão teórica)"
    },
    21: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Declarações de integridade de 117 universidades britânicas, PubPeer"
    },
    22: {
        "Ferramenta": "Categorias de OER (Dedicated Learning Content, Learning Design Content, OER Ecosystem)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "N/A (Estudo metodológico conceitual)"
    },
    23: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "SciELO, Redalyc"
    },
    24: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "ORCID"
    },
    25: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Bases de dados bibliográficas (Scopus/Web of Science)"
    },
    26: {
        "Ferramenta": "Relative Specialization Index (RSI - Índice de Especialização Relativa)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Dados de universidades alemãs (pessoal, estudantes e financiamento)"
    },
    27: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Overton, FAPESP"
    },
    28: {
        "Ferramenta": "Modelos de Processamento de Linguagem Natural (NLP / NER), Análise de Grafos Temporais",
        "Identifica": "Sim",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Base de dados de 24.539 publicações de DLT/Blockchain"
    },
    29: {
        "Ferramenta": "Kompetenznetzwerk Bibliometrie (KB) Data Infrastructure",
        "Identifica": "Sim",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Kompetenznetzwerk Bibliometrie (KB) (dados bibliométricos comerciais e abertos)"
    },
    30: {
        "Ferramenta": "Modelos de Regressão 2SLS (Two-stage least squares), Variáveis Instrumentais (IV)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Microsoft Academic Graph (MAG), Web of Science (WoS)"
    },
    31: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Web of Science"
    },
    32: {
        "Ferramenta": "Modelos de Grafos Acíclicos Direcionados (DAG), Modelagem Multinível com Pós-estratificação",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Villum Experiment (VEX)"
    },
    33: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "OpenAlex, Scopus, Web of Science, African Journals Online (AJOL)"
    },
    34: {
        "Ferramenta": "Método Reputable Citations (RC)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Clarivate InCites Essential Science Indicators, Web of Science"
    },
    35: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "N/A",
        "Fonte": "N/A (Carta teórica e epistemológica)"
    },
    36: {
        "Ferramenta": "Modelos de Embedding de Grafo (node2vec, residual2vec), Modelos de Embedding de Texto",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "American Physical Society (APS)"
    },
    37: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Websites da Clarivate, ISI e Thomson Reuters"
    },
    38: {
        "Ferramenta": "Modelo Bayesiano Hierárquico com Validação Cruzada",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Avaliação Nacional Italiana de Pesquisa VQR (2011–2014)"
    },
    39: {
        "Ferramenta": "Lei de Benford (Benford's Law), Testes qui-quadrado, MAD e Max",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Web of Science, Scopus, Dados históricos"
    },
    40: {
        "Ferramenta": "Métodos de Mineração de Texto e Cienciometria",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Periódicos de ciências do comportamento e Mankind Quarterly"
    },
    41: {
        "Ferramenta": "Python (Pacote de medidas de transição), personalized PageRank, node2vec",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Rede de citações de artigos e coautoria"
    },
    42: {
        "Ferramenta": "Método HJ-biplot",
        "Identifica": "Sim",
        "Onde": "análise dos dados, visualização - gerar gráficos",
        "Fonte": "Web of Science"
    },
    43: {
        "Ferramenta": "Modelo Research Strategy Q (Modelo Q)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Dados empíricos e sintéticos de publicações"
    },
    44: {
        "Ferramenta": "Modelos de Regressão Vetorial, Support Vector Machine (SVM), Modelos de Embeddings de Tópicos baseados em LMs",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "15 milhões de artigos de Ciência da Computação"
    },
    45: {
        "Ferramenta": "Modelos de regressão (Regression analysis)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Marie Curie Actions sob o 7º Programa-Quadro da UE (CIG)"
    },
    46: {
        "Ferramenta": "Modelo de Séries Temporais Interrompidas (Interrupted Time Series), Métodos de Mineração de Texto",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "ClinicalTrials.gov, Dimensions"
    },
    47: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Bases de dados bibliográficas (Scopus/Web of Science)"
    },
    48: {
        "Ferramenta": "Algoritmos de agrupamento em rede (Network clustering)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Bases de dados de astronomia e astrofísica, registros de busca de bases de literatura"
    },
    49: {
        "Ferramenta": "GPT-4, Llama3 70B, Llama2 70B, Mistral 7x8B (LLMs), Modelos Preditivos de Deep Learning (XGBoost/BERT)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "OpenAlex"
    },
    50: {
        "Ferramenta": "Diagrama de Monotonia, Diagrama de Dependência, Estatística de Proporção Condicional",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "OpenAlex, Dimensions"
    },
    51: {
        "Ferramenta": "Análise de Painel (Panel data analysis), Análise de Redes de Coautoria",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Agradecimentos de financiamento de publicações de Food Science e Renewable Energy"
    },
    52: {
        "Ferramenta": "Convolutional Neural Networks (CNN), Recurrent Neural Networks (RNN), Transformers",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Microsoft Academic Graph (MAG)"
    },
    53: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Scopus"
    },
    54: {
        "Ferramenta": "Sistemas de Recomendação de Artigos (Research paper recommender systems), Modelos de NLP, Análise de Redes",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Bases de dados de publicações científicas"
    },
    55: {
        "Ferramenta": "Método de Configuração de Financiamento (Funding configuration method)",
        "Identifica": "Sim",
        "Onde": "análise dos dados, visualização - gerar gráficos",
        "Fonte": "N/A (Trabalho metodológico conceitual)"
    },
    56: {
        "Ferramenta": "Modelos estatísticos de associação (Statistical association models)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Web of Science (Clarivate), Faculty Opinions (H1 Connect)"
    },
    57: {
        "Ferramenta": "Modelos de Avaliação por Pares (Peer review models)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Web of Science"
    },
    58: {
        "Ferramenta": "N/A",
        "Identifica": "N/A",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "14 agências de fomento públicas e privadas na Dinamarca"
    },
    59: {
        "Ferramenta": "Métodos de Mineração de Texto personalizados (modality search)",
        "Identifica": "Sim",
        "Onde": "coleta dos dados, análise dos dados",
        "Fonte": "Propostas de financiamento (Grant proposals)"
    },
    60: {
        "Ferramenta": "Jogo de Duopólio Hotelling de Três Estágios (Hotelling duopoly game), Simulação Numérica",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Dados empíricos de 1.346 periódicos de acesso aberto padrão ouro"
    },
    61: {
        "Ferramenta": "Técnicas de Normalização, Análise de Redes (Network-based analysis)",
        "Identifica": "Sim",
        "Onde": "análise dos dados",
        "Fonte": "Conjunto de dados original da pesquisa de bolsas de medicina de Wennerås & Wold (1997)"
    }
}

def main():
    print("Iniciando refinamento de dados do dataset...")
    
    with open("qss_raw_data.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    refined_dataset = []
    
    for idx, item in enumerate(raw_data, 1):
        refined_item = item.copy()
        
        # Remover a chave temporária do abstract
        if "_raw_abstract" in refined_item:
            del refined_item["_raw_abstract"]
            
        # Aplicar mapeamento de alta fidelidade
        if idx in REFINED_DATA:
            ref = REFINED_DATA[idx]
            refined_item["Ferramenta utilizada"] = ref["Ferramenta"]
            refined_item["Identifica a ferramenta?"] = ref["Identifica"]
            refined_item["Onde usou (coleta dos dados, análise dos dados ou visualização - gerar gráficos)"] = ref["Onde"]
            refined_item["Fonte de coleta de dados (da onde o pesquisador tirou a informação?)"] = ref["Fonte"]
            
        refined_dataset.append(refined_item)
        
    # Gravar o arquivo final de alta fidelidade
    with open("qss_volume_6_data.json", "w", encoding="utf-8") as f:
        json.dump(refined_dataset, f, ensure_ascii=False, indent=2)
        
    print("Sucesso! O arquivo 'qss_volume_6_data.json' foi atualizado com classificações refinadas de alta qualidade.")

if __name__ == "__main__":
    main()
