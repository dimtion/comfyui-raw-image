
RUFF=uvx --isolated ruff
GITLINT=uvx --isolated --from gitlint-core gitlint

check:
	@${RUFF} check
	@${RUFF} format --check

fmt:
	@${RUFF} format

check-git:
	@${GITLINT}
