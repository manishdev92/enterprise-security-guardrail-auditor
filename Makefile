.PHONY: help

help:
	@echo "Available targets:"
	@echo "  make run-api"
	@echo "  make run-dashboard"
	@echo "  make test"

run-api:
	uvicorn app.main:app --reload

run-dashboard:
	streamlit run app/ui/streamlit/app.py

test:
	pytest -q
