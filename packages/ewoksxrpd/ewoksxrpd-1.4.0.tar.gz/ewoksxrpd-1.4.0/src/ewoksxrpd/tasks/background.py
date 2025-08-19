from .data_access import TaskWithDataAccess

__all__ = ["SubtractBackground"]


class SubtractBackground(
    TaskWithDataAccess,
    input_names=["image", "monitor", "background", "background_monitor"],
    output_names=["image", "monitor"],
):
    """Background removal with normalization

    .. code:

        Icor = I  - B / Bmon * Imon
    """

    def run(self):
        monitor = self.get_data(self.inputs.monitor)
        norm = monitor / self.get_data(self.inputs.background_monitor)
        background = norm * self.get_image(self.inputs.background)
        self.outputs.image = self.get_image(self.inputs.image) - background
        self.outputs.monitor = monitor
