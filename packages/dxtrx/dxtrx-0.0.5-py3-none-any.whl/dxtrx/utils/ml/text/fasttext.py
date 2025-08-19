import logging
import fasttext
import fasttext.util
import numpy as np
import fsspec
import tempfile
import gzip
import shutil

from pathlib import Path
from typing import List, Optional, Any, Union
from sklearn.base import TransformerMixin, BaseEstimator


class FastTextVectorizer(TransformerMixin, BaseEstimator):
    """A scikit-learn compatible transformer that converts text into fastText embeddings.

    Will auto-download a model the first time you need it.

    Args:
        model_path: Local path where the fastText `.bin` model is (or should be) stored.
            If the file is missing or an empty string is supplied, it will be
            downloaded automatically (see `lang` below).
        lang: Two-letter ISO-639-1 code (e.g. "en", "es") for one of
            Facebook's 300-dimensional multilingual vectors.
            Required only when the model isn't already on disk.
        vector_size: Expected size of the word vectors (default 300).
        min_word_count: Minimum number of words required in a text to return a non-zero vector.
            If a text has fewer words, a zero vector is returned (default 1).

    Attributes:
        model_: The loaded fastText model.
        model_path_: The path to the loaded model.
        vector_size_: The size of the word vectors.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        lang: Optional[str] = "es",
        vector_size: int = 300,
        min_word_count: int = 1,
    ):
        self.model_path = model_path
        self.lang = lang
        self.vector_size = vector_size
        self.min_word_count = min_word_count
        self._logger = logging.getLogger(__name__)
        self._is_fitted = True  # This transformer is always fitted

    def _validate_input(self, X: Any) -> List[str]:
        """Validates input data.

        Args:
            X: Input data to validate.

        Returns:
            List of strings.

        Raises:
            TypeError: If input is not a list or numpy array.
            ValueError: If input list is empty.
        """
        if not isinstance(X, (list, np.ndarray)):
            raise TypeError("Input must be a list or numpy array of strings")
        if len(X) == 0:
            raise ValueError("Input list is empty")
        return [str(x) for x in X]

    def _ensure_model_loaded(self) -> None:
        """Ensures the fastText model is loaded, loading it if necessary."""
        if not hasattr(self, 'model_'):
            # If the model file is not found, download it
            p = Path(self.model_path) if self.model_path else None
            if not p or not p.is_file():
                if not self.lang:
                    raise ValueError(
                        "Model file not found and no `lang` provided. "
                        "Pass a language code (e.g. lang='en') to download a model."
                    )
                self._logger.info(
                    "FastText model not found at %s. Downloading %s vectors...",
                    self.model_path or "<unspecified>", self.lang
                )
                # fasttext.util.download_model returns the full path
                self.model_path = fasttext.util.download_model(
                    self.lang, if_exists="ignore", dimension=self.vector_size
                )

            self.model_ = fasttext.load_model(str(self.model_path))
            self.model_path_ = str(self.model_path)
            self.vector_size_ = self.vector_size
            
            self._logger.info("FastText model loaded from %s", self.model_path_)

    def fit(self, X: Any, y: Any = None) -> "FastTextVectorizer":
        """Fits the vectorizer. This is a no-op as fastText models are pre-trained.

        Args:
            X: Training data, where each element is a text string.
            y: Ignored.

        Returns:
            The fitted vectorizer.
        """
        self._validate_input(X)
        return self

    def get_vector(self, text: str) -> np.ndarray:
        """Gets the average fastText word embedding for a single text.

        Args:
            text: The text to get the vector for.

        Returns:
            The average of the word vectors.
        """
        self._ensure_model_loaded()
        
        return self.model_.get_sentence_vector(text)

    def transform(self, X: Any) -> np.ndarray:
        """Transforms texts into their corresponding embeddings.

        Args:
            X: The texts to convert.

        Returns:
            The embeddings of the texts.
        """
        X = self._validate_input(X)
        self._ensure_model_loaded()
        
        return np.vstack([self.get_vector(t) for t in X])

    def fit_transform(self, X: Any, y: Any = None) -> np.ndarray:
        """Fits the vectorizer and transforms the data.

        Args:
            X: The texts to convert.
            y: Ignored.

        Returns:
            The embeddings of the texts.
        """
        return self.fit(X, y).transform(X)

    @classmethod
    def from_fsspec(
        cls,
        model_url: str,
        local_tmp_path: Optional[str] = None,
        fallback_local_tmp_path_root: Optional[str] = None,
        vector_size: int = 300,
        min_word_count: int = 1,
        lang: Optional[str] = "es",
    ) -> "FastTextVectorizer":
        """Create a FastTextVectorizer by downloading a model from a URL using fsspec.
        
        Supports HTTP, GCS, S3, and other fsspec-compatible protocols.
        
        Args:
            model_url: URL to the FastText model file (supports .bin, .bin.gz)
            local_tmp_path: Local path where to save the downloaded model
            fallback_local_tmp_path_root: Root directory for temporary files if local_tmp_path not provided
            vector_size: Expected size of the word vectors
            min_word_count: Minimum number of words required in a text
            lang: Language code for fallback auto-download
            
        Returns:
            FastTextVectorizer instance with the downloaded model
        """
        logger = logging.getLogger(__name__)
        
        # Determine local path for the model
        if local_tmp_path:
            local_path = Path(local_tmp_path)
        else:
            if fallback_local_tmp_path_root:
                tmp_root = Path(fallback_local_tmp_path_root)
            else:
                tmp_root = Path(tempfile.gettempdir()) / "fasttext_models"
            
            tmp_root.mkdir(parents=True, exist_ok=True)
            # Extract filename from URL
            filename = Path(model_url).name
            if filename.endswith('.gz'):
                filename = filename[:-3]  # Remove .gz extension for local file
            local_path = tmp_root / filename
        
        # Download if not exists locally
        if not local_path.exists():
            logger.info(f"Downloading FastText model from {model_url} to {local_path}")
            
            # Create parent directories
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download using fsspec
            with fsspec.open(model_url, 'rb') as remote_file:
                if model_url.endswith('.gz'):
                    # Handle gzipped files
                    with gzip.open(remote_file, 'rb') as gz_file:
                        with open(local_path, 'wb') as local_file:
                            shutil.copyfileobj(gz_file, local_file)
                else:
                    # Handle regular files
                    with open(local_path, 'wb') as local_file:
                        shutil.copyfileobj(remote_file, local_file)
            
            logger.info(f"FastText model downloaded successfully to {local_path}")
        else:
            logger.info(f"FastText model already exists at {local_path}")
        
        # Create vectorizer instance
        vectorizer = cls(
            model_path=str(local_path),
            lang=lang,
            vector_size=vector_size,
            min_word_count=min_word_count
        )
        
        return vectorizer

    @classmethod
    def from_pyfunc(
        cls,
        pyfunc_model: Any,
        vector_size: int = 300,
        min_word_count: int = 1,
        lang: Optional[str] = "es",
    ) -> "FastTextVectorizer":
        """Create a FastTextVectorizer from an MLflow PyFunc model.
        
        Args:
            pyfunc_model: MLflow PyFunc model containing a FastText model
            vector_size: Expected size of the word vectors
            min_word_count: Minimum number of words required in a text
            lang: Language code for identification
            
        Returns:
            FastTextVectorizer instance with the PyFunc model
        """
        logger = logging.getLogger(__name__)
        
        # Create vectorizer instance
        vectorizer = cls(
            model_path=None,  # No local path since we have the model directly
            lang=lang,
            vector_size=vector_size,
            min_word_count=min_word_count
        )
        
        # Set the model directly
        vectorizer.model_ = pyfunc_model
        vectorizer.model_path_ = f"pyfunc_model_{id(pyfunc_model)}"
        vectorizer.vector_size_ = vector_size
        
        logger.info("FastTextVectorizer created from PyFunc model")
        
        return vectorizer
    
    