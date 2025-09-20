# Git Integration System

This is a separate git integration system that can work alongside the main AI system without conflicts.

## Features

- **Code Extraction**: Extract code from the main system's generated files
- **GitHub Upload**: Push extracted code to GitHub repositories
- **Repository Management**: Create, list, and manage GitHub repositories
- **Smart Filtering**: Include/exclude specific file patterns
- **Auto README**: Generate README files automatically

## Structure

```
git-integration/
├── README.md                 # This file
├── github_service.py         # Core GitHub API service
├── code_extractor.py         # Code extraction from main system
├── git_agent.py             # Main git integration agent
├── config.py                # Configuration management
├── requirements.txt         # Dependencies
└── test_integration.py      # Test the integration
```

## Usage

1. **Configure GitHub**: Set up your GitHub token and username
2. **Extract Code**: Extract code from the main system's generated files
3. **Upload to GitHub**: Push the extracted code to a new or existing repository

## Integration with Main System

This system reads from the main system's `backend-ai/generated/` directory and can push code to GitHub without interfering with the main system's operation.

## Safety

- Completely separate from the main system
- No modifications to main system files
- Can be safely tested and debugged independently
- Easy to remove if issues arise
