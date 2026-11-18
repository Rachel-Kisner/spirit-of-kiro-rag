# Spirit of Kiro — Repository Guide

## Project Overview

The root `README.md` describes Spirit of Kiro as an AI-powered, infinite-crafting workshop game/demo. It presents a game loop in which players find generated items, combine or transform them, and sell items to an appraiser. Those are the project's stated goals; this checkout does not contain the game implementation needed to verify that behavior.

The files present in this checkout show a Vue/Vite client project, a Bun-based root launcher intended to start a client and a server, Docker Compose configuration for a local DynamoDB-backed environment, and AWS CloudFormation assets for hosting the client. The referenced `server/`, `docs/`, and `client/src/` directories are absent. Consequently, the server architecture, client screens, data model, WebSocket protocol, and actual game behavior cannot be confirmed from the available source files.

## Main Features and Functionality

Features described by `README.md` (not independently verifiable in this source snapshot):

- Generate unique items with descriptions, damage, and quirks.
- Use a workbench to transform items, break them into components, and combine components into more complex items.
- Sell items through an appraiser.

Capabilities evident in the checked-in infrastructure and manifests:

- A Vue 3 client project configured for Vite, Vue Router, and Pinia.
- A root `dev` script intended to launch client and server processes together.
- A Docker Compose configuration describing local DynamoDB, an ECS local credentials endpoint, a WebSocket server, and the client.
- AWS CloudFormation resources for static S3 website hosting behind CloudFront, a WebSocket origin path, and a Lambda@Edge basic-auth handler.

The last two development/deployment flows reference files and directories not present in this checkout, so they are not currently runnable as configured.

## Technology Stack

Verified from the manifests and configuration:

- **Runtime/package tooling:** Bun (root package declares Bun; the client Dockerfile uses `oven/bun:1.2.15`).
- **Client:** Vue 3, Vue Router 4, Pinia, TypeScript, Vite, and Vue JSX support.
- **Client testing/lint/format:** Vitest with jsdom and Vue Test Utils, ESLint with Vue/TypeScript/Vitest configurations, and Prettier.
- **Root dependencies:** AWS SDK DynamoDB client, `uuid`, `yaml`, Bun, and ESLint.
- **Local infrastructure:** Docker Compose and Amazon DynamoDB Local; an Amazon ECS local container endpoints image is configured for credentials.
- **AWS hosting configuration:** CloudFormation, S3, CloudFront, Lambda@Edge (Node.js 20), and AWS CLI commands in the deployment script.

No backend source or backend-specific package manifest is present, so its implementation language, framework, and dependency set cannot be established.

## System Architecture

The architecture suggested by present configuration is:

```text
Browser
  └─ Vue/Vite client (client/)
       └─ WebSocket endpoint (configured through VITE_WS_URL in Compose)
            └─ Backend server (server/ — not present in this checkout)
                 └─ DynamoDB (DynamoDB Local in the Compose configuration)
```

In the configured local container environment, Compose also starts `amazon/amazon-ecs-local-container-endpoints` and mounts the user's AWS configuration directory for credential vending. The server container is assigned the local endpoint address and a DynamoDB endpoint through environment variables.

The production-oriented client deployment described in `client/iac/web.yaml` uploads built static files to a private S3 bucket served by CloudFront. A `/ws*` cache behavior forwards WebSocket-related headers to a configured HTTPS custom origin. The default website behavior associates a Lambda@Edge function that challenges requests with HTTP Basic authentication.

These are configuration-level descriptions, not confirmation of a complete running system: the server directory, client source, local environment file, and several Compose build inputs are missing here.

## Main Components and Their Responsibilities

- **Root `package.json`:** Provides the `dev` command (`bun launch.ts`) and declares root dependencies.
- **`launch.ts`:** Starts `server/server.ts` with Bun watch mode and starts the client's `dev` script, prefixes child output, and attempts to stop both processes if interrupted or one exits unsuccessfully. Its server target is absent from this checkout.
- **`client/`:** Contains the client package manifest, Vite/Vue/TypeScript configuration, HTML entry document, Dockerfile, and deployment assets. `client/index.html` points to `src/main.ts`, but that source file and the rest of `client/src/` are absent.
- **`docker-compose.yml`:** Describes local DynamoDB, ECS local credential endpoints, a backend service, and a client service. The backend build context and `dev.env` are not present in the checkout.
- **`client/iac/web.yaml`:** Defines CloudFormation resources for the static website, logging buckets, CloudFront distribution, WebSocket origin, and Lambda@Edge basic authentication.
- **`client/iac/deploy.sh`:** Builds the client, deploys the CloudFormation stack, syncs build output to S3, and requests CloudFront cache invalidation. It requires AWS CLI credentials/permissions and a WebSocket endpoint; its defaults include a domain name and certificate ARN that may not be usable in another AWS account.

No application component implementations, API handlers, store definitions, or game-specific source modules are available to describe more precisely.

## Installation and Setup

### Requirements indicated by checked-in configuration

- Bun is required by the root and client scripts. The client container currently specifies Bun 1.2.15.
- Docker and Docker Compose are needed for the configured local infrastructure.
- AWS credentials/configuration are referenced by the ECS local endpoint service.
- AWS CLI credentials and access to the relevant AWS resources are needed for the deployment script.

### Installing dependencies

From the repository root:

```sh
bun install
```

For client dependencies:

```sh
cd client
bun install
```

### Important checkout limitations

The expected `server/` and `client/src/` source directories are absent. The root launch command therefore cannot start its configured server, and the client HTML references a missing `client/src/main.ts`. The Compose server build also expects `server/Dockerfile`, and Compose references a `dev.env` file that is not present (it is excluded by `.gitignore`). As a result, a working full local setup cannot be completed from the files in this checkout alone.

The Compose file also mounts `$HOME/.aws/` for the local ECS credential service. Review the Compose configuration and configure a suitable local AWS profile before running it; do not assume the default profile or credentials are available.

## Development and Execution

Commands declared by the manifests:

```sh
# Root: intended to start both server and client
bun run dev

# Client only
cd client
bun run dev

# Client build and type check
bun run build
bun run type-check

# Client unit tests
bun run test:unit

# Client lint and formatting
bun run lint
bun run format
```

`bun run lint` applies ESLint fixes (`eslint . --fix`), and `bun run format` writes formatting changes under `src/`; use these commands with care if you want to avoid modifying files. The client test script starts Vitest; the Vitest configuration uses jsdom and excludes `e2e/`.

The root command is declared in `package.json`, while the client commands are declared in `client/package.json`. Due to the missing application and server source, these commands describe intended workflows but cannot be assumed to complete successfully in this checkout. The client Dockerfile exposes port 5173 and starts Vite bound to `0.0.0.0`. Compose maps client port 5173 and server port 8080, DynamoDB Local port 8000, and sets `VITE_WS_URL` to `http://localhost:8080/`.

## Coding Conventions and Development Guidelines

Conventions explicitly encoded in the client configuration:

- Use TypeScript and Vue single-file components; Vue JSX is also enabled.
- Use two spaces, LF line endings, UTF-8, a final newline, no semicolons, single quotes, and a Prettier print width of 100.
- Use the `@/` alias for paths under `client/src/`.
- ESLint covers TypeScript, TSX, and Vue files, applies the Vue essential and recommended TypeScript configurations, and enables the Vitest recommended rules for `src/**/__tests__/*`.
- Unit tests are configured with Vitest and jsdom; the client manifest also includes Vue Test Utils.

Contribution guidance in `CONTRIBUTING.md` asks contributors to work against the latest `main`, check for existing issues/PRs, discuss significant work in an issue, keep pull requests focused, run local tests, and use clear commit messages. No additional backend coding conventions or test commands can be verified because the backend source and its configuration are absent.

## Repository Evidence and Unknowns

This guide is based on the files present in this checkout, including the root README, manifests, launcher, Compose file, contribution/code-of-conduct documents, client manifests/configuration, Dockerfile, HTML entry, and AWS deployment assets. The README links to `docs/` pages, but that directory is absent. The `.kiro/steering/` directory exists, but its contents were not used as the basis for this independently prepared guide.

The following cannot be confirmed from the available repository files:

- Actual UI routes, components, screens, and client-side state shape.
- Backend implementation, persistence schema, and WebSocket message/event formats.
- Whether README-described game functionality is implemented in the missing source.
- A complete set of setup steps or a verified working development/deployment workflow.
- Any CI workflow, since no workflow files are present in the inspected repository structure.
