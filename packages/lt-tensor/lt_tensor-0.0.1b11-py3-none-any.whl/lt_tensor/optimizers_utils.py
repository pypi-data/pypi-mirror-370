__all__ = ["OptimizerWrapper", "get_adamw_optimizer"]
import inspect
import torch
from torch import optim, Tensor, nn
from torch.optim import Optimizer
from typing import Dict, List, Optional, Any, Tuple, Union
from torch.amp.grad_scaler import GradScaler


class OptimizerWrapper:
    def __init__(
        self,
        optimizers: Dict[str, Optimizer] = {},
        schedulers: Dict[str, optim.lr_scheduler.LRScheduler] = {},
    ):
        self.optimizers = optimizers
        self.schedulers = schedulers
        self.keys = list(optimizers.keys())

    def state_dict(self):
        std = {
            "optimizers": [],
            "schedulers": [],
        }
        for k, v in self.optimizers.items():
            try:
                std["optimizers"].append({k: v.state_dict()})
            except:
                pass
        for k, v in self.schedulers.items():
            try:
                std["schedulers"].append({k: v.state_dict()})
            except:
                pass
        return std.copy()

    def load_state_dict(self, state_dict: Dict[str, List[Dict[str, Any]]]):
        optimizers = state_dict["optimizers"]
        schedulers = state_dict["schedulers"]
        if optimizers and self.optimizers:
            for otm in optimizers:
                try:
                    for k, v in otm.items():
                        if k in self.optimizers:
                            self.optimizers[k].load_state_dict(v)
                        else:
                            print(
                                f"Key '{k}' does not exist in the optimizers, it will be ignored."
                            )
                except Exception as e:
                    print(
                        f"(load_state_dict -> optimizers): The key '{k}' was not loaded due to the exception: {e}"
                    )
        if schedulers and self.schedulers:
            for scheduler in schedulers:
                try:
                    for k, v in scheduler.items():
                        if k in self.schedulers:
                            self.schedulers[k].load_state_dict(v)
                        else:
                            print(
                                f"Key '{k}' does not exist in the schedulers, it will be ignored."
                            )
                except Exception as e:
                    print(
                        f"(load_state_dict -> schedulers): The key '{k}' was not loaded due to the exception: {e}"
                    )

    def get_lr(
        self, keys: Optional[Union[str, List[str]]] = None
    ) -> List[Dict[str, float]]:
        lrs = []
        if keys and isinstance(keys, (str, list, tuple)):
            if isinstance(keys, str):
                return [{keys: self.optimizers[keys].param_groups[0]["lr"]}]
            for k in keys:
                lrs.append({k: self.optimizers[k].param_groups[0]["lr"]})
            return lrs
        for k, v in self.optimizers.items():
            lrs.append({k: v.param_groups[0]["lr"]})
        return lrs

    def _set_lr(self, new_lr: float, opt: str):
        for p in self.optimizers[opt].param_groups:
            if isinstance(p["lr"], Tensor):
                p["lr"].fill_(new_lr)
            else:
                p["lr"] = new_lr

    def set_lr(self, new_lr: float, keys: Optional[Union[str, List[str]]]):
        if keys and isinstance(keys, (str, list, tuple)):
            if isinstance(keys, str):
                self._set_lr(new_lr, keys)
                return
            for key in keys:
                self._set_lr(new_lr, key)
            return
        for key in self.keys:
            self._set_lr(new_lr, key)

    def step(
        self,
        keys: Optional[Union[str, List[str]]] = None,
        scaler: Optional[GradScaler] = None,
    ):
        ks = (
            [keys]
            if isinstance(keys, str)
            else keys if isinstance(keys, (list, tuple)) else self.keys
        )

        for k in ks:
            if scaler is not None:
                scaler.step(self.optimizers[k])
                scaler.update()
            else:
                self.optimizers[k].step()

    def zero_grad(self, keys: Optional[Union[str, List[str]]] = None):
        if keys:
            if isinstance(keys, str):
                self.optimizers[keys].zero_grad()
            else:
                for key in keys:
                    self.optimizers[key].zero_grad()
        else:
            for _, v in self.optimizers.items():
                v.zero_grad()

    def scheduler(self, *args, key: Optional[Union[str, List[str]]] = None):
        if key is not None:
            self.schedulers[key].step(*args)
            return self.schedulers[key].optimizer.param_groups[0]["lr"]
        lr = 0
        for i, (_, v) in enumerate(self.schedulers.items()):
            v.step()
            if i == 0:
                lr = v.optimizer.param_groups[0]["lr"]
        return lr


def get_adamw_optimizer(
    model: nn.Module,
    lr: float = 1e-3,
    weight_decay_1: float = 1e-3,
    weight_decay_2: float = 0.0,
    betas: Tuple = (0.9, 0.999),
    device: str = "cpu",
    eps: float = 1e-8,
):
    group_decay_1 = []  # 2 or more n-dims
    group_decay_2 = []  # less than 2 (biases)
    for param in model.parameters():
        if not param.requires_grad:
            continue  # 'no grad' dont requires optim
        if param.ndim >= 2:
            group_decay_1.append(param)
        else:
            group_decay_2.append(param)
    optim_groups = [
        {"params": group_decay_1, "weight_decay": weight_decay_1},
        {"params": group_decay_2, "weight_decay": weight_decay_2},
    ]
    use_fused = (
        "fused" in inspect.signature(optim.AdamW).parameters
    ) and device == "cuda"
    return optim.AdamW(
        optim_groups, lr=lr, betas=betas, eps=eps, fused=use_fused or None
    )
