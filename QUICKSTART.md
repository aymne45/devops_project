# 🚀 Guide de Démarrage Rapide

## Installation en 5 minutes

### Prérequis
- Docker et Docker Compose installés
- 8 GB RAM minimum
- Ports disponibles: 80, 8001-8005, 9000-9001, 9042, 11434

### Étape 1: Démarrer les services

```bash
cd devops
docker-compose up -d --build
```

⏱️ Temps estimé: 2-3 minutes

### Étape 2: Attendre que Cassandra soit prêt

```bash
# Vérifier le statut
docker-compose ps

# Attendre que cassandra soit "healthy"
watch docker-compose ps
```

⏱️ Temps estimé: 30-60 secondes

### Étape 3: Initialiser la base de données

```bash
chmod +x scripts/*.sh
./scripts/init-db.sh
```

⏱️ Temps estimé: 10 secondes

### Étape 4: Créer les utilisateurs

```bash
./scripts/create-default-users.sh
```

⏱️ Temps estimé: 5 secondes

### Étape 5: (Optionnel) Télécharger Llama 3

```bash
./scripts/setup-ollama.sh
```

⏱️ Temps estimé: 10-30 minutes (selon votre connexion)

**Note**: Vous pouvez utiliser l'application sans cette étape. Le chatbot ne sera simplement pas disponible.

### Étape 6: Accéder à l'application

🌐 **Frontend**: http://localhost/login

👤 **Comptes par défaut**:
- **Admin**: `admin` / `admin123`
- **Enseignant**: `teacher` / `teacher123`
- **Étudiant**: `student` / `student123`

⚠️ **Changez ces mots de passe en production !**

## 📚 API Documentation

Chaque microservice expose une documentation Swagger:

- Auth: http://localhost:8001/docs
- File Management: http://localhost:8002/docs
- Download: http://localhost:8003/docs
- Admin: http://localhost:8004/docs
- Chatbot: http://localhost:8005/docs

## 🛠️ Commandes Utiles

### Avec Make (recommandé)

```bash
# Installation complète automatique
make setup

# Démarrer les services
make up

# Voir les logs
make logs

# Arrêter les services
make down

# Vérifier la santé
make health
```

### Sans Make

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f

# Redémarrer un service
docker-compose restart auth-service
```

## 🐛 Problèmes Courants

### Les services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Redémarrer
docker-compose restart
```

### Erreur de connexion à Cassandra

Cassandra prend du temps à démarrer. Attendez 1-2 minutes et relancez:

```bash
docker-compose restart auth-service
```

### Port déjà utilisé

Si le port 80 est occupé:

```bash
# Modifier docker-compose.yml
# Changer "80:80" en "8080:80"
docker-compose up -d
# Accéder à http://localhost:8080
```

## 📊 Vérifier que Tout Fonctionne

```bash
# Vérifier la santé des services
curl http://localhost/health

# Vérifier tous les services
make health
```

## 🎯 Prochaines Étapes

1. ✅ Se connecter avec un compte par défaut
2. ✅ Créer un cours (compte enseignant)
3. ✅ Télécharger un cours (compte étudiant)
4. ✅ Créer un utilisateur (compte admin)
5. ✅ Utiliser le chatbot IA (après avoir téléchargé Llama 3)

## 📖 Documentation Complète

Pour plus de détails, consultez [README.md](README.md)

## 🆘 Besoin d'Aide?

- Vérifiez les logs: `docker-compose logs -f [service-name]`
- Consultez la documentation API
- Vérifiez la santé des services: `make health`
