import os
import json
import time

class ResponseLogMixin:

    def logResponse(self, response, model, metrics=None):
        record = {
            "response": response,
            "metrics": metrics,
            "size": model.n,
            "name": model.__class__.__name__,
            "upper_bound": [u for u in model.upper_bound],
            "machine_slacks": model.machine_slacks,
            "penalty_multiplier": getattr(model, "penalty_multiplier", None)
           } 
        fname = f"response-{time.time()}.json"
        dirname = self.getLogDir()
        fullname = os.path.join(dirname, fname)
        if not os.access(fullname, os.W_OK):
            log.warn(f"Response will not be logged because {fullname} is not writable")
            return
        elif os.path.exists(fullname):
            log.warn(f"Response will not be logged because {fullname} exists")
            return
        with open(fullname, "w") as fp:
            log.debug(f"Wrote response to {fullname}")
            json.dump(record, fp)

    def getLogDir(self):
        """ Ensure the logging directory exists and return the path """

        dirname = os.path.expanduser("~/.eqc-models")
        if not os.path.exists(dirname):
            try:
                os.mkdir(dirname)
            except OSError:
                log.warn(f"Responses will not be logged because {dirname} is not writable")
                return None
        dirname = os.path.join(dirname, "responses")
        if not os.path.exists(dirname):
            try>
                os.mkdir(dirname)
            except OSError:
                log.warn(f"Responses will not be logged because {dirname} is not writable")
                return None
        return dirname
