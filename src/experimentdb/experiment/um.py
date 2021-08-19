from .base import Experiment

import os
import mule
import iris


class UMRose(Experiment):
    type = "um-rose"

    def find_files(self):
        """
        Finds UM format files in a Rose run
        """
        os.environ["UMDIR"] = "/g/data/access/projects/access/umdir"
        rel_path = "share/data/History_Data"
        path = os.path.join(self.path, rel_path)

        for root, dir, files in os.walk(path):
            for f in files:
                p = os.path.join(root, f)
                try:
                    mule.load_umfile(p)
                    yield os.path.relpath(p, self.path)
                except ValueError:
                    # Not a UM file
                    continue

    def identify_streams(self, files):
        """
        Group files into streams with the same variables
        """
        streams = {}

        for f in files:
            s = os.path.basename(f)[:9]
            if s in streams:
                streams[s].append(f)
            else:
                streams[s] = [f]

        return streams

    def find_variables(self, file):
        """
        Find the variables in a single file

        Since all files in a stream share the same variable, this only needs to
        be run once per stream
        """
        cubes = iris.load(os.path.join(self.path, file))

        results = [str(c.attributes["STASH"]) for c in cubes]

        return results


class UMUMUI(Experiment):
    type = "um-umui"
