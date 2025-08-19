import glob
import importlib.util
import logging

from fastapi import APIRouter, FastAPI


class AutoLoader:

    def __init__(self, target_dir: str = "controllers", logger=None):
        self.target_dir = target_dir
        self.modules = []
        if logger is None:
            # Create a basic logger if none is provided
            logger = logging.getLogger("DynamicRouter")
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s:     %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        self.logger = logger

    def load(self, app: FastAPI):
        py_files = glob.glob(f"{self.target_dir}/**/[!__]*.py", recursive=True)
        for target_name in py_files:
            import_name = target_name.replace("/", ".").replace(".py", "")

            spec = importlib.util.spec_from_file_location(
                f"{import_name}.router", target_name
            )
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "router") and isinstance(module.router, APIRouter):
                    app.include_router(module.router)
                    self.modules.append(target_name)
                    self.logger.debug(f"Loaded router from {target_name}")

        self.logger.debug(
            f"DynamicRouter loaded {len(self.modules)} modules from {self.target_dir}"
        )
        return self
