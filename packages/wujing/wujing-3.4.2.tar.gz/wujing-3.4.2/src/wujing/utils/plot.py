import matplotlib.pyplot as plt
import matplotlib_inline
import numpy as np
from adjustText import adjust_text

matplotlib_inline.backend_inline.set_matplotlib_formats("svg")


def format_number(num):
    """Format number with 'k' suffix if it's large."""
    if num >= 1000:
        return f"{num / 1000:.1f}k"
    else:
        return f"{num:.1f}"


def plot_log_scaled_histogram(lengths, label: str = "label"):
    plt.figure(figsize=(15, 10))

    min_length = min(lengths)
    max_length = max(lengths)

    if max_length / min_length > 100:
        bins = np.logspace(np.log10(min_length), np.log10(max_length), 20)
        plt.xscale("log")
        plt.xlabel(f"Length of {label} (log scale)")
    else:
        bins = np.linspace(min_length, max_length, 20)
        plt.xlabel(f"Length of {label}")

    plt.ylabel("Number of Samples")
    n, bins, patches = plt.hist(lengths, bins=bins, alpha=0.7)
    cmap = plt.get_cmap("viridis")
    for i, patch in enumerate(patches):
        plt.setp(patch, "facecolor", cmap(i / len(patches)))

    total = len(lengths)
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

    texts = []
    average_length = np.mean(lengths)
    plt.annotate(
        f"average: {format_number(average_length)}",
        xy=(average_length, 0),
        xycoords="data",
        xytext=(average_length, -0.025 * plt.gca().get_ylim()[1]),
        textcoords="data",
        ha="center",
        va="top",
        fontsize=8,
        color="red",
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color="red"),
    )

    for rect, count in zip(patches, n):
        height = rect.get_height()
        if height > 0:
            percentage_text = plt.text(
                rect.get_x() + rect.get_width() / 2,
                height,
                f"({100 * count / total:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=8,
                color="white",
                bbox=dict(facecolor="black", alpha=0.5),
            )
            range_label = f"[{format_number(rect.get_x())}, {format_number(rect.get_x() + rect.get_width())}]"
            range_text = plt.text(
                rect.get_x() + rect.get_width() / 2,
                height + 0.02 * plt.gca().get_ylim()[1],  # slightly above the top of the bar
                range_label,
                ha="center",
                va="bottom",
                fontsize=8,
                color="white",
                bbox=dict(facecolor="black", alpha=0.5),
            )
            texts.append(percentage_text)
            texts.append(range_text)

    adjust_text(
        texts,
        only_move={"points": "y", "texts": "y"},
        arrowprops=dict(arrowstyle="->", color="grey"),
    )

    plt.show()


if __name__ == "__main__":
    data = [0.05, 1, 2 * 2, 3**2, 4e2, 5e4, 600, 77, 888, 9**6, 10]
    plot_log_scaled_histogram(data)
