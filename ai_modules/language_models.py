"""Experiment 10: Micro (Bigram) & Small (Trigram) Statistical Language Models for RouteMind AI.

Lightweight, fully local statistical NLP models trained on domain logistics corpus:
- Micro Language Model: Bigram P(w_i | w_{i-1}) = Count(w_{i-1}, w_i) / Count(w_{i-1})
- Small Language Model: Trigram P(w_i | w_{i-2}, w_{i-1}) = Count(w_{i-2}, w_{i-1}, w_i) / Count(w_{i-2}, w_{i-1})
- Supports user prompts, top-k next word probability distributions, and greedy / stochastic text generation.
- Handles out-of-vocabulary and unknown contexts via backoff.
- Clearly contrasts statistical n-gram counting with modern deep transformer LLMs.
"""
import os
import re
from collections import defaultdict, Counter
from typing import Dict, Any, List, Tuple

class LogisticsLanguageModels:
    def __init__(self, corpus_path: str = None):
        if corpus_path is None:
            corpus_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "language_corpus.txt")
        self.corpus_path = corpus_path
        self.vocabulary = set()
        self.unigrams = Counter()
        self.bigrams = Counter()
        self.trigrams = Counter()
        self.bigram_transitions = defaultdict(Counter)
        self.trigram_transitions = defaultdict(Counter)
        self.load_and_train()

    def tokenize(self, text: str) -> List[str]:
        # Lowercase and clean punctuation
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = [t.strip() for t in cleaned.split() if t.strip()]
        return tokens

    def load_and_train(self):
        text = ""
        if os.path.exists(self.corpus_path):
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = "high priority parcel dispatched from central warehouse to final delivery hub."

        sentences = text.split("\n")
        for sentence in sentences:
            tokens = self.tokenize(sentence)
            if not tokens:
                continue

            for t in tokens:
                self.unigrams[t] += 1
                self.vocabulary.add(t)

            # Bigrams
            for i in range(len(tokens) - 1):
                w1, w2 = tokens[i], tokens[i+1]
                self.bigrams[(w1, w2)] += 1
                self.bigram_transitions[w1][w2] += 1

            # Trigrams
            for i in range(len(tokens) - 2):
                w1, w2, w3 = tokens[i], tokens[i+1], tokens[i+2]
                self.trigrams[(w1, w2, w3)] += 1
                self.trigram_transitions[(w1, w2)][w3] += 1

    def predict_bigram(self, previous_word: str, top_k: int = 5) -> Dict[str, Any]:
        """Predicts next word using Micro Bigram model."""
        word = previous_word.strip().lower()
        if word not in self.bigram_transitions:
            # Fallback to most frequent unigrams if word is unseen
            top_unigrams = self.unigrams.most_common(top_k)
            total_uni = sum(self.unigrams.values())
            candidates = [{"word": w, "count": c, "probability": round(c / total_uni, 4)} for w, c in top_unigrams]
            return {
                "model": "Micro Language Model (Bigram: N=2)",
                "context": [word],
                "context_known": False,
                "note": f"Word '{word}' was not seen in training corpus. Falling back to unigram prior distribution.",
                "predictions": candidates
            }

        counts = self.bigram_transitions[word]
        total_transitions = sum(counts.values())
        sorted_candidates = counts.most_common(top_k)

        predictions = [
            {
                "word": next_w,
                "count": count,
                "probability": round(count / total_transitions, 4),
                "formula": f"Count('{word}', '{next_w}') / Count('{word}') = {count}/{total_transitions}"
            }
            for next_w, count in sorted_candidates
        ]

        return {
            "model": "Micro Language Model (Bigram: N=2)",
            "context": [word],
            "context_known": True,
            "total_occurrences": total_transitions,
            "predictions": predictions
        }

    def predict_trigram(self, word1: str, word2: str, top_k: int = 5) -> Dict[str, Any]:
        """Predicts next word using Small Trigram model."""
        w1 = word1.strip().lower()
        w2 = word2.strip().lower()
        pair = (w1, w2)

        if pair in self.trigram_transitions:
            counts = self.trigram_transitions[pair]
            total_transitions = sum(counts.values())
            sorted_candidates = counts.most_common(top_k)
            predictions = [
                {
                    "word": next_w,
                    "count": count,
                    "probability": round(count / total_transitions, 4),
                    "formula": f"Count('{w1}', '{w2}', '{next_w}') / Count('{w1}', '{w2}') = {count}/{total_transitions}"
                }
                for next_w, count in sorted_candidates
            ]
            return {
                "model": "Small Language Model (Trigram: N=3)",
                "context": [w1, w2],
                "context_known": True,
                "total_occurrences": total_transitions,
                "predictions": predictions
            }
        else:
            # Backoff to bigram using w2
            bigram_backoff = self.predict_bigram(w2, top_k=top_k)
            return {
                "model": "Small Language Model (Trigram: N=3) [Backoff to Bigram]",
                "context": [w1, w2],
                "context_known": False,
                "note": f"Trigram context ('{w1}', '{w2}') not found. Gracefully backed off to Bigram on '{w2}'.",
                "predictions": bigram_backoff["predictions"]
            }

    def generate_completion(self, seed_phrase: str, max_words: int = 8, model_type: str = "trigram") -> Dict[str, Any]:
        tokens = self.tokenize(seed_phrase)
        if not tokens:
            tokens = ["central", "dispatch"]

        generated = list(tokens)

        for _ in range(max_words):
            if model_type == "trigram" and len(generated) >= 2:
                w1, w2 = generated[-2], generated[-1]
                if (w1, w2) in self.trigram_transitions:
                    next_word = self.trigram_transitions[(w1, w2)].most_common(1)[0][0]
                elif w2 in self.bigram_transitions:
                    next_word = self.bigram_transitions[w2].most_common(1)[0][0]
                else:
                    break
            else:
                last_w = generated[-1]
                if last_w in self.bigram_transitions:
                    next_word = self.bigram_transitions[last_w].most_common(1)[0][0]
                else:
                    break
            generated.append(next_word)
            if next_word in [".", "hub", "arrival"]:
                # Natural stop condition
                if len(generated) >= 6:
                    break

        return {
            "model_type": model_type,
            "seed_phrase": seed_phrase,
            "tokens_input": tokens,
            "generated_sentence": " ".join(generated) + ".",
            "words_added": len(generated) - len(tokens)
        }

# Global instance
_LM_INSTANCE = None

def get_lm_instance() -> LogisticsLanguageModels:
    global _LM_INSTANCE
    if _LM_INSTANCE is None:
        _LM_INSTANCE = LogisticsLanguageModels()
    return _LM_INSTANCE

def run_language_experiment(user_prompt: str = "high priority", model_choice: str = "both") -> Dict[str, Any]:
    lm = get_lm_instance()
    tokens = lm.tokenize(user_prompt)

    results = {
        "user_prompt": user_prompt,
        "tokenized_prompt": tokens,
        "vocabulary_size": len(lm.vocabulary),
        "corpus_stats": {
            "unique_words": len(lm.vocabulary),
            "unigram_tokens": sum(lm.unigrams.values()),
            "distinct_bigrams": len(lm.bigrams),
            "distinct_trigrams": len(lm.trigrams)
        }
    }

    # Bigram prediction
    seed_word = tokens[-1] if tokens else "dispatch"
    results["bigram_micro_model"] = lm.predict_bigram(seed_word)
    results["bigram_completion"] = lm.generate_completion(user_prompt, max_words=6, model_type="bigram")

    # Trigram prediction
    if len(tokens) >= 2:
        w1, w2 = tokens[-2], tokens[-1]
    elif len(tokens) == 1:
        w1, w2 = "the", tokens[0]
    else:
        w1, w2 = "central", "warehouse"

    results["trigram_small_model"] = lm.predict_trigram(w1, w2)
    results["trigram_completion"] = lm.generate_completion(user_prompt, max_words=7, model_type="trigram")

    results["educational_note"] = (
        "These are statistical n-gram counting models computing conditional frequencies from local text data. "
        "Unlike neural Transformer LLMs (like Gemini, GPT, or BERT), n-gram models have no attention mechanism, "
        "no semantic vector embeddings, and zero general reasoning. They predict the next token purely based on previous token frequency."
    )

    return results
