from typing import Tuple, Union
import torch


def culen_indices(cu_lens: torch.Tensor):
    lengths = cu_lens[1:] - cu_lens[:-1]
    device = cu_lens.device

    starts = torch.cat(
        [torch.tensor([0], device=device), lengths.cumsum(0)[:-1]])
    ids = torch.repeat_interleave(torch.arange(
        len(lengths), device=device), lengths)
    positions = torch.arange(cu_lens[-1], device=device)
    return positions - starts[ids]


def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary(
    x: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    cu_lens: torch.Tensor,
) -> torch.Tensor:
    """
    Apply rotary embeddings using torch.scatter_.

    Args:
        x: Input tensor of shape (total_seq_len, nheads, headdim).
        cos: Cosine embeddings of shape (max_seqlen, rotary_dim).
        sin: Sine embeddings of shape (max_seqlen, rotary_dim).
        cu_seqlens: Cumulative lengths tensor of shape (batch_size + 1).
        max_seqlen: Maximum sequence length in the batch.
        rotary_dim: Dimension for rotary embeddings.
        inplace: If True, modifies `x` in-place.
    Returns:
        Rotated tensor of shape (total_seq_len, nheads, headdim).
    """
    indices = culen_indices(cu_lens)
    return x * cos[indices].unsqueeze(1) + rotate_half(x) * sin[indices].unsqueeze(1)


class ApplyRotaryEmbQKV_(torch.autograd.Function):
    @staticmethod
    def forward(ctx, q, k, cos, sin, cu_lens):
        ctx.save_for_backward(cos, sin, cu_lens)

        q_r = apply_rotary(q, cos, sin, cu_lens)
        k_r = apply_rotary(k, cos, sin, cu_lens)

        return q_r, k_r

    @staticmethod
    def backward(ctx, dq, dk):
        cos, sin, cu_lens = ctx.saved_tensors

        dq_r = apply_rotary(dq, cos, sin, cu_lens)
        dk_r = apply_rotary(dk, cos, sin, cu_lens)

        return dq_r, dk_r, None, None, None, None


def apply_rotary_emb_qkv_(q, k, cos, sin, cu_lens: torch.Tensor) -> torch.Tensor:
    """
    Apply rotary embedding *inplace* to the first rotary_dim of Q and K.

    Arguments:
        qkv: (batch_size * seqlen, 3, nheads, headdim)
        cos, sin: (seqlen, rotary_dim / 2)
        cu_seqlen: (batch_size + 1) the cumulative sum of the sequence lengths
        max_seqlen: int the maximum sequence length in the batch
    Return:
        qkv: (batch_size * seqlen, 3, nheads, headdim)
    """
    return ApplyRotaryEmbQKV_.apply(q, k, cos, sin, cu_lens)


class RotaryEmbedding(torch.nn.Module):
    """
    The rotary position embeddings from RoFormer_ (Su et. al).
    """

    def __init__(self, dim: int, base=10000.0, pos_idx_in_fp32=True, device=None):
        """
        pos_idx_in_fp32: if True, the position indices [0.0, ..., seqlen - 1] are in fp32,
            otherwise they might be in lower precision.
            This option was added because previously (before 2023-07-02), when we construct
            the position indices, we use the dtype of self.inv_freq. In most cases this would
            be fp32, but if the model is trained in pure bf16 (not mixed precision), then
            self.inv_freq would be bf16, and the position indices are also in bf16.
            Because of the limited precision of bf16 (e.g. 1995.0 is rounded to 2000.0), the
            embeddings for some positions will coincide.
            To maintain compatibility with models previously trained in pure bf16,
            we add this option.
        """
        super().__init__()
        self.dim = dim
        self.base = float(base)
        self.pos_idx_in_fp32 = pos_idx_in_fp32
        inv_freq = self._compute_inv_freq(device)
        self.register_buffer("inv_freq", inv_freq, persistent=False)

        self._seq_len_cached = 0
        self._cos_cached = None
        self._sin_cached = None

    def _compute_inv_freq(self, device=None):
        return 1.0 / (
            self.base
            ** (torch.arange(0, self.dim, 2, device=device, dtype=torch.float32) / self.dim)
        )

    def _update_cos_sin_cache(self, seqlen, device=None, dtype=None):
        # Reset the tables if the sequence length has changed,
        # if we're on a new device (possibly due to tracing for instance),
        # or if we're switching from inference mode to training
        if (
            seqlen > self._seq_len_cached
            or self._cos_cached is None
            or self._cos_cached.device != device
            or self._cos_cached.dtype != dtype
            or (self.training and self._cos_cached.is_inference())
        ):
            self._seq_len_cached = seqlen
            # We want fp32 here, not self.inv_freq.dtype, since the model could be loaded in bf16
            # And the output of arange can be quite large, so bf16 would lose a lot of precision.
            # However, for compatibility reason, we add an option to use the dtype of self.inv_freq.
            if self.pos_idx_in_fp32:
                t = torch.arange(seqlen, device=device, dtype=torch.float32)
                # We want fp32 here as well since inv_freq will be multiplied with t, and the output
                # will be large. Having it in bf16 will lose a lot of precision and cause the
                # cos & sin output to change significantly.
                # We want to recompute self.inv_freq if it was not loaded in fp32
                if self.inv_freq.dtype != torch.float32:
                    inv_freq = self._compute_inv_freq(device=device)
                else:
                    inv_freq = self.inv_freq
            else:
                t = torch.arange(seqlen, device=device,
                                 dtype=self.inv_freq.dtype)
                inv_freq = self.inv_freq

            freqs = torch.outer(t, inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1)
            self._cos_cached = emb.cos().to(dtype)
            self._sin_cached = emb.sin().to(dtype)

    def forward(self, q: torch.Tensor, k: torch.Tensor,
                cu_lens: torch.Tensor, max_len: int) -> torch.Tensor:
        """
        Apply rotary embedding *inplace*.

        Arguments:
            qkv: (batch * seqlen, 3, nheads, headdim) query, key, value.
            cu_seqlens: (batch + 1) the cumulative sum of the sequence lengths.
            max_seqlen: int the maximum sequence length in the batch.
        Return:
            qkv: (batch_size * seqlen, 3, nheads, headdim)
        """
        self._update_cos_sin_cache(max_len, device=q.device, dtype=q.dtype)

        return apply_rotary_emb_qkv_(q, k, self._cos_cached, self._sin_cached, cu_lens)
