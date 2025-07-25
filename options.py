"""
Arguments for running agents for demos
"""

from collections.abc import Mapping
from itertools import product
from typing import Iterator, Literal, Tuple

from notte_sdk.types import ProxySettings
from pydantic import BaseModel, Field


class Options(BaseModel, Mapping):

    def __iter__(self):
        return iter(self.model_dump())

    def __getitem__(self, key):
        return self.model_dump()[key]

    def __len__(self):
        return len(self.model_dump())


class SessionOptions(Options):
    browser: Literal["chrome", "chromium"] = "chrome"
    headless: bool = False
    viewport_width: int = Field(default=1280, ge=800, le=3840, description="Viewport width in pixels")
    viewport_height: int = Field(default=1080, ge=600, le=2160, description="Viewport height in pixels")
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
        (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # chrome_args : list[str] = []


class SDKSessionOptions(SessionOptions):
    browser: Literal["chrome", "chromium", "firefox"] = "firefox"
    solve_captchas: bool = True
    proxies: bool | list[ProxySettings] = True


class AgentOptions(Options):
    reasoning_model: str = "cerebras/llama-3.3-70b"
    max_steps: int = Field(default=15, ge=5, le=50)


def iterate_options(local=True) -> Iterator[Tuple[SessionOptions, AgentOptions]]:
    """
    Iterator for potentially successful option combos

    Yields:
        tuple[SessionOptions, AgentOptions]
    """
    viewport_widths = [1280, 1920]
    proxies = [True, False, "US", "UK", "FR"]
    max_steps = [10, 15, 25, 35]
    reasoning_models = ["cerebras/llama-3.3-70b", "vertex_ai/gemini-2.0-flash", "openai/gpt-4o"]

    if local:
        for viewport_width, proxy, max_step, model in product(viewport_widths, proxies, max_steps, reasoning_models):
            yield SessionOptions(viewport_width=viewport_width, proxies=proxy), AgentOptions(
                max_steps=max_step, reasoning_model=model
            )
    else:
        for viewport_width, proxy, max_step, model in product(viewport_widths, proxies, max_steps, reasoning_models):
            yield SDKSessionOptions(viewport_width=viewport_width, proxies=proxy), AgentOptions(
                max_steps=max_step, reasoning_model=model
            )
