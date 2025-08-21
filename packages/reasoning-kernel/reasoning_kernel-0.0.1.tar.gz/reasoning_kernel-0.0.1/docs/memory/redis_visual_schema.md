# Redis Database Visual Schema
## MSA Reasoning Engine

## Key Structure Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     REDIS KEY SPACE                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              REASONING CHAINS                         │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  reasoning_chain:session_1754754645                  │   │
│  │  reasoning_chain:session_1754754481                  │   │
│  │  reasoning_chain:climate_model_chain                 │   │
│  │  [SET] reasoning_chains → {all chain IDs}            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              KNOWLEDGE ENTITIES                       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  knowledge:concept:bayesian_inference                │   │
│  │  knowledge:entity:pharmaceutical_company             │   │
│  │  knowledge:process:drug_development                  │   │
│  │  [SET] knowledge_type:concept → {IDs}                │   │
│  │  [SET] knowledge_tag:statistics → {type:id pairs}    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SESSION MANAGEMENT                       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  session:session_1754754645                          │   │
│  │  session:session_1754754481:chains → {chain IDs}     │   │
│  │  [SET] active_sessions → {active session IDs}        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MODEL CACHE                              │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  model_cache:gpt4:a3f8b2c9... (input hash)           │   │
│  │  model_cache:numpyro:d7e1f4a6...                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
    USER REQUEST
         │
         ▼
    ┌──────────┐
    │ SESSION  │──────────┐
    └──────────┘          │
         │                │
         ▼                ▼
    ┌──────────┐    ┌──────────┐
    │  MODE 1  │    │  CACHE   │
    │ (LLM)    │◄───│  CHECK   │
    └──────────┘    └──────────┘
         │                │
         ▼                │
    ┌──────────┐          │
    │KNOWLEDGE │          │
    │EXTRACTION│          │
    └──────────┘          │
         │                │
         ▼                │
    ┌──────────┐          │
    │  MODE 2  │          │
    │(NumPyro) │          │
    └──────────┘          │
         │                │
         ▼                ▼
    ┌──────────────────────┐
    │   STORE IN REDIS     │
    ├──────────────────────┤
    │ • Reasoning Chain    │
    │ • Knowledge Entities │
    │ • Model Results      │
    │ • Session Data       │
    └──────────────────────┘
         │
         ▼
    RESPONSE TO USER
```

## Index Relationships

```
┌─────────────────────────────────────────────────────┐
│                 INDEX STRUCTURE                      │
├─────────────────────────────────────────────────────┤
│                                                       │
│  reasoning_chains (SET)                              │
│       │                                              │
│       ├──► chain_001                                 │
│       ├──► chain_002                                 │
│       └──► chain_003                                 │
│                                                       │
│  knowledge_type:concept (SET)                        │
│       │                                              │
│       ├──► bayesian_inference                        │
│       ├──► neural_network                            │
│       └──► decision_theory                           │
│                                                       │
│  knowledge_tag:ml (SET)                              │
│       │                                              │
│       ├──► concept:neural_network                    │
│       ├──► process:training                          │
│       └──► entity:model                              │
│                                                       │
│  active_sessions (SET)                               │
│       │                                              │
│       ├──► session_1754754645                        │
│       └──► session_1754754481                        │
│                                                       │
└─────────────────────────────────────────────────────┘
```

## TTL Lifecycle

```
Timeline (in seconds)
0        300      600      900      1200     1500     1800     3600     7200     86400
├────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│                                                                                   │
│ Model Cache (30 min) ──────────────────────┤                                    │
│                                                                                   │
│ Reasoning Chain (1 hour) ─────────────────────────────────────┤                 │
│                                                                                   │
│ Session (2 hours) ───────────────────────────────────────────────────────┤       │
│                                                                                   │
│ Knowledge Entity (24 hours) ─────────────────────────────────────────────────────┤
│                                                                                   │
```

## Query Pattern Examples

### 1. Store New Reasoning Chain
```
CLIENT                     REDIS
  │                          │
  ├──SETEX chain:123───────►│ Store with TTL
  │                          │
  ├──SADD reasoning_chains──►│ Add to index
  │                          │
  ├──SADD session:abc:chains►│ Link to session
  │                          │
  │◄─────────OK──────────────│
  │                          │
```

### 2. Retrieve Knowledge by Tag
```
CLIENT                     REDIS
  │                          │
  ├──SMEMBERS tag:ml────────►│ Get all refs
  │                          │
  │◄──[concept:nn, ...]──────│
  │                          │
  ├──GET knowledge:concept:nn►│ Get each item
  │                          │
  │◄──{data}──────────────────│
  │                          │
```

### 3. Cache Check Pattern
```
CLIENT                     REDIS
  │                          │
  ├──Hash input──────────────┤
  │                          │
  ├──GET cache:model:hash───►│ Check cache
  │                          │
  │◄──nil or {cached_data}───│
  │                          │
  If nil:                    │
  ├──Run model──────────────┤
  ├──SETEX cache:model:hash─►│ Store result
  │                          │
```

## Memory Layout Example

```
┌──────────────────────────────────────────────────────┐
│              REDIS MEMORY SNAPSHOT                    │
├──────────────────────────────────────────────────────┤
│                                                        │
│  Type         Count    Avg Size    Total Memory       │
│  ─────────────────────────────────────────────        │
│  Reasoning    100      5 KB        500 KB             │
│  Knowledge    500      2 KB        1 MB               │
│  Sessions     50       1 KB        50 KB              │
│  Model Cache  200      10 KB       2 MB               │
│  Indexes      20       100 B       2 KB               │
│  ─────────────────────────────────────────────        │
│  TOTAL        870                  ~3.5 MB            │
│                                                        │
│  Fragmentation Ratio: 1.2                             │
│  Eviction Policy: allkeys-lru                         │
│  Max Memory: 100 MB                                   │
│  Current Usage: 3.5%                                  │
│                                                        │
└──────────────────────────────────────────────────────┘
```

## Access Pattern Heatmap

```
Operation                 Frequency    Latency
────────────────────────────────────────────────
GET reasoning_chain       ████████     < 1ms
SETEX reasoning_chain     ████         < 2ms
SMEMBERS knowledge_type   ██████       < 1ms
GET knowledge:*           ███████      < 1ms
SETEX model_cache        ████         < 2ms
GET model_cache          ████████     < 1ms
SADD indexes             ███          < 1ms
UPDATE session           ██           < 2ms
SCAN knowledge:*         █            < 10ms
```

## Connection Pool Configuration

```
┌─────────────────────────────────────┐
│        CONNECTION POOL               │
├─────────────────────────────────────┤
│                                      │
│  Max Connections: 50                 │
│  Min Idle: 10                        │
│  Max Idle: 20                        │
│                                      │
│  Current State:                      │
│  ┌─────────────────────────────┐    │
│  │ Active:  ████░░░░░░ (8/50)  │    │
│  │ Idle:    ██████░░░░ (12/20) │    │
│  │ Waiting: ░░░░░░░░░░ (0)     │    │
│  └─────────────────────────────┘    │
│                                      │
│  Connection Timeout: 5s              │
│  Socket Timeout: 30s                 │
│  Retry on Timeout: Yes               │
│                                      │
└─────────────────────────────────────┘
```