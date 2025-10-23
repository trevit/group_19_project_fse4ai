#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
continue_phrase.py
Generates phrase continuation up to 7 words using transformers optimized for M1 Mac.
Usage: python3 continue_phrase.py "your starting phrase" [--corpus path/to/text.txt] [--seed N] [--use-markov]
Primary method: Transformers with M1 MPS acceleration
Fallback method: N-gram (Markov) model for reliability
"""

import sys
import argparse
import random
import re
import os
import time
import gc
from collections import defaultdict, Counter
from pathlib import Path

# Memory and performance monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

MAX_WORDS = 20
MODEL_CACHE = {}

def log_memory_usage(stage=""):
    """Log current memory usage if psutil is available"""
    if PSUTIL_AVAILABLE:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"[{stage}] Memory usage: {memory_mb:.1f} MB", file=sys.stderr)



def clear_model_cache():
    """Clear model cache to free memory"""
    global MODEL_CACHE
    MODEL_CACHE.clear()
    if 'torch' in sys.modules:
        import torch
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    gc.collect()

def get_model_size_priority():
    """Return model names in order of preference for M1 8GB RAM"""
    return [
        "gpt2",  # Good balance of quality and size
        "distilgpt2",  # Smaller, faster
        "microsoft/DialoGPT-small"  # Alternative for conversational style
    ]

def load_transformer_model(model_name=None, device=None):
    """Load transformer model with M1 optimizations and caching"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
    except ImportError as e:
        raise RuntimeError("transformers/torch not installed") from e

    if device is None:
        device = get_optimal_device()
    
    if model_name is None:
        model_names = get_model_size_priority()
    else:
        model_names = [model_name]

    log_memory_usage("before_model_load")

    for model_name in model_names:
        try:
            # Check cache first
            cache_key = f"{model_name}_{device}"
            if cache_key in MODEL_CACHE:
                print(f"Using cached model: {model_name}", file=sys.stderr)
                return MODEL_CACHE[cache_key]

            print(f"Loading model: {model_name} on {device}", file=sys.stderr)
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Load model with memory optimization
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device.type == "mps" else torch.float32,
                low_cpu_mem_usage=True
            )
            
            model.to(device)
            model.eval()  # Set to evaluation mode

            # Cache the model
            MODEL_CACHE[cache_key] = (model, tokenizer, device)
            
            log_memory_usage(f"after_loading_{model_name}")
            print(f"Successfully loaded {model_name} on {device}", file=sys.stderr)
            
            return model, tokenizer, device

        except Exception as e:
            print(f"Failed to load {model_name}: {e}", file=sys.stderr)
            continue

    raise RuntimeError("Failed to load any transformer model")

def generate_with_transformers(start_phrase, max_words=MAX_WORDS, model_name=None):
    """Generate text continuation using transformers with M1 optimizations"""
    try:
        import torch
        
        model, tokenizer, device = load_transformer_model(model_name)
        
        # Generate with optimized parameters for English
        with torch.no_grad():  # Disable gradients for inference
            outputs = model.generate(
                inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.8,  # Slightly more conservative for better quality
                top_p=0.9,        # Nucleus sampling
                top_k=50,         # Top-k sampling
                repetition_penalty=1.1,  # Reduce repetition
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                early_stopping=True
            )
        
        # Decode output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        log_memory_usage("after_generation")
        
        # Post-process: limit to approximately max_words additional words
        if generated_text.startswith(start_phrase):
            continuation = generated_text[len(start_phrase):].strip()
        else:
            continuation = generated_text.strip()
        
        # Clean up punctuation spacing
        result = re.sub(r'\s+([.,:;?!])', r'\1', result)
        
        return result.strip()
        
    except Exception as e:
        raise RuntimeError(f"Transformer generation failed: {e}") from e

# Markov model functions (fallback)
def tokenize(text):
    """Simple tokenization: words + punctuation as separate tokens"""
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    return [t for t in tokens if t.strip()]

def build_ngram_model(tokens, n=3):
    """Build n-gram model for Markov chain"""
    model = defaultdict(Counter)
    pad = ["<s>"] * (n-1)
    seq = pad + tokens + ["</s>"]
    for i in range(len(seq) - n + 1):
        ctx = tuple(seq[i:i+n-1])
        nxt = seq[i+n-1]
        model[ctx][nxt] += 1
    return model

def sample_next(counter):
    """Sample next word based on frequency"""
    items = list(counter.items())
    words, weights = zip(*items)
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for w, wt in zip(words, weights):
        if upto + wt >= r:
            return w
        upto += wt
    return words[-1]

def generate_markov(start_phrase, model, n=3, max_words=MAX_WORDS):
    """Generate text using Markov chain (fallback method)"""
    start_tokens = tokenize(start_phrase)
    if not start_tokens:
        return start_phrase
    
    out = start_tokens.copy()
    
    # Simple fallback generation - just add common words if model fails
    common_continuations = [
        "is", "are", "will", "can", "should", "would", "could", "may", "might",
        "the", "a", "an", "and", "or", "but", "with", "for", "to", "of", "in",
        "very", "more", "most", "good", "great", "important", "useful", "helpful"
    ]
    
    # Try to use the model, but with strict limits
    for i in range(min(max_words, 7)):  # Strict limit
        # Get context
        if len(out) >= n-1:
            ctx = tuple(out[-(n-1):])
        else:
            ctx = tuple(["<s>"] * (n-1-len(out)) + out)
        
        # Try to find next word in model
        next_word = None
        if ctx in model and model[ctx]:
            try:
                next_word = sample_next(model[ctx])
                if next_word == "</s>" or not next_word.strip():
                    break
            except:
                next_word = None
        
        # If model fails, use fallback
        if not next_word:
            if i < len(common_continuations):
                next_word = common_continuations[i]
            else:
                break
        
        out.append(next_word)
    
    # Join tokens with proper spacing
    result = []
    for tok in out:
        if result and re.match(r"[.,:;?!%)\]]", tok):
            result[-1] = result[-1] + tok
        elif result and re.match(r"['\"(\[]", tok):
            result.append(tok)
        else:
            result.append(tok)
    
    return " ".join(result)

def load_corpus(path):
    """Load text corpus from file"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_default_corpus():
    """Get default English corpus"""
    # Try to load english_corpus.txt first
    script_dir = Path(__file__).parent
    english_corpus_path = script_dir / "english_corpus.txt"
    
    if english_corpus_path.exists():
        try:
            return load_corpus(english_corpus_path)
        except Exception:
            pass
    
    # Fallback to embedded corpus
    return (
        "The quick brown fox jumps over the lazy dog. "
        "Machine learning is transforming technology. "
        "Natural language processing enables computers to understand human language. "
        "Programming requires creativity and logical thinking. "
        "The future of technology looks promising with advances in AI."
    )

def main():
    parser = argparse.ArgumentParser(
        description="Generate phrase continuation using transformers (M1 optimized)"
    )
    parser.add_argument("phrase", type=str, help="Starting phrase in quotes")
    parser.add_argument("--corpus", type=str, default=None, 
                       help="Path to text corpus file (UTF-8)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--use-markov", action="store_true", 
                       help="Force use of Markov model instead of transformers")
    parser.add_argument("--model", type=str, default=None,
                       help="Specific transformer model to use")
    parser.add_argument("--max-words", type=int, default=MAX_WORDS,
                       help=f"Maximum words to generate (default: {MAX_WORDS})")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed processing information")
    
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    max_words = min(args.max_words, 15)  # Cap at 15 for memory safety

    if args.verbose:
        log_memory_usage("startup")

    # Try transformers first (unless explicitly disabled)
    if not args.use_markov:
        try:
            start_time = time.time()
            result = generate_with_transformers(
                args.phrase, 
                max_words=max_words, 
                model_name=args.model
            )
            
            if args.verbose:
                elapsed = time.time() - start_time
                print(f"Generation time: {elapsed:.2f}s", file=sys.stderr)
                log_memory_usage("after_transformers")
            
            print(result)
            return
            
        except Exception as e:
            print(f"Transformers failed, falling back to Markov: {e}", file=sys.stderr)
            clear_model_cache()  # Free memory before fallback

    # Fallback to Markov model
    if args.verbose:
        print("Using Markov model", file=sys.stderr)
    
    # Load corpus
    if args.corpus:
        try:
            text = load_corpus(args.corpus)
        except Exception as e:
            print(f"Failed to load corpus: {e}", file=sys.stderr)
            print("Using default corpus", file=sys.stderr)
            text = get_default_corpus()
    else:
        text = get_default_corpus()

    # Build Markov model
    tokens = tokenize(text.lower())
    if not tokens:
        print("Empty corpus - cannot generate", file=sys.stderr)
        sys.exit(1)

    n = 3
    model = build_ngram_model(tokens, n=n)
    
    # Generate text
    generated = generate_markov(args.phrase.lower(), model, n=n, max_words=max_words)
    
    # Fix capitalization
    if args.phrase and args.phrase[0].isupper() and generated:
        generated = generated[0].upper() + generated[1:]
    
    print(generated)

if __name__ == "__main__":
    main()
