import torch


def torch_check():
    is_available = torch.cpu.is_available()

    a = torch.tensor(1.0)
    b = torch.tensor(2.0)
    c = a + b

    assert c.item() == 3.0
    assert is_available


if __name__ == "__main__":
    # assert successfully, returncode -> 0
    # assert unsuccessfully, returncode -> 1
    torch_check()
