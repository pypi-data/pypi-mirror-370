import matplotlib.pyplot as plt
from ...private_eye.tools.exceptions import DebugToolsException
from skimage import img_as_ubyte, io
from skimage.exposure import cumulative_distribution


def create_histogram(input_path: str, output_path: str) -> None:
    print(f"Creating histogram of {input_path}")
    bins = 256
    img = img_as_ubyte(io.imread(input_path, as_gray=True))
    if len(img.shape) > 2:
        raise DebugToolsException("Only greyscale images supported")
    cdf, bins = cumulative_distribution(img, bins)

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("Intensity")
    ax1.set_ylabel("Pixel count")
    ax1.hist(img.ravel(), bins=bins)

    cdf_colour = "tab:red"
    ax2 = ax1.twinx()
    ax2.set_ylabel("CDF", color=cdf_colour)
    ax2.tick_params(axis="y", labelcolor=cdf_colour)
    ax2.set_ylim([0.0, 1.0])
    ax2.plot(bins, cdf, color=cdf_colour)

    fig.tight_layout()
    plt.savefig(output_path)
    print(f"Histogram saved to {output_path}")
