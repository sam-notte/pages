ROOT_DIR := $(dir $(realpath $(lastword $(MAKECMDGOALS))))
# Default API directory, can be overridden with make API_DIR=/custom/path
API_DIR ?= ../monorepo/apps/back/notte-api

# Common check for API directory
check-api-dir:
	@if [ ! -d "$(API_DIR)" ]; then \
		echo "\033[0;31mError: API directory does not exist: $(API_DIR)\n"; \
		echo "Usage: make <target> API_DIR=/path/to/notte-api\n"; \
		echo "The API directory should point to monorepo/apps/back/notte-api\n"; \
		exit 1; \
	fi

.PHONY: pre-commit-setup
pre-commit-setup:
	@echo "\033[0;35mInstalling pre-commit hooks...\033[0m"
	@uv run pre-commit install
	@uv run pre-commit install-hooks

.PHONY: pre-commit-run
pre-commit-run:
	find src -name "*.py" -type f | xargs uv run --active pre-commit run --files

.PHONY: pre-commit-cleanup
pre-commit-cleanup:
	git checkout ../scripts ../cli ../../../demo-bank ../../../automations

.PHONY: setup
setup: check-api-dir
	@echo "\033[0;35mUsing API directory: $(API_DIR)\033[0m"
	@cd ${API_DIR} && uv sync --dev --all-extras
	@cd ${API_DIR} && uv run patchright install
	@uv pip install ipykernel
	@if [ ! -f .env ]; then \
		if [ -f ${API_DIR}/.env ]; then \
			cp ${API_DIR}/.env .; \
			echo "\033[0;32mCopied .env file to current directory\033[0m"; \
		else \
			echo "\033[0;31mWarning: .env file not found in API directory: $(API_DIR)\n"; \
		fi; \
	else \
		echo "\033[0;33mNote: .env already exists in current directory, not overwriting\033[0m"; \
	fi
	@$(MAKE) pre-commit-setup

.PHONY: build-api
build-api:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "\033[0;31mError: No environment specified. Usage: make build-api <environment>\033[0m"; \
		echo "Example: make build-api dev"; \
		echo "Example: make build-api prod"; \
		echo "Example: make build-api minoan"; \
		exit 1; \
	fi
	@echo "\033[0;35mDeploying API to environment: $(filter-out $@,$(MAKECMDGOALS))\033[0m"
	@cd $(API_DIR) && bash aws/aws_login.sh
	@if [ "$(filter-out $@,$(MAKECMDGOALS))" = "worker" ] || [ "$(filter-out $@,$(MAKECMDGOALS))" = "gateway" ]; then \
		cd $(API_DIR) && sh aws/aws_scaled_build.sh "$(filter-out $@,$(MAKECMDGOALS))"; \
	else \
		cd $(API_DIR) && sh aws/aws_docker_deploy.sh "$(filter-out $@,$(MAKECMDGOALS))"; \
	fi

.PHONY: deploy-api
deploy-api:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "\033[0;31mError: No environment specified. Usage: make deploy-api <environment>\033[0m"; \
		echo "Example: make deploy-api dev"; \
		echo "Example: make deploy-api prod"; \
		echo "Example: make deploy-api minoan"; \
		exit 1; \
	fi
	@echo "\033[0;35mDeploying API to environment: $(filter-out $@,$(MAKECMDGOALS))\033[0m"
	@cd $(API_DIR) && bash aws/aws_login.sh
	@cd $(API_DIR) && bash aws/aws_k8s_deploy.sh "$(filter-out $@,$(MAKECMDGOALS))"


# This allows passing arguments to the deploy target
%:
	@:

.PHONY: hash
hash:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "\033[0;31mError: No word specified. Usage: make hash <word>\033[0m"; \
		echo "Example: make hash nottelabs"; \
		exit 1; \
	fi
	@echo "\033[0;35mHashing word: $(filter-out $@,$(MAKECMDGOALS))\033[0m"
	@python3 $(ROOT_DIR)/devtools/hash-customers/hash.py "$(filter-out $@,$(MAKECMDGOALS))"
