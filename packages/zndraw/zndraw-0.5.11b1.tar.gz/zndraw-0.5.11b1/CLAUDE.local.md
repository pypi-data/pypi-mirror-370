# Bash commands
- cd app && bun run build: Build the project (or bun vite build to ignore typescript errors)
- cd app && bun run format: (or bun run format:check) to format the files
- cd app && bun run lint: (or bun run lint:fix) to lint the files
- uv add: add a new python package dependency
- uvx pre-commit run --all-files : run the pre-commit hooks for lint and format of all files 
- uv run pytest tests/ : run the test suite

# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Package design
- The Typescript part of the App is in /app
- The Python code of the app is in /zndraw and /zndraw_app
- The Python and Typescript part use flask and mostly websockets via socket.io and znsocket (https://zincware.github.io/ZnSocket/python_api.html and https://zincware.github.io/ZnSocket/javascript_api.html ) for communication
- The package heavily relies on frontend components. Ask the user to verify for changes you can not test yourself by including `console.log` statements.

# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
- When changing the exposed Python user API, keep a focus on useability
- Update the sphinx documentation when necessary
- Use numpy style docstrings
- Avoid code duplication and prefer creating code snippets in the utils module
