# Repository Guidelines

## Project Structure & Module Organization
This repository is a lightweight product prototype rather than a packaged application. The main UI lives in `html/index.html`. A larger standalone prototype snapshot is stored in `beepop-prototype.html`. Supporting product context lives in `bbox-interaction-spec.txt`, `beepop-bbox-product-logic.txt`, and `beepop-user-copy.csv`.

Keep UI changes in `html/` when possible. Treat the root-level `.txt` and `.csv` files as reference inputs for copy, interaction behavior, and product rules.

## Build, Test, and Development Commands
There is no formal build pipeline in this repo. Use a simple static server for local review:

- `python3 -m http.server 8000` from the repository root: serves the project locally.
- Open `http://localhost:8000/html/`: previews the main prototype.
- `git diff -- html/index.html`: reviews UI edits before committing.

If you change the standalone prototype, verify both `html/index.html` and `beepop-prototype.html` still reflect the intended behavior.

## Coding Style & Naming Conventions
Use 2-space indentation in HTML, CSS, and inline JavaScript to match the existing files. Preserve the current single-file prototype style unless a refactor is explicitly requested. Prefer descriptive kebab-case class names such as `.canvas-hint` and `.bbox-card-label`.

Keep comments brief and only where behavior is not obvious. Avoid introducing tooling-specific formatting unless the repo adopts it consistently.

## Testing Guidelines
This project currently relies on manual validation. After any UI change, test in a browser at desktop width and a narrower mobile-sized viewport. Verify interaction flows, text rendering, overflow behavior, and any state transitions tied to the bbox workflow.

When adding new behavior, document a short manual test checklist in the PR or commit notes. No coverage threshold is defined because there is no automated test suite yet.

## Commit & Pull Request Guidelines
Recent history uses very short commit subjects such as `html`, `index`, and `skill`. Keep the message imperative, but make it more descriptive, for example: `Refine bbox card selection states`.

Pull requests should include a concise summary, the files changed, manual test notes, and screenshots or screen recordings for visible UI changes. Link any related product spec or issue so reviewers can compare the implementation against the source requirements.
