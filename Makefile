.PHONY: dev clean test findings evaluate setup

# === Quick Start ===
setup:
	pip install -r requirements.txt

dev:
	@echo "Starting backend..."
	cd backend && python3 main.py &
	@sleep 2
	@echo "Starting frontend..."
	cd frontend && streamlit run app.py &
	@echo "✅ Backend: http://localhost:8000  |  Frontend: http://localhost:8501"

# === Testing ===
test:
	cd backend && python3 test_traps.py

findings:
	curl -s http://localhost:8000/findings | python3 -c "import sys,json; d=json.load(sys.stdin); json.dump(d['findings'], open('backend/out/findings.json','w'), ensure_ascii=False, indent=2); print(f'Exported {len(d[\"findings\"])} findings')"

evaluate:
	cd backend && python3 evaluate.py --truth fixtures/ground_truth.json --pred out/findings.json

# === Security: Clean data after contest ===
clean:
	@echo "🧹 Cleaning sample data & logs..."
	rm -f backend/data/audit_log.json
	rm -f backend/data/audit_log.jsonl
	rm -f backend/out/*.json
	rm -rf backend/__pycache__ backend/agents/__pycache__
	rm -rf frontend/__pycache__
	@echo "✅ Done. Sample data retained (required for demo)."

clean-all: clean
	@echo "🧹 Deep clean — removing sample data..."
	rm -f backend/data/*.csv
	rm -f backend/data/*.json
	rm -rf backend/data/emails/
	@echo "✅ All sample data removed."
