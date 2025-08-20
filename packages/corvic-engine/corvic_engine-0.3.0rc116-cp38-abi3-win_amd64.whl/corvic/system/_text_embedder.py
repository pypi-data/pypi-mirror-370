import asyncio
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import polars as pl

from corvic.result import InternalError, InvalidArgumentError, Ok
from corvic.system._embedder import (
    EmbedTextContext,
    EmbedTextResult,
    TextEmbedder,
)


class RandomTextEmbedder(TextEmbedder):
    """Embed inputs by choosing random vectors.

    Useful for testing.
    """

    @classmethod
    def model_name(cls) -> str:
        return "random"

    def embed(
        self, context: EmbedTextContext
    ) -> Ok[EmbedTextResult] | InvalidArgumentError | InternalError:
        rng = np.random.default_rng()

        match context.expected_coordinate_bitwidth:
            case 64:
                coord_dtype = pl.Float64()
            case 32:
                coord_dtype = pl.Float32()

        return Ok(
            EmbedTextResult(
                context=context,
                embeddings=pl.Series(
                    rng.random(
                        size=(len(context.inputs), context.expected_vector_length)
                    ),
                    dtype=pl.List(
                        coord_dtype,
                    ),
                ),
            )
        )

    async def aembed(
        self,
        context: EmbedTextContext,
        worker_threads: ThreadPoolExecutor | None = None,
    ) -> Ok[EmbedTextResult] | InvalidArgumentError | InternalError:
        return await asyncio.get_running_loop().run_in_executor(
            worker_threads, self.embed, context
        )


class IdentityTextEmbedder(TextEmbedder):
    """A deterministic text embedder.

    Embedding Process:
    - Each character in the input text is converted to its ASCII value.
    - The ASCII values are normalized to [0.0, 1.0] by dividing by 127.
    - The resulting list is truncated or padded to match the expected vector length.
    """

    @classmethod
    def model_name(cls) -> str:
        return "identity"

    def _text_to_embedding(
        self, text: str, vector_length: int, *, normalization: bool = False
    ) -> list[float]:
        """Convert text to a deterministic embedding vector.

        Use ASCII values of characters to generate embeddings.
        """
        ascii_values: list[float] = list(text.encode("ascii", "ignore"))

        if normalization:
            ascii_values = [value / 127 for value in ascii_values]

        if len(ascii_values) < vector_length:
            ascii_values.extend([0] * (vector_length - len(ascii_values)))
        elif len(ascii_values) > vector_length:
            ascii_values = ascii_values[:vector_length]

        return ascii_values

    def embed(
        self, context: EmbedTextContext
    ) -> Ok[EmbedTextResult] | InvalidArgumentError | InternalError:
        match context.expected_coordinate_bitwidth:
            case 64:
                coord_dtype = pl.Float64()
            case 32:
                coord_dtype = pl.Float32()

        embeddings = [
            self._text_to_embedding(text, context.expected_vector_length)
            for text in context.inputs
        ]

        return Ok(
            EmbedTextResult(
                context=context,
                embeddings=pl.Series(embeddings, dtype=pl.List(coord_dtype)),
            )
        )

    async def aembed(
        self,
        context: EmbedTextContext,
        worker_threads: ThreadPoolExecutor | None = None,
    ) -> Ok[EmbedTextResult] | InvalidArgumentError | InternalError:
        return await asyncio.get_running_loop().run_in_executor(
            worker_threads, self.embed, context
        )

    def preimage(self, embedding: list[float], *, normalized: bool = False) -> str:
        """Reconstruct the text from a given embedding vector."""
        if normalized:
            ascii_values = [int(round(value * 127)) for value in embedding]
        else:
            ascii_values = [int(round(value)) for value in embedding]
        chars = [chr(value) for value in ascii_values if value > 0]

        return "".join(chars)
