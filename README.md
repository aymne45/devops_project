# ENT - Espace Numérique de Travail

## 📋 Description

Plateforme éducative basée sur une architecture microservices avec intelligence artificielle intégrée (Llama 3). Ce projet implémente un ENT complet permettant la gestion des cours, des utilisateurs, et incluant un chatbot IA pour assister les étudiants et enseignants.

## 🏗️ Architecture

### Microservices

1. **Auth Service** (Port 8001)
   - Authentification JWT
   - Gestion des utilisateurs
   - Inscription et connexion

2. **File Management Service** (Port 8002)
   - Ajout de cours par les enseignants
   - Upload de fichiers vers MinIO
   - Stockage des métadonnées dans Cassandra

3. **Download Service** (Port 8003)
   - Liste des cours disponibles
   - Téléchargement des fichiers
   - Recherche de cours

4. **Admin Service** (Port 8004)
   - Gestion des utilisateurs (CRUD)
   - Attribution des rôles
   - Statistiques de la plateforme

5. **Chatbot Service** (Port 8005)
   - Assistant IA avec Llama 3
   - Réponses contextuelles sur les cours
   - Historique des conversations

### Technologies Utilisées

- **Backend**: Python FastAPI
- **Base de données**: Apache Cassandra
- **Stockage de fichiers**: MinIO
- **IA**: Ollama avec Llama 3
- **API Gateway**: Nginx
- **Conteneurisation**: Docker & Docker Compose
- **Frontend**: HTML/CSS/JavaScript (Tailwind CSS)

## 📦 Prérequis

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- 8 GB RAM minimum
- 20 GB d'espace disque

## 🚀 Installation et Déploiement

### 1. Cloner le projet

```bash
git clone <votre-repo-url>
cd devops
```

### 2. Construire et lancer les services

```bash
docker-compose up -d --build
```

Cette commande va :
- Construire les images Docker pour chaque microservice
- Démarrer Cassandra, MinIO, Ollama, et tous les microservices
- Configurer le réseau Docker

### 3. Vérifier que les services sont démarrés

```bash
docker-compose ps
```

Tous les services devraient être à l'état "Up".

### 4. Initialiser la base de données

```bash
./scripts/init-db.sh
```

### 5. Télécharger le modèle Llama 3

```bash
./scripts/setup-ollama.sh
```

**Note**: Cette étape peut prendre 10-30 minutes selon votre connexion Internet (le modèle fait environ 4 GB).

### 6. Créer les utilisateurs par défaut

```bash
./scripts/create-default-users.sh
```

Utilisateurs créés :
- **Admin** : username=`admin`, password=`admin123`
- **Enseignant** : username=`teacher`, password=`teacher123`
- **Étudiant** : username=`student`, password=`student123`

**Note** : Changez ces mots de passe après la première connexion en production.

## 🌐 Accès à la Plateforme

### Frontend
- **URL**: http://localhost
- **Login**: http://localhost/login

### API Documentation

Chaque service expose une documentation Swagger/OpenAPI :

- Auth Service: http://localhost:8001/docs
- File Management: http://localhost:8002/docs
- Download Service: http://localhost:8003/docs
- Admin Service: http://localhost:8004/docs
- Chatbot Service: http://localhost:8005/docs

### Interfaces d'administration

- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin)
- **Nginx Gateway**: http://localhost

## 📚 Utilisation des APIs

### Authentification

#### S'inscrire
```bash
curl -X POST "http://localhost/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "full_name": "New User",
    "role": "student"
  }'
```

#### Se connecter
```bash
curl -X POST "http://localhost/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student&password=student123"
```

Réponse :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "student",
    "email": "student@ent.com",
    "full_name": "Étudiant ENT",
    "role": "student"
  }
}
```

### Gestion des Cours (Enseignant)

#### Ajouter un cours
```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost/api/files/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Introduction à Python" \
  -F "description=Cours complet sur Python pour débutants" \
  -F "file=@/path/to/course.pdf"
```

#### Lister les cours
```bash
curl -X GET "http://localhost/api/download/courses" \
  -H "Authorization: Bearer $TOKEN"
```

#### Télécharger un cours
```bash
COURSE_ID="uuid-of-course"

curl -X GET "http://localhost/api/download/courses/$COURSE_ID/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o course_downloaded.pdf
```

### Chatbot IA

#### Poser une question
```bash
curl -X POST "http://localhost/api/chatbot/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quels sont les cours disponibles en informatique?"
  }'
```

#### Historique des conversations
```bash
curl -X GET "http://localhost/api/chatbot/history?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### Administration

#### Lister tous les utilisateurs
```bash
curl -X GET "http://localhost/api/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### Créer un utilisateur
```bash
curl -X POST "http://localhost/api/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newteacher",
    "email": "teacher@example.com",
    "password": "secure123",
    "full_name": "New Teacher",
    "role": "teacher"
  }'
```

#### Statistiques
```bash
curl -X GET "http://localhost/api/admin/stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## 🔧 Configuration

### Variables d'environnement

Les variables peuvent être modifiées dans le fichier `docker-compose.yml` :

#### Cassandra
- `CASSANDRA_HOST`: cassandra
- `CASSANDRA_PORT`: 9042

#### MinIO
- `MINIO_ENDPOINT`: minio:9000
- `MINIO_ACCESS_KEY`: minioadmin
- `MINIO_SECRET_KEY`: minioadmin

#### Ollama
- `OLLAMA_URL`: http://ollama:11434
- `MODEL_NAME`: llama3

#### Auth
- `SECRET_KEY`: Changez cette valeur en production !

## 🛠️ Développement

### Structure du projet

```
devops/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── microservices/
│   ├── auth-service/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── file-management-service/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── download-service/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── admin-service/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── chatbot-service/
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── devops_app/
│   └── frontend/
│       ├── login/
│       ├── student/
│       ├── teacher/
│       └── admin/
└── scripts/
    ├── init-db.sh
    ├── setup-ollama.sh
    └── create-default-users.sh
```

### Ajouter un nouveau microservice

1. Créer un nouveau dossier dans `microservices/`
2. Ajouter `main.py`, `requirements.txt`, et `Dockerfile`
3. Ajouter le service dans `docker-compose.yml`
4. Configurer la route dans `nginx/nginx.conf`

## 🐛 Dépannage

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs -f

# Redémarrer un service spécifique
docker-compose restart auth-service
```

### Cassandra n'est pas prêt

Cassandra peut prendre 1-2 minutes pour démarrer. Attendez et vérifiez :

```bash
docker exec -it ent-cassandra cqlsh -e "describe cluster"
```

### Le modèle Ollama ne se télécharge pas

Si vous avez des problèmes réseau :

```bash
# Se connecter au conteneur
docker exec -it ent-ollama bash

# Télécharger manuellement
ollama pull llama3
```

### Erreur de connexion MinIO

Vérifiez que MinIO est démarré :

```bash
docker-compose logs minio
```

## 📊 Monitoring

### Vérifier la santé des services

```bash
# Nginx health check
curl http://localhost/health

# Cassandra
docker exec -it ent-cassandra nodetool status

# MinIO
curl http://localhost:9000/minio/health/live

# Ollama
curl http://localhost:11434/api/tags
```

## 🔒 Sécurité

⚠️ **Important pour la production** :

1. Changez tous les mots de passe par défaut
2. Utilisez HTTPS avec des certificats SSL
3. Configurez des secrets forts pour JWT
4. Activez l'authentification Cassandra
5. Limitez l'accès aux ports exposés
6. Utilisez des variables d'environnement pour les secrets

## 📈 Scalabilité

Pour scaler horizontalement :

```bash
# Scaler un service
docker-compose up -d --scale download-service=3
```

Pour Kubernetes :
1. Convertir avec Kompose : `kompose convert`
2. Appliquer les manifests : `kubectl apply -f .`

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changes (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📝 Licence

Ce projet est sous licence MIT.

## 👥 Auteurs

- Équipe DevOps ENT

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe support

---

**Version**: 1.0.0  
**Date**: Mars 2026
