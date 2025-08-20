import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile


@pytest.fixture
def temp_brain():
    """Create temporary brain directory with synthetic test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_dir = Path(tmpdir) / "brain"
        brain_dir.mkdir()

        # Create comprehensive test data structure
        create_synthetic_notes(brain_dir)
        yield brain_dir


@pytest.fixture
def mock_config(temp_brain):
    """Mock config to use temporary brain directory."""
    with patch("obsidian_ai.infrastructure.config.config") as mock_cfg:
        mock_cfg.brain_dir = temp_brain
        mock_cfg.ignore_patterns = [".git", "__pycache__", ".obsidian"]
        mock_cfg.max_file_size = 2 * 1024 * 1024  # 2MB
        mock_cfg.model = "gpt-4o"
        mock_cfg.max_tool_calls = 5
        yield mock_cfg


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch("obsidian_ai.services.openai_client.OpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value.choices = [
            type("Choice", (), {"message": type("Message", (), {"content": "Test response", "tool_calls": None})()})()
        ]
        yield mock_client


def create_synthetic_notes(brain_dir: Path) -> None:
    """Create comprehensive synthetic test data."""

    # Daily notes
    daily_dir = brain_dir / "daily"
    daily_dir.mkdir()

    (daily_dir / "2024-01-15.md").write_text(
        """
# January 15, 2024

## Tasks
- [ ] Review [[Machine Learning Project]]
- [x] Meeting with [[John Smith]]
- [ ] Read paper on neural networks

## Notes
Met with [[John Smith]] today about the AI research proposal.
The [[Machine Learning Project]] is progressing well.
""".strip()
    )

    (daily_dir / "2024-01-16.md").write_text(
        """
# January 16, 2024

## Reflection
Yesterday's meeting with [[John Smith]] was productive.
Need to focus more on the [[Deep Learning]] aspects.

## Ideas
- Implement transformer architecture
- Use attention mechanisms
- Consider BERT model variations
""".strip()
    )

    # People directory
    people_dir = brain_dir / "people"
    people_dir.mkdir()

    (people_dir / "john-smith.md").write_text(
        """
# John Smith

## Background
Senior researcher at AI Lab, specializing in [[Deep Learning]].

## Expertise
- Neural networks
- Computer vision
- Natural language processing

## Collaborations
- [[Machine Learning Project]] - Lead researcher
- [[Research Paper]] - Co-author

## Contact
Email: john.smith@ailab.com
""".strip()
    )

    (people_dir / "sarah-wilson.md").write_text(
        """
# Sarah Wilson

## Role
Data scientist with focus on [[Statistical Analysis]].

## Skills
- Python programming
- Data visualization
- Machine learning algorithms

## Projects
- [[Data Pipeline]] - Lead developer
- [[Analytics Dashboard]] - UI designer
""".strip()
    )

    # Projects directory
    projects_dir = brain_dir / "projects"
    projects_dir.mkdir()

    (projects_dir / "machine-learning.md").write_text(
        """
# Machine Learning Project

## Overview
Large-scale ML project for predictive analytics.

## Team
- [[John Smith]] - Lead researcher
- [[Sarah Wilson]] - Data scientist
- [[Mike Johnson]] - Software engineer

## Technologies
- Python
- TensorFlow
- PyTorch
- Docker

## Timeline
- Phase 1: Data collection (Q1 2024)
- Phase 2: Model development (Q2 2024)
- Phase 3: Deployment (Q3 2024)

## Challenges
- Data quality issues
- Computational resources
- Model interpretability

## Related
- [[Deep Learning]]
- [[Neural Networks]]
- [[Research Paper]]
""".strip()
    )

    (projects_dir / "data-pipeline.md").write_text(
        """
# Data Pipeline

## Description
Automated data processing pipeline for [[Machine Learning Project]].

## Components
- Data ingestion service
- ETL transformations
- Quality validation
- Storage optimization

## Architecture
Uses microservices pattern with Docker containers.
Kafka for streaming, PostgreSQL for storage.

## Maintainer
[[Sarah Wilson]] is the primary maintainer.
""".strip()
    )

    # Concepts directory
    concepts_dir = brain_dir / "concepts"
    concepts_dir.mkdir()

    (concepts_dir / "deep-learning.md").write_text(
        """
# Deep Learning

## Definition
Subset of machine learning using neural networks with multiple layers.

## Key Concepts
- Backpropagation
- Gradient descent
- Regularization techniques
- Activation functions

## Applications
- Image recognition
- Natural language processing
- Speech recognition
- Recommendation systems

## Researchers
- [[John Smith]] - Expert in computer vision
- [[Alice Chen]] - NLP specialist

## Related Topics
- [[Neural Networks]]
- [[Machine Learning]]
- [[Artificial Intelligence]]
""".strip()
    )

    (concepts_dir / "neural-networks.md").write_text(
        """
# Neural Networks

## Fundamentals
Computational models inspired by biological neural networks.

## Types
- Feedforward networks
- Convolutional neural networks (CNNs)
- Recurrent neural networks (RNNs)
- Transformer networks

## Training
Requires large datasets and computational power.
Uses gradient-based optimization methods.

## Applications in [[Machine Learning Project]]
Primary technology for predictive modeling.
""".strip()
    )

    # Research directory
    research_dir = brain_dir / "research"
    research_dir.mkdir()

    (research_dir / "paper-ideas.md").write_text(
        """
# Research Paper Ideas

## Current Focus
Advancing transformer architectures for [[Deep Learning]].

## Potential Topics
1. Attention mechanisms in computer vision
2. Multi-modal learning approaches
3. Efficient training techniques
4. Model compression methods

## Collaborators
- [[John Smith]] - Primary collaborator
- [[Alice Chen]] - NLP expertise
- [[Sarah Wilson]] - Statistical analysis

## Timeline
- Literature review: February 2024
- Experiments: March-April 2024
- Writing: May 2024
- Submission: June 2024
""".strip()
    )

    # Technical directory
    tech_dir = brain_dir / "technical"
    tech_dir.mkdir()

    (tech_dir / "python-snippets.py").write_text(
        """
# Python Code Snippets

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def preprocess_data(df):
    # Data preprocessing for [[Machine Learning Project]]
    df_clean = df.dropna()
    df_normalized = (df_clean - df_clean.mean()) / df_clean.std()
    return df_normalized

def train_model(X, y):
    # Simple model training example
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    # Training logic here
    return model, X_test, y_test

# Usage in [[Data Pipeline]]
""".strip()
    )

    (tech_dir / "docker-setup.md").write_text(
        """
# Docker Configuration

## For [[Machine Learning Project]]

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## Docker Compose
Used for [[Data Pipeline]] orchestration.

```yaml
version: '3.8'
services:
  ml-service:
    build: .
    ports:
      - "8000:8000"
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mldata
```
""".strip()
    )

    # Create some files in subdirectories for testing
    sub_projects = projects_dir / "archived"
    sub_projects.mkdir()

    (sub_projects / "old-experiment.md").write_text(
        """
# Old Experiment

This was an early attempt at [[Deep Learning]] before the current [[Machine Learning Project]].

## Results
Inconclusive due to limited data.

## Lessons Learned
- Need better data quality
- Importance of feature engineering
- Value of cross-validation
""".strip()
    )

    # Create files with different extensions
    (brain_dir / "notes.txt").write_text("Plain text notes about general topics.")
    (brain_dir / "config.json").write_text('{"project": "obsidian-ai", "version": "1.0"}')
    (brain_dir / "data.csv").write_text("name,role,project\nJohn,researcher,ML\nSarah,analyst,Pipeline")

    # Create some larger files for testing file size limits
    large_content = "This is a large file.\n" * 1000
    (brain_dir / "large-file.md").write_text(large_content)

    # Create files with special characters and spaces
    (brain_dir / "file with spaces.md").write_text("Testing file names with spaces.")
    (brain_dir / "special-chars-@#$.md").write_text("Testing special characters in filenames.")
