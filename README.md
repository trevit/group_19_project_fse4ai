# Phrase Continuation App

## Team members:

Stepan Epifantsev

Viktor Nekrasov

Yakupova Valeria

Viktor Shilov

A high-performance phrase continuation application specifically optimized for Apple M1 Macs with 8GB RAM. Uses transformer models with MPS acceleration as the primary method, with Markov chains as a reliable fallback.

## Features

- **M1 GPU Acceleration**: Leverages Metal Performance Shaders (MPS) for optimal performance
- **Smart Memory Management**: Optimized for 8GB RAM with model caching and monitoring
- **Dual Generation Methods**: GPT-2 transformers (primary) + Markov chains (fallback)
- **English Optimized**: Fine-tuned parameters for high-quality English text generation
- **Performance Monitoring**: Real-time memory usage and generation time tracking
- **Modern Python Packaging**: Uses `pyproject.toml` for dependency management

## Quick Start

### Docker setup
```bash
# Build and start the application
docker-compose up --build
```

#### Web Interface
- Open your browser and go to: `http://localhost:5001`
- The web interface provides an easy-to-use GUI for phrase continuation
- Toggle between transformer and Markov methods
- Real-time text generation with performance monitoring
