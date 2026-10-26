# Docker Engineering Memory Deck — Official Sources

The import JSON intentionally preserves the simple `{topic, concepts: [{title, content, image_prompt}]}` schema. The following official documentation was consulted when preparing the deck.

## Dockerfiles, builds, images, and supply chain
- Building best practices: https://docs.docker.com/build/building/best-practices/
- Optimize cache usage in builds: https://docs.docker.com/build/cache/optimize/
- Build secrets: https://docs.docker.com/build/building/secrets/
- Multi-stage builds: https://docs.docker.com/get-started/docker-concepts/building-images/multi-stage-builds/
- Build attestations (SBOM and provenance): https://docs.docker.com/build/metadata/attestations/
- Build security check for secrets in ARG/ENV: https://docs.docker.com/reference/build-checks/secrets-used-in-arg-or-env/

## Compose, networking, runtime, and resources
- Compose networking and service discovery: https://docs.docker.com/compose/how-tos/networking/
- Compose startup order and healthchecks: https://docs.docker.com/compose/how-tos/startup-order/
- Compose service reference: https://docs.docker.com/reference/compose-file/services/
- Bridge networking: https://docs.docker.com/engine/network/drivers/bridge/
- Port publishing and mapping: https://docs.docker.com/engine/network/port-publishing/
- Resource constraints: https://docs.docker.com/engine/containers/resource_constraints/
- Restart policies: https://docs.docker.com/engine/containers/start-containers-automatically/

## Storage, logging, security, and operations
- Storage and mounts: https://docs.docker.com/engine/storage/
- Configure logging drivers and rotation: https://docs.docker.com/engine/logging/configure/
- Docker Engine security: https://docs.docker.com/engine/security/
- Rootless mode: https://docs.docker.com/engine/security/rootless/
- Docker system disk usage: https://docs.docker.com/reference/cli/docker/system/df/
- Docker system prune: https://docs.docker.com/reference/cli/docker/system/prune/

## Notes on applicability
- Compose behavior depends on the Compose plugin and deployment mode; validate options against the version used by your environment.
- The `shm_size` card describes container `/dev/shm`; it is distinct from PostgreSQL's own memory settings and from host disk capacity.
- Database mount paths are image-version-specific. The deck explicitly advises checking the official image guidance, particularly when changing PostgreSQL major versions.
