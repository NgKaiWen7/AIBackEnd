---
name: technical-memory-card-author
description: Author complete sets of technical memory-card concepts (compact JSON with topic, concepts, and per-card title, content, image_prompt) for Linux server administration, DevOps, cloud, Kubernetes, infrastructure as code, observability, security, and AI DevOps (MLOps, LLMOps, GPU infrastructure, LLM serving). Use this skill whenever the user asks to generate study cards, flashcards, memory cards, topic card sets, "everything I need to know" about a technical domain, cheat-sheet cards, or card image prompts, even if they never say "JSON" or "skill". Also use it when the user wants a detailed, broad topic breakdown that will later be rendered as card images. This skill writes the concepts and illustration briefs; it does not render images (hand those to gemini-card-image-generator or another image tool).
---

# Technical Memory-Card Author

Produce dense, accurate, illustratable card sets for technical domains. Each card teaches one concept and carries a short illustration brief that an image model can render as a finished card.

## Boundary

- This skill owns: topic coverage, concept order, card content, and each card's `image_prompt`.
- Rendering images belongs to `gemini-card-image-generator` or another image-generation tool. Do not claim images were produced unless a real image tool ran and files exist.
- If the user asks for images and no image-generation capability exists in the session, say so plainly, deliver the JSON, and offer to hand it off. Check by looking at the tool list and, if useful, testing network access; do not guess.

## Output format

Write compact JSON, one file per domain, saved to the outputs folder and presented to the user:

```json
{
  "topic": "Linux Server Administration",
  "concepts": [
    {"title": "...", "content": "...", "image_prompt": "..."}
  ]
}
```

Rules for the file:
- Exactly the three keys per concept; no ids, no extra fields. Array order is teaching order.
- One concept per line keeps diffs and review manageable.
- Valid JSON: no double quotes inside strings (use single quotes for shell quoting, e.g. awk '{print $1}'), no backslashes, no trailing commas.
- Name files after the domain: `linux-server-administration.json`, `devops-engineering.json`, `ai-devops-mlops-llmops.json`.
- Split a broad request into several domain files of about 35-50 cards each rather than one huge file.

## Writing a card

**title** (under 70 characters): the concept name, optionally with its key tools after a colon. Examples: "Disk Space and Inodes", "Model Serving Frameworks", "Interconnects: NCCL, NVLink, InfiniBand".

**content** (target 30-60 words, hard ceiling about 70): one idea, packed with facts a practitioner would actually use.
- Open with what the thing is or why it matters, then the mechanics, then one operational tip or trap.
- Include real commands, flags, paths, file names and defaults inline, exactly as typed: `chmod 750`, `/etc/fstab`, `lvextend -r -L +10G /dev/vg0/data`, `kubectl logs --previous`.
- Prefer one worked example over three abstract statements.
- Name the common failure mode (lockout from a firewall rule, bad fstab entry, training-serving skew, pickle model files).
- State trade-offs honestly (XFS cannot shrink, RAID is not backup, service meshes add overhead).
- No filler such as "it is important to note". No marketing language.

**image_prompt** (target 15-35 words): a brief for one diagram.
- Name the diagram type (layered stack, pipeline, tree, state diagram, timeline, comparison matrix, grid, loop, gauge panel).
- List the exact labels, nodes and arrows that must appear, and the direction of flow.
- Encode the relationship the card teaches (control plane versus workers, offline versus online store, prefill versus decode), not decoration.
- Do not describe color, font or layout style; the renderer applies one shared style across the series.
- Do not ask for logos or brand marks; say "plain labeled boxes" for tool comparisons.
- Never ask for extra text beyond the card's own content and short diagram labels.

## Accuracy rules

Cards are study material, so mistakes are costly.
1. Verify arithmetic before writing it. Examples used before: 99.9% over 30 days is about 43 minutes of downtime; a 7B model is about 14 GB in FP16, 7 GB in INT8, 3.5 GB in INT4 for weights only.
2. Only include commands and flags you are certain of. If unsure, describe the concept without the flag.
3. Be careful with fast-moving projects. Tools get deprecated, renamed or put into maintenance mode (for example some model servers). If you cannot confirm a project is current, search the web, or leave it out and name healthier alternatives.
4. Scope claims: say "weights only", "on supported NVIDIA datacenter GPUs", "RHEL default", "by default" where the statement is conditional.
5. Do not invent statistics, benchmark numbers, version numbers or dates. Regulations and frameworks (EU AI Act, NIST AI RMF, OWASP lists) should be named, not summarized in detail, unless verified.
6. Prefer vendor-neutral terms; mention a specific tool as an example, not as the only option.
7. When recency matters (current versions, deprecations, regulations), run a web search first.

## Coverage maps

When asked for "everything" on a domain, use the matching map to decide cards, then add domain-specific extras. Keep order foundational to advanced.

**Linux server administration**: architecture and syscalls; boot (UEFI, GRUB, initramfs, systemd); filesystem hierarchy; users and groups; permissions, special bits, ACLs; sudo; package managers; systemd units; journald, logrotate; processes and signals; cron and timers; disks, partitions, filesystems, fstab; LVM; mdadm RAID; disk and inode usage; memory, swap, OOM; CPU and load; I/O; USE method; ip/ss networking; DNS; nftables/ufw/firewalld; SSH keys and hardening; tunnels and rsync; TLS and certbot; nginx; HAProxy and keepalived; hardening checklist; SELinux/AppArmor; auditd; sysctl; backups (3-2-1, restic, borg); bash scripting; text processing; find/xargs/lsof; network troubleshooting; tmux; time sync; namespaces and cgroups; strace/perf/eBPF; NFS and remote storage; troubleshooting methodology; disaster recovery.

**DevOps**: culture and CALMS; DORA metrics; CI/CD; Git and branching; code review gates; test pyramid; GitHub Actions, GitLab CI, Jenkins; deployment strategies; feature flags; registries and SemVer; Docker (images, Dockerfiles, networking, Compose, security); Kubernetes (architecture, objects, config and secrets, ingress, storage, probes, autoscaling, kubectl debugging, Helm and Kustomize, RBAC and NetworkPolicy, service mesh); IaC (Terraform workflow and state, Ansible, Packer and immutability); GitOps; cloud fundamentals; FinOps; observability (three pillars, Prometheus, Grafana and alerting, logging, tracing); SLOs and error budgets; golden signals, RED, USE; incident management; DevSecOps; secrets; policy as code and supply chain; chaos engineering; twelve-factor and zero-downtime releases; platform engineering.

**AI DevOps**: MLOps lifecycle and maturity; data versioning and validation; feature stores and skew; experiment tracking; model registry; GPU drivers and CUDA; GPUs in containers and Kubernetes; GPU sharing (MIG, time-slicing, MPS); distributed training; NCCL, NVLink, InfiniBand; training orchestration (Slurm, Kubeflow, Ray, Kueue); reproducibility and ML CI; serving patterns and frameworks; LLM inference engines; KV cache, PagedAttention, continuous batching; quantization; GPU memory sizing; serving metrics (TTFT, tokens per second); inference autoscaling; rollout strategies; drift monitoring; GPU observability (DCGM); prompt versioning; RAG operations; LLM evaluation; LLM observability; gateways; caching; guardrails and OWASP LLM risks; agent operations and MCP; fine-tuning (LoRA, QLoRA); local AI server on Linux; AI FinOps; model supply-chain security; governance; ONNX and optimization; reference architecture.

For other domains (databases, networking, security, SRE, data engineering), build a comparable map first, show it to the user only if they ask, then write the cards.

## Workflow

1. Clarify scope only if the request is truly ambiguous. A request like "cover as much as possible" means: use the full coverage map, aim for 35-50 cards per domain file, and prioritize depth of practical detail over breadth of trivia.
2. If current facts matter, search before writing.
3. Draft the cards in teaching order, one domain file at a time.
4. Save each file to the outputs folder and validate:
   `python scripts/validate_cards.py path/to/file.json [more.json ...]`
   Fix every ERROR. Review warnings (word counts, logo mentions) and fix any that indicate a real problem.
5. Present the files. Report the card count per file and state whether images were generated. Keep the closing note short and offer the handoff to an image renderer.

## Quality checklist

- Each card teaches exactly one concept and stands alone.
- Content contains at least one concrete command, path, number or rule.
- The image_prompt shows the concept's structure and names every label that must appear.
- No duplicate titles; no overlapping cards that repeat the same facts.
- All commands, flags and arithmetic are verified; time-sensitive claims are searched or omitted.
- JSON validates with zero errors.
- Image status stated honestly.

## Handoff to rendering

When an image tool is available, pass the JSON to it unchanged and render one card per concept in array order. Do not rewrite content or prompts at that stage. Shared visual style (aspect ratio, palette, typography) is set once for the whole series by the renderer or the user, not inside each `image_prompt`.
