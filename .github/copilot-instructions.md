<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Hotel Scraper Project Instructions

This is a Python project for scraping hotel websites to extract information relevant to front desk AI agents. The data is structured and formatted for RAG (Retrieval Augmented Generation) systems.

## Project Context

- **Purpose**: Extract hotel information (policies, amenities, nearby attractions) for AI agent consumption
- **Target Format**: Clean, structured data optimized for RAG systems
- **Deployment**: Designed for DigitalOcean App Platform
- **Data Categories**: Contact info, check-in/out policies, parking, amenities, dining, nearby attractions

## Code Guidelines

1. **Data Structure**: Use the `HotelInfo` dataclass for consistent data formatting
2. **Error Handling**: Always include try-catch blocks for web scraping operations
3. **Rate Limiting**: Be respectful to websites - include delays between requests
4. **Output Formats**: Support JSON, JSONL, text, and markdown formats for different use cases
5. **Logging**: Use structured logging for debugging and monitoring

## RAG Optimization

When generating code for data processing:
- Structure text in clear, semantic sections
- Use consistent field names and formats
- Include metadata (timestamps, source URLs)
- Optimize for text chunking and vector similarity search
- Create human-readable summaries alongside structured data

## Dependencies

- Web scraping: requests, beautifulsoup4, selenium
- Data processing: pandas, pydantic
- Output formatting: rich (for display), jsonlines
- Environment: python-dotenv

## Common Tasks

- Adding new data extraction patterns
- Creating new output formatters
- Implementing rate limiting and error recovery
- Optimizing text structure for RAG systems
- Adding support for new hotel website types
