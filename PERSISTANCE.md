# 💾 Persistance des Données - ENT

## ✅ Configuration Actuelle

Tous les utilisateurs créés dans l'application ENT sont **automatiquement sauvegardés** et **persistants** grâce aux volumes Docker configurés.

### 📂 Volumes Configurés

Dans `docker-compose.yml`, trois volumes sont définis pour la persistance :

```yaml
volumes:
  cassandra_data:    # Base de données utilisateurs
  minio_data:        # Fichiers et cours uploadés
  ollama_data:       # Modèle IA
```

### 🗄️ Base de Données Cassandra

La configuration de Cassandra inclut le volume de persistance :

```yaml
cassandra:
  volumes:
    - cassandra_data:/var/lib/cassandra
```

**Emplacement physique** : `/var/lib/docker/volumes/devo_cassandra_data/_data`

## 🔄 Comportement avec les Commandes Docker

### ✅ Les données RESTENT après :

- `docker compose restart` - ✅ Redémarre les conteneurs, données préservées
- `docker compose stop` puis `docker compose start` - ✅ Données préservées
- `docker compose down` puis `docker compose up` - ✅ Données préservées
- Redémarrage de la machine - ✅ Données préservées

### ⚠️ Les données sont SUPPRIMÉES avec :

- `docker compose down -v` (l'option `-v` supprime les volumes)
- `docker volume rm devo_cassandra_data`
- `make clean` (si configuré pour supprimer les volumes)

## 🧪 Tester la Persistance

Utilisez le script de test fourni :

```bash
./scripts/test-persistance.sh
```

Ce script va :
1. Afficher les utilisateurs actuels
2. Redémarrer tous les services
3. Vérifier que les utilisateurs sont toujours présents

## 📊 Vérifier Manuellement les Données

### Voir tous les utilisateurs :

```bash
docker exec ent-cassandra cqlsh -e "SELECT username, email, full_name, role FROM ent_db.users;"
```

### Compter les utilisateurs :

```bash
docker exec ent-cassandra cqlsh -e "SELECT COUNT(*) FROM ent_db.users;"
```

### Voir les utilisateurs par rôle :

```bash
# Étudiants
docker exec ent-cassandra cqlsh -e "SELECT username, full_name FROM ent_db.users WHERE role='student' ALLOW FILTERING;"

# Enseignants
docker exec ent-cassandra cqlsh -e "SELECT username, full_name FROM ent_db.users WHERE role='teacher' ALLOW FILTERING;"

# Admins
docker exec ent-cassandra cqlsh -e "SELECT username, full_name FROM ent_db.users WHERE role='admin' ALLOW FILTERING;"
```

## 🎯 Flux de Création d'Utilisateur

1. **Admin** se connecte sur http://localhost/admin/dashboard.html
2. **Admin** remplit le formulaire avec Prénom et Nom
3. **Email généré automatiquement** : `prenom_nom@um5.ac.ma`
4. **Mot de passe généré automatiquement** : 12 caractères aléatoires
5. **Username** : `prenom_nom`
6. **Données envoyées** à l'API `/register` du service Auth
7. **Stockage dans Cassandra** dans la table `ent_db.users`
8. **Volume Docker** persiste les données sur le disque

## 🔐 Sécurité de la Persistance

### Sauvegarde recommandée :

```bash
# Backup du volume Cassandra
docker run --rm \
  -v devo_cassandra_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/cassandra-$(date +%Y%m%d).tar.gz /data
```

### Restauration :

```bash
# Restore du volume Cassandra
docker run --rm \
  -v devo_cassandra_data:/data \
  -v $(pwd)/backups:/backup \
  alpine sh -c "cd /data && tar xzf /backup/cassandra-YYYYMMDD.tar.gz --strip 1"
```

## 📝 Notes Importantes

1. **Ne jamais utiliser** `docker compose down -v` en production
2. **Faire des backups réguliers** du volume `cassandra_data`
3. **Les volumes persistent** même si les conteneurs sont supprimés
4. **Seul le volume est important** pour la persistance des données
5. **Les utilisateurs créés par l'admin** sont immédiatement accessibles pour se connecter

## 🎉 Résumé

✅ **OUI** - Tous les utilisateurs créés sont stockés de manière permanente  
✅ **OUI** - Les données survivent aux redémarrages  
✅ **OUI** - Les données restent même après `docker compose down`  
✅ **OUI** - Chaque utilisateur créé par l'admin peut se connecter immédiatement  

La configuration actuelle garantit une **persistance complète** des données utilisateurs ! 🚀
