# Approve every planning and coding step

## Steps

- Start with initial Basic prompt
- Use https://promptperfect.jina.ai to improve initial prompt
- Start running improved prompt in Roo Code Architect agent with Gemini 2.5 Pro
- Approve every step
- Continue runnging Roo Code Code agent with Gemini 2.5 Pro

## Result

- Almost all functionality has been implemeted with (Tokens: Out:11.9M and Input:111.2k)
  - 2 error running the project (both has been fixed by coder agent)
  - MCP server hasn't been implemented
  - Average code quality
  - Informative readme.md 
  - `click` library used to implement cli entrypoints
  - all methods has explanation comments
  - tests have been generated
- Running `arch-assist`
  - with `--version`
    - version 0.1.0
  - with `--help`
    - displayed usage help page
  - with `analyze`
    - just return the project structure with  
  - with `map-deps` --format mermaid / plantunml
    - creates the diagram listing the folder structure returned by `analyze` implementation 
  - with `find-use-cases`
    - returned list of files in the repo with short sentense generated based on regex analysis
- Tests
  - 16 failed, 76 passed, 1 warning in 6.01s