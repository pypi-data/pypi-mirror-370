import torchvision.models as models
import torch, torch_musa  # noqa


def test_torchvision_on_musa():
    model = models.resnet18(pretrained=False)

    device = torch.device("musa")
    model = model.to(device)

    input_tensor = torch.randn(1, 3, 224, 224, device=device)
    output_tensor = model(input_tensor)

    assert output_tensor.shape == torch.Size([1, 1000])


if __name__ == "__main__":
    # assert successfully, returncode -> 0
    # assert unsuccessfully, returncode -> 1
    test_torchvision_on_musa()
