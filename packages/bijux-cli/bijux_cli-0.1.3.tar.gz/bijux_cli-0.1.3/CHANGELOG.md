# Changelog
<a id="top"></a>

All notable changes to **Bijux CLI** are documented here.
This project adheres to [Semantic Versioning](https://semver.org) and the
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

<a id="unreleased"></a>
## [Unreleased]

### Added
* (add new entries via Towncrier fragments in `changelog.d/`)

### Changed
* (add here)

### Fixed
* (add here)

[Back to top](#top)

---

<!-- towncrier start -->

<a id="v0-1-3"></a>

## [0.1.3] – 2025-08-20

### Added
* **ADR-0005:** Zero-root-pollution via **Makefile-orchestrated artifact containment** (all generated outputs under `artifacts/`).  
* **Curated release assets:** zipped bundles for **tests (py311/py312/py313)** and for **lint, quality, security, api, docs, sbom, citation, build**, plus consolidated **checksums**.
* **End-to-end automation:** GitHub Actions to **publish to PyPI**, **create a GitHub Release** with curated bundles, and **deploy docs**.

### Changed
* **Makefiles + workflows** brought into **full ADR-0005 compliance**: CI uploads/downloads only `artifacts/**`; docs deploy hydrates from CI artifacts and builds from `artifacts/docs/**`.

[Back to top](#top)

---

<a id="v0-1-2"></a>

## [0.1.2] – 2025-08-17

### Added
* **New Documentation Engine:** Introduced a new modular documentation builder in `scripts/docs_builder/` that replaces the previous helper script.
* **CI Artifact Pages:** The documentation site now automatically generates detailed pages for all CI artifacts, including tests, linting, code quality, security, API tests, SBOMs, and citation files.
* **Release Evidence:** The `publish` workflow now downloads all artifacts from the `CI` run, packages them as `evidence/*.tar.gz` bundles, and attaches them to the GitHub Release for traceability.
* **Build Hygiene:** Makefiles now enforce a "hygienic" build process, ensuring all temporary files, caches, and build outputs are stored under the `artifacts/` directory to prevent root directory pollution.

### Changed
* **CI/CD Overhaul:**
    * The `ci.yml` workflow now uploads each category of artifact separately for better organization and downstream consumption.
    * The `docs.yml` workflow now waits for the main `CI` run to complete, downloads all artifacts, and uses them to build a data-rich documentation site.
    * The `publish.yml` workflow has been streamlined and made more robust, removing the optional "wait for docs" step and improving tag detection.
* **Documentation Content:** All top-level Markdown documents (`README.md`, `USAGE.md`, `TESTS.md`, `TOOLING.md`, `CONTRIBUTING.md`, etc.) have been significantly rewritten and expanded with tables of contents, `back-to-top` links, and cross-references to the new artifact pages.
* **Build System:**
    * All `Makefile` modules have been refactored to use the new hygienic `artifacts/` directory structure for outputs and caches.
    * `tox.ini` has been updated to align with the new Makefile targets and to run a comprehensive suite of checks for the `py311` environment, mirroring the full CI validation process.
* **API Schema:** The OpenAPI `schema.yaml` has been improved with stricter validation (`additionalProperties: false`), better descriptions, response links, and more detailed examples.
* **Source Code:** Refactored async handling in `src/bijux_cli/api.py` and improved type safety across multiple modules by removing `pyright: ignore` comments and adding explicit `cast` calls where necessary.

### Fixed
* **Type Safety:** Resolved numerous previously ignored type errors throughout the codebase and test suite.
* **API Endpoint Logic:** Corrected the item update logic in `src/bijux_cli/httpapi.py` by removing a faulty check for duplicate names that was causing incorrect 409 Conflict errors.
* **Test Suite:** Improved the stability and correctness of E2E tests by enhancing golden file comparisons and fixing brittle assertions.

[Back to top](#top)

---

<a id="v0-1-1"></a>

## [0.1.1] – 2025-08-14

### Added
* **Publish pipeline:** GitHub Actions `publish.yml` that publishes via `make publish` only after required checks are green and a tag is present.
* **Project map:** `PROJECT_TREE.md` (and `docs/project_tree.md`) with a curated overview.
* **Developer Tooling page:** `TOOLING.md` (and `docs/tooling.md`) with embedded configs, Makefile snippets, and CI workflows via `include-markdown`.
* **Docs assets:** Community landing page, Plausible analytics partial, and CSS overrides.

### Changed
* **Docs generator (`scripts/helper_mkdocs.py`):**
  * Copies **README**, **USAGE**, **TESTS**, **PROJECT_TREE**, and **TOOLING** into the site with link rewrites and `{#top}` anchors.
  * Generates mkdocstrings pages for all modules under `src/bijux_cli/**`.
  * Builds **one** consolidated **API Reference** with this structure:
    * top: **Api Module**, **Cli Module**, **Httpapi Module**
    * sections (collapsed by default): **Commands**, **Contracts**, **Core**, **Infra**, **Services**
    * nested groups for command subpackages (`config/`, `dev/`, `history/`, `memory/`, `plugins/`) beneath **Commands**.
  * Emits `reference/**/index.md` to power Material’s section indexes.
* **MkDocs config (`mkdocs.yml`):** tightened plugin ordering and settings for `include-markdown`, enabled section indexes, and strict mode; added watch paths for configs and scripts.
* **README / USAGE:** Refined copy; standardized **top anchors** and links to **TESTS.md**/**PROJECT_TREE.md**/**TOOLING.md**.
* **SECURITY.md:** Rewritten with clearer reporting, SLAs, scope, and safe harbor.
* **Makefiles:** macOS-safe env handling; Cairo-less Interrogate wrapper for doc coverage.
* **Config:** Expanded lints/dictionary.

### Fixed
* **Docs build (strict):** resolved broken/unknown links in **TOOLING.md** and removed duplicate **API Reference** sections; left sidebar now stays populated when deep-linking into API pages.
* **Tests:** E2E version fixtures cleaned up.

### Packaging
* **PyPI links corrected:** `project.urls` now points to accurate Homepage/Docs/Changelog/Issues/Discussions.
* **Dynamic versioning from Git tags:** Using `hatch-vcs` with `dynamic = ["version"]`; annotated tags like `v0.1.1` define the release version. `commitizen` tags as `v$version`.
* **Richer PyPI description:** `hatch-fancy-pypi-readme` renders **README.md** + **CHANGELOG.md** on PyPI.
* **Wheel/Sdist layout:** Explicit Hatch build config ensures `py.typed`, licenses, and metadata are included.

[Back to top](#top)

---

<a id="v0-1-0"></a>

## [0.1.0] – 2025-08-12

### Added

* **Core runtime**

    * Implemented Dependency Injection kernel, REPL shell, plugin loader, telemetry hooks, and shell completion (bash/zsh/fish).
    * Added core modules: `api`, `cli`, `httpapi`, `core/{constants,context,di,engine,enums,exceptions,paths}`.

* **Contracts layer** (`contracts/`)

    * Defined protocols for `audit`, `config`, `context`, `docs`, `doctor`, `emitter`, `history`,
      `memory`, `observability`, `process`, `registry`, `retry`, `serializer`, `telemetry`.
    * Added `py.typed` markers for downstream type checking.

* **Services layer**

    * Implemented concrete services for `audit`, `config`, `docs`, `doctor`, `history`, `memory`.
    * Built plugin subsystem: `plugins/{entrypoints,groups,hooks,registry}`.

* **Infra layer** (`infra/`)

    * Implemented `emitter`, `observability`, `process`, `retry`, `serializer`, `telemetry`.

* **Command suite**

    * Added top-level commands: `audit`, `docs`, `doctor`, `help`, `repl`, `sleep`, `status`, `version`.
    * Added `config/` commands: `clear`, `export`, `get`, `list`, `load`, `reload`, `set`, `unset`, `service`.
    * Added `dev/` commands: `di`, `list-plugins`, `service`.
    * Added `history/` commands: `clear`, `service`.
    * Added `memory/` commands: `clear`, `delete`, `get`, `list`, `set`, `service`.
    * Added `plugins/` commands: `check`, `info`, `install`, `list`, `scaffold`, `uninstall`.

* **Structured output & flags**

    * Added JSON/YAML output via `--format`, pretty printing, and deterministic global flag precedence ([ADR-0002](https://bijux.github.io/bijux-cli/ADR/0002-global-flags-precedence)).

* **API contract validation & testing**

    * Automated lint/validation of `api/*.yaml` with Prance, OpenAPI Spec Validator, Redocly, and OpenAPI Generator.
    * Added **Schemathesis** contract testing against the running server.
    * Pinned OpenAPI Generator CLI version via `OPENAPI_GENERATOR_VERSION` and automated Node.js toolchain setup in Makefile.

* **Documentation tooling**

    * Integrated MkDocs (Material), mkdocstrings, literate-nav, and ADR index generation.

* **Quality & security pipeline**

    * Added formatting/linting: `ruff` (+format).
    * Added typing: `mypy`, `pyright`, `pytype`.
    * Added docs style/coverage: `pydocstyle`, `interrogate`.
    * Added code health: `vulture`, `deptry`, `radon`, `codespell`, `reuse`.
    * Added security: `bandit`, `pip-audit`.
    * Added mutation testing: `mutmut`, `cosmic-ray`.

* **SBOM**

    * Generated CycloneDX JSON for prod/dev dependencies via `make sbom` (uses `pip-audit`).

* **Citation**

    * Validated `CITATION.cff` and added export to BibTeX/RIS/EndNote formats via `make citation`.

* **Makefile architecture**

    * Modularized the Makefile into `makefiles/*.mk` for maintainability and clear separation of concerns.
    * Centralized all developer workflows (`test`, `lint`, `quality`, `security`, `api`, `docs`, `build`, `sbom`, `citation`, `changelog`, `publish`) in one consistent interface.
    * Added `bootstrap` target for idempotent virtualenv setup and Git hook installation from `scripts/git-hooks` (skips re-installation if already linked).
    * Added `all-parallel` target to run independent checks (`quality`, `security`, `api`, `docs`) concurrently for faster CI/CD.
    * Added `make help` for self-documenting targets with grouped sections.
    * Provided helper macros (`run_tool`, `read_pyproject_version`) to standardize tooling invocation.

* **pre-commit**

    * Added hygiene hooks: `ruff-format` + `ruff`, `mdformat`, and `codespell`.
      * Enforced Conventional Commits via **commitizen** `commit-msg` hook.

* **tox orchestration**

    * Configured multi-Python test envs (`py311`, `py312`, `py313`).
    * Mapped Makefile workflows into tox envs (`lint`, `quality`, `security`, `api`, `docs`, `build`, `sbom`, `changelog`, `citation`) to ensure reproducibility.
    * Passed `MAKEFLAGS` to execute Makefile targets inside tox-managed virtualenvs.

* **Continuous Integration**

    * Added **GitHub Actions** workflow running tox across Python versions with Node.js 20 and Java 17 for API checks.
    * Added **GitLab CI** sample mirroring the GitHub workflow (tox-driven) with artifacts for coverage and API logs.
    * CI/CD pipelines directly leverage the modularized Makefile for consistent local/CI behavior.

* **Packaging / PyPI page**

    * Built dynamic long description via **hatch-fancy-pypi-readme** from **README.md** and **CHANGELOG.md** for PyPI/TestPyPI.
    * Packaged with `LICENSES/`, `REUSE.toml`, `CITATION.cff`, and `py.typed` included in source distributions.

### Changed

* Released initial public version.

### Fixed

* None

[Back to top](#top)

[Unreleased]: https://github.com/bijux/bijux-cli/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/bijux/bijux-cli/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/bijux/bijux-cli/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/bijux/bijux-cli/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/bijux/bijux-cli/releases/tag/v0.1.0

