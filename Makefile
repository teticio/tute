.PHONY: help
help: ## show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  \033[36m\033[0m\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: build
build: ## build project
	@mkdir -p build; \
	cd build; \
	cmake .. && \
	make -j$(nproc)

.PHONY: debug
debug: ## build debug version
	@mkdir -p build; \
	cd build; \
	BUILD_TYPE=Debug cmake .. && \
	make -j$(nproc)

.PHONY: run
run: ## run project
	@build/tute-prefix/src/tute-build/tute_game

.PHONY: test
test: ## test project
	@cd build/tute-prefix/src/tute-build; \
	ctest -R tute_test

.PHONY: clean
clean: ## clean build directory
	@rm -rf build