# ✅ Votre projet ENT est maintenant opérationnel !

## 🎉 Installation Réussie

Tous les services sont en cours d'exécution :
- ✅ Nginx (API Gateway) - Port 80
- ✅ Auth Service - Port 8001
- ✅ File Management Service - Port 8002
- ✅ Download Service - Port 8003
- ✅ Admin Service - Port 8004
- ✅ Chatbot Service - Port 8005
- ✅ Cassandra - Port 9042
- ✅ MinIO - Ports 9000-9001
- ✅ Ollama (IA Llama 3) - Port 11434

## 🌐 Accéder à l'Application

### Frontend
**URL**: http://localhost/login

### Comptes de Test
- **Admin**: `admin` / `admin123`
- **Enseignant**: `teacher` / `teacher123`
- **Étudiant**: `student` / `student123`

### Documentation API (Swagger)
- Auth: http://localhost:8001/docs
- File Management: http://localhost:8002/docs
- Download: http://localhost:8003/docs
- Admin: http://localhost:8004/docs
- Chatbot: http://localhost:8005/docs

### Interfaces Admin
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin)

## 📝 Commandes Utiles

```bash
cd /home/achraf/test-site-docker/devops

# Voir l'état des services
docker compose ps

# Voir les logs
docker compose logs -f [service-name]

# Redémarrer un service
docker compose restart [service-name]

# Arrêter tous les services
docker compose down

# Démarrer tous les services
docker compose up -d

# Tester l'API
./scripts/test-api.sh
```

## 🧪 Test Rapide

### 1. Tester la connexion (Admin)
```bash
curl -X POST "http://localhost/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 2. Tester la connexion (Étudiant)
```bash
curl -X POST "http://localhost/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student&password=student123"
```

### 3. Voir les statistiques (Admin)
```bash
# D'abord obtenir un token
TOKEN=$(curl -s -X POST "http://localhost/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Puis voir les stats
curl -X GET "http://localhost/api/admin/stats" \
  -H "Authorization: Bearer $TOKEN"
```

## 📚 Cas d'Usage

### En tant qu'Enseignant

1. Se connecter sur http://localhost/login avec `teacher` / `teacher123`
2. Aller dans la section "Mes Cours"
3. Cliquer sur "Ajouter un cours"
4. Remplir le titre, description et uploader un fichier
5. Le cours est maintenant disponible pour tous les étudiants

### En tant qu'Étudiant

1. Se connecter sur http://localhost/login avec `student` / `student123`
2. Aller dans la section "Cours disponibles"
3. Voir la liste de tous les cours
4. Cliquer sur "Télécharger" pour obtenir les fichiers
5. Utiliser le chatbot pour poser des questions sur les cours

### En tant qu'Admin

1. Se connecter sur http://localhost/login avec `admin` / `admin123`
2. Voir le dashboard avec les statistiques
3. Gérer les utilisateurs (créer, modifier, supprimer)
4. Voir tous les cours disponibles

## 🤖 Utiliser le Chatbot

```bash
# Obtenir un token
TOKEN=$(curl -s -X POST "http://localhost/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student&password=student123" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Poser une question au chatbot
curl -X POST "http://localhost/api/chatbot/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Quels sont les cours disponibles?"}'
```

## 🔧 Maintenance

### Sauvegarder la base de données
```bash
make backup-db
```

### Voir les logs en temps réel
```bash
docker compose logs -f
```

### Redémarrer tous les services
```bash
docker compose restart
```

### Nettoyer et réinstaller
```bash
docker compose down -v
make setup
```

## 📊 Architecture Déployée

```
Internet
   ↓
Nginx (Port 80) → API Gateway
   ↓
   ├→ Auth Service (8001) ───┐
   ├→ File Mgmt (8002) ──────┤
   ├→ Download (8003) ────────├→ Cassandra (9042)
   ├→ Admin (8004) ──────────┤
   └→ Chatbot (8005) ────────┴→ Ollama (11434)
                  ↓
              MinIO (9000)
```

## 🎯 Prochaines Étapes

1. ✅ Testez la connexion avec les différents comptes
2. ✅ Créez un cours en tant qu'enseignant
3. ✅ Téléchargez-le en tant qu'étudiant
4. ✅ Testez le chatbot
5. ✅ Explorez les APIs avec Swagger
6. ✅ Personnalisez le frontend selon vos besoins

## 🆘 Problèmes?

Si un service ne répond pas:
```bash
# Voir les logs du service
docker compose logs [service-name]

# Redémarrer le service
docker compose restart [service-name]
```

Pour réinitialiser complètement:
```bash
docker compose down -v
docker compose up -d --build
./scripts/init-db.sh
./scripts/create-default-users.sh
```

## 📖 Documentation Complète

- [README.md](README.md) - Documentation complète
- [QUICKSTART.md](QUICKSTART.md) - Guide de démarrage rapide
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture détaillée

---

**Félicitations ! Votre ENT est prêt à être utilisé ! 🚀**
