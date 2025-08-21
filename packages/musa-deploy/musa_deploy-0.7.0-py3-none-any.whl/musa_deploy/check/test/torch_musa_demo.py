import torch, torch_musa  # noqa


def torch_musa_check():
    is_available = torch.musa.is_available()

    a = torch.tensor(1.0, device="musa")
    b = torch.tensor(2.0).to("musa")
    c = a + b

    assert c.item() == 3.0
    assert is_available


if __name__ == "__main__":
    # assert successfully, returncode -> 0
    # assert unsuccessfully, returncode -> 1
    torch_musa_check()
