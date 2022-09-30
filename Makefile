.PHONY: help
help: ## show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: build
build: build ## build project
	@mkdir -p build; \
	cd build; \
	cmake .. && \
	make -j$(nproc)

.PHONY: debug
debug: build ## build debug version
	@mkdir -p build; \
	cd build; \
	BUILD_TYPE=Debug cmake .. && \
	make -j$(nproc)

.PHONY: run
run: ## run project
	@./build/dqn

.PHONY: test
test: ## test project
	@cd build; \
	ctest

.PHONY: clean
clean: ## clean build directory
	@rm -rf open_spiel/build