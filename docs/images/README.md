# API Documentation Screenshots

This directory contains screenshots of the API documentation for the README.

## Recommended Screenshots

1. **swagger-overview.png** - Swagger UI showing all endpoints
2. **swagger-auth.png** - Authentication endpoints expanded
3. **swagger-projects.png** - Projects endpoints with example responses
4. **swagger-tasks.png** - Tasks endpoints
5. **swagger-members.png** - Project members endpoints
6. **swagger-schemas.png** - Schema definitions

## How to Generate

1. Start the API: `uv run uvicorn app.main:app --reload`
2. Open http://localhost:8000/docs
3. Take screenshots of the Swagger UI
4. Save them in this directory
5. Reference in README.md:
   ```markdown
   ![Swagger UI](docs/images/swagger-overview.png)
   ```

## Image Guidelines

- Use PNG format for best quality
- Capture at reasonable resolution (1920x1080 is good)
- Crop to show relevant content
- Show both collapsed and expanded views
- Include example request/response bodies
