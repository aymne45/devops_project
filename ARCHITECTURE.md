# Architecture du Projet ENT

## 🏗️ Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (Browser)                         │
│                     http://localhost                             │
└──────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
                  ┌─────────────────────────┐
                  │    Nginx (API Gateway)   │
                  │       Port 80/443        │
                  └─────────────┬────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌──────────────────┐    ┌──────────────┐
│ Auth Service  │     │  File Management │    │   Download   │
│   Port 8001   │     │    Port 8002     │    │  Port 8003   │
└───────┬───────┘     └────────┬─────────┘    └──────┬───────┘
        │                      │                      │
        │             ┌────────┴────────┐            │
        │             ▼                 ▼            │
        │    ┌──────────────┐   ┌─────────────┐     │
        │    │ Admin Service│   │  Chatbot    │     │
        │    │  Port 8004   │   │  Port 8005  │     │
        │    └──────┬───────┘   └──────┬──────┘     │
        │           │                   │            │
        └───────────┼───────────────────┼────────────┘
                    │                   │
        ┌───────────┴───────────┐       │
        ▼                       ▼       ▼
┌───────────────┐      ┌────────────────────┐
│   Cassandra   │      │       Ollama       │
│   Port 9042   │      │  (Llama 3 Model)   │
└───────────────┘      │    Port 11434      │
                       └────────────────────┘
        ▲
        │
        │              ┌────────────────┐
        └──────────────┤     MinIO      │
                       │  Object Storage│
                       │   Ports 9000   │
                       └────────────────┘
```

## 🔄 Flux de Données

### 1. Authentification

```
User → Nginx → Auth Service → Cassandra
                     ↓
                 JWT Token
                     ↓
                   User
```

### 2. Upload de Cours (Enseignant)

```
Teacher → Nginx → File Management Service
                         ↓
                    ┌────┴────┐
                    ▼         ▼
                MinIO    Cassandra
               (Fichier) (Metadata)
```

### 3. Téléchargement de Cours (Étudiant)

```
Student → Nginx → Download Service
                       ↓
                  Cassandra (metadata)
                       ↓
                  MinIO (file)
                       ↓
                  Student
```

### 4. Chatbot IA

```
User → Nginx → Chatbot Service
                    ↓
              ┌─────┴──────┐
              ▼            ▼
         Cassandra      Ollama
        (Context)    (Llama 3)
              └─────┬──────┘
                    ↓
                Response
```

## 📊 Modèle de Données Cassandra

### Table: users

```cql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    hashed_password TEXT,
    role TEXT,              -- admin, teacher, student
    full_name TEXT,
    created_at TIMESTAMP
);

CREATE INDEX ON users (username);
```

### Table: courses

```cql
CREATE TABLE courses (
    id UUID PRIMARY KEY,
    title TEXT,
    description TEXT,
    teacher_username TEXT,
    file_name TEXT,
    file_url TEXT,
    file_size BIGINT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX ON courses (teacher_username);
```

### Table: chat_history

```cql
CREATE TABLE chat_history (
    id UUID PRIMARY KEY,
    username TEXT,
    question TEXT,
    answer TEXT,
    timestamp TIMESTAMP
);

CREATE INDEX ON chat_history (username);
```

## 🔐 Sécurité

### Authentification JWT

1. **Login** → Username/Password
2. **Validation** → Auth Service vérifie dans Cassandra
3. **Token Generation** → JWT avec payload:
   ```json
   {
     "sub": "username",
     "role": "student",
     "exp": 1234567890
   }
   ```
4. **Authorization** → Tous les services vérifient le JWT

### Protection des Endpoints

- **Public**: `/api/auth/register`, `/api/auth/token`
- **Authenticated**: Tous les autres endpoints
- **Role-based**:
  - `admin`: Tous les accès
  - `teacher`: Upload de cours, gestion de ses cours
  - `student`: Lecture et téléchargement de cours

## 🚀 Déploiement

### Docker Compose (Développement)

```yaml
Services:
  - nginx (API Gateway)
  - cassandra (Database)
  - minio (Object Storage)
  - ollama (IA)
  - auth-service
  - file-management-service
  - download-service
  - admin-service
  - chatbot-service
```

### Kubernetes (Production)

```
Deployments:
  - nginx-deployment (3 replicas)
  - cassandra-statefulset (3 replicas)
  - minio-deployment (1 replica)
  - ollama-deployment (1 replica)
  - auth-deployment (2 replicas)
  - file-management-deployment (2 replicas)
  - download-deployment (3 replicas)
  - admin-deployment (1 replica)
  - chatbot-deployment (2 replicas)

Services:
  - LoadBalancer pour nginx
  - ClusterIP pour les services internes
  - StatefulSet pour Cassandra

PersistentVolumeClaims:
  - cassandra-data
  - minio-data
  - ollama-models
```

## 📈 Scalabilité

### Horizontal Scaling

Tous les services peuvent être scalés horizontalement sauf:
- Cassandra (nécessite configuration du cluster)
- Ollama (un seul modèle chargé en mémoire)

```bash
# Docker Compose
docker-compose up -d --scale download-service=3

# Kubernetes
kubectl scale deployment download-service --replicas=5
```

### Load Balancing

Nginx fait du round-robin entre les instances:

```nginx
upstream download_service {
    server download-service-1:8003;
    server download-service-2:8003;
    server download-service-3:8003;
}
```

## 🔍 Monitoring

### Health Checks

Chaque service expose:
- `GET /` → Service info
- `GET /health` → Health status (Nginx)

### Métriques Recommandées

- **Nginx**: Requests/sec, Response time, Error rate
- **Services**: Request latency, Error count, Active connections
- **Cassandra**: Read/Write latency, Storage size
- **MinIO**: Object count, Storage usage
- **Ollama**: Model load time, Inference time

### Outils Recommandés

- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Monitoring**: Prometheus + Grafana
- **Tracing**: Jaeger
- **Alerting**: Alertmanager

## 🔄 CI/CD Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│   Git    │───▶│  Build   │───▶│  Deploy  │
│  Push    │    │  Docker  │    │  K8s/DC  │
└──────────┘    └──────────┘    └──────────┘
```

### GitHub Actions Example

```yaml
name: CI/CD
on: [push]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker images
        run: docker-compose build
      - name: Deploy to production
        run: kubectl apply -f k8s/
```

## 📁 Structure des Services

Chaque microservice suit cette structure:

```
service-name/
├── main.py           # Point d'entrée FastAPI
├── requirements.txt  # Dépendances Python
├── Dockerfile        # Image Docker
├── models.py         # Modèles Pydantic (optionnel)
└── database.py       # Connexion DB (optionnel)
```

## 🌐 API Gateway Routes

```nginx
/                          → Frontend (Static files)
/api/auth/*                → Auth Service (8001)
/api/files/*               → File Management (8002)
/api/download/*            → Download Service (8003)
/api/admin/*               → Admin Service (8004)
/api/chatbot/*             → Chatbot Service (8005)
/health                    → Nginx health check
```

## 🔧 Configuration

Variables d'environnement par service:

**Tous les services**:
- `CASSANDRA_HOST`
- `CASSANDRA_PORT`

**Auth Service**:
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

**File Management / Download**:
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `AUTH_SERVICE_URL`

**Chatbot**:
- `OLLAMA_URL`
- `MODEL_NAME`
- `AUTH_SERVICE_URL`

**Admin**:
- `AUTH_SERVICE_URL`

## 🎯 Bonnes Pratiques

1. **Isolation**: Chaque service a sa propre base de code
2. **Communication**: API REST synchrone, Message Queue pour async
3. **Logging**: Format JSON structuré
4. **Errors**: Gestion centralisée des erreurs
5. **Documentation**: Swagger/OpenAPI pour chaque service
6. **Versioning**: API versioning (`/api/v1/...`)
7. **Security**: HTTPS, JWT, Rate limiting
