PYTHON ?= python

.PHONY: refresh_env extraction model clean_processed clean_model_input

refresh_env:
	@echo Refreshing environment.yaml
	@echo "name: deep-deter-env" > environment.yaml
	@conda env export --no-builds | grep -v "^prefix: " | grep -v "^name: " >> environment.yaml

extraction:
	@echo Running ./deep_deter/data_extraction/main.py
	python ./deep_deter/data_extraction/main.py

model:
	@echo Running ./deep_deter/deep_model/main.py
	python ./deep_deter/deep_model/train.py

clean_processed:
	@echo Cleaning processed directory
	rm -f ./data/processed/masked_feature_bands/*.tif
	rm -f ./data/processed/labels/*.tif

clean_model_input:
	@echo Cleaning model inputs
	rm -f ./data/model_inputs/train_features/*.tif
	rm -f ./data/model_inputs/train_labels/*.tif
	rm -f ./data/model_inputs/test_features/*.tif
	rm -f ./data/model_inputs/test_labels/*.tif
