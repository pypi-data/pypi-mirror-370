# Generate all combinations of Python and Django versions
COMBINATIONS := py27-django110 py27-django111 \
                py34-django110 py34-django111 py34-django20 \
                py35-django110 py35-django111 py35-django20 py35-django21 py35-django22 \
                py36-django111 py36-django20 py36-django21 py36-django22 py36-django30 py36-django31 \
                py37-django111 py37-django20 py37-django21 py37-django22 py37-django30 py37-django31 \
                py38-django22 py38-django30 py38-django31 py38-django32 py38-django40 py38-django41 py38-django42 \
                py39-django32 py39-django40 py39-django41 py39-django42 \
                py310-django40 py310-django41 py310-django42 py310-django50 \
                py311-django42 py311-django50 \
                py312-django42 py312-django50

# ANSI color codes
YELLOW := \033[33m
WHITE := \033[97m
RESET := \033[0m

# Define commands
.PHONY: test help

help:
	@echo "Usage:"
	@echo "  make test                          # Run tests for every combination of Python and Django versions"
	@echo "  make test py=<version>             # Run tests for the specified Python version and all Django versions"


test:
ifdef py
	@echo "$(WHITE)Running tests for available combinations of Python $(YELLOW)$(py)$(WHITE) and all Django versions$(RESET)"
	@for combination in $(filter py$(py)-%,$(COMBINATIONS)); do \
		echo "$(WHITE)Running tests for $(YELLOW)$$combination$(RESET)"; \
		tox -e $$combination; \
	done
else
	@echo "$(WHITE)Running tests for every combination of Python and Django versions"
	@for combination in $(COMBINATIONS); do \
		echo "$(WHITE)Running tests for $(YELLOW)$$combination$(RESET)"; \
		tox -e $$combination; \
	done
endif

.DEFAULT_GOAL := test
