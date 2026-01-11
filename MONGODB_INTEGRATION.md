# 📊 MongoDB Integration — Sistema de Auditoria e Analytics

## Overview

Este projeto implementa um sistema completo de **auditoria e análise de dados** usando MongoDB em conjunto com PostgreSQL. O objetivo é rastrear e analisar todas as operações críticas (inscrições, consultas, atividades) para fins educacionais de Base de Dados.

---

## 🎯 Funcionalidades Implementadas

### 1. **Auditoria de Inscrições em Turnos** ✅
- Cada tentativa de inscrição é registada em:
  - **PostgreSQL**: Tabela `auditoria_inscricao` (persistência)
  - **MongoDB**: Coleção `auditoria_inscricoes` (análise)
- Captura: resultado (sucesso/falha), motivo, tempo de processamento

**Localização:**
- Model: `core/models.py` → `AuditoriaInscricao`
- View: `core/views.py` → `inscrever_turno()`
- Service: `bd2_projeto/services/mongo_service.py` → `registar_auditoria_inscricao()`

---

### 2. **Logging Completo com Contexto** ✅
Cada log captura:
- IP do utilizador
- User-Agent (browser/dispositivo)
- Método HTTP (GET, POST, etc)
- Caminho da URL
- Timestamp
- Detalhes da operação

**Localização:**
- Service: `bd2_projeto/services/mongo_service.py` → `adicionar_log()`
- Uso: `views.py` → chamadas a `adicionar_log(..., request)`

**Exemplo:**
```python
adicionar_log("inscricao_turno_sucesso", 
    {
        "aluno": "João Silva",
        "uc": "Estruturas de Dados",
        "turno": 5,
        "tempo_ms": 145
    }, 
    request  # ← Captura IP, user-agent, etc
)
```

---

### 3. **Logging de Consultas de Alunos** ✅
Registam-se todas as consultas:
- Plano curricular
- Horários
- Avaliações

**Localização:**
- Service: `registar_consulta_aluno()` em `mongo_service.py`
- Implementado em: `plano_curricular()`, `horarios()`, `avaliacoes()` em `views.py`

---

### 4. **Análise de Dados — Aggregations MongoDB** ✅

#### 4.1 Taxa de Sucesso de Inscrições
```python
analisar_taxa_sucesso_inscricoes()
# Retorna: Número de tentativas por resultado (sucesso, turno_cheio, etc)
```

#### 4.2 Inscrições por Dia
```python
analisar_inscricoes_por_dia()
# Retorna: Tendência temporal — inscrições/dia com taxa de sucesso
```

#### 4.3 Alunos Mais Ativos
```python
analisar_alunos_mais_ativos()
# Top 20 alunos com mais tentativas de inscrição + taxa de sucesso
```

#### 4.4 UCs Mais Procuradas
```python
analisar_ucs_mais_procuradas()
# Quais UCs têm mais inscrições
```

#### 4.5 Turnos Sobrecarregados
```python
analisar_turnos_sobrecarregados()
# Quais turnos mais vezes foram rejeitados por estar cheios
```

**Localização:** `bd2_projeto/services/mongo_service.py` (linhas 140+)

---

### 5. **Dashboard de Analytics** ✅
Nova página admin para visualizar análises:

**URL:** `/admin-panel/analytics/inscricoes/`

**Dados exibidos:**
- Taxa de sucesso (gráfico pizza/bar)
- Inscrições por dia (gráfico linha)
- Top 10 alunos mais ativos
- Top 10 UCs mais procuradas
- Turnos sobrecarregados

**Localização:** `core/analytics_views.py`

**APIs disponíveis:**
- `/api/analytics/inscricoes-dia/` — JSON com dados por dia
- `/api/analytics/taxa-sucesso/` — JSON com taxa de sucesso
- `/api/analytics/alunos-ativos/` — JSON com alunos ativos
- `/api/analytics/ucs-procuradas/` — JSON com UCs procuradas

---

### 6. **Validações Duplas (PostgreSQL + MongoDB)** ✅
Antes de inscrever aluno em turno:
1. ✅ Valida em MongoDB se já tem inscrição
2. ✅ Valida capacidade do turno em PostgreSQL
3. ✅ Registar resultado em ambas as BD

**Localização:** `inscrever_turno()` em `views.py`

---

### 7. **Índices MongoDB para Performance** ✅
Índices criados automaticamente:
- `logs`: timestamp, acao, utilizador
- `auditoria_inscricoes`: timestamp, aluno_id, resultado
- `consultas_alunos`: timestamp, aluno_id, tipo_consulta
- `atividades_docentes`: timestamp, docente_id
- `erros`: timestamp, funcao

**Localização:** `criar_indices()` em `mongo_service.py`

---

### 8. **TTL (Time-To-Live) para Limpeza Automática** ✅
Logs com mais de **30 dias** são deletados automaticamente pelo MongoDB.

---

## 🚀 Como Usar

### Passo 1: Executar Inicialização MongoDB

```bash
# No diretório raiz do projeto
python manage.py shell

>>> from bd2_projeto.mongo_init import inicializar_mongodb
>>> inicializar_mongodb()
```

Isto vai:
- ✅ Criar índices
- ✅ Criar coleção time-series
- ✅ Configurar TTL
- ✅ Validar schemas

### Passo 2: Fazer Migrações (Para a tabela PostgreSQL)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Passo 3: Testar Auditoria

```bash
# 1. Login como aluno
# 2. Ir para "Inscrição em Turnos"
# 3. Tentar inscrever em turno
# 4. Ir para admin panel:
#    - /admin-panel/analytics/inscricoes/ — Ver estatísticas
#    - /admin-panel/logs/detalhados/ — Ver logs detalhados
```

---

## 📊 Exemplos de Queries em MongoDB

### Ver todas as auditoria_inscricoes com sucesso

```javascript
db.auditoria_inscricoes.find({resultado: "sucesso"})
```

### Ver inscrições de um aluno específico

```javascript
db.auditoria_inscricoes.find({aluno_id: 12345})
```

### Ver logs da última hora

```javascript
db.logs.find({
    timestamp: {
        $gte: new Date(new Date().getTime() - 60*60*1000)
    }
})
```

### Aggregation — Taxa de sucesso

```javascript
db.auditoria_inscricoes.aggregate([
    {
        $group: {
            _id: "$resultado",
            count: {$sum: 1}
        }
    },
    {
        $sort: {count: -1}
    }
])
```

---

## 🔍 Estrutura de Dados

### Coleção: `auditoria_inscricoes`
```json
{
    "_id": ObjectId(),
    "aluno_id": 12345,
    "turno_id": 5,
    "uc_id": 42,
    "uc_nome": "Estruturas de Dados",
    "resultado": "sucesso",
    "motivo_rejeicao": null,
    "tempo_processamento_ms": 145,
    "timestamp": ISODate("2024-01-11T15:30:00Z"),
    "data_formatada": "2024-01-11 15:30:00"
}
```

### Coleção: `logs`
```json
{
    "_id": ObjectId(),
    "acao": "inscricao_turno_sucesso",
    "detalhes": {
        "aluno": "João Silva",
        "uc": "Estruturas de Dados",
        "turno": 5,
        "tempo_ms": 145
    },
    "timestamp": ISODate("2024-01-11T15:30:00Z"),
    "data_formatada": "2024-01-11 15:30:00",
    "contexto": {
        "ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "metodo": "POST",
        "caminho": "/turnos/inscrever/5/42/",
        "utilizador": "joao_silva"
    }
}
```

### Coleção: `consultas_alunos`
```json
{
    "_id": ObjectId(),
    "aluno_id": 12345,
    "aluno_nome": "João Silva",
    "tipo_consulta": "plano_curricular",
    "detalhes": {
        "curso": "EI"
    },
    "timestamp": ISODate("2024-01-11T15:30:00Z"),
    "data_formatada": "2024-01-11 15:30:00"
}
```

---

## 📁 Ficheiros Criados/Modificados

### Criados:
- ✅ `core/analytics_views.py` — Views de analytics
- ✅ `bd2_projeto/mongo_init.py` — Script de inicialização

### Modificados:
- ✅ `bd2_projeto/services/mongo_service.py` — Expandido com +200 linhas
- ✅ `core/models.py` — Adicionado modelo `AuditoriaInscricao`
- ✅ `core/views.py` — Atualizado com:
  - Auditoria em `inscrever_turno()`
  - Logging de consultas em `plano_curricular()`, `horarios()`, `avaliacoes()`
  - Imports para `time`, novos serviços
- ✅ `core/urls.py` — Adicionadas 6 URLs para analytics

---

## 🎓 Aprendizados de Base de Dados

Este projeto demonstra:

1. **Polyglot Persistence**: Dados em PostgreSQL (estruturado) + MongoDB (flexível)
2. **Auditoria Dupla**: Rastreamento em relacional + análise em NoSQL
3. **Aggregation Pipelines**: Análise complexa de dados sem mover para Python
4. **Índices para Performance**: Otimização de queries em MongoDB
5. **TTL e Limpeza Automática**: Gestão automática de retenção de dados
6. **Validação em Múltiplas Camadas**: Checks em view + DB constraints
7. **Time-Series Data**: Coleção especial para dados temporais

---

## 📈 Próximas Melhorias (Sugeridas)

- [ ] Sharding por aluno_id (se escala para 10k+ alunos)
- [ ] Replicação para backup automático
- [ ] Alertas em tempo real (inscrições anormais)
- [ ] Dashboard interativo com Grafana/Kibana
- [ ] Backup automático para S3/GCS

---

## ❓ FAQ

**P: Por que MongoDB E PostgreSQL?**
R: PostgreSQL para dados estruturados e transações ACID; MongoDB para auditoria flexível, análise temporal, e escalabilidade.

**P: Quanto espaço vai ocupar?**
R: Depende do volume. TTL automático limpa logs com >30 dias. Índices ocupam ~10% do tamanho dos dados.

**P: Posso usar isto em produção?**
R: Sim, mas recomenda-se:
- Backup regular do MongoDB
- Monitoramento de tamanho de coleções
- Tuning de índices baseado em queries reais

---

**Desenvolvido para disciplina de Base de Dados 2 — ISEC**
