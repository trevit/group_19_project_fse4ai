#!/usr/bin/env python3
"""
Test script to demonstrate M1-optimized phrase continuation features
"""

import subprocess
import sys
import time

def run_test(description, command):
    """Run a test command and display results"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    

def main():
    print("🚀 M1 Mac Phrase Continuation - Feature Test Suite")
    print("Testing M1-optimized transformer implementation...")
    
    # Activate virtual environment prefix
    venv_prefix = "source venv/bin/activate && "
    
    tests = [
        ("Basic Transformer Generation", 
         f'{venv_prefix}python3 continue_phrase.py "The future of technology"'),
        
        ("Verbose Mode with Memory Monitoring", 
         f'{venv_prefix}python3 continue_phrase.py "Machine learning will" --verbose'),
        
        ("Custom Max Words", 
         f'{venv_prefix}python3 continue_phrase.py "Artificial intelligence is" --max-words 5'),
        
        ("Specific Model Selection", 
         f'{venv_prefix}python3 continue_phrase.py "Programming languages are" --model distilgpt2'),
        
        ("Markov Fallback Test", 
         f'{venv_prefix}python3 continue_phrase.py "Natural language processing" --use-markov'),
        
        ("Custom Corpus Test", 
         f'{venv_prefix}python3 continue_phrase.py "Deep learning algorithms" --corpus english_corpus.txt'),
        
        ("Reproducible Generation", 
         f'{venv_prefix}python3 continue_phrase.py "Neural networks can" --seed 42'),
        
        ("Performance Test - Multiple Runs", 
         f'{venv_prefix}python3 continue_phrase.py "Data science involves" --verbose --max-words 3')
    ]
    
    passed = 0
    total = len(tests)
    
    for description, command in tests:
        if run_test(description, command):
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print(f"{'='*60}")
    print('python3 continue_phrase.py "Your phrase here"')
    print("\n# With performance monitoring:")
    print('python3 continue_phrase.py "Your phrase here" --verbose')
    print("\n# Force Markov model (faster, less memory):")
    print('python3 continue_phrase.py "Your phrase here" --use-markov')

if __name__ == "__main__":
    main()