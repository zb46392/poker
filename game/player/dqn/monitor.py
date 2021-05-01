import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from typing import Dict


class Monitor:
    def __init__(self, model: nn.Module, monitor_comment_params: Dict[str, str]) -> None:
        self._model = model
        self._comment_params = monitor_comment_params
        self._progress = 0
        self._step = 0
        self._summary_writer = None
        self._device = next(model.parameters()).device

        self._init_summary_writer()

    def _init_summary_writer(self) -> None:
        comment = self._generate_comment()
        dummy_data = [0 for _ in range(self._model[0].in_features)]
        input_to_model = torch.as_tensor(dummy_data, dtype=torch.float32).to(self._device)

        self._summary_writer = SummaryWriter(comment=f' - {comment}')
        self._summary_writer.add_graph(self._model, input_to_model)

    def _generate_comment(self) -> str:
        comment = ''
        params_amount = len(self._comment_params)

        for i, k in enumerate(self._comment_params.keys()):
            comment += f'{k}={self._comment_params.get(k)}'
            if i < params_amount - 1:
                comment += ', '

        return comment

    def monitor(self) -> None:
        progress = self._progress
        self._summary_writer.add_scalar('Progress', progress, self._step)

        for name, param in self._model.named_parameters():
            self._summary_writer.add_histogram(name, param, self._step)
            self._summary_writer.add_histogram(f'{name}_grad', param.grad, self._step)

        self._step += 1

    def update_progress(self, new_progress: int) -> None:
        self._progress = new_progress

    def close(self) -> None:
        self._summary_writer.close()