.PHONY: install upgrade nltk install-kernel-syftr remove-kernel-syftr mypy pre-commit-run unit-tests functional-tests e2e-tests tests aws-login submit- ray-submit- ray-stop-job ray-experiment- ray-cancel-jobs check tunnel 

export AWS_PROFILE=rd
OUTFILE := syftr.txt

install:
	@uv pip install -e ".[dev]"
	@pre-commit install || true
	@uv lock

upgrade:
	@uv pip install --upgrade -e ".[dev]"
	@pre-commit install || true
	@uv lock

nltk:
	python -m syftr.startup

install-kernel-syftr:
	@python -m ipykernel install --user --name=syftr

remove-kernel-syftr:
	@jupyter kernelspec remove -y syftr || true

mypy:
	@uv run --frozen mypy . --incremental

pre-commit-run:
	@pre-commit run --all-files

unit-tests:
	@uv run pytest -svv tests/unit/
functional-tests:
	@uv run pytest -svv tests/functional/

e2e-tests:
	@uv run pytest -svv tests/e2e/

tests: unit-tests functional-tests e2e-tests

# Use like `make submit-hotpot-toy`, which submits the study defined in studies/hotpot-toy.yaml
submit-%: studies/%.yaml
	@python -m syftr.ray.submit --study-config $< 2>&1 | tee $(OUTFILE)

aws-login:
	@test -n "$(shell find ~/.aws/sso/cache/ -type f -mmin -480)" || yawsso login --profile rd
	@python -m syftr.amazon

# Use like `make ray-submit-hotpot`, which submits study defined in studies/hotpot.yaml
ray-submit-%: studies/%.yaml
	@PYTHONUNBUFFERED=1 python -m syftr.ray.submit --remote --study-config $<

ray-stop-job:
	@python -m syftr.ray.stop --remote --id="$(id)"

ray-experiment-%:
	@PYTHONUNBUFFERED=1 python -m syftr.scripts.experiments.$* --remote

ray-cancel-jobs:
	@PYTHONUNBUFFERED=1 python -m syftr.scripts.cancel_jobs --substring="$(substring)"

tunnel:
	ssh -NT \
		-o ServerAliveInterval=60 \
		-o ServerAliveCountMax=10 \
		-o TCPKeepAlive=yes \
		-o ExitOnForwardFailure=true \
		-L 127.0.0.1:10001:localhost:10001 \
		-L 127.0.0.1:3000:localhost:3000 \
		-L 127.0.0.1:5432:localhost:5432 \
		-L 127.0.0.1:8265:localhost:8265 \
		-L 127.0.0.1:16686:localhost:16686 \
		jump

check:
	@python -m syftr.scripts.system_check
