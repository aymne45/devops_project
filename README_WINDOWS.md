# 🪟 Guide d'Installation - Windows

Ce guide vous accompagne pas à pas pour installer et lancer le projet ENT sur une machine Windows.

---

## 📋 Prérequis Système

- **Windows 10/11** 
- **Docker Desktop déjà installé** ✅
- **8 GB RAM minimum** (16 GB recommandé)
- **20 GB d'espace disque libre**
- **Connexion Internet**

---

## 🔧 Étape 1 : Vérifier Docker

### 1.1 Démarrer Docker Desktop
1. Ouvrir **Docker Desktop** depuis le menu Démarrer
2. Attendre que l'icône Docker dans la barre des tâches devienne verte
3. Si Docker demande d'utiliser WSL2, vous pouvez **ignorer** et utiliser Hyper-V

### 1.2 Vérifier que Docker fonctionne
Ouvrir PowerShell et taper :
```powershell
docker --version
docker-compose --version
```

✅ Si vous voyez les versions s'afficher, Docker est prêt !

---

## 📥 Étape 3 : Cloner le Projet

### 3.1 Ouvrir Git Bash
- Rechercher "Git Bash" dans le menu Démarrer
- Ouvrir l'application

### 3.2 Cloner le projet
Dans Git Bash, taper :
```bash
# Se placer dans le dossier de votre choix (par exemple Documents)
cd ~/Documents

# Cloner le projet (remplacer par votre URL GitHub)
git clone https://github.com/VOTRE_USERNAME/VOTRE_REPO.git

# Entrer dans le dossier
cd devops
```

---

## 🚀 Étape 4 : Lancer le Projet

### 4.1 Démarrer les services
Dans Git Bash, taper :
```bash
docker-compose up -d --build
```

⏱️ **Patience** : Cette étape prend 3-5 minutes (téléchargement des images Docker).

### 4.2 Vérifier que tout démarre
```bash
docker-compose ps
```

Attendez que tous les services soient "Up" et que Cassandra soit "healthy" (1-2 minutes).

### 4.3 Initialiser la base de données
```bash
./scripts/init-db.sh
```

✅ Vous devriez voir : "Keyspace and tables created successfully!"

### 4.4 Créer les utilisateurs
```bash
./scripts/create-default-users.sh
```

✅ Vous devriez voir 3 utilisateurs créés : admin, teacher, student

### 4.5 (Optionnel) Télécharger l'IA Llama 3
```bash
./scripts/setup-ollama.sh
```

⏱️ **Attention** : Cette étape prend 10-30 minutes selon votre connexion (télécharge 4 GB).
Vous pouvez sauter cette étape, le chatbot ne sera simplement pas disponible.

---

## 🌐 Étape 5 : Accéder à l'Application

### Ouvrir votre navigateur
- **Application** : http://localhost
- **Page de connexion** : http://localhost/login

### Comptes disponibles
| Rôle | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Enseignant | `teacher` | `teacher123` |
| Étudiant | `student` | `student123` |

⚠️ **Changez ces mots de passe après la première connexion !**

---

## 📚 Documentation des APIs

Chaque microservice a sa documentation Swagger :

- **Auth Service** : http://localhost:8001/docs
- **File Management** : http://localhost:8002/docs
- **Download Service** : http://localhost:8003/docs
- **Admin Service** : http://localhost:8004/docs
- **Chatbot Service** : http://localhost:8005/docs

---

## 🛠️ Commandes Utiles

### Voir les logs
```bash
docker-compose logs -f
```
(Appuyer sur `Ctrl+C` pour sortir)

### Arrêter les services
```bash
docker-compose down
```

### Redémarrer les services
```bash
docker-compose restart
```

### Redémarrer un service spécifique
```bash
docker-compose restart auth-service
```

### Voir les services en cours
```bash
docker-compose ps
```

---

## 🐛 Problèmes Courants et Solutions

### ❌ "Docker daemon is not running"
**Solution** : Démarrer Docker Desktop depuis le menu Démarrer et attendre l'icône verte.

### ❌ Docker demande WSL2
**Solution** : Vous pouvez utiliser Hyper-V à la place.
1. Dans Docker Desktop → Settings → General
2. Décocher "Use the WSL 2 based engine"
3. Redémarrer Docker Desktop
4. **Note** : Hyper-V nécessite Windows Pro/Enterprise/Education

### ❌ "Port 80 is already in use"
**Solution** : Un autre programme utilise le port 80.
1. Ouvrir `docker-compose.yml`
2. Ligne 50, changer `"80:80"` en `"8080:80"`
3. Accéder à http://localhost:8080 au lieu de http://localhost

### ❌ "Cassandra is not ready"
**Solution** : Cassandra prend du temps à démarrer.
1. Attendre 2-3 minutes
2. Vérifier : `docker-compose ps`
3. Si "unhealthy", redémarrer : `docker-compose restart cassandra`

### ❌ "Cannot connect to the Docker daemon"
**Solution** :
1. Fermer Docker Desktop
2. Le relancer en tant qu'administrateur (clic droit)
3. Attendre qu'il démarre complètement

### ❌ Les scripts .sh ne fonctionnent pas dans PowerShell
**Solution** : Utiliser **Git Bash** au lieu de PowerShell pour exécuter les scripts.

---

## 🔄 Mettre à Jour le Projet

Si le projet est mis à jour sur GitHub :

```bash
# Arrêter les services
docker-compose down

# Récupérer les mises à jour
git pull

# Reconstruire et redémarrer
docker-compose up -d --build
```

---

## 🆘 Besoin d'Aide ?

### Vérifier la santé des services
```bash
# Nginx
curl http://localhost/health

# Cassandra
docker exec -it ent-cassandra nodetool status

# MinIO
curl http://localhost:9000/minio/health/live

# Ollama
curl http://localhost:11434/api/tags
```

### Voir les logs d'un service spécifique
```bash
docker-compose logs auth-service
docker-compose logs cassandra
docker-compose logs minio
```

### Réinitialiser complètement le projet
⚠️ **Attention : Supprime toutes les données !**
```bash
docker-compose down -v
docker-compose up -d --build
./scripts/init-db.sh
./scripts/create-default-users.sh
```

---

## 📞 Support

- Consulter le [README.md](README.md) principal
- Consulter le [QUICKSTART.md](QUICKSTART.md)
- Consulter l'[ARCHITECTURE.md](ARCHITECTURE.md)

---

## ✅ Checklist Complète

Avant de dire que tout fonctionne, vérifier :

- [ ] Docker Desktop est installé et démarré (icône verte)
- [ ] Git est installé
- [ ] Le projet est cloné
- [ ] `docker-compose ps` montre tous les services "Up"
- [ ] Cassandra est "healthy"
- [ ] http://localhost fonctionne
- [ ] Vous pouvez vous connecter avec `student` / `student123`
- [ ] Les 3 comptes (admin, teacher, student) sont créés

---

**Version** : 1.0.0  
**Date** : Mars 2026  
**Plateforme** : Windows 10/11

Bon courage ! 🚀
