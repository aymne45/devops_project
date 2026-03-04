.PHONY: help build up down restart logs clean init-db setup-ollama create-users

help: ## Afficher l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construire les images Docker
	docker compose build

up: ## Démarrer tous les services
	docker compose up -d

down: ## Arrêter tous les services
	docker compose down

restart: ## Redémarrer tous les services
	docker compose restart

logs: ## Afficher les logs
	docker compose logs -f

ps: ## Afficher le statut des services
	docker compose ps

clean: ## Nettoyer les volumes et images
	docker compose down -v
	docker system prune -f

init-db: ## Initialiser la base de données Cassandra
	@echo "Initialisation de la base de données..."
	@sleep 30
	@./scripts/init-db.sh

setup-ollama: ## Télécharger le modèle Llama 3
	@echo "Téléchargement du modèle Llama 3..."
	@./scripts/setup-ollama.sh

create-users: ## Créer les utilisateurs par défaut
	@echo "Création des utilisateurs par défaut..."
	@./scripts/create-default-users.sh

setup: build up init-db setup-ollama create-users ## Installation complète
	@echo "Installation terminée!"
	@echo "Accédez à l'application sur http://localhost"
	@echo ""
	@echo "Utilisateurs par défaut:"
	@echo "  Admin    : admin / admin123"
	@echo "  Teacher  : teacher / teacher123"
	@echo "  Student  : student / student123"

dev: up logs ## Démarrer en mode développement avec logs

health: ## Vérifier la santé des services
	@echo "=== Auth Service ==="
	@curl -s http://localhost:8001/ | jq . || echo "Service non disponible"
	@echo "\n=== File Management ==="
	@curl -s http://localhost:8002/ | jq . || echo "Service non disponible"
	@echo "\n=== Download Service ==="
	@curl -s http://localhost:8003/ | jq . || echo "Service non disponible"
	@echo "\n=== Admin Service ==="
	@curl -s http://localhost:8004/ | jq . || echo "Service non disponible"
	@echo "\n=== Chatbot Service ==="
	@curl -s http://localhost:8005/ | jq . || echo "Service non disponible"
	@echo "\n=== Nginx Health ==="
	@curl -s http://localhost/health || echo "Service non disponible"

backup-db: ## Sauvegarder la base de données
	@echo "Sauvegarde de la base de données..."
	@docker exec ent-cassandra cqlsh -e "DESCRIBE KEYSPACE ent_db" > backup_schema.cql
	@echo "Sauvegarde terminée: backup_schema.cql"

restore-db: ## Restaurer la base de données
	@echo "Restauration de la base de données..."
	@docker exec -i ent-cassandra cqlsh < backup_schema.cql
	@echo "Restauration terminée"
