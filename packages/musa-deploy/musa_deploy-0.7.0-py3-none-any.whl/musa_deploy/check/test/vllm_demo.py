from vllm.model_executor.layers.rotary_embedding import get_rope
import torch, torch_musa  # noqa


def vllm_test_ropes(
    head_size=128,
    num_heads=8,
    batch_size=1,
    seq_len=11,
    rotary_dim=64,
    max_position=128,
    base=10000,
    is_neox_style=False,
    scaling_factors=[1, 2, 4],
    dtype=torch.float16,
):

    rope = get_rope(
        head_size,
        rotary_dim,
        max_position,
        base,
        is_neox_style,
        {"type": "linear", "factor": (1,)},
    ).to(dtype=dtype)
    positions = torch.randint(0, max_position, (batch_size, seq_len)).to("musa:0")
    query = torch.randn(batch_size, seq_len, num_heads * head_size, dtype=dtype).to(
        "musa:0"
    )
    key = torch.randn_like(query).to("musa:0")
    ref_query, ref_key = rope._forward(positions, query, key)

    return ref_query, ref_key


if __name__ == "__main__":
    ref_query, ref_key = vllm_test_ropes()
    if ref_query.device == torch.device("musa:0") and ref_key.device == torch.device(
        "musa:0"
    ):
        print(True)
    else:
        print(False)
