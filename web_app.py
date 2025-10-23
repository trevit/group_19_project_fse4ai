#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web application for phrase continuation using transformers and Markov chains
"""

import os
import sys
import json
import threading
from flask import Flask, render_template, request, jsonify
from pathlib import Path

# Add current directory to path to import continue_phrase
sys.path.insert(0, str(Path(__file__).parent))

from continue_phrase import (
    generate_with_transformers, 
    generate_markov, 
    build_ngram_model, 
    tokenize, 
    get_default_corpus,
    load_corpus,
    clear_model_cache
)

app = Flask(__name__)

# Global variables for models
markov_model = None
corpus_tokens = None
model_lock = threading.Lock()

def initialize_markov_model():
    """Initialize Markov model on startup"""
    global markov_model, corpus_tokens
    
    try:
        # Try to load War and Peace first, then fallback to other corpora
        script_dir = Path(__file__).parent
        war_and_peace_path = script_dir / "war_and_peace.txt"
        english_corpus_path = script_dir / "english_corpus.txt"
        
        if war_and_peace_path.exists():
            print("Loading War and Peace corpus for Markov model...", file=sys.stderr)
            text = load_corpus(war_and_peace_path)
            # Clean up Project Gutenberg header/footer
            lines = text.split('\n')
            start_idx = 0
            end_idx = len(lines)
            
            # Find actual start of book (after Project Gutenberg header)
            for i, line in enumerate(lines):
                if 'CHAPTER I' in line.upper() or 'BOOK ONE' in line.upper():
                    start_idx = i
                    break
            
            # Find end of book (before Project Gutenberg footer)
            for i in range(len(lines)-1, -1, -1):
                if 'END OF' in lines[i].upper() and 'PROJECT GUTENBERG' in lines[i].upper():
                    end_idx = i
                    break
            
            text = '\n'.join(lines[start_idx:end_idx])
            
        elif english_corpus_path.exists():
            text = load_corpus(english_corpus_path)
        else:
            text = get_default_corpus()
        
        # Build Markov model
        corpus_tokens = tokenize(text.lower())
        markov_model = build_ngram_model(corpus_tokens, n=3)
        print(f"Markov model initialized successfully with {len(corpus_tokens)} tokens", file=sys.stderr)
        
    except Exception as e:
        print(f"Failed to initialize Markov model: {e}", file=sys.stderr)
        markov_model = None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_text():
    """API endpoint for text generation"""
    try:
        data = request.get_json()
        
        if not data or 'phrase' not in data:
            return jsonify({'error': 'Missing phrase parameter'}), 400
        
        
        with model_lock:
            if use_markov:
                # Use Markov model
                if markov_model is None:
                    return jsonify({'error': 'Markov model not initialized'}), 500
                
                try:
                    result = generate_markov(phrase.lower(), markov_model, n=3, max_words=max_words)
                    
                    # Fix capitalization
                    if phrase and phrase[0].isupper() and result:
                        result = result[0].upper() + result[1:]
                    
                    return jsonify({
                        'result': result,
                        'method': 'markov',
                        'original_phrase': phrase
                    })
                    
                except Exception as e:
                    return jsonify({'error': f'Markov generation failed: {str(e)}'}), 500
            
            else:
                # Use transformers
                try:
                    result = generate_with_transformers(phrase, max_words=max_words)
                    
                    return jsonify({
                        'result': result,
                        'method': 'transformers',
                        'original_phrase': phrase
                    })
                    
                except Exception as e:
                    # Fallback to Markov if transformers fail
                    print(f"Transformers failed, using Markov fallback: {e}", file=sys.stderr)
                    
                    if markov_model is None:
                        return jsonify({'error': f'Both transformers and Markov failed: {str(e)}'}), 500
                    
                    try:
                        result = generate_markov(phrase.lower(), markov_model, n=3, max_words=max_words)
                        
                        # Fix capitalization
                        if phrase and phrase[0].isupper() and result:
                            result = result[0].upper() + result[1:]
                        
                        return jsonify({
                            'result': result,
                            'method': 'markov_fallback',
                            'original_phrase': phrase,
                            'warning': 'Transformers failed, used Markov fallback'
                        })
                        
                    except Exception as markov_error:
                        return jsonify({'error': f'Both methods failed: {str(e)}, {str(markov_error)}'}), 500
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    # Initialize Markov model on startup
    print("Initializing models...", file=sys.stderr)
    initialize_markov_model()
    
    # Run Flask app
    print("Starting web server on http://localhost:5001", file=sys.stderr)
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)