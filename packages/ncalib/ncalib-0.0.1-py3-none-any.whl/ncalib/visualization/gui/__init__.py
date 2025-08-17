import cv2
import torch
from tqdm import tqdm

from ncalib import NCA
from ncalib.seed_factory import NCA_SeedFactory
from ncalib.visualization.gui.window_manager import GUIWindow


class FrameBuffer(list):
    def __init__(self, size: int):
        super().__init__()
        self.size = size

    def append(self, frame: torch.Tensor):
        super().append(frame)
        self._cleanup()

    def _cleanup(self):
        while len(self) > self.size:
            self.pop(0)

    def get(self) -> torch.Tensor:
        return self.pop(-1)


class NCA_GUI:
    def __init__(
            self,
            nca: NCA,
            windows: GUIWindow,
            seed_factory: NCA_SeedFactory,
            *,
            batch_size: int = 1,
            initial_delay: int = 10,
            take_every_k_frames: int = 1,
            buffersize=100,
    ):
        self.nca = nca
        self.windows = windows
        self.seed_factory = seed_factory
        self.batch_size = batch_size

        self.delay = initial_delay
        self.take_every_k_frames = take_every_k_frames
        self.buffer = FrameBuffer(buffersize)

        # GUI features
        self.state = None
        self.paused = None
        self.pbar = None
        self.i = None

        self._required_kwargs = nca.required_kwargs()

    def run(self, n=None):
        device = self.nca.device
        with torch.no_grad():
            self.state = self.seed_factory(self.batch_size, device=device)

        self.windows.init_state(self.state)

        self.nca.eval()
        self.paused = -1
        self.i = 0
        self.buffer.clear()
        self.pbar = tqdm(desc="GUI", unit=" generations", unit_scale=True, total=n)
        while True:
            if self.paused != 0:
                self.pbar.update(self.take_every_k_frames)
                self.buffer.append(self.state)

                with torch.no_grad():
                    for k in range(self.take_every_k_frames):
                        kwargs = {}
                        self.i += 1
                        if "t" in self._required_kwargs and self.paused != 0:
                            if n is None:
                                raise ValueError("'t' is an required kwarg but no 'n' is given!")

                            if self.i > n:
                                break
                            kwargs["t"] = torch.as_tensor([1 - (self.i / n)] * self.batch_size)

                        self.state = self.nca(self.state, **kwargs)
                        self.windows.update_state(self.state, step=self.i)
                        self.paused -= 1
                        if self.paused == 0:
                            break
                    if n is not None and self.i > n:
                        self.paused = 0
                    self.state = self.windows.modify_state(self.state)

            self.windows.update_windows()
            key = cv2.waitKey(self.delay)
            try:
                self.handle_key(key)
                self.windows.handle_key(key)
            except StopIteration:
                break

        cv2.destroyAllWindows()
        self.pbar.close()

    def handle_key(self, key: int):
        if key != -1:
            self.pbar.set_postfix({f"Key pressed": key})

        if key == ord("q"):
            self.pbar.set_postfix({"cmd": f"Quit"})
            raise StopIteration()
        elif key == ord("r"):
            self.state = self.seed_factory(self.batch_size, device=self.state.device)
            self.windows.init_state(self.state)
            self.buffer.append(self.state)
            self.pbar.set_postfix({"cmd": f"Reset after {self.pbar.n} generations"})
            self.pbar.reset()
            self.i = 0
        elif key == ord("p") or key == ord(" "):
            if self.paused != 0:
                self.paused = 0
                self.pbar.set_postfix({"cmd": f"Paused"})
            else:
                self.paused = -1
                self.pbar.set_postfix({"cmd": f"Unpaused"})
        elif key == ord("+"):
            self.delay = max(int(self.delay / 1.5), 1)
            self.pbar.set_postfix({"cmd": f"Delay set to {self.delay}"})
        elif key == ord("-"):
            self.delay = max(int(self.delay * 1.5), 2)
            self.pbar.set_postfix({"cmd": f"Delay set to {self.delay}"})
        elif key == ord(">"):
            self.take_every_k_frames += 1
            self.pbar.set_postfix({"cmd": f"Take every {self.take_every_k_frames} frames"})
        elif key == ord("<"):
            self.take_every_k_frames = max(1, self.take_every_k_frames - 1)
            self.pbar.set_postfix({"cmd": f"Take every {self.take_every_k_frames} frames"})
        elif key == 81:  # Left Arrow
            if len(self.buffer) == 0:
                self.pbar.set_postfix({"cmd": f"Buffer empty!"})
                return
            self.state = self.buffer.get()
            self.i -= 1
            self.pbar.update(-1)
            self.pbar.set_postfix({"cmd": f"Taking next buffered image (new length={len(self.buffer)})"})
        elif key == 83:  # Right Arrow
            self.paused = 1
