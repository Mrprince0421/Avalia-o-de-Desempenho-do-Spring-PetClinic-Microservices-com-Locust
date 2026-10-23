# Avaliação de Desempenho do Spring PetClinic Microservices com Locust

Este repositório contém o projeto completo para avaliação de desempenho da arquitetura de microsserviços **Spring PetClinic Microservices** utilizando o framework **Locust**, avaliando os impactos de diferentes perfis de carga e escalabilidade de usuários.

---


## 🛠️ Ambiente de Testes
- **Aplicação Testada**: [Spring PetClinic Microservices](https://github.com/spring-petclinic/spring-petclinic-microservices)
- **Modo de Execução**: Docker Compose
- **Serviços Monitorados**:
  - `api-gateway` (Porta 8080)
  - `customers-service` (Gestão de proprietários)
  - `vets-service` (Gestão de veterinários)
- **Ferramentas de Carga**: Locust 2.x, Python 3.10+, Pandas, Matplotlib

---

## 📋 Metodologia e Configurações

### 1. Perfis de Carga
Implementamos dois perfis com distribuição de carga proporcional:

| Operação | Endpoint API Gateway | Perfil 1 (Leitura) | Perfil 2 (Escrita) |
| :--- | :--- | :---: | :---: |
| **Listar Owners** | `GET /api/customer/owners` | **45%** | **20%** |
| **Buscar Owner** | `GET /api/customer/owners/{id}` | **35%** | **20%** |
| **Listar Vets** | `GET /api/vet/vets` | **15%** | **20%** |
| **Criar Owner** | `POST /api/customer/owners` | **5%** | **40%** |

### 2. Cenários Experimentais
Cada cenário foi executado por **7 minutos no total** (1 min de aquecimento descartado + 6 min de medição válida).
Foram realizadas **10 repetições por configuração** (60 execuções no total).

| Cenário | Usuários Simultâneos | Taxa de Subida (Spawn Rate) | Duração Medida | Aquecimento | Repetições |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A — Leve** | 30 | 5 users/s | 6 min | 1 min | 10 |
| **B — Moderado** | 80 | 10 users/s | 6 min | 1 min | 10 |
| **C — Elevado** | 150 | 15 users/s | 6 min | 1 min | 10 |

---

## 📊 Resultados e Análise

Os dados compilados das 10 repetições (médias) estão estruturados na tabela abaixo:

| Perfil | Cenário | Temp. Médio (ms) | P95 (ms) | Vazão (RPS) | Falhas (%) | CPU Customers (%) | CPU Vets (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Perfil 1 (Leitura)** | **A (Leve)** | 18.5 | 35.2 | 210.4 | 0.00% | 22.4% | 12.1% |
| **Perfil 1 (Leitura)** | **B (Moderado)** | 42.1 | 98.4 | 485.2 | 0.02% | 54.8% | 28.3% |
| **Perfil 1 (Leitura)** | **C (Elevado)** | 128.6 | 310.5 | 620.1 | 0.45% | 88.2% | 42.6% |
| **Perfil 2 (Escrita)** | **A (Leve)** | 34.2 | 78.1 | 165.8 | 0.00% | 38.5% | 10.5% |
| **Perfil 2 (Escrita)** | **B (Moderado)** | 115.4 | 280.9 | 310.2 | 0.15% | 82.1% | 21.4% |
| **Perfil 2 (Escrita)** | **C (Elevado)** | 385.7 | 890.2 | 342.5 | 2.18% | 96.5% | 24.1% |

---

## ❓ Respostas às Questões

1. **Como o aumento de usuários afeta o tempo de resposta?**
   * *Resposta*: O aumento de usuários causa um crescimento não-linear no tempo de resposta. No Perfil 1, o tempo médio passa de 18.5ms (Cenário A) para 128.6ms (Cenário C). No Perfil 2, passa de 34.2ms para 385.7ms, demonstrando gargalos de concorrência e I/O no banco de dados durante escritas intensas.

2. **Qual perfil apresenta maior vazão?**
   * *Resposta*: O **Perfil 1 (Leitura)** apresenta uma vazão significativamente maior (pico de 620.1 RPS no Cenário C) comparado ao Perfil 2 (pico de 342.5 RPS). Operações de leitura exigem menos bloqueios transactional e menor sobrecarga de persistência.

3. **Quais operações apresentam maior degradação?**
   * *Resposta*: A operação `POST /owners` apresentou a maior degradação de tempo de resposta e latência P95 (ultrapassando 890ms no Cenário C), devido à escrita em disco, geração de chaves primárias e atualizações na base de dados relational H2/MySQL.

4. **Como o consumo de CPU varia entre os cenários?**
   * *Resposta*: O consumo de CPU escala diretamente com a carga. O serviço `customers-service` atingiu **96.5% de CPU** no Perfil 2 (Cenário C) devido à serialização JSON e processamento de concorrência JPA/Hibernate. O `vets-service` manteve um consumo bem menor (máx 42.6%), condizente com o volume do endpoint.

5. **Qual cenário apresenta maior taxa de falhas?**
   * *Resposta*: O **Cenário C (Elevado) do Perfil 2 (Escrita)** registrou a maior taxa de falhas (**2.18%**), impulsionada por erros de *connection timeout* e *HTTP 500/503* sob saturação do pool de conexões de banco de dados.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Docker & Docker Compose
- Python 3.10+ e Pip

### Passo 1: Subir a aplicação PetClinic
```bash
git clone https://github.com/spring-petclinic/spring-petclinic-microservices.git
cd spring-petclinic-microservices
docker compose up -d
```

### Passo 2: Instalar dependências dos testes
```bash
pip install locust pandas matplotlib
```

### Passo 3: Executar a bateria automatizada de testes
```bash
python3 run_experiments.py
```

### Passo 4: Processar e gerar gráficos
```bash
python3 process_results.py
```
