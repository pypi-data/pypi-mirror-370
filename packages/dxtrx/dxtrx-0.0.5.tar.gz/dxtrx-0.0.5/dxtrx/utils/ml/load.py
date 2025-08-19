import joblib
import os
import numpy as np
from pathlib import Path

from typing import Optional, Union, List
from dagster import get_dagster_logger
from mlflow.pyfunc import PyFuncModel
from sklearn.base import BaseEstimator

def _try_load_model_from_directory(temp_dir_path: str, logger) -> Union[PyFuncModel, BaseEstimator, np.ndarray, object]:
    """
    Try to load a model from a directory using various heuristics.
    
    Priority order:
    1. MLflow PyFunc model (if MLmodel file exists)
    2. Known model filenames with appropriate loaders
    
    Args:
        temp_dir_path: Path to the directory containing the model
        logger: Dagster logger for logging
        
    Returns:
        Loaded model object
        
    Raises:
        ValueError: If no supported model format is found in the directory
    """
    path_obj = Path(temp_dir_path)
    
    # Strategy 1: Try MLflow PyFunc model first
    if (path_obj / "MLmodel").exists():
        try:
            import mlflow.pyfunc
            model = mlflow.pyfunc.load_model(str(temp_dir_path))
            logger.info(f"✅ Model loaded as MLflow PyFunc from directory: {temp_dir_path}")
            return model
        except ImportError:
            logger.warning("⚠️ MLflow not available, skipping MLflow PyFunc loading")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load as MLflow PyFunc: {e}")
    
    # Strategy 2: Look for known model filenames in the directory
    model_file_patterns = [
        # XGBoost patterns
        ("model.xgb", "xgboost"),
        ("model.bin", "xgboost"),
        ("xgboost_model.bin", "xgboost"),
        ("booster.bin", "xgboost"),
        # Pickle/Joblib patterns
        ("model.pkl", "joblib"),
        ("model.joblib", "joblib"),
        ("sklearn_model.pkl", "joblib"),
        ("classifier.pkl", "joblib"),
        ("regressor.pkl", "joblib"),
        # NumPy patterns
        ("model.npy", "numpy"),
        ("weights.npy", "numpy"),
    ]
    
    found_files = []
    for filename, loader_type in model_file_patterns:
        file_path = path_obj / filename
        if file_path.exists() and file_path.is_file():
            found_files.append((str(file_path), loader_type, filename))
            logger.info(f"🔍 Found potential model file: {filename} (type: {loader_type})")
    
    if not found_files:
        # Strategy 3: Look for any files with known extensions
        logger.info("🔍 No known model filenames found, scanning for files with known extensions...")
        for file_path in path_obj.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix == ".xgb" or suffix == ".bin":
                    found_files.append((str(file_path), "xgboost", file_path.name))
                elif suffix in [".pkl", ".joblib"]:
                    found_files.append((str(file_path), "joblib", file_path.name))
                elif suffix == ".npy":
                    found_files.append((str(file_path), "numpy", file_path.name))
        
        if found_files:
            logger.info(f"🔍 Found {len(found_files)} files with known extensions")
    
    if not found_files:
        # List directory contents for debugging
        dir_contents = list(path_obj.iterdir())
        logger.error(f"❌ No supported model files found in directory: {temp_dir_path}")
        logger.error(f"Directory contents: {[f.name for f in dir_contents]}")
        raise ValueError(
            f"❌ No supported model files found in directory '{temp_dir_path}'. "
            f"Expected files: MLmodel (for MLflow), model.xgb/model.bin (for XGBoost), "
            f"model.pkl/model.joblib (for scikit-learn), or model.npy (for NumPy). "
            f"Found files: {[f.name for f in dir_contents]}"
        )
    
    # Try to load the first found file (prioritized by the order in model_file_patterns)
    for file_path, loader_type, filename in found_files:
        try:
            if loader_type == "xgboost":
                try:
                    import xgboost as xgb
                    model = xgb.Booster()
                    model.load_model(file_path)
                    logger.info(f"✅ Model loaded as XGBoost from directory file: {filename}")
                    return model
                except ImportError:
                    logger.warning(f"⚠️ XGBoost not available, skipping {filename}")
                    continue
            
            elif loader_type == "joblib":
                model = joblib.load(file_path)
                logger.info(f"✅ Model loaded with joblib from directory file: {filename}")
                return model
            
            elif loader_type == "numpy":
                model = np.load(file_path)
                logger.info(f"✅ Model loaded as NumPy array from directory file: {filename}")
                return model
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to load {filename} with {loader_type}: {e}")
            continue
    
    # If we get here, all loading attempts failed
    attempted_files = [f"{filename} ({loader_type})" for _, loader_type, filename in found_files]
    raise ValueError(
        f"❌ Failed to load model from directory '{temp_dir_path}'. "
        f"Attempted to load: {attempted_files}"
    )

def load_model(
    model_name: Optional[str] = None,
    model_tag: Optional[str] = None,
    model_uri: Optional[str] = None,
    fallback_model_path: Optional[str] = None,
    fallback_local_tmp_path_root: Optional[str] = None,
    delete: bool = True,
    skip_if_exists: bool = False,
    mlflow_client: Optional[object] = None,
    storage_client: Optional[object] = None,
) -> Union[PyFuncModel, BaseEstimator, np.ndarray, object]:
    """
    Load a model from MLflow (by name+tag or URI), or from a fallback local path with automatic type detection.
    
    Priority order:
    1. MLflow by model_name + model_tag
    2. MLflow by model_uri
    3. Fallback to local path with automatic type detection
    
    Fallback supports multiple model types:
    
    **Files:**
    - Pickle (.pkl) -> joblib.load()
    - Joblib (.joblib) -> joblib.load()
    - NumPy (.npy) -> np.load()
    - XGBoost (.xgb, .bin) -> xgboost.Booster().load_model()
    
    **Directories:**
    - MLflow folder (contains MLmodel file) -> mlflow.pyfunc.load_model()
    - Directories with known model files:
      - model.xgb, model.bin, xgboost_model.bin, booster.bin -> XGBoost
      - model.pkl, model.joblib, sklearn_model.pkl, classifier.pkl, regressor.pkl -> joblib
      - model.npy, weights.npy -> NumPy
    - Fallback: scan for any files with known extensions (.xgb, .bin, .pkl, .joblib, .npy)

    Args:
        model_name: Name of the model in MLflow
        model_tag: Tag of the model in MLflow
        model_uri: URI of the model in MLflow
        fallback_model_path: Path to fallback model file or folder
        fallback_local_tmp_path_root: Root directory for temporary files when downloading
        delete: Whether to delete the temporary file/directory when the context exits
        skip_if_exists: Whether to skip download if target already exists locally
        mlflow_client: MLflow client for loading models
        storage_client: Storage client for downloading files

    Returns:
        Union[PyFuncModel, BaseEstimator, np.ndarray, object]: Loaded model
        
    Raises:
        ValueError: If no valid loading method is provided or model type is unsupported
        FileNotFoundError: If the fallback path doesn't exist
    """
    logger = get_dagster_logger()

    # Try MLflow by name and tag first
    if model_name and model_tag:
        if not mlflow_client:
            raise ValueError("mlflow_client is required when using model_name and model_tag")
        try:
            model = mlflow_client.load_model_by_name_and_tag(model_name, model_tag)
            logger.info(f"✅ Model loaded from MLflow: {model_name}@{model_tag}")
            return model
        except Exception as e:
            logger.warning(f"⚠️ Failed to load model from MLflow ({model_name}@{model_tag}): {e}")
            if not fallback_model_path:
                raise

    # Try MLflow by URI second
    if model_uri:
        if not mlflow_client:
            raise ValueError("mlflow_client is required when using model_uri")
        try:
            model = mlflow_client.load_model_by_uri(model_uri)
            logger.info(f"✅ Model loaded from MLflow URI: {model_uri}")
            return model
        except Exception as e:
            logger.warning(f"⚠️ Failed to load model from MLflow URI ({model_uri}): {e}")
            if not fallback_model_path:
                raise

    # Fallback to local path with automatic type detection
    if fallback_model_path:
        if not storage_client:
            raise ValueError("storage_client is required when using fallback_model_path")
        
        logger.info(f"🔄 Trying to load model from fallback path: {fallback_model_path}")
        
        # Use fallback_local_tmp_path_root if provided
        download_kwargs = {
            'delete': delete,
            'skip_if_exists': skip_if_exists,
        }
        if fallback_local_tmp_path_root:
            download_kwargs['local_tmp_path_root'] = fallback_local_tmp_path_root
            
        with storage_client.download_to_temp_file(fallback_model_path, **download_kwargs) as temp_file_path:
            # Use automatic type detection on the downloaded file/directory
            path_obj = Path(temp_file_path)
            
            # Check if it's a directory (MLflow model or model folder) FIRST
            if path_obj.is_dir():
                logger.info(f"📁 Detected directory, using directory-based model loading: {temp_file_path}")
                return _try_load_model_from_directory(temp_file_path, logger)
            
            # File-based model detection (only if it's a file, not a directory)
            elif path_obj.is_file():
                logger.info(f"📄 Detected file, using file-based model loading: {temp_file_path}")
                file_extension = path_obj.suffix.lower()
                
                # Pickle files
                if file_extension == ".pkl":
                    model = joblib.load(str(temp_file_path))
                    logger.info(f"✅ Model loaded as Pickle from fallback: {temp_file_path}")
                    return model
                
                # Joblib files
                elif file_extension == ".joblib":
                    model = joblib.load(str(temp_file_path))
                    logger.info(f"✅ Model loaded as Joblib from fallback: {temp_file_path}")
                    return model
                
                # NumPy arrays
                elif file_extension == ".npy":
                    model = np.load(str(temp_file_path), allow_pickle=True)
                    logger.info(f"✅ Model loaded as NumPy array from fallback: {temp_file_path}")
                    return model
                
                # XGBoost models
                elif file_extension in [".xgb", ".bin"]:
                    try:
                        import xgboost as xgb
                        model = xgb.Booster()
                        model.load_model(str(temp_file_path))
                        logger.info(f"✅ Model loaded as XGBoost from fallback: {temp_file_path}")
                        return model
                    except ImportError:
                        raise ValueError("❌ XGBoost is required to load .xgb/.bin models")
                
                # For files without extensions or unknown extensions, try multiple loading methods
                else:
                    logger.warning(f"⚠️ Unknown file extension '{file_extension}', trying multiple loading methods")
                    
                    # Try XGBoost first (common for MLflow artifacts without extensions)
                    try:
                        import xgboost as xgb
                        model = xgb.Booster()
                        model.load_model(str(temp_file_path))
                        logger.info(f"✅ Model loaded as XGBoost from fallback: {temp_file_path}")
                        return model
                    except Exception as e:
                        logger.debug(f"Failed to load as XGBoost: {e}")
                    
                    # Try joblib/pickle as fallback
                    try:
                        model = joblib.load(str(temp_file_path))
                        logger.info(f"✅ Model loaded with joblib from fallback: {temp_file_path}")
                        return model
                    except Exception as e:
                        logger.debug(f"Failed to load with joblib: {e}")
                    
                    # If all methods fail, raise an informative error
                    raise ValueError(f"❌ Could not load model from '{temp_file_path}'. Tried XGBoost and joblib/pickle loading methods. File extension: '{file_extension}'")
            
            else:
                # Path exists but is neither a file nor a directory
                raise ValueError(f"❌ Unsupported path type: '{temp_file_path}' is neither a file nor a directory")

    raise ValueError("❌ You must provide either (model_name + model_tag), model_uri, or fallback_model_path")
