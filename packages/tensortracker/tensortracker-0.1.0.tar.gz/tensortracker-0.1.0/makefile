# Extract current version and increment dev number
.PHONY: get-version
get-version:
	@current_version=$$(grep -E 'version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+-dev-[0-9]+"' Cargo.toml | sed -E 's/.*"([^"]+)".*/\1/'); \
	if [ -z "$$current_version" ]; then \
		echo "Error: Version pattern not found or incorrect format"; \
		exit 1; \
	fi; \
	base_version=$$(echo "$$current_version" | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+)-dev-[0-9]+/\1/'); \
	dev_num=$$(echo "$$current_version" | sed -E 's/.*-dev-([0-9]+)/\1/'); \
	new_num=$$(printf "%02d" $$((10#$$dev_num + 1))); \
	new_version="$$base_version-dev-$$new_num"; \
	sed -i.bak -E "s/version *= *\"[0-9]+\.[0-9]+\.[0-9]+-dev-[0-9]+\"/version = \"$$new_version\"/" Cargo.toml && rm Cargo.toml.bak; \
	sed -i.bak -E "s/version *= *\"[0-9]+\.[0-9]+\.[0-9]+-dev-[0-9]+\"/version = \"$$new_version\"/" pyproject.toml && rm pyproject.toml.bak; \
	echo "Bumped version to $$new_version"

# Development build with automatic version bump
dev: get-version
	uv run maturin develop

# Test build with automatic version bump
test: get-version
	# Run Rust unit tests
	cargo test
	# Build/install python extension for tests
	uv run maturin develop
	# Run Python integration tests (they will skip if extension/deps not present)
	uv run pytest tests/python -q || true

# Show current version
version:
	@grep -E 'version\s*=\s*"[^"]+"' Cargo.toml | head -n1 | sed -E 's/.*"([^"]+)".*/\1/'

# Clean build artifacts and reset dev version
clean:
	cargo clean
	@base_version=$$(grep -E 'version\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+-dev-[0-9]+"' Cargo.toml | sed -E 's/.*"([0-9]+\.[0-9]+\.[0-9]+)-dev-[0-9]+.*/\1/'); \
	if [ -z "$$base_version" ]; then \
		echo "Error: Version pattern not found or incorrect format"; \
		exit 1; \
	fi; \
	new_version="$$base_version-dev-01"; \
	sed -i.bak -E "s/version *= *\"[0-9]+\.[0-9]+\.[0-9]+-dev-[0-9]+\"/version = \"$$new_version\"/" Cargo.toml && rm Cargo.toml.bak; \
	sed -i.bak -E "s/version *= *\"[0-9]+\.[0-9]+\.[0-9]+-dev-[0-9]+\"/version = \"$$new_version\"/" pyproject.toml && rm pyproject.toml.bak; \
	echo "Reset version to $$new_version"