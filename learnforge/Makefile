.PHONY: setup index demo eval clean

setup:
	pip install -e . --break-system-packages 2>/dev/null || pip install -e .
	@echo "✅ Setup complete"

index:
	python scripts/build_index.py
	@echo "✅ ChromaDB index built"

demo:
	LEARNFORGE_MODE=demo streamlit run app/streamlit_app.py --server.port 8501

run:
	streamlit run app/streamlit_app.py --server.port 8501

eval:
	python scripts/run_evals.py
	@echo "✅ Evaluations complete"

clean:
	rm -rf chroma_db/ learnforge.db data/generated/*
	@echo "🧹 Cleaned"
