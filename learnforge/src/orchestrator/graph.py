"""LangGraph orchestrator — state machine wiring Curriculum Architect, Content Generator, Adaptive Assessor + RAG."""
import logging
from typing import TypedDict, Optional, List, Dict

from langgraph.graph import StateGraph, END

from src.agents.curriculum_architect import CurriculumArchitect
from src.agents.content_generator import ContentGenerator
from src.agents.adaptive_assessor import AdaptiveAssessor

logger = logging.getLogger(__name__)


# ── State Schema ──

class LearnState(TypedDict, total=False):
    action: str                      # CURRICULUM | LESSON | QUIZ | FLASHCARD | EVALUATE | RECOMMEND
    topic: str
    level: str
    curriculum: Optional[Dict]
    active_module: Optional[Dict]
    lesson: Optional[Dict]
    quiz: Optional[Dict]
    flashcards: Optional[Dict]
    user_answer: Optional[str]
    question: Optional[Dict]
    evaluation: Optional[Dict]
    retrieved_docs: List[Dict]
    knowledge_gaps: List[str]
    recommendations: Optional[Dict]
    error: Optional[str]


# ── Lazy singletons ──

_architect = None
_generator = None
_assessor = None
_retriever = None
_reranker = None


def _get_architect():
    global _architect
    if _architect is None:
        _architect = CurriculumArchitect()
    return _architect


def _get_generator():
    global _generator
    if _generator is None:
        _generator = ContentGenerator()
    return _generator


def _get_assessor():
    global _assessor
    if _assessor is None:
        _assessor = AdaptiveAssessor()
    return _assessor


def _get_retriever():
    global _retriever
    if _retriever is None:
        try:
            from src.rag.retrieve import HybridRetriever
            _retriever = HybridRetriever()
        except Exception as e:
            logger.warning(f"Could not init retriever: {e}")
    return _retriever


def _get_reranker():
    global _reranker
    if _reranker is None:
        try:
            from src.rag.retrieve import Reranker
            _reranker = Reranker()
        except Exception as e:
            logger.warning(f"Could not init reranker: {e}")
    return _reranker


# ── Node Functions ──

def curriculum_node(state: LearnState) -> LearnState:
    """Agent 1: Generate curriculum."""
    architect = _get_architect()
    curriculum = architect.generate_curriculum(state.get("topic", ""), state.get("level", "intermediate"))
    return {**state, "curriculum": curriculum}


def lesson_node(state: LearnState) -> LearnState:
    """Agent 2: Generate lesson for active module."""
    generator = _get_generator()
    module = state.get("active_module", {})
    lesson = generator.generate_lesson(module, state.get("topic", ""), state.get("level", "intermediate"))
    return {**state, "lesson": lesson}


def quiz_node(state: LearnState) -> LearnState:
    """Agent 2: Generate quiz for active module."""
    generator = _get_generator()
    module = state.get("active_module", {})
    quiz = generator.generate_quiz(module, state.get("topic", ""), state.get("level", "intermediate"))
    return {**state, "quiz": quiz}


def flashcard_node(state: LearnState) -> LearnState:
    """Agent 2: Generate flashcards for active module."""
    generator = _get_generator()
    module = state.get("active_module", {})
    flashcards = generator.generate_flashcards(module, state.get("topic", ""), state.get("level", "intermediate"))
    return {**state, "flashcards": flashcards}


def retrieve_node(state: LearnState) -> LearnState:
    """RAG: Retrieve relevant documents for the assessor."""
    retriever = _get_retriever()
    if retriever is None:
        return {**state, "retrieved_docs": []}

    question = state.get("question", {})
    topic = state.get("topic", "")
    user_answer = state.get("user_answer", "")

    query = f"{topic} {question.get('question', '')} {user_answer[:200]}"
    candidates = retriever.retrieve(query, top_k=10, method="hybrid")

    reranker = _get_reranker()
    if reranker and candidates:
        top_docs = reranker.rerank(query, candidates, top_k=3)
    else:
        top_docs = candidates[:3]

    formatted = [{
        "source_id": d.get("metadata", {}).get("source_id", d.get("id", "")),
        "text": d.get("text", ""),
        "score": d.get("rerank_score", d.get("score", 0.0)),
    } for d in top_docs]

    return {**state, "retrieved_docs": formatted}


def evaluate_node(state: LearnState) -> LearnState:
    """Agent 3: Evaluate user answer with RAG context."""
    assessor = _get_assessor()
    evaluation = assessor.evaluate_answer(
        state.get("question", {}),
        state.get("user_answer", ""),
        state.get("retrieved_docs", []),
    )
    gaps = evaluation.get("gap_tags", [])
    return {**state, "evaluation": evaluation, "knowledge_gaps": gaps}


def recommend_node(state: LearnState) -> LearnState:
    """Agent 3: Generate study recommendations from knowledge gaps."""
    assessor = _get_assessor()
    recommendations = assessor.generate_study_recommendation(
        state.get("knowledge_gaps", []),
        state.get("topic", ""),
        state.get("level", "intermediate"),
    )
    return {**state, "recommendations": recommendations}


# ── Router ──

def router(state: LearnState) -> str:
    action = state.get("action", "CURRICULUM")
    mapping = {
        "CURRICULUM": "curriculum",
        "LESSON": "lesson",
        "QUIZ": "quiz",
        "FLASHCARD": "flashcard",
        "EVALUATE": "retrieve",     # evaluate goes through RAG first
        "RECOMMEND": "recommend",
    }
    return mapping.get(action, "curriculum")


# ── Build Graph ──

def build_graph():
    graph = StateGraph(LearnState)

    graph.add_node("curriculum", curriculum_node)
    graph.add_node("lesson", lesson_node)
    graph.add_node("quiz", quiz_node)
    graph.add_node("flashcard", flashcard_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("recommend", recommend_node)

    graph.set_conditional_entry_point(router)

    # After curriculum, lesson, quiz, flashcard → END
    graph.add_edge("curriculum", END)
    graph.add_edge("lesson", END)
    graph.add_edge("quiz", END)
    graph.add_edge("flashcard", END)

    # Evaluate flow: retrieve → evaluate → END
    graph.add_edge("retrieve", "evaluate")
    graph.add_edge("evaluate", END)

    # Recommend → END
    graph.add_edge("recommend", END)

    return graph.compile()


# ── Singleton & Convenience ──

_compiled_graph = None


def get_orchestrator():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_pipeline(action: str, topic: str = "", level: str = "intermediate",
                 active_module: dict = None, question: dict = None,
                 user_answer: str = None, knowledge_gaps: list = None) -> dict:
    """
    Run the orchestrator pipeline.

    Actions: CURRICULUM, LESSON, QUIZ, FLASHCARD, EVALUATE, RECOMMEND
    Returns the full updated state dict.
    """
    orchestrator = get_orchestrator()
    state = {
        "action": action,
        "topic": topic,
        "level": level,
        "active_module": active_module or {},
        "question": question or {},
        "user_answer": user_answer or "",
        "knowledge_gaps": knowledge_gaps or [],
        "retrieved_docs": [],
    }
    return orchestrator.invoke(state)
