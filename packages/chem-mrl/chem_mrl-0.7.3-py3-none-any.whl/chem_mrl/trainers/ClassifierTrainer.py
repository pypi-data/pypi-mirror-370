import logging

from sentence_transformers import SentenceTransformer
from sentence_transformers.evaluation import SentenceEvaluator

from chem_mrl.evaluation import LabelAccuracyEvaluator
from chem_mrl.schemas import BaseConfig, ClassifierConfig

from .BaseTrainer import _BaseTrainer

logger = logging.getLogger(__name__)


class ClassifierTrainer(_BaseTrainer):
    def __init__(self, config: BaseConfig):
        super().__init__(config=config, init_data_kwargs={"is_classifier": True})

        self._model_config: ClassifierConfig = config.model
        if not isinstance(self._model_config, ClassifierConfig):
            raise TypeError("config.model must be a ClassifierConfig instance")

        self.__model: SentenceTransformer = self._init_model()
        self.__loss_function = self._init_loss()
        self.__val_evaluator = self._init_val_evaluator()
        self.__test_evaluator = self._init_test_evaluator()

    ############################################################################
    # concrete properties
    ############################################################################

    @property
    def config(self):
        return self._config

    @property
    def model(self):
        return self.__model

    @property
    def loss_function(self):
        return self.__loss_function

    @property
    def val_evaluator(self) -> dict[str, SentenceEvaluator]:
        return self.__val_evaluator

    @property
    def test_evaluator(self) -> dict[str, SentenceEvaluator]:
        return self.__test_evaluator

    @property
    def eval_metric(self) -> str:
        return self._model_config.eval_metric.value

    ############################################################################
    # concrete methods
    ############################################################################

    def _init_model(self):
        model = SentenceTransformer(
            self._model_config.model_name,
            truncate_dim=self._model_config.classifier_hidden_dimension,
        )
        logger.info(model)
        return model

    def _init_val_evaluator(self):
        """
        Initialize validation evaluators for all datasets.

        Returns:
            Dictionary mapping dataset names to evaluators
        """
        evaluators: dict[str, SentenceEvaluator] = {}
        for dataset_name, eval_ds in self.eval_dataset.items():
            evaluators[dataset_name] = LabelAccuracyEvaluator(
                dataset=eval_ds,
                softmax_model=self.__loss_function,
                write_csv=True,
                name=dataset_name,
                batch_size=self._config.training_args.per_device_eval_batch_size,
                smiles_column_name="smiles_a",
                label_column_name="label",
            )

        logger.info(f"Initialized {len(evaluators)} validation evaluators")
        return evaluators

    def _init_test_evaluator(self):
        """
        Initialize test evaluators for all datasets.

        Returns:
            Dictionary mapping dataset names to test evaluators, or empty dict if no test datasets
        """
        evaluators: dict[str, SentenceEvaluator] = {}
        for dataset_name, test_ds in self.test_dataset.items():
            evaluators[dataset_name] = LabelAccuracyEvaluator(
                dataset=test_ds,
                softmax_model=self.__loss_function,
                write_csv=True,
                name=dataset_name,
                batch_size=self._config.training_args.per_device_eval_batch_size,
                smiles_column_name="smiles_a",
                label_column_name="label",
            )

        logger.info(f"Initialized {len(evaluators)} test evaluators")
        return evaluators

    def _init_loss(self):
        from chem_mrl.losses import SelfAdjDiceLoss, SoftmaxLoss

        if self._model_config.loss_func == "softmax":
            return SoftmaxLoss(
                model=self.__model,
                smiles_embedding_dimension=self._model_config.classifier_hidden_dimension,
                num_labels=self.config.model.num_labels,
                dropout=self._model_config.dropout_p,
                freeze_model=self._model_config.freeze_model,
            )

        return SelfAdjDiceLoss(
            model=self.__model,
            smiles_embedding_dimension=self._model_config.classifier_hidden_dimension,
            num_labels=self.config.model.num_labels,
            dropout=self._model_config.dropout_p,
            freeze_model=self._model_config.freeze_model,
            reduction=self._model_config.dice_reduction,
            gamma=self._model_config.dice_gamma,
        )
